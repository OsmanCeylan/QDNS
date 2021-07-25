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

from QDNS.tools.any_settings import AnySettings

DEFAULT_APPLICATION_NAME = "default_app"


def set_default_application_name(new_name: str):
    """
    Changes the default application name for first unlabaled application.
    """

    global DEFAULT_APPLICATION_NAME
    DEFAULT_APPLICATION_NAME = new_name


# Applicaton states.
APPLICATION_NOT_STARTED = "\"application is not started\""
APPLICATION_IS_RUNNING = "\"application is running\""
APPLICATION_IS_STOPPED = "\"application is stopped\""
APPLICATION_IS_PAUSED = "\"application is paused\""
APPLICATION_IS_FINISHED = "\"application is finished\""
APPLICATION_IS_TERMINATED = "\"applicatin is terinated\""

application_states = (
    APPLICATION_NOT_STARTED,
    APPLICATION_IS_RUNNING,
    APPLICATION_IS_STOPPED,
    APPLICATION_IS_PAUSED,
    APPLICATION_IS_FINISHED,
    APPLICATION_IS_TERMINATED
)


class ApplicationSettings(AnySettings):

    static_ = "static_"
    enabled_ = "enabled_"
    end_device_if_terminated_ = "end_device_if_terminated_"
    bond_end_with_device_ = "bond_end_with_device_"
    delayed_start_time_ = "delayed_start_time_"

    def __init__(
            self, static: bool = False, enabled: bool = True,
            end_device_if_terminated: bool = False,
            bond_end_with_device: bool = False,
            delayed_start_time: float = 0.15
    ):
        """
        Application settings constructor.

        Args:
            static: Marks app static.
            enabled: Application enabled flag.
            end_device_if_terminated: Ends device simulation if this app terminates.
            bond_end_with_device: Also ends device when application ends.
            delayed_start_time: Start application after time.
        """

        kwargs = {
            self.static_: static,
            self.enabled_: enabled,
            self.end_device_if_terminated_: end_device_if_terminated,
            self.bond_end_with_device_: bond_end_with_device,
            self.delayed_start_time_: delayed_start_time
        }

        super(ApplicationSettings, self).__init__(**kwargs)

    def change_static(self, new_flag: bool):
        """ Changes application static. """

        self.change_paramater(self.static_, new_flag)

    def enable(self):
        """ Enables the application. """

        self.change_paramater(self.enabled_, True)

    def disable(self):
        """ Disables the application. """

        self.change_paramater(self.enabled_, True)

    def change_enabled(self, new_flag: bool):
        """ Changes enabled setting. """

        self.change_paramater(self.enabled_, new_flag)

    def change_end_device_if_terminated(self, new_flag: bool):
        """ Changes end device if terminated setting. """

        self.change_paramater(self.end_device_if_terminated_, new_flag)

    @property
    def static(self) -> bool:
        return self.get_setting(self.static_)

    @property
    def enabled(self) -> bool:
        return self.get_setting(self.enabled_)

    @property
    def end_device_if_terminated(self) -> bool:
        return self.get_setting(self.end_device_if_terminated_)

    @property
    def delayed_start_time(self) -> float:
        return self.get_setting(self.delayed_start_time_)

    @property
    def bond_end_with_device(self) -> bool:
        return self.get_setting(self.bond_end_with_device_)

    def __str__(self) -> str:
        text = str()
        text += "Enabled: {}\n".format(self.enabled)
        text += "Static: {}\n".format(self.static)
        text += "End device if term.: {}\n".format(self.end_device_if_terminated)
        text += "Bond end with device: {}\n".format(self.bond_end_with_device)
        text += "Delayed start time: {}\n".format(self.delayed_start_time)
        return text


default_application_settings = ApplicationSettings(
    static=False, enabled=True,
    end_device_if_terminated=False,
    delayed_start_time=0.15
)


def change_default_application_settings(new_application_settings: ApplicationSettings):
    """ Changes the default application settings. """

    global default_application_settings
    default_application_settings = new_application_settings
