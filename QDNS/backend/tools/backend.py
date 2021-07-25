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


from typing import Sequence, List

from QDNS.backend.tools.config import BackendConfiguration
from QDNS.backend.tools.noise import NoisePattern


class Backend(object):
    def __init__(
            self, config: BackendConfiguration,
            noise_pattern: NoisePattern
    ):
        """
        Generic Backend.

        Args:
            config: Backend configuration.
            noise_pattern: Noise pattern for simulation.
        """

        self._configuration = config
        self._noise_pattern = noise_pattern

    def start_backend(self) -> bool:
        """ Starts the processes. """

        pass

    def terminate_backend(self):
        """ Terminates the backend. """

        pass

    def figure_allocation(self, frame_size: int, frame_count: int, dimension: int):
        """
        Figures allocation places.

        Args:
            frame_size: Frame size.
            frame_count: Frame count.
            dimension:  Dimension.
        """

        pass

    def figure_deallocation(self, qubits: Sequence[str]):
        """
        Figures the deallocation.

        Args
            qubits: List[Qubit ID].

        Return:
            Boolean.
        """

        pass

    def allocate_qubits(self, count: int, *args):
        """
        Allocates qubits.

        Args:
            count: Count of qubits.
        """

        pass

    def allocate_qframes(self, frame_size: int, frame_count: int, *args) -> List[List[str]]:
        """
        Allocates a qframe.

        Args:
            frame_size: Frame Size.
            frame_count: Frame Count.
            args: Backend specific arguments.

        Returns:
             List[Qubit ID]
        """

        pass

    def deallocate_qubits(self, qubits: Sequence[str]):
        """
        Deallocates qubits.

        Args:
            qubits: List[Qubit ID]
        """

        pass

    def apply_transformation(self, gate_id, gate_arguments, qubits: Sequence[str], *args):
        """
        Applies transformation on qubits.

        Args:
            gate_id: Gate Id.
            gate_arguments: Gate constructor args.
            qubits: Qubits.
        """

        pass

    def measure_qubits(self, qubits: Sequence[str], *args):
        """
        Measures qubits.

        Args:
            qubits: List[Qubit ID].
            args: Backend specific arguments.

        Returns:
            List[int]
        """

        pass

    def reset_qubits(self, qubits: Sequence[str]):
        """
        Reset Qubits.

        Args:
            qubits: List[Qubit ID]
        """

        pass

    def generate_ghz_pair(self, size: int, count: int):
        """
        Generates ghz pairs.

        Args:
            size: Size of qubits.
            count: Count of qubits.

        Return:
            List[List[QubitID]].
        """

        pass

    def process_channel_error(self, qubits, percent: float):
        """
        Process channel error.

        Args:
            qubits: Qubits in channel.
            percent: Error percent.
        """

        pass

    def apply_serial_transformations(self, list_of_gates: Sequence[List], *args):
        """
        Applies list of transformations.

        Args:
            list_of_gates: List[[GateID, GateArgs, List[Qubit]]].
        """

        pass

    @property
    def configuration(self) -> BackendConfiguration:
        return self._configuration

    @property
    def noise_pattern(self) -> NoisePattern:
        return self._noise_pattern
