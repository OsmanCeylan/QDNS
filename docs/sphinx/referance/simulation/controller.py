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

from typing import List, Dict, Union

from QDNS.device.device import Device
from QDNS.simulation.miner import Process
from QDNS.tools.layer import ID_SIMULATION
from QDNS.tools.module import Module
from QDNS.simulation import tools


class MinerController(Module):
    controller_module_name = "Miner Module"

    def __init__(self, kernel_request_queue, user_dump_queue, miner_settings: tools.MinerControllerSettings):
        """
        Controlls the simulation processes.

        Args:
            kernel_request_queue: Request queue of kernel.
            user_dump_queue: User dump_queue of kernel.
            miner_settings: Miner settings.
        """

        super().__init__(
            ID_SIMULATION[0], self.controller_module_name,
            module_settings=miner_settings
        )

        # Set list and dicts.
        self._miner_list: List[Process] = list()
        self._miner_to_device: Dict[Process, List[Device]] = dict()
        self._miner_states: Dict[Process, str] = dict()

        # Set queues.
        self._kernel_request_queue = kernel_request_queue
        self._user_dump_queue = user_dump_queue

    def prepair_module(self):
        """
        Prepairs processes.
        Only simulation kernel should call this.
        """

        # Clear the lists.
        self._miner_list.clear()
        self._miner_to_device.clear()
        self._miner_states.clear()

        # Generate the processes.
        for i in range(self.max_process_count):
            miner = Process(self._kernel_request_queue, self._user_dump_queue, daemonized=self.daemonized)
            self._miner_list.append(miner)
            self._miner_to_device[miner] = list()
            self._miner_states[miner] = tools.MINER_NOT_STARTED

    def add_device_to_next(self, device: Device):
        """ Adds device to next miner for simulation. """

        minimum_device = self._miner_list[0]
        for miner in self._miner_list:
            if miner.device_count < minimum_device.device_count:
                minimum_device = miner

        minimum_device.add_device_for_simulation(device)
        self._miner_to_device[minimum_device].append(device)

    def start_module(self):
        """
        Starts all processes.
        Simulation kernel should this method.
        """

        for miner in self._miner_list:
            miner.start()

    def update_miner_matched_states(self):
        """ Updates process states by given reports. """

        for miner in self._miner_list:
            if not miner.is_alive() and self._miner_states[miner] == tools.MINER_IS_RUNNING:
                self._miner_states[miner] = tools.MINER_IS_FINISHED

            if not miner.is_alive() and self._miner_states[miner] == tools.MINER_MAY_END:
                self._miner_states[miner] = tools.MINER_IS_FINISHED

    def update_miner_state(self, miner: Process, new_state):
        """ Update process state given by report. """

        self._miner_states[miner] = new_state

    def is_simulation_endable(self) -> bool:
        """ Return if simulation can be ended. """

        self.update_miner_matched_states()
        for miner in self._miner_list:
            if self._miner_states[miner] == tools.MINER_IS_RUNNING:
                return False
        return True

    def get_miner(self, key: Union[int, str, Device], _raise=True) -> Union[Process, None]:
        """
        Gets the process by given key.

        Args:
            key: Key can be int, str or Device.
            _raise: Raise flag.

        Returns:
            Process, None

        Raises:
            ValueError if process cannot be found by given key.
        """

        for i, miner in enumerate(self._miner_list):
            if isinstance(key, int) and key == i:
                return miner

            if isinstance(key, str) and key == miner.name:
                return miner

            if isinstance(key, Device) and key in self._miner_to_device[miner]:
                return miner

        if _raise:
            raise ValueError("Process cannot found by given {}".format(key))
        return None

    @property
    def controller_settings(self) -> tools.MinerControllerSettings:
        return self.module_settings

    @property
    def max_process_count(self) -> int:
        return self.controller_settings.max_process_count

    @property
    def uses_real_cores(self) -> bool:
        return self.controller_settings.use_real_core_count

    @property
    def daemonized(self) -> bool:
        return self.controller_settings.processes_daemons

    @property
    def miner_list(self) -> List[Process]:
        return self._miner_list

    @property
    def miner_to_device(self) -> Dict[Process, List[Device]]:
        return self._miner_to_device

    @property
    def miner_states(self) -> Dict[Process, str]:
        return self._miner_states

    @property
    def miner_count(self) -> int:
        return self._miner_list.__len__()
