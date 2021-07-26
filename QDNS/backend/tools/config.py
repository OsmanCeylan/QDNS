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


# Implemented backends.
CIRQ_BACKEND = "CIRQ backend"
QISKIT_BACKEND = "QISKIT backend"
SDQS_BACKEND = "SDQS backend"
STIM_BACKEND = "STIM backend"

supported_backends = (
    CIRQ_BACKEND,
    QISKIT_BACKEND,
    SDQS_BACKEND,
    STIM_BACKEND
)

avaible_backends = list()

# Check for avaible backends in system wide.
try:
    import cirq
except ImportError:
    pass
else:
    avaible_backends.append(CIRQ_BACKEND)

try:
    import qiskit
except ImportError:
    pass
else:
    avaible_backends.append(QISKIT_BACKEND)

try:
    import stim
except ImportError:
    pass
else:
    avaible_backends.append(STIM_BACKEND)

try:
    from QDNS.backend.sdqs_backend import SdqsBackend
except ImportError:
    pass
else:
    avaible_backends.append(SDQS_BACKEND)


class BackendConfiguration(object):
    def __init__(self, backend: str, process_count: int, frame_config: dict):
        """
        Backend configuration.

        Args:
            backend: Backend Flag.
            process_count: Process count.
            frame_config: Frame configuration dictionary.

        >>> BackendConfiguration(CIRQ_BACKEND, 4, {2: {1: 128, 2: 64, 3: 32}, 3: {1: 64, 2: 16}})
        >>> BackendConfiguration(QISKIT_BACKEND, 4, {2: {1: 128, 2: 64, 3: 32}})
        >>> BackendConfiguration(SDQS_BACKEND, 4, {2: {1: 128, 2: 64, 3: 32}})
        >>> BackendConfiguration(STIM_BACKEND, 1, {2: 50000})
        """

        self._backend = backend
        self._process_count = process_count
        self._frame_config = frame_config

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def process_count(self) -> int:
        return self._process_count

    @property
    def frame_config(self) -> dict:
        return self._frame_config

    def __int__(self) -> int:
        return self._process_count

    def __str__(self) -> str:
        to_return = str()
        to_return += "Backend: {}\n".format(self._backend)
        to_return += "Process Count: {}\n".format(self._process_count)
        to_return += "Frame Config: {}\n".format(self._frame_config)
        return to_return
