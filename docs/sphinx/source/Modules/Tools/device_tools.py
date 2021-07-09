import uuid
from typing import Optional

from QDNS.tools import various_tools
from QDNS.tools import architecture_tools

"""
##==============================================  DEVICE STATES  =====================================================##
"""

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

"""
##==============================================  DEVICE INFO  =====================================================##
"""


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

    def __str__(self):
        to_return = str()
        to_return += "{}, {}".format(str(self.label), str(self.uuid))
        return to_return

    def __int__(self):
        return self._id


class ChannelIdentification(DeviceIdentification):
    def __init__(self, id_=None, label=None, use_uuid=False):
        super(ChannelIdentification, self).__init__(id_=id_, label=label, use_uuid=use_uuid, random_gen_len=16)


"""
##==============================================  DEVICE MODULE  =====================================================##
"""


class DeviceModule(architecture_tools.Module):
    def __init__(
            self, module_name: str, can_disable=False,
            can_removable=False, can_restartable=True, can_pausable=True,
            no_state_module: bool = True,
            special_state: Optional[architecture_tools.StateHandler] = None,
            module_settings: Optional[architecture_tools.ModuleSettings] = None
    ):
        """
        Device module derived from Module.
        See details from QDNS.tools.architecture_tools.Module()...
        """

        super(DeviceModule, self).__init__(
            architecture_tools.ID_DEVICE[1], module_name, self, can_disable=can_disable,
            can_removable=can_removable, can_restartable=can_restartable, no_state_module=no_state_module,
            can_pausable=can_pausable, special_state=special_state, module_settings=module_settings
        )


"""
##============================================  APP_MAN SETTINGS  ====================================================##
"""


class ApplicationManagerSettings(architecture_tools.AnySettings):
    def __init__(self, max_application_count: int, enable_localhost: bool = True, disable_user_apps: bool = False):
        """
        Application manager settings.

        Args:
            max_application_count: Maximum application count on this device.
            enable_localhost: Enable local host queue for applications.
            disable_user_apps: Disables new non-static applications.
        """

        self._max_application_count = max_application_count
        self._enable_localhost = enable_localhost
        self._disable_user_apps = disable_user_apps

        super(ApplicationManagerSettings, self).__init__(
            max_application_count=self._max_application_count,
            enable_local_host=self._enable_localhost,
            disable_user_apps=self._disable_user_apps
        )

    @property
    def max_application_count(self) -> int:
        return self._max_application_count

    @property
    def enable_localhost(self) -> bool:
        return self._enable_localhost

    @property
    def disable_user_apps(self) -> bool:
        return self._disable_user_apps


default_application_manager_settings = ApplicationManagerSettings(10, True, False)


def change_default_application_manager_settings(new_settings: ApplicationManagerSettings):
    """
    Changes the "default_application_manager_settings" in device_tools.
    """

    global default_application_manager_settings
    default_application_manager_settings = new_settings


"""
##==============================================  DEVICE SETTINGS  ===================================================##
"""


class DeviceSettings(architecture_tools.AnySettings):
    def __init__(
            self, otg_device: bool, observe_capability: bool,
            idle_after_device_ends: bool, start_after_delay: float = 0
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

        self._otg_device = otg_device
        self._observe_capability = observe_capability
        self._idle_after_device_ends = idle_after_device_ends
        self._start_after_delay = start_after_delay

        super(DeviceSettings, self).__init__(
            otg_device=self._otg_device,
            observe_capability=self._observe_capability,
            idle_after_device_ends=self._idle_after_device_ends,
            start_after_delay=self._start_after_delay
        )

    @property
    def otg_device(self) -> bool:
        return self._otg_device

    @property
    def observe_capability(self) -> bool:
        return self._observe_capability

    @property
    def idle_after_device_ends(self) -> bool:
        return self._idle_after_device_ends

    @property
    def start_after_delay(self) -> float:
        return self._start_after_delay

    def __str__(self):
        to_return = str()
        to_return += "OTG Device: {}".format(self._otg_device)
        to_return += "Observer Capability: {}".format(self._observe_capability)
        to_return += "Idle After Device Ends: {}".format(self._idle_after_device_ends)
        to_return += "Start After Delay Time: {}".format(self._start_after_delay)


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
