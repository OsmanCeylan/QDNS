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
from typing import Union
from datetime import datetime
from queue import Empty

from QDNS.architecture import request, signal
from QDNS.device.application import Application
from QDNS.tools import command_tools


def calculate_time_delta(datetime_old, datetime_new=None):
    """
    Calculates timedelta between two dates.

    Args:
        datetime_old: Old time in datatime format.
        datetime_new: New time in datatime format. Default is now().

    Returns:
        Date differance in seconds.
    """

    if datetime_new is None:
        datetime_new = datetime.now()
    return (datetime_new - datetime_old).seconds


def get_date():
    """ Returns the date. """

    return datetime.now()


def get_time():
    """ Returns the time. """

    return time.time()


def application_wait_next_package(application: Application, timeout=None):
    """
    Wait application next incoming package.
    This could be a package given by device or socket.

    Args:
        application: Application.
        timeout: Expire time in float.

    Returns:
         Package or None.
    """

    if timeout is None:
        timeout = command_tools.package_expire_time

    try:
        package = application.income_package_queue.get(timeout=timeout)
    except Empty:
        return None
    else:
        return package


def application_wait_next_qubit(application: Application, timeout=None):
    """
    Application waits next qubit for itself.

    Args:
        application: Application.
        timeout: Expire time.

    Returns:
         Qubit or None.
    """

    if timeout is None:
        timeout = command_tools.qubit_expire_time

    try:
        qubit = application.income_qubit_queue.get(timeout=timeout)
    except Empty:
        return None
    else:
        return qubit


def application_wait_next_Trespond(application: Application, timeout=None):
    """
    Application waits next (threaded) respond.

    Args:
        application: Application.
        timeout: Expire time.

    Returns:
         Respond or None.
    """

    if timeout is None:
        timeout = command_tools.respond_expire_time

    try:
        respond_ = application.threaded_respond_queue.get(timeout=timeout)
    except Empty:
        return None
    else:
        return respond_


def application_wait_next_Mrespond(application: Application, timeout=None):
    """
    Application waits next (multiprocessed) respond.

    Args:
        application: Application.
        timeout: Expire time.

    Returns:
         Respond or None.
    """

    if timeout is None:
        timeout = command_tools.respond_expire_time

    try:
        respond_ = application.respond_queue.get(timeout=timeout)
    except Empty:
        return None
    else:
        return respond_


def update_application_requests(application: Application, timeout=None) -> bool:
    """
    Updates application request.
    Deletes old and unprocessed requests.
    The libs or protocols should update the relative container queue before starts.

    Args:
        application: Application.
        timeout: Expire check time.

    Returns:
        True if an deletion occurred.
    """

    if timeout is None:
        timeout = command_tools.respond_expire_time

    for_return = False
    delete_list = list()
    for req in application.active_requests:
        d = calculate_time_delta(req.creation_date)
        if d > timeout + int(timeout / 5):
            delete_list.append(req)

    if delete_list.__len__() > 0:
        for_return = True

    for req in delete_list:
        application.active_requests.remove(req)

    return for_return


def update_application_packages(application: Application, timeout=None) -> bool:
    """
    Updates application old packages.
    Deletes old and unprocessed packages.
    The libs or protocols should update the relative container queue before starts.

    Args:
        application: Application.
        timeout : Expire check time.

    Returns:
        True if there is an package needs to be deleted.
    """

    if timeout is None:
        timeout = command_tools.package_expire_time

    for_return = False
    delete_list = list()
    for package in application.old_packages:
        d = calculate_time_delta(package.creation_date)
        if d > timeout + int(timeout / 5):
            delete_list.append(package)

    if delete_list.__len__() > 0:
        for_return = True

    for package in delete_list:
        application.old_packages.remove(package)

    return for_return


def update_application_qubits(application: Application, timeout=None) -> bool:
    """
    Updates application old qubits.
    Deletes old and unprocessed qubits.
    The libs or protocols should update the relative container queue before starts.

    Args:
        application: Application.
        timeout : Expire check time.

    Returns:
        True if there is an package needs to be deleted.
    """

    if timeout is None:
        timeout = command_tools.qubit_expire_time

    for_return = False
    delete_list = list()
    for qubit in application.old_qubits:
        d = calculate_time_delta(qubit[2])
        if d > timeout + int(timeout / 5):
            delete_list.append(qubit)

    if delete_list.__len__() > 0:
        for_return = True

    for qubit in delete_list:
        application.old_qubits.remove(qubit)

    return for_return


def delete_from_active_request(application: Application, request_id=None, request_type=None) -> bool:
    """
    Deletes active request from application.

    Args:
        application: Application.
        request_id: Request ID.
        request_type: Request Type.

    Notes:
        Refrain using request type for searching in active requests.

    Returns:
         True if deletion success.
    """

    if request_id is None and request_type is None:
        application.logger.warning("Delete active request requires id or type. Returning false.")
        return False

    if request_id is not None:
        for request_ in application.active_requests:
            if request_.generic_id == request_id:
                application.active_requests.remove(request_)
                return True

    if request_type is not None:
        for request_ in application.active_requests:
            if isinstance(request_, request_type):
                application.active_requests.remove(request_)
                return True

    return False


def find_active_request(application: Application, request_id=None, request_type=None) -> Union[request.REQUEST, None]:
    """
    Searches active request from application and deletes.

    Args:
        application: Application.
        request_id: Request ID.
        request_type: Request Type.

    Notes:
        Refrain using request type for searching in active requests.

    Returns:
         Request if search success.
    """

    if request_id is None and request_type is None:
        application.logger.warning("Search active request requires id or type. Returning None.")
        return None

    if request_id is not None:
        for request_ in application.active_requests:
            if request_.generic_id == request_id:
                application.active_requests.remove(request_)
                return request_

    if request_type is not None:
        for request_ in application.active_requests:
            if isinstance(request_, request_type):
                application.active_requests.remove(request_)
                return request_
    return None


def reveal_device_information_request(application: Application, want_respond=True) -> request.REQUEST:
    """
    Makes get device information request to device.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.DeviceInformationRequest(application.label, want_respond=want_respond)
    the_request.process(application.device_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def reveal_socket_information_request(application: Application, want_respond=True) -> request.REQUEST:
    """
    Makes get socket information request to socket.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.SocketInformationRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def reveal_connectivity_information_request(application: Application, get_uuids=False, want_respond=True) -> request.REQUEST:
    """
    Makes get connectivity information request to socket.

    Args:
        application: Requester application.
        get_uuids: Get target device uuids insetead of label.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.ConnectivityInformationRequest(application.label, get_uuids, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def reveal_port_information_request(application: Application, port_key, search_classic=True, search_quantum=True, want_respond=True) -> request.REQUEST:
    """
    Makes get port information request to socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.PortInformationRequest(application.label, port_key, search_classic, search_quantum, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def open_communication_request(application: Application, want_respond=False) -> request.REQUEST:
    """
    Makes open communication request to socket.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.OpenCommunicationRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def close_communication_request(application: Application, want_respond=False) -> request.REQUEST:
    """
    Makes close communication request to socket.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.CloseCommunicationRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def activate_port_request(application: Application, port_key, search_classic=True, search_quantum=True, want_respond=False) -> request.REQUEST:
    """
    Makes activate port request to socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.ActivatePortRequest(application.label, port_key, search_classic, search_quantum, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def deactivate_port_request(application: Application, port_key, search_classic=True, search_quantum=True, want_respond=False) -> request.REQUEST:
    """
    Makes deactivate port request to socket.

    Args:
        application: Requester application.
        port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.DeactivatePortRequest(application.label, port_key, search_classic, search_quantum, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def resume_socket_request(application: Application, want_respond=False) -> request.REQUEST:
    """
    Makes resume socket request to socket.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.ResumeSocketRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def pause_socket_request(application: Application, want_respond=False) -> request.REQUEST:
    """
    Makes pause socket request to socket.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.PauseSocketRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def end_socket_signal(application: Application) -> signal.SIGNAL:
    """
    Makes end socket signal to socket.

    Args:
        application: Requester application.

    Return:
        Signal.
    """

    the_signal = signal.DeviceEndSocketSignal()
    the_signal.emit(application.socket_request_queue)
    return the_signal


def terminate_socket_signal(application: Application) -> signal.SIGNAL:
    """
    Makes terminate socket signal to socket.

    Args:
        application: Requester application.

    Return:
        Signal.
    """

    the_signal = signal.TerminateSocketSignal()
    the_signal.emit(application.socket_request_queue)
    return the_signal


def refresh_connections_request(application: Application, want_respond=False):
    """
    Makes refresh connections request to socket.
    Works when Auto_Ping OFF.

    Args:
        application: Requester application.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.RefreshConnectionsRequest(application.label, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def unconnect_channel_request(application: Application, channel_key, search_classic=True, search_quantum=True, want_respond=False) -> request.REQUEST:
    """
    Makes unconnect channel request to socket.

    Args:
        application: Requester application.
        channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.UnconnectChannelRequest(application.label, channel_key, search_classic, search_quantum, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def reconnect_channel_request(application: Application, channel_key, search_classic=True, search_quantum=True, want_respond=False) -> request.REQUEST:
    """
    Makes reconnect channel request to socket.

    Args:
        application: Requester application.
        channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
        search_classic: Search in classic ports.
        search_quantum: Search in quantum ports.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.ReconnectChannelRequest(application.label, channel_key, search_classic, search_quantum, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def send_package_request(application: Application, target, package, want_respond=True):
    """
    Makes send package request to socket.

    Args:
        application: Application.
        target: Target device id.
        package: Package.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.SendPackageRequest(application.label, target, package, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def send_qupack_request(application: Application, target, qupack, want_respond=True):
    """
    Makes send qupack request to socket.

    Args:
        application: Application.
        target: Target device id.
        qupack: Qupack.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.SendQupackRequest(application.label, target, qupack, want_respond=want_respond)
    the_request.process(application.socket_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def find_classic_route_request(application: Application, start_uuid, end_uuid, want_respond=True):
    """
    Makes find classic route request.

    Args:
        application: Application.
        start_uuid: Start UUID.
        end_uuid: End UUID.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.FindClassicRouteRequest(start_uuid, end_uuid, application.host_uuid, application.label, want_respond=want_respond)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def find_quantum_route_request(application: Application, start_uuid, end_uuid, want_respond=True):
    """
    Makes find quantum route request.

    Args:
        application: Application.
        start_uuid: Start UUID.
        end_uuid: End UUID.
        want_respond: Want respond flag.

    Return:
        Request.
    """

    the_request = request.FindQuantumRouteRequest(start_uuid, end_uuid, application.host_uuid, application.label, want_respond=want_respond)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def end_device_simulation(application: Application):
    """
    Ends device simulation of an Application.

    Args:
        application: Application.

    Returns:
        None.
    """

    the_request = signal.EndDeviceSignal(application.label)
    the_request.emit(application.device_request_queue)


def put_localhost(application: Application, values):
    """
    Puts values to application localhost.

    Args:
        application: Application.
        values: Values.
    """

    application.localhost_queue.put(values)


def flush_route_data(application: Application) -> bool:
    """
    Flushes socket routing data.

    Args:
        application: Application.

    Returns:
        True if sending signal success.
    """

    if application.host_device.route_app is not None:
        signal_ = signal.FlushRouteData()
        signal_.emit(application.host_device.route_app.threaded_request_queue)
        return True
    return False


def allocate_qubit(application: Application, *args):
    """
    Makes allocate qubit request to simulation.

    Args:
        application: Application.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.AllocateQubitRequest(application.label, application.host_uuid, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def allocate_qubits(application: Application, count, *args):
    """
    Makes allocate qubits request to simulation.

    Args:
        application: Application.
        count: Count of qubit.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.AllocateQubitsRequest(application.label, application.host_uuid, count, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def allocate_qframe(application: Application, frame_size, *args):
    """
    Makes allocate qubit request to simulation.

    Args:
        application: Application.
        frame_size: Qubit count in frame.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.AllocateQFrameRequest(application.label, application.host_uuid, frame_size, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def allocate_qframes(application: Application, frame_size, count, *args):
    """
    Makes allocate qubits request to simulation.

    Args:
        application: Application.
        frame_size: Count of qubit.
        count: Count of frame.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.AllocateQFramesRequest(application.label, application.host_uuid, frame_size, count, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def deallocate_qubits(application: Application, qubits):
    """
    Makes deallocate qubit request.

    Args:
        application: Application.
        qubits: Qubits for deallocate.

    Return:
        Request.
    """

    the_request = request.DeallocateQubitRequest(application.label, application.host_uuid, qubits)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def extend_qframe(application: Application, qubit_of_frame):
    """
    Makes extend frame request.

    Args:
        application: Application.
        qubit_of_frame: Qubit of frame.

    Return:
        Request.
    """

    the_request = request.ExtendQFrameRequest(application.label, application.host_uuid, qubit_of_frame)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def measure_qubits(application: Application, qubits, *args):
    """
    Makes measure qubits request to simulation.

    Args:
        application: Application.
        qubits: Qubits to measure.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.MeasureQubitsRequest(application.label, application.host_uuid, qubits, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def reset_qubits(application: Application, qubits, *args):
    """
    Makes reset qubits request to simulation.

    Args:
        application: Application.
        qubits: Qubits to measure.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.ResetQubitsRequest(application.label, application.host_uuid, qubits, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def apply_transformation(application: Application, gate_id, gate_args, qubits, *args):
    """
    Makes apply transformation request to simulation.

    Args:
        application: Application.
        gate_id: Id of gate.
        gate_args: Consturctor args for gate.
        qubits: Qubits to measure.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.ApplyTransformationRequest(application.label, application.host_uuid, gate_id, gate_args, qubits, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def generate_entangle_pairs(application: Application, count, *args):
    """
    Generates entangle pairs.

    Args:
        application: Application.
        count: Count of pairs.
        args: Backend specific arguments.

    Returns:
        Request.
    """

    the_request = request.GenerateEPRRequest(application.label, application.host_uuid, count, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def generate_ghz_pair(application: Application, size, *args):
    """
    Generates ghz entangle pair.

    Args:
        application: Application.
        size: Qubit count in ghz.
        args: Backend specific arguments.

    Returns:
        Request.
    """

    the_request = request.GenerateGHZRequest(application.label, application.host_uuid, size, *args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def make_channel_error_request(device_uuid, channel_uuid, qubits, sim_request_queue):
    """
    Makes channel error request to simulation.

    Args:
        device_uuid: Device UUID.
        channel_uuid: Channel UUID.
        qubits: Qubit in channel.
        sim_request_queue: Simulation kernel request queue.

    Notes:
        Whoever wants to use this method must know sim_queue
        and must be a part of device.
    """

    the_request = request.ApplyChannelError(device_uuid, channel_uuid, qubits)
    the_request.process(sim_request_queue)

    return the_request


def make_repeater_proceess_request(device_uuid, qubits, sim_request_queue):
    """
    Makes repeater process request to simulation.

    Args:
        device_uuid: Device UUID.
        qubits: Qubit in channel.
        sim_request_queue: Simulation kernel request queue.

    Notes:
        Whoever wants to use this method must know sim_queue
        and must be a part of device.
    """

    the_request = request.RepeaterProcessRequest(device_uuid, qubits)
    the_request.process(sim_request_queue)

    return the_request


def make_channel_error_and_repeater_request(device_uuid, channel_uuid, qubits, sim_request_queue):
    """
    Makes channel error and repeater request to simulation.

    Args:
        device_uuid: Device UUID.
        channel_uuid: Channel UUID.
        qubits: Qubit in channel.
        sim_request_queue: Simulation kernel request queue.

    Notes:
        Whoever wants to use this method must know sim_queue
        and must be a part of device.
    """

    the_request = request.ChannelAndRepeaterProcessRequest(device_uuid, channel_uuid, qubits)
    the_request.process(sim_request_queue)

    return the_request


def run_qkd_protocol_request(application: Application, target_device, key_lenght, method, side):
    """
    Makes qkd protocol request to application.
    
    Args:
        application: Application. 
        target_device: Identitier of device.
        key_lenght: Key length.
        method: QKD method.
        side: Side of party.
        
    Returns:
        Request or None.
    """

    qkd_app = application.host_device.qkd_app
    if qkd_app is None:
        return None

    the_request = request.RunQKDProtocolRequest(application.label, target_device, key_lenght, method, side)
    the_request.process(qkd_app.threaded_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def apply_serial_transformations_request(application: Application, list_of_gates, *args):
    """
    Makes apply transformation request to simulation.

    Args:
        application: Application.
        list_of_gates: Serial transformations of gates.
        *args: Backend specific arguments.

    Return:
        Request.
    """

    the_request = request.ApplySerialTransformationsRequest(application.label, application.host_uuid, list_of_gates, args)
    the_request.process(application.sim_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def current_qkd_key_request(application: Application):
    """
    Makes qkd protocol key request to application.

    Args:
        application: Application.

    Returns:
        Request or None.
    """

    qkd_app = application.host_device.qkd_app
    if qkd_app is None:
        return None

    the_request = request.CurrentQKDKeyRequest(application.label)
    the_request.process(qkd_app.threaded_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request


def flush_qkd_key_request(application: Application):
    """
    Makes flush qkd key request.

    Args:
        application: Application.

    Returns:
        Request or None.
    """

    qkd_app = application.host_device.qkd_app
    if qkd_app is None:
        return None

    the_request = request.FlushQKDKey(application.label)
    the_request.process(qkd_app.threaded_request_queue)

    if the_request.want_respond:
        application.active_requests.append(the_request)

    return the_request
