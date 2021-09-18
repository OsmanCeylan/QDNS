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

from typing import Union
from psutil import cpu_count

from QDNS.tools.module import ModuleSettings

core_count = cpu_count(logical=False)
thread_count = cpu_count(logical=True)

# Simulation states.
SIMULATION_NOT_STARTED = "\"simulation is not started\""
SIMULATION_IS_RUNNING = "\"simulation is running\""
SIMULATION_IS_FINISHED = "\"simulation is over\""
SIMULATON_IS_STOPPED = "\"simulation is stopped\""
SIMULATON_IS_TERMINATED = "\"simulation is terminated\""
SIMULATION_IS_PAUSED = "\"simulation is paused\""

simulation_states = (
    SIMULATION_NOT_STARTED,
    SIMULATION_IS_RUNNING,
    SIMULATION_IS_FINISHED,
    SIMULATON_IS_STOPPED,
    SIMULATON_IS_TERMINATED,
    SIMULATION_IS_PAUSED
)

kernel_layer_label = "Kernel"

# Process states.
MINER_NOT_STARTED = "\"miner process not started\""
MINER_IS_RUNNING = "\"miner process is running\""
MINER_MAY_END = "\"miner process may end\""
MINER_IS_FINISHED = "\"miner is finished\""

miner_states = (
    MINER_NOT_STARTED,
    MINER_IS_RUNNING,
    MINER_MAY_END,
    MINER_IS_FINISHED
)


class MinerControllerSettings(ModuleSettings):
    __all_cores__ = "use all cores"
    __half_cores__ = "use half cores"
    __quarter_cores__ = "use quarter cores"

    cpu_core_count_ = "cpu_core_count"
    use_real_cores_ = "use real_cores_"
    daemonize_ = "daemonize_"

    def __init__(
            self, max_cpu_core_count: Union[int, str],
            use_real_cores: bool, miner_daemons: bool
    ):
        """
        Miner Controller Settings.

        Args:
            max_cpu_core_count: Maximum avaible cpu core count.
            use_real_cores: Use only physical cores.
            miner_daemons: Processes are daemons.
        """

        core_count_final = core_count
        if max_cpu_core_count == self.__all_cores__:
            if use_real_cores:
                core_count_final = core_count
            else:
                core_count_final = thread_count

        elif max_cpu_core_count == self.__half_cores__:
            if use_real_cores:
                core_count_final = int(core_count / 2)
            else:
                core_count_final = int(thread_count / 2)

        elif max_cpu_core_count == self.__quarter_cores__:
            if use_real_cores:
                core_count_final = core_count
            else:
                core_count_final = thread_count

        else:
            if max_cpu_core_count > core_count and use_real_cores:
                core_count_final = core_count

            if max_cpu_core_count > thread_count and not use_real_cores:
                core_count_final = thread_count

        kwargs = {
            self.cpu_core_count_: core_count_final,
            self.use_real_cores_: use_real_cores,
            self.daemonize_: miner_daemons
        }
        super(MinerControllerSettings, self).__init__(
            can_disable=False, can_restartable=False,
            can_removalbe=False, no_state_module=True,
            logger_enabled=False, **kwargs
        )

    def change_max_process_count(self, new_value: int):
        """ Changes max process count for devices. """

        self.change_paramater(self.cpu_core_count_, new_value)

    @property
    def max_process_count(self) -> int:
        return self.get_setting(self.cpu_core_count_)

    @property
    def use_real_core_count(self) -> bool:
        return self.get_setting(self.use_real_cores_)

    @property
    def processes_daemons(self) -> bool:
        return self.get_setting(self.daemonize_)


default_controller_settings = MinerControllerSettings(
    MinerControllerSettings.__half_cores__, True, True
)


def change_deafault_miner_controller_settings(new_settings: MinerControllerSettings):
    """
    Changes default miner controller module settings.
    Must call before simulation.
    """

    global default_controller_settings
    default_controller_settings = new_settings


class SimulationResults(object):
    def __init__(self, readings):
        """
        Simulation result.
        Kernel knows the format of reading.
        """

        self.readings = readings

    def device_logs(self, device_label: str):
        """
        Logs of given device.
        """

        if self.readings[device_label]["DeviceLogs"].__len__() <= 1:
            if self.readings[device_label]["DeviceLogs"][0].__len__() <= 1:
                return self.readings[device_label]["DeviceLogs"][0][0]
            return self.readings[device_label]["DeviceLogs"][0]
        return self.readings[device_label]["DeviceLogs"]

    def application_logs(self, device_label: str, application_label: str):
        """
        Logs of given application of given device.
        """

        if self.readings[device_label][application_label + "Logs"].__len__() <= 1:
            if self.readings[device_label][application_label + "Logs"][0].__len__() <= 1:
                return self.readings[device_label][application_label + "Logs"][0][0]
            return self.readings[device_label][application_label + "Logs"][0]
        return self.readings[device_label][application_label + "Logs"]

    def user_dumpings(self, device_label: str, application_label: str):
        """
        User outputs of given application of given device.
        """

        if self.readings[device_label][application_label].__len__() <= 1:
            if self.readings[device_label][application_label][0].__len__() <= 1:
                return self.readings[device_label][application_label][0][0]
            return self.readings[device_label][application_label][0]
        return self.readings[device_label][application_label]

    def simulation_logs(self):
        """
        Logs of simulation instance.
        """

        return self.readings["SimulationLogs"]

    def backend_logs(self):
        """
        Logs of backend wrapper.
        """

        return self.readings["BackendLogs"]