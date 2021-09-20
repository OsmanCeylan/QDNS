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

default_scramble_percent = 0.5

# Implemented channels.
reset_channel = "reset channel"
depolarisation_channel = "depolarisation"
bit_flip_channel = "bit_flip_channel"
phase_flip_channel = "phase_flip_channel"
bit_and_phase_flip_channel = "bit_and_phase_flip"
no_noise_channel = "no noise channel"

channels = (
    depolarisation_channel,
    bit_flip_channel,
    phase_flip_channel,
    bit_and_phase_flip_channel,
    reset_channel,
    no_noise_channel
)


class NoisePattern(object):
    def __init__(
            self,
            sp_probability: float,
            measure_probability: float,
            gate_error_probability: float,
            sp_channel=bit_flip_channel,
            measure_channel=bit_flip_channel,
            gate_channel=depolarisation_channel,
            scramble_channel=depolarisation_channel,
    ):
        """
        Noise pattern of backend.

        Args:
            sp_probability: State Prepair Error Probability.
            measure_probability: Measure Error Probability.
            gate_error_probability: Gate Error Probability.
            sp_channel: State Prepair Error Channel.
            measure_channel: Measure Error Channel.
            gate_channel: Gate Error Channel.
            scramble_channel: Scramble Channel.

        Notes:
            Scramble channel method also used for quantum channel scrambling.
        """

        self.state_prepare_error_probability = sp_probability
        self.state_prepare_error_channel = sp_channel

        self.measure_error_probability = measure_probability
        self.measure_error_channel = measure_channel

        self.gate_error_probability = gate_error_probability
        self.gate_error_channel = gate_channel

        self.scramble_percent = default_scramble_percent
        self.scramble_channel = scramble_channel

    def __str__(self) -> str:
        text = str()
        text += "State Prepair: " + self.state_prepare_error_channel + " | " + str(self.state_prepare_error_probability) + "\n"
        text += "Measure: " + self.measure_error_channel + " | " + str(self.measure_error_probability) + "\n"
        text += "Gate Error: " + self.gate_error_channel + " | " + str(self.gate_error_probability) + "\n"
        text += "Scramble Error: " + self.scramble_channel + " | " + str(self.scramble_percent) + "\n"
        return text


default_noise_pattern = NoisePattern(
    0.00375, 0.00425, 0.00175,
    sp_channel=bit_flip_channel,
    measure_channel=bit_and_phase_flip_channel,
    gate_channel=phase_flip_channel,
    scramble_channel=depolarisation_channel,
)


def change_default_noise_pattern(new_pattern: NoisePattern):
    """ Changes default noise pattern. """

    global default_noise_pattern
    default_noise_pattern = new_pattern
