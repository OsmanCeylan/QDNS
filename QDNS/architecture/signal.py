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
from typing import Tuple, Any


class SIGNAL(object):
    """
    Layer comminication element signal.
    """

    class Common:
        STATE_REPORT = "A layer signals its state to up layer."
        END_LAYER_SIGNAL = "A layer signals to up layer for end itself."
        END_QKD_LAYER = "A layer signals to qkd layer to end itself."

    class SocketToSim:
        CONNECTION_CHANGED = "Connection changed between socket layers.."

    class SimToApp:
        FLUSH_ROUTE_DATA = "Flush your route data."

    class SimToMiner:
        DISTRABUTE_ACTION = "Simulation layer commands miner to send an action to all devices."

    @staticmethod
    def is_legit_signal(signal) -> bool:
        """
        Check if signal type matches.

        Args:
            signal: Signal.

        Returs true if signal header is in known_signals.
        """

        for key in known_signals:
            legits = known_signals[key]
            for legit in legits:
                if signal == legit:
                    return True
        return False

    def __init__(self, header: str, *data, source_emiter=None):
        """
        Signals among layers.
        Only close layer can/should emit signals at each other.

        Args:
            header: Must be one of top classes variables.
            data: Signal data.
            source_emiter: Emiter source. When using multiple object at one layer.
            target_queue: Target queue to put. Also you can manually do this.
        """

        self._header = header
        self._data = data
        self._source_emiter = source_emiter
        self._creation_date = datetime.now()
        self._emited = False

        if not self.is_legit_signal(self._header):
            raise KeyError("Exepted known signal header but got {}.".format(self._header))

    def emit(self, target) -> None:
        """
        Emits the signal through target queue.

        Args:
            target: target layer accept queue.

        Raises:
            Emiting more than once.
        """

        if self._emited:
            raise ValueError("Can not emit a signal second time. Singal info: {}\n".format(self))
        self._emited = True
        target.put(self)

    def data_(self, index: int) -> Any:
        """
        Return index of data tuple.

        Args:
            index: Pozitif Integer

        Return:
            Signal data of index.

        Raises:
            May raise KeyError.
        """

        try:
            to_return = self._data[index]
        except (KeyError, IndexError) as e:
            raise e("Index {} of signal data not valid.".format(index))
        return to_return

    @property
    def data(self) -> Tuple[Any, ...]:
        return self._data

    @property
    def header(self):
        return self._header

    @property
    def source_emiter(self):
        return self._source_emiter

    @property
    def createion_date(self):
        return self._creation_date

    @property
    def details(self) -> str:
        text: str = ""
        text += "Signal Type: {}\n".format(str(self._header))
        text += "Creation Date: {}\n".format(str(self._creation_date))
        text += "Emited: {}\n".format(str(self._emited))

        if self._source_emiter is not None:
            text += "Source Emiter: {}\n".format(self._source_emiter)
        try:
            text += "Data: {}\n".format(str(self._data))
        except TypeError:
            text += "Data is not convertable\n"
        return text

    def __str__(self) -> str:
        return str(self._header)


known_signals = dict()
known_signals["Common"] = (
    SIGNAL.Common.STATE_REPORT,
    SIGNAL.Common.END_LAYER_SIGNAL
)
known_signals["SocketToSim"] = (
    SIGNAL.SocketToSim.CONNECTION_CHANGED,
)
known_signals["SimToApp"] = (
    SIGNAL.SimToApp.FLUSH_ROUTE_DATA,
)
known_signals["SimToMiner"] = (
    SIGNAL.SimToMiner.DISTRABUTE_ACTION,
)


class StateReportSignal(SIGNAL):
    def __init__(self, source, new_state):
        """
        State report signal.

        Args:
            source: Source layer identification.
            new_state: New state of source layer.
        """
        super(StateReportSignal, self).__init__(SIGNAL.Common.STATE_REPORT, new_state, source_emiter=source)
        self.new_state = self._data[0]


class EndDeviceSignal(SIGNAL):
    def __init__(self, source_application):
        """
        An application signals for end its device simulation.

        Args:
            source_application: Source application.
        """

        super(EndDeviceSignal, self).__init__(SIGNAL.Common.END_LAYER_SIGNAL, source_emiter=source_application)


class EndDeviceSignalChVer(SIGNAL):
    def __init__(self, new_state):
        """
        End checker signals for end its device simulation.
        """

        super(EndDeviceSignalChVer, self).__init__(SIGNAL.Common.END_LAYER_SIGNAL, new_state)
        self.new_state = self._data[0]


class DeviceEndSocketSignal(SIGNAL):
    def __init__(self, new_state=None):
        """
        Device / Application signals to socket for end socket simulation.
        """

        super(DeviceEndSocketSignal, self).__init__(SIGNAL.Common.END_LAYER_SIGNAL, new_state)
        self.new_state = self._data[0]


class TerminateSocketSignal(SIGNAL):
    def __init__(self):
        """
        App / Device / Miner signals to socket for end socket simulation.
        """

        super(TerminateSocketSignal, self).__init__(SIGNAL.Common.END_LAYER_SIGNAL)


class EndSimulationSignal(SIGNAL):
    """
    Simulation uses this signal to check finalize state.
    """

    def __init__(self):
        super(EndSimulationSignal, self).__init__(SIGNAL.Common.END_LAYER_SIGNAL)


class ConnectionChangedSignal(SIGNAL):
    """
    Socket signals about connection changes.
    """

    def __init__(self, device_r_uuid, device_l_uuid, channel_uuid, state, emiter):
        """
        Connection changed signal.

        Args:
            device_r_uuid: Device R UUID.
            device_l_uuid: Device L UUID.
            channel_uuid: Channel UUID.
            state: Connection state.
            emiter: Emiter Device UUID.
        """
        super(ConnectionChangedSignal, self).__init__(
            SIGNAL.SocketToSim.CONNECTION_CHANGED, device_l_uuid, device_r_uuid,
            channel_uuid, state, source_emiter=emiter
        )

        self.device_r_uuid = self.data[0]
        self.device_l_uuid = self.data[1]
        self.channel_uuid = self.data[2]
        self.connection_state = self.data[3]


class FlushRouteData(SIGNAL):
    """
    Signal about communication changes.
    """

    def __init__(self):
        super(FlushRouteData, self).__init__(SIGNAL.SimToApp.FLUSH_ROUTE_DATA, None)


class DistrabuteAction(SIGNAL):
    """
    Simulation commands miner to distrabute action among device.
    """

    def __init__(self, target_layer, action, target_layer_info):
        super(DistrabuteAction, self).__init__(
            SIGNAL.SimToMiner.DISTRABUTE_ACTION, target_layer,
            action, target_layer_info
        )


class EndQKDLayer(SIGNAL):
    def __init__(self):
        """
        App / Device / Miner signals to socket for end qkd layer simulation.
        """

        super(EndQKDLayer, self).__init__(SIGNAL.Common.END_QKD_LAYER)
