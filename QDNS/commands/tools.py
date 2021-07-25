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

package_expire_time = 2.0
qubit_expire_time = 2.0
respond_expire_time = 2.0
qstream_capacity = 64


def set_package_expire_time(new: float) -> bool:
    """
    Sets default expire time in api calls.

    Notes:
        New value in float. (Must be >= 0.1)
        Returns True if set successful.

        If this function called in simulation run time:
            The changes on expire time is same for threads derived from same device,
            but changes does not apply in other threads that derived from devices.

        We advise change this value(if needs) before simulation.
    """

    if new <= 0:
        return False

    elif new >= 0.1:
        global package_expire_time
        package_expire_time = new
        return True

    else:
        return False


def set_qubit_expire_time(new: float) -> bool:
    """
    Sets default expire time in api calls.

    Notes:
        New value in float. (Must be >= 0.1)
        Returns True if set successful.

        If this function called in simulation run time:
            The changes on expire time is same for threads derived from same device,
            but changes does not apply in other threads that derived from devices.

        We advise change this value(if needs) before simulation.
    """

    if new <= 0:
        return False

    elif new >= 0.1:
        global qubit_expire_time
        qubit_expire_time = new
        return True

    else:
        return False


def set_respond_expire_time(new: float) -> bool:
    """
    Sets default expire time in api calls.

    Notes:
        New value in float. (Must be >= 0.1)
        Returns True if set successful.

        If this function called in simulation run time:
            The changes on expire time is same for threads derived from same device,
            but changes does not apply in other threads that derived from devices.

        We advise change this value(if needs) before simulation.
    """

    if new <= 0:
        return False

    elif new >= 0.1:
        global respond_expire_time
        respond_expire_time = new
        return True

    else:
        return False
