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

from QDNS.tools import layer


class RESPOND(object):
    def __init__(self, generic_id, giver_id, target_id, exit_code, *data,
                 spesific_giver=None, spesific_target=None, spesific_target_integration=None):
        """
        Respond parent class.

        Args:
            generic_id: Request generic id.
            giver_id:  Respond giver id from arch_tools.
            target_id: Respond target id from arch_tools.
            exit_code: Exit code of respond.
            data: Request carry data.
            spesific_giver: Request spesific giver.
            spesific_target: Request spesific target.
            spesific_target_integration: Request spesific target_2

        Notes:
            generic_id must be related request generated id.
            giver and target id must be in QDNS.tools.arch_tools.layers
            exit_code must be in QDNS.tools.arch_tool.exit_codes

        Raises:
            ValueError if id paramaters is not found.
        """

        self._generic_id = generic_id
        self._giver_id = giver_id
        self._target_id = target_id

        if self._giver_id not in layer.layers:
            raise ValueError("Architecute ID {} is not recognized in respond of {}"
                             .format(self._giver_id, str(type(self))))

        if self._target_id not in layer.layers:
            raise ValueError("Architecute ID {} is not recognized in respond of {}"
                             .format(self._target_id, str(type(self))))

        self._exit_code = exit_code
        self._data = data
        self._spesific_giver = spesific_giver
        self._spesific_target = spesific_target
        self._spesific_target_integration = spesific_target_integration
        self._creation_date = datetime.now()

    def data_(self, index: int) -> Any:
        """
        Returns index of data.

        Args:
            index: Index.

        Returns:
            Items in data.

        Raises:
            Key, IndexError.
        """

        try:
            return self._data[index]
        except (KeyError, IndexError) as E:
            raise E("Index {} of request data is not avaible.".format(index))

    def process(self, queue) -> None:
        """
        Process the request.
        :param queue: Queue.
        :return: None
        """

        queue.put(self)

    @property
    def data(self) -> Tuple[Any, ...]:
        return self._data

    @property
    def giver_id(self):
        return self._giver_id

    @property
    def target_id(self):
        return self._target_id

    @property
    def spesific_giver(self):
        return self._spesific_giver

    @property
    def spesific_target(self):
        return self._spesific_target

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def spesific_target_integration(self):
        return self._spesific_target_integration

    @property
    def details(self) -> str:
        text: str = ""
        text += "Request Type {}\n".format(str(type(self)))
        text += "Giver: {}\n".format(self._giver_id)
        try:
            text += "Data: {}\n".format(str(self._data))
        except TypeError:
            text += "Data is not convertable\n"
        text += "Target: {}\n".format(self._target_id)

        if self._spesific_giver is not None:
            text += "Spesific Giver: {}\n".format(self._spesific_giver)
        if self._spesific_target is not None:
            text += "Spesific Target: {}\n".format(self._spesific_target)
        return text

    @property
    def generic_id(self):
        return self._generic_id

    @property
    def exit_code(self):
        return self._exit_code

    def __str__(self) -> str:
        return str(type(self))


class GenericRespond(RESPOND):
    def __init__(self, generic_id, exit_code, *data, spesific_target=None):
        """
        Generic Respond.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            data: Yielded informaiton.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_ANY_LAYER, layer.ID_ANY_LAYER,
            exit_code, *data, spesific_target=spesific_target
        )


class DeviceInformationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, device_information, spesific_target=None):
        """
        Device respond to application for device informaiton request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            device_information: Yielded informaiton.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, device_information, spesific_target=spesific_target
        )

        self.device_information = self.data[0]


class SocketInformationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, socket_information, spesific_target=None):
        """
        Socket respond to application for socket informaiton request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            socket_information: Yielded informaiton.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, socket_information, spesific_target=spesific_target
        )

        self.socket_information = self.data[0]


class ConnectivityInformationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, connectivity_information, spesific_target=None):
        """
        Socket respond to application for connectivity informaiton request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            connectivity_information: Yielded informaiton.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, connectivity_information, spesific_target=spesific_target
        )

        self.connectivity_information = self.data[0]


class PortInformationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, port_information, spesific_target=None):
        """
        Socket respond to application for port informaiton request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            port_information: Yielded informaiton.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, port_information, spesific_target=spesific_target
        )

        self.port_information = self.data[0]


class OpenCommunicationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for open communication request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed respond.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class CloseCommunicationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for close communication request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed respond.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class ActivatePortRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for activate request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed flag.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class DeactivatePortRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for port deactivate request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed flag.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class ResumeSocketRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for resume request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed flag.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class PauseSocketRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for pause request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed flag.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class RefreshConnectionsRespond(RESPOND):
    def __init__(self, generic_id, exit_code, results, process_time, spesific_target=None):
        """
        Socket respond to application for refresh request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            results: State changed flag.
            process_time: Refresh time.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, results, process_time, spesific_target=spesific_target
        )

        self.results = self.data[0]
        self.process_time = self.data[1]


class UnconnectChannelRespond(RESPOND):
    def __init__(self, generic_id, exit_code, state_changed, spesific_target=None):
        """
        Socket respond to application for unconnect channel request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            state_changed: State changed flag.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, state_changed, spesific_target=spesific_target
        )

        self.state_changed = self.data[0]


class ReconnectChannelRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Socket respond to application for reconnect channel request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class SendPackageRespond(RESPOND):
    def __init__(self, generic_id, exit_code, count, spesific_target=None):
        """
        Socket respond to application for send package request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            count: Count of sended device.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, count, spesific_target=spesific_target
        )

        self.count = self.data[0]


class SendQupackRespond(RESPOND):
    def __init__(self, generic_id, exit_code, count, spesific_target=None):
        """
        Socket respond to application for send qupack request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            count: Count of sended qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, count, spesific_target=spesific_target
        )

        self.count = self.data[0]


class RoutePackageRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        This request wants no respond.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class RouteQupackRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        This request wants no respond.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class FindClassicRouteRespond(RESPOND):
    def __init__(self, generic_id, exit_code, route, spesific_target=None):
        """
        Socket respond to application for find classic route request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            route: Route info.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, route, spesific_target=spesific_target
        )

        self.route = self.data[0]


class FindQuantumRouteRespond(RESPOND):
    def __init__(self, generic_id, exit_code, route, spesific_target=None):
        """
        Socket respond to application for find quantum route request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            route: Route info.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SOCKET, layer.ID_APPLICATION,
            exit_code, route, spesific_target=spesific_target
        )

        self.route = self.data[0]


class AllocateQubitRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubit, spesific_target=None):
        """
        Simulation respond to application for allocate qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubit: Qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubit, spesific_target=spesific_target
        )

        self.qubit = self.data[0]


class AllocateQubitsRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubits, spesific_target=None):
        """
        Simulation respond to application for allocate qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubits: Qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubits, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class AllocateQFrameRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubits, spesific_target=None):
        """
        Simulation respond to application for allocate qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubits: Qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubits, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class AllocateQFramesRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubits, spesific_target=None):
        """
        Simulation respond to application for allocate qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubits: Qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubits, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class DeallocateQubitRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond to application for deallocate qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class ExtendQFrameRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubit, spesific_target=None):
        """
        Simulation respond to application for extended qubit.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubit: Qubit.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubit, spesific_target=spesific_target
        )

        self.qubit = self.data[0]


class MeasureQubitsRespond(RESPOND):
    def __init__(self, generic_id, exit_code, results, spesific_target=None):
        """
        Simulation respond to measure results.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            results: Results of measures.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, results, spesific_target=spesific_target
        )

        self.results = self.data[0]


class ResetQubitsRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for reset operation..

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class ApplyTransformationRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for apply gate.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class ApplySerialTransformationsRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for apply serial gates.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class GenerateEPRRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubits, spesific_target=None):
        """
        Simulation respond for generate epr request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubits: Pair of qubits.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubits, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class GenerateGHZRespond(RESPOND):
    def __init__(self, generic_id, exit_code, qubits, spesific_target=None):
        """
        Simulation respond for generate ghz request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
            qubits: Pair of qubits.
            spesific_target: Application label.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_APPLICATION,
            exit_code, qubits, spesific_target=spesific_target
        )

        self.qubits = self.data[0]


class ApplyChannelErrorRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for apply channel error request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_ANY_LAYER,
            exit_code, spesific_target=spesific_target
        )


class RepeaterProcessRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for apply repeater process request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_ANY_LAYER,
            exit_code, spesific_target=spesific_target
        )


class ChannelAndRepeaterProcessRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation respond for apply repeater and channel process request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_SIMULATION, layer.ID_ANY_LAYER,
            exit_code, spesific_target=spesific_target
        )


class RunQKDProtocolRespond(RESPOND):
    def __init__(self, generic_id, exit_code, key, spesific_target=None):
        """
        QKD Application respond for key generate request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_APPLICATION, layer.ID_APPLICATION,
            exit_code, key, spesific_target=spesific_target
        )

        self.key = self.data[0]


class CurrentQKDKeyRespond(RESPOND):
    def __init__(self, generic_id, exit_code, key, spesific_target=None):
        """
        QKD Application respond for current key request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_APPLICATION, layer.ID_APPLICATION,
            exit_code, key, spesific_target=spesific_target
        )

        self.key = self.data[0]


class FlushQKDKeyRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        QKD Application respond for current key request.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_APPLICATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )


class ChangeChannelLenghtRespond(RESPOND):
    def __init__(self, generic_id, exit_code, spesific_target=None):
        """
        Simulation kernel respond for channel length change.

        Args:
            generic_id: Request ID.
            exit_code: Exit Code.
        """

        super().__init__(
            generic_id, layer.ID_APPLICATION, layer.ID_APPLICATION,
            exit_code, spesific_target=spesific_target
        )
