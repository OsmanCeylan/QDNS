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

import uuid

from QDNS.tools import various_tools
# Device states.
from QDNS.tools.any_settings import AnySettings
from QDNS.tools.module import ModuleSettings

DEVICE_NOT_STARTED = "\"device not started\""
DEVICE_IS_RUNNING = "\"device is running\""
DEVICE_IS_STOPPED = "\"device is stopped\""
DEVICE_IS_FINISHED = "\"device is finished\""
DEVICE_IS_TERMINATED = "\"device is terminated\""
DEVICE_IS_PAUSED = "\"device is paused\""
DEVICE_MAY_END = "\"device may end\""

device_states = (
    DEVICE_NOT_STARTED,
    DEVICE_IS_RUNNING,
    DEVICE_IS_STOPPED,
    DEVICE_IS_FINISHED,
    DEVICE_IS_TERMINATED,
    DEVICE_MAY_END
)


# Device ID.

class DeviceIdentification(object):
    def __init__(self, id_=None, label=None, use_uuid=True, random_gen_len=16):
        """
        Device Identification.

        Args:
            id_: Device Id.
            label: Device label.
            use_uuid: Use uuid for generation id.
            random_gen_len: Random id str generation length.
        """

        if id_ is not None:
            self._id = id_
        else:
            if use_uuid:
                self._id = uuid.uuid4()
            else:
                self._id = various_tools.ran_gen(random_gen_len)

        if label is not None:
            self._label = label
        else:
            self._label = various_tools.ran_gen(random_gen_len)

    @property
    def uuid(self):
        return self._id

    @property
    def label(self):
        return self._label

    def __str__(self) -> str:
        to_return = str()
        to_return += "Device Identifier: {}, {}".format(str(self.label), str(self.uuid))
        return to_return

    def __int__(self) -> int:
        return self._id


class ChannelIdentification(DeviceIdentification):
    def __init__(self, id_=None, label=None, use_uuid=False):
        """
        Channel Identification.

        Args:
            id_: Device Id.
            label: Device label.
            use_uuid: Use uuid for generation id.
        """

        super(ChannelIdentification, self).__init__(id_=id_, label=label, use_uuid=use_uuid, random_gen_len=16)

    def __str__(self) -> str:
        to_return = str()
        to_return += "Device Identifier: {}, {}".format(str(self.label), str(self.uuid))
        return to_return


# Application Manager Setting

class ApplicationManagerSettings(ModuleSettings):

    max_application_count_ = "max_application_count"
    enable_localhost_ = "enable_localhost"
    disable_user_apps_ = "disable_user_apps"

    def __init__(
            self, max_application_count: int,
            enable_localhost: bool = True,
            disable_user_apps: bool = False
    ):
        """
        Application manager settings.

        Args:
            max_application_count: Maximum application count on this device.
            enable_localhost: Enable local host queue for applications.
            disable_user_apps: Disables new non-static applications.
        """

        kwargs = {
            self.max_application_count_: max_application_count,
            self.enable_localhost_: enable_localhost,
            self.disable_user_apps_: disable_user_apps
        }

        super(ApplicationManagerSettings, self).__init__(
            can_disable=False, can_restartable=False, can_removalbe=False,
            no_state_module=True, logger_enabled=True,
            **kwargs
        )

    @property
    def max_application_count(self) -> int:
        return self.get_setting(self.max_application_count_)

    @property
    def enabled_localhost(self) -> bool:
        return self.get_setting(self.enable_localhost_)

    @property
    def disabled_user_apps(self) -> bool:
        return self.get_setting(self.disable_user_apps_)

    def __str__(self) -> str:
        text = str()
        text += "Max application count: {}\n".format(self.max_application_count)
        text += "Localhost enabled: {}\n".format(self.enabled_localhost)
        text += "User apps disabled: {}\n".format(self.disabled_user_apps)
        return text


default_application_manager_settings = ApplicationManagerSettings(10, True, False)


def change_default_application_manager_settings(new_settings: ApplicationManagerSettings):
    """
    Changes the "default_application_manager_settings" in device_tools.
    """

    global default_application_manager_settings
    default_application_manager_settings = new_settings


# DEVICE SETTINGS


class DeviceSettings(AnySettings):

    otg_device_ = "otg_device"
    observe_capability_ = "observe_capability"
    idle_after_device_ends_ = "idle_after_device_ends"
    start_after_delay_ = "start_after_delay"

    def __init__(
            self,
            otg_device: bool,
            observe_capability: bool,
            idle_after_device_ends: bool,
            start_after_delay: float = 0
    ):
        """
        Args:
            otg_device: OTG Flag.
            observe_capability: Observe capability of device.
            idle_after_device_ends: Idle after device ends flag.
            start_after_delay: Device starts after delay.

        Notes:
            OTG device has own socket setting. Ignore other socket settings.
            Trusted devices cannot contain any user applications.
            Observe capability meaningless in trusted devices.
        """

        kwargs = {
            self.otg_device_: otg_device,
            self.observe_capability_: observe_capability,
            self.idle_after_device_ends_: idle_after_device_ends,
            self.start_after_delay_: start_after_delay
        }

        super(DeviceSettings, self).__init__(**kwargs)

    @property
    def otg_device(self) -> bool:
        return self.get_setting(self.otg_device_)

    @property
    def observe_capability(self) -> bool:
        return self.get_setting(self.observe_capability_)

    @property
    def idle_after_device_ends(self) -> bool:
        return self.get_setting(self.idle_after_device_ends_)

    @property
    def start_after_delay(self) -> float:
        return self.get_setting(self.start_after_delay_)

    def __str__(self):
        to_return = str()
        to_return += "OTG Device: {}".format(self.otg_device)
        to_return += "Observer Capability: {}".format(self.observe_capability)
        to_return += "Idle After Device Ends: {}".format(self.idle_after_device_ends)
        to_return += "Start After Delay Time: {}".format(self.start_after_delay)


default_device_settings = DeviceSettings(
    otg_device=False, observe_capability=False,
    idle_after_device_ends=True, start_after_delay=0.0
)


def change_default_device_settings(new_device_settings: DeviceSettings):
    """
    Changes default application settings.
    """

    global default_device_settings
    default_device_settings = new_device_settings
