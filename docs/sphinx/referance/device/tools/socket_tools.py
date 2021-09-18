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

# These flags are used application listener.
RELEASE_PACKAGE = "RELEASE PACKAGE"
DROP_PACKAGE = "DROP PACKAGE"

# Socket states.
SOCKET_IS_DOWN = "\"socket down\""
SOCKET_IS_UP = "\"socket up\""
SOCKET_PAUSED = "\"socket paused\""
SOCKET_IS_OVER = "\"socket is over\""

socket_states = (
    SOCKET_IS_DOWN,
    SOCKET_IS_UP,
    SOCKET_PAUSED,
    SOCKET_IS_OVER,
)

default_ping_time = 2.5

max_avaible_classic_connection = 99
max_avaible_quantum_connection = 99


class SocketSettings(AnySettings):
    max_cc_count_ = "max_cc_count"
    max_qc_count_ = "max_qc_count"
    auto_ping_ = "auto_ping"
    ping_time_ = "ping_time"
    clear_route_cache_ = "clear_route_cache"
    remove_future_packages_ = "remove_future_packages"
    enable_routing_ = "enable_routing"
    enable_qkd_ = "enable_qkd"

    def __init__(
            self, max_cc_count: int, max_qc_count: int, auto_ping: bool = True,
            ping_time: float = default_ping_time, clear_route_cache: bool = False,
            remove_future_packages: bool = True, enable_routing: bool = True,
            enable_qkd: bool = True
    ):
        """
        Socket settings for a device adapter.

        Args:
            max_cc_count: Maximum classic port count.
            max_qc_count: Maximum quantum port count.
            auto_ping: Auto ping targets.
            ping_time: Ping timing.
            remove_future_packages: Drop future dated packages.
            enable_routing: Enable routing module.
            enable_qkd: Enable qkd module.
        """

        kwargs = {
            self.max_cc_count_: max_cc_count,
            self.max_qc_count_: max_qc_count,
            self.auto_ping_: auto_ping,
            self.ping_time_: ping_time,
            self.clear_route_cache_: clear_route_cache,
            self.remove_future_packages_: remove_future_packages,
            self.enable_routing_: enable_routing,
            self.enable_qkd_: enable_qkd
        }

        super(SocketSettings, self).__init__(**kwargs)

    def is_routing_enabled(self) -> bool:
        """ Returns if routing enabled. """

        return self.get_setting(self.enable_routing_)

    def is_qkd_enabled(self) -> bool:
        """ Returns if routing enabled. """

        return self.get_setting(self.enable_qkd_)

    @property
    def max_cc_count(self) -> int:
        return self.get_setting(self.max_cc_count_)

    @property
    def max_qc_count(self) -> int:
        return self.get_setting(self.max_qc_count_)

    @property
    def auto_ping(self) -> bool:
        return self.get_setting(self.auto_ping_)

    @property
    def ping_time(self) -> float:
        return self.get_setting(self.ping_time_)

    @property
    def remove_future_packages(self) -> bool:
        return self.get_setting(self.remove_future_packages_)

    @property
    def clear_route_cache(self) -> bool:
        return self.get_setting(self.clear_route_cache_)

    def __str__(self):
        to_return = str()
        to_return += "Auto Ping: {}\n".format(self.auto_ping)
        to_return += "Ping Time: {}\n".format(self.ping_time)
        to_return += "Enable Routing: {}".format(self.is_routing_enabled())
        return to_return


default_socket_settings = SocketSettings(
    8, 8, auto_ping=True, ping_time=default_ping_time,
    clear_route_cache=False, remove_future_packages=True,
    enable_routing=True, enable_qkd=True
)


def change_default_socket_settings(new_socket_settings: SocketSettings):
    """
    Changes the deafult socket settings.
    """

    global default_socket_settings
    default_socket_settings = new_socket_settings


def change_default_ping_time(new_time: float):
    """
    Changes the drafult ping time.
    """

    global default_ping_time
    default_ping_time = new_time
