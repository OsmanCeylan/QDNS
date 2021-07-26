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

from typing import Union, Type, List, Sequence, Tuple
import numpy as np

from QDNS.backend.tools.virt_qubit import VirtQudit
from QDNS.backend.tools.backend import Backend
from QDNS.backend.tools import config
from QDNS.backend.tools import noise
from QDNS.tools import gates

# Check if avaible.
try:
    import stim
except ImportError:
    stim = None
    tableau_simulator = None
else:
    tableau_simulator = stim.TableauSimulator()

selected_simulator = tableau_simulator

# SUPPORTED GATES

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


# QUBIT POINTER

class VirtQudit(VirtQudit):
    """
    Virtual qudit template.
    """

    #       [QUBIT]
    #          |
    #          |
    #        000000
    #
    # Template supports pointing:
    #   Max 1 Process, 1 dimension, 999999 qubit.
    #

    qubit_length = 7

    @staticmethod
    def qubit_id_resolver(qubit_id: str):
        """
        Qubit ID resolve from string.
        Returns index
        """

        return int(qubit_id)

    @staticmethod
    def generate_pointer(index) -> str:
        """
        Qubit ID Generator.
        """

        return "{:07d}".format(index)


# NOISE CHANNELS

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
                                         Type[ResetChannel], Type[NoNoiseChannel]]:
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


# STIM BACKEND


class StimBackend(Backend):
    def __init__(
            self,
            configuration: config.BackendConfiguration,
            noise_pattern: noise.NoisePattern):
        """
        Stim Backend.

        Args:
            configuration: Stim backend configuration.
            noise_pattern: Noise pattern for simulation.
        """

        super().__init__(configuration, noise_pattern)
        self._qubit_memory_index: List[int] = list()
        self._qubit_memory_allocation: List[int] = list()
        self.start_backend()

    def start_backend(self):
        """ Inıtializes the backend. """

        try:
            _ = self.configuration.frame_config[2]
        except KeyError:
            raise ValueError("Stim backend expected key 2 from chunk configuration.")
        else:
            if self.configuration.frame_config[2] >= np.power(10, VirtQudit.qubit_length):
                raise OverflowError("Stim is limited to allocate 10^^{} qubits.".format(VirtQudit.qubit_length))
            self._qubit_memory_index = np.arange(self.configuration.frame_config[2])
            self._qubit_memory_allocation = np.zeros(self.configuration.frame_config[2])

    def terminate_backend(self):
        """ Terminates the backend. """

        del self._qubit_memory_index
        del self._qubit_memory_allocation
        global tableau_simulator
        tableau_simulator = None

    def allocate_qubits(self, count: int, *args) -> List[str]:
        """
        Allocates qubits.

        Args:
            count: Count of qubits.
        """

        t = count
        indexes = list()
        for i, allocation in enumerate(self._qubit_memory_allocation):
            if allocation == 0:
                self._qubit_memory_allocation[i] = 1
                indexes.append(i)
                t -= 1

            if t <= 0:
                break

        if indexes.__len__() < count:
            raise OverflowError("There is no space to allocate more qubits.")

        qubits = [VirtQudit.generate_pointer(i) for i in indexes]
        self.scramble_qubits(self.noise_pattern.state_prepare_error_channel, qubits,
                             self.noise_pattern.state_prepare_error_probability)
        return qubits

    def allocate_qframes(self, frame_size: int, frame_count: int, *args) -> List[List[str]]:
        """ Allocates qframes on backend. """

        return [self.allocate_qubits(frame_size) for _ in range(frame_count)]

    def deallocate_qubits(self, qubits: Sequence[str]) -> bool:
        """ Deallocates qframes from backend. """

        indexes = [VirtQudit.qubit_id_resolver(i) for i in qubits]
        self.reset_qubits(qubits)
        for index in indexes:
            self._qubit_memory_allocation[index] = 0
        return True

    def extend_circuit(self, qubit: str, size: int) -> List[str]:
        """
        Extend qframe from back.
        Just returns with more allocation.
        """

        _ = qubit
        return self.allocate_qubits(size)

    def apply_transformation(self, gate_id: int, gate_arguments: Tuple, qubits: Sequence[str], *args):
        """
        Apply transformation on qubits.

        Args:
            gate_id: Gate ID.
            gate_arguments: Gate constructor arguments.
            qubits: Qubits

        :arg[0] Apply gate noise flag.
        """

        apply_noise = False if args.__len__() > 0 and args[0] else True

        if gate_id not in supported_operations.keys():
            raise AttributeError("Gate {} is not supported on STIM.".format(gate_id))

        indexes = [VirtQudit.qubit_id_resolver(i) for i in qubits]
        if gate_id == gates.IDGate.gate_id:
            pass
        elif gate_id == gates.PauliX.gate_id:
            tableau_simulator.x(*indexes)
        elif gate_id == gates.PauliY.gate_id:
            tableau_simulator.y(*indexes)
        elif gate_id == gates.PauliZ.gate_id:
            tableau_simulator.z(*indexes)
        elif gate_id == gates.HGate.gate_id:
            tableau_simulator.h(*indexes)
        elif gate_id == gates.SGate.gate_id:
            tableau_simulator.s(*indexes)
        elif gate_id == gates.SWAPGate.gate_id:
            tableau_simulator.swap(*indexes)
        elif gate_id == gates.ISWAPGate.gate_id:
            tableau_simulator.iswap(*indexes)
        elif gate_id == gates.CXGate.gate_id:
            tableau_simulator.cnot(*indexes)
        elif gate_id == gates.CYGate.gate_id:
            tableau_simulator.cy(*indexes)
        elif gate_id == gates.CZGate.gate_id:
            tableau_simulator.cz(*indexes)
        else:
            raise AttributeError("Gate {} is not supported on STIM.".format(gate_id))

        if apply_noise:
            self.scramble_qubits(self.noise_pattern.gate_error_channel, qubits,
                                 self.noise_pattern.gate_error_probability)

    def measure_qubits(self, qubits: Sequence[str], *args) -> List[int]:
        """
        Measures qubits.

        :arg[0] => Non-destructive.
        """

        non_destructive = args[0] if args.__len__() > 0 else False
        indexes = [VirtQudit.qubit_id_resolver(i) for i in qubits]

        if not non_destructive:
            self.scramble_qubits(
                self.noise_pattern.measure_error_channel, qubits,
                self.noise_pattern.measure_error_probability
            )

        to_return = [int(i) for i in tableau_simulator.measure_many(*indexes)]
        if not non_destructive:
            self.scramble_qubits(self.noise_pattern.scramble_channel, qubits, 0.57)
        return to_return

    def reset_qubits(self, qubits: Sequence[str], *args):
        """ Reset Qubits. """

        indexes = [VirtQudit.qubit_id_resolver(i) for i in qubits]
        tableau_simulator.reset(*indexes)

    def generate_ghz_pair(self, size: int, count: int, *args):
        """ Generates ghz pairs. """

        qubits_frame = self.allocate_qframes(size, count, *args)

        for qubits in qubits_frame:
            self.apply_transformation(gates.HGate.gate_id, (), (qubits[0],))
            for i in range(size - 1):
                self.apply_transformation(gates.CXGate.gate_id, (), (qubits[i], qubits[i + 1]))
        return qubits_frame

    def scramble_qubits(self, channel: str, qubits: Sequence[str], percent: float):
        """
        Scramble qubits by given channel and percent.

        Args:
            channel: Channel of error FLAG.
            qubits: Qubits.
            percent: Percent tuple of scramble that constructs channel object.
        """

        channel = get_channel_gate(channel)(percent)
        for qubit in qubits:
            for gate in channel.get_gates():
                if gate == "R":
                    self.reset_qubits((qubit,))
                else:
                    self.apply_transformation(gate.gate_id, (), (qubit,), True)

    def process_channel_error(self, qubits: Sequence[str], percent: float, *args):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.
            args: Backend specific arguments.
        """

        # This value is already cheked few times to make sure not raise.
        if percent < 0.001 or percent > 1.001:
            raise ValueError("Percent must be in range of 0 and 1.")

        channel = self.noise_pattern.scramble_channel
        self.scramble_qubits(channel, qubits, percent)

    def apply_serial_transformations(self, list_of_gates, *args):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[GateID, GateArgs, List[Qubit]].
        """

        for gate_instructor in list_of_gates:
            self.apply_transformation(gate_instructor[0], gate_instructor[1], gate_instructor[2], *args)
