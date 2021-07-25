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

from QDNS.device.tools import device_tools
from QDNS.tools.various_tools import fiber_formula

default_channel_length = 1.0
default_altitude_formula = fiber_formula

LEFT_SIDE = "left side of channel"
RIGHT_SIDE = "rigth side of channel"


class Channel(object):
    def __init__(self, device_l, device_r, length):
        """
        Channel super object.

        Args:
            device_l: Left device.
            device_r: Right device.
            length: Length of channel.
        """

        self._device_l_id = device_l.device_id
        self._device_r_id = device_r.device_id

        self._length = length
        if self._length is None:
            self._length = default_channel_length

        self._channel_id = device_tools.ChannelIdentification(
            label="{}-{}".format(self._device_r_id.label, self._device_l_id.label),
            use_uuid=False
        )

        # Make sure quantum channel change this.
        self.percentage = 0.0

    @property
    def length(self):
        return self._length

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def devL_ID(self):
        return self._device_l_id

    @property
    def devR_ID(self):
        return self._device_r_id

    @property
    def label(self) -> str:
        return self._channel_id.label

    @property
    def uuid(self):
        return self._channel_id.uuid

    def __str__(self):
        return str(self._channel_id)


class QuantumChannel(Channel):
    def __init__(self, device_l, device_r, length):
        """
        Represents as quantum channel.

        Args:
            device_l: Left device.
            device_r: Right device.
            length: Length of channel.
        """

        super(QuantumChannel, self).__init__(device_l, device_r, length)
        self.port_r = device_r.ntwk_socket.connect_quantum_channel(self)
        self.port_l = device_l.ntwk_socket.connect_quantum_channel(self)

        self.port_l.set_put_queue(self.port_r.receive_queue)
        self.port_r.set_put_queue(self.port_l.receive_queue)

        self.port_l.set_side(LEFT_SIDE)
        self.port_r.set_side(RIGHT_SIDE)

        self.port_l.set_target_device_id(self.devR_ID)
        self.port_r.set_target_device_id(self.devL_ID)
        self.percentage = default_altitude_formula(self.length)


class ClassicChannel(Channel):
    def __init__(self, device_l, device_r, length=None):
        """
        Represents as classic channel.

        Args:
            device_l: Left device.
            device_r: Right device.
            length: Length of channel.
        """

        super(ClassicChannel, self).__init__(device_l, device_r, length)
        self.port_r = device_r.ntwk_socket.connect_classic_channel(self)
        self.port_l = device_l.ntwk_socket.connect_classic_channel(self)

        self.port_l.set_put_queue(self.port_r.receive_queue)
        self.port_r.set_put_queue(self.port_l.receive_queue)

        self.port_l.set_side(LEFT_SIDE)
        self.port_r.set_side(RIGHT_SIDE)

        self.port_l.set_target_device_id(self.devR_ID)
        self.port_r.set_target_device_id(self.devL_ID)


def change_default_connection_length(new_length: float):
    """
    Changes the default length of channels in km.
    Make sure use before the construct of network object.
    """

    if new_length < 0.1:
        raise ValueError("Channel lenght cannot lower then 0.1 km.")
    global default_channel_length
    default_channel_length = new_length


def change_default_altitude_formula(new_formula_function):
    """
    Changes the channel altitude calculation formula.
    Formula must take only one parameter: length.
    """

    global default_altitude_formula
    default_altitude_formula = new_formula_function
