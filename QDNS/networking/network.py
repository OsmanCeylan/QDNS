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

import uuid
from typing import List, Union

import matplotlib.pyplot as plt
import networkx

from QDNS.device.channel import Channel, ClassicChannel
from QDNS.device.channel import QuantumChannel
from QDNS.device.channel import default_channel_length
from QDNS.device.device import Device


class Network(object):
    def __init__(self, *devices: Device):
        """
        Simple nxnetwork gparh holder object.

        Args:
            devices: Device open list.

        Notes:
            Do not add if device already exists.
        """

        self.device_list: List[Device] = list()
        self.classic_channels: List[ClassicChannel] = list()
        self.quantum_channels: List[QuantumChannel] = list()
        self.classic_network = networkx.Graph()
        self.quantum_network = networkx.Graph()

        for device in devices:
            if device not in self.device_list:
                self.device_list.append(device)
                self.classic_network.add_node(device.uuid)
                self.quantum_network.add_node(device.uuid)

    def add_device(self, *devices: Device):
        """
        Add device(s) to network.

        Args:
            devices: Device(s) for add.

        Notes:
            Do not add if device already exists.
        """

        for device in devices:
            if device not in self.device_list:
                self.device_list.append(device)
                self.classic_network.add_node(device)
                self.quantum_network.add_node(device)

    def add_classic_channel(self, device_l: Device, device_r: Device):
        """
        Adds classic channel between devices.

        Args:
            device_l: Left device.
            device_r: Right device.

        Raises:
            NetworkError: If channel is exist between devices.
        """

        for channel in self.classic_channels:
            if channel.devL_ID == device_l.device_id and channel.devR_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )
            if channel.devR_ID == device_l.device_id and channel.devL_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )

        channel = ClassicChannel(device_l, device_r)
        self.classic_channels.append(channel)
        self.classic_network.add_edge(device_l.uuid, device_r.uuid)

    def add_quantum_channel(self, device_l: Device, device_r: Device, length=default_channel_length):
        """
        Adds quantum channel between devices.

        Args:
            device_l: Left device.
            device_r: Right device.
            length: Legth of channel.

        Raises:
            NetworkError: If channel is exist between devices.
        """

        for channel in self.quantum_channels:
            if channel.devL_ID == device_l.device_id and channel.devR_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )
            if channel.devR_ID == device_l.device_id and channel.devL_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )

        channel = QuantumChannel(device_l, device_r, length)
        self.quantum_channels.append(channel)
        self.quantum_network.add_edge(device_l.uuid, device_r.uuid)

    def add_channels(self, device_l: Device, device_r: Device, length=default_channel_length):
        """
        Adds classic and quantum channel between devices.

        Args:
            device_l: Left device.
            device_r: Right device.
            length: Legth of channel.

        Raises:
            NetworkError: If channel is exist between devices.
        """

        for channel in self.quantum_channels:
            if channel.devL_ID == device_l.device_id and channel.devR_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )
            if channel.devR_ID == device_l.device_id and channel.devL_ID == device_r.device_id:
                raise networkx.NetworkXError(
                    "There is a channel between device {} and device {}.".format(device_l.label, device_r.label)
                )

        channel = QuantumChannel(device_l, device_r, length)
        self.quantum_channels.append(channel)
        self.quantum_network.add_edge(device_l.uuid, device_r.uuid)

        channel = ClassicChannel(device_l, device_r, length=length)
        self.classic_channels.append(channel)
        self.classic_network.add_edge(device_l.uuid, device_r.uuid)

    def get_all_devices(self) -> List[Device]:
        """
        Gets the device list in network.
        """

        return self.device_list

    def get_classic_channel_route(self, uuid_l, uuid_r):
        """
        Finds classical route.

        Args:
            uuid_l: Letf device uuid.
            uuid_r: Right device uuid.

        Returns:
            List[uuid] or None.
        """

        try:
            route = networkx.shortest_path(self.classic_network, source=uuid_l, target=uuid_r)
            to_delete = list()
            for node in route:
                for device in self.get_all_devices():
                    if node == device.uuid and device.otg_device:
                        to_delete.append(node)
                        break
            for item in to_delete:
                route.remove(item)
            return route
        except networkx.NetworkXNoPath:
            return None

    def get_quantum_channel_route(self, uuid_l, uuid_r):
        """
        Finds quantum route.

        Args:
            uuid_l: Letf device uuid.
            uuid_r: Right device uuid.

        Returns:
            List[uuid] or None.
        """

        try:
            route = networkx.shortest_path(self.quantum_network, source=uuid_l, target=uuid_r)
            to_delete = list()
            for node in route:
                for device in self.get_all_devices():
                    if node == device.uuid and device.otg_device:
                        to_delete.append(node)
                        break
            for item in to_delete:
                route.remove(item)
            return route
        except networkx.NetworkXNoPath:
            return None

    def get_channel(self, key: Union[str, int, ClassicChannel, QuantumChannel, uuid.UUID], raise_=True) -> Union[Channel, None]:
        """
        Finds the channel in network by givent key.

        Args:
            key: Unique identifier of channel.
            raise_: Raise flag.

        Return:
            Channel object or None.

        Raises:
            KeyError: If channel is not found while raise flag active.
        """

        for i in range(self.quantum_channels.__len__()):
            if isinstance(key, int) and key == i:
                return self.quantum_channels[i]

            elif isinstance(key, str) and key == self.quantum_channels[i].label:
                return self.quantum_channels[i]

            elif isinstance(key, str) and key == self.quantum_channels[i].uuid:
                return self.quantum_channels[i]

            elif isinstance(key, uuid.UUID) and key == self.quantum_channels[i].uuid:
                return self.quantum_channels[i]

            elif isinstance(key, QuantumChannel) and key == self.quantum_channels[i]:
                return self.quantum_channels[i]

            else:
                pass

        for i in range(self.classic_channels.__len__()):
            if isinstance(key, int) and key == i:
                return self.classic_channels[i]

            elif isinstance(key, str) and key == self.classic_channels[i].label:
                return self.classic_channels[i]

            elif isinstance(key, str) and key == self.classic_channels[i].uuid:
                return self.classic_channels[i]

            elif isinstance(key, uuid.UUID) and key == self.classic_channels[i].uuid:
                return self.classic_channels[i]

            elif isinstance(key, ClassicChannel) and key == self.classic_channels[i]:
                return self.classic_channels[i]

            else:
                pass

        if raise_:
            raise KeyError("Channel is not found by given key {}.".format(key))
        return None

    def unconnect_channel(self, uuid_l, uuid_r, classic=True, quantum=True) -> bool:
        """
        Finds classical route.

        Args:
            uuid_l: Letf device uuid.
            uuid_r: Right device uuid.
            classic: Search in classic.
            quantum: Search in quantum.

        Notes:
            Provide exact information about channel type.
            Else removes what it find in both network.

        Returns:
            List[uuid] or None.
        """

        if classic:
            try:
                self.classic_network.remove_edge(uuid_l, uuid_r)
            except networkx.NetworkXError:
                pass
            else:
                return True

        if quantum:
            try:
                self.quantum_network.remove_edge(uuid_l, uuid_r)
            except networkx.NetworkXError:
                pass
            else:
                return True
        return False

    def draw_classic_network(self):
        """
        Draw classic network.
        """

        networkx.draw_circular(self.classic_network)
        plt.draw()

    def draw_quantum_network(self):
        """
        Draw quantum network.
        """

        networkx.draw_circular(self.quantum_network)
        plt.draw()
