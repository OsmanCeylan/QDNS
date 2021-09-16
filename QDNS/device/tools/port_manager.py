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

import multiprocessing
import uuid
from typing import List, Dict, Union

from QDNS.device.tools.port import CLASSIC_PORT
from QDNS.device.tools.port import Port
from QDNS.device.tools.port import QUANTUM_PORT
from QDNS.interactions import signal
from QDNS.tools import various_tools
from QDNS.tools.layer import ID_SOCKET
from QDNS.tools.module import Module, ModuleSettings
from QDNS.tools.state_handler import StateHandler

COMMUNICATION_UP = "\"communication is up\""
COMMUNICATION_DOWN = "\"communication is down\""

port_manager_states = (
    COMMUNICATION_UP,
    COMMUNICATION_DOWN
)

use_simple_queue_for_ports = True


class PortManagerSetting(ModuleSettings):
    max_cc_port_count_ = "max_cc_port_count"
    max_qc_port_count_ = "max_qc_port_count"

    def __init__(
            self, max_cc_port_count: int,
            max_qc_port_count: int
    ):
        """
        Application settings constructor.

        Args:
            max_cc_port_count: Maximum classic port count.
            max_qc_port_count: Maximum quantum port count.
        """

        kwargs = {
            self.max_cc_port_count_: max_cc_port_count,
            self.max_qc_port_count_: max_qc_port_count
        }

        super(PortManagerSetting, self).__init__(
            can_disable=False, can_restartable=True,
            can_removalbe=False, no_state_module=False,
            logger_enabled=False, **kwargs
        )

    def change_max_cc_count(self, new_value: int):
        """ Changes classic port count. """

        self.change_paramater(self.max_cc_port_count_, new_value)

    def change_max_qc_count(self, new_value: int):
        """ Changes quants port count. """

        self.change_paramater(self.max_qc_port_count_, new_value)

    @property
    def max_cc_count(self) -> int:
        return self.get_setting(self.max_cc_port_count_)

    @property
    def max_qc_count(self) -> int:
        return self.get_setting(self.max_qc_port_count_)

    def __str__(self) -> str:
        text = str()
        text += "Max classic port count: {}\n".format(self.max_cc_count)
        text += "Max quantum port count: {}\n".format(self.max_qc_count)
        return text


default_port_manager_setting = PortManagerSetting(21, 21)


def change_default_port_manager_setting(new_setting: PortManagerSetting):
    """ Changes the default port_manager setting. """

    global default_port_manager_setting
    default_port_manager_setting = new_setting


class PortManager(Module):

    module_name = "Port Manager"

    def __init__(self, host_id, port_manager_setting: PortManagerSetting):
        """
        Port Manager module for network socket.

        Args:
            host_id: Device Id.
            port_manager_setting: Setting for this object.
        """

        state_handler = StateHandler(
            ID_SOCKET[0],
            False, *port_manager_states,
            GENERAL_STATE_IS_RUNNING=COMMUNICATION_UP,
            GENERAL_STATE_IS_STOPPED=COMMUNICATION_DOWN
        )

        super(PortManager, self).__init__(
            ID_SOCKET[0], self.module_name,
            special_state=state_handler,
            module_settings=port_manager_setting
        )

        self._host_id = host_id

        # Set list and dicts about ports.
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

        # Set queues.
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

        for i in range(self.cc_port_capacity):
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

        for i in range(self.qc_port_capacity):
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
        """
        Sets sim request queue.
        Must be setted with simulation thread,
        network socket prepare layer.
        """

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
        """ Returns if connectivity is opened. """

        if self.state == COMMUNICATION_UP:
            return True
        return False

    def is_connectivity_close(self) -> bool:
        """ Returns if connectivity is closed. """

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
    def portman_settings(self) -> PortManagerSetting:
        return self.module_settings

    @property
    def cc_port_capacity(self) -> int:
        return self.portman_settings.max_cc_count

    @property
    def qc_port_capacity(self) -> int:
        return self.portman_settings.max_qc_count

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


def set_use_simple_queue_for_ports(new_flag: bool):
    """
    Setts simple queue usage for multiprocess ports.
    Must set before simulations.
    """

    global use_simple_queue_for_ports
    use_simple_queue_for_ports = new_flag
