# Copyright (c) 2021, COMU Team, Osman Ceylan and etc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the COMU Team organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from typing import Union, Type, Sequence, Tuple
from copy import deepcopy, copy
from typing import List, Dict
import multiprocessing
import numpy as np
import os

from QDNS.tools.various_tools import tensordot, dev_mode
from QDNS.backend.tools.virt_qubit import VirtQudit
from QDNS.backend.tools.backend import Backend
from QDNS.backend.tools import config
from QDNS.backend.tools import noise
from QDNS.tools import gates

# Check if cirq avaible.
try:
    import cirq
except ImportError:
    cirq = None
    normal_simulator = None
    density_simulator = None
else:
    normal_simulator = cirq.Simulator()
    density_simulator = cirq.DensityMatrixSimulator()

selected_simulator = normal_simulator


def change_cirq_simulator(new_simulator: cirq.Simulator):
    """
    Changes the simulator run on Cirq backend.

    Args:
        new_simulator: cirq.Simulator

    Notes:
        New simulator must have simulate()
        New simulator must yiled final_state_vector in result
    """

    global selected_simulator
    selected_simulator = new_simulator


class ProcessMessages:
    class Request:
        """
        Main process -> cirq backend process.
        """

        START_LISTENING = ("process should start listening", False)
        TERMINATE_PROCESS = ("process should end", False)
        ALLOCATE_QFRAME = ("allocate qframe operation message", True)
        DEALLOCATE_QFRAME = ("deallocate qframe operation message", False)
        MEASURE_QUBITS = ("measure qubits operation message", True)
        EXTEND_CIRCUIT = ("extend circut operation message", True)
        APPLY_GATE = ("apply gate operation message", False)
        RESET_QUBITS = ("reset qubits operation message", False)
        APPLY_SERIAL_GATE = ("apply serial gate operation message", False)
        APPLY_CHANNEL_ERROR = ("apply channel error operation message", False)

    class Respond:
        """
        Main process <- cirq backend process.
        """

        PROCESS_PREPAIR_DONE = "process prepare is done"
        TERMINATE_SLAVE_DONE = "process termiante done"
        ALLOCATE_QFRAME_DONE = "allocate qframe operation done"
        DEALLOCATE_QFRAME_DONE = "deallocate qframe operation done"
        MEASURE_QUBITS_DONE = "measure qubits operation done"
        EXTEND_CIRCUIT_DONE = "extend circut operation done"
        APPLY_GATE_DONE = "apply gate operation done"
        RESET_QUBIT_DONE = "reset qubits operation done"
        APPLY_SERIAL_GATE_DONE = "apply serial gate operation done"
        APPLY_CHANNEL_ERROR_DONE = "apply channel error operation done"


lock = multiprocessing.Lock()


# Works with dev mode.
def log(message: str):
    if dev_mode:
        lock.acquire()
        print(message)
        lock.release()


# NOISE CHANNELS

class Id(cirq.SingleQubitGate):
    """ ID gate for multi dimension. """

    def __init__(self, dimension):
        super(Id, self)
        self.dimension = dimension

    def _qid_shape_(self):
        return self.dimension,

    def _num_qubits_(self):
        return 1

    def _unitary_(self):
        zero = np.zeros(shape=(self.dimension, self.dimension), dtype=complex)
        for i in range(self.dimension):
            zero[i][i] = complex(1, 0)
        return zero

    def _circuit_diagram_info_(self, args):
        self.args = args
        return "I"

    @property
    def unitary(self):
        return self._unitary_()


class PlusOneGate(cirq.SingleQubitGate):
    """ Plus One Gate """

    def __init__(self, dimension):
        super(PlusOneGate, self)
        self.dimension = dimension

    def _qid_shape_(self):
        return self.dimension,

    def _num_qubits_(self):
        return 1

    def _unitary_(self) -> np.ndarray:
        if self.dimension == 2:
            return np.array([[0, 1], [1, 0]], dtype=complex)

        zero = np.zeros(shape=(self.dimension, self.dimension), dtype=complex)
        zero[0][self.dimension - 1] = 1
        for i in range(1, self.dimension):
            zero[i][i - 1] = complex(1, 0)
        return zero

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+1]"

    @property
    def unitary(self):
        return self._unitary_()


class PlusXGate(cirq.SingleQubitGate):
    """ Plus X Gate """

    def __init__(self, dimension):
        super(PlusXGate, self)
        self.dimension = dimension
        self._plus = PlusOneGate(self.dimension).unitary

    def _qid_shape_(self):
        return self.dimension,

    def _num_qubits_(self):
        return 1

    def _unitary_(self) -> np.ndarray:
        if self.dimension == 2:
            return np.array([[0, 1], [1, 0]], dtype=complex)

        count = np.random.randint(0, self.dimension - 1)
        bf = self._plus
        for i in range(count):
            bf = bf.dot(PlusOneGate(self.dimension).unitary)

        return bf

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+X]"

    @property
    def unitary(self):
        return self._unitary_()


class PlusZGate(cirq.SingleQubitGate):
    """ Plus Z Gate """

    def __init__(self, dimension):
        super(PlusZGate, self)
        self.dimension = dimension

    def _qid_shape_(self):
        return self.dimension,

    def _num_qubits_(self):
        return 1

    def _unitary_(self) -> np.ndarray:
        if self.dimension == 2:
            return np.array([[1, 0], [0, -1]], dtype=complex)

        zero = np.zeros(shape=(self.dimension, self.dimension), dtype=complex)
        for i in range(self.dimension):
            if i % 2 == 0:
                zero[i][i] = complex(1, 0)
            else:
                zero[i][i] = complex(-1, 0)
        return zero

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+Z]"

    @property
    def unitary(self):
        return self._unitary_()


class BitFlipChannel(cirq.SingleQubitGate):
    """ Bit flip channel """

    def __init__(self, p: float, dim: int) -> None:
        self._p = p
        self._dim = dim
        self._plus = PlusXGate(self._dim).unitary

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [Id(self._dim).unitary, self._plus]
        return tuple(zip(ps, ops))

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "BF({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


class PhaseFlipChannel(cirq.SingleQubitGate):
    """ Phase flip channel """

    def __init__(self, p: float, dim: int) -> None:
        self._p = p
        self._dim = dim

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [Id(self._dim).unitary, PlusZGate(self._dim).unitary]
        return tuple(zip(ps, ops))

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "PF({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


class YFlipChannel(cirq.SingleQubitGate):
    """ Y flip channel or Bit and Phase Flip channel """

    def __init__(self, p: float, dim: int) -> None:
        self._p = p
        self._dim = dim
        self._plus = PlusXGate(self._dim).unitary.dot(PlusZGate(self._dim).unitary)

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [Id(self._dim).unitary, self._plus]
        return tuple(zip(ps, ops))

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "BPF({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


class DepolarizingChannel(cirq.SingleQubitGate):
    """ Depolarizing channel """

    def __init__(self, p: float, dim: int) -> None:
        self._p = p
        self._dim = dim
        self._plus_x = PlusXGate(self._dim).unitary
        self._plus_z = PlusZGate(self._dim).unitary
        self._plus_y = self._plus_x.dot(self._plus_z)

    def _mixture_(self):
        ps = [1.0 - self._p, self._p / 3, self._p / 3, self._p / 3]
        ops = [Id(dimension=self._dim).unitary, self._plus_x, self._plus_y, self._plus_z]
        return tuple(zip(ps, ops))

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "DPZ({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


class ResetChannel(cirq.ResetChannel):
    """ Reset channel """

    def __init__(self, p: float, dim: int = 2) -> None:
        self._dim = dim
        self._p = p
        super().__init__(dim)

    def _mixture_(self):
        ps = [1 - self._p, self._p]
        ops = [Id(dimension=self._dim).unitary, self._channel_()]
        return tuple(zip(ps, ops))

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "Reset({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


class NoNoiseChannel(cirq.SingleQubitGate):
    """ No noise channel """

    def __init__(self, p: float, dim: int) -> None:
        self._p = p
        self._dim = dim
        self._plus = Id(self._dim).unitary

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [Id(self._dim).unitary, self._plus]
        return tuple(zip(ps, ops))

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

    @staticmethod
    def _has_mixture_() -> bool:
        return True

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "NN({})".format(self._p)

    @property
    def unitary(self):
        return self._mixture_()


def get_channel_gate(flag: str) -> Union[Type[BitFlipChannel], Type[PhaseFlipChannel],
                                         Type[cirq.SingleQubitGate], Type[YFlipChannel],
                                         Type[DepolarizingChannel], Type[ResetChannel],
                                         Type[NoNoiseChannel]]:
    """ Gets the gate object from string in simulation_tools.channels. """

    if flag not in noise.channels:
        raise ValueError("Expected channel error flag from tools, but {}.".format(flag))

    if flag == noise.bit_flip_channel:
        return BitFlipChannel

    elif flag == noise.phase_flip_channel:
        return PhaseFlipChannel

    elif flag == noise.bit_and_phase_flip_channel:
        return YFlipChannel

    elif flag == noise.depolarisation_channel:
        return DepolarizingChannel

    elif flag == noise.reset_channel:
        return ResetChannel

    elif flag == noise.no_noise_channel:
        return NoNoiseChannel

    else:
        raise ValueError("Expected known channel error flag from tools, but {}.".format(flag))


# QUBIT POINTER

class VirtQudit(VirtQudit):
    """
    Virtual qudit template.

    #
    #  [PID]    [CH_IND]      [INDEX]
    #    |      00   00000      00
    #    |      /     |         |
    #    P     DIM   CHUNK      |
    #    0     00    00000      00
    #
    # Template supports pointing:
    #   Max 9 Process, 9 dimension, 99999 circuit, 99 qubit in a circuit.
    #
    """

    pid_length = 1
    dim_length = 2
    chunk_length = 5
    qubit_length = 2

    @staticmethod
    def qubit_id_resolver(qubit_id: str):
        """
        Qubit ID resolve from string.
        Returns pid, dim, chunk_id, qubit_id
        """

        return qubit_id[0:1], qubit_id[1:3], qubit_id[3:8], qubit_id[8:10]

    @staticmethod
    def generate_pointer(pid: int, dim: int, chunk_value: int, index: int) -> str:
        """
        Qubit ID Generator.
        """

        return "{:01d}{:02d}{:05d}{:02d}".format(pid, dim, chunk_value, index)


# CIRCUIT CHUNK

class Chunk(object):
    def __init__(
            self, index: int, qubit_count: int,
            noise_pattern: noise.NoisePattern,
            dimension=2, allocated=False
    ):
        """
        Chunk is a reference of one single circuit.

        Args:
            index: Index of chunk.
            qubit_count: Qubit count of this chunk.
            noise_pattern: Noise pattern of this chunk.
            dimension: Qubit dimension of this chunk.
            allocated: Allocated Flag.
        """

        if dimension <= 1:
            raise ValueError("Qudit dimension cannot below 2.")

        self._index = index
        self._qubit_count = qubit_count
        self._noise_pattern = noise_pattern
        self._dimension = dimension
        self._allocated = allocated
        self._extended_count = 0

        # Construct ID gate.
        if self._dimension == 2:
            self._id_gate = cirq.I
        else:
            self._id_gate = Id(self._dimension)

        # Iterate circuit for first time and apply state prepare error.
        self._circuit = cirq.Circuit()
        self._circuit_state = None

        self.scramble_qubits(
            (), self._noise_pattern.state_prepare_error_channel,
            self._noise_pattern.state_prepare_error_probability, _all=True
        )
        self.iterate_circuit()

    def iterate_circuit(self):
        """
        Iterates / Flush circuit of chunk.

        Returns:
            cirq.Result
        """

        result = selected_simulator.simulate(self._circuit, initial_state=self._circuit_state)
        self._circuit_state = result.state_vector()
        self._circuit.moments.clear()
        line_qids = [cirq.LineQid(i, dimension=self._dimension) for i in range(self._qubit_count)]
        self._circuit.append(Id(self._dimension).on_each(*line_qids))
        return result

    def deallocate_chunk(self) -> None:
        """ Hard reset the circuit. """

        self._circuit.moments.clear()
        self._circuit_state = None
        self._qubit_count -= self._extended_count
        self._extended_count = 0

        self.scramble_qubits(
            (), self._noise_pattern.state_prepare_error_channel,
            self._noise_pattern.state_prepare_error_probability, _all=True
        )
        self.set_allocated(False)

    def scramble_qubits(self, qubits: Sequence[int], method: str, percent: float, _all=False):
        """
        Process any channel with any percents.

        Args:
            qubits: Qubits to scramble.
            method: Channel method.
            percent: Percents tuple.
            _all: All qubits in this chunk flag.
        """

        if _all:
            qubits = np.arange(self.qubit_count)

        channel = get_channel_gate(method)
        line_qids = [cirq.LineQid(qubit, dimension=self._dimension) for qubit in qubits]
        for qid in line_qids:
            channel_obj = channel(percent, dim=self._dimension)
            self._circuit.append(channel_obj.on(qid))

    def extend_chunk(self, size: int):
        """
        Extends circuit by size from back.
        Comsumes time.

        Args:
            size: Size of iteration.

        Returns:
            List[int]
        """

        base = np.zeros(self._dimension, dtype=complex)
        base[0] = complex(1, 0)

        for i in range(size):
            self._circuit_state = tensordot(self._circuit_state, base)

        self._extended_count += size
        self._qubit_count += size
        return np.arange(self._qubit_count - size, self._qubit_count)

    def apply_transformation(self, gate: cirq.Gate, qubits: Sequence[int], iterate=False):
        """
        Applies gate to qubits on chunk.

        Args:
            gate: Cirq Gate.
            qubits: List[int].
            iterate: Iterate circuit.
        """

        if not self._allocated:
            raise AttributeError("Chunk {} is not allocated.".format(self._index))

        channel = get_channel_gate(self._noise_pattern.gate_error_channel)
        line_qids = [cirq.LineQid(qubit, dimension=self._dimension) for qubit in qubits]

        for qid in line_qids:
            channel_onj = channel(self._noise_pattern.gate_error_probability, dim=self._dimension)
            self._circuit.append(channel_onj.on(qid))
        self._circuit.append(gate.on(*line_qids))

        if iterate:
            self.iterate_circuit()

    def measure_qubits(self, qubits: Sequence[int], non_destructive=False, measure_dimension=None):
        """
        Measure Qubits.

        Args:
            qubits: List[int].
            non_destructive: Non-destructive flag.
            measure_dimension: Measure dimension.

        Returns:
             List[int]
        """

        if not self._allocated:
            raise AttributeError("Chunk {} is not allocated.".format(self._index))

        line_qids = [cirq.LineQid(qubit, dimension=self._dimension) for qubit in qubits]

        # Hold old state for non-destructive measurements.
        old_state = None
        old_circuit = None
        if non_destructive:
            old_state = copy(self._circuit_state)
            old_circuit = copy(self._circuit)

        # Set measure error channel error.
        if not non_destructive:
            self.scramble_qubits(
                qubits, self._noise_pattern.measure_error_channel,
                self._noise_pattern.measure_error_probability, _all=False
            )

        # Add measure OP.
        self._circuit.append(cirq.measure(*line_qids))

        # Add scramble after.
        if not non_destructive:
            self.scramble_qubits(
                qubits,
                self._noise_pattern.scramble_channel,
                0.565, _all=False)

        # Flush circuit.
        results = self.iterate_circuit()

        # Regain old state.
        if non_destructive:
            self._circuit_state = old_state
            self._circuit = old_circuit

        # Set measure dimension.
        if measure_dimension is None:
            measure_dimension = self._dimension
        else:
            if measure_dimension > self._dimension:
                measure_dimension = self._dimension

        for key in results.measurements.keys():
            return results.measurements[key] % measure_dimension

    def reset_qubits(self, qubits: Sequence[int], no_error=False):
        """
        Reset qubits.

        Args:
            qubits: List[int].
            no_error: Apply spam error flag.
        """

        line_qids = [cirq.LineQid(qubit, dimension=self._dimension) for qubit in qubits]
        for qid in line_qids:
            self._circuit.append(cirq.reset(qid))

        if not no_error:
            channel = get_channel_gate(self._noise_pattern.state_prepare_error_channel)
            self._circuit.append(channel(
                self._noise_pattern.state_prepare_error_probability,
                dim=self._dimension
            ).on_each(*line_qids))

    def set_allocated(self, flag: bool):
        """ Make sure reset before deallocate. """

        self._allocated = flag

    @property
    def circuit(self) -> cirq.Circuit:
        return self._circuit

    @property
    def circuit_state(self) -> np.ndarray:
        return self._circuit_state

    @property
    def allocated(self) -> bool:
        return self._allocated

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def qubit_count(self) -> int:
        return self._qubit_count

    @property
    def index(self) -> int:
        return self._index

    def __str__(self) -> str:
        text = str()
        text += "Index: {}, Dim: {}, Qubits: {}".format(self._index, self._dimension, self._qubit_count)
        return text


# CIRQ BACKEND SLAVE


class CirqBackendSlave(object):
    def __init__(
            self, pid: int,
            configuration: config.BackendConfiguration,
            noise_pattern: noise.NoisePattern
    ) -> None:
        """
        Cirq Backend for multiprocessing.

        Args:
            pid: Process id of owner process.
            configuration: Cirq backend configuration.
            noise_pattern: Noise pattern for simulation.
        """

        self._configuretion = configuration
        self._noise_pattern = noise_pattern
        self._int_to_static_chunks: Dict[int, Chunk] = dict()
        self._pid = pid

    def prepair_slave(self):
        """ Starts preallocate. """

        for dim in self._configuretion.frame_config:
            left_side = 0
            for value in self._configuretion.frame_config[dim]:
                for i in range(self._configuretion.frame_config[dim][value]):
                    key = int("{:0{}d}{:0{}d}".format(
                        dim, VirtQudit.dim_length, i + left_side, VirtQudit.chunk_length)
                    )
                    self._int_to_static_chunks[key] = Chunk(
                        int("{:0{}d}".format(i + left_side, VirtQudit.chunk_length)),
                        value, self.noise_pattern,
                        allocated=False, dimension=dim
                    )
                left_side += self.configuretion.frame_config[dim][value]

    def terminate_slave(self):
        """ Terminates backend. """

        for chunk_index in self._int_to_static_chunks:
            self._int_to_static_chunks[chunk_index].deallocate_chunk()
        del self._int_to_static_chunks

    def allocate_qframes(self, frame_size: int, frame_count: int, dimension: int) -> List[List[str]]:
        """
        Allocates a qframe.

        Args:
            frame_size: Frame size.
            frame_count: Frame count.
            dimension: Dimension of frames.

        Returns:
             List[List[Qubit ID]].
        """

        to_return = list()
        low = int("{:0{}d}{:0{}d}".format(dimension, VirtQudit.dim_length, 0, VirtQudit.chunk_length))
        high = int("{:0{}d}{:0{}d}".format(
            dimension, VirtQudit.dim_length,
            int("9" * VirtQudit.chunk_length), VirtQudit.chunk_length)
        )

        for i in range(low, high):
            current = self._int_to_static_chunks[i]
            if not current.allocated and current.qubit_count == frame_size:
                to_return.append([
                    VirtQudit.generate_pointer(
                        self.pid, dimension, current.index, i
                    ) for i in range(current.qubit_count)
                ])
                current.set_allocated(True)
                frame_count -= 1

            if frame_count <= 0:
                break

        if frame_count > 1:
            raise OverflowError("Cirq slave cannot allocate more frame.")

        return to_return

    def deallocate_chunks(self, qubits: Sequence[str]):
        """
        Deallocates the qubits.

        Args:
            qubits: Qubits for deallocate.
        """

        for qubit in qubits:
            _, dim, chunk_val, _ = VirtQudit.qubit_id_resolver(qubit)
            chunk_index = int(dim + chunk_val)
            if self._int_to_static_chunks[chunk_index].allocated:
                self._int_to_static_chunks[chunk_index].deallocate_chunk()

    def extend_chunk(self, qubit: str, size: int):
        """
        Extends a circut by size from back.

        Args:
            qubit: Qubit for extension.
            size: Size of extension.

        Returns:
            List[QubitID].
        """

        _, dim, chunk_val, _ = VirtQudit.qubit_id_resolver(qubit)
        chunk = self._int_to_static_chunks[int(dim + chunk_val)]

        if not chunk.allocated:
            raise AttributeError("Chunk {} is not allocated. Extend chunk is failed.".format(chunk.index))

        return_list = list()
        for index in chunk.extend_chunk(size):
            return_list.append(VirtQudit.generate_pointer(self.pid, chunk.dimension, chunk.index, index))
        return return_list

    def apply_transformation(self, gate_id: int, gate_arguments: Sequence, qubits: List[str]):
        """
        Applies transformation on qubits.

        Args:
            gate_id: Gate Id.
            gate_arguments: Gate constructor args.
            qubits: Qubits.
        """

        indexes = np.zeros(qubits.__len__())
        _, dim, chunk_index, qubit_index = VirtQudit.qubit_id_resolver(qubits[0])
        chunk = self._int_to_static_chunks[int(dim + chunk_index)]
        indexes[0] = int(qubit_index)

        if not chunk.allocated:
            raise AttributeError("Chunk {} is not allocated. Apply transformation is failed.".format(chunk.index))

        for i in range(1, qubits.__len__()):
            _, dim, chunk_index, qubit_index = VirtQudit.qubit_id_resolver(qubits[i])
            if self._int_to_static_chunks[int(dim + chunk_index)] != chunk:
                raise OverflowError("Qubits must be in same circuit for transformation.")
            indexes[i] = int(qubit_index)

        gate = gates.gate_id_to_gate[gate_id](*gate_arguments)
        if gate.qubit_shape != qubits.__len__():
            raise ArithmeticError("Qubit count must be match with gate. {} != {}.".format(gate.qubit_shape, qubits.__len__()))

        gate = cirq.MatrixGate(gate.matrix, qid_shape=(chunk.dimension,) * qubits.__len__())
        chunk.apply_transformation(gate, indexes, iterate=False)

    def measure_qubits(self, qubits: Sequence[str], non_destructive=False, measure_dimension=None):
        """
        Measure Qubits.

        Args:
            qubits: List[Qubit ID].
            non_destructive: Non-destructive flag.
            measure_dimension: Measure dimension.

        Returns:
             List[int]
        """

        results = list()
        chunks: Dict[int, List[int]] = dict()

        for qubit in qubits:
            _, dim, chunk_val, index = VirtQudit.qubit_id_resolver(qubit)
            key = int(dim + chunk_val)

            try:
                chunks[key].append(int(index))
            except KeyError:
                chunks[key] = list()
                chunks[key].append(int(index))

        for chunk in chunks:
            result = self._int_to_static_chunks[chunk].measure_qubits(
                chunks[chunk], non_destructive=non_destructive, measure_dimension=measure_dimension
            )
            results.extend(result)
        return results

    def reset_qubits(self, qubits):
        """
        Resets the given qubits.

        Args:
            qubits: List[Qubit ID]
        """

        chunks = dict()

        for qubit in qubits:
            pid, dim, chunk_val, index = VirtQudit.qubit_id_resolver(qubit)
            qid = int(index)
            key = int(dim + chunk_val)

            try:
                chunks[key].append(qid)
            except KeyError:
                chunks[key] = list()
                chunks[key].append(qid)

        for chunk in chunks:
            self._int_to_static_chunks[chunk].reset_qubits(chunks[chunk])

    def process_channel_error(self, qubits, percent):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.

        Raises:
            ValueError: Percent range error.
        """

        # This value is already cheked few times to make sure not raise.
        if percent < 0.001 or percent > 1.001:
            raise ValueError("Percent must be in range of 0 and 1.")

        chunks = dict()

        for qubit in qubits:
            pid, dim, chunk_index, qubit_index = VirtQudit.qubit_id_resolver(qubit)
            qid = int(qubit_index)
            key = int(dim + chunk_index)

            try:
                chunks[key].append(qid)
            except KeyError:
                chunks[key] = list()
                chunks[key].append(qid)

        for chunk in chunks:
            self._int_to_static_chunks[chunk].scramble_qubits(
                chunks[chunk], self.noise_pattern.scramble_channel, percent, _all=False
            )

    def apply_serial_transformations(self, list_of_gates):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[GateID, GateArgs, List[Qubit]].
        """

        for gate_instructor in list_of_gates:
            self.apply_transformation(gate_instructor[0], gate_instructor[1], gate_instructor[2])

    @property
    def configuretion(self) -> config.BackendConfiguration:
        return self._configuretion

    @property
    def noise_pattern(self) -> noise.NoisePattern:
        return self._noise_pattern

    @property
    def chunks_dict(self) -> Dict[int, Chunk]:
        return self._int_to_static_chunks

    @property
    def pid(self) -> int:
        return self._pid

    def __int__(self):
        return self._pid

    @staticmethod
    def run_slave(
            pid_index: int,
            configuration: config.BackendConfiguration,
            noise_: noise.NoisePattern,
            out_queue: multiprocessing.SimpleQueue,
            in_queue: multiprocessing.SimpleQueue
    ):
        """
        Process runner of cirq backends.

        Args:
            pid_index: Index of this pid.
            configuration: Backend configuration.
            noise_: Noise pattern for simulation.
            out_queue: Unique queue for this process.
            in_queue: Income queue for this process.
        """

        def put_message(_command, _message):
            """
            Puts message to other processes.
            Out: [Index, Command, Message]
            Income: [Command, Respond, Message]
            """

            out_queue.put([pid_index, _command, _message])

        np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))

        cb = CirqBackendSlave(pid_index, configuration, noise_)
        cb.prepair_slave()

        log("Process-{}: Circuits: {}".format(pid_index, cb.configuretion.frame_config))
        put_message(ProcessMessages.Respond.PROCESS_PREPAIR_DONE, 0)

        command, report, message = in_queue.get()
        if command != ProcessMessages.Request.START_LISTENING[0]:
            raise ValueError("Process-{}: Unexpected message from main backend.".format(pid_index))

        if report:
            put_message(ProcessMessages.Respond.PROCESS_PREPAIR_DONE, 0)

        log("Process-{}: Starting listening commands.".format(pid_index))
        while 1:
            command, report, message = in_queue.get()

            if command == ProcessMessages.Request.TERMINATE_PROCESS[0]:
                cb.terminate_slave()

                if report:
                    put_message(ProcessMessages.Respond.TERMINATE_SLAVE_DONE, 0)
                log("Process-{}: Process is returning as master backend commands".format(pid_index))
                return

            elif command == ProcessMessages.Request.ALLOCATE_QFRAME[0]:
                frame_size = message[0]
                frame_count = message[1]
                dimension = message[2]
                qubits = cb.allocate_qframes(frame_size, frame_count, dimension)

                if report:
                    put_message(ProcessMessages.Respond.ALLOCATE_QFRAME_DONE, qubits)
                log("Process-{}: Allocates {}x{} qubits(s)".format(pid_index, qubits.__len__(), qubits[0].__len__()))

            elif command == ProcessMessages.Request.DEALLOCATE_QFRAME[0]:
                qubits = message[0]
                cb.deallocate_chunks(qubits)

                if report:
                    put_message(ProcessMessages.Respond.DEALLOCATE_QFRAME_DONE, 0)
                log("Process-{}: Deallocate Frame ({}) -> {} ... {}".format(pid_index, qubits.__len__(), qubits[0], qubits[-1]))

            elif command == ProcessMessages.Request.EXTEND_CIRCUIT[0]:
                qubit = message[0]
                size = message[1]
                qubits = cb.extend_chunk(qubit, size)

                if report:
                    put_message(ProcessMessages.Respond.EXTEND_CIRCUIT_DONE, qubits)
                log("Process-{}: Extend circuit ({}) -> {} ... {}".format(pid_index, qubits.__len__(), qubits[0], qubits[-1]))

            elif command == ProcessMessages.Request.APPLY_GATE[0]:
                gate_id = message[0]
                gate_args = message[1]
                qubits = message[2]
                cb.apply_transformation(gate_id, gate_args, qubits)

                if report:
                    put_message(ProcessMessages.Respond.APPLY_GATE_DONE, 0)
                log("Process-{}: Apply gate_id: {} to qubits ({}) -> {} ... {}".format(pid_index, gate_id, qubits.__len__(), qubits[0], qubits[-1]))

            elif command == ProcessMessages.Request.MEASURE_QUBITS[0]:
                qubits = message[0]
                args = message[1]
                for_print = list()
                results = list()
                results.extend(cb.measure_qubits(qubits, *args))
                for_print.extend(results)

                if report:
                    put_message(ProcessMessages.Respond.MEASURE_QUBITS_DONE, results)
                log("Process-{}: Measure Qubit(s) ({}) -> {} ... {}".format(pid_index, for_print.__len__(), for_print[0], for_print[-1]))

            elif command == ProcessMessages.Request.RESET_QUBITS[0]:
                qubits = message[0]
                cb.reset_qubits(qubits)

                if report:
                    put_message(ProcessMessages.Respond.RESET_QUBIT_DONE, 0)
                log("Process-{}: Reset qubit(s) ({}) -> {} ... {}".format(pid_index, qubits.__len__(), qubits[0], qubits[-1]))

            elif command == ProcessMessages.Request.APPLY_CHANNEL_ERROR[0]:
                qubits = message[0]
                percent = message[1]
                cb.process_channel_error(qubits, percent)

                if report:
                    put_message(ProcessMessages.Respond.APPLY_CHANNEL_ERROR_DONE, 0)
                log("Process-{}: Processes channel error to count of ({})".format(pid_index, qubits.__len__()))

            elif command == ProcessMessages.Request.APPLY_SERIAL_GATE[0]:
                gate_list = message[0]
                count = 0
                cb.apply_serial_transformations(gate_list)
                count += gate_list.__len__()

                if report:
                    put_message(ProcessMessages.Respond.APPLY_SERIAL_GATE_DONE, 0)
                log("Process-{}: Apply serial ({}) gates".format(pid_index, count))

            else:
                raise ValueError("Cirq backend slave runner cannot recognize the command: {}?".format(command))


# CIRQ BACKEND MASTER


class CirqBackend(Backend):
    def __init__(
            self, configuration: config.BackendConfiguration,
            noise_pattern: noise.NoisePattern) -> None:
        """
        Cirq Backend.

        Args:
            configuration: Cirq backend configuration.
            noise_pattern: Noise pattern for simulation.
        """

        super().__init__(configuration, noise_pattern)
        self.processes: List[multiprocessing.Process] = list()
        self.income_queue = multiprocessing.SimpleQueue()
        self.process_queues: List[multiprocessing.SimpleQueue] = list()
        self.process_to_queue: Dict[multiprocessing.Process, multiprocessing.SimpleQueue] = dict()
        self.queue_to_process: Dict[multiprocessing.SimpleQueue, multiprocessing.Process] = dict()
        self.process_to_frame: Dict[multiprocessing.Process, Dict[int, Dict[int, int]]] = dict()

        for i in range(configuration.process_count):
            q = multiprocessing.SimpleQueue()
            p = multiprocessing.Process(
                target=CirqBackendSlave.run_slave,
                args=(i + 1, configuration, noise_pattern, self.income_queue, q),
                daemon=True
            )
            self.processes.append(p)
            self.process_queues.append(q)

            self.process_to_frame[p] = deepcopy(self.configuration.frame_config)
            self.process_to_queue[p] = q
            self.queue_to_process[q] = p

        self._allocate_memory: Dict[int, List[str]] = dict()
        self.start_backend()

    def put_message(self, process: multiprocessing.Process, command: Tuple[str, bool], *message):
        """
        Puts message to other processes.
        Out: [Command, Respond, Message]
        Income: [Index, Command, Message]
        """

        self.process_to_queue[process].put([command[0], command[1], message])

    def start_backend(self) -> bool:
        """ Starts the processes. """

        log("Cirq backend initialized with {} process.".format(self.configuration.process_count))
        for process in self.processes:
            process.start()

        for i in range(self.configuration.process_count):
            index, command, _ = self.income_queue.get()
            if command != ProcessMessages.Respond.PROCESS_PREPAIR_DONE:
                raise ValueError(
                    "Cirq backend process {}'s respond is not expected. "
                    "Expected {}".format(index, ProcessMessages.Respond.PROCESS_PREPAIR_DONE)
                )
            log("Process {} is returned prepair message as expected.".format(index))

        for process in self.processes:
            self.put_message(process, ProcessMessages.Request.START_LISTENING)

        if ProcessMessages.Request.START_LISTENING[1]:
            for _ in self.processes:
                pid, command, message = self.income_queue.get()
                if command != ProcessMessages.Respond.PROCESS_PREPAIR_DONE:
                    raise ValueError("Cirq master backend expected prepair done  message but got {}.".format(command))
        return True

    def terminate_backend(self):
        """ Terminates the backend. """

        for process in self.processes:
            self.put_message(process, ProcessMessages.Request.TERMINATE_PROCESS)

        self.processes.clear()
        self.process_queues.clear()
        self.process_to_queue.clear()
        self.queue_to_process.clear()
        self.process_to_frame.clear()

        if ProcessMessages.Request.TERMINATE_PROCESS[1]:
            for _ in self.processes:
                pid, command, message = self.income_queue.get()
                if command != ProcessMessages.Respond.TERMINATE_SLAVE_DONE:
                    raise ValueError("Cirq master backend expected terminate done  message but got {}.".format(command))

        self.income_queue = None
        log("Cirq backend master terminated.")

    def figure_allocation(self, frame_size: int, frame_count: int, dimension: int) -> Dict[multiprocessing.Process, int]:
        """
        Figures allocation places.

        Args:
            frame_size: Frame size.
            frame_count: Frame count.
            dimension:  Dimension.
        """

        process_to_size: Dict[multiprocessing.Process, int] = dict()
        org_frame_count = frame_count

        while frame_count > 0:
            change_happen = False
            for process in self.process_to_frame:
                try:
                    _ = self.process_to_frame[process][dimension]
                except KeyError:
                    pass
                else:
                    try:
                        _ = self.process_to_frame[process][dimension][frame_size]
                    except KeyError:
                        pass
                    else:
                        if self.process_to_frame[process][dimension][frame_size] > 0:
                            self.process_to_frame[process][dimension][frame_size] -= 1
                            try:
                                process_to_size[process] += 1
                            except KeyError:
                                process_to_size[process] = 1
                            frame_count -= 1
                            change_happen = True

                if frame_count <= 0:
                    break

            if not change_happen:
                log("Cirq master backend cannot allocate {}x{} qframes!".format(org_frame_count, frame_size))
                return {}

        log("Cirq master calculates {}x{} qframes allocation.".format(org_frame_count, frame_size))
        return process_to_size

    def figure_deallocation(self, qubits: Sequence[str]):
        """
        Figures the deallocation.

        Args
            qubits: List[Qubit ID].

        Return:
            Boolean.
        """

        report = True
        deleted_chunks = list()
        for qubit in qubits:
            pid, dim, chunk_val, index = VirtQudit.qubit_id_resolver(qubit)
            chunk_pointer = pid + dim + chunk_val

            qubit_found = False
            for frame_size in self._allocate_memory:
                if qubit in self._allocate_memory[frame_size]:
                    if chunk_pointer not in deleted_chunks:
                        self.process_to_frame[self.processes[int(pid) - 1]][int(dim)][frame_size] += 1
                        deleted_chunks.append(chunk_pointer)
                    self._allocate_memory[frame_size].remove(qubit)
                    qubit_found = True

            if not qubit_found:
                log("Qubit {} is not found in allocated qubit memory. This may cause of an extended qubit.".format(qubit))
                report = False

        return report

    def allocate_qubits(self, count: int, *args):
        """ Allocates qubits. Picks countx1 chunk. """

        return self.allocate_qframes(count, 1, *args)[0]

    def allocate_qframes(self, frame_size: int, frame_count: int, *args) -> List[List[str]]:
        """
        Allocates a qframe.

        Args:
            frame_size: Frame Size.
            frame_count: Frame Count.
            args: Backend specific arguments.

        Returns:
             List[Qubit ID]

        :arg[0] = dimension
        """

        dimension = 2
        if args.__len__() > 0:
            dimension = args[0]

        process_to_frame = self.figure_allocation(frame_size, frame_count, dimension)
        if process_to_frame == {}:
            raise OverflowError("Cirq master backend cannot allocate more qubits.")

        for process in process_to_frame:
            self.put_message(
                process,
                ProcessMessages.Request.ALLOCATE_QFRAME,
                frame_size,
                process_to_frame[process],
                dimension
            )

        qubits = list()
        if ProcessMessages.Request.ALLOCATE_QFRAME[1]:
            for _ in range(process_to_frame.keys().__len__()):
                pid, command, message = self.income_queue.get()

                if command != ProcessMessages.Respond.ALLOCATE_QFRAME_DONE:
                    raise ValueError("Cirq master backend expected allocate done message but got {}.".format(command))
                qubits.extend(message)

            for q in qubits:
                try:
                    self._allocate_memory[frame_size].extend(q)
                except KeyError:
                    self._allocate_memory[frame_size] = list()
                    self._allocate_memory[frame_size].extend(q)

            log("Cirq master backend allocates ({}x{}) qubit(s) from {} process(s)."
                .format(qubits.__len__(), qubits[0].__len__(), process_to_frame.__len__()))
        return qubits

    def deallocate_qubits(self, qubits: Sequence[str]):
        """
        Deallocates qubits.

        Args:
            qubits: List[Qubit ID]
        """

        process_to_qubits: Dict[multiprocessing.Process, List[str]] = dict()
        for qubit in qubits:
            pid, _, _, _ = VirtQudit.qubit_id_resolver(qubit)

            try:
                _ = process_to_qubits[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_qubits[self.processes[int(pid) - 1]] = list()

            process_to_qubits[self.processes[int(pid) - 1]].append(qubit)

        for process in process_to_qubits:
            self.put_message(
                process,
                ProcessMessages.Request.DEALLOCATE_QFRAME,
                process_to_qubits[process]
            )

        if ProcessMessages.Request.DEALLOCATE_QFRAME[1]:
            for _ in range(process_to_qubits.keys().__len__()):
                pid, command, message = self.income_queue.get()

                if command != ProcessMessages.Respond.DEALLOCATE_QFRAME_DONE:
                    raise ValueError("Cirq master backend expected deallocate done message but got {}.".format(command))

        return self.figure_deallocation(qubits)

    def extend_circuit(self, qubit: str, size: int):
        """
        Extend circuit by size from back.

        Args:
            qubit: Qubit of chuck.
            size: Size of extension.

        Returns:
            List[Qubit ID].
        """

        pid, dim, chunk_value, index = VirtQudit.qubit_id_resolver(qubit)
        process = self.processes[int(pid) - 1]
        self.put_message(
            process,
            ProcessMessages.Request.EXTEND_CIRCUIT,
            qubit, size
        )

        results = list()
        if ProcessMessages.Request.EXTEND_CIRCUIT[1]:
            pid, command, message = self.income_queue.get()
            if command != ProcessMessages.Respond.EXTEND_CIRCUIT_DONE:
                raise ValueError("Cirq master backend expected extend done message but got {}.".format(command))
            results.extend(message)
        return results

    def apply_transformation(self, gate_id, gate_arguments, qubits: Sequence[str], *args):
        """
        Applies transformation on qubits.

        Args:
            gate_id: Gate Id.
            gate_arguments: Gate constructor args.
            qubits: Qubits.
        """

        process_to_chunks: Dict[multiprocessing.Process, List[str]] = dict()
        for qubit in qubits:
            pid, dim, chunk_value, index = VirtQudit.qubit_id_resolver(qubit)

            try:
                _ = process_to_chunks[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_chunks[self.processes[int(pid) - 1]] = list()

            process_to_chunks[self.processes[int(pid) - 1]].append(qubit)

        if process_to_chunks.keys().__len__() != 1:
            raise OverflowError("Cannot apply gate_id: {}! Qubits are in different chunks.".format(gate_id))

        process = None
        for p in process_to_chunks:
            process = p
            break

        self.put_message(
            process,
            ProcessMessages.Request.APPLY_GATE,
            gate_id, gate_arguments,
            process_to_chunks[process]
        )

        if ProcessMessages.Request.APPLY_GATE[1]:
            for _ in range(process_to_chunks.keys().__len__()):
                pid, command, message = self.income_queue.get()
                if command != ProcessMessages.Respond.APPLY_GATE_DONE:
                    raise ValueError("Cirq master backend expected apply gate done message but got {}.".format(command))

    def measure_qubits(self, qubits: Sequence[str], *args):
        """
        Measures qubits.

        Args:
            qubits: List[Qubit ID].
            args: Backend specific arguments.

        Returns:
            List[int]

        :arg[0]: Non-destructive
        :arg[1]: Measure dimension.
        """

        placement: Dict[int, List[int]] = dict()
        process_to_chunks: Dict[multiprocessing.Process, List[str]] = dict()
        for i, qubit in enumerate(qubits):
            pid, dim, chunk_value, index = VirtQudit.qubit_id_resolver(qubit)

            try:
                _ = process_to_chunks[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_chunks[self.processes[int(pid) - 1]] = list()

            process_to_chunks[self.processes[int(pid) - 1]].append(qubit)

            try:
                _ = placement[int(pid) - 1]
            except KeyError:
                placement[int(pid) - 1] = list()
            placement[int(pid) - 1].append(i)

        for process in process_to_chunks:
            self.put_message(
                process,
                ProcessMessages.Request.MEASURE_QUBITS,
                process_to_chunks[process], args
            )

        results = np.zeros(qubits.__len__(), dtype=int)
        if ProcessMessages.Request.MEASURE_QUBITS[1]:
            for _ in range(process_to_chunks.keys().__len__()):
                pid, command, message = self.income_queue.get()

                if command != ProcessMessages.Respond.MEASURE_QUBITS_DONE:
                    raise ValueError("Cirq master backend expected measure done message but got {}.".format(command))
                for i, result in enumerate(message):
                    results[placement[pid - 1][i]] = result
        return results

    def reset_qubits(self, qubits: Sequence[str]):
        """
        Reset Qubits.

        Args:
            qubits: List[Qubit ID]
        """

        process_to_chunks: Dict[multiprocessing.Process, List[str]] = dict()
        for qubit in qubits:
            pid, dim, chunk_value, index = VirtQudit.qubit_id_resolver(qubit)

            try:
                _ = process_to_chunks[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_chunks[self.processes[int(pid) - 1]] = list()

            process_to_chunks[self.processes[int(pid) - 1]].append(qubit)

        for process in process_to_chunks:
            self.put_message(
                process,
                ProcessMessages.Request.RESET_QUBITS,
                process_to_chunks[process]
            )

        if ProcessMessages.Request.RESET_QUBITS[1]:
            for _ in range(process_to_chunks.keys().__len__()):
                pid, command, message = self.income_queue.get()

                if command != ProcessMessages.Respond.MEASURE_QUBITS_DONE:
                    raise ValueError("Cirq master backend expected reset done message but got {}.".format(command))

    def generate_ghz_pair(self, size: int, count: int):
        """
        Generates ghz pairs.

        Args:
            size: Size of qubits.
            count: Count of qubits.

        Return:
            List[List[QubitID]].
        """

        transformations = list()
        qubits = self.allocate_qframes(size, count, 2)
        for i in range(qubits.__len__()):
            transformations.append([gates.HGate.gate_id, (), (qubits[i][0],)])
            for j in range(size - 1):
                transformations.append([gates.CXGate.gate_id, (), (qubits[i][j], qubits[i][j + 1])])

        self.apply_serial_transformations(transformations)
        return qubits

    def process_channel_error(self, qubits, percent: float):
        """
        Process channel error.

        Args:
            qubits: Qubits in channel.
            percent: Error percent.
        """

        process_to_chunks: Dict[multiprocessing.Process, List[str]] = dict()
        for qubit in qubits:
            pid, dim, chunk_value, index = VirtQudit.qubit_id_resolver(qubit)

            try:
                _ = process_to_chunks[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_chunks[self.processes[int(pid) - 1]] = list()

            process_to_chunks[self.processes[int(pid) - 1]].append(qubit)

        for process in process_to_chunks:
            self.put_message(
                process,
                ProcessMessages.Request.APPLY_CHANNEL_ERROR,
                process_to_chunks[process],
                percent
            )

        if ProcessMessages.Request.APPLY_CHANNEL_ERROR[1]:
            for _ in range(process_to_chunks.keys().__len__()):
                pid, command, message = self.income_queue.get()
                if command != ProcessMessages.Respond.APPLY_CHANNEL_ERROR_DONE:
                    raise ValueError("Cirq master backend expected apply channel error done message but got {}.".format(command))

    def apply_serial_transformations(self, list_of_gates: Sequence[List], *args):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[[GateID, GateArgs, List[Qubit]]].
        """

        process_to_chunks: Dict[multiprocessing.Process, List] = dict()
        for gate_instructor in list_of_gates:
            gate_id, gate_args, qubits = gate_instructor[0], gate_instructor[1], gate_instructor[2]
            pid, dim, chunk_val, index = VirtQudit.qubit_id_resolver(qubits[0])

            try:
                _ = process_to_chunks[self.processes[int(pid) - 1]]
            except KeyError:
                process_to_chunks[self.processes[int(pid) - 1]] = list()

            process_to_chunks[self.processes[int(pid) - 1]].append([gate_id, gate_args, qubits])

        for process in process_to_chunks:
            self.put_message(
                process,
                ProcessMessages.Request.APPLY_SERIAL_GATE,
                process_to_chunks[process]
            )

        if ProcessMessages.Request.APPLY_SERIAL_GATE[1]:
            for _ in range(process_to_chunks.keys().__len__()):
                pid, command, message = self.income_queue.get()
                if command != ProcessMessages.Respond.APPLY_SERIAL_GATE_DONE:
                    raise ValueError("Cirq master backend expected apply serial gate done message but got {}.".format(command))
