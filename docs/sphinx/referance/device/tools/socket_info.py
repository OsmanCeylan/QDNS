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
from QDNS.device.tools.port import Port
from QDNS.device.tools.port_manager import PortManager
from QDNS.device.tools.socket_tools import SocketSettings


class SocketInformation(object):
    def __init__(
            self, socket_state: str,
            host_device_id: device_tools.DeviceIdentification,
            socket_settings: SocketSettings, port_manager: PortManager
    ):
        """
        Socket Information.
        Used when user request information.
        """

        self._socket_state = socket_state
        self._host_device_label = host_device_id.label
        self._host_device_uuid = host_device_id.uuid
        self._max_cc_count = socket_settings.max_cc_count
        self._max_qc_count = socket_settings.max_qc_count
        self._port_count = port_manager.all_port_count
        self._cconnected_count = port_manager.classic_connected_port_count
        self._qconnected_count = port_manager.quantum_connected_port_count
        self._active_cconnected_count = port_manager.active_connected_classic_port_count
        self._active_qconnected_count = port_manager.active_connected_quantum_port_count

        self.printer = "Socket state: {}\n".format(socket_state)
        self.printer += host_device_id.__str__() + "\n" + socket_settings.__str__() + "\n" + port_manager.__str__()

    @property
    def socket_state(self):
        return self._socket_state

    @property
    def host_device_label(self) -> str:
        return self._host_device_label

    @property
    def host_device_uuid(self) -> str:
        return self._host_device_uuid

    @property
    def total_port_count(self) -> int:
        return self._port_count

    @property
    def classic_port_count(self) -> int:
        return self._max_cc_count

    @property
    def quantum_port_count(self) -> int:
        return self._max_qc_count

    @property
    def connected_classic_port_count(self) -> int:
        return self._cconnected_count

    @property
    def connected_quantum_port_count(self) -> int:
        return self._qconnected_count

    @property
    def active_connected_classic_port_count(self) -> int:
        return self._active_cconnected_count

    @property
    def active_connected_quantum_port_count(self) -> int:
        return self._active_qconnected_count

    def __str__(self) -> str:
        return self.printer


class ConnectivityInformation(object):
    def __init__(self, port_manager: PortManager, get_uuids):
        """
        Connectivity Information.
        Used when user request information.
        """

        self._classic_channel_uuids = port_manager.connected_classic_channel_uuids
        self._quantum_channel_uuids = port_manager.connected_quantum_channel_uuids
        self._classic_targets = list()
        self._quantum_targets = list()
        self._communication_state = port_manager.is_connectivity_open()

        for port in port_manager.connected_classic_ports:
            if not get_uuids:
                if port.target_device_id is not None:
                    self._classic_targets.append(port.target_device_id.label)
                else:
                    self._classic_targets.append("?")
            else:
                if port.target_device_id is not None:
                    self._classic_targets.append(port.target_device_id.uuid)
                else:
                    self._classic_targets.append("?")

        for port in port_manager.connected_quantum_ports:
            if not get_uuids:
                if port.target_device_id is not None:
                    self._quantum_targets.append(port.target_device_id.label)
                else:
                    self._quantum_targets.append("?")
            else:
                if port.target_device_id is not None:
                    self._quantum_targets.append(port.target_device_id.uuid)
                else:
                    self._quantum_targets.append("?")

    @property
    def classic_channels(self) -> list:
        return self._classic_channel_uuids

    @property
    def quantum_channels(self) -> list:
        return self._quantum_channel_uuids

    @property
    def classic_targets(self) -> list:
        return self._classic_targets

    @property
    def quantum_targets(self) -> list:
        return self._quantum_targets

    @property
    def communication_state(self) -> bool:
        return self._communication_state

    def __str__(self):
        to_return = str()
        to_return += "Classic UUIDs: {}\n".format(self._classic_channel_uuids)
        to_return += "Quantum UUIDs: {}\n".format(self._quantum_channel_uuids)
        to_return += "Classic Targets: {}\n".format(self._classic_targets)
        to_return += "Quantum Targets: {}\n".format(self._quantum_targets)
        to_return += "Communication State: {}\n".format(self._communication_state)
        return to_return


class PortInformation(object):
    def __init__(self, port: Port):
        """
        Port Information.
        Used when user request information.
        """

        self._port_index = port.index
        self._port_type = port.type_
        self._port_active = port.active
        self._port_connected = port.connected

        self._port_channel = None
        if port.connected:
            self._port_channel = port.channel_uuid

        self._port_target_label = None
        self._port_target_uuid = None

        if port.target_device_id is not None:
            self._port_target_label = port.target_device_id.label
            self._port_target_uuid = port.target_device_id.uuid

        self._port_latency = port.latency

    def is_active(self) -> bool:
        return self._port_active

    def is_connected(self) -> bool:
        return self._port_connected

    @property
    def port_index(self) -> int:
        return self._port_index

    @property
    def port_type(self):
        return self._port_type

    @property
    def channel_id(self):
        return self._port_channel

    @property
    def target_label(self):
        return self._port_target_label

    @property
    def target_uuid(self):
        return self._port_target_uuid

    @property
    def latency(self) -> float:
        return self._port_latency

    def __str__(self):
        to_return = str()
        to_return += "Index: {}\n".format(self._port_index)
        to_return += "Type: {}\n".format(self._port_type)
        to_return += "Active: {}\n".format(self._port_active)
        to_return += "Connected: {}\n".format(self._port_connected)
        to_return += "Target: {}, {}\n".format(self._port_target_label, self._port_target_uuid)
        to_return += "Latency: {}\n".format(self._port_latency)
        return to_return
