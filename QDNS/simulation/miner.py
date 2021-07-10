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

import time
import uuid
import multiprocessing
from queue import Queue as TQueue
from typing import List, Dict, Union

from QDNS.device.device import Device
from QDNS.architecture import signal, request
from QDNS.tools import architecture_tools
from QDNS.tools import simulation_tools
from QDNS.tools import device_tools


class Miner(multiprocessing.Process, architecture_tools.Layer):
    def __init__(self, sim_request_queue, user_dump_queue, daemonized=True):
        """
        Miners manages device threads.

        Args:
            sim_request_queue: Simulation request queue.
            user_dump_queue: User dump queue.
            daemonized: Daemonize processes flag.
        """

        multiprocessing.Process.__init__(self, daemon=daemonized)
        architecture_tools.Layer.__init__(self, layer=architecture_tools.ID_MINER, layer_type=architecture_tools.PROCESS_LAYER, layer_name=self.name)

        state_handler = architecture_tools.StateHandler(
            self.layer_id, True, *simulation_tools.miner_states,
            GENERAL_STATE_NOT_STARTED=simulation_tools.MINER_NOT_STARTED,
            GENERAL_STATE_IS_RUNNING=simulation_tools.MINER_IS_RUNNING,
            GENERAL_STATE_IS_FINISHED=simulation_tools.MINER_IS_FINISHED,
            GENERAL_STATE_MAY_END=simulation_tools.MINER_MAY_END
        )
        self.set_state_handler(state_handler)

        self._end_check_thread = None
        self.queue_manager.add_queue(architecture_tools.SIM_REQUEST_QUEUE, sim_request_queue)
        self.queue_manager.add_queue(architecture_tools.USER_DUMP_QUEUE, user_dump_queue)
        self._devices: List[Device] = list()
        self._device_thread_list: List[simulation_tools.TerminatableThread] = list()
        self._device_states: Dict[Device, str] = dict()
        self._device_thread_dict: [Device, simulation_tools.TerminatableThread] = dict()
        self._thread_device_dict: [simulation_tools.TerminatableThread, Device] = dict()
        self.set_queues(multiprocessing.Queue(), None)

        self.set_state_report_queue(self.sim_request_queue)
        self.logger.info("Process {} is genereted.".format(self.name))

    def prepair_layer(self, *args):
        self.set_threaded_queues(TQueue(), None)
        self._end_check_thread = simulation_tools.TerminatableThread(self.check_finalize, daemon=True)

        for device in self._devices:
            device.prepair_layer(self.sim_request_queue, self.threaded_request_queue, self.user_dump_queue)
            tt = simulation_tools.TerminatableThread(target_method=device.run, daemon=True)
            self._device_thread_list.append(tt)
            self._device_states[device] = device_tools.DEVICE_NOT_STARTED
            self._device_thread_dict[device] = tt
            self._thread_device_dict[tt] = device

        self.logger.info("Process {} is setup with {} devices.".format(self.name, self.device_count))

    def add_device_for_simulation(self, *devices: Device):
        """ Adds device to this miner for simulation. """

        for device in devices:
            if device in self._devices:
                self.logger.warning("Device {} is already binded. This might be a bug.".format(device.label))

            self._devices.append(device)
            self.logger.debug("Device {} is binded to {}.".format(device.label, self.name))

    def run(self) -> None:
        """ Runs this miner. """

        self.prepair_layer()
        if self.device_count <= 0:
            self.change_state(simulation_tools.MINER_IS_FINISHED)
            self.logger.info("Process {} no job to do. Ending miner.".format(self.name))
            return

        self.change_state(simulation_tools.MINER_IS_RUNNING)

        self._end_check_thread.start()
        for device_thread in self._device_thread_list:
            device_thread.start()

        while 1:
            action = self.threaded_request_queue.get()

            if isinstance(action, signal.SIGNAL):
                self.__handle_signal(action)

            elif isinstance(action, request.REQUEST):
                pass

            else:
                raise ValueError("Unrecognized action for {}. What \"{}\"?".format(self.name, action))

    def __handle_signal(self, signal_: signal.SIGNAL):
        """ Handles signals from devices. """

        if isinstance(signal_, signal.StateReportSignal):
            self.update_device_state(self.get_device_from(signal_.source_emiter), signal_.new_state)

        else:
            raise ValueError("Unrecognized signal for {}. What signal \"{}\"?".format(self.name, signal_))

    def check_finalize(self):
        time.sleep(0.5)
        while 1:
            excepted_states = (simulation_tools.MINER_IS_RUNNING, )
            if self.state in excepted_states and self.is_miner_endable():
                self.change_state(simulation_tools.MINER_MAY_END)
            time.sleep(1.5)

    def get_device_from(self, key: Union[int, str, uuid.UUID, Device], _raise=True) -> Union[Device, None]:
        """
        Tries to find device inside miner from given key.

        Args:
            key: Device identifier.
            _raise: Raise flag.

        Returns:
            Device or None.

        Raises:
            ValueError KeyError.
        """

        if isinstance(key, int):
            for i, device in enumerate(self._devices):
                if key == i:
                    return device

        elif isinstance(key, str):
            for device in self._devices:
                if key == device.label or key == device.uuid:
                    return device

        elif isinstance(key, uuid.UUID):
            for device in self._devices:
                if key == device.uuid:
                    return device

        elif isinstance(key, Device):
            if key in self._devices:
                return key
            else:
                if _raise:
                    raise KeyError("Device {} is not on this {}.".format(key.label, self.name))
                return None

        if _raise:
            raise ValueError("Device is not found on this {} by key {}.".format(self.name, key))
        else:
            return None

    def update_device_state(self, device: Device, new_state):
        """
        Updates device states using from singals.

        Args:
            device: Device.
            new_state: New state of device.
        """

        try:
            self._device_states[device] = new_state
        except (KeyError, IndexError) as E:
            raise E("Device {} is not found on miner {}. Update state failed.".format(device.label, self.name))

    def is_miner_endable(self):
        """ Checks miner if this process is enable. """

        self.update_device_matched_states()
        for device in self._devices:
            if self.device_to_thread_dict[device].is_alive():
                if self.device_states[device] != device_tools.DEVICE_MAY_END:
                    return False
        return True

    def update_device_matched_states(self):
        for device in self._devices:
            thread = self.device_to_thread_dict[device]
            if not thread.is_alive() and self.device_states[device] == device_tools.DEVICE_IS_RUNNING:
                self.device_states[device] = device_tools.DEVICE_IS_TERMINATED
                self.logger.warning("Device {} is probably termianted!".format(device.label))

            if not thread.is_alive() and self.device_states[device] == device_tools.DEVICE_IS_PAUSED:
                self.device_states[device] = device_tools.DEVICE_IS_TERMINATED
                self.logger.warning("Device {} is probably termianted!".format(device.label))

    @property
    def devices(self) -> List[Device]:
        return self._devices

    @property
    def sim_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.SIM_REQUEST_QUEUE)

    @property
    def user_dump_queue(self):
        return self.queue_manager.get_queue(architecture_tools.USER_DUMP_QUEUE)

    @property
    def end_check_thread(self):
        return self._end_check_thread

    @property
    def device_states(self) -> Dict[Device, str]:
        return self._device_states

    @property
    def device_to_thread_dict(self) -> Dict[Device, simulation_tools.TerminatableThread]:
        return self._device_thread_dict

    @property
    def thread_to_device_dict(self) -> Dict[simulation_tools.TerminatableThread, Device]:
        return self._thread_device_dict

    @property
    def device_count(self) -> int:
        return self._devices.__len__()