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
from QDNS.device.tools.device_tools import DeviceIdentification
from QDNS.tools import various_tools

CLASSIC_PORT = "Classic port type"
QUANTUM_PORT = "Quantum port type"


class Port(object):
    def __init__(
            self, index: int, _type: str,
            active: bool = True, receive_queue=None
    ):
        """
        A Port of network socket.

        Args:
            index: Index of port
            _type: Type of port.
            active: Active port.
            receive_queue: Sets manager receive queue.
        """

        if _type != CLASSIC_PORT and _type != QUANTUM_PORT:
            raise ValueError("Port type must be classic or quantum not {}".format(_type))

        self._index = index
        self._type = _type
        self._active = active
        self._connected = False
        self._side = None

        self._channel = None
        self._receive_queue = receive_queue
        self._put_queue = None
        self._target_device_id = None
        self._latency = None

    def change_index(self, new_index: int):
        """ Changes the port index. """

        self._index = new_index

    def set_receive_queue(self, new_queue):
        """ Sets port receive queue. """

        self._receive_queue = new_queue

    def set_put_queue(self, new_queue):
        """ Sets port put queue. """

        self._put_queue = new_queue

    def set_queues(self, new_put, new_receive):
        """ Sets put/receive queues. """

        self._put_queue = new_put
        self._receive_queue = new_receive

    def set_side(self, new_side: str):
        """ Sets the side. (L or R) """

        self._side = new_side

    def set_target_device_id(self, new_id: DeviceIdentification):
        """ Set target device id. """

        self._target_device_id = new_id

    def set_latency(self, latency: float):
        """ Sets the port latency. """

        self._latency = round(latency, 5)

    def flush_put_queue(self):
        """ Flushes put queue. """

        if self._put_queue is None:
            return

        various_tools.flush_queue(self._put_queue)

    def set_active(self, flag=True):
        """ Sets port as active. """

        self._active = flag

    def unconnect_channel(self, soft=True) -> bool:
        """ Unconnects a channel. """

        if self._connected is False:
            return False

        self._connected = False
        self._target_device_id = None
        self._latency = None
        self.set_active(False)

        if not soft:
            self._side = None
            self._channel = None
            self._put_queue = None
        return True

    def reconnect_channel(self) -> bool:
        """ Reconnects a channel. """

        if self.connected:
            return False

        if self._channel is None:
            return False

        if self._put_queue is None:
            return False

        self._connected = True
        self.set_active(True)
        return True

    def is_unconnected(self) -> bool:
        """ Returns if port connected. """

        if not self._connected and self.channel is not None:
            return True
        return False

    def connect_channel(self, channel, put_queue, override=False):
        """ Connects a channel. """

        if self._connected and not override:
            return False

        self._connected = True
        self._channel = channel
        self._put_queue = put_queue

    def is_classic_type(self) -> bool:
        """ Returns if port is classic type. """

        if self._type == CLASSIC_PORT:
            return True
        return False

    def is_quantum_type(self) -> bool:
        """ Returns if port is quantum type. """

        if self._type == QUANTUM_PORT:
            return True
        return False

    @property
    def channel(self):
        return self._channel

    @property
    def index(self) -> int:
        return self._index

    @property
    def target_device_id(self):
        return self._target_device_id

    @property
    def active(self) -> bool:
        return self._active

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def channel_uuid(self):
        if self.channel is None:
            return None
        return self._channel.uuid

    @property
    def put_queue(self):
        return self._put_queue

    @property
    def receive_queue(self):
        return self._receive_queue

    @property
    def type_(self):
        return self._type

    @property
    def side(self):
        return self._side

    @property
    def latency(self):
        return self._latency

    def __int__(self) -> int:
        return self._index

    def __str__(self) -> str:
        to_return = str()
        to_return += "Port: {}\n".format(self._index)
        to_return += "Type: {}\n".format(self._type)
        to_return += "Active: {}\n".format(self._active)
        to_return += "Connected: {}\n".format(self._connected)
        to_return += "Channel: {}\n".format(self.channel_uuid)
        to_return += "Side: {}\n".format(self._side)

        if self._put_queue is None:
            bind = False
        else:
            bind = True

        to_return += "Put Binded: {}\n".format(bind)

        if self._receive_queue is None:
            bind = False
        else:
            bind = True
        to_return += "Receive Binded: {}\n".format(bind)

        to_return += "Connected To: {}\n".format(self._target_device_id)
        to_return += "Latency: {}\n".format(self._latency)
        return to_return
