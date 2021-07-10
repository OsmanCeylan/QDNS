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

import logging
from typing import Tuple, Dict, Optional, Any

from QDNS.tools.instance_logger import SubLogger
from QDNS.architecture.signal import StateReportSignal

"""
##========================================  SIMPLE QUEUE MANAGER  ====================================================##
"""

# General Layer Queues.
LAYER_STATE_REPORT_QUEUE = "STATE REPORT QUEUE OF LAYER"
LAYER_REQUEST_QUEUE = "REQUEST QUEUE OF LAYER"
LAYER_RESPOND_QUEUE = "RESPOND QUEUE OF LAYER"
LAYER_THREADED_REQUEST_QUEUE = "THREADED REQUEST QUEUE OF LAYER"
LAYER_THREADED_RESPOND_QUEUE = "THREADED RESPOND QUEUE OF LAYER"

# Simulation queues.
SIM_REQUEST_QUEUE = "SIMULATION REQUEST QUEUE"
USER_DUMP_QUEUE = "USER DUMP QUEUE"

# Miner queues.
MINER_REQUEST_QUEUE = "MINER REQUEST QUEUE"

# Device queues.
DEVICE_REQUEST_QUEUE = "DEVICE REQUEST QUEUE"
LOCALHOST_QUEUE = "LOCALHOST QUEUE"

# Socket qeueus.
SOCKET_REQUEST_QUEUE = "SOCKET REQUEST QUEUE"
INCOME_CLASSIC_QUEUE = "SOCKET INCOME CLASSIC QUEUE"
INCOME_QUANTUM_QUEUE = "SOCKET INCOME QUANTUM QUEUE"
PING_HANDLE_QUEUE = "SOKCET PING HANDLE QUEUE"
PING_REQUEST_QUEUE = "PING REQUEST QUEUE"
OBSERVER_QUEUE = "OBSERVER QUEUE"

# Application Queues.
INCOME_QUBIT_QUEUE = "QUBIT QUEUE OF APPLICATION"
INCOME_PACKAGE_QUEUE = "PACKAGE QUEUE OF APPLICATION"


class QueueManager(object):
    def __init__(self, **kwargs):
        """
        'Foreign Queue' Manager mostly used for layers.
        QUEUE_NAME = QUEUE()
        """

        self._queue_dict = dict()
        for args in kwargs:
            self._queue_dict[args] = kwargs[args]

    def get_queue(self, label: str):
        try:
            return self._queue_dict[label]
        except (KeyError, IndexError) as E:
            raise E("Queue manager cannot parse queue for {}.".format(label))

    def add_queue(self, label: str, new_queue):
        if label in self._queue_dict.keys():
            raise KeyError("{} labeled queue is already in manager.".format(label))
        self._queue_dict[label] = new_queue

    def update_queue(self, label: str, new_queue):
        if label not in self._queue_dict.keys():
            raise KeyError("{} labeled queue is not in manager.".format(label))
        self._queue_dict[label] = new_queue

    def remove_queue(self, label):
        if label not in self._queue_dict.keys():
            raise KeyError("{} labeled queue is not in manager.".format(label))
        self._queue_dict.pop(label)

    def is_have_this_queue(self, label: str) -> bool:
        if label not in self._queue_dict.keys():
            return False
        return True

    def clear_queues(self):
        self._queue_dict.clear()

    @property
    def queue_count(self) -> int:
        return self._queue_dict.__len__()

    @property
    def queue_dict(self) -> dict:
        return self._queue_dict

    def __len__(self) -> int:
        return self._queue_dict.__len__()

    def __str__(self) -> str:
        to_return = str()
        to_return += "Queue Manager\n"
        to_return += "----------------\n"
        to_return += "Counts: {}\n".format(self.queue_count)
        to_return += "Queues: {}\n".format(self.queue_dict)
        return to_return


"""
##============================================  STATE HANDLER  =======================================================##
"""

GENERAL_STATE_NOT_STARTED = "GENERAL_STATE_NOT_STARTED"
GENERAL_STATE_IS_RUNNING = "GENERAL_STATE_IS_RUNNING"
GENERAL_STATE_IS_STOPPED = "GENERAL_STATE_IS_STOPPED"
GENERAL_STATE_IS_FINISHED = "GENERAL_STATE_IS_FINISHED"
GENERAL_STATE_IS_TERMINATED = "GENERAL_STATE_IS_TERMINATED"
GENERAL_STATE_MAY_END = "GENERAL_STATE_MAY_END"
GENERAL_STATE_IS_PAUSED = "GENERAL_STATE_IS_PAUSED"

GENERAL_STATE_FLAGS = (
    GENERAL_STATE_NOT_STARTED,
    GENERAL_STATE_IS_RUNNING,
    GENERAL_STATE_IS_STOPPED,
    GENERAL_STATE_IS_FINISHED,
    GENERAL_STATE_IS_TERMINATED,
    GENERAL_STATE_MAY_END,
    GENERAL_STATE_IS_PAUSED
)


class StateHandler(object):
    COUNT_STATES = "count_states"

    def __init__(self, layer_id: int, must_report_state, *states, **flags):
        """
        State handler for layered objects.

        Args:
            layer_id: Layer ID.
            must_report_state: State report flag.
            states: All layer states.
            flags: State flags.

        Raise:
            ValueError If state lenght is zero.
            ValueError If flags do not recognized.
            TypeError If counter state is not bool.

        Kwargs:
            counter_states = bool
            GENERAL_STATE_NOT_STARTED = state
            GENERAL_STATE_IS_RUNNING = state
            GENERAL_STATE_IS_STOPPED = state
            GENERAL_STATE_IS_FINISHED = state
            GENERAL_STATE_IS_TERMINATED = state
            GENERAL_STATE_MAY_END = state
            GENERAL_STATE_IS_PAUSED = state

        """

        if states.__len__() <= 0:
            raise ValueError("State object excepts at least 1 state.")

        self._states = states
        self._layer_id = layer_id

        self._current_state = states[0]
        self._count_states = False

        self._not_started_state = None
        self._is_running_state = None
        self._is_stopped_state = None
        self._is_finished_state = None
        self._is_terminated_state = None
        self._may_end_state = None
        self._is_paused_state = None

        self._state_counter_dict = dict()
        for state in self._states:
            self._state_counter_dict[state] = 0
        self._state_counter_dict[self._current_state] += 1

        for value in flags:
            if value == GENERAL_STATE_NOT_STARTED:
                self._not_started_state = flags[value]

            elif value == GENERAL_STATE_IS_RUNNING:
                self._is_running_state = flags[value]

            elif value == GENERAL_STATE_IS_STOPPED:
                self._is_stopped_state = flags[value]

            elif value == GENERAL_STATE_IS_FINISHED:
                self._is_finished_state = flags[value]

            elif value == GENERAL_STATE_IS_TERMINATED:
                self._is_terminated_state = flags[value]

            elif value == GENERAL_STATE_MAY_END:
                self._may_end_state = flags[value]

            elif value == GENERAL_STATE_IS_PAUSED:
                self._is_paused_state = flags[value]

            elif value == self.COUNT_STATES:
                if not isinstance(flags[value], bool):
                    raise TypeError("Excepted a bool for count_states but got {}".format(flags[value]))
                self._count_states = flags[value]

            else:
                raise ValueError("Exepted a general state but got {}.".format(value))

        self._must_report_state = must_report_state

    def change_state(self, new_state, _raise=True) -> bool:
        """
        Changes state of layer

        Args:
            new_state: New state of layer.
            _raise: Raise if not successfull.

        Raise:
            ValueError If state is not in dict.

        Return:
            Boolean.
        """

        if new_state not in self._states:
            if _raise:
                raise ValueError("Exepted a state for layer {} but got {}".format(self._layer_id, new_state))
            else:
                return False

        else:
            if self._current_state == new_state:
                return False

            if self._count_states:
                self._state_counter_dict[new_state] += 1

            self._current_state = new_state
            return True

    def is_state_counter_active(self) -> bool:
        return self._count_states

    def is_not_started_active(self) -> bool:
        if self._not_started_state is None:
            return False
        return True

    def is_running_active(self) -> bool:
        if self._is_running_state is None:
            return False
        return True

    def is_stopped_active(self) -> bool:
        if self._is_stopped_state is None:
            return False
        return True

    def is_finished_active(self) -> bool:
        if self._is_finished_state is None:
            return False
        return True

    def is_terminated_active(self) -> bool:
        if self._is_terminated_state is None:
            return False
        return True

    def is_may_end_active(self) -> bool:
        if self._may_end_state is None:
            return False
        return True

    def is_paused_active(self) -> bool:
        if self._is_paused_state is None:
            return False
        return True

    def is_started(self) -> bool:
        exptected = (self._is_paused_state, self._may_end_state, self._is_running_state)
        if self._current_state in exptected:
            return True
        return False

    def is_running(self) -> bool:
        expected = (self._is_running_state,)
        if self._current_state in expected:
            return True
        return False

    def is_finished(self) -> bool:
        expected = (self._is_finished_state,)
        if self._current_state in expected:
            return True
        return False

    def is_terminated(self) -> bool:
        expected = (self._is_terminated_state,)
        if self._current_state in expected:
            return True
        return False

    def may_end(self) -> bool:
        expected = (self._may_end_state,)
        if self._current_state in expected:
            return True
        return False

    def is_stopped(self) -> bool:
        expected = (self._is_terminated_state, self._is_finished_state, self._not_started_state)
        if self._current_state in expected:
            return True
        return False

    def is_breakable(self) -> bool:
        expected = (self._is_terminated_state, self._is_finished_state, self._not_started_state, self._may_end_state)
        if self._current_state in expected:
            return True
        return False

    @property
    def layer_id(self) -> int:
        return self._layer_id

    @property
    def state(self):
        return self._current_state

    @property
    def all_states(self):
        return self._states

    @property
    def state_not_started(self):
        return self._not_started_state

    @property
    def state_is_running(self):
        return self._is_running_state

    @property
    def state_is_stopped(self):
        return self._is_stopped_state

    @property
    def state_is_finished(self):
        return self._is_finished_state

    @property
    def state_is_terminated(self):
        return self._is_terminated_state

    @property
    def state_may_end(self):
        return self._may_end_state

    @property
    def state_is_paused(self):
        return self._is_paused_state

    @property
    def state_count(self):
        return self.all_states.__len__()

    @property
    def state_change_counts(self) -> dict:
        return self._state_counter_dict

    @property
    def is_reports_state(self) -> bool:
        return self._must_report_state

    def __int__(self):
        return self.state_count

    def __str__(self):
        to_return = str()
        to_return += "State Object\n"
        to_return += "------------------\n"
        to_return += "Owned Layer ID: {}\n".format(self.layer_id)
        to_return += "State Counter Acive: {}\n".format(self.is_state_counter_active())
        to_return += "Not Started Defined: {}\n".format(self.is_not_started_active())
        to_return += "Is Running Defined: {}\n".format(self.is_running_active())
        to_return += "Is Stopped Defined: {}\n".format(self.is_stopped_active())
        to_return += "Is Finished Defined: {}\n".format(self.is_finished_active())
        to_return += "Is Terminated Defined: {}\n".format(self.is_terminated_active())
        to_return += "May End Defined: {}\n".format(self.is_may_end_active())
        to_return += "Is Paused Defined: {}\n".format(self.is_paused_active())
        to_return += "Is Reports State: {}\n".format(self.is_reports_state)
        to_return += "All States:\n"
        to_return += "------------------\n"
        to_return += "{}\n".format(self.all_states)

        if self.is_state_counter_active():
            to_return += "------------------\n"
            to_return += "{}\n".format(self.state_change_counts)

        return to_return


"""
##===========================================  LAYER FLAGS  ==========================================================##
"""

# If layer simulation is in thread, its a thread layer.
# Else its a process layer.
THREAD_LAYER = "This layer run in a thread"
PROCESS_LAYER = "This layer run in a process"

layer_types = (
    THREAD_LAYER,
    PROCESS_LAYER
)

# Layers that are using in simulation.
ID_EPR_LAYER: Tuple[int, str] = (70, "Architecture identifier of epr layer.",)
ID_QKD_LAYER: Tuple[int, str] = (60, "Architecture identifier of qkd layer.",)
ID_APPLICATION: Tuple[int, str] = (80, "Architecture identifier of application layer.",)
ID_DEVICE: Tuple[int, str] = (40, "Architecture identifier of device layer.",)
ID_SOCKET: Tuple[int, str] = (50, "Architecture identifier of device's network socket layer.",)
ID_MINER: Tuple[int, str] = (20, "Architecture identifier of miner layer.",)
ID_SIMULATION: Tuple[int, str] = (10, "Architecture identifier of simulation layer.",)
ID_CHANNEL_CONTROLLER: Tuple[int, str] = (30, "Architecture identifier of channel controller layer.",)
ID_ANY_LAYER: Tuple[int, str] = (1000, "Symbolize a layer in arhitecture.",)

hardware_layers = (
    ID_SOCKET, ID_DEVICE, ID_EPR_LAYER, ID_QKD_LAYER, ID_CHANNEL_CONTROLLER
)

software_layers = (
    ID_SIMULATION, ID_MINER, ID_APPLICATION
)

layers = (
    ID_SOCKET,
    ID_DEVICE,
    ID_EPR_LAYER,
    ID_QKD_LAYER,
    ID_SIMULATION,
    ID_MINER,
    ID_APPLICATION,
    ID_CHANNEL_CONTROLLER,
    ID_ANY_LAYER
)

layer_to_layer_id: Dict[Tuple[int, str], int] = {
    ID_SIMULATION: ID_SIMULATION[0],
    ID_MINER: ID_MINER[0],
    ID_CHANNEL_CONTROLLER: ID_CHANNEL_CONTROLLER[0],
    ID_DEVICE: ID_DEVICE[0],
    ID_SOCKET: ID_SOCKET[0],
    ID_QKD_LAYER: ID_QKD_LAYER[0],
    ID_EPR_LAYER: ID_EPR_LAYER[0],
    ID_APPLICATION: ID_APPLICATION[0],
    ID_ANY_LAYER: ID_ANY_LAYER[0]
}

layer_to_layer_string: Dict[Tuple[int, str], str] = {
    ID_SIMULATION: ID_SIMULATION[1],
    ID_MINER: ID_MINER[1],
    ID_CHANNEL_CONTROLLER: ID_CHANNEL_CONTROLLER[1],
    ID_DEVICE: ID_DEVICE[1],
    ID_SOCKET: ID_SOCKET[1],
    ID_QKD_LAYER: ID_QKD_LAYER[1],
    ID_EPR_LAYER: ID_EPR_LAYER[1],
    ID_APPLICATION: ID_APPLICATION[1],
    ID_ANY_LAYER: ID_ANY_LAYER[1]
}

"""
##===========================================  ANY SETTINGS  =========================================================##
"""


class AnySettings(object):
    def __init__(self, **kwargs):
        """
        Any setting constructor.
        This class is template class, must inherit from this.

        Notes:
            {variable_name} = variable\n
            {variable_name_2} = variable_name_2\n
            ...

        Upmost settings template.
        """

        self._kwargs = kwargs

    def change_paramater(self, param, new_value):
        try:
            self._kwargs[param] = new_value
        except (KeyError, IndexError) as E:
            raise E("Expected layer settings but got {}.".format(param))

    def details(self) -> str:
        return self.__str__()

    @property
    def kwargs(self):
        return self._kwargs

    def __len__(self):
        return self._kwargs.__len__()

    def __str__(self):
        return str(self._kwargs)


"""
##===========================================  LAYER SETTINGS  =======================================================##
"""


class LayerSettings(AnySettings):
    def __init__(self, **kwargs):
        """
        Layer setting constructor.
        This class is template class, must inherit from this.

        Notes:
            {variable_name} = variable\n
            {variable_name_2} = variable_name_2\n
            ...
        """

        super(LayerSettings, self).__init__(**kwargs)

    def change_paramater(self, param, new_value):
        try:
            self._kwargs[param] = new_value
        except (KeyError, IndexError) as E:
            raise E("Expected layer settings but got {}.".format(param))

    def details(self) -> str:
        return self.__str__()

    @property
    def kwargs(self):
        return self._kwargs

    def __len__(self):
        return self._kwargs.__len__()

    def __str__(self):
        return str(self._kwargs)


"""
##===============================================  LAYER  ============================================================##
"""


class Layer(object):
    def __init__(
            self,
            layer: Tuple[int, str],
            layer_type: Tuple[str],
            layer_name: str,
            request_queue=None,
            respond_queue=None,
            state_handler: Optional[StateHandler] = None,
            layer_settings: Optional[LayerSettings] = None
    ):
        """
        Layer constructor.

        Args:
            layer: Layer flag in layers.
            layer_type: Layer type in layer_types.
            request_queue: Layer request queue.
            respond_queue: Layer respond queue.
            state_handler: State handler object for layer.

        Notes:
            Sets layer type None if layer type is unknown.
            Process must match layer type.
        """

        self._layer_id = layer_to_layer_id[layer]
        self._layer_string = layer_to_layer_string[layer]
        self._layer_name = layer_name

        self._layer_type = None
        if layer_type not in layer_types:
            logging.critical("Layer type {} is not recognized.".format(layer_type))
        else:
            self._layer_type = layer_type

        self._modules = list()

        if state_handler is not None and state_handler.layer_id != self._layer_id:
            raise ValueError("Layer {} has wrong layer id state handler.".format(self._layer_id))

        self._queue_manager = QueueManager()
        self._queue_manager.add_queue(LAYER_REQUEST_QUEUE, request_queue)
        self._queue_manager.add_queue(LAYER_RESPOND_QUEUE, respond_queue)
        self._queue_manager.add_queue(LAYER_THREADED_REQUEST_QUEUE, None)
        self._queue_manager.add_queue(LAYER_THREADED_RESPOND_QUEUE, None)

        self._state_handler = state_handler
        self._layer_settings = layer_settings
        self._logger = SubLogger(self._layer_name)

    def prepair_layer(self, *args):
        """
        Prepair the layer for simulation.
        Must run right before simulation.
        Layers must override this method.
        """

        pass

    def set_state_handler(self, new_handler: StateHandler) -> bool:
        if not new_handler.layer_id == self.layer_id:
            return False
        self._state_handler = new_handler
        return True

    def set_state_report_queue(self, report_queue):
        """
        Puts a report to the target layer's signal/request queue.
        Must be setted before simulation and state handler must be report flag to work.
        """

        self._queue_manager.add_queue(LAYER_STATE_REPORT_QUEUE, report_queue)

    def set_layer_settings(self, new_settings: LayerSettings):
        self._layer_settings = new_settings

    def add_module(self, new_module) -> bool:
        if new_module in self._modules:
            return False

        self.modules.append(new_module)
        return True

    def update_module(self, module, new_module) -> bool:
        if module.module_name != new_module.module_name:
            self.logger.warning("Cannot update module {}. Module names are mismatches with {}."
                                .format(module.module_name, new_module.module_name))
            return False

        if not self.remove_module(module):
            self.logger.error("Revoing module {} is failed.".format(module.module_name))
            return False
        self.add_module(new_module)
        return True

    def remove_module(self, module) -> bool:
        """
        Removes module from layer.

        Args:
            module: Module name or module object.

        Notes:
            Module should have removable.
        """

        to_remove = None
        for m in self._modules:
            if m == module or m == module.module_name:
                to_remove = m
                break

        if to_remove is not None:
            if to_remove.can_removable:
                self._modules.remove(to_remove)
                return True
            else:
                return False
        else:
            return False

    def get_module(self, key):
        """
        Gets the module given key.

        Args:
            key: Module name or module object.

        Returns:
            Module or None.
        """

        for module in self._modules:
            if key == module or key == module.module_name:
                return module

        return None

    def set_queues(self, request_queue, respond_queue):
        """ Sets multiprocessing queues. """

        self._queue_manager.update_queue(LAYER_REQUEST_QUEUE, request_queue)
        self._queue_manager.update_queue(LAYER_RESPOND_QUEUE, respond_queue)

    def set_request_queue(self, request_queue):
        """ Sets multiprocessing request queue. """

        self._queue_manager.update_queue(LAYER_REQUEST_QUEUE, request_queue)

    def set_respond_queue(self, respond_queue):
        """ Sets multiprocessing respond queue. """

        self._queue_manager.update_queue(LAYER_RESPOND_QUEUE, respond_queue)

    def set_threaded_queues(self, request_queue, respond_queue):
        """ Sets threaded queues. """

        self._queue_manager.update_queue(LAYER_THREADED_REQUEST_QUEUE, request_queue)
        self._queue_manager.update_queue(LAYER_THREADED_RESPOND_QUEUE, respond_queue)

    def layer_details(self) -> str:
        to_return = str()
        to_return += "Layer_ID: {}\n".format(self._layer_id)
        to_return += "Layer Str: {}\n".format(self._layer_string)
        to_return += "Layer Type: {}\n".format(self._layer_type)

        if self.request_queue is None:
            bind = False
        else:
            bind = True
        to_return += "Request Binded: {}\n".format(bind)

        if self.respond_queue is None:
            bind = False
        else:
            bind = True
        to_return += "Respond Binded: {}\n".format(bind)

        if self._layer_settings is not None:
            bind = True
        else:
            bind = False
        to_return += "Settings Binded: {}\n".format(bind)
        return to_return

    def settings_details(self):
        if self._layer_settings is None:
            return None
        else:
            return self._layer_settings.details()

    def is_have_this_module(self, key) -> bool:
        """
        Searches the module given key.

        Args:
            key: Module name or module object.

        Returns:
            Boolean.
        """

        if self.get_module(key) is None:
            return False
        return True

    def is_have_module(self) -> bool:
        if self._modules.__len__() <= 0:
            return False
        return True

    def change_state(self, new_state, _raise=True, log_level=logging.DEBUG):
        """
        Changes and log the state change by using state handler.

        Args:
            new_state: New state.
            _raise: Raise if change state counters critical error.
            log_level: Log level.

        Returns:
            Boolean.
        """

        if self._state_handler is not None:
            to_return = self.state_handler.change_state(new_state, _raise=_raise)

            if to_return:
                self.logger.log("{} changes state to {}".format(self.layer_name, new_state), log_level)
                if self._state_handler.is_reports_state:
                    if self.state_report_queue is not None:
                        StateReportSignal(self.layer_name, self.state).emit(self.state_report_queue)
            return to_return
        return False

    def change_settings(self, param: Any, new_value: Any):
        if self._layer_settings is not None:
            return self._layer_settings.change_paramater(param, new_value)

    @property
    def state_handler(self) -> StateHandler:
        return self._state_handler

    @property
    def layer_setting(self):
        return self._layer_settings

    @property
    def layer_id(self) -> int:
        return self._layer_id

    @property
    def layer_string(self) -> str:
        return self._layer_string

    @property
    def layer_name(self) -> str:
        return self._layer_name

    @property
    def layer_type(self):
        return self._layer_type

    @property
    def modules(self) -> list:
        return self._modules

    @property
    def module_legth(self) -> int:
        return self._modules.__len__()

    @property
    def request_queue(self):
        return self.queue_manager.get_queue(LAYER_REQUEST_QUEUE)

    @property
    def respond_queue(self):
        return self.queue_manager.get_queue(LAYER_RESPOND_QUEUE)

    @property
    def threaded_request_queue(self):
        return self.queue_manager.get_queue(LAYER_THREADED_REQUEST_QUEUE)

    @property
    def threaded_respond_queue(self):
        return self.queue_manager.get_queue(LAYER_THREADED_RESPOND_QUEUE)

    @property
    def logger(self) -> SubLogger:
        return self._logger

    @property
    def state(self):
        return self._state_handler.state

    @property
    def state_report_queue(self):
        return self.queue_manager.get_queue(LAYER_STATE_REPORT_QUEUE)

    @property
    def queue_manager(self) -> QueueManager:
        return self._queue_manager

    def __int__(self):
        return self._layer_id

    def __str__(self):
        return self._layer_string


"""
##===========================================  MODULE SETTINGS  ======================================================##
"""


class ModuleSettings(AnySettings):
    def __init__(self, **kwargs):
        """
        Module setting constructor.
        This class is template class, must inherit from this.

        Notes:
            {variable_name} = variable\n
            {variable_name_2} = variable_name_2\n
            ...

        Uses same template as Settings.
        """

        super(ModuleSettings, self).__init__(**kwargs)

    def change_paramater(self, param, new_value):
        try:
            self._kwargs[param] = new_value
        except (KeyError, IndexError) as E:
            raise E("Expected module settings but got {}.".format(param))

    def details(self) -> str:
        return self.__str__()

    @property
    def kwargs(self):
        return self._kwargs

    def __len__(self):
        return self._kwargs.__len__()


"""
##===============================================  MODULE  ===========================================================##
"""


class Module(object):
    MODULE_NOT_STARTED = "\"module is not started.\""
    MODULE_IS_RUNNNG = "\"module is running.\""
    MODULE_IS_FINISHED = "\"module is finished.\""
    MODULE_IS_TERMINATED = "\"module is terminated.\""
    MODULE_IS_PASUED = "\"module is paused.\""

    MODULE_STATES = (
        MODULE_NOT_STARTED,
        MODULE_IS_RUNNNG,
        MODULE_IS_FINISHED,
        MODULE_IS_TERMINATED,
        MODULE_IS_PASUED,
    )

    def __init__(
            self, layer_id, module_name, module_object, can_disable=True,
            can_removable=False, can_restartable=True, can_pausable=True,
            no_state_module: bool = True,
            special_state: Optional[StateHandler] = None,
            module_settings: Optional[ModuleSettings] = None
    ):
        """
        Mdoule constructor.

        Args:
            layer_id: Module owner layer ID.
            module_name: Module name.
            module_object: Module object.
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

        self._layer_id = layer_id
        self._module_name = module_name
        self._module_object = module_object
        self._can_disable = can_disable
        self._can_removable = can_removable
        self._can_restartable = can_restartable
        self._can_pausable = can_pausable
        self._no_state_module = no_state_module

        self._disabled = False

        if not self._no_state_module:
            if special_state is None:
                self._state = StateHandler(
                    self._layer_id, False, *self.MODULE_STATES,
                    GENERAL_STATE_NOT_STARTED=self.MODULE_NOT_STARTED,
                    GENERAL_STATE_IS_RUNNING=self.MODULE_IS_RUNNNG,
                    GENERAL_STATE_IS_FINISHED=self.MODULE_IS_FINISHED,
                    GENERAL_STATE_IS_TERMINATED=self.MODULE_IS_TERMINATED,
                    GENERAL_STATE_IS_PAUSED=self.MODULE_IS_PASUED
                )

            else:
                self._state = special_state
        else:
            self._state = None

        self._module_setting = module_settings

    def prepair_module(self):
        """
        Prepirs module for simulation.

        # Must override method.
        """

        pass

    def enable_module(self) -> bool:
        """
        Enables Module.

        Return:
            True if module state changed to enabled.
            False if module state is not changed.

        # Must override method.
        """

        pass

    def pause_module(self) -> bool:
        """
        Pauses Module.

        Return:
            True if module state changed to paused.
            False if module state is not changed..

        # Must override method.
        """

        pass

    def resume_module(self) -> bool:
        """
        Resume Module.

        Return:
            True if module state changed to running.
            False if module state is not changed.

        # Must override method.
        """

        pass

    def disable_module(self) -> bool:
        """
        Disables Module.

        Return:
            True if module can disable.
            False if module cannot disable.

        # Must override method.
        """

        pass

    def start_module(self) -> bool:
        """
        Starts Module.

        Return:
            True if module can start now.
            False if module cannot start now.

        # Must override method.
        """

        pass

    def stop_module(self) -> bool:
        """
        Stops Module.

        Return:
            True if module state can changed to stopped.
            False if module state not changed..

        # Must override method.
        """

        pass

    def restart_module(self) -> bool:
        """
        Restarts Module.

        Return:
            True if module can restartable.
            False if module cannot restartable.

        # Must override method.
        """

        pass

    def is_enabled(self) -> bool:
        return not self._disabled

    def is_disabled(self) -> bool:
        return self._disabled

    def set_new_settings(self, new_settings: ModuleSettings):
        self._module_setting = new_settings

    def module_details(self) -> str:
        to_return = str()
        to_return += "Module Info\n"
        to_return += "-------------------\n"
        to_return += "Layer ID: {}\n".format(self.layer_id)
        to_return += "Module name: {}\n".format(self.module_name)
        if self._no_state_module:
            bind = "No state module"
        else:
            bind = self.state
        to_return += "Module state: {}\n".format(bind)
        return to_return

    def settings_details(self):
        if self._module_setting is None:
            return None
        else:
            return self._module_setting.details()

    @property
    def state(self):
        return self._state.state

    @property
    def state_object(self) -> StateHandler:
        return self._state

    @property
    def layer_id(self) -> int:
        return self._layer_id

    @property
    def module_name(self) -> str:
        return self._module_name

    @property
    def module_object(self):
        return self._module_object

    @property
    def can_disable(self) -> bool:
        return self._can_disable

    @property
    def can_removable(self) -> bool:
        return self._can_removable

    @property
    def can_pausable(self) -> bool:
        return self._can_pausable

    @property
    def can_restartable(self) -> bool:
        return self._can_restartable

    @property
    def module_settings(self):
        return self._module_setting

    def __int__(self):
        return self._layer_id
