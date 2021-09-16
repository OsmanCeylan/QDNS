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

import time
from copy import copy

from QDNS.commands import api
from QDNS.commands import tools as command_tools
from QDNS.device.application import Application
from QDNS.rtg_apps.qkd import SENDER_SIDE, RECIEVER_SIDE
from QDNS.tools import communication


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
         Package or None
    """

    # Update old packages.
    api.update_application_packages(application)
    if timeout is None:
        timeout = command_tools.package_expire_time

    # Look package in old.
    if check_old_packages:
        selected = None
        for package in application.old_packages:
            sender = package.ip_layer.sender

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
            return to_return

    # Wait package.
    while 1:
        package = api.application_wait_next_package(application, timeout=timeout)
        if package is None:
            return None

        sender = package.ip_layer.sender
        if source is None:
            return package
        else:
            if source == sender:
                return package
            else:
                application.old_packages.append(package)

        timeout -= 0.1
        if timeout <= 0.1:
            return None


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
         Package or None.
    """

    # Update old packages.
    api.update_application_packages(application)
    if timeout is None:
        timeout = command_tools.package_expire_time

    # Wait package.
    remaning_time = timeout
    while 1:
        package = application_wait_next_package(application, source=source, timeout=timeout, check_old_packages=check_old_packages)["package"]
        if package is not None:
            if package.ip_layer.protocol_info is not None:
                application.logger.debug("Application {} is got protocol package from {}.".format(application.label, source))
                return package
            else:
                application.old_packages.append(package)

            remaning_time -= float(timeout / 3)
            check_old_packages = False
            if remaning_time <= 0.2:
                break
        else:
            break
    return None


def application_wait_next_qubit(application: Application, source=None, timeout=None, check_old_qubits=True):
    """
    Application waits qubit from hinted device.

    Args:
        application: Application.
        source: Hinted device.
        timeout: Expire time.
        check_old_qubits: Check old unprocessed qubits..

    Returns:
         ("port_index", "sender", "time", "qubit") or None.
    """

    # Update old qubits.
    api.update_application_qubits(application)
    if timeout is None:
        timeout = command_tools.qubit_expire_time

    # Look in old qubits.
    if check_old_qubits:
        selected = None
        for qubit in application.old_qubits:
            sender = qubit[1]
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
            return to_return[0], to_return[1], to_return[2], to_return[3]

    # Wait loop.
    while 1:
        qubit = api.application_wait_next_qubit(application, timeout=timeout)
        if qubit is None:
            return None

        sender = qubit[1]
        block_0 = application.block_list.get_all_communication(sender)
        block_1 = application.block_list.get_all_qubit_stream(sender)

        block = block_0 or block_1
        if not block:
            if source is None:
                application.allocated_qubits.append(qubit[3])
                return qubit[0], qubit[1], qubit[2], qubit[3]

            else:
                if source == sender:
                    application.allocated_qubits.append(qubit[3])
                    return qubit[0], qubit[1], qubit[2], qubit[3]
                else:
                    application.old_qubits.append(qubit)

        timeout -= 0.01
        if timeout <= 0.1:
            return None


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
         (qubits, count) or None
    """

    # Update old qubits.
    api.update_application_qubits(application)
    if timeout is None:
        timeout = command_tools.qubit_expire_time

    # Look in old qubits.
    found_qubits = list()
    found_count = 0
    if check_old_qubits:
        selected = None
        for qubit in application.old_qubits:
            sender = qubit[1]
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
                return found_qubits, found_count

    # Wait loop.
    while 1:
        start_time = time.time()
        qubit = api.application_wait_next_qubit(application, timeout=timeout)
        if qubit is None:
            return found_qubits, found_count

        sender = qubit[1]
        if source is None:
            found_qubits.append(qubit[3])
            count -= 1
            found_count += 1
            application.allocated_qubits.append(qubit[3])

            if count <= 0:
                return found_qubits, found_count
        else:
            if source == sender:
                found_qubits.append(qubit[3])
                count -= 1
                found_count += 1
                application.allocated_qubits.append(qubit[3])

                if count <= 0:
                    return found_qubits, found_count
            else:
                application.old_qubits.append(qubit)

        timeout -= (time.time() - start_time)
        if timeout <= 0.1:
            return found_qubits, found_count


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
        (exit_code, data) or None
    """

    # Update application old requests.
    api.update_application_requests(application)
    if timeout is None:
        timeout = command_tools.respond_expire_time

    # Look respond in old.
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
            return to_return.exit_code, to_return.data

    # Wait loop
    while 1:
        _response = api.application_wait_next_Trespond(application, timeout=timeout)
        if _response is None:
            return None

        else:
            if request_id is not None:
                if _response.generic_id == request_id:
                    return _response.exit_code, _response.data
                else:
                    application.old_responses.append(_response)

            elif request_type is not None:
                if isinstance(_response, request_type):
                    return _response.exit_code, _response.data
                else:
                    application.old_responses.append(_response)

            else:
                return _response.exit_code, _response.data

        timeout -= 0.1
        if timeout <= 0.1:
            return None


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
        (exit_code, data) or None
    """

    # Update old requests.
    api.update_application_requests(application)
    if timeout is None:
        timeout = command_tools.respond_expire_time

    # Look in old requests.
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
            return to_return.exit_code, to_return.data

    while 1:
        _response = api.application_wait_next_Mrespond(application, timeout=timeout)
        if _response is None:
            return None

        else:
            if request_id is not None:
                if _response.generic_id == request_id:
                    return _response.exit_code, _response.data
                else:
                    application.old_responses.append(_response)

            elif request_type is not None:
                if isinstance(_response, request_type):
                    return _response.exit_code, _response.data
                else:
                    application.old_responses.append(_response)

            else:
                return _response.exit_code, _response.data

        timeout -= 0.1
        if timeout <= 0.1:
            return None


def application_reveal_device_information(application: Application):
    """
    Extract device information of an Application.

    Args:
        application: Application.

    Return:
        DeviceIdentifier or None
    """

    the_request = api.reveal_device_information_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_reveal_socket_information(application: Application):
    """
    Extract socket information of the device of an Application.

    Args:
        application: Application.

    Return:
        SocketInformation or None.
    """

    the_request = api.reveal_socket_information_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_reveal_connectivity_information(application: Application, get_uuids=False):
    """
    Extract connectivity information.

    Args:
        application: Application.
        get_uuids: Get target device uuids insetead of label.

    Return:
        ConnectivityInformation or None
    """

    the_request = api.reveal_connectivity_information_request(application, get_uuids=get_uuids, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_reveal_port_information(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Extract port information request to socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        PortInformation or None
    """

    the_request = api.reveal_port_information_request(application, port_key, search_classic=search_classic, search_quantum=search_quantum)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_open_communication(application: Application):
    """
    Application opens communication on socket.

    Args:
        application: The application.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.open_communication_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_close_communication(application: Application):
    """
    Application closes communication on socket.

    Args:
        application: The application.

    Notes:
         When communication is closed, nothing can pass thought the device socket, brokes the routing.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.close_communication_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_activate_port(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Activates port on socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.activate_port_request(
        application, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=True
    )
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_deactivate_port(application: Application, port_key, search_classic=True, search_quantum=True):
    """
    Dectivates port on socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Notes:
        Port still can be pinged but brokes the routing.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.deactivate_port_request(
        application, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=True
    )
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_pause_socket(application: Application):
    """
    Pauses socket request to socket.

    Args:
        application: Requester application.

    Notes:
        Applications of host device of socket cannot use socket. Did not interrupt incoming communication.

    Return:
       state_changed[Boolean] or None
    """

    the_request = api.pause_socket_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_resume_socket(application: Application):
    """
    Resumes socket request to socket.

    Args:
        application: Requester application.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.resume_socket_request(application, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


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


def ping_socket_connections(application: Application):
    """
    Ping all connected channels.

    Args:
        application: Application.

    Notes:
        Works on when auto-ping is OFF.
        Do not return anything.
    """

    api.refresh_connections_request(application, want_respond=False)


def socket_unconnect_channel(application: Application, channel_key, search_classic=True, search_quantum=True):
    """
    Unconnects channel request to socket.

    Args:
        application: Requester application.
        channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.

    Return:
        state_changed[Boolean] or None
    """

    the_request = api.unconnect_channel_request(
        application, channel_key, search_classic=search_classic,
        search_quantum=search_quantum, want_respond=True
    )
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


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
         Qubit or None.
    """

    the_request = api.allocate_qubit(application, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    application.allocated_qubits.append(respond_[1][0])
    return respond_[1][0]


def application_allocate_qubits(application: Application, count, *args):
    """
    Makes allocate qubits request to simulation.

    Args:
        application: Application.
        count: Count of qubit.
        *args: Backend specific arguments.

    Return:
         Qubits or None.
    """

    the_request = api.allocate_qubits(application, count, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    for qubit in respond_[1][0]:
        application.allocated_qubits.append(qubit)
    return respond_[1][0]


def application_allocate_qframe(application: Application, frame_size, *args):
    """
    Makes allocate qframe request to simulation.

    Args:
        application: Application.
        frame_size: Qubit count of frame.
        *args: Backend specific arguments.

    Return:
         Qubits or None.
    """

    the_request = api.allocate_qframe(application, frame_size, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    for qubit in respond_[1][0]:
        application.allocated_qubits.append(qubit)
    return respond_[1][0]


def application_allocate_qframes(application: Application, frame_size, count, *args):
    """
    Makes allocate qframes request to simulation.

    Args:
        application: Application.
        frame_size: Qubit count of frame.
        count: Count of qubit.
        *args: Backend specific arguments.

    Return:
         List[List[Qubits]] or None.
    """

    the_request = api.allocate_qframes(application, frame_size, count, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    for frame in respond_[1][0]:
        application.allocated_qubits.extend(frame)
    return respond_[1][0]


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


def application_measure_qubits(application: Application, qubits, *args):
    """
    Measures given qubits.

    Args:
        application: Application.
        qubits: Qubits to measure.
        args: Backend specific arguments.

    Return:
         Results or None.
    """

    the_request = api.measure_qubits(application, qubits, *args)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


def application_reset_qubits(application: Application, qubits):
    """
    Measures given qubits.

    Args:
        application: Application.
        qubits: Qubits to measure.

    Return:
         None.
    """

    # Kernel does not respond this request.
    api.reset_qubits(application, qubits)


def application_apply_serial_transformations(application: Application, list_of_gates, *args):
    """
    Makes apply serial transformation request to simulation.

    Args:
        application: Application.
        list_of_gates: List[Gate, GateArgs, List[Qubits]]
        args: Backend specific arguments.

    Return:
        None.
    """

    # Kernel should not respond this request.
    api.apply_serial_transformations_request(application, list_of_gates, args)


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
        target_count[int] or None.
    """

    al = communication.ApplicationLayer(application.label)
    il = communication.InternetLayer(application.host_label, reciever, None, data, broadcast=broadcast, routing=routing)
    package = communication.Package(al, il)

    the_request = api.send_package_request(application, reciever, package, want_respond=True)
    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0]


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

    Returns:
        exit_code[int]
    """

    if qubits.__len__() <= 0:
        return None

    for qubit in qubits:
        try:
            application.allocated_qubits.remove(qubit)
        except ValueError:
            pass

    qubit_stream = list()
    if qubits.__len__() > command_tools.qstream_capacity:
        new_stream = []

        for i, qubit in enumerate(qubits):
            if i % command_tools.qstream_capacity == 0 and i != 0:
                qubit_stream.append(copy(new_stream))
                new_stream.clear()
            new_stream.append(qubit)

        if new_stream.__len__() > 0:
            qubit_stream.append(new_stream)

    else:
        qubit_stream.append(qubits)

    respond_ = None

    for stream in qubit_stream:
        al = communication.ApplicationLayer(application.label)
        il = communication.InternetLayer(application.host_label, target, None, stream, routing=routing)
        qupack = communication.Qupack(al, il)

        the_request = api.send_qupack_request(application, target, qupack, want_respond=True)
        respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    return respond_[0]


def application_generate_entangle_pairs(application: Application, count):
    """
    Generates entangle pairs.

    Args:
        application: Application.
        count: Count of pairs.

    Returns:
        List[Pair] or None.
    """

    the_request = api.generate_entangle_pairs(application, count)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    for frame in respond_[1][0]:
        application.allocated_qubits.extend(frame)

    return respond_[1][0]


def application_generate_ghz_pair(application: Application, size: int, count: int):
    """
    Generates entangle pairs.

    Args:
        application: Application.
        size: Qubit count in ghz state.
        count: Count of pairs.

    Returns:
        List[Pair] or None.
    """

    if size <= 1:
        application.logger.error("GHZ generation size should be more than 1.")
        return None

    the_request = api.generate_ghz_pair(application, size, count)
    respond_ = application_wait_next_Mrespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    for frame in respond_[1][0]:
        application.allocated_qubits.extend(frame)

    return respond_[1][0]


def application_send_entangle_pairs(application: Application, count: int, target, routing=True):
    """
    Sends entangle pairs to node.

    Args:
        application: Application.
        count: Count of pairs.
        target: Target node.
        routing: Routing enable flag.

    Returns:
        List[Qubits] or None.
    """

    result = application_generate_entangle_pairs(application, count)

    if result is None:
        return None

    my_pairs = list()
    his_pairs = list()

    for pair in result:
        my_pairs.append(pair[0])
        his_pairs.append(pair[1])

    respond_ = application_send_quantum(application, target, *his_pairs, routing=routing)

    if respond_ is None:
        return None

    if respond_ < 0:
        return None

    return my_pairs


def application_broadcast_ghz_state(application: Application):
    """
    Broadcasts ghz state to quantum connected nodes.

    Returns:
        (GHZ Size[int], Qubit) or None.
    """

    connections = application_reveal_connectivity_information(application, get_uuids=False)
    if connections is None:
        return None

    targets = connections.quantum_targets

    if targets.__len__() <= 0:
        application.logger.error("Device has no quantum connections. Boardcasting ghz stops")
        return None

    result = application_generate_ghz_pair(application, targets.__len__() + 1, 1)
    if result is None:
        return None

    qubits = result[0]
    for i in range(targets.__len__()):
        application_send_quantum(application, targets[i], qubits[i + 1], routing=False)

    return targets.__len__(), qubits[0]


def application_run_qkd_protocol(application: Application, target_device, key_lenght, method):
    """
    Makes qkd protocol request to application.

    Args:
        application: Application.
        target_device: Identitier of device.
        key_lenght: Key length.
        method: QKD method.

    Returns:
        (key[List[int]], key_lenght[int]) or None.
    """

    the_request = api.run_qkd_protocol_request(application, target_device, key_lenght, method, SENDER_SIDE)

    if the_request is None:
        return None

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)

    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0], respond_[1][0].__len__()


def application_wait_qkd(application: Application, source=None):
    """
    Apllication waits QKD from source.

    Args:
        application: Application.
        source: Initiater device identifier.

    Returns:
        (key[List[int]], key_lenght[int]) or None.
    """

    the_request = api.run_qkd_protocol_request(application, source, None, None, RECIEVER_SIDE)

    if the_request is None:
        return None

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)
    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    return respond_[1][0], respond_[1][0].__len__()


def application_current_qkd_key(application: Application):
    """
    Apllication requests for current key from QKD.

    Args:
        application: Application.

    Returns:
        (key[List[int]], key_lenght[int]) or None.
    """

    the_request = api.current_qkd_key_request(application)
    if the_request is None:
        return None

    respond_ = application_wait_next_Trespond(application, request_id=the_request.generic_id)
    if respond_ is None:
        return None

    if respond_[0] < 0:
        return None

    if respond_[1][0] is None:
        return [], 0

    return respond_[1][0], respond_[1][0].__len__()


def application_flush_qkd_key(application: Application):
    """
    Apllication requests to remove key in QKD Layer.

    Args:
        application: Application.

    Returns:
        None.
    """

    api.flush_qkd_key_request(application)
