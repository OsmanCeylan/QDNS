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

class VirtQudit(object):
    """
    Virtual qudit template.
    CIRQ
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

    """
    Virtual qudit template.
    QISKIT
    #
    #  [PID]    [CH_IND]      [INDEX]
    #    |       00000          00
    #    |         |             |
    #    P       CHUNK           |
    #    0       00000          00
    #
    # Template supports pointing:
    #   Max 9 Process, 99999 circuit, 99 qubit in a circuit.
    #
    """

    """
    Virtual qudit template.
    STIM
    #       [QUBIT]
    #          |
    #          |
    #        000000
    #
    # Template supports pointing:
    #   Max 1 Process, 1 dimension, 999999 qubit.
    #
    """

    @staticmethod
    def qubit_id_resolver(qubit_id: str):
        """
        Qubit ID resolve from string.
        Must override.
        """

        pass

    @staticmethod
    def generate_pointer(*args) -> str:
        """
        Qubit ID Generator.
        Must override.
        """

        pass
