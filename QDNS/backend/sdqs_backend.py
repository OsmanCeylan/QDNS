"""
## ===========================================#
##  Header of QDNS/backend/sdqs.py            #
## ===========================================#

## ===========================================#
## Brief                                      #
## Contains SDQS Backend                      #
## ===========================================#
"""

from typing import Dict, Iterable, List, Optional

import numpy as np

from QDNS.tools.instance_logger import SubLogger
from QDNS.tools import simulation_tools
from QDNS.tools.various_tools import int2base

default_qframe_configuretion = dict()
default_qframe_configuretion[1] = 4096
default_qframe_configuretion[2] = 2048
default_qframe_configuretion[3] = 1024
default_qframe_configuretion[4] = 512
default_qframe_configuretion[5] = 256
default_qframe_configuretion[6] = 128
default_qframe_configuretion[7] = 64
default_qframe_configuretion[8] = 32
default_qframe_configuretion[9] = 16
default_qframe_configuretion[10] = 8


def change_default_sdqs_qframe_configuretion(
        qubits: dict
):
    """
    Changes sdqs qframe configuration.

    Args:
        qubits: 2 Dim.
    """

    global default_qframe_configuretion
    default_qframe_configuretion = qubits


def sdqs_total_frame_size():
    """ Returns sdqs total frame size. """

    total = 0

    for value in default_qframe_configuretion:
        left_side = default_qframe_configuretion[value]
        total += left_side

    return total


class VirtQudit(object):
    def __init__(self, chunk_value: int, index: int):
        """
        Virtual qudit object.
        Hold a pointer for a qubit.
        """

        #     [C_IND]       [INDEX]
        #     000000           00

        self.__uuid = "{:06d}{:02d}".format(chunk_value, index)

    @property
    def uuid(self):
        return self.__uuid

    @property
    def index(self):
        return int(self.__uuid[-2:])

    @property
    def chunk_index(self):
        return int(self.__uuid[0:6])

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__uuid == other

    def __str__(self):
        return "Qudit Id: {}.".format(self.__uuid)


def qubit_id_resolver(qubit_id):
    """
    Qubit ID resolve from string.
    Returns chunk_index, qubit_index
    """

    return qubit_id[0:6], qubit_id[-2:]


def tensordot(state_first, state_second):
    source_row = len(state_first)
    target_row = len(state_second)
    source_column = len(state_first[0])
    target_column = len(state_second[0])

    new_shape = (source_row * target_row, source_column * target_column)

    new_state = list()
    temp = list()
    for i in range(new_shape[0]):
        temp.clear()
        for j in range(new_shape[1]):
            temp.append(complex(0, 0))
        new_state.append(temp)

    a, b = 0, 0
    k, d = 0, 0
    for i in range(new_shape[0]):
        for j in range(new_shape[1]):
            new_state[i][j] = state_first[a][b] * state_second[k][d]
            b += 1

            if b >= source_column:
                b = 0
                d += 1

        a += 1
        b = 0
        d = 0

        if a >= source_row:
            a = 0
            k += 1

    return new_state


class IDGate:
    def __init__(self):
        self._matrix = np.zeros(shape=(2, 2), dtype=complex)
        for i in range(2):
            self._matrix[i][i] = complex(1, 0)

    @staticmethod
    def _num_qubits_():
        return 1

    @property
    def unitary(self):
        return self._matrix

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix


IDGate_matrix = IDGate().matrix


class PlusOneGate:
    """ Plus One Gate """

    def __init__(self):
        super(PlusOneGate, self)
        self._matrix = np.array([[0, 1], [1, 0]], dtype=complex)

    @staticmethod
    def _num_qubits_():
        return 1

    def _unitary_(self) -> np.ndarray:
        return self._matrix

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+1]"

    @property
    def unitary(self):
        return self._unitary_()


class PlusXGate:
    """ Plus X Gate """

    def __init__(self):
        super(PlusXGate, self)
        self._plus = PlusOneGate().unitary

    def _unitary_(self) -> np.ndarray:
        return self._plus

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+X]"

    @staticmethod
    def _num_qubits_():
        return 1

    @property
    def unitary(self):
        return self._unitary_()


class PlusZGate:
    """ Plus Z Gate """

    def __init__(self):
        super(PlusZGate, self)
        self._matrix = np.array([[1, 0], [0, -1]], dtype=complex)

    def _unitary_(self) -> np.ndarray:
        return self._matrix

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "[+Z]"

    @staticmethod
    def _num_qubits_():
        return 1

    @property
    def unitary(self):
        return self._unitary_()


class BitFlipChannel:
    """ Bit flip channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self._plus = PlusXGate().unitary

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [IDGate_matrix, self._plus]
        return tuple(zip(ps, ops))

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "BF({})".format(self._p)

    @staticmethod
    def _num_qubits_():
        return 1

    @property
    def unitary(self):
        return self._mixture_()


class PhaseFlipChannel:
    """ Phase flip channel """

    def __init__(self, p: float) -> None:
        self._p = p

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [IDGate_matrix, PlusZGate().unitary]
        return tuple(zip(ps, ops))

    @staticmethod
    def _num_qubits_():
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


class YFlipChannel:
    """ Y flip channel or Bit and Phase Flip channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self._plus = PlusXGate().unitary.dot(PlusZGate().unitary)

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [IDGate_matrix, self._plus]
        return tuple(zip(ps, ops))

    @staticmethod
    def _num_qubits_():
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


class DepolarizingChannel:
    """ Depolarizing channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self._plus_x = PlusXGate().unitary
        self._plus_z = PlusZGate().unitary
        self._plus_y = self._plus_x.dot(self._plus_z)

    def _mixture_(self):
        ps = [1.0 - self._p, self._p / 3, self._p / 3, self._p / 3]
        ops = [IDGate_matrix, self._plus_x, self._plus_y, self._plus_z]
        return tuple(zip(ps, ops))

    @staticmethod
    def _num_qubits_():
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


class AsymmetricDepolarizingChannel:
    """ Asymmetric Depolarizing channel """

    def __init__(
            self, p: Optional[float] = None, p_x: Optional[float] = None,
            p_y: Optional[float] = None, p_z: Optional[float] = None
    ) -> None:

        self._plus_x = PlusXGate().unitary
        self._plus_z = PlusZGate().unitary
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
        ops = [IDGate_matrix, self._plus_x, self._plus_y, self._plus_z]
        return tuple(zip(ps, ops))

    @staticmethod
    def _num_qubits_():
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


class ResetChannel:
    """ Reset channel """

    def __init__(self, p: Optional[float] = None) -> None:
        self._p = p

    def _mixture_(self):
        ps = [1 - self._p, self._p]
        ops = [IDGate_matrix, self._channel_()]
        return tuple(zip(ps, ops))

    @staticmethod
    def _channel_() -> Iterable[np.ndarray]:
        channel = np.zeros((2,) * 3, dtype=np.complex64)
        channel[:, 0, :] = np.eye(2)
        return channel

    @staticmethod
    def _num_qubits_():
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


class NoNoiseChannel:
    """ No Noise channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self._plus = IDGate_matrix

    def _mixture_(self):
        ps = [1.0 - self._p, self._p]
        ops = [IDGate_matrix, self._plus]
        return tuple(zip(ps, ops))

    def _circuit_diagram_info_(self, args) -> str:
        self.args = args
        return "BF({})".format(self._p)

    @staticmethod
    def _num_qubits_():
        return 1

    @property
    def unitary(self):
        return self._mixture_()


def get_channel_gate(flag: str):
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


class Circuit(object):
    def __init__(
            self, full_index, qubit_count,
            noise_pattern: simulation_tools.NoisePattern,
            initial_state=None, allocated=False
    ):
        """
        Circuit.

        Args:
            full_index: Full Index.
            qubit_count: Qubit in chunk.
            noise_pattern: Noise pattern.
            initial_state: Initial state.
            allocated: Allocate flag.
        """

        self._full_index = full_index
        self._qubit_count = qubit_count
        self._allocated = allocated
        self._noise_pattern = noise_pattern
        self._extended = 0

        self._virt_qudits: List[VirtQudit] = list()
        self._virt_qudits_uuids: List[str] = list()

        for i in range(qubit_count):
            qubit = VirtQudit(self.full_index, i)
            self._virt_qudits.append(qubit)
            self._virt_qudits_uuids.append(qubit.uuid)

        if initial_state is not None:
            if self._state.shape[0] != initial_state.shape[0]:
                raise AttributeError("Initial state did not match qubit count.")
            self._state = initial_state
        else:
            self._state = np.zeros(shape=np.power(2, qubit_count), dtype=np.complex)
            self._state[0] = complex(1, 0)

        channel = get_channel_gate(self._noise_pattern.state_prepare_error_channel)
        self.apply_channel(
            channel(*self._noise_pattern.state_prepare_error_probability).unitary,
            np.arange(self.qubit_count)
        )

    def apply_channel(self, mixture, qubits):
        num = np.random.randint(0, 100) / 100
        choosen = None

        for mix in mixture:
            num -= mix[0]

            if num <= 0:
                choosen = mix[1]
                break

        zeros = np.zeros(self.qubit_count, dtype=int)
        for qubit in qubits:
            zeros[qubit] = 1

        if zeros[0] == 0:
            first = IDGate_matrix
        else:
            first = choosen

        for i in range(1, zeros.__len__()):
            if zeros[i] == 0:
                first = tensordot(first, IDGate_matrix)
            else:
                first = tensordot(first, choosen)

        self._state = np.dot(self._state, first)

    def apply_single_transformation(self, gate_matrix, qubit):
        final_gate = np.array([[1]])
        i = 0
        while i < qubit:
            final_gate = tensordot(final_gate, IDGate_matrix)
            i += 1

        final_gate = tensordot(final_gate, gate_matrix)

        j = self._qubit_count - 1
        while j > qubit:
            final_gate = tensordot(final_gate, IDGate_matrix)
            j -= 1

        self._state = np.dot(self._state, final_gate)

    def apply_controlled_transformation(self, gate_maxrix, controlled_qubit, target_qubit):
        pass

    def measure(self, qubits):
        depth = list()
        for row in self._state:
            if row.real == 0 and row.imag == 0:
                depth.append(0)

            elif row.real != 0:
                depth.append(np.power(row, 2).real * 100)

            elif row.imag != 0:
                depth.append(np.power(row, 2).imag * 100)

            else:
                raise ValueError("Circuit state is unstable.")

        value = 0
        r = np.random.randint(0, 100)
        for j, i in enumerate(depth):
            r -= i
            if r <= 0:
                value = j
                break

        measures = int2base(value, self.qubit_count, 2)
        return [measures[i] for i in qubits]

    def reset_circuit(self) -> None:
        """ Clears the circuit. """

        self._state = np.zeros(shape=np.power(2, self._qubit_count), dtype=np.complex)
        self._state[0] = complex(1, 0)

    def destroy_chunk(self) -> None:
        """ Destroys the chunk. """

        self._virt_qudits.clear()
        self._virt_qudits_uuids.clear()
        self._state = None
        self._qubit_count = 0
        self.set_allocated(False)

    def index_to_virt_qubit(self, index) -> VirtQudit:
        return self.virt_qubits[index]

    def reset(self, qubit):
        """ Adds reset to given qubit in circuit. """

        pass

    def extend_chunk(self):
        """ Extends circuit one more qubit. """

        base = np.zeros(2, dtype=complex)
        base[0] = complex(1, 0)
        new = VirtQudit(self._full_index, self.qubit_count)
        self._virt_qudits.append(new)
        self._extended += 1

        self._state = tensordot(self._state, base)
        return new.uuid

    def set_allocated(self, flag=True):
        self._allocated = flag

    def deallocate_chunk(self):
        """ Reset the circuit. """

        for i in range(self._extended):
            self._virt_qudits.pop()
            self._virt_qudits_uuids.pop()

        self.reset_circuit()
        self.set_allocated(False)

    def scramble_qudit(self, qubits, method, percent, _all=False):
        if _all:
            qubits = np.arange(self._qubit_count)

        channel = get_channel_gate(method)
        self.apply_channel(channel(*percent, 2).unitary, qubits)

    def set_new_state(self, new_state):
        if not self._state.shape == new_state.shape:
            raise AttributeError(
                "State shapes do not match with given state!"
                " {} and {}.".format(self._state.shape, new_state.shape)
            )
        self._state = new_state

    @property
    def full_index(self) -> int:
        return self._full_index

    @property
    def qubit_count(self) -> int:
        return self._qubit_count

    @property
    def allocated(self) -> bool:
        return self._allocated

    @property
    def virt_qubits(self) -> List[VirtQudit]:
        return self._virt_qudits

    @property
    def virt_qubits_uuids(self) -> List[str]:
        return self._virt_qudits_uuids

    @property
    def state(self):
        return self._state

    @property
    def extended(self):
        return self._extended


class SdqsBackend:
    def __init__(self, noise_pattern: simulation_tools.NoisePattern):
        """
        SDQS backend constructor.

        Args:
            noise_pattern: Noise pattern for this simulation.

        See QDNS.tools.simulation_tools.NoisePattern() for details.
        """

        self.logger = SubLogger("SDQS Backend")
        self.noise_pattern = noise_pattern
        self.int_to_static_chunks: Dict[int, Circuit] = dict()

    def prepair_backend(self):
        self.int_to_static_chunks.clear()

        left_side = 0
        for value in default_qframe_configuretion:
            for i in range(default_qframe_configuretion[value]):
                key = int("{:06d}".format(i + left_side))
                self.int_to_static_chunks[key] = Circuit(key, value, self.noise_pattern, allocated=False)
            left_side += default_qframe_configuretion[value]

    def restart_engine(self, *args) -> bool:
        """ Restarts Sdqs Backend. """

        if args.__len__() > 0:
            self.logger.warning("Sdqs backend do not use restart flags.")

        for chunk in self.int_to_static_chunks:
            self.int_to_static_chunks[chunk].deallocate_chunk()
        return True

    def terminate_engine(self, *args):
        """ Terminates Sdqs Backend. """

        if args.__len__() > 0:
            self.logger.warning("Sdqs backend do not use terminate flags.")

        for chunk in self.int_to_static_chunks:
            self.int_to_static_chunks[chunk].destroy_chunk()

    def allocate_qubit(self, *args) -> List[str]:
        """ Allocates qubit. """

        self.logger.error("Sdqs backend uses qframe for allocate qubits! Returning 1x1 qframe.")
        return self.allocate_qframe(1, *args)

    def allocate_qubits(self, count: int, *args) -> List[str]:
        """ Allocates qubits. """

        self.logger.error("Sdqs backend uses qframe for allocate qubits! Returning 2xN qframe.")
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

    def allocate_qframes(self, frame_size: int, frame_count, *args) -> List[str]:
        """
        Allocates qubit from staticly created chunks.

        Args:
            frame_size: Frame Size.
            frame_count: Frame Count.

        Return:
            Qubit uuid(s).

        :arg[0] = initial state
        """

        initial_state = None
        if args.__len__() > 0:
            initial_state = args[0]

        to_return = list()
        low = 0
        high = 999999

        for i in range(low, high):
            current = self.int_to_static_chunks[i]
            if not current.allocated and current.qubit_count == frame_size:
                to_return.extend(current.virt_qubits_uuids)
                current.set_allocated(True)
                if initial_state is not None:
                    current.set_new_state(initial_state)
                frame_count -= 1

            if frame_count <= 0:
                break

        if frame_count > 0:
            raise OverflowError("Kernel cannot allocate {} qframe on {}.".format(frame_count, frame_size))
        return to_return

    def deallocate_qubit(self, qubits, args=None):
        """
        Deallocates qubit.

        Args:
            qubits: Qubit uuid.
            args: Backend spesific args.

        Return:
            Boolean.
        """

        if args is not None:
            self.logger.warning("Sdqs backend do not use args on deallocate qubit.")

        chunks = list()
        for qubit in qubits:
            chunk_index, qubit_index = qubit_id_resolver(qubit)
            key = int(chunk_index)
            chunk = self.int_to_static_chunks[key]

            if chunk not in chunks:
                chunks.append(chunk)

        for chunk in chunks:
            chunk.deallocate_chunk()
        return True

    def extend_qframe(self, qubit) -> str:
        """ Extends frame by qubit. """

        chunk_index, qubit_index = qubit_id_resolver(qubit)
        key = int(chunk_index)
        return self.int_to_static_chunks[key].extend_chunk()

    def apply_transformation(self, gate_id, gate_arguments, qubits, *args):
        pass
