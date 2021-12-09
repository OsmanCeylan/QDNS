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

from typing import List, Sequence, Tuple, Optional
import logging
import time

from QDNS.simulation.tools import kernel_layer_label
from QDNS.tools.module import Module
from QDNS.tools.module import ModuleSettings
from QDNS.tools.layer import ID_SIMULATION

from QDNS.backend.tools.backend import Backend
from QDNS.backend.tools import config
from QDNS.backend.tools import noise

from QDNS.backend.cirq_backend import CirqBackend
from QDNS.backend.qiskit_backend import QiskitBackend
from QDNS.backend.sdqs_backend import SdqsBackend
from QDNS.backend.stim_backend import StimBackend

# Backend flags to object.
backend_flag_to_object = {
    config.CIRQ_BACKEND: CirqBackend,
    config.STIM_BACKEND: StimBackend,
    config.SDQS_BACKEND: SdqsBackend,
    config.QISKIT_BACKEND: QiskitBackend
}


class BackendWrapper(Module):
    """ Wrapper around backends and kernel. """

    backend_module_label = "Backend"

    def __init__(self):
        """
        Backend Wrapper object. Direct the backend calls to right backend.
        """

        self._backend_object: Optional[Backend] = None

        ms = ModuleSettings(
            can_disable=False, can_removalbe=False,
            can_restartable=False, no_state_module=True,
            logger_enabled=True
        )

        Module.__init__(
            self, layer_id=ID_SIMULATION[0], module_name=self.backend_module_label,
            module_logger_name="{}::{}".format(kernel_layer_label, self.backend_module_label),
            module_settings=ms
        )

    def start_module(self, configuration: config.BackendConfiguration, noise_pattern: noise.NoisePattern):
        """
        Prepares and starts the backend.

        Raises:
            AttributeError: When given backend is not found.
        """

        # Disable some logging for time being.
        logging.disable(logging.WARNING)
        start_time = time.time()

        # Check if backend is supported.
        if configuration.backend not in config.supported_backends:
            raise AttributeError("Backend {} is not supported.".format(configuration.backend))

        # Check if backend is avaible.
        if configuration.backend not in config.avaible_backends:
            raise AttributeError("Backend {} is not avaible in system.")

        # Prepare backend object.
        self._backend_object = backend_flag_to_object[configuration.backend](
            configuration, noise_pattern
        )

        # Open logging.
        logging.disable(logging.NOTSET)
        message = "{} is prepaired for simulation. Prepairation time: ~{} sec"
        self._logger.warning(message.format(self._backend_object.configuration.backend, round(time.time() - start_time, 4)))

    def terminate_backend(self):
        """ Terminates backend for this instance. """

        self._backend_object.terminate_backend()
        self._logger.info("Terminate backend -> {}.".format(self._backend_object.configuration.backend))

    def allocate_qubits(self, count: int, *args) -> List[str]:
        """
        Allocates qubit on backend.

        Args:
            count: Count of qubit.
            args: Backend specific arguments.

        Return:
            List[Qubit ID].
        """

        to_return = self._backend_object.allocate_qubits(count, *args)
        self._logger.debug("Allocate Qubits ({}) -> [{} ... {}]".format(to_return.__len__(), to_return[0], to_return[-1]))
        return to_return

    def allocate_qframes(self, frame_size: int, frame_count: int, *args) -> List[List[str]]:
        """
        Allocates qframe on backend.

        Args:
            frame_size: Frame size.
            frame_count: Frame count.
            args: Backend specific arguments.

        Return:
            List[List[Qubit ID]].
        """

        to_return = self._backend_object.allocate_qframes(frame_size, frame_count, *args)
        self._logger.debug("Allocate Frames ({}x{}) -> [{} ... {}]".format(
            to_return.__len__(), to_return[0].__len__(), to_return[0][0], to_return[-1][-1])
        )
        return to_return

    def deallocate_qubits(self, qubits: Sequence[str]) -> bool:
        """
        Deallocates qframes from backend.

        Args:
            qubits: List of qubits.

        Return:
            Bool.
        """

        if not self._backend_object.deallocate_qubits(qubits):
            self._logger.warning("Deallocation qubit may be failed!")
            return False

        self._logger.debug("Deallocate qubits ({}) -> [{} ... {}]".format(qubits.__len__(), qubits[0], qubits[-1]))
        return True

    def apply_transformation(self, gate_id: int, gate_arguments: Tuple, qubits: Sequence[str], *args):
        """
        Apply transformation on qubits.

        Args:
            gate_id: Gate id from QDNS.tools.gates.Gate()
            gate_arguments: Gate constructor arguments.
            qubits: Selected qubits.
        """

        self._backend_object.apply_transformation(gate_id, gate_arguments, qubits, *args)
        self._logger.debug("Apply gate of id {} to qubits ({}) -> {} ... {}.".format(gate_id, qubits.__len__(), qubits[0], qubits[-1]))

    def measure_qubits(self, qubits: Sequence[str], *args) -> List[int]:
        """
        Measures qubit.

        Args:
            qubits: Selected qubits.
            args: Backend specific arguments.

        Return:
            List[int].
        """

        results = self._backend_object.measure_qubits(qubits, *args)
        self._logger.debug(
            "Measure qubits ({}) -> [{} ... {}] -> [{} ... {}]".format(
                results.__len__(), qubits[0], qubits[-1], results[0], results[-1]
            )
        )
        return results

    def reset_qubits(self, qubits: Sequence[str]):
        """
        Reset Qubits.

        Args:
            qubits: Qubit uuids.
        """

        self._backend_object.reset_qubits(qubits)
        self._logger.debug("Reset qubits ({}) -> {} ... {}.".format(qubits.__len__(), qubits[0], qubits[-1]))

    def generate_ghz_pair(self, size: int, count: int) -> List[List[str]]:
        """
        Generates ghz pair.

        Args:
            size: Qubit count in ghz.
            count: Count of pairs.

        Return:
            List[List[Qubit ID]].
        """

        to_return = self._backend_object.generate_ghz_pair(size, count)
        self._logger.debug("Generate GHZ Pairs ({}x{}) -> [{} ... {}]".format(
            to_return.__len__(), to_return[0].__len__(), to_return[0][0], to_return[-1][-1])
        )
        return to_return

    def process_channel_error(self, qubits: Sequence[str], percent: float):
        """
        Process channel errors.

        Args:
            qubits: Qubits in channel.
            percent: Percent of channel.
        """

        to_return = self._backend_object.process_channel_error(qubits, percent)
        self._logger.debug("Apply channel error percent ({}) -> ({}) qubits".format(percent, qubits.__len__()))
        return to_return

    def apply_serial_transformations(self, list_of_gates: Sequence[List], *args):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[GateID, GateArgs, List[Qubit]].
        """

        self._backend_object.apply_serial_transformations(list_of_gates, *args)
        self._logger.debug("Applied serial {} gates.".format(list_of_gates.__len__()))

    def get_logs(self) -> str:
        """ Yileds the logs in the logger. """

        return self._logger.logs
