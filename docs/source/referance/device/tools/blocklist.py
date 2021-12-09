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

from typing import Dict, Union, Optional

from QDNS.tools.layer import ID_APPLICATION
from QDNS.tools.module import Module, ModuleSettings

_devices = "devices"
_all_communication = "all_communication"
_all_packages = "all_packages"
_all_protocols = "all_protocols"
_all_qubit_streams = "all_qubit_streams"
_blocked_protocols = "blocked_protocols"

block_list_param_resolver = (
    _devices,
    _all_communication,
    _all_packages,
    _all_protocols,
    _all_qubit_streams,
    _blocked_protocols
)


class BlockList(Module):
    DEFAULT_ALL_COMMUNICATION = False
    DEFAULT_ALL_PACKAGES = False
    DEFAULT_ALL_PROTOCOLS = False
    DEFAULT_ALL_QUBIT_STREAMS = False
    DEFAULT_BLOCKED_PROTOCOLS = list()
    MODULE_NAME = "BlockList"

    def __init__(self, application, **kwargs):
        """
        Black list for application.

        Args:
            devices: Device label list.
            all_communication: Block all communication. Default is False.
            all_packages: Bloack all packages. Default is False.
            all_protocols: Block all protocols. Default is False.
            all_qubit_streams: Block qubit streams. Default is False.
            blocked_protocols:  Specify blocked protocols. Default is [].

        Examples:
            >>> BlockList(
            >>>     devices=["Alice", "Bob"],
            >>>     all_communication=[False, False],
            >>>     all_packages=[False, False],
            >>>     all_protocols=[False, False],
            >>>     all_qubit_streams=[False, False],
            >>>     blocked_protocols=[list(), list()]
            >>> )
        """

        ms = ModuleSettings(
            can_disable=True,
            can_restartable=True,
            can_removalbe=True,
            no_state_module=True,
            logger_enabled=True
        )
        super(BlockList, self).__init__(
            ID_APPLICATION[0],
            self.MODULE_NAME,
            module_logger_name="{}::{}".format(application.logger_name, self.MODULE_NAME),
            module_settings=ms
        )

        self._device_list = list()
        self._device_count = 0

        self._all_communication_list = list()
        self._all_packages_list = list()
        self._all_protocols_list = list()
        self._all_qubits_list = list()
        self._blocked_protocols_list = list()

        self._default_all_communication = self.DEFAULT_ALL_COMMUNICATION
        self._default_all_packages = self.DEFAULT_ALL_PACKAGES
        self._default_all_protocols = self.DEFAULT_ALL_PROTOCOLS
        self._default_all_qubits = self.DEFAULT_ALL_PROTOCOLS
        self._default_blocked_protocols = self.DEFAULT_BLOCKED_PROTOCOLS

        self._blocked_count: Dict[str, int] = dict()

        for args in kwargs:
            if args == _devices:
                self._device_list = kwargs[_devices]
                self._device_count = self._device_list.__len__()

            elif args == _all_communication:
                self._all_communication_list = kwargs[_all_communication]

            elif args == _all_packages:
                self._all_packages_list = kwargs[_all_packages]

            elif args == _all_protocols:
                self._all_protocols_list = kwargs[_all_protocols]

            elif args == _all_qubit_streams:
                self._all_qubits_list = kwargs[_all_qubit_streams]

            elif args == _blocked_protocols:
                self._blocked_protocols_list = kwargs[_blocked_protocols]

            else:
                raise ValueError("Blacklist argument {} is not recognized.".format(args))

        if self._device_count <= 0:
            return

        if self._all_communication_list.__len__() <= 0:
            for i in range(self._device_count):
                self._all_communication_list.append(self._default_all_communication)

        if self._all_communication_list.__len__() < self._device_count:
            for i in range(self._all_communication_list.__len__() - 1, self._device_count - 1):
                self._all_communication_list.append(self._default_all_communication)

        if self._all_packages_list.__len__() <= 0:
            for i in range(self._device_count):
                self._all_packages_list.append(self._default_all_packages)

        if self._all_packages_list.__len__() < self._device_count:
            for i in range(self._all_packages_list.__len__() - 1, self._device_count - 1):
                self._all_packages_list.append(self._default_all_communication)

        if self._all_protocols_list.__len__() <= 0:
            for i in range(self._device_count):
                self._all_protocols_list.append(self._default_all_protocols)

        if self._all_protocols_list.__len__() < self._device_count:
            for i in range(self._all_protocols_list.__len__() - 1, self._device_count - 1):
                self._all_protocols_list.append(self._default_all_protocols)

        if self._all_qubits_list.__len__() <= 0:
            for i in range(self._device_count):
                self._all_qubits_list.append(self._default_all_qubits)

        if self._all_qubits_list.__len__() < self._device_count:
            for i in range(self._all_qubits_list.__len__() - 1, self._device_count - 1):
                self._all_qubits_list.append(self._default_all_qubits)

        if self._blocked_protocols_list.__len__() <= 0:
            for i in range(self._device_count):
                self._blocked_protocols_list.append(self._default_blocked_protocols)

        if self._blocked_protocols_list.__len__() < self._device_count:
            for i in range(self._blocked_protocols_list.__len__() - 1, self._device_count - 1):
                self._blocked_protocols_list.append(self._default_blocked_protocols)

        for device in self._device_list:
            self._blocked_count[device] = 0

    def add_device(self, device_label: str,
                   all_communication=False,
                   all_packages=False,
                   all_protocols=False,
                   all_qubit_streams=False,
                   blocked_protocols=None):
        """
        Adds new blacklisted device to application blacklist.

        Args:
            device_label: Device label.
            all_communication: Block all communication.
            all_packages: Bloack all packages.
            all_protocols: Block all protocols.
            all_qubit_streams: Block qubit streams.
            blocked_protocols:  Specify blocked protocols.

        Example:
            >>> BlockList().add_device(
            >>>     "Alice", all_communication=False, all_packages=False, all_protocols=False,
            >>>     all_qubit_streams=False, blocked_protocols=list()
            >>> )

        """

        if device_label in self.devices:
            return self.update_device(
                device_label=device_label, all_communication=all_communication,
                all_packages=all_packages, all_protocols=all_protocols,
                all_qubit_streams=all_qubit_streams, blocked_protocols=blocked_protocols
            )

        if blocked_protocols is None:
            blocked_protocols = list()

        self._device_list.append(device_label)
        self._all_communication_list.append(all_communication)

        self._all_packages_list.append(all_packages)
        self._all_protocols_list.append(all_protocols)
        self._all_qubits_list.append(all_qubit_streams)
        self._blocked_protocols_list.append(blocked_protocols)
        self._blocked_count[device_label] = 0
        self._device_count += 1

    def update_device(self, device_label: str,
                      all_communication=None,
                      all_packages=None,
                      all_protocols=None,
                      all_qubit_streams=None,
                      blocked_protocols=None):

        """
        Updates blacklisted device in application blacklist.

        Args:
            device_label: Device label.
            all_communication: Block all communication.
            all_packages: Bloack all packages.
            all_protocols: Block all protocols.
            all_qubit_streams: Block qubit streams.
            blocked_protocols: Specify blocked protocols.

        Example:
            >>> BlockList().update_device("Alice", all_packages=False, blocked_protocols=None)
            >>> BlockList().update_device("Alice", all_packages=True, blocked_protocols=list())
            >>> BlockList().update_device("Alice", all_packages=True, all_qubit_streams=True, blocked_protocols=None)
        """

        index = self._device_list.index(device_label)
        if all_communication is not None:
            self._all_communication_list[index] = all_communication

        if all_packages is not None:
            self._all_packages_list[index] = all_packages

        if all_protocols is not None:
            self._all_protocols_list[index] = all_protocols

        if all_qubit_streams is not None:
            self._all_qubits_list[index] = all_qubit_streams

        if blocked_protocols is not None:
            self._blocked_protocols_list[index] = blocked_protocols

    def remove_device(self, device_label):
        """
        Removes device from block list.

        :raises: Error if anything happen with lists.
        :returns: True if operation is successes.
        """

        if device_label not in self._device_list:
            return False

        try:
            index = self._device_list.index(device_label)
            self._all_communication_list.remove(index)
            self._all_packages_list.remove(index)
            self._all_protocols_list.remove(index)
            self._all_qubits_list.remove(index)
            self._blocked_protocols_list.remove(index)
            self._blocked_count.pop(device_label)
            self._device_count -= 1

        except (IndexError, KeyError, ValueError):
            return False
        else:
            return True

    def get_all_communication(self, device_label) -> Union[bool, None]:
        """
        Gets all communication property of device in black list.
        :returns: Boolean or None.
        """

        try:
            index = self._device_list.index(device_label)
            return self._all_communication_list[index]
        except (IndexError, KeyError, ValueError):
            return None

    def get_all_packages(self, device_label) -> Union[bool, None]:
        """
        Gets all packages property of device in black list.
        :returns: Boolean or None.
        """

        try:
            index = self._device_list.index(device_label)
            return self._all_packages_list[index]
        except (IndexError, KeyError, ValueError):
            return None

    def get_all_protocols(self, device_label) -> Union[bool, None]:
        """
        Gets all protocols property of device in black list.
        :returns: Boolean or None.
        """

        try:
            index = self._device_list.index(device_label)
            return self._all_protocols_list[index]
        except (IndexError, KeyError, ValueError):
            return None

    def get_all_qubit_stream(self, device_label) -> Union[bool, None]:
        """
        Gets all qubit_stream property of device in black list.
        :returns: Boolean or None.
        """

        try:
            index = self._device_list.index(device_label)
            return self._all_qubits_list[index]
        except (IndexError, KeyError, ValueError):
            return None

    def get_blocked_protocols(self, device_label) -> Union[bool, None]:
        """
        Gets blocked protocols. property of device in black list.
        :returns: Boolean or None.
        """

        try:
            index = self._device_list.index(device_label)
            return self._blocked_protocols_list[index]
        except (IndexError, KeyError, ValueError):
            return None

    def is_protocol_blocked(self, device_label, protocol) -> Union[bool, None]:
        """
        Find if specified protocol is blocked.

        Args:
            device_label: Device label.
            protocol: Protocol.

        Returns:
            Boolean or None.

        Raises:
            Errors related list and dict operations.
        """

        try:
            index = self._device_list.index(device_label)
        except (IndexError, KeyError, ValueError):
            return False

        try:
            black_listed_protocols = self._blocked_protocols_list[index]
            if protocol in black_listed_protocols:
                return True
            return False
        except (IndexError, KeyError, ValueError):
            return None

    def add_blocked_count(self, device_label: str, add_value: int = 1):
        """
        Updates blocked count of device.

        Args:
            device_label: Device label.
            add_value: Plus value.

        Return:
            True if operation is success.
        """

        try:
            self._blocked_count[device_label] += add_value
        except (IndexError, KeyError, ValueError):
            return False
        return True

    def get_blocked_count(self, device_label) -> Union[int, None]:
        """ Gets the block count of device. """

        try:
            return self._blocked_count[device_label]
        except (IndexError, KeyError, ValueError):
            return None

    def clear_counts(self):
        """ Clears the blocked counts. """
        for key in self._blocked_count:
            self._blocked_count[key] = 0

    def enable_module(self) -> bool:
        """
        Enables Module.

        Return:
            True if module state changed to enabled.
            False if module state is not changed.
        """

        if self.is_disabled():
            self._disabled = False
            return True
        return False

    def disable_module(self) -> bool:
        """
        Disables Module.

        Return:
            True if module can disable.
            False if module cannot disable.
        """

        if self.can_disable:
            if not self.is_disabled():
                self._disabled = True
            return True
        return False

    def clear_blocklist(self):
        self._device_list.clear()
        self._device_count = 0

        self._all_communication_list.clear()
        self._all_packages_list.clear()
        self._all_protocols_list.clear()
        self._all_qubits_list.clear()
        self._blocked_protocols_list.clear()
        self._blocked_count: Dict[str, int] = dict()

    @property
    def devices(self) -> list:
        return self._device_list

    @property
    def all_communication(self) -> list:
        return self._all_communication_list

    @property
    def all_packages(self) -> list:
        return self._all_packages_list

    @property
    def all_protocols(self) -> list:
        return self._all_protocols_list

    @property
    def all_qubit_streams(self) -> list:
        return self._all_qubits_list

    @property
    def blocked_protocols(self) -> list:
        return self._blocked_protocols_list

    @property
    def blocked_count(self) -> Dict[str, int]:
        return self._blocked_count

    @property
    def device_count(self) -> int:
        return self._device_count

    def __int__(self) -> int:
        return self.device_count

    def __len__(self) -> int:
        return self.device_count

    def __str__(self) -> str:
        to_return = str()
        to_return += "BlockList\n"
        to_return += "------------------\n"
        to_return += "Device Count: {}\n".format(self.device_count)
        to_return += "Devices: {}\n".format(self.devices)
        to_return += "Blocked Counts: {}\n".format(self.blocked_count)
        to_return += "All communication: {}\n".format(self.all_communication)
        to_return += "All packages: {}\n".format(self.all_packages)
        to_return += "All protocols: {}\n".format(self.all_protocols)
        to_return += "All qubit streams: {}\n".format(self.all_qubit_streams)
        to_return += "Blocked protocols: {}\n".format(self.blocked_protocols)
        return to_return


def change_block_list_defaults(
        all_communication: bool = False, all_packages: bool = False,
        all_protocols: bool = False, all_qubit_streams: bool = False,
        blocked_protocols: Optional[list] = None
):
    """
    Changes the defaults in BlockList constructor.

    Args:
        all_communication: Change all communication default.
        all_packages: Change all packages default.
        all_protocols: Change all protocols default.
        all_qubit_streams: Change all qubit stream default.
        blocked_protocols: Change all blocked protocols default.
    """

    if blocked_protocols is None:
        blocked_protocols = list()

    BlockList.DEFAULT_ALL_COMMUNICATION = all_communication
    BlockList.DEFAULT_ALL_PACKAGES = all_packages
    BlockList.DEFAULT_ALL_PROTOCOLS = all_protocols
    BlockList.DEFAULT_ALL_QUBIT_STREAMS = all_qubit_streams
    BlockList.DEFAULT_BLOCKED_PROTOCOLS = blocked_protocols
