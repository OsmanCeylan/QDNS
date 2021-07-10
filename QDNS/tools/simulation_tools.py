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

import ctypes
import threading
from typing import Optional
from psutil import cpu_count

from QDNS.tools import architecture_tools

core_count = cpu_count(logical=False)
thread_count = cpu_count(logical=True)

"""
##===============================================  TERM. THREAD  =====================================================##
"""


def terminate_thread(thread):
    """
    Terminates the thread but not consistent solution,
    this because not always main thread calls this method.
    Child threads mostly call this for another child for most of time.
    Make sure call this function in try, except block.
    """

    if not thread.is_alive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("Nonexistent thread id")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class TerminatableThread(threading.Thread):
    def __init__(self, target_method, *data, daemon=False, args=None):

        if args is None:
            args = tuple()

        super().__init__(target=target_method, args=(*args,), daemon=daemon)
        self._data = data

    def terminate(self):
        terminate_thread(self)

    def data_(self, index):
        try:
            return self._data[index]
        except (KeyError, IndexError):
            return None

    @property
    def data(self):
        return self._data


"""
##===============================================  MINER STATES ======================================================##
"""

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

"""
##===============================================  MINER STATES ======================================================##
"""

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

"""
##==============================================  KERNEL MODULE ======================================================##
"""


class KernelModule(architecture_tools.Module):
    def __init__(
            self, module_name, can_disable=True,
            can_removable=False, can_restartable=True, can_pausable=True,
            no_state_module: bool = True,
            special_state: Optional[architecture_tools.StateHandler] = None,
            module_settings: Optional[architecture_tools.ModuleSettings] = None
    ):
        """
        Kernek Module.

        Args:
            module_name: Module name.
            can_disable: Is module disable.
            can_removable: Is module removable.
            can_restartable: Is module restartable.
            can_pausable: Is module pausable.
            no_state_module: Module do not uses states.
            special_state: Use special state handler.
            module_settings: Use module settings for module.

        Notes:
            Only layered objects should have a module.
            Modules should have remove, disable, restart, enable actions.
            Module settings should have specialized for module.
        """

        super(KernelModule, self).__init__(
            architecture_tools.ID_SIMULATION[0], module_name, self, can_disable=can_disable,
            can_removable=can_removable, can_restartable=can_restartable, can_pausable=can_pausable,
            no_state_module=no_state_module,
            special_state=special_state,
            module_settings=module_settings
        )


"""
##============================================  MINER CONT. MODULE ===================================================##
"""


class MinerControllerSettings(architecture_tools.ModuleSettings):
    __all_cores__ = "use all cores"
    __half_cores__ = "use half cores"
    __quarter_cores__ = "use quarter cores"

    def __init__(self, max_cpu_core_count, use_real_cores: bool, miner_daemons: bool = True):
        """
        Miner Controller Settings.

        Args:
            max_cpu_core_count: Maximum avaible cpu core count.
            use_real_cores: Use only physical cores.
            miner_daemons: Processes are daemons.
        """

        self._max_cpu_core_count = max_cpu_core_count
        self._use_real_cores = use_real_cores
        self._miner_daemons = miner_daemons

        if self._max_cpu_core_count == self.__all_cores__:
            if self._use_real_cores:
                self._max_cpu_core_count = core_count
            else:
                self._max_cpu_core_count = thread_count

        elif self._max_cpu_core_count == self.__half_cores__:
            if self._use_real_cores:
                self._max_cpu_core_count = int(core_count / 2)
            else:
                self._max_cpu_core_count = int(thread_count / 2)

        elif self._max_cpu_core_count == self.__quarter_cores__:
            if self._use_real_cores:
                self._max_cpu_core_count = core_count
            else:
                self._max_cpu_core_count = thread_count

        else:
            if self._max_cpu_core_count > core_count and self._use_real_cores:
                self._max_cpu_core_count = core_count

            if self._max_cpu_core_count > thread_count and not self._use_real_cores:
                self._max_cpu_core_count = thread_count

        super(MinerControllerSettings, self).__init__(
            max_cpu_core_count=max_cpu_core_count, use_real_cores=use_real_cores, miner_daemons=self._miner_daemons
        )

    @property
    def max_process_count(self) -> int:
        return self._max_cpu_core_count

    @property
    def use_real_core_count(self) -> bool:
        return self._use_real_cores

    @property
    def processes_daemons(self) -> bool:
        return self._miner_daemons


default_miner_controller_settings = MinerControllerSettings(MinerControllerSettings.__all_cores__, False, True)


def change_deafault_miner_controller_settings(new_settings: MinerControllerSettings):
    """
    Changes default miner controller module settings.
    Must call before simulation.
    """

    global default_miner_controller_settings
    default_miner_controller_settings = new_settings


"""
##===============================================  NOISE =====================================================##
"""

reset_channel = "reset channel"
asymmetric_depolarisation_channel = "asymmetric_depolarizing channel"
depolarisation_channel = "depolarisation"
bit_flip_channel = "bit_flip_channel"
phase_flip_channel = "phase_flip_channel"
bit_and_phase_flip_channel = "bit_and_phase_flip"
no_noise_channel = "no noise channel"

channels = (
    depolarisation_channel, bit_flip_channel, phase_flip_channel,
    asymmetric_depolarisation_channel, bit_and_phase_flip_channel,
    reset_channel, no_noise_channel
)


class NoisePattern(object):
    def __init__(
            self,
            sp_probability: float,
            measure_probability: float,
            gate_error_probability: float,
            scramble_probability: float,
            sp_channel=bit_flip_channel,
            measure_channel=bit_flip_channel,
            gate_channel=depolarisation_channel,
            scramble_channel=depolarisation_channel,
    ):
        """
        Noise pattern of backend.

        Args:
            sp_probability: State Prepair Error Probability.
            measure_probability: Measure Error Probability.
            gate_error_probability: Gate Error Probability.
            scramble_probability: Scramble Percent.
            sp_channel: State Prepair Error Channel.
            measure_channel: Measure Error Channel.
            gate_channel: Gate Error Channel.
            scramble_channel: Scramble Channel.

        Notes:
            Scramble Channel method also used for quantum channel scrambling.
        """

        self.state_prepare_error_probability = (sp_probability,)
        self.state_prepare_error_channel = sp_channel

        self.measure_error_probability = (measure_probability,)
        self.measure_error_channel = measure_channel

        self.gate_error_probability = (gate_error_probability,)
        self.gate_error_channel = gate_channel

        self.scramble_percent = (scramble_probability,)
        self.scramble_channel = scramble_channel

    def __str__(self) -> str:
        text = str()
        text += "State Prepair: " + self.state_prepare_error_channel + " | " + str(self.state_prepare_error_probability) + "\n"
        text += "Measure: " + self.measure_error_channel + " | " + str(self.measure_error_probability) + "\n"
        text += "Gate Error: " + self.gate_error_channel + " | " + str(self.gate_error_probability) + "\n"
        text += "Scramble Error: " + self.scramble_channel + " | " + str(self.scramble_percent) + "\n"
        return text


default_noise_pattern = NoisePattern(
    0.005, 0.005, 0.005, 0.667,
    sp_channel=bit_flip_channel,
    measure_channel=bit_flip_channel,
    gate_channel=phase_flip_channel,
    scramble_channel=depolarisation_channel,
)


def change_default_noise_pattern(new_pattern: NoisePattern):
    """
    Changes default noise pattern.
    """

    global default_noise_pattern
    default_noise_pattern = new_pattern


"""
##===============================================  SIM RESULTS =====================================================##
"""


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