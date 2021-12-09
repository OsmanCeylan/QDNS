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

from typing import Optional

from QDNS.tools.any_settings import AnySettings
from QDNS.tools.instance_logger import SubLogger
from QDNS.tools.state_handler import StateHandler


class ModuleSettings(AnySettings):
    can_disable_ = "can disable"
    can_restartable_ = "can restartable"
    can_removable_ = "can removable"
    no_state_module_ = "no state module"
    logger_enabled_ = "logger enabled"

    def __init__(
            self,
            can_disable, can_restartable,
            can_removalbe, no_state_module,
            logger_enabled, **kwargs
    ):
        """
        Module setting constructor.
        This class is template class, must inherit from this.

        Args:
            can_disable: Module can be disabled.
            can_restartable: Module can be restarted.
            can_removable: Module can be removed.
            no_state_module: Module have no state handler.
            logger_enabled: Module have sublogger.

        Notes:
            {variable_name} = variable_value\n
            {variable_name_2} = variable_value\n
            ...

        Uses same template as Settings.
        """

        kwargs[self.can_disable_] = can_disable
        kwargs[self.can_restartable_] = can_restartable
        kwargs[self.can_removable_] = can_removalbe
        kwargs[self.no_state_module_] = no_state_module
        kwargs[self.logger_enabled_] = logger_enabled
        super(ModuleSettings, self).__init__(**kwargs)

    @property
    def can_disable(self):
        return self.get_setting(self.can_disable_)

    @property
    def can_restartable(self):
        return self.get_setting(self.can_restartable_)

    @property
    def can_removable(self):
        return self.get_setting(self.can_removable_)

    @property
    def no_state_module(self):
        return self.get_setting(self.no_state_module_)

    @property
    def logger_enabled(self):
        return self.get_setting(self.logger_enabled_)

    def __str__(self) -> str:
        text = str()
        text += "Can disable: {}\n".format(self.can_disable)
        text += "Can restartable: {}\n".format(self.can_restartable)
        text += "Can removable: {}\n".format(self.can_removable)
        text += "No state module: {}\n".format(self.no_state_module)
        text += "Logger enabled: {}\n".format(self.logger_enabled)
        return text


default_module_setting = ModuleSettings(
    can_disable=False, can_restartable=False,
    can_removalbe=False, no_state_module=True,
    logger_enabled=False
)


def change_default_module_setting(new_module_setting: ModuleSettings):
    """ Changes default module setting. """

    global default_module_setting
    default_module_setting = new_module_setting


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


class Module(object):
    def __init__(
            self, layer_id, module_name: str,
            module_logger_name: Optional[str] = None,
            special_state: Optional[StateHandler] = None,
            module_settings=default_module_setting
    ):
        """
        Module constructor.

        Args:
            layer_id: Layer id of the layer containing module.
            module_name: Module name. Must be unique names in same layer.
            module_logger_name: Logger name for module.
            special_state: Special state for module.
            module_settings: Module setting.

        Notes:
            Only layered objects should have a module.
            Modules should have remove, disable, restart, enable actions.
            Module settings should have specialized for module.
        """

        self._module_setting = module_settings
        self._layer_id = layer_id
        self._module_name = module_name
        self._disabled = False

        if not self.no_state_module:
            if special_state is None:
                self._state = StateHandler(
                    self._layer_id, False, *MODULE_STATES,
                    GENERAL_STATE_NOT_STARTED=MODULE_NOT_STARTED,
                    GENERAL_STATE_IS_RUNNING=MODULE_IS_RUNNNG,
                    GENERAL_STATE_IS_FINISHED=MODULE_IS_FINISHED,
                    GENERAL_STATE_IS_TERMINATED=MODULE_IS_TERMINATED,
                    GENERAL_STATE_IS_PAUSED=MODULE_IS_PASUED
                )
            else:
                self._state = special_state
        else:
            self._state = None

        if self.logger_enabled:
            if module_logger_name is None:
                module_logger_name = self._module_name
            self._logger = SubLogger(module_logger_name)
        else:
            self._logger = None

    def prepair_module(self, *args):
        """
        Prepirs module for simulation.

        # Must override method.
        """

        pass

    def enable_module(self, *args):
        """
        Enables Module.

        Return:
            True if module state changed to enabled.
            False if module state is not changed.

        # Must override method.
        """

        pass

    def pause_module(self, *args):
        """
        Pauses Module.

        Return:
            True if module state changed to paused.
            False if module state is not changed..

        # Must override method.
        """

        pass

    def resume_module(self, *args):
        """
        Resume Module.

        Return:
            True if module state changed to running.
            False if module state is not changed.

        # Must override method.
        """

        pass

    def disable_module(self, *args):
        """
        Disables Module.

        Return:
            True if module can disable.
            False if module cannot disable.

        # Must override method.
        """

        pass

    def start_module(self, *args):
        """
        Starts Module.

        Return:
            True if module can start now.
            False if module cannot start now.

        # Must override method.
        """

        pass

    def stop_module(self, *args):
        """
        Stops Module.

        Return:
            True if module state can changed to stopped.
            False if module state not changed..

        # Must override method.
        """

        pass

    def restart_module(self, *args):
        """
        Restarts Module.

        Return:
            True if module can restartable.
            False if module cannot restartable.

        # Must override method.
        """

        pass

    def is_enabled(self) -> bool:
        """ Returns if module enabled. """

        return not self._disabled

    def is_disabled(self) -> bool:
        """ Returns if module disabled. """

        return self._disabled

    def set_new_settings(self, new_settings: ModuleSettings):
        """ Sets new settings to module. """

        self._module_setting = new_settings

    def module_details(self) -> str:
        """ Returns module details in string. """

        to_return = str()
        to_return += "Module Info\n"
        to_return += "-------------------\n"
        to_return += "Module name: {}\n".format(self.module_name)
        if self.no_state_module:
            bind = "No state module"
        else:
            bind = self.state
        to_return += "Module state: {}\n".format(bind)

        to_return += self.get_settings_details()
        return to_return

    def get_settings_details(self) -> str:
        """ Return settings __str__. """

        return self._module_setting.details()

    @property
    def module_name(self) -> str:
        return self._module_name

    @property
    def layer_id(self) -> int:
        return self._layer_id

    @property
    def state(self):
        return self._state.state

    @property
    def state_object(self) -> StateHandler:
        return self._state

    @property
    def can_disable(self) -> bool:
        return self._module_setting.can_disable

    @property
    def can_restartable(self) -> bool:
        return self._module_setting.can_restartable

    @property
    def no_state_module(self) -> bool:
        return self._module_setting.no_state_module

    @property
    def logger_enabled(self) -> bool:
        return self._module_setting.logger_enabled

    @property
    def module_settings(self):
        return self._module_setting

    @property
    def logger(self) -> SubLogger:
        return self._logger

    def __int__(self) -> int:
        return self._layer_id

    def __str__(self) -> str:
        return self.module_details()
