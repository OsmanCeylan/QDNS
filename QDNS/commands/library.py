"""
## ==========================================#
##  Header of QF/commands/library.py         #
## ==========================================#

## ==========================================#
## Brief                                     #
## Contains Library Level.                   #
## ==========================================#
"""
import time
from copy import copy

from QDNS.device.application import Application
from QDNS.commands import api
from QDNS.tools import command_tools
from QDNS.tools import exit_codes
from QDNS.tools import communication_tools
from QDNS.rtg_apps.qkd import SENDER_SIDE, RECIEVER_SIDE


def application_wait_next_package(
        application: Application, source=None,
        timeout=None, check_old_packages=True
):
    """
    Application waits next package from hinted device.

    Args:
        application: Application.
        source: Hinted device.
        timeout: Expire time.
        check_old_packages: Checks old packages first.

    Returns:
         {"exit_code", "package"}
    """

    api.update_application_packages(application)
    if timeout is None:
        timeout = command_tools.package_expire_time

    if check_old_packages:
        selected = None
        for package in application.old_packages:
            sender = package.ip_layer.sender
            block_0 = application.block_list.get_all_communication(sender)
            block_1 = application.block_list.get_all_packages(sender)

            block = block_0 or block_1
            if not block:
                if source is None:
                    selected = package
                    break
                else:
                    if source == sender:
                        selected = package
                        break

        if selected is not None:
            to_return = copy(selected)
            application.old_packages.remove(selected)
            return {"exit_code": exit_codes.GOT_PACKAGE[0], "package": to_return}

    while 1:
        package = api.application_wait_next_package(application, timeout=timeout)
        if package is None:
            return {"exit_code": exit_codes.WAIT_PACKAGE_TIMEOUT[0], "package": None}

        sender = package.ip_layer.sender
        block_0 = application.block_list.get_all_communication(sender)
        block_1 = application.block_list.get_all_packages(sender)
        block = block_0 or block_1
        if not block:
            if source is None:
                return {"exit_code": exit_codes.GOT_PACKAGE[0], "package": package}
            else:
                if source == sender:
                    return {"exit_code": exit_codes.GOT_PACKAGE[0], "package": package}
                else:
                    application.old_packages.append(package)
        timeout -= 0.1
        if timeout <= 0.1:
            return {"exit_code": exit_codes.WAIT_PACKAGE_TIMEOUT[0], "package": None}


def application_wait_next_protocol_package(
        application: Application, source=None, timeout=None, check_old_packages=True
):
    """
    Application waits protocol package from hinted device.

    Args:
        application: Application.
        source: Hinted device.
        timeout: Expire time.
        check_old_packages: Check old unprocessed packages.

    Returns:
         {"exit_code", "package"}
    """

    api.update_application_packages(application)
    if timeout is None:
        timeout = command_tools.package_expire_time

    remaning_time = timeout
    while 1:
        package = application_wait_next_package(application, source=source, timeout=timeout, check_old_packages=check_old_packages)["package"]
        if package is not None:
            if package.ip_layer.protocol_info is not None:
                application.logger.debug("Application {} is got protocol package from {}.".format(application.label, source))
                return {"exit_code": exit_codes.GOT_PACKAGE[0], "package": package}
            else:
                application.old_packages.append(package)
            remaning_time -= float(timeout / 3)
            check_old_packages = False
            if remaning_time <= 0.2:
                break
        else:
            break
    return {"exit_code": exit_codes.WAIT_PACKAGE_TIMEOUT[0], "package": None}


def application_wait_next_qubit(application: Application, source=None, timeout=None, check_old_qubits=True):
    """
    Application waits qubit from hinted device.

    Args:
        application: Application.
        source: Hinted device.
        timeout: Expire time.
        check_old_qubits: Check old unprocessed qubits..

    Returns:
         {"exit_code", "port_index", "sender", "time", "qubit"}
    """

    api.update_application_qubits(application)
    if timeout is None:
        timeout = command_tools.qubit_expire_time

    if check_old_qubits:
        selected = None
        for qubit in application.old_qubits:
            sender = qubit[1]
            block_0 = application.block_list.get_all_communication(sender)
            block_1 = application.block_list.get_all_qubit_stream(sender)

            block = block_0 or block_1
            if not block:
                if source is None:
                    selected = qubit
                    break
                else:
                    if source == sender:
                        selected = qubit
                        break

        if selected is not None:
            to_return = copy(selected)
            application.old_qubits.remove(selected)
            application.allocated_qubits.append(to_return[3])
            return {"exit_code": exit_codes.GOT_QUBIT[0], "port_index": to_return[0], "sender": to_return[1], "time": to_return[2], "qubit": to_return[3]}

    while 1:
        qubit = api.application_wait_next_qubit(application, timeout=timeout)
        if qubit is None:
            return {"exit_code": exit_codes.WAIT_QUBIT_TIMEOUT[0], "port_index": None, "sender": None, "time": None, "qubit": None}

        sender = qubit[1]
        block_0 = application.block_list.get_all_communication(sender)
        block_1 = application.block_list.get_all_qubit_stream(sender)

        block = block_0 or block_1
        if not block:
            if source is None:
                application.allocated_qubits.append(qubit[3])
                return {"exit_code": exit_codes.GOT_QUBIT[0], "port_index": qubit[0], "sender": qubit[1], "time": qubit[2], "qubit": qubit[3]}

            else:
                if source == sender:
                    application.allocated_qubits.append(qubit[3])
                    return {"exit_code": exit_codes.GOT_QUBIT[0], "port_index": qubit[0], "sender": qubit[1], "time": qubit[2], "qubit": qubit[3]}
                else:
                    application.old_qubits.append(qubit)

        timeout -= 0.01
        if timeout <= 0.1:
            return {"exit_code": exit_codes.WAIT_QUBIT_TIMEOUT[0], "port_index": None, "sender": None, "time": None, "qubit": None}


def application_wait_next_qubits(application: Application, count, source=None, timeout=None, check_old_qubits=True):
    """
    Application waits qubits from hinted device.

    Args:
        application: Application.
        count: Qubit count.
        source: Hinted device.
        timeout: Expire time.
        check_old_qubits: Check old unprocessed qubits..

    Returns:
         {"exit_code", "qubits", "count"}
    """

    api.update_application_qubits(application)
    if timeout is None:
        timeout = command_tools.qubit_expire_time

    found_qubits = list()
    found_count = 0
    if check_old_qubits:
        selected = None
        for qubit in application.old_qubits:
            sender = qubit[1]
            block_0 = application.block_list.get_all_communication(sender)
            block_1 = application.block_list.get_all_qubit_stream(sender)

            block = block_0 or block_1
            if not block:
                if source is None:
                    selected = qubit
                    break
                else:
                    if source == sender:
                        selected = qubit
                        break

        if selected is not None:
            to_return = copy(selected)
            application.old_qubits.remove(selected)
            found_qubits.append(to_return[3])
            count -= 1
            found_count += 1
            application.allocated_qubits.append(to_return[3])

            if count <= 0:
                return {"exit_code": exit_codes.GOT_QUBIT[0], "qubits": found_qubits, "count": found_count}

    while 1:
        start_time = time.time()
        qubit = api.application_wait_next_qubit(application, timeout=timeout)
        if qubit is None:
            return {"exit_code": exit_codes.WAIT_QUBIT_TIMEOUT[0], "qubits": found_qubits, "count": found_count}

        sender = qubit[1]
        block_0 = application.block_list.get_all_communication(sender)
        block_1 = application.block_list.get_all_qubit_stream(sender)

        block = block_0 or block_1
        if not block:
            if source is None:
                found_qubits.append(qubit[3])
                count -= 1
                found_count += 1
                application.allocated_qubits.append(qubit[3])

                if count <= 0:
                    return {"exit_code": exit_codes.GOT_QUBIT[0], "qubits": found_qubits, "count": found_count}
            else:
                if source == sender:
                    found_qubits.append(qubit[3])
                    count -= 1
                    found_count += 1
                    application.allocated_qubits.append(qubit[3])

                    if count <= 0:
                        return {"exit_code": exit_codes.GOT_QUBIT[0], "qubits": found_qubits, "count": found_count}
                else:
                    application.old_qubits.append(qubit)

        timeout -= (time.time() - start_time)
        if timeout <= 0.1:
            return {"exit_code": exit_codes.WAIT_QUBIT_TIMEOUT[0], "qubits": found_qubits, "count": found_count}


def application_wait_next_Trespond(application: Application, request_id=None, request_type=None, timeout=None, check_old_responses=True):
    """
    Waits next threaded respond.

    Args:
        application: Application.
        request_id: Request ID.
        request_type: Request Type.
        timeout: Expire time.
        check_old_responses: Check flag.

    Return:
        {"exit_code", "respond_exit_code", "respond_data"}
    """

    api.update_application_requests(application)
    if check_old_responses:
        to_delete = None
        for _response in application.old_responses:
            if request_id is not None:
                if _response.generic_id == request_id:
                    to_delete = _response
                    break
            elif request_type is not None:
                if isinstance(_response, request_type):
                    to_delete = _response
                    break
            else:
                if api.calculate_time_delta(_response.creation_date) < 2:
                    to_delete = _response
                    break

        if to_delete is not None:
            to_return = copy(to_delete)
            application.old_responses.remove(to_delete)
            return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": to_return.exit_code, "respond_data": to_return.data}

    while 1:
        _response = api.application_wait_next_Trespond(application, timeout=timeout)
        if _response is None:
            return {"exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0], "respond_exit_code": None, "respond_data": None}

        else:
            if request_id is not None:
                if _response.generic_id == request_id:
                    return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}
                else:
                    application.old_responses.append(_response)

            elif request_type is not None:
                if isinstance(_response, request_type):
                    return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}
                else:
                    application.old_responses.append(_response)

            else:
                return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}

        timeout -= 0.1
        if timeout <= 0.1:
            return {"exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0], "respond_exit_code": None, "respond_data": None}


def application_wait_next_Mrespond(application: Application, request_id=None, request_type=None, timeout=None, check_old_responses=True):
    """
    Waits next multi threaded respond.

    Args:
        application: Application.
        request_id: Request ID.
        request_type: Request Type.
        timeout: Expire time.
        check_old_responses: Check flag.

    Return:
        {"exit_code", "respond_exit_code", "respond_data"}
    """

    api.update_application_requests(application)
    if check_old_responses:
        to_delete = None
        for _response in application.old_responses:
            if request_id is not None:
                if _response.generic_id == request_id:
                    to_delete = _response
                    break
            elif request_type is not None:
                if isinstance(_response, request_type):
                    to_delete = _response
                    break
            else:
                if api.calculate_time_delta(_response.creation_date) < 2:
                    to_delete = _response
                    break

        if to_delete is not None:
            to_return = copy(to_delete)
            application.old_responses.remove(to_delete)
            return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": to_return.exit_code, "respond_data": to_return.data}

    while 1:
        _response = api.application_wait_next_Mrespond(application, timeout=timeout)
        if _response is None:
            return {"exit_code": -exit_codes.WAIT_RESPOND_TIMEOUT[0], "respond_exit_code": None, "respond_data": None}

        else:
            if request_id is not None:
                if _response.generic_id == request_id:
                    return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}
                else:
                    application.old_responses.append(_response)

            elif request_type is not None:
                if isinstance(_response, request_type):
                    return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}
                else:
                    application.old_responses.append(_response)

            else:
                return {"exit_code": exit_codes.GOT_LAYER_RESPOND[0], "respond_exit_code": _response.exit_code, "respond_data": _response.data}

        timeout -= 0.1
        if timeout <= 0.1:
            return {"exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0], "respond_exit_code": None, "respond_data": None}


def application_reveal_device_information(application: Application):
    """
    Extract device information of an Application.

    Args:
        application: Application.

    Return:
        {"exit_code", "device_label", "device_unique_id"}
    """

    the_request = api.reveal_device_information_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {"exit_code": exit_codes.GATHER_DEVICE_INFORMATION_FAILED[0], "device_label": None, "device_unique_id": None}
    else:
        return {"exit_code": exit_codes.GATHER_DEVICE_INFORMATION_SUCCESS[0], "device_label": dic.label, "device_unique_id": dic.uuid}


def application_reveal_socket_information(application: Application, yield_all_string=False):
    """
    Extract socket information of the device of an Application.

    Args:
        application: Application.
        yield_all_string: Yields SocketInformation object string.

    Return:
        {
            "exit_code", "socket_state", "classic_port_count", "quantum_port_count",
            "connected_classic_port", "connected_quantum_port", "object_string"
        }
    """

    the_request = api.reveal_socket_information_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.GATHER_SOCKET_INFORMATION_FAILED[0],
            "socket_state": None,
            "classic_port_count": None,
            "quantum_port_count": None,
            "connected_classic_port": None,
            "connected_quantum_port": None,
            "object_string": None
        }
    else:
        info = dic.__str__() if yield_all_string else "No Yield!"
        return {
            "exit_code": exit_codes.GATHER_SOCKET_INFORMATION_SUCCESS[0],
            "socket_state": dic.socket_state,
            "classic_port_count": dic.classic_port_count,
            "quantum_port_count": dic.quantum_port_count,
            "connected_classic_port": dic.connected_classic_port_count,
            "connected_quantum_port": dic.connected_quantum_port_count,
            "object_string": info
        }


def application_reveal_connectivity_information(application: Application, get_uuids=False):
    """
    Extract connectivity information.

    Args:
        application: Application.
        get_uuids: Get target device uuids insetead of label.

    Return:
        {"exit_code", "classic_targets", "quantum_targets", "communication_state"}
    """

    the_request = api.reveal_connectivity_information_request(application, get_uuids=get_uuids, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.GATHER_CONNECTIVITY_INFORMATION_FAILED[0],
            "classic_targets": None,
            "quantum_targets": None,
            "communication_state": None
        }
    else:
        return {
            "exit_code": exit_codes.GATHER_CONNECTIVITY_INFORMATION_SUCCESS[0],
            "classic_targets": dic.classic_targets,
            "quantum_targets": dic.quantum_targets,
            "communication_state": dic.communication_state
        }


def application_reveal_connection_information(application: Application, get_uuids=False):
    """
    Extract connection information.

    Args:
        application: Application.
        get_uuids: Get target device uuids insetead of label.

    Return:
        {"exit_code", "classic_connections_group", "quantum_connections_group"}
    """

    the_request = api.reveal_connectivity_information_request(application, get_uuids=get_uuids, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.GATHER_CONNECTIVITY_INFORMATION_FAILED[0],
            "classic_connections_group": None,
            "quantum_connections_group": None
        }
    else:
        classic_group = list()
        quantum_group = list()

        for i in range(dic.classic_channels.__len__()):
            classic_group.append((dic.classic_channels[i], dic.classic_targets[i]))

        for i in range(dic.quantum_channels.__len__()):
            quantum_group.append((dic.quantum_channels[i], dic.quantum_targets[i]))

        return {
            "exit_code": exit_codes.GATHER_CONNECTIVITY_INFORMATION_SUCCESS[0],
            "classic_connections_group": classic_group,
            "quantum_connections_group": quantum_group
        }


def application_reveal_port_information(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Extract port information request to socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        {"exit_code", "index", "type", "active", "connected", "channel_id", "target", "latency"}
    """

    the_request = api.reveal_port_information_request(application, port_key, search_classic=search_classic, search_quantum=search_quantum)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.GATHER_PORT_INFORMATION_FAILED[0],
            "index": None,
            "type": None,
            "active": None,
            "connected": None,
            "channel_id": None,
            "target": None,
            "latency": None
        }

    else:
        return {
            "exit_code": exit_codes.GATHER_PORT_INFORMATION_SUCCESS[0],
            "index": dic.port_index,
            "type": dic.port_type,
            "active": dic.is_active(),
            "connected": dic.is_connected(),
            "channel_id": dic.channel_id,
            "target": dic.target_label,
            "latency": dic.latency
        }


def application_open_communication(application: Application):
    """
    Application opens communication on socket.

    Args:
        application: The application.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.open_communication_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.OPEN_COMMUNICATION_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.OPEN_COMMUNICATION_SUCCESS[0],
            "state_changed": dic
        }


def application_close_communication(application: Application):
    """
    Application closes communication on socket.

    Args:
        application: The application.

    Notes:
         When communication is closed, nothing can pass thought the device socket, brokes the routing.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.close_communication_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.CLOSE_COMMUNICATION_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.CLOSE_COMMUNICATION_SUCCESS[0],
            "state_changed": dic
        }


def application_activate_port(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Activates port on socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.activate_port_request(
        application, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=True
    )
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ACTIVATE_PORT_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.ACTIVATE_PORT_SUCCESS[0],
            "state_changed": dic
        }


def application_deactivate_port(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Dectivates port on socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Notes:
        Port still can be pinged. Brokes the routing.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.deactivate_port_request(
        application, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=True
    )
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.DEACTIVATE_PORT_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.DEACTIVATE_PORT_SUCCESS[0],
            "state_changed": dic
        }


def application_pause_socket(application: Application):
    """
    Pauses socket request to socket.

    Args:
        application: Requester application.

    Notes:
        Applications of host device of socket cannot use socket. Did not interrupt incoming communication.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.pause_socket_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.PAUSE_SOCKET_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.PAUSE_SOCKET_SUCCESS[0],
            "state_changed": dic
        }


def application_resume_socket(application: Application):
    """
    Resumes socket request to socket.

    Args:
        application: Requester application.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.resume_socket_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None
    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.RESUME_SOCKET_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.RESUME_SOCKET_SUCCESS[0],
            "state_changed": dic
        }


def application_end_socket(application: Application):
    """
    Makes end socket signal to socket.

    Args:
        application: Requester application.
    """

    return api.end_socket_signal(application)


def application_terminate_socket(application: Application):
    """
    Makes terminate socket signal to socket.

    Args:
        application: Requester application.
    """

    return api.terminate_socket_signal(application)


def ping_socket_connections(application: Application, timeout=None):
    """
    Ping all connected channels.

    Args:
        application: Application.
        timeout: Timeout for respond.

    Notes:
        Works on when auto-ping is OFF.

    Return:
        {"exit_code", "port_states", "ping_time"}
    """

    the_request = api.refresh_connections_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id, timeout=timeout)["respond_data"]
    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.PING_CONNECTIONS_FAILED[0],
            "port_states": None,
            "ping_time": None
        }
    else:
        return {
            "exit_code": exit_codes.PING_CONNECTIONS_SUCCESS[0],
            "port_states": dic.keys(),
            "ping_time": respond_[1]
        }


def socket_unconnect_channel(application: Application, channel_key, search_classic=True, search_quantum=True):
    """
    Unconnects channel request to socket.

    Args:
        application: Requester application.
        channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        {"exit_code", "state_changed"}
    """

    the_request = api.unconnect_channel_request(application, channel_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)["respond_data"]
    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.UNCONNECT_CHANNEL_FAILED[0],
            "state_changed": False
        }
    else:
        return {
            "exit_code": exit_codes.UNCONNECT_CHANNEL_SUCCESS[0],
            "state_changed": dic
        }


def application_put_localhost(application: Application, *values):
    """
    Puts values to application localhost.

    Args:
        application: Application.
        values: Values.
    """

    api.put_localhost(application, [application.label, *values])


def application_put_simulation_result(application: Application, *values):
    """
    Puts values to simulation result.

    Args:
        application: Application.
        values: Values.
    """

    application.user_dump_queue.put([application.host_label, application.label, *values])


def application_flush_route_data(application: Application) -> bool:
    """
    Flushes socket routing data.

    Args:
        application: Application.

    Returns:
        True if sending signal success.
    """

    return api.flush_route_data(application)


def application_allocate_qubit(application: Application, *args):
    """
    Makes allocate qubit request to simulation.

    Args:
        application: Application.
        *args: Backend specific arguments.

    Return:
         {"exit_code", "qubit"}
    """

    the_request = api.allocate_qubit(application, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_FAILED[0],
            "qubit": None
        }
    else:
        application.allocated_qubits.append(dic[0])
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_SUCCESS[0],
            "qubit": dic[0]
        }


def application_allocate_qubits(application: Application, count, *args):
    """
    Makes allocate qubits request to simulation.

    Args:
        application: Application.
        count: Count of qubit.
        *args: Backend specific arguments.

    Return:
         {"exit_code", "qubits"}
    """

    the_request = api.allocate_qubits(application, count, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_FAILED[0],
            "qubits": None
        }
    else:
        for qubit in dic:
            application.allocated_qubits.append(qubit)

        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_SUCCESS[0],
            "qubits": dic
        }


def application_allocate_qframe(application: Application, frame_size, *args):
    """
    Makes allocate qframe request to simulation.

    Args:
        application: Application.
        frame_size: Qubit count of frame.
        *args: Backend specific arguments.

    Return:
         {"exit_code", "qubits"}
    """

    the_request = api.allocate_qframe(application, frame_size, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_FAILED[0],
            "qubits": None
        }
    else:
        for qubit in dic:
            application.allocated_qubits.append(qubit)

        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_SUCCESS[0],
            "qubits": dic
        }


def application_allocate_qframes(application: Application, frame_size, count, *args):
    """
    Makes allocate qframes request to simulation.

    Args:
        application: Application.
        frame_size: Qubit count of frame.
        count: Count of qubit.
        *args: Backend specific arguments.

    Return:
         {"exit_code", "qubits"}
    """

    the_request = api.allocate_qframes(application, frame_size, count, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_FAILED[0],
            "qubits": None
        }
    else:
        for qubit in dic:
            application.allocated_qubits.append(qubit)

        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_SUCCESS[0],
            "qubits": dic
        }


def application_deallocate_qubits(application: Application, *qubits):
    """
    Deallocate qframes from app.

    Args:
        application: Application.
        qubits: Qubits for deallocation.

    Return:
         None.
    """

    # Try to remove them in app reqardless of simulation respond.
    # No time to wait response anyway.

    for qubit in qubits:
        try:
            application.allocated_qubits.remove(qubit)
        except ValueError:
            pass

    api.deallocate_qubits(application, qubits)


def application_extend_qframe(application: Application, qubit_of_frame):
    """
    Exntend frame of qubit from back by 1.

    Args:
        application: Application.
        qubit_of_frame: Qubit of frame.

    Return:
         {"exit_code", "qubit"}
    """

    the_request = api.extend_qframe(application, qubit_of_frame)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_FAILED[0],
            "qubit": None
        }
    else:
        application.allocated_qubits.append(dic)

        return {
            "exit_code": exit_codes.ALLOCATE_QUBIT_SUCCESS[0],
            "qubits": dic
        }


def application_measure_qubits(application: Application, qubits, *args):
    """
    Measures given qubits.

    Args:
        application: Application.
        qubits: Qubits to measure.
        args: Backend specific arguments.

    Return:
         {"exit_code", "results"}
    """

    the_request = api.measure_qubits(application, qubits, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)["respond_data"]

    if respond_ is None:
        return None

    dic = respond_[0]
    if dic is None:
        return {
            "exit_code": exit_codes.MEASURE_QUBIT_FAILED[0],
            "results": None
        }
    else:
        return {
            "exit_code": exit_codes.MEASURE_QUBIT_SUCCESS[0],
            "results": dic
        }


def application_reset_qubits(application: Application, qubits, *args):
    """
    Measures given qubits.

    Args:
        application: Application.
        qubits: Qubits to measure.
        args: Backend specific arguments.

    Return:
         None.
    """

    # Kernel does not respond this request.
    api.reset_qubits(application, qubits, *args)


def application_apply_serial_transformations(application: Application, list_of_gates):
    """
    Makes apply serial transformation request to simulation.

    Args:
        application: Application.
        list_of_gates: List[Gate, GateArgs, List[Qubits]]

    Return:
        None.
    """

    # Kernel should not respond this request.
    api.apply_serial_transformations_request(application, list_of_gates)


def application_apply_transformation(application: Application, qubits, gate_id, *gate_args):
    """
    Makes apply transformation request to simulation.

    Args:
        application: Application.
        qubits: Qubits to measure.
        gate_id: Gate ID.
        gate_args: Consturctor args for gate.

    Return:
        None.
    """

    # Kernel should not respond this request.
    api.apply_transformation(application, gate_id, gate_args, qubits)


def application_send_classic_data(application: Application, reciever, data, broadcast=False, routing=True):
    """
    Send classical data to target node.

    Args:
        application: Application.
        reciever: Reciever node.
        data: Data.
        broadcast: Broadcast flag.
        routing: Routing flag.

    Notes:
        Reciever must be node label or node id.
        Data must be pickable Python object.
        Broadcast flag disable target.
        Routing capability of device socket must be enabled for using this flag.

    Returns:
        {exit_code, target_count}
    """

    al = communication_tools.ApplicationLayer(application.label)
    il = communication_tools.InternetLayer(application.host_label, reciever, None, data, broadcast=broadcast, routing=routing)
    package = communication_tools.Package(al, il)

    the_request = api.send_package_request(application, reciever, package, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_["exit_code"] < 0:
        return respond_

    if respond_["respond_exit_code"] < 0:
        return {
            "exit_code": respond_["respond_exit_code"],
            "target_count": 0
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.PACKAGE_SEND_MAY_FAILED[0],
            "target_count": 0
        }
    else:
        return {
            "exit_code": exit_codes.PACKAGE_SENDED_COMFIRMED[0],
            "target_count": dic[0]
        }


def application_send_quantum(application: Application, target, *qubits, routing=True):
    """
    Send quantum bits to another node.

    Args:
        application: Application.
        target: Target node.
        qubits: Qubits to send.
        routing: Routing enable flag.

    Notes:
        Reciever must be node label or node id.
        When no_repeater flag activated repeaters along the way do not touch the qubits.

    Returns:
        {exit_code}
    """

    for qubit in qubits:
        try:
            application.allocated_qubits.remove(qubit)
        except ValueError:
            pass

    qubit_stream = list()
    if qubits.__len__() > 64:
        new_stream = []

        for i, qubit in enumerate(qubits):
            if i % 64 == 0 and i != 0:
                qubit_stream.append(copy(new_stream))
                new_stream.clear()
            new_stream.append(qubit)

        if new_stream.__len__() > 0:
            qubit_stream.append(new_stream)

    else:
        qubit_stream.append(qubits)

    respond_ = None

    for stream in qubit_stream:
        al = communication_tools.ApplicationLayer(application.label)
        il = communication_tools.InternetLayer(application.host_label, target, None, stream, routing=routing)
        qupack = communication_tools.Qupack(al, il)

        the_request = api.send_qupack_request(application, target, qupack, want_respond=True)
        respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_["exit_code"] < 0:
        return respond_

    if respond_["respond_exit_code"] < 0:
        return {
            "exit_code": respond_["respond_exit_code"]
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.QUANTUM_INFO_MAY_FAILED[0]
        }
    else:
        return {
            "exit_code": exit_codes.QUANTUM_INFO_SENDED_COMFIRMED[0],
        }


def application_generate_entangle_pairs(application: Application, count, *args):
    """
    Generates entangle pairs.

    Args:
        application: Application.
        count: Count of pairs.
        args: Backend specific arguments.

    Returns:
        {"exit_code", "pairs"}
    """

    the_request = api.generate_entangle_pairs(application, count, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_["exit_code"] < 0:
        return {
            "exit_code": respond_["exit_code"],
            "pairs": None
        }

    if respond_["respond_exit_code"] < 0:
        return {
            "exit_code": respond_["respond_exit_code"],
            "pairs": None
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.GENERATE_EPR_FAILED[0],
            "pairs": None
        }
    else:
        new_list = list()
        for i in range(count):
            new_list.append([dic[0][2 * i], dic[0][2 * i + 1]])
            application.allocated_qubits.append(dic[0][2 * i])
            application.allocated_qubits.append(dic[0][2 * i + 1])

        return {
            "exit_code": exit_codes.GENERATE_EPR_SUCCESS[0],
            "pairs": new_list
        }


def application_generate_ghz_pair(application: Application, size, *args):
    """
    Generates entangle pairs.

    Args:
        application: Application.
        size: Qubit count in ghz state.
        args: Backend specific arguments.

    Returns:
        {"exit_code", "qubits"}
    """

    if size <= 1:
        application.logger.error("Device {}; GHZ generation size should be more than 1.".format(application.host_label))

        return {
            "exit_code": exit_codes.GENERATE_GHZ_FAILED[0],
            "qubits": None
        }

    the_request = api.generate_ghz_pair(application, size, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return {
            "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
            "qubits": None
        }

    if respond_["exit_code"] < 0:
        return {
            "exit_code": respond_["exit_code"],
            "qubits": None
        }

    if respond_["respond_exit_code"] < 0:
        return {
            "exit_code": respond_["respond_exit_code"],
            "qubits": None
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.GENERATE_GHZ_FAILED[0],
            "qubits": None
        }
    else:
        for qubit in dic[0]:
            application.allocated_qubits.append(qubit)

        return {
            "exit_code": exit_codes.GENERATE_GHZ_SUCCESS[0],
            "qubits": dic[0]
        }


def application_send_entangle_pairs(application: Application, count, target, routing=True):
    """
    Sends entangle pairs to node.

    Args:
        application: Application.
        count: Count of pairs.
        target: Target node.
        routing: Routing enable flag.

    Returns:
        {exit_code, my_pairs}
    """

    result = application_generate_entangle_pairs(application, count)
    if result["pairs"] is None:
        return {
            "exit_code": exit_codes.SEND_EPR_FAILED[0],
            "my_pairs": []
        }

    pairs = result["pairs"]
    my_pairs = list()
    his_pairs = list()

    for pair in pairs:
        my_pairs.append(pair[0])
        his_pairs.append(pair[1])

    result = application_send_quantum(application, target, *his_pairs, routing=routing)
    if result["exit_code"] < 0:
        return {
            "exit_code": exit_codes.SEND_EPR_FAILED[0],
            "my_pairs": my_pairs
        }

    else:
        return {
            "exit_code": exit_codes.SEND_EPR_SUCCESS[0],
            "my_pairs": my_pairs
        }


def application_broadcast_ghz_state(application: Application):
    """
    Broadcasts ghz state to quantum connected nodes.

    Returns:
        {exit_code, my_qubit}
    """

    connections = application_reveal_connection_information(application, get_uuids=False)['quantum_connections_group']
    if connections.__len__() <= 0:
        application.logger.error(
            "Device {} have {} quatum connections. Boardcasting ghz stops".format(
                application.host_uuid, connections.__len__()
            )
        )

        return {
            "exit_code": exit_codes.SEND_GHZ_FAILED[0],
            "my_qubit": None
        }

    result = application_generate_ghz_pair(application, connections.__len__() + 1)
    if result["qubits"] is None:
        return {
            "exit_code": exit_codes.SEND_GHZ_FAILED[0],
            "my_qubit": []
        }

    qubits = result["qubits"]
    for i in range(connections.__len__()):
        application_send_quantum(application, connections[i][1], qubits[i + 1], routing=False)

    return {
        "exit_code": exit_codes.SEND_GHZ_SUCCESS[0],
        "my_qubit": qubits[0]
    }


def application_run_qkd_protocol(application: Application, target_device, key_lenght, method):
    """
    Makes qkd protocol request to application.

    Args:
        application: Application.
        target_device: Identitier of device.
        key_lenght: Key length.
        method: QKD method.

    Returns:
        {exit_code, key, lenght}
    """

    the_request = api.run_qkd_protocol_request(application, target_device, key_lenght, method, SENDER_SIDE)
    if the_request is None:
        return {
            "exit_code": exit_codes.QKD_LAYER_IS_NOT_AVAIBLE[0],
            "key": None,
            "length": 0
        }

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return {
            "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
            "key": None,
            "length": 0
        }

    if respond_["exit_code"] < 0:
        return {
            "exit_code": respond_["exit_code"],
            "key": None,
            "length": 0
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
            "key": None,
            "length": 0
        }

    else:
        try:
            if dic[0] is None:
                return {
                    "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                    "key": None,
                    "length": 0
                }
        except AttributeError:
            return {
                "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                "key": None,
                "length": 0
            }

        return {
            "exit_code": exit_codes.QKD_PROTOCOL_SUCCESS[0],
            "key": dic[0],
            "length": dic[0].__len__()
        }


def application_wait_qkd(application: Application, source=None):
    """
    Apllication waits QKD from source.

    Args:
        application: Application.
        source: Initiater device identifier.

    Returns:
        {exit_code, key, lenght}
    """

    the_request = api.run_qkd_protocol_request(application, source, None, None, RECIEVER_SIDE)
    if the_request is None:
        return {
            "exit_code": exit_codes.QKD_LAYER_IS_NOT_AVAIBLE[0],
            "key": None,
            "length": 0
        }

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)
    if respond_["exit_code"] < 0:
        return {
            "exit_code": respond_["exit_code"],
            "key": None,
            "length": 0
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
            "key": None,
            "length": 0
        }

    else:
        try:
            if dic[0] is None:
                return {
                    "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                    "key": None,
                    "length": 0
                }
        except AttributeError:
            return {
                "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                "key": None,
                "length": 0
            }

        return {
            "exit_code": exit_codes.QKD_PROTOCOL_SUCCESS[0],
            "key": dic[0],
            "length": dic[0].__len__()
        }


def application_current_qkd_key(application: Application):
    """
    Apllication requests for current key from QKD.

    Args:
        application: Application.

    Returns:
        {exit_code, key, lenght}
    """

    the_request = api.current_qkd_key_request(application)
    if the_request is None:
        return {
            "exit_code": exit_codes.QKD_LAYER_IS_NOT_AVAIBLE[0],
            "key": None,
            "length": 0
        }

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)
    if respond_["exit_code"] < 0:
        return {
            "exit_code": respond_["exit_code"],
            "key": None,
            "length": 0
        }

    dic = respond_["respond_data"]
    if dic is None:
        return {
            "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
            "key": None,
            "length": 0
        }

    else:
        try:
            if dic[0] is None:
                return {
                    "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                    "key": None,
                    "length": 0
                }
        except AttributeError:
            return {
                "exit_code": exit_codes.WAIT_RESPOND_TIMEOUT[0],
                "key": None,
                "length": 0
            }

        return {
            "exit_code": exit_codes.QKD_PROTOCOL_SUCCESS[0],
            "key": dic[0],
            "length": dic[0].__len__()
        }


def application_flush_qkd_key(application: Application):
    """
    Apllication requests to remove key in QKD Layer.

    Args:
        application: Application.

    Returns:
        None.
    """

    api.flush_qkd_key_request(application)
