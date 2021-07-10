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

from copy import copy
from typing import Dict, Iterable, List, Optional, Type, Union

try:
    import cirq
except ImportError:
    cirq = "None"

import numpy as np

from QDNS.tools import simulation_tools
from QDNS.tools.instance_logger import SubLogger
from QDNS.tools import gates

clifford_simulator = cirq.CliffordSimulator()
normal_simulator = cirq.Simulator()

default_qframe_configuretion = dict()
default_qframe_configuretion[2] = dict()
default_qframe_configuretion[2][1] = 4096
default_qframe_configuretion[2][2] = 2048
default_qframe_configuretion[2][3] = 1024
default_qframe_configuretion[2][4] = 512
default_qframe_configuretion[2][5] = 256
default_qframe_configuretion[2][6] = 128
default_qframe_configuretion[2][7] = 64
default_qframe_configuretion[2][8] = 32
default_qframe_configuretion[2][9] = 16
default_qframe_configuretion[2][10] = 8

default_qframe_configuretion[3] = dict()
default_qframe_configuretion[3][1] = 64
default_qframe_configuretion[3][2] = 32
default_qframe_configuretion[3][3] = 16
default_qframe_configuretion[3][4] = 8
default_qframe_configuretion[3][5] = 4
default_qframe_configuretion[3][6] = 2

default_qframe_configuretion[4] = dict()
default_qframe_configuretion[4][1] = 32
default_qframe_configuretion[4][2] = 16
default_qframe_configuretion[4][3] = 8
default_qframe_configuretion[4][4] = 4
default_qframe_configuretion[4][5] = 2

default_qframe_configuretion[5] = dict()
default_qframe_configuretion[5][1] = 4
default_qframe_configuretion[5][2] = 2

default_qframe_configuretion[6] = dict()
default_qframe_configuretion[6][2] = 2


def change_default_cirq_qframe_configuretion(
        qubits: dict, qutrits: Optional[dict] = None,
        quqrits: Optional[dict] = None, qugrits: Optional[dict] = None,
        qusrits: Optional[dict] = None
):
    """
    Changes cirq qframe configuration.

    Args:
        qubits: 2 Dim.
        qutrits: 3 Dim.
        quqrits: 4 Dim.
        qugrits: 5 Dim.
        qusrits: 6 Dim.
    """

    global default_qframe_configuretion
    default_qframe_configuretion[2] = qubits

    default_qframe_configuretion[3] = qutrits
    if qutrits is None:
        default_qframe_configuretion[3] = dict()

    default_qframe_configuretion[4] = quqrits
    if quqrits is None:
        default_qframe_configuretion[4] = dict()

    default_qframe_configuretion[5] = qugrits
    if qugrits is None:
        default_qframe_configuretion[5] = dict()

    default_qframe_configuretion[6] = qusrits
    if qusrits is None:
        default_qframe_configuretion[6] = dict()


def cirq_total_frame_size():
    """ Returns cirq total frame size. """

    total = 0

    for dim in default_qframe_configuretion:
        for value in default_qframe_configuretion[dim]:
            left_side = default_qframe_configuretion[dim][value]
            for i in range(left_side):
                total += 1

    return total


class VirtQudit(object):
    def __init__(self, chunk_value: int, index: int):
        """
        Virtual qudit object.
        Hold a pointer for a qubit.
        """

        #     [C_IND]       [INDEX]
        #     00 00000       00
        #     /    |        |
        #  DIM   CHUNK      |
        #  00    00000       00

        self.__uuid = "{:07d}{:02d}".format(chunk_value, index)

    @property
    def uuid(self):
        return self.__uuid

    @property
    def index(self):
        return int(self.__uuid[-2:])

    @property
    def chunk_index(self):
        return int(self.__uuid[2:7])

    @property
    def dimension(self) -> int:
        return int(self.__uuid[0:2])

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__uuid == other

    def __str__(self):
        return "Qudit Id: {}, Dimension {}.".format(self.__uuid, self.dimension)


def qubit_id_resolver(qubit_id):
    """
    Qubit ID resolve from string.
    Returns dim, chunk_id, qubit_id
    """

    return qubit_id[0:2], qubit_id[2:7], qubit_id[7:9]


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


class AsymmetricDepolarizingChannel(cirq.SingleQubitGate):
    """ Asymmetric Depolarizing channel """

    def __init__(
            self, p: Optional[float] = None, p_x: Optional[float] = None,
            p_y: Optional[float] = None, p_z: Optional[float] = None, dim: int = 2
    ) -> None:

        self._dim = dim

        self._plus_x = PlusXGate(self._dim).unitary
        self._plus_z = PlusZGate(self._dim).unitary
        self._plus_y = self._plus_x.dot(self._plus_z)

        self.p_x, self.p_y, self.p_z = p_x, p_y, p_z

        if p is None:
            if p_x is None:
                self.p_x = 0

            if p_y is None:
                self.p_y = 0

            if p_z is None:
                self.p_z = 0

            if p_x + p_y + p_z > 1.0:
                raise ValueError("Asymmetric depolarization channel should not have chance greater then 1.")

            self.p_id = 1 - (self.p_x + self.p_y + self.p_z)

        else:
            self.p_id = 1 - p
            self.p_x = np.random.uniform(0, p * 4 / 5)
            self.p_y = np.random.uniform(0, (p - self.p_x) * 4 / 5)
            self.p_z = p - self.p_x - self.p_y

    def _mixture_(self):
        ps = [self.p_id, self.p_x, self.p_y, self.p_z]
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
        return "ADP({})".format(1 - self.p_id)

    @property
    def unitary(self):
        return self._mixture_()


class ResetChannel(cirq.SingleQubitGate):
    """ Reset channel """

    def __init__(self, p: Optional[float] = None, dim: int = 2) -> None:
        self._dim = dim
        self._p = p

    def _mixture_(self):
        ps = [1 - self._p, self._p]
        ops = [Id(dimension=self._dim).unitary, self._channel_()]
        return tuple(zip(ps, ops))

    def _channel_(self) -> Iterable[np.ndarray]:
        channel = np.zeros((self._dim,) * 3, dtype=np.complex64)
        channel[:, 0, :] = np.eye(self._dim)
        return channel

    def _qid_shape_(self):
        return self._dim,

    def _num_qubits_(self):
        return 1

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
                                         Type[DepolarizingChannel], Type[ResetChannel], Type[NoNoiseChannel]]:
    """ Gets the gate object from string in simulation_tools.channels. """

    if flag not in simulation_tools.channels:
        raise ValueError("Expected channel error flag from tools, but {}.".format(flag))

    if flag == simulation_tools.bit_flip_channel:
        return BitFlipChannel

    elif flag == simulation_tools.phase_flip_channel:
        return PhaseFlipChannel

    elif flag == simulation_tools.bit_and_phase_flip_channel:
        return YFlipChannel

    elif flag == simulation_tools.depolarisation_channel:
        return DepolarizingChannel

    elif flag == simulation_tools.asymmetric_depolarisation_channel:
        return AsymmetricDepolarizingChannel

    elif flag == simulation_tools.reset_channel:
        return ResetChannel

    elif flag == simulation_tools.no_noise_channel:
        return NoNoiseChannel

    else:
        raise ValueError("Expected known channel error flag from tools, but {}.".format(flag))


class Chunk(object):
    def __init__(
            self, full_index, qubit_count: int, noise_pattern: simulation_tools.NoisePattern,
            dimension=2, initial_state=None, allocated=False
    ):
        if dimension <= 1:
            raise ValueError("Qudit dimension cannot below 2.")

        self._allocated = allocated
        self._full_index = full_index
        self._noise_pattern = noise_pattern
        self._qubit_dimension = dimension
        self._initial_state = initial_state
        self._extended = 0

        self._virt_qudits: List[VirtQudit] = list()
        self._virt_qudits_uuids: List[str] = list()

        # Construct ID gate.
        if self._qubit_dimension == 2:
            self._id_gate = cirq.I
        else:
            self._id_gate = Id(self._qubit_dimension)

        # Set qubits.
        for i in range(qubit_count):
            qubit = VirtQudit(self._full_index, i)
            self._virt_qudits.append(qubit)
            self._virt_qudits_uuids.append(qubit.uuid)

        # Iterate circuit for first time and apply state prepare error.
        channel = get_channel_gate(self._noise_pattern.state_prepare_error_channel)
        self._circuit = cirq.Circuit()
        qubits = cirq.LineQid.range(qubit_count, dimension=self._qubit_dimension)

        self._circuit.append(
            channel(*self._noise_pattern.state_prepare_error_probability,
                    dim=self._qubit_dimension).on_each(*qubits)
        )

        if initial_state is None:
            result = normal_simulator.simulate(self._circuit)
        else:
            try:
                result = normal_simulator.simulate(self._circuit, initial_state=initial_state)
            except ValueError:
                raise ValueError("Initial state of qudit not accepted by backend.")
        self._circuit_state = result.final_state_vector

    def clear_circuit(self, iterate=False) -> None:
        """ Clears the circuit of chunk. """

        self._circuit = cirq.Circuit()
        qubits = cirq.LineQid.range(self.qubit_count, dimension=self._qubit_dimension)
        self._circuit.append(self._id_gate.on_each(*qubits))

        if iterate:
            result = normal_simulator.simulate(self._circuit)
            self._circuit_state = result.final_state_vector

    def iterate_circuit(self):
        """ Iterates / Flush circuit of chunk. """

        result = normal_simulator.simulate(self._circuit, initial_state=self._circuit_state)
        self._circuit_state = result.final_state_vector
        self.clear_circuit(iterate=False)
        return result

    def destroy_chunk(self) -> None:
        """ Destroys the chunk. """

        self._virt_qudits.clear()
        self._virt_qudits_uuids.clear()
        del self._circuit

    def index_to_virt_qubit(self, index) -> VirtQudit:
        return self.virt_qubits[index]

    def reset(self, qubit_index, no_error=False):
        """ Adds reset to given qubit in circuit. """

        channel = get_channel_gate(self._noise_pattern.state_prepare_error_channel)
        for qubit in qubit_index:
            liq = cirq.LineQid(qubit, dimension=self._qubit_dimension)
            self._circuit.append(cirq.reset(liq))

            if not no_error:
                self._circuit.append(channel(*self._noise_pattern.state_prepare_error_probability, dim=self._qubit_dimension).on(liq))

    def deallocate_chunk(self):
        """ Reset the circuit. """

        for i in range(self._extended):
            self._virt_qudits.pop()
            self._virt_qudits_uuids.pop()
        self._extended = 0

        self.clear_circuit(iterate=True)
        self.set_allocated(False)

    def apply_transformation(self, gate: cirq.Gate, qubits, iterate=False) -> bool:
        """
        Applies gate to qubits on chunk.
        """

        channel = get_channel_gate(self._noise_pattern.gate_error_channel)

        line_qid = list()
        for qubit in qubits:
            qid = cirq.LineQid(qubit, dimension=self._qubit_dimension)
            line_qid.append(qid)

        self._circuit.append(
            channel(*self._noise_pattern.gate_error_probability, dim=self._qubit_dimension).on_each(*line_qid)
        )

        self._circuit.append(gate.on(*line_qid))

        if iterate:
            self.iterate_circuit()
        return True

    def scramble_qudit(self, qubits, method, percents, _all=False):
        """
        Process any channel with any percents.

        Args:
            qubits: Qubits to scramble.
            method: Channel method.
            percents: Percents tuple.
            _all: All qubits in this chunk flag.
        """

        if _all:
            qubits = np.arange(self.qubit_count)

        channel = get_channel_gate(method)
        for qubit in qubits:
            qid = cirq.LineQid(qubit, dimension=self._qubit_dimension)
            self._circuit.append(channel(*percents, dim=self._qubit_dimension).on(qid))

    def measure(self, qubits, non_destructive=False, measure_dimension=None):
        """
        Measures Qudits

        Args:
            qubits: Qudits.
            non_destructive: Non-destructive flag
            measure_dimension: Measure dimension.
        """

        line_qids = list()
        for qubit in qubits:
            line_qids.append(cirq.LineQid(qubit, dimension=self._qubit_dimension))

        # Hold old state for non-destructive measurements.
        old_state = None
        old_circuit = None
        if non_destructive:
            old_state = copy(self._circuit_state)
            old_circuit = copy(self._circuit)

        # Set SPAM channel error.
        if not non_destructive:
            channel = get_channel_gate(self._noise_pattern.measure_error_channel)
            self._circuit.append(channel(*self._noise_pattern.measure_error_probability,
                                         dim=self._qubit_dimension).on_each(*line_qids))

        self._circuit.append(cirq.measure(*line_qids))

        if not non_destructive:
            self.scramble_qudit(
                qubits, method=self._noise_pattern.scramble_channel,
                percents=self._noise_pattern.scramble_percent
            )

        # Flush circuit.
        results = self.iterate_circuit()

        if non_destructive:
            self._circuit_state = old_state
            self._circuit = old_circuit

        if measure_dimension is None:
            measure_dimension = self._qubit_dimension
        else:
            if measure_dimension > self._qubit_dimension:
                measure_dimension = self._qubit_dimension

        for key in results.measurements.keys():
            return results.measurements[key] % measure_dimension

    def extend_chunk(self):
        """ Extends circuit one more qubit. """

        base = np.zeros(self._qubit_dimension, dtype=complex)
        base[0] = complex(1, 0)
        new = VirtQudit(self._full_index, self.qubit_count)
        self._virt_qudits.append(new)
        self._virt_qudits_uuids.append(new.uuid)
        self._extended += 1

        self._circuit_state = tensordot(self._circuit_state, base)
        self.clear_circuit(iterate=True)
        return new.uuid

    def set_allocated(self, flag=True):
        self._allocated = flag

    def set_new_state(self, new_state):
        if not self._circuit_state.shape == new_state.shape:
            raise AttributeError(
                "State shapes do not match with given state!"
                " {} and {}.".format(self._circuit_state.shape, new_state.shape)
            )
        self._circuit_state = new_state

    @property
    def full_index(self):
        return self._full_index

    @property
    def circuit_state(self):
        return self._circuit_state

    @property
    def qubit_count(self) -> int:
        return self._virt_qudits.__len__()

    @property
    def dimension(self) -> int:
        return self._qubit_dimension

    @property
    def allocated(self):
        return self._allocated

    @property
    def virt_qubits(self) -> List[VirtQudit]:
        return self._virt_qudits

    @property
    def virt_qubit_uuids(self) -> List[str]:
        return self._virt_qudits_uuids

    @property
    def extended(self) -> int:
        return self._extended

    @property
    def circuit(self):
        return self._circuit


def tensordot(state_first, state_second):
    """
    Cirq circuit state specialized tensordot product.
    Return new merged state.
    """

    source_row = state_first.shape[0]
    target_row = state_second.shape[0]

    try:
        source_column = state_first.shape[1]
    except IndexError:
        source_column = 1
    try:
        target_column = state_second.shape[1]
    except IndexError:
        target_column = 1

    new_shape = (source_row * target_row, source_column * target_column)
    new_state = np.zeros(shape=new_shape, dtype=complex)
    state_first = np.array(state_first).reshape((source_row, source_column))
    state_second = np.array(state_second).reshape((target_row, target_column))

    a, b = 0, 0
    c, d = 0, 0
    for i in range(new_shape[0]):
        for j in range(new_shape[1]):
            new_state[i][j] = state_first[a][b] * state_second[c][d]
            d += 1

            if d >= target_column:
                d = 0
                b += 1
        b = 0
        c += 1

        if c >= target_row:
            c = 0
            a += 1

    return new_state.transpose()[0]


class CirqBackend(object):
    def __init__(self, noise_pattern: simulation_tools.NoisePattern):
        """
        Cirq backend constructor.

        Args:
            noise_pattern: Noise pattern for this simulation.

        See QDNS.tools.simulation_tools.NoisePattern() for details.
        """

        self.noise_pattern = noise_pattern
        self.int_to_static_chunks: Dict[int, Chunk] = dict()
        self.logger = SubLogger("Backend")

    def prepair_backend(self):
        self.int_to_static_chunks.clear()
        for dim in default_qframe_configuretion:
            left_side = 0
            for value in default_qframe_configuretion[dim]:
                for i in range(default_qframe_configuretion[dim][value]):
                    key = int("{:02d}{:05d}".format(dim, i + left_side))
                    self.int_to_static_chunks[key] = Chunk(key, value, self.noise_pattern, allocated=False, dimension=dim)
                left_side += default_qframe_configuretion[dim][value]

    def restart_engine(self, *args) -> bool:
        """ Restarts Cirq Backend. """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use restart flags.")

        for chunk in self.int_to_static_chunks:
            self.int_to_static_chunks[chunk].deallocate_chunk()
        return True

    def terminate_engine(self, *args):
        """ Terminates Cirq Backend. """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use terminate flags.")

        for chunk in self.int_to_static_chunks:
            self.int_to_static_chunks[chunk].destroy_chunk()

    def allocate_qubit(self, *args) -> List[str]:
        """ Allocates qubit. """

        self.logger.error("Cirq backend uses qframe for allocate qubits! Returning 1x1 qframe.")
        return self.allocate_qframe(1, *args)

    def allocate_qubits(self, count: int, *args) -> List[str]:
        """ Allocates qubits. """

        self.logger.error("Cirq backend uses qframe for allocate qubits! Returning 2xN qframe.")
        if count % 2 == 0:
            return self.allocate_qframes(2, count / 2, *args)
        else:
            return self.allocate_qframes(1, count, *args)

    def allocate_qframe(self, frame_size, *args) -> List[str]:
        """
        Creates chunk and allocates qubit inside the chunk.

        Args:
            frame_size: Qubit count of circuit.
            args: Definition in below.

        Return:
            List of qubit uuids.
        """

        return self.allocate_qframes(frame_size, 1, *args)

    def allocate_qframes(self, frame_size, frame_count, *args) -> List[str]:
        """
        Allocates qubit from staticly created chunks.

        Args:
            frame_size: Frame Size.
            frame_count: Frame Count.

        Return:
            Qubit uuid(s).

        :arg[0] = dimension
        :arg[1] = initial state
        """

        dimension = 2
        if args.__len__() > 0:
            dimension = args[0]

        initial_state = None
        if args.__len__() > 1:
            initial_state = args[1]

        to_return = list()
        low = int("{:02d}{:05d}".format(dimension, 0))
        high = int("{:02d}{:05d}".format(dimension, 99999))

        for i in range(low, high):
            current = self.int_to_static_chunks[i]
            if not current.allocated and current.qubit_count == frame_size:
                to_return.extend(current.virt_qubit_uuids)
                current.set_allocated(True)
                if initial_state is not None:
                    current.set_new_state(initial_state)
                frame_count -= 1

            if frame_count <= 0:
                break

        if frame_count > 0:
            raise OverflowError("Kernel cannot allocate {} qframe on {}.".format(frame_count, frame_size))
        return to_return

    def deallocate_qubit(self, qubits) -> bool:
        """
        Deallocates qubit.

        Args:
            qubits: Qubit uuid.

        Return:
            Boolean.
        """

        chunks = list()
        for qubit in qubits:
            chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubit)
            key = int(chunk_dim + chunk_index)
            chunk = self.int_to_static_chunks[key]

            if chunk not in chunks:
                chunks.append(chunk)

        for chunk in chunks:
            chunk.deallocate_chunk()
        return True

    def extend_qframe(self, qubit) -> str:
        """ Extends frame by qubit. """

        chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubit)
        key = int(chunk_dim + chunk_index)
        return self.int_to_static_chunks[key].extend_chunk()

    def apply_transformation(self, gate_id, gate_arguments, qubits, *args) -> bool:
        """
        Applies transformation on qubits.

        Args:
            gate_id: Gate Id.
            gate_arguments: Gate constructor args.
            qubits: Qubits.
            args: Backend spesific arguments.

        Returns:
            Boolean.
        """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use args on apply transformation.")

        indexes = list()
        chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubits[0])
        chunk = self.int_to_static_chunks[int(chunk_dim + chunk_index)]
        indexes.append(int(qubit_index))

        for i in range(1, qubits.__len__()):
            chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubits[i])
            if self.int_to_static_chunks[int(chunk_dim + chunk_index)] != chunk:
                raise OverflowError("Qubits must be in same circuit for transformation.")
            indexes.append(int(qubit_index))

        gate = gates.gate_id_to_gate[gate_id](*gate_arguments)
        if gate.qubit_shape != qubits.__len__():
            raise ArithmeticError("Qubit count must be match with gate. {} != {}.".format(gate.qubit_shape, qubits.__len__()))

        gate = cirq.MatrixGate(gate.matrix, qid_shape=(chunk.dimension,) * qubits.__len__())
        return chunk.apply_transformation(gate, indexes, iterate=False)

    def measure(self, qubits, *args) -> List[int]:
        """
        Measure qubits.

        :arg[0] => non-destructive
        :arg[1] => measure_dimension
        """

        non_destructive = False
        measure_dimension = None

        if args.__len__() == 0:
            non_destructive = False
            measure_dimension = None

        elif args.__len__() == 1:
            non_destructive = args[0]

        elif args.__len__() == 2:
            measure_dimension = args[1]

        else:
            self.logger.error("Cannot determine measure args {}.".format(args))

        results = list()
        chunks = dict()

        for qubit in qubits:
            chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubit)
            qid = int(qubit_index)
            key = int(chunk_dim + chunk_index)

            try:
                chunks[key].append(qid)
            except KeyError:
                chunks[key] = list()
                chunks[key].append(qid)

        for chunk in chunks:
            result = self.int_to_static_chunks[chunk].measure(
                chunks[chunk], non_destructive=non_destructive, measure_dimension=measure_dimension
            )
            for res in result:
                results.append(res)

        return results

    def reset_qubits(self, qubits, *args) -> bool:
        """
        Reset Qubits.

        Args:
            qubits: Qubit uuids.
            args: Backend spesific arguments.

        Return:
            Boolean.
        """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use args on reset qubit.")

        chunks = dict()
        for qubit in qubits:
            chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubit)
            key = int(chunk_dim + chunk_index)

            try:
                chunks[key].append(int(qubit_index))
            except KeyError:
                chunks[key] = list()
                chunks[key].append(int(qubit_index))

        for chunk in chunks:
            self.int_to_static_chunks[chunk].reset(chunks[chunk])
        return True

    def generate_epr_pairs(self, count, *args):
        """
        Generates epr pairs.

        Args:
            count: Count of pairs.

        Return:
            List[Qubit IDs].
        """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use args on generate entange pairs.")

        qubits = self.allocate_qframes(2, count, *args)
        for i in range(count):
            self.apply_transformation(gates.HGate.gate_id, (), (qubits[2 * i],))
            self.apply_transformation(gates.CXGate.gate_id, (), (qubits[2 * i], qubits[2 * i + 1]))
        return qubits

    def generate_ghz_pair(self, size, *args):
        """
        Generates ghz pair.

        Args:
            size: GHZ size.

        Return:
            List[Qubit IDs].
        """

        if args.__len__() > 0:
            self.logger.warning("Cirq backend do not use args on generate ghz pair.")

        qubits = self.allocate_qframe(size, *args)
        self.apply_transformation(gates.HGate.gate_id, (), (qubits[0],))
        for i in range(size - 1):
            self.apply_transformation(gates.CXGate.gate_id, (), (qubits[i], qubits[i + 1]))
        return qubits

    def process_channel_error(self, qubits, percent):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.

        Return:
             Boolean.

        Raises:
            ValueError: Percent range error.
        """

        # This value is already cheked few times to make sure not raise.
        if percent < 0.001 or percent > 1.0:
            raise ValueError("Percent must be in range of 0 and 1.")

        chunks = dict()

        for qubit in qubits:
            chunk_dim, chunk_index, qubit_index = qubit_id_resolver(qubit)
            qid = int(qubit_index)
            key = int(chunk_dim + chunk_index)

            try:
                chunks[key].append(qid)
            except KeyError:
                chunks[key] = list()
                chunks[key].append(qid)

        for chunk in chunks:
            self.int_to_static_chunks[chunk].scramble_qudit(
                chunks[chunk], self.noise_pattern.scramble_channel, (percent, ), _all=False
            )
        return True

    def apply_serial_transformations(self, list_of_gates):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[GateID, GateArgs, List[Qubit]].

        Return:
            Boolean.
        """

        for gate_instructor in list_of_gates:
            self.apply_transformation(gate_instructor[0], gate_instructor[1], gate_instructor[2])
        return True
