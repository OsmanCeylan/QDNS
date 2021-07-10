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

from typing import Optional

from QDNS.backend.sdqs_backend import SdqsBackend
from QDNS.backend.stim_backend import StimBackend
from QDNS.tools import simulation_tools
from QDNS.backend.cirq_backend import CirqBackend

CIRQ_BACKEND = "\"cirq_backend\""
PROJECTQ_BACKEND = "\"projectq_backend\""
SDQS_BACKEND = "\"smddqs_backend \""
STIM_BACKEND = "\"stim backend\""

supported_backends = (
    CIRQ_BACKEND,
    PROJECTQ_BACKEND,
    STIM_BACKEND,
    SDQS_BACKEND
)

avaible_backends = list()
default_backend = None

try:
    import stim
except ImportError:
    pass
else:
    avaible_backends.append(STIM_BACKEND)

try:
    import cirq
except ImportError:
    pass
else:
    avaible_backends.append(CIRQ_BACKEND)
avaible_backends.append(SDQS_BACKEND)


class BackendWrapper(simulation_tools.KernelModule):
    module_name = "BackendWrapper"

    def __init__(self):
        super(BackendWrapper, self).__init__(
            self.module_name, can_disable=False, can_removable=False,
            can_restartable=True, can_pausable=True, no_state_module=True
        )

        self._backend_obj: Optional[CirqBackend] = None
        self.noise_pattern: Optional[simulation_tools.NoisePattern] = None

    def prepair_module(self):
        if avaible_backends.__len__() <= 0:
            raise ImportWarning("There must be qubit simulator for run.")

        global default_backend
        default_backend = avaible_backends[0]

    def start_module(self, noise=None, backend_type=None):
        """
        Starts the module.

        Args:
            noise: Noise pattern.
            backend_type: Backend type.
        """

        if noise is None:
            noise = simulation_tools.default_noise_pattern

        if backend_type is None:
            backend_type = default_backend

        if backend_type == CIRQ_BACKEND:
            self._backend_obj = CirqBackend(noise)
            self._backend_obj.prepair_backend()

        elif backend_type == PROJECTQ_BACKEND:
            pass

        elif backend_type == SDQS_BACKEND:
            self._backend_obj = SdqsBackend(noise)
            self._backend_obj.prepair_backend()

        elif backend_type == STIM_BACKEND:
            self._backend_obj = StimBackend(noise)
            self._backend_obj.prepair_backend()

        else:
            raise AttributeError("Given backend {} is not recognized.".format(backend_type))

    def restart_backend(self, *args):
        """ Restarts backend. """

        return self._backend_obj.restart_engine(*args)

    def terminate_backend(self, *args):
        """ Terminates backend for this instance. """

        return self._backend_obj.terminate_engine(*args)

    def allocate_qubit(self, *args):
        """
        Allocates qubit on backend.

        Return:
            List[Qubit ID].
        """

        return self._backend_obj.allocate_qubit(*args)

    def allocate_qubits(self, count, *args):
        """
        Allocates qubit on backend.

        Args:
            count: Count of qubit.

        Return:
            List[Qubit ID].
        """

        return self._backend_obj.allocate_qubits(count, *args)

    def allocate_qframe(self, frame_size, *args):
        """
        Allocates qubit on backend.

        Args:
            frame_size: Frame size.

        Return:
            List[Qubit ID].
        """

        return self._backend_obj.allocate_qframe(frame_size, *args)

    def allocate_qframes(self, frame_size, frame_count, *args):
        """
        Allocates qubit on backend.

        Args:
            frame_size: Frame size.
            frame_count: Frame count.

        Return:
            List[Qubit ID].
        """

        return self._backend_obj.allocate_qframes(frame_size, frame_count, *args)

    def deallocate_qubits(self, qubits):
        """
        Deallocates qubits from backend.

        Args:
            qubits: List of qubits.

        Return:
            Bool.
        """

        return self._backend_obj.deallocate_qubit(qubits)

    def extend_circuit(self, qubit):
        """
        Extend qframe from back.

        Return:
            Qubit ID.
        """

        return self._backend_obj.extend_qframe(qubit)

    def apply_transformation(self, gate_id, gate_arguments, qubits, *args):
        """
        Apply transformation on qubits.

        Args:
            gate_id: Gate id from QDNS.tools.gates.Gate()
            gate_arguments: Gate constructor arguments.
            qubits: Selected qubits.

        Return:
            Bool.
        """

        return self._backend_obj.apply_transformation(gate_id, gate_arguments, qubits, *args)

    def measure(self, qubits, *args):
        """
        Measures qubit.

        Args:
            qubits: Selected qubits.

        Return:
            List[int].
        """

        return self._backend_obj.measure(qubits, *args)

    def reset_qubits(self, qubits, *args):
        """
        Reset Qubits.

        Args:
            qubits: Qubit uuids.

        Return:
            Boolean.
        """

        return self._backend_obj.reset_qubits(qubits, *args)

    def generate_epr_pairs(self, count, *args):
        """
        Generates epr pairs.

        Args:
            count: Count of pairs.

        Return:
            List[Qubit IDs].
        """

        return self._backend_obj.generate_epr_pairs(count, *args)

    def generate_ghz_pair(self, size, *args):
        """
        Generates ghz pair.

        Args:
            size: Qubit count in ghz.

        Return:
            List[Qubit IDs].
        """

        return self._backend_obj.generate_ghz_pair(size, *args)

    def process_channel_error(self, qubits, percent):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.

        Return:
             Boolean.
        """

        return self._backend_obj.process_channel_error(qubits, percent)

    def apply_serial_transformations(self, list_of_gates):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[GateID, GateArgs, List[Qubit]].

        Return:
            Boolean.
        """

        return self._backend_obj.apply_serial_transformations(list_of_gates)
