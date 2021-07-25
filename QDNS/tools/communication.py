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

import time
from datetime import datetime
from typing import Any, Tuple

ACK_DATA = "This message represents as a ack data."

classic_package_live_count = 20


def set_classic_package_live_count(count: int):
    """
    Sets classic package max routing count.

    Args:
        count: Positive Integer
    """

    if not isinstance(count, int):
        raise ValueError("Classic package live count must be integer.")

    if not count > 0:
        count = 20

    global classic_package_live_count
    classic_package_live_count = count


class InternetLayer(object):
    def __init__(self, sender, receiver, protocol_info, data,
                 broadcast: bool = False, routing: bool = True):
        """
        Basic internet layer.
        Args:
            sender: Sender device identifier.
            receiver: Receiver device identifier.
            protocol_info: Protocol Information.
            data: Data tuple of package.
            broadcast: Broadcast flag
            routing: Routing flag

        Sender and reciecer must str or uuid of a device.

        Examples:
        ========================================================
        >>> InternetLayer("Alice", "Bob", "SomeProtocol", "This is protocol message!", broadcast=False)
        >>> InternetLayer("Alice", "Bob", None, "Hello Bob!", broadcast=False)
        >>> InternetLayer("Alice", "Bob", None, "Hello Everyone!", broadcast=True)
        """

        self._sender = sender
        self._receiver = receiver
        self._protocol_info = protocol_info
        self._data = data
        self._broadcast = broadcast
        self._routing = routing
        self._route = None

    def data_(self, index: int) -> Any:
        """
        Return index of data tuple.
        :param index: Positive Integer
        :return: Any
        :raises: May raise KeyError.
        """

        try:
            to_return = self._data[index]
        except (KeyError, IndexError) as e:
            raise e("Index {} of signal data not valid.".format(index))
        return to_return

    def change_receiver(self, to):
        self._receiver = to

    def set_broadcast(self, to: bool):
        self._broadcast = to

    def set_route_data(self, route: list):
        self._route = route

    @property
    def route(self):
        return self._route

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def receiver(self) -> str:
        return self._receiver

    @property
    def protocol_info(self):
        return self._protocol_info

    @property
    def data(self) -> Tuple[Any, ...]:
        return self._data

    @property
    def broadcast(self) -> bool:
        return self._broadcast

    @property
    def routing(self) -> bool:
        return self._routing


class ApplicationLayer(object):
    def __init__(self, app_label: str, *app_args):
        """
        Basic application Layer.

        Args:
            app_label: Application label
            *app_args: Application args.
        """

        self._app_label = app_label
        self._app_args = app_args

    @property
    def app_label(self) -> str:
        return self._app_label

    @property
    def app_args(self):
        return self._app_args


class Package(object):
    def __init__(self, app_layer: ApplicationLayer, ip_layer: InternetLayer):
        """
        Creates basic classic network packet.

        Args:
            app_layer: Application layer object.
            ip_layer: InternetLayer object.
        """

        self._ip_layer = ip_layer
        self._app_layer = app_layer
        self._live_count = 1
        self._creation_date = datetime.now()

    def is_drop(self) -> bool:
        """
        Every receiver should call this.
        """

        self._live_count += 1
        if self._live_count >= classic_package_live_count:
            return True
        return False

    @property
    def app_layer(self) -> ApplicationLayer:
        return self._app_layer

    @property
    def app_args(self):
        return self._app_layer.app_args

    @property
    def ip_layer(self) -> InternetLayer:
        return self._ip_layer

    @property
    def sender(self):
        return self._ip_layer.sender

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def live_count(self) -> int:
        return self._live_count

    @property
    def data(self):
        return self.ip_layer.data


class Qupack(object):
    def __init__(self, app_layer: ApplicationLayer, ip_layer: InternetLayer):
        """
        Creates Qupack, qubit along with package.

        Args:
            app_layer: Application layer object.
            ip_layer: InternetLayer object.
        """

        self._ip_layer = ip_layer
        self._app_layer = app_layer
        self._creation_date = datetime.now()

    @property
    def app_layer(self) -> ApplicationLayer:
        return self._app_layer

    @property
    def qubits(self):
        return self._ip_layer.data

    @property
    def ip_layer(self) -> InternetLayer:
        return self._ip_layer

    @property
    def creation_date(self):
        return self._creation_date


class PingRequestPackage(object):
    def __init__(self, device_id):
        self._device_id = device_id
        self._ping_time = time.time()

    @property
    def device_id(self):
        return self._device_id

    @property
    def ping_time(self):
        return self._ping_time


class PingRespondPackage(object):
    def __init__(self, device_id):
        self._device_id = device_id
        self._ping_time = time.time()

    @property
    def device_id(self):
        return self._device_id

    @property
    def ping_time(self):
        return self._ping_time
