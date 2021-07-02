"""
## ===========================================#
##  Header of QDNS/backend/stim.py            #
## ===========================================#

## ===========================================#
## Brief                                      #
## Contains STIM Backend                      #
## ===========================================#
"""

try:
    import stim
except ImportError:
    stim = None

from typing import List, Union, Type
import numpy as np

from QDNS.tools.instance_logger import SubLogger
from QDNS.tools import simulation_tools
from QDNS.tools import gates

tableau_simulator = stim.TableauSimulator()
circuit_simulator = stim.Circuit()

supported_operations = dict()
supported_operations[gates.IDGate.gate_id] = gates.IDGate
supported_operations[gates.PauliX.gate_id] = gates.PauliX
supported_operations[gates.PauliY.gate_id] = gates.PauliY
supported_operations[gates.PauliZ.gate_id] = gates.PauliZ
supported_operations[gates.HGate.gate_id] = gates.HGate
supported_operations[gates.SGate.gate_id] = gates.SGate
supported_operations[gates.SWAPGate.gate_id] = gates.SWAPGate
supported_operations[gates.ISWAPGate.gate_id] = gates.ISWAPGate
supported_operations[gates.CXGate.gate_id] = gates.CXGate
supported_operations[gates.CYGate.gate_id] = gates.CYGate
supported_operations[gates.CZGate.gate_id] = gates.CZGate


class VirtQudit(object):
    def __init__(self, index: int):
        """
        Virtual qudit object.
        Hold a pointer for a qubit.
        """

        # [C_IND]
        # 000000

        self.__uuid = "{:06d}".format(index)

    @property
    def uuid(self):
        return self.__uuid

    @property
    def index(self):
        return int(self.__uuid)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__uuid == other

    def __str__(self):
        return "Qudit Id: {}.".format(self.__uuid)


class BitFlipChannel(object):
    """ Bit flip channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - p, p]
        self.compose_channel = [gates.IDGate, gates.PauliX]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self._p:
            return self.compose_channel[1],
        else:
            return self.compose_channel[0],


class PhaseFlipChannel(object):
    """ Phase flip channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - p, p]
        self.compose_channel = [gates.IDGate, gates.PauliZ]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self._p:
            return self.compose_channel[1],
        else:
            return self.compose_channel[0],


class YFlipChannel(object):
    """ Y flip channel or Bit and Phase Flip channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - p, p]
        self.compose_channel = [gates.IDGate, [gates.PauliX, gates.PauliZ]]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self._p:
            return self.compose_channel[1]
        else:
            return self.compose_channel[0],


class DepolarizingChannel(object):
    """ Depolarizing channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - self._p, self._p / 3, self._p / 3, self._p / 3]
        self.compose_channel = [gates.IDGate, gates.PauliX, gates.PauliY, gates.PauliZ]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self._p:
            final_gates = list()
            random_ = np.random.uniform()
            if random_ <= self._p:
                final_gates.append(self.compose_channel[1])
            random_ = np.random.uniform()
            if random_ <= self._p:
                final_gates.append(self.compose_channel[2])
            random_ = np.random.uniform()
            if random_ <= self._p:
                final_gates.append(self.compose_channel[3])
            if final_gates.__len__() <= 0:
                final_gates.append(self.compose_channel[np.random.randint(1, 4)])
            return final_gates
        else:
            return self.compose_channel[0],


class AsymmetricDepolarizingChannel(object):
    """ Asymmetric Depolarizing Channel """

    def __init__(self, p_x: float, p_y: float = 0.01, p_z: float = 0.01) -> None:
        self.p_x, self.p_y, self.p_z = p_x, p_y, p_z
        self.total = p_x + p_y + p_z

        if self.total > 1.001:
            raise ValueError("Total error rate cannot higher than 1.")

        self.compose_props = [1.0 - self.total, self.p_x, self.p_y, self.p_z]
        self.compose_channel = [gates.IDGate, gates.PauliX, gates.PauliY, gates.PauliZ]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self.total:
            final_gates = list()
            random_ = np.random.uniform()
            if random_ <= self.p_x:
                final_gates.append(self.compose_channel[1])
            random_ = np.random.uniform()
            if random_ <= self.p_y:
                final_gates.append(self.compose_channel[2])
            random_ = np.random.uniform()
            if random_ <= self.p_z:
                final_gates.append(self.compose_channel[3])
            if final_gates.__len__() <= 0:
                final_gates.append(self.compose_channel[np.random.randint(1, 4)])
            return final_gates
        else:
            return self.compose_channel[0],


class ResetChannel(object):
    """ Reset channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - p, p]
        self.compose_channel = [gates.IDGate, "R"]

    def get_gates(self):
        random_ = np.random.uniform()
        if random_ <= self._p:
            return self.compose_channel[1],
        else:
            return self.compose_channel[0],


class NoNoiseChannel(object):
    """ No noise channel """

    def __init__(self, p: float) -> None:
        self._p = p
        self.compose_props = [1.0 - p, p]
        self.compose_channel = [gates.IDGate, gates.IDGate]

    def get_gates(self):
        return self.compose_channel[0],


def get_channel_gate(flag: str) -> Union[Type[BitFlipChannel], Type[PhaseFlipChannel],
                                         Type[YFlipChannel], Type[DepolarizingChannel],
                                         Type[ResetChannel], Type[NoNoiseChannel],
                                         Type[AsymmetricDepolarizingChannel]]:
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


class StimBackend:
    def __init__(self, noise_pattern: simulation_tools.NoisePattern):
        """
        STIM backend constructor.

        Args:
            noise_pattern: Noise pattern for this simulation.

        See QDNS.tools.simulation_tools.NoisePattern() for details.
        """

        self.logger = SubLogger("STIM Backend")
        self.noise_pattern = noise_pattern
        self.virt_qubits: List[VirtQudit] = list()
        self.circuit = tableau_simulator
        self.deallocated_qubits: List[int] = list()

    def prepair_backend(self):
        self.deallocated_qubits.clear()
        self.virt_qubits.clear()

        if self.circuit == circuit_simulator:
            self.circuit.clear()

    def restart_engine(self, *args) -> bool:
        """ Restarts Stim Backend. """

        if args.__len__() > 0:
            self.logger.warning("Stim backend do not use restart flags.")

        self.deallocated_qubits.clear()
        self.virt_qubits.clear()
        self.circuit.clear()
        return True

    def terminate_engine(self, *args):
        """ Terminates Stim Backend. """

        if args.__len__() > 0:
            self.logger.warning("Stim backend do not use restart flags.")

        self.deallocated_qubits = None
        self.virt_qubits = None
        self.circuit = None

    def allocate_qubit(self, *args) -> List[str]:
        """ Allocates qubit. """

        if args.__len__() > 0:
            self.logger.warning("Stim do not use arguments for allocate qubit.")

        if self.deallocated_count > 0:
            index = self.deallocated_qubits.pop()
            return [self.virt_qubits[index].uuid]

        new = VirtQudit(self.qubit_count)
        self.virt_qubits.append(new)

        self.scramble_qubits(self.noise_pattern.state_prepare_error_channel, (new.uuid,),
                             self.noise_pattern.state_prepare_error_probability)
        return [new.uuid]

    def allocate_qubits(self, count: int, *args) -> List[str]:
        """ Allocates qubits. """

        if args.__len__() > 0:
            self.logger.warning("Stim do not use arguments for allocate qubits.")

        to_return = list()
        if self.deallocated_count > 0:
            for i in range(count):
                try:
                    index = self.deallocated_qubits.pop()
                except IndexError:
                    break
                else:
                    to_return.append(self.virt_qubits[index].uuid)
                    count -= 1

        for i in range(count):
            new = VirtQudit(self.qubit_count)
            self.virt_qubits.append(new)
            to_return.append(new.uuid)

        self.scramble_qubits(self.noise_pattern.state_prepare_error_channel, to_return,
                             self.noise_pattern.state_prepare_error_probability)
        return to_return

    def allocate_qframe(self, frame_size, *args) -> List[str]:
        """
        Creates chunk and allocates qubit inside the chunk.

        Args:
            frame_size: Qubit count of circuit.
            args: Definition in below.

        Return:
            List of qubit uuids.
        """

        self.logger.error("Stim cannot allocate qframes. Returning N qubits.")
        return self.allocate_qubits(frame_size, *args)

    def allocate_qframes(self, frame_size: int, frame_count, *args) -> List[str]:
        """
        Allocates qubit from staticly created chunks.

        Args:
            frame_size: Frame Size.
            frame_count: Frame Count.

        Return:
            Qubit uuid(s).
        """

        self.logger.error("Stim cannot allocate qframes. Returning MxN qubits.")
        return self.allocate_qubits(frame_size * frame_count, *args)

    def deallocate_qubit(self, qubits) -> bool:
        """
        Deallocates qubit.

        Args:
            qubits: Qubit uuid.

        Return:
            Boolean.
        """

        for qubit in qubits:
            key = int(qubit)
            try:
                self.virt_qubits[key].__hash__()
            except IndexError:
                pass
            else:
                self.deallocated_qubits.append(key)
                self.reset_qubits((key,))
        return True

    def apply_transformation(self, gate_id, gate_arguments, qubits, *args) -> bool:
        """
        Apply transformation on qubits.

        Args:
            gate_id: Gate ID.
            gate_arguments: Gate constructor arguments.
            qubits: Qubits

        Return:
            Boolean.
        """

        if gate_arguments.__len__() > 0:
            self.logger.error("STIM backend do not use gate arguments.")

        appy_noise = False if args.__len__() > 0 and args[0] else True

        if gate_id not in supported_operations.keys():
            raise AttributeError("Gate {} is not supported on STIM.".format(gate_id))

        indexes = [int(i) for i in qubits]

        if self.circuit == circuit_simulator:
            self.circuit.append_operation(supported_operations[gate_id].stim_alias, indexes)
        else:
            if gate_id == gates.IDGate.gate_id:
                pass
            elif gate_id == gates.PauliX.gate_id:
                self.circuit.x(*indexes)
            elif gate_id == gates.PauliY.gate_id:
                self.circuit.y(*indexes)
            elif gate_id == gates.PauliZ.gate_id:
                self.circuit.z(*indexes)
            elif gate_id == gates.HGate.gate_id:
                self.circuit.h(*indexes)
            elif gate_id == gates.SGate.gate_id:
                self.circuit.s(*indexes)
            elif gate_id == gates.SWAPGate.gate_id:
                self.circuit.swap(*indexes)
            elif gate_id == gates.ISWAPGate.gate_id:
                self.circuit.iswap(*indexes)
            elif gate_id == gates.CXGate.gate_id:
                self.circuit.cnot(*indexes)
            elif gate_id == gates.CYGate.gate_id:
                self.circuit.cy(*indexes)
            elif gate_id == gates.CZGate.gate_id:
                self.circuit.cz(*indexes)
            else:
                raise AttributeError("Gate {} is not supported on STIM.".format(gate_id))

        if appy_noise:
            self.scramble_qubits(self.noise_pattern.gate_error_channel, qubits,
                                 self.noise_pattern.gate_error_probability)
        return True

    def measure(self, qubits, *args) -> List[int]:
        """
        Measures qubits.

        :arg[0] => Non-destructive.
        """

        non_destructive = True if args.__len__() > 0 and args[0] else False

        indexes = [int(i) for i in qubits]

        if self.circuit == circuit_simulator:
            self.scramble_qubits(self.noise_pattern.measure_error_channel, qubits, self.noise_pattern.measure_error_probability)
            self.circuit.append_operation("M", indexes)
            if not non_destructive:
                self.scramble_qubits(self.noise_pattern.scramble_channel, qubits, (0.8,))
            sampler = self.circuit.compile_sampler()
            batch = sampler.sample(1)
            return batch[0][-qubits.__len__():]
        else:
            self.scramble_qubits(self.noise_pattern.measure_error_channel, qubits, self.noise_pattern.measure_error_probability)
            to_return = [int(i) for i in self.circuit.measure_many(*indexes)]
            if not non_destructive:
                self.scramble_qubits(self.noise_pattern.scramble_channel, qubits, (0.8,))
            return to_return

    def reset_qubits(self, qubits, *args):
        """
        Reset Qubits.

        Args:
            qubits: Qubit uuids.
            args: Backend spesific arguments.

        Return:
            Boolean.
        """

        if args.__len__() > 0:
            self.logger.error("STIM backend do not use arguments on reset.")

        indexes = [int(i) for i in qubits]
        if self.circuit == circuit_simulator:
            self.circuit.append_operation("R", indexes)
        else:
            self.circuit.reset(*indexes)
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
            self.logger.warning("STIM backend do not use args on generate entange pairs.")

        qubits = self.allocate_qubits(2 * count)
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
            self.logger.warning("STIM backend do not use args on generate ghz pair.")

        qubits = self.allocate_qframe(size, *args)
        self.apply_transformation(gates.HGate.gate_id, (), (qubits[0],))
        for i in range(size - 1):
            self.apply_transformation(gates.CXGate.gate_id, (), (qubits[i], qubits[i + 1]))
        return qubits

    def scramble_qubits(self, channel, qubits, percents):
        """
        Scramble qubits by given channel and percents.

        Args:
            channel: Channel of error FLAG.
            qubits: Qubits.
            percents: Percent tuple of scramble that constructs channel object.
        """

        channel = get_channel_gate(channel)(*percents)
        for qubit in qubits:
            for gate in channel.get_gates():
                if gate == "R":
                    self.reset_qubits((qubit,))
                else:
                    self.apply_transformation(gate.gate_id, (), (qubit,), True)

    def process_channel_error(self, qubits, percent):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.

        Return:
             Boolean.
        """

        # This value is already cheked few times to make sure not raise.
        if percent < 0.001 or percent > 1.001:
            raise ValueError("Percent must be in range of 0 and 1.")

        channel = self.noise_pattern.scramble_channel
        self.scramble_qubits(channel, qubits, (percent,))

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

    @property
    def qubit_count(self):
        return self.virt_qubits.__len__()

    @property
    def deallocated_count(self):
        return self.deallocated_qubits.__len__()
