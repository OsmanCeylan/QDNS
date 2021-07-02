"""
## ==================================================##
##  Header of QF/simulation/miner_controller.py          ##
## ==================================================##

## ==================================================##
## Brief                                             ##
## Contains Simulation Miner Process                 ##
## ==================================================##
"""

from typing import Optional, List, Dict, Union

from QDNS.device.device import Device
from QDNS.simulation.miner import Miner
from QDNS.tools import simulation_tools


class MinerController(simulation_tools.KernelModule):
    module_name = "Miner Module"

    def __init__(
            self, kernel_request_queue, user_dump_queue,
            miner_settings: Optional[simulation_tools.MinerControllerSettings] = None
    ):
        """
        Controlls the simulation processes.
        """

        if miner_settings is None:
            miner_settings = simulation_tools.default_miner_controller_settings

        super().__init__(
            self.module_name, can_disable=False, can_removable=False, can_restartable=True,
            can_pausable=True, no_state_module=True, module_settings=miner_settings
        )

        self._miner_list: List[Miner] = list()
        self._miner_to_device: Dict[Miner, List[Device]] = dict()
        self._miner_states: Dict[Miner, str] = dict()

        self.kernel_request_queue = kernel_request_queue
        self.user_dump_queue = user_dump_queue

    def prepair_module(self):
        """
        Prepair processes.
        """

        self._miner_list.clear()
        self._miner_to_device.clear()
        self._miner_states.clear()

        for i in range(self.max_process_count - 1):
            miner = Miner(self.kernel_request_queue, self.user_dump_queue, daemonized=self.daemonized)
            self._miner_list.append(miner)
            self._miner_to_device[miner] = list()
            self._miner_states[miner] = simulation_tools.MINER_NOT_STARTED

    def add_device_to_next(self, device: Device):
        minimum_device = self._miner_list[0]
        for miner in self._miner_list:
            if miner.device_count < minimum_device.device_count:
                minimum_device = miner

        minimum_device.add_device_for_simulation(device)
        self._miner_to_device[minimum_device].append(device)

    def start_all_processes(self):
        for miner in self._miner_list:
            miner.start()

    def update_miner_matched_states(self):
        for miner in self._miner_list:
            if not miner.is_alive() and self._miner_states[miner] == simulation_tools.MINER_IS_RUNNING:
                self._miner_states[miner] = simulation_tools.MINER_IS_FINISHED

            if not miner.is_alive() and self._miner_states[miner] == simulation_tools.MINER_MAY_END:
                self._miner_states[miner] = simulation_tools.MINER_IS_FINISHED

    def update_miner_state(self, miner: Miner, new_state):
        self._miner_states[miner] = new_state

    def is_simulation_endable(self) -> bool:
        self.update_miner_matched_states()
        for miner in self._miner_list:
            if self._miner_states[miner] == simulation_tools.MINER_IS_RUNNING:
                return False
        return True

    def get_miner(self, key: Union[int, str, Device], _raise=True) -> Union[Miner, None]:
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
    def controller_settings(self) -> simulation_tools.MinerControllerSettings:
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
    def miner_list(self) -> List[Miner]:
        return self._miner_list

    @property
    def miner_to_device(self) -> dict[Miner, list[Device]]:
        return self._miner_to_device

    @property
    def miner_states(self) -> Dict[Miner, str]:
        return self._miner_states

    @property
    def miner_count(self) -> int:
        return self._miner_list.__len__()
