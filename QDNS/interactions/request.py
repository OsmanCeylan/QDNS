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

from datetime import datetime
from typing import Any, Tuple

import numpy as np

from QDNS.tools import layer


class REQUEST(object):
    def __init__(self, asker_id, target_id, *data,
                 spesific_asker=None, spesific_target=None, want_respond: bool = True):
        """
        Respond parent class.

        Args:
            asker_id:  Respond giver id from arch_tools.
            target_id: Respond target id from arch_tools.
            data: Request carry data.
            spesific_giver: Request spesific giver.
            spesific_target: Request spesific target.
            want_respond: Requst want ack back flag.

        Notes:
            asker and target id must be in QDNS.tools.arch_tools.layers

        Raises:
            ValueError id paramaters is not in lists.
        """

        self._asker_id = asker_id
        self._target_id = target_id
        self._generic_id = None

        if self._asker_id not in layer.layers:
            raise ValueError("Architecute ID {} is not recognized in reuqest of {}".format(self._asker_id, str(type(self))))

        if self._target_id not in layer.layers:
            raise ValueError("Architecute ID {} is not recognized in reuqest of {}".format(self._target_id, str(type(self))))

        self._data = data
        self._spesific_asker = spesific_asker
        self._spesific_target = spesific_target
        self._want_respond = want_respond
        self._creation_date = datetime.now()

        if want_respond:
            self._generic_id = np.random.randint(0, 100000)

    def data_(self, index: int) -> Any:
        """
        Returns index of data.

        Args:
            index: Index.

        Returns:
            Item.

        Raises:
            Key, IndexError.
        """

        try:
            return self._data[index]
        except (KeyError, IndexError) as E:
            raise E("Index {} of request data is not avaible.".format(index))

    def process(self, queue) -> None:
        """ Process the request. """

        queue.put(self)

    @property
    def data(self) -> Tuple[Any, ...]:
        return self._data

    @property
    def asker_id(self):
        return self._asker_id

    @property
    def target_id(self):
        return self._target_id

    @property
    def spesific_asker(self):
        return self._spesific_asker

    @property
    def spesific_target(self):
        return self._spesific_target

    @property
    def want_respond(self) -> bool:
        return self._want_respond

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def details(self) -> str:
        text: str = ""
        text += "Request Type {}\n".format(str(type(self)))
        text += "Asker: {}\n".format(self._asker_id)
        try:
            text += "Data: {}\n".format(str(self._data))
        except TypeError:
            text += "Data is not convertable\n"
        text += "Target: {}\n".format(self._target_id)
        text += "Want Respond: {}\n".format(str(self._want_respond))

        if self._spesific_asker is not None:
            text += "Spesific Asker: {}\n".format(self._spesific_asker)
        if self._spesific_target is not None:
            text += "Spesific Target: {}\n".format(self._spesific_target)
        text += "Generic Id = {}\n".format(self._generic_id)
        return text

    @property
    def generic_id(self):
        return self._generic_id

    def __str__(self) -> str:
        return str(type(self))


class DeviceInformationRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=True):
        """
        Application request device to reveal its information.

        Args:
            asker_app_label: Applicaiton label.
            want_respond: Should be true for this request.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_DEVICE, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class SocketInformationRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=True):
        """
        Application request socket to reveal socket information.

        Args:
            asker_app_label: Applicaiton label.
            want_respond: Should be true for this request.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class ConnectivityInformationRequest(REQUEST):
    def __init__(self, asker_app_label: str, get_uuids, want_respond=True):
        """
        Application request socket port manager to reveal connectivity information.

        Args:
            asker_app_label: Applicaiton label.
            get_uuids: Get target device uuids insetead of label.
            want_respond: Should be true for this request.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, get_uuids,
            spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.get_uuids = self.data[0]


class PortInformationRequest(REQUEST):
    def __init__(self, asker_app_label: str, port_key, search_classic, search_quantum, want_respond=True):
        """
        Application request socket to reveal the port information.

        Args:
            asker_app_label: Asker application label.
            port_key: Port Identification.
            search_classic: Search in classic flag.
            search_quantum: Search in quantum flag.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, port_key, search_classic,
            search_quantum, spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.port_key = self.data[0]
        self.search_classic = self.data[1]
        self.search_quantum = self.data[2]


class OpenCommunicationRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=False):
        """
        Application request socket to open communication on port manager.

        Args:
            asker_app_label: Asker application label.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class CloseCommunicationRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=False):
        """
        Application request socket to close communication on port manager.

        Args:
            asker_app_label: Asker application label.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class ActivatePortRequest(REQUEST):
    def __init__(self, asker_app_label: str, port_key, search_classic, search_quantum, want_respond=False):
        """
        Application request socket to activate port.

        Args:
            asker_app_label: Asker application label.
            port_key: Port Identification.
            search_classic: Search in classic flag.
            search_quantum: Search in quantum flag.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, port_key, search_classic,
            search_quantum, spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.port_key = self.data[0]
        self.search_classic = self.data[1]
        self.search_quantum = self.data[2]


class DeactivatePortRequest(REQUEST):
    def __init__(self, asker_app_label: str, port_key, search_classic, search_quantum, want_respond=False):
        """
        Application request socket to deactivate port.

        Args:
            asker_app_label: Asker application label.
            port_key: Port Identification.
            search_classic: Search in classic flag.
            search_quantum: Search in quantum flag.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, port_key, search_classic,
            search_quantum, spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.port_key = self.data[0]
        self.search_classic = self.data[1]
        self.search_quantum = self.data[2]


class ResumeSocketRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=False):
        """
        Application request socket to open for requests.

        Args:
            asker_app_label: Asker application label.
            want_respond: Want respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class PauseSocketRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=False):
        """
        Application request socket to close for requests.

        Args:
            asker_app_label: Asker application label.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class RefreshConnectionsRequest(REQUEST):
    def __init__(self, asker_app_label: str, want_respond=False):
        """
        Application request socket to refresh connections.

        Args:
            asker_app_label: Asker application label.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, None,
            spesific_asker=asker_app_label, want_respond=want_respond
        )


class UnconnectChannelRequest(REQUEST):
    def __init__(self, asker_app_label: str, channel_key, search_classic, search_quantum, want_respond=False):
        """
        Application request socket to deactivate port.

        Args:
            asker_app_label: Asker application label.
            channel_key: Channel Identification.
            search_classic: Search in classic flag.
            search_quantum: Search in quantum flag.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, channel_key, search_classic,
            search_quantum, spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.channel_key = self.data[0]
        self.search_classic = self.data[1]
        self.search_quantum = self.data[2]


class ReconnectChannelRequest(REQUEST):
    def __init__(self, asker_app_label: str, channel_key, search_classic, search_quantum, want_respond=False):
        """
        Application request socket to deactivate port.

        Args:
            asker_app_label: Asker application label.
            channel_key: Channel Identification.
            search_classic: Search in classic flag.
            search_quantum: Search in quantum flag.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, channel_key, search_classic,
            search_quantum, spesific_asker=asker_app_label, want_respond=want_respond
        )

        self.channel_key = self.data[0]
        self.search_classic = self.data[1]
        self.search_quantum = self.data[2]


class SendPackageRequest(REQUEST):
    def __init__(self, asker_app, target, package, want_respond):
        """
        Application request device's socket to send package.

        Args:
            asker_app: Application label.
            target: Target device identifier.
            package: Package object.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, target,
            package, spesific_asker=asker_app, want_respond=want_respond
        )

        self.target = self._data[0]
        self.package = self._data[1]


class SendQupackRequest(REQUEST):
    def __init__(self, asker_app, target, qupack, want_respond):
        """
        Application request device's socket to send qupack.

        Args:
            asker_app: Application label.
            target: Target device identifier.
            qupack: Qupack object.
            want_respond: Want to respond flag.
        """

        super().__init__(
            layer.ID_APPLICATION, layer.ID_SOCKET, target,
            qupack, spesific_asker=asker_app, want_respond=want_respond
        )

        self.target = self._data[0]
        self.qupack = self._data[1]


class RoutePackageRequest(REQUEST):
    def __init__(self, target, package):
        """
        Socket request routing layer for send package.

        Args:
            target: Target device identifier.
            package: Package object.
        """

        super().__init__(
            layer.ID_SOCKET, layer.ID_APPLICATION,
            target, package, want_respond=False
        )

        self.target = self._data[0]
        self.package = self._data[1]


class RouteQupackRequest(REQUEST):
    def __init__(self, target, qupack):
        """
        Socket request routing layer for send qupack.

        Args:
            target: Target device identifier.
            qupack: Qupack object.
        """

        super().__init__(
            layer.ID_SOCKET, layer.ID_APPLICATION,
            target, qupack, want_respond=False
        )

        self.target = self._data[0]
        self.qupack = self._data[1]


class FindClassicRouteRequest(REQUEST):
    def __init__(self, start_uuid, end_uuid, asker_uuid, asker_app, want_respond):
        """
        An application request route from simulation kernel.

        Args:
            start_uuid: Start device UUID.
            end_uuid: End device UUID.
            asker_uuid: Asker UUID.
            asker_app: Asker app label.
            want_respond: Want respond flag.
        """

        super(FindClassicRouteRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            start_uuid, end_uuid, asker_uuid, asker_app,
            spesific_asker=asker_app, want_respond=want_respond,
        )

        self.start_uuid = self.data[0]
        self.end_uuid = self.data[1]
        self.asker_uuid = self.data[2]


class FindQuantumRouteRequest(REQUEST):
    def __init__(self, start_uuid, end_uuid, asker_uuid, asker_app, want_respond):
        """
        An application request route from simulation kernel.

        Args:
            start_uuid: Start device UUID.
            end_uuid: End device UUID.
            asker_uuid: Asker UUID.
            asker_app: Asker app label.
            want_respond: Want respond flag.
        """

        super(FindQuantumRouteRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            start_uuid, end_uuid, asker_uuid, asker_app,
            spesific_asker=asker_app, want_respond=want_respond,
        )

        self.start_uuid = self.data[0]
        self.end_uuid = self.data[1]
        self.asker_uuid = self.data[2]


class AllocateQubitRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, *args):
        """
        An application request for qubit from simulation layer.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
        """

        super(AllocateQubitRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            args, asker_uuid, spesific_asker=asker_app, want_respond=True
        )

        self.args = self.data[0]
        self.asker_uuid = self.data[1]


class AllocateQubitsRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, count, *args):
        """
        An application request for qubit from simulation layer.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             count: Count of qubit.
        """

        super(AllocateQubitsRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            args, asker_uuid, count, spesific_asker=asker_app, want_respond=True
        )

        self.args = self.data[0]
        self.asker_uuid = self.data[1]
        self.count = self.data[2]


class AllocateQFrameRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, frame_size, *args):
        """
        An application request for qubit frame from simulation layer.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             frame_size: Qubit count in the frame.
        """

        super(AllocateQFrameRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            args, asker_uuid, frame_size, spesific_asker=asker_app, want_respond=True
        )

        self.args = self.data[0]
        self.asker_uuid = self.data[1]
        self.frame_size = self.data[2]


class AllocateQFramesRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, frame_size, count, *args):
        """
        An application request for qubit from simulation layer.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             frame_size: Qubit count in the frame.
             count: Count of qubit.
        """

        super(AllocateQFramesRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            args, asker_uuid, frame_size, count, spesific_asker=asker_app, want_respond=True
        )

        self.args = self.data[0]
        self.asker_uuid = self.data[1]
        self.frame_size = self.data[2]
        self.count = self.data[3]


class DeallocateQubitRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, qubits):
        """
        An application request to deallote qubits from simulation.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             qubits: Qubit list for deallocation.
        """

        super(DeallocateQubitRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, qubits, spesific_asker=asker_app, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.qubits = self.data[1]


class ExtendQFrameRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, qubit_of_frame):
        """
        An application request to extend frame from back by 1.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             qubit_of_frame: Qubit of frame.
        """

        super(ExtendQFrameRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, qubit_of_frame, spesific_asker=asker_app, want_respond=True
        )

        self.asker_uuid = self.data[0]
        self.qubit_of_frame = self.data[1]


class MeasureQubitsRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, qubits, *args):
        """
        An application request to measure qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             qubits: Qubits to measure.
             args: Backend specific arguments.
        """

        super(MeasureQubitsRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, args, qubits, spesific_asker=asker_app, want_respond=True
        )

        self.asker_uuid = self.data[0]
        self.args = self.data[1]
        self.qubits = self.data[2]


class ResetQubitsRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, qubits, *args):
        """
        An application request to reset qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             qubits: Qubits to reset.
             args: Backend specific arguments.
        """

        super(ResetQubitsRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, args, qubits, spesific_asker=asker_app, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.args = self.data[1]
        self.qubits = self.data[2]


class ApplyTransformationRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, gate_id, gate_args, qubits, *args):
        """
        An application request to apply gate on qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             gate_id: ID of gate.
             gate_args: Constructor arguments of gate.
             qubits: Qubits to reset.
             args: Backend specific arguments.
        """

        super(ApplyTransformationRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, gate_id, gate_args, qubits, args, spesific_asker=asker_app,
            want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.gate_id = self.data[1]
        self.gate_args = self.data[2]
        self.qubits = self.data[3]
        self.args = self.data[4]


class ApplySerialTransformationsRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, list_of_gates, *args):
        """
        An application request to apply gate on qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             list_of_gates: List[GateID, GateArg, List[Qubits]]
             args: Backend specific arguments.
        """

        super(ApplySerialTransformationsRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, list_of_gates, args, spesific_asker=asker_app,
            want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.list_of_gates = self.data[1]
        self.args = self.data[2]


class GenerateEPRRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, count, *args):
        """
        An application request to genreate epr on qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             count: Count of pairs.
             args: Backend specific arguments.
        """

        super(GenerateEPRRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, count, args, spesific_asker=asker_app,
            want_respond=True
        )

        self.asker_uuid = self.data[0]
        self.count = self.data[1]
        self.args = self.data[2]


class GenerateGHZRequest(REQUEST):
    def __init__(self, asker_app, asker_uuid, size, count, *args):
        """
        An application request to generate ghz on qubits.

        Args:
             asker_app: Asker app label.
             asker_uuid: Asker device UUID.
             size: Count of pairs.
             args: Backend specific arguments.
        """

        super(GenerateGHZRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, size, count, args, spesific_asker=asker_app,
            want_respond=True
        )

        self.asker_uuid = self.data[0]
        self.size = self.data[1]
        self.count = self.data[2]
        self.args = self.data[3]


# Literally anyone who knows kernel accsess can use apply channel error.
# Make sure only right layer use this at right time.
class ApplyChannelError(REQUEST):
    def __init__(self, asker_uuid, channel_uuid, qubits):
        """
        A layer (prefer socket) request to apply channel error at qubits.

        Args:
            asker_uuid: Asker device UUID.
            channel_uuid: Channel UUID.
            qubits: Qubits in channel.
        """

        super(ApplyChannelError, self).__init__(
            layer.ID_ANY_LAYER, layer.ID_SIMULATION,
            asker_uuid, channel_uuid, qubits, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.channel_uuid = self.data[1]
        self.qubits = self.data[2]


# Literally anyone who knows kernel accsess can use apply channel error.
# Make sure only right layer use this at right time.
class RepeaterProcessRequest(REQUEST):
    def __init__(self, asker_uuid, qubits):
        """
        A layer (prefer socket) request to apply repeater at qubits.

        Args:
            asker_uuid: Asker device UUID.
            qubits: Qubits in channel.
        """

        super(RepeaterProcessRequest, self).__init__(
            layer.ID_ANY_LAYER, layer.ID_SIMULATION,
            asker_uuid, qubits, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.qubits = self.data[1]


# Literally anyone who knows kernel accsess can use apply channel error.
# Make sure only right layer use this at right time.
class ChannelAndRepeaterProcessRequest(REQUEST):
    def __init__(self, asker_uuid, channel_uuid, qubits):
        """
        A layer (prefer socket) request to apply channel error
        and repeater process at qubits.

        Args:
            asker_uuid: Asker device UUID.
            channel_uuid: Channel UUID.
            qubits: Qubits in channel.
        """

        super(ChannelAndRepeaterProcessRequest, self).__init__(
            layer.ID_ANY_LAYER, layer.ID_SIMULATION,
            asker_uuid, channel_uuid, qubits, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.channel_uuid = self.data[1]
        self.qubits = self.data[2]


class RunQKDProtocolRequest(REQUEST):
    def __init__(self, asker_app, target, key_length, method, side):
        """
        An application request qkd layer to run qkd protocol.

        Args:
            asker_app: Asker application.
            target: Target device.
            key_length: Key length.
            method: Method of qkd.
            side: Device side.
        """

        super(RunQKDProtocolRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_APPLICATION,
            asker_app, target, key_length, method, side, want_respond=True
        )

        self.asker_app = self.data[0]
        self.target_device = self.data[1]
        self.key_lenght = self.data[2]
        self.method = self.data[3]
        self.side = self.data[4]


class CurrentQKDKeyRequest(REQUEST):
    def __init__(self, asker_app):
        """
        An application request qkd layer to reveal current key.

        Args:
            asker_app: Asker application.
        """

        super(CurrentQKDKeyRequest, self).__init__(
            layer.ID_APPLICATION, layer.ID_APPLICATION,
            asker_app, want_respond=True
        )

        self.asker_app = self.data[0]


class FlushQKDKey(REQUEST):
    def __init__(self, asker_app):
        """
        An application request qkd layer to flush key.

        Args:
            asker_app: Asker application.
        """

        super(FlushQKDKey, self).__init__(
            layer.ID_APPLICATION, layer.ID_APPLICATION,
            asker_app, want_respond=False
        )

        self.asker_app = self.data[0]


class ChangeChannelLenght(REQUEST):
    def __init__(self, asker_uuid, channel_key, new_length: float):
        """
        A device request simulation kernel to change a channel lenght.

        Args:
            asker_uuid: Asker device.
            channel_key: Unique channel key.
            new_length: New length for channel.
        """

        super(ChangeChannelLenght, self).__init__(
            layer.ID_APPLICATION, layer.ID_SIMULATION,
            asker_uuid, channel_key, new_length, want_respond=False
        )

        self.asker_uuid = self.data[0]
        self.target_channel = self.data[1]
        self.new_length = self.data[2]
