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

from queue import Empty

from QDNS.device.tools.socket_tools import DROP_PACKAGE
from QDNS.device.tools.socket_tools import RELEASE_PACKAGE
from QDNS.tools import communication
from QDNS.tools.layer import ID_APPLICATION
from QDNS.tools.module import ModuleSettings, Module


class Listener(Module):
    MODULE_NAME = "LISTENER"

    def __init__(self, application):
        """
        Listener helps to listen socket traffic on Device.
        Device als needs to be able to observe.
        """

        ms = ModuleSettings(
            can_disable=True, can_removalbe=True,
            can_restartable=False, no_state_module=True,
            logger_enabled=True
        )

        super().__init__(
            ID_APPLICATION[0],
            self.MODULE_NAME,
            module_logger_name="{}::{}".format(application.logger_name, self.MODULE_NAME),
            module_settings=ms
        )

        self.application = application
        self._listen_queue = None
        self._release_queue = None
        self._interrupt = False

    def set_listen_queue(self, new_queue):
        """ Sets the listen queue. """

        self._listen_queue = new_queue

    def set_release_queue(self, new_queue):
        """ Sets the release queue. """

        self._release_queue = new_queue

    def set_interrupt(self, new_flag: bool):
        """
        Interrupt flag.
        If the flag set True, traffic will interrupted.
        """

        self.logger.info("Traffic on device is now interrupted.")
        self._interrupt = new_flag

    def get_communication_item(self, timeout=5.0):
        """
        Gets the traffic item from socket.
        """

        try:
            item = self._listen_queue.get(self, timeout=timeout)
        except Empty:
            return None
        else:
            return item

    def release_item(self):
        """
        Releases the last item.
        """

        if self._interrupt:
            self._release_queue.put(RELEASE_PACKAGE)
        else:
            self.application.logger.warning("Interrupt is not running! Pacakge is already released.")

    def drop_item(self):
        """
        Drops the item.
        """

        if self._interrupt:
            self._release_queue.put(DROP_PACKAGE)
        else:
            self.application.logger.warning("Interrupt is not running! Pacakge is already released.")

    def print_item(self, package):
        """
        Prints package or qupack.
        """

        print("-" * 15)
        print("Traffic on device: ", self.application.host_label)
        if isinstance(package, communication.Qupack):
            print("TYPE: QUANTUM DATA")
        else:
            print("TYPE: CLASSIC DATA")

        print("SENDER: ", package.ip_layer.sender)
        print("RECEIVER: ", package.ip_layer.receiver)
        print("APP Label: ", package.app_layer.app_label)
        print("Broadcast: ", str(package.ip_layer.broadcast))
        if isinstance(package, communication.Qupack):
            print("Qubits: ", str(package.ip_layer.data))
        else:
            print("Data: ", str(package.ip_layer.data))
        print("\n")

    @property
    def listen_queue(self):
        return self._listen_queue

    @property
    def release_queue(self):
        return self._release_queue

    @property
    def interrupt(self):
        return self._interrupt
