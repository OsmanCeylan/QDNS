"""
## ==========================================##
##  Header of QF/device/channel.py           ##
## ==========================================##

## ==========================================##
## Brief                                     ##
## Contains Classic / Quantum Channel Obj.   ##
## ==========================================##
"""

from QDNS.tools import device_tools
from QDNS.tools.various_tools import fiber_formula

default_channel_length = 1.0

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
        self.percentage = fiber_formula(self.length)


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
