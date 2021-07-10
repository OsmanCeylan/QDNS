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
import multiprocessing
from typing import List, Dict, Union

from QDNS.architecture import signal
from QDNS.tools import architecture_tools
from QDNS.tools import various_tools
from QDNS.tools import device_tools

RELEASE_PACKAGE = "RELEASE PACKAGE"
DROP_PACKAGE = "DROP PACKAGE"

"""
##===============================================  SOCKET STATES  ====================================================##
"""

SOCKET_IS_DOWN = "\"socket down\""
SOCKET_IS_UP = "\"socket up\""
SOCKET_PAUSED = "\"socket paused\""
SOCKET_IS_OVER = "\"socket is over\""

socket_states = (
    SOCKET_IS_DOWN,
    SOCKET_IS_UP,
    SOCKET_PAUSED,
    SOCKET_IS_OVER,
)

default_ping_time = 2.5

"""
##=============================================  SOCKET SETTINGS  ====================================================##
"""

max_classic_connection = 999
max_quantum_connection = 999


class SocketSettings(architecture_tools.AnySettings):
    def __init__(
            self, max_cc_count: int, max_qc_count: int, auto_ping=True,
            ping_time=default_ping_time, clear_route_cache=False,
            remove_future_packages=True, enable_routing=True,
            enable_qkd=True
    ):
        """
        Socket settings for a device adapter.

        Args:
            max_cc_count: Maximum classic port count.
            max_qc_count: Maximum quantum port count.
            auto_ping: Auto ping targets.
            ping_time: Ping timing.
            remove_future_packages: Drop future dated packages.
            enable_routing: Enable routing module.
            enable_qkd: Enable qkd module.
        """

        self._max_cc_count = max_cc_count
        if self._max_cc_count < 0:
            self._max_cc_count = 8

        self._max_qc_count = max_qc_count
        if self._max_qc_count < 0:
            self._max_qc_count = 8

        self._auto_ping = auto_ping
        self._ping_time = ping_time
        self._remove_future_packages = remove_future_packages
        self._enable_routing = enable_routing
        self._enable_qkd = enable_qkd
        self.__clear_route_cache = clear_route_cache

        super(SocketSettings, self).__init__(
            max_cc_count=self._max_cc_count,
            max_qc_count=self._max_qc_count,
            auto_ping=self._auto_ping,
            ping_time=self._ping_time,
            clear_route_cache=self.__clear_route_cache,
            remove_future_packages=self._remove_future_packages,
            enable_routing=self._enable_routing,
            enable_qkd=self._enable_qkd
        )

    def is_routing_enabled(self) -> bool:
        return self._enable_routing

    def is_qkd_enabled(self) -> bool:
        return self._enable_qkd

    @property
    def max_cc_count(self) -> int:
        return self._max_cc_count

    @property
    def max_qc_count(self) -> int:
        return self._max_qc_count

    @property
    def auto_ping(self) -> bool:
        return self._auto_ping

    @property
    def ping_time(self) -> float:
        return self._ping_time

    @property
    def remove_future_packages(self) -> bool:
        return self._remove_future_packages

    @property
    def clear_route_cache(self) -> bool:
        return self.__clear_route_cache

    def __str__(self):
        to_return = str()
        to_return += "Auto Ping: {}\n".format(self.auto_ping)
        to_return += "Ping Time: {}\n".format(self.ping_time)
        to_return += "Enable Routing: {}".format(self.is_routing_enabled())
        return to_return


default_socket_settings = SocketSettings(
    8, 8, auto_ping=True, ping_time=default_ping_time,
    clear_route_cache=False, remove_future_packages=True,
    enable_routing=True, enable_qkd=True
)


def change_default_socket_settings(new_socket_settings: SocketSettings):
    """
    Changes the deafult socket settings.
    """

    global default_socket_settings
    default_socket_settings = new_socket_settings


def change_default_ping_time(new_time: float):
    """
    Changes the drafult ping time.
    """

    global default_ping_time
    default_ping_time = new_time


"""
##===============================================  PORT MODULE  ======================================================##
"""

CLASSIC_PORT = "Classic port type"
QUANTUM_PORT = "Quantum port type"

use_simple_queue_for_ports = True


class Port(object):
    def __init__(self, index, _type, active=True, receive_queue=None):
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
        self._index = new_index

    def set_receive_queue(self, new_queue):
        self._receive_queue = new_queue

    def set_put_queue(self, new_queue):
        self._put_queue = new_queue

    def set_queues(self, new_put, new_receive):
        self._put_queue = new_put
        self._receive_queue = new_receive

    def set_side(self, new_side):
        self._side = new_side

    def set_target_device_id(self, new_id):
        self._target_device_id = new_id

    def set_latency(self, latency):
        self._latency = round(latency, 5)

    def flush_put_queue(self):
        if self._put_queue is None:
            return

        various_tools.flush_queue(self._put_queue)

    def set_active(self, flag=True):
        self._active = flag

    def unconnect_channel(self, soft=True) -> bool:
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
        if not self._connected and self.channel is not None:
            return True
        return False

    def connect_channel(self, channel, put_queue, override=False):
        if self._connected and not override:
            return False

        self._connected = True
        self._channel = channel
        self._put_queue = put_queue

    def is_classic_type(self) -> bool:
        if self._type == CLASSIC_PORT:
            return True
        return False

    def is_quantum_type(self) -> bool:
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


COMMUNICATION_UP = "\"communication is up\""
COMMUNICATION_DOWN = "\"communication is down\""

port_manager_states = (
    COMMUNICATION_UP,
    COMMUNICATION_DOWN
)


class PortManager(architecture_tools.Module):
    max_cc_port_count = 99
    max_qc_port_count = 99
    module_name = "Port Manager"

    def __init__(self, host_id, cc_port_capacity=max_cc_port_count, qc_port_capacity=max_qc_port_count):
        """
        Port Manager module for network socket.

        Args:
            host_id: Device Id.
            cc_port_capacity: Classic port capacity.
            qc_port_capacity: Quantum port capacity.
        """

        state_handler = architecture_tools.StateHandler(
            architecture_tools.ID_SOCKET[0],
            False, *port_manager_states,
            GENERAL_STATE_IS_RUNNING=COMMUNICATION_UP,
            GENERAL_STATE_IS_STOPPED=COMMUNICATION_DOWN
        )

        super(PortManager, self).__init__(
            architecture_tools.ID_SOCKET[0], self.module_name, self, can_disable=False,
            can_removable=False, can_pausable=False, no_state_module=False, special_state=state_handler
        )

        self._host_id = host_id
        self._cc_port_count = cc_port_capacity
        self._qc_port_count = qc_port_capacity

        self._classic_ports: List[Port] = list()
        self._quantum_ports: List[Port] = list()

        self._classic_ports_by_uuid: Dict[uuid.UUID, Port] = dict()
        self._quantum_ports_by_uuid: Dict[uuid.UUID, Port] = dict()

        self._active_classic_ports: List[Port] = list()
        self._active_quantum_ports: List[Port] = list()

        self._connected_classic_ports: List[Port] = list()
        self._connected_quantum_ports: List[Port] = list()

        self._active_connected_classic_ports: List[Port] = list()
        self._active_connected_quantum_ports: List[Port] = list()

        self._connected_classic_channel_uuids: List[uuid.UUID] = list()
        self._connected_quantum_channels_uuids: List[uuid.UUID] = list()

        self._unconnected_ports: List[Port] = list()
        self._unconnected_ports_to_values = dict()

        self._all_ports: List[Port] = list()
        self._port_process_counts: Dict[Port, int] = dict()

        self._sim_request_queue = None

        if use_simple_queue_for_ports:
            self._classic_receive_queue = multiprocessing.SimpleQueue()
            self._quantum_receive_queue = multiprocessing.SimpleQueue()
        else:
            self._classic_receive_queue = multiprocessing.Queue()
            self._quantum_receive_queue = multiprocessing.Queue()

        self.generate_ports()
        self.state_object.change_state(COMMUNICATION_UP)

    def generate_ports(self):
        """ Generate ports. This must be call after module is created. """

        self._classic_ports.clear()
        self._quantum_ports.clear()

        self._classic_ports_by_uuid.clear()
        self._quantum_ports_by_uuid.clear()

        self._active_classic_ports.clear()
        self._active_quantum_ports.clear()

        self._connected_classic_ports.clear()
        self._connected_quantum_ports.clear()

        self._active_connected_classic_ports.clear()
        self._active_connected_quantum_ports.clear()

        self._connected_classic_channel_uuids.clear()
        self._connected_quantum_channels_uuids.clear()
        self._port_process_counts.clear()
        self._unconnected_ports.clear()
        self._unconnected_ports_to_values.clear()

        self._all_ports.clear()

        for i in range(self._cc_port_count):
            p = Port(i, CLASSIC_PORT, receive_queue=self._classic_receive_queue)
            self._classic_ports.append(p)
            if p.active:
                self._active_classic_ports.append(p)
            if p.connected:
                self._connected_classic_ports.append(p)
                self._classic_ports_by_uuid[p.channel_uuid] = p
                self._connected_classic_channel_uuids.append(p.channel_uuid)
            if p.active and p.connected:
                self._active_connected_classic_ports.append(p)
            self._all_ports.append(p)
            self._port_process_counts[p] = 0

        for i in range(self._qc_port_count):
            p = Port(i, QUANTUM_PORT, receive_queue=self._quantum_receive_queue)
            self._quantum_ports.append(p)
            if p.active:
                self._active_quantum_ports.append(p)
            if p.connected:
                self._connected_quantum_ports.append(p)
                self._quantum_ports_by_uuid[p.channel_uuid] = p
                self._connected_quantum_channels_uuids.append(p.channel_uuid)
            if p.active and p.connected:
                self._active_connected_quantum_ports.append(p)
            self._all_ports.append(p)
            self._port_process_counts[p] = 0

    def set_sim_request_queue(self, the_queue):
        self._sim_request_queue = the_queue

    def add_port(self, new_port: Port):
        """ Not recommended. """

        if new_port.type_ == CLASSIC_PORT:
            if self.classic_port_count >= self.cc_port_capacity:
                raise OverflowError("Port count exceeds port capacity. Cannot advance adding ports.")
            else:
                self._classic_ports.append(new_port)
                if new_port.active:
                    self._active_classic_ports.append(new_port)
                if new_port.connected:
                    self._connected_classic_ports.append(new_port)
                    new_port.set_receive_queue(self._classic_receive_queue)
                    if new_port.channel_uuid in self._connected_classic_channel_uuids:
                        raise ValueError("New port connected channel is already connected to another port in {} device."
                                         .format(self.host_label))
                    self._classic_ports_by_uuid[new_port.channel_uuid] = new_port
                    self._connected_classic_channel_uuids.append(new_port.channel_uuid)
                if new_port.active and new_port.connected:
                    self._active_connected_classic_ports.append(new_port)
            new_port.change_index(self.classic_port_count)

        else:
            if self.quantum_port_count >= self.qc_port_capacity:
                raise OverflowError("Port count exceeds port capacity. Cannot advance adding ports.")
            else:
                self._quantum_ports.append(new_port)
                if new_port.active:
                    self._active_quantum_ports.append(new_port)
                if new_port.connected:
                    self._connected_quantum_ports.append(new_port)
                    new_port.set_receive_queue(self._quantum_receive_queue)
                    if new_port.channel_uuid in self._connected_quantum_channels_uuids:
                        raise ValueError(
                            "New port connected channel is already connected to another port in {} device.".format(self.host_label)
                        )
                    self._quantum_ports_by_uuid[new_port.channel_uuid] = new_port
                    self._connected_quantum_channels_uuids.append(new_port.channel_uuid)
                if new_port.active and new_port.connected:
                    self._active_connected_quantum_ports.append(new_port)
            new_port.change_index(self.quantum_port_count)
        self._all_ports.append(new_port)

    def get_port(self, key: Union[int, uuid.UUID, str, Port], classic=False, quantum=True, _raise=True) -> Union[Port, None]:
        """
        Gets port object from given key.

        Args:
            key: Port identifier. Port index or Channel Id.
            classic: Search in only classic.
            quantum: Search in only quantum.
            _raise: Raise if enconter None.

        Returns:
            Port or None.
        """

        if isinstance(key, int):
            if classic:
                try:
                    return self._classic_ports[key]
                except (KeyError, IndexError) as E:
                    if _raise:
                        raise E("Index {} of classic port do not exsist.")
                    else:
                        return None

            if quantum:
                try:
                    return self._quantum_ports[key]
                except (KeyError, IndexError) as E:
                    if _raise:
                        raise E("Index {} of quantum port do not exsist.")
                    else:
                        return None

            if _raise:
                raise ValueError("Find port from index failed.")
            else:
                return None

        elif isinstance(key, uuid.UUID):
            if classic:
                for port in self._classic_ports:
                    if port.channel_uuid == key:
                        return port

                for port in self._classic_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.uuid == key:
                            return port

            if quantum:
                for port in self._quantum_ports:
                    if port.channel_uuid == key:
                        return port

                for port in self._quantum_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.uuid == key:
                            return port

            if _raise:
                raise ValueError("Find port from index failed.")
            else:
                return None

        elif isinstance(key, str):
            if classic:
                for port in self._classic_ports:
                    if port.channel_uuid == key:
                        return port

                for port in self._classic_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.uuid == key:
                            return port

                for port in self._classic_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.label == key:
                            return port

            if quantum:
                for port in self._quantum_ports:
                    if port.channel_uuid == key:
                        return port

                for port in self._quantum_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.uuid == key:
                            return port

                for port in self._quantum_ports:
                    if port.target_device_id is not None:
                        if port.target_device_id.label == key:
                            return port

            if _raise:
                raise ValueError("Find port from index failed.")
            else:
                return None

        elif isinstance(key, Port):
            if classic:
                if key in self._classic_ports:
                    return key

            if quantum:
                if key in self._quantum_ports:
                    return key

            if _raise:
                raise ValueError("Find port from object failed. Port is not on this device.")
            else:
                return None

        else:
            raise ValueError("Port can find onlt integer, str or uuids. Not {}".format(type(key)))

    def find_next_avaible_port(self, classic=False, quantum=True, must_active=True, _raise=False) -> Union[Port, None]:
        """
        Tries to find next avaible port on device sokcet.

        Args:
            classic: Search classic ports.
            quantum: Search quantum ports.
            must_active: Must be active port.
            _raise: Raises if not found.

        Returns:
             Port or None.
        """

        if classic:
            for port in self.classic_ports:
                if not port.connected:
                    if port.active and must_active:
                        return port
                    if not must_active:
                        return port

        if quantum:
            for port in self.quantum_ports:
                if not port.connected:
                    if port.active and must_active:
                        return port
                    if not must_active:
                        return port

        if _raise:
            raise ConnectionAbortedError("There is no more avaible port on device {}.".format(self.host_label))
        return None

    def connect_channel(self, _type, channel) -> Port:
        """
        Connects channel to port.
        This operation must be done in two steps.
        Must be setted queues after connect.

        Args:
            _type: Channel type.
            channel: Channel.

        Returns:
            Port or None.
        """

        if _type == CLASSIC_PORT:
            if channel.uuid in self._connected_classic_channel_uuids:
                return self.classic_ports_by_uuid[channel.uuid]
            else:
                to_return = self.find_next_avaible_port(classic=True, quantum=False, must_active=True, _raise=True)
                to_return.connect_channel(channel, None, override=True)
                if to_return.receive_queue is None:
                    to_return.set_receive_queue(self._classic_receive_queue)
                self._connected_classic_channel_uuids.append(channel.uuid)
                self.classic_ports_by_uuid[to_return.channel_uuid] = to_return

                if to_return.active:
                    self.active_connected_classic_ports.append(to_return)
                self._connected_classic_ports.append(to_return)

        else:
            if channel.uuid in self._connected_quantum_channels_uuids:
                return self.quantum_ports_by_uuid[channel.uuid]
            else:
                to_return = self.find_next_avaible_port(classic=False, quantum=True, must_active=True, _raise=True)
                to_return.connect_channel(channel, None, override=True)
                if to_return.receive_queue is None:
                    to_return.set_receive_queue(self._quantum_receive_queue)
                self._connected_quantum_channels_uuids.append(channel.uuid)
                self.quantum_ports_by_uuid[to_return.channel_uuid] = to_return

                if to_return.active:
                    self.active_connected_quantum_ports.append(to_return)
                self._connected_quantum_ports.append(to_return)
        return to_return

    def send_information(self, port: Port, information, check_active=True) -> bool:
        """
        Sends information throught port.

        Args:
            port: The port.
            information: Information.
            check_active: Chech port state befre send.

        Returns:
            True if send processes.
        """

        expected_states = (COMMUNICATION_UP,)
        if self.state not in expected_states:
            return False

        if port.connected:
            if check_active and port.active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            if not check_active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            return True
        else:
            return False

    def send_classic_information(self, port: Port, information, check_active=True) -> bool:
        """
        Sends classic information throught port.

        Args:
            port: The port.
            information: Information.
            check_active: Chech port state befre send.

        Returns:
            True if send processes.
        """

        if port.type_ != CLASSIC_PORT:
            return False

        expected_states = (COMMUNICATION_UP,)
        if self.state not in expected_states:
            return False

        if port.connected:
            if check_active and port.active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            if not check_active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            return True
        else:
            return False

    def send_quantum_information(self, port: Port, information, check_active=True) -> bool:
        """
        Sends quantum information throught port.

        Args:
            port: The port.
            information: Information.
            check_active: Chech port state befre send.

        Returns:
            True if send processes.
        """

        if not port.is_quantum_type():
            return False

        expected_states = (COMMUNICATION_UP,)
        if self.state not in expected_states:
            return False

        if port.connected:
            if check_active and port.active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            if not check_active:
                port.put_queue.put((port.channel_uuid, information))
                self._port_process_counts[port] += 1

            return True
        else:
            return False

    def unconnect_port(self, port: Port, soft=True) -> bool:
        """
        Unconnects a port.

        Args:
            port: Port object.
            soft: Reconnectable flag.

        Return:
            True if unconnect happen.
        """

        target_device_id = port.target_device_id
        channel_uuid = port.channel_uuid

        if port.is_classic_type():
            try:
                self._connected_classic_ports.remove(port)
            except ValueError:
                pass

            try:
                self._active_connected_classic_ports.remove(port)
            except ValueError:
                pass

            try:
                self._active_classic_ports.remove(port)
            except ValueError:
                pass

            try:
                self._connected_classic_channel_uuids.remove(port.channel_uuid)
            except ValueError:
                pass
            to_return = port.unconnect_channel(soft=soft)

        elif port.is_quantum_type():
            try:
                self._connected_quantum_ports.remove(port)
            except ValueError:
                pass

            try:
                self._active_quantum_ports.remove(port)
            except ValueError:
                pass

            try:
                self._active_connected_quantum_ports.remove(port)
            except ValueError:
                pass

            try:
                self._connected_quantum_channels_uuids.remove(port.channel_uuid)
            except ValueError:
                pass
            to_return = port.unconnect_channel(soft=soft)

        else:
            raise AttributeError("Port type is unknown.")

        if soft:
            self._unconnected_ports.append(port)
            self._unconnected_ports_to_values[port] = target_device_id, channel_uuid

        if to_return:
            signal.ConnectionChangedSignal(
                self.host_uuid, target_device_id.uuid, channel_uuid, "DROP", self.host_uuid
            ).emit(self.sim_request_queue)

        return to_return

    def reconnect_port(self, port: Port) -> bool:
        """
        Reconnects a port.
        Port should be in unconnected list.

        Args:
            port: Port object.

        Return:
            True if reconnect happen.
        """

        if port not in self.unconnected_ports:
            return False

        if port.is_classic_type():
            if not port.reconnect_channel():
                return False

            self._classic_ports_by_uuid[port.channel_uuid] = port
            self._connected_classic_ports.append(port)
            self._active_classic_ports.append(port)
            self._active_connected_classic_ports.append(port)
            self._connected_classic_channel_uuids.append(port.channel_uuid)

        elif port.is_quantum_type():
            if not port.reconnect_channel():
                return False

            self._quantum_ports_by_uuid[port.channel_uuid] = port
            self._connected_quantum_ports.append(port)
            self._active_quantum_ports.append(port)
            self._active_connected_quantum_ports.append(port)
            self._connected_quantum_channels_uuids.append(port.channel_uuid)

        else:
            raise AttributeError("Port type is unknown.")

        self.unconnected_ports.remove(port)
        target_device_id, channel_uuid = self._unconnected_ports_to_values[port]
        port.set_target_device_id(target_device_id)

        signal.ConnectionChangedSignal(
            self.host_uuid, port.target_device_id.uuid, port.channel_uuid, "RESTORE", self.host_uuid
        ).emit(self.sim_request_queue)
        return True

    def connect_classic_channel(self, channel) -> Union[Port, None]:
        """
        Connects channel to port.
        This operation must be done in two steps.
        Must be setted queues after connect.

        Args:
            channel: Channel.

        Returns:
            Port or None.
        """

        return self.connect_channel(CLASSIC_PORT, channel)

    def connect_quantum_channel(self, channel) -> Union[Port, None]:
        """
        Connects channel to port.
        This operation must be done in two steps.
        Must be setted queues after connect.

        Args:
            channel: Channel.

        Returns:
            Port or None.
        """

        return self.connect_channel(QUANTUM_PORT, channel)

    def get_classic_receive(self, block=True, timeout=None):
        """
        Waits for classic package.

        Args:
            block: Get blocks.
            timeout: Get timeout.

        Return:
            (Port, Package)
        """

        func = self._classic_receive_queue.get
        args = []

        expected_states = (COMMUNICATION_UP,)

        if not use_simple_queue_for_ports:
            args.append(block)
            args.append(timeout)

        while 1:
            ch_uuid, package = func(*args)

            if self.state in expected_states:
                if ch_uuid in self.connected_classic_channel_uuids:
                    port = self.classic_ports_by_uuid[ch_uuid]
                    self._port_process_counts[port] += 1
                    return port, package

                else:
                    port = self.classic_ports_by_uuid[ch_uuid]
                    if port in self._unconnected_ports:
                        return port, package

    def get_quantum_receive(self, block=True, timeout=None):
        """
        Waits for quantum package.

        Args:
            block: Get blocks.
            timeout: Get timeout.

        Return:
            (Port, Qupack)
        """

        func = self._quantum_receive_queue.get
        args = []

        expected_states = (COMMUNICATION_UP,)

        if not use_simple_queue_for_ports:
            args.append(block)
            args.append(timeout)

        while 1:
            ch_uuid, qupack = func(*args)
            if self.state in expected_states:
                if ch_uuid in self.connected_quantum_channel_uuids:
                    port = self.quantum_ports_by_uuid[ch_uuid]
                    return port, qupack

                else:
                    port = self.quantum_ports_by_uuid[ch_uuid]
                    if port in self._unconnected_ports:
                        return port, qupack

    def activate_port(self, port_: Port) -> bool:
        """ Activates a port. """

        state_change = False
        if not port_.active:
            state_change = True

        port_.set_active(True)
        if port_.is_classic_type() and port_ not in self._active_classic_ports:
            self._active_classic_ports.append(port_)

            if port_.connected and port_ not in self._active_connected_classic_ports:
                self._active_connected_classic_ports.append(port_)

            return state_change

        if port_.is_quantum_type() and port_ not in self._active_quantum_ports:
            self._active_quantum_ports.append(port_)

            if port_.connected and port_ not in self._active_connected_quantum_ports:
                self._active_connected_quantum_ports.append(port_)

            return state_change

    def deactivate_port(self, port_: Port) -> bool:
        """ Deactivates a port. """

        state_change = False
        if port_.active:
            state_change = True

        port_.set_active(False)
        if port_.is_classic_type() and port_ in self._active_classic_ports:
            self._active_classic_ports.remove(port_)

            if port_.connected and port_ in self._active_connected_classic_ports:
                self._active_connected_classic_ports.remove(port_)

            return state_change

        if port_.is_quantum_type() and port_ in self._active_quantum_ports:
            self._active_quantum_ports.remove(port_)

            if port_.connected and port_ in self._active_connected_quantum_ports:
                self._active_connected_quantum_ports.remove(port_)

            return state_change

    def is_connectivity_open(self) -> bool:
        if self.state == COMMUNICATION_UP:
            return True
        return False

    def is_connectivity_close(self) -> bool:
        if self.state == COMMUNICATION_DOWN:
            return True
        return False

    def open_connectivity(self) -> bool:
        """
        Opens connectivity.

        Return:
            True if state changes.
        """

        expected_states = (COMMUNICATION_DOWN,)
        if self.state in expected_states:
            self.flush_income_queues()
            self.state_object.change_state(COMMUNICATION_UP)
            return True
        return False

    def close_connectivity(self) -> bool:
        """
        Closes connectivity.

        Return:
            True if state changes.
        """

        expected_states = (COMMUNICATION_UP,)
        if self.state in expected_states:
            self.flush_income_queues()
            self.state_object.change_state(COMMUNICATION_DOWN)
            return True
        return False

    def flush_income_classic_queue(self):
        """ Flushes income classic ports. """

        various_tools.flush_queue(self._classic_receive_queue)

    def flush_income_quantum_queue(self):
        """ Flushes income quantum ports. """

        various_tools.flush_queue(self._quantum_receive_queue)

    def flush_income_queues(self):
        """ Flushes income ports. """

        self.flush_income_classic_queue()
        self.flush_income_quantum_queue()

    @property
    def host_label(self) -> str:
        return self._host_id.label

    @property
    def host_uuid(self) -> str:
        return self._host_id.uuid

    @property
    def cc_port_capacity(self) -> int:
        return self._cc_port_count

    @property
    def qc_port_capacity(self) -> int:
        return self._qc_port_count

    @property
    def classic_ports(self) -> List[Port]:
        return self._classic_ports

    @property
    def quantum_ports(self) -> List[Port]:
        return self._quantum_ports

    @property
    def classic_ports_by_uuid(self) -> Dict[uuid.UUID, Port]:
        return self._classic_ports_by_uuid

    @property
    def quantum_ports_by_uuid(self) -> Dict[uuid.UUID, Port]:
        return self._quantum_ports_by_uuid

    @property
    def active_classic_ports(self) -> List[Port]:
        return self._active_classic_ports

    @property
    def active_quantum_ports(self) -> List[Port]:
        return self._active_quantum_ports

    @property
    def active_connected_classic_ports(self) -> List[Port]:
        return self._active_connected_classic_ports

    @property
    def active_connected_classic_port_count(self) -> int:
        return self._active_connected_classic_ports.__len__()

    @property
    def active_connected_quantum_ports(self) -> List[Port]:
        return self._active_connected_quantum_ports

    @property
    def active_connected_quantum_port_count(self) -> int:
        return self._active_connected_quantum_ports.__len__()

    @property
    def connected_classic_ports(self) -> List[Port]:
        return self._connected_classic_ports

    @property
    def connected_quantum_ports(self) -> List[Port]:
        return self._connected_quantum_ports

    @property
    def classic_port_count(self):
        return self._classic_ports.__len__()

    @property
    def quantum_port_count(self):
        return self._quantum_ports.__len__()

    @property
    def all_ports(self) -> List[Port]:
        return self._all_ports

    @property
    def all_port_count(self) -> int:
        return self._all_ports.__len__()

    @property
    def connected_classic_channel_uuids(self):
        return self._connected_classic_channel_uuids

    @property
    def classic_connected_port_count(self) -> int:
        return self._connected_classic_channel_uuids.__len__()

    @property
    def quantum_connected_port_count(self) -> int:
        return self._connected_quantum_channels_uuids.__len__()

    @property
    def connected_quantum_channel_uuids(self):
        return self._connected_quantum_channels_uuids

    @property
    def classic_receive_queue(self):
        return self._classic_receive_queue

    @property
    def unconnected_ports(self) -> list:
        return self._unconnected_ports

    @property
    def quantum_receive_queue(self):
        return self._quantum_receive_queue

    @property
    def sim_request_queue(self):
        return self._sim_request_queue

    def __str__(self) -> str:
        to_return = str()
        to_return += "Port Manager of {}\n".format(self.host_label)
        to_return += "Classic Port Capacity: {}\n".format(self.cc_port_capacity)
        to_return += "Quantum Port Capacity: {}\n".format(self.qc_port_capacity)
        to_return += "Classic Port Count: {}\n".format(self.classic_port_count)
        to_return += "Quantum Port Count: {}\n".format(self.quantum_port_count)
        to_return += "Connected Classic Port Count: {}\n".format(self.classic_connected_port_count)
        to_return += "Connected Quantum Port Count: {}\n".format(self.quantum_connected_port_count)
        to_return += "Communication State: {}\n".format(self.state)

        used_counts_dict = dict()
        for port in self._port_process_counts:
            used_counts_dict[port.type_[0] + str(port.index)] = self._port_process_counts[port]

        to_return += "Port used counts: {}\n".format(used_counts_dict)
        return to_return


def change_default_port_capacities(new_cc_port_capacity, new_qc_port_capacity):
    """
    Changes default port_capacities of devices.
    Must run before any simulation.

    Args:
        new_cc_port_capacity: Maximum classic port capacity.
        new_qc_port_capacity: Maximum quantum port capacity.
    """

    PortManager.max_qc_port_count = new_qc_port_capacity
    PortManager.max_cc_port_count = new_cc_port_capacity


def set_use_simple_queue_for_ports(new_flag: bool):
    """
    Setts simple queue usage for multiprocess ports.
    Must set before simulations.
    """

    global use_simple_queue_for_ports
    use_simple_queue_for_ports = new_flag


"""
##===============================================  INFORMATION TOOLS ======================================================##
"""


class SocketInformation(object):
    def __init__(self, socket_state, host_device_id: device_tools.DeviceIdentification,
                 socket_settings: SocketSettings, port_manager: PortManager):
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
