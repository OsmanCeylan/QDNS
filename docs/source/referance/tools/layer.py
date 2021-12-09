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

from typing import Tuple, Dict, Optional, Any, Union, List
import logging

from QDNS.interactions.signal import StateReportSignal
from QDNS.tools.any_settings import AnySettings
from QDNS.tools.any_settings import default_any_setting
from QDNS.tools import queue_manager
from QDNS.tools.instance_logger import SubLogger
from QDNS.tools.module import Module
from QDNS.tools.state_handler import StateHandler


# Layer types.
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


class Layer(object):
    def __init__(
            self,
            layer: Tuple[int, str], layer_type: str,
            layer_name: str, logger_name: Optional[str] = None,
            state_handler: Optional[StateHandler] = None,
            layer_settings=default_any_setting
    ):
        """
        Layer constructor.

        Args:
            layer: Layer flag in layers.
            layer_type: Layer type in layer_types.
            layer_name: Name of layer.
            logger_name: Sets the logger name different.
            state_handler: State handler object for layer.
            layer_settings: Settings of layer.

        Notes:
            Sets layer type None if layer type is unknown.
            Process must match layer type.
        """

        # Set layer id's.
        self._layer_id = layer_to_layer_id[layer]
        self._layer_string = layer_to_layer_string[layer]
        self._layer_name = layer_name

        # Check layer type.
        self._layer_type = None
        if layer_type not in layer_types:
            logging.critical("Layer type {} is not recognized.".format(layer_type))
        else:
            self._layer_type = layer_type

        # Add module list.
        self._modules = list()

        # Check state handler.
        if state_handler is not None and state_handler.layer_id != self._layer_id:
            raise ValueError("Layer {} has wrong layer id state handler.".format(self._layer_id))

        # Create queue manager.
        self._queue_manager = queue_manager.QueueManager()
        self._queue_manager.add_queue(queue_manager.LAYER_REQUEST_QUEUE, None)
        self._queue_manager.add_queue(queue_manager.LAYER_RESPOND_QUEUE, None)
        self._queue_manager.add_queue(queue_manager.LAYER_THREADED_REQUEST_QUEUE, None)
        self._queue_manager.add_queue(queue_manager.LAYER_THREADED_RESPOND_QUEUE, None)

        # Set state handler and setting.
        self._state_handler = state_handler
        self._layer_settings = layer_settings

        # Set logger.
        self._logger_name = logger_name
        if self._logger_name is None:
            self._logger_name = self._layer_name
        self._logger = SubLogger(self._logger_name)

    def prepair_layer(self, *args):
        """
        Prepair the layer for simulation.
        Must run right before simulation.
        Layers must override this method.
        """

        pass

    def set_state_handler(self, new_handler: StateHandler) -> bool:
        """ Sets new state handler. """

        # Checks layer compability.
        if not new_handler.layer_id == self.layer_id:
            return False

        self._state_handler = new_handler
        return True

    def set_state_report_queue(self, report_queue):
        """
        Puts a report to the target layer's signal/request queue.
        Must be setted before simulation and state handler must be report flag to work.
        """

        self._queue_manager.add_queue(queue_manager.LAYER_STATE_REPORT_QUEUE, report_queue)

    def set_layer_settings(self, new_settings: AnySettings):
        """ Sets new layer settings. """

        self._layer_settings = new_settings

    def add_module(self, new_module: Module):
        """ Add module to layer. """

        if new_module in self._modules:
            raise ValueError("Module {} is already exists.".format(new_module.module_name))

        for module in self._modules:
            if module.module_name == new_module:
                raise ValueError("Module {} is already exists.".format(new_module.module_name))

        self.modules.append(new_module)

    def update_module(self, module: Module, new_module: Module) -> bool:
        """ Updates module with the new one. """

        # Check module compability.
        if module.module_name != new_module.module_name:
            self.logger.warning("Cannot update module {}. Module names are mismatches with {}."
                                .format(module.module_name, new_module.module_name))
            return False

        # Remove old module.
        if not self.remove_module(module):
            self.logger.error("Revoing module {} is failed.".format(module.module_name))
            return False

        self.add_module(new_module)
        return True

    def remove_module(self, module: Union[Module, str]) -> bool:
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

    def get_module(self, key: Union[str, Module]):
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

        self._queue_manager.update_queue(queue_manager.LAYER_REQUEST_QUEUE, request_queue)
        self._queue_manager.update_queue(queue_manager.LAYER_RESPOND_QUEUE, respond_queue)

    def set_request_queue(self, request_queue):
        """ Sets multiprocessing request queue. """

        self._queue_manager.update_queue(queue_manager.LAYER_REQUEST_QUEUE, request_queue)

    def set_respond_queue(self, respond_queue):
        """ Sets multiprocessing respond queue. """

        self._queue_manager.update_queue(queue_manager.LAYER_RESPOND_QUEUE, respond_queue)

    def set_threaded_queues(self, request_queue, respond_queue):
        """ Sets threaded queues. """

        self._queue_manager.update_queue(queue_manager.LAYER_THREADED_REQUEST_QUEUE, request_queue)
        self._queue_manager.update_queue(queue_manager.LAYER_THREADED_RESPOND_QUEUE, respond_queue)

    def layer_details(self) -> str:
        """ Returns layer details as __str__. """

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
        """ Returns the layer settings. """

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
        """ Retrurn if layer has any module. """

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

        old_state = self._state_handler.state
        if self._state_handler is not None:
            to_return = self.state_handler.change_state(new_state, _raise=_raise)

            if to_return:
                self.logger.log(":State: {} ---> {}".format(old_state, new_state), log_level)
                if self._state_handler.is_reports_state:
                    if self.state_report_queue is not None:
                        StateReportSignal(self.layer_name, self.state).emit(self.state_report_queue)
            return to_return
        return False

    def change_settings(self, param: Any, new_value: Any):
        """ Changes a settings in layer. """

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
    def logger_label(self) -> str:
        return self._logger.host

    @property
    def modules(self) -> List[Module]:
        return self._modules

    @property
    def module_legth(self) -> int:
        return self._modules.__len__()

    @property
    def request_queue(self):
        return self.queue_manager.get_queue(queue_manager.LAYER_REQUEST_QUEUE)

    @property
    def respond_queue(self):
        return self.queue_manager.get_queue(queue_manager.LAYER_RESPOND_QUEUE)

    @property
    def threaded_request_queue(self):
        return self.queue_manager.get_queue(queue_manager.LAYER_THREADED_REQUEST_QUEUE)

    @property
    def threaded_respond_queue(self):
        return self.queue_manager.get_queue(queue_manager.LAYER_THREADED_RESPOND_QUEUE)

    @property
    def logger(self) -> SubLogger:
        return self._logger

    @property
    def logger_name(self) -> str:
        return self._logger_name

    @property
    def state(self) -> str:
        return self._state_handler.state

    @property
    def state_report_queue(self):
        return self.queue_manager.get_queue(queue_manager.LAYER_STATE_REPORT_QUEUE)

    @property
    def queue_manager(self) -> queue_manager.QueueManager:
        return self._queue_manager

    def __int__(self):
        return self._layer_id

    def __str__(self):
        return self._layer_string
