"""
## =============================================#
##  Header of QF/tools/command_tools.py         #
## =============================================#

## =============================================#
## Brief                                        #
## Contains Command Tools.                      #
## =============================================#
"""

package_expire_time = 2.0
qubit_expire_time = 2.0
respond_expire_time = 2.0


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
