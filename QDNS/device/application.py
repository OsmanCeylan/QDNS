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

import logging
import time
from multiprocessing import Queue as MQueue
from queue import Queue as TQueue
from queue import SimpleQueue as TSimpleQueue
from typing import Optional

import QDNS
from QDNS.architecture import signal
from QDNS.tools import application_tools
from QDNS.tools import architecture_tools
from QDNS.tools import gates


class Application(architecture_tools.Layer):
    def __init__(self, label: str, host_device, function_, *args, app_settings: Optional[application_tools.ApplicationSettings] = None):
        """
        Application constructor.

        Args:
            label: Label of device.
            host_device: Host device of application.
            function_: Method of application.
            args: User arguments of application.
            app_settings: Applicaion settings.

        Notes:
            Static applications cannot be deleted.
            Disabled applications will not simulate.
            See QDNS.tools.application_tools.ApplicationSettings() for details.
        """

        self._label = label

        if app_settings is None:
            app_settings = application_tools.default_application_settings

        super(Application, self).__init__(architecture_tools.ID_APPLICATION, architecture_tools.THREAD_LAYER, self._label, layer_settings=app_settings)

        state_handler = architecture_tools.StateHandler(
            self.layer_id, True, *application_tools.application_states,
            GENERAL_STATE_NOT_STARTED=application_tools.APPLICATION_NOT_STARTED,
            GENERAL_STATE_IS_RUNNING=application_tools.APPLICATION_IS_RUNNING,
            GENERAL_STATE_IS_STOPPED=application_tools.APPLICATION_IS_STOPPED,
            GENERAL_STATE_IS_FINISHED=application_tools.APPLICATION_IS_FINISHED,
            GENERAL_STATE_IS_TERMINATED=application_tools.APPLICATION_IS_TERMINATED,
            GENERAL_STATE_IS_PAUSED=application_tools.APPLICATION_IS_PAUSED
        )
        self.set_state_handler(state_handler)

        self._host_device = host_device
        self._function = function_
        self._arguments = args

        self.add_module(application_tools.BlockList())

        self._active_requests = list()
        self._old_packages = list()
        self._old_qubits = list()
        self._old_responses = list()
        self._allocated_qubits = list()

        self.set_respond_queue(MQueue())
        self.listener = application_tools.Listener(self)
        self.logger.debug("Application {} of device {} is created.".format(self.label, self.host_label))

    def is_static(self) -> bool:
        return self.application_settings.static

    def is_enabled(self) -> bool:
        return self.application_settings.enabled

    def is_disabled(self) -> bool:
        return not self.application_settings.enabled

    def set_enable(self):
        self.application_settings.enable()

    def set_disable(self):
        self.application_settings.disable()

    def prepair_layer(self, sim_request_queue, user_dump_queue):
        self.queue_manager.add_queue(architecture_tools.SIM_REQUEST_QUEUE, sim_request_queue)
        self.queue_manager.add_queue(architecture_tools.DEVICE_REQUEST_QUEUE, self.host_device.threaded_request_queue)
        self.queue_manager.add_queue(architecture_tools.SOCKET_REQUEST_QUEUE, self.host_device.ntwk_socket.threaded_request_queue)

        self.queue_manager.add_queue(architecture_tools.INCOME_QUBIT_QUEUE, TSimpleQueue())
        self.queue_manager.add_queue(architecture_tools.INCOME_PACKAGE_QUEUE, TSimpleQueue())
        self.queue_manager.add_queue(architecture_tools.USER_DUMP_QUEUE, user_dump_queue)
        self.queue_manager.add_queue(architecture_tools.LOCALHOST_QUEUE, self.host_device.localhost)
        self.listener.set_listen_queue(TSimpleQueue())
        self.listener.set_release_queue(self.host_device.ntwk_socket.observer_queue)

        req = TQueue() if self.is_static() else None
        self.set_request_queue(req)
        self.set_threaded_queues(req, TSimpleQueue())
        self.set_state_report_queue(self.host_device.threaded_request_queue)
        self.logger.debug("Application {} of device {} prepaired its layer.".format(self.label, self.host_label))

    def run(self):
        if self.is_disabled():
            if self.is_static():
                self.logger.info("Application {} of device {} is disabled. Therefore do not simulate.".format(self.label, self.host_label))
            else:
                self.logger.warning("Application {} of device {} is disabled. Therefore do not simulate.".format(self.label, self.host_label))
            self.change_state(application_tools.APPLICATION_IS_FINISHED)
            return

        time.sleep(self.application_settings.delayed_start_time)
        self.logger.info("Application {} of device {} is starting...".format(self.label, self.host_label))
        time.sleep(0.5)

        start_time = time.time()
        self.change_state(application_tools.APPLICATION_IS_RUNNING)
        self._function(self, *self.arguments)
        end_time = time.time() - start_time

        self.logger.info("Application {} of device {} is ended in {} seconds.".format(self.label, self.host_label, end_time))
        time.sleep(0.5)
        self.change_state(application_tools.APPLICATION_IS_FINISHED)
        self.user_dump_queue.put([self.host_label, "{}Logs".format(self.label), self.logger.logs])

        if self.bond_end_with_device:
            signal.EndDeviceSignal(self.label).emit(self.device_request_queue)

    def bind_block_list(self, new_block_list: application_tools.BlockList) -> bool:
        """
        Updates blocklist of application.

        Args:
            new_block_list: New block list object.

        Returns:
            True if operation is success.
        """

        module = self.block_list
        if module is not None:
            to_return = self.update_module(module, new_block_list)
        else:
            self.add_module(new_block_list)
            to_return = True

        if to_return:
            self.logger.info("New blocklist module added to application {} of device {}.".format(self.label, self.host_label))
        else:
            self.logger.warning("Updating blocklist module of application {} of device {} is failed!".format(self.label, self.host_label))
        return to_return

    def change_host_device(self, new_host):
        """
        Changes or sets host device of application.
        Do not call manually! Let application manager handles it.
        """

        self._host_device = new_host

    @property
    def label(self) -> str:
        return self._label

    @property
    def application_settings(self) -> application_tools.ApplicationSettings:
        return self.layer_setting

    @property
    def host_device(self):
        return self._host_device

    @property
    def host_label(self) -> str:
        return self._host_device.label

    @property
    def host_uuid(self):
        return self._host_device.uuid

    @property
    def function(self):
        return self._function

    @property
    def arguments(self) -> tuple:
        return self._arguments

    @property
    def bond_end_with_device(self) -> bool:
        return self.application_settings.bond_end_with_device

    @property
    def end_device_if_terminated(self) -> bool:
        return self.application_settings.end_device_if_terminated

    @property
    def delayed_start_time(self) -> float:
        return self.application_settings.delayed_start_time

    @property
    def block_list(self) -> application_tools.BlockList:
        return self.get_module(application_tools.BlockList.MODULE_NAME)

    @property
    def sim_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.SIM_REQUEST_QUEUE)

    @property
    def device_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.DEVICE_REQUEST_QUEUE)

    @property
    def socket_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.SOCKET_REQUEST_QUEUE)

    @property
    def income_qubit_queue(self):
        return self.queue_manager.get_queue(architecture_tools.INCOME_QUBIT_QUEUE)

    @property
    def income_package_queue(self):
        return self.queue_manager.get_queue(architecture_tools.INCOME_PACKAGE_QUEUE)

    @property
    def active_requests(self):
        return self._active_requests

    @property
    def old_packages(self):
        return self._old_packages

    @property
    def old_qubits(self):
        return self._old_qubits

    @property
    def old_responses(self):
        return self._old_responses

    @property
    def allocated_qubits(self):
        return self._allocated_qubits

    @property
    def user_dump_queue(self):
        return self.queue_manager.get_queue(architecture_tools.USER_DUMP_QUEUE)

    @property
    def localhost_queue(self):
        return self.queue_manager.get_queue(architecture_tools.LOCALHOST_QUEUE)

    @property
    def listener_queue(self):
        return self.listener.listen_queue

    @property
    def listener_interrupt(self):
        return self.listener.interrupt

    """
    ================================================================================================
    #                                      some api.py calls                                       #
    ================================================================================================
    """

    @staticmethod
    def sleep(seconds: float):
        return time.sleep(seconds)

    @staticmethod
    def calculate_time_delta(datetime_old, datetime_new=None):
        """
        Calculates timedelta between two dates.

        Args:
            datetime_old: Old time in datatime format.
            datetime_new: New time in datatime format. Default is now().

        Returns:
            Date differance in seconds.
        """

        return QDNS.api.calculate_time_delta(datetime_old, datetime_new=datetime_new)

    @property
    def global_date(self):
        return QDNS.api.get_date()

    @property
    def global_time(self):
        return QDNS.api.get_time()

    def _wait_next_package(self, timeout=None):
        """
        Wait application next incoming package.

        Args:
            timeout: Expire time in float.

        Returns:
             Package or None.
        """

        return QDNS.api.application_wait_next_package(self, timeout=timeout)

    def _wait_next_qubit(self, timeout=None):
        """
        Application waits next qubit for itself.

        Args:
            timeout: Expire time.

        Returns:
             Qubit or None.
        """

        return QDNS.api.application_wait_next_qubit(self, timeout=timeout)

    def _wait_next_Trespond(self, timeout=None):
        """
        Application waits next (threaded) respond.

        Args:
            timeout: Expire time.

        Returns:
             Respond or None.
        """

        return QDNS.api.application_wait_next_Trespond(self, timeout=timeout)

    def _wait_next_Mrespond(self, timeout=None):
        """
        Application waits next (multiprocessed) respond.

        Args:
            timeout: Expire time.

        Returns:
             Respond or None.
        """

        return QDNS.api.application_wait_next_Mrespond(self, timeout=timeout)

    def _update_application_requests(self, timeout=None) -> bool:
        """
        Updates application request.
        Deletes old and unprocessed requests.
        The libs or protocols should update the relative container queue before starts.

        Args:
            timeout: Expire check time.

        Returns:
            True if an deletion occurred.
        """

        return QDNS.api.update_application_requests(self, timeout=timeout)

    def _update_application_packages(self, timeout=None) -> bool:
        """
        Updates application old packages.
        Deletes old and unprocessed packages.
        The libs or protocols should update the relative container queue before starts.

        Args:
            timeout: Expire check time.

        Returns:
            True if there is an package needs to be deleted.
        """

        return QDNS.api.update_application_packages(self, timeout=timeout)

    def _update_application_qubits(self, timeout=None) -> bool:
        """
        Updates application old qubits.
        Deletes old and unprocessed qubits.
        The libs or protocols should update the relative container queue before starts.

        Args:
            timeout: Expire check time.

        Returns:
            True if there is an package needs to be deleted.
        """

        return QDNS.api.update_application_qubits(self, timeout=timeout)

    def _delete_from_active_request(self, request_id=None, request_type=None) -> bool:
        """
        Deletes active request from application.

        Args:
            request_id: Request ID.
            request_type: Request Type.

        Notes:
            Refrain using request type for searching in active requests.

        Returns:
             True if deletion success.
        """

        return QDNS.api.delete_from_active_request(self, request_id=request_id, request_type=request_type)

    def _find_active_request(self, request_id=None, request_type=None):
        """
        Searches active request from application.

        Args:
            request_id: Request ID.
            request_type: Request Type.

        Notes:
            Refrain using request type for searching in active requests.

        Returns:
             Request if search success.
        """

        return QDNS.api.find_active_request(self, request_id=request_id, request_type=request_type)

    def _reveal_device_information_request(self, want_respond=True):
        """
        Makes get device information request to device.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.reveal_device_information_request(self, want_respond=want_respond)

    def _reveal_socket_information_request(self, want_respond=True):
        """
        Makes get socket information request to socket.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.reveal_socket_information_request(self, want_respond=want_respond)

    def _reveal_connectivity_information_request(self, get_uuids=False, want_respond=True):
        """
        Makes get connectivity information request to socket.

        Args:
            get_uuids: Get target device uuids insetead of label.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.reveal_connectivity_information_request(self, get_uuids, want_respond=want_respond)

    def _reveal_port_information_request(self, port_key, search_classic=True, search_quantum=True, want_respond=True):
        """
        Makes get port information request to socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.reveal_port_information_request(self, port_key, search_classic, search_quantum, want_respond=want_respond)

    def _open_communication_request(self, want_respond=False):
        """
        Makes open communication request to socket.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.open_communication_request(self, want_respond=want_respond)

    def _close_communication_request(self, want_respond=False):
        """
        Makes close communication request to socket.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.close_communication_request(self, want_respond=want_respond)

    def _activate_port_request(self, port_key, search_classic=True, search_quantum=True, want_respond=False):
        """
        Makes activate port request to socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.activate_port_request(
            self, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=want_respond
        )

    def _deactivate_port_request(self, port_key, search_classic=True, search_quantum=True, want_respond=False):
        """
        Makes activate port request to socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.deactivate_port_request(
            self, port_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=want_respond
        )

    def _resume_socket_request(self, want_respond=False):
        """
        Makes resume socket request to socket.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.resume_socket_request(self, want_respond=want_respond)

    def _pause_socket_request(self, want_respond=False):
        """
        Makes pause socket request to socket.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.pause_socket_request(self, want_respond=want_respond)

    def _end_socket_signal(self):
        """
        Makes terminate socket signal to socket.

        Return:
            Signal.
        """

        return QDNS.api.end_socket_signal(self)

    def _terminate_socket_signal(self):
        """
        Makes terminate socket signal to socket.

        Return:
            Signal.
        """

        return QDNS.api.terminate_socket_signal(self)

    def _refresh_connections_request(self, want_respond=False):
        """
        Makes refresh connections request to socket.
        Works when Auto_Ping OFF.

        Args:
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.refresh_connections_request(self, want_respond=want_respond)

    def _unconnect_channel_request(self, channel_key, search_classic=True, search_quantum=True, want_respond=False):
        """
        Makes unconnect channel request to socket.

        Args:
            channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.unconnect_channel_request(
            self, channel_key, search_classic=search_classic, search_quantum=search_quantum, want_respond=want_respond
        )

    def _send_package_request(self, target, package, want_respond=True):
        """
        Makes send package request to socket.

        Args:
            target: Target device id.
            package: Package.
            want_respond: Want respond flag.
        """

        return QDNS.api.send_package_request(self, target, package, want_respond=want_respond)

    def _send_qupack_request(self, target, qupack, want_respond=True):
        """
        Makes send qupack request to socket.

        Args:
            target: Target device id.
            qupack: Qupack.
            want_respond: Want respond flag.
        """

        return QDNS.api.send_qupack_request(self, target, qupack, want_respond=want_respond)

    def _find_classic_route_request(self, start_uuid, end_uuid, want_respond=True):
        """
        Makes find classic route request.

        Args:
            start_uuid: Start UUID.
            end_uuid: End UUID.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.find_classic_route_request(self, start_uuid, end_uuid, want_respond=want_respond)

    def _find_quantum_route_request(self, start_uuid, end_uuid, want_respond=True):
        """
        Makes find quantum route request.

        Args:
            start_uuid: Start UUID.
            end_uuid: End UUID.
            want_respond: Want respond flag.

        Return:
            Request.
        """

        return QDNS.api.find_quantum_route_request(self, start_uuid, end_uuid, want_respond=want_respond)

    def _flush_route_data(self):
        """
        Flushes socket routing data.

        Returns:
            True if sending signal success.
        """

        return QDNS.api.flush_route_data(self)

    def _allocate_qubit(self, *args):
        """
        Makes allocate qubit request to simulation.

        Args:
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.allocate_qubit(self, *args)

    def _allocate_qubits(self, count, *args):
        """
        Makes allocate qubit request to simulation.

        Args:
            count: Qubit count.
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.allocate_qubits(self, count, *args)

    def _allocate_qframe(self, frame_size, *args):
        """
        Makes allocate qframe request to simulation.

        Args:
            frame_size: Qubit count of frame.
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.allocate_qframe(self, frame_size, *args)

    def _allocate_qframes(self, frame_size, count, *args):
        """
        Makes allocate qframes request to simulation.

        Args:
            frame_size: Qubit count of frame.
            count: Frame count.
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.allocate_qframes(self, frame_size, count, *args)

    def _deallocate_qubits(self, *qubits):
        """
        Makes deallocate qubit request.

        Args:
            application: Application.
            qubits: Qubits for deallocate.

        Return:
            Request.
        """

        return QDNS.api.deallocate_qubits(self, qubits)

    def _extend_qframe(self, qubit_of_frame):
        """
        Makes extend frame request.

        Args:
            qubit_of_frame: Qubit of frame.

        Return:
            Request.
        """

        return QDNS.api.extend_qframe(self, qubit_of_frame)

    def _measure_qubits(self, qubits, *args):
        """
        Makes measure qubits request to simulation.

        Args:
            qubits: Qubits to measure.
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.measure_qubits(self, qubits, *args)

    def _reset_qubits(self, qubits, *args):
        """
        Makes reset qubits request to simulation.

        Args:
            qubits: Qubits to measure.
            *args: Backend specific arguments.

        Return:
            Request.
        """

        return QDNS.api.reset_qubits(self, qubits, *args)

    def _generate_entangle_pairs(self, count, *args):
        """
        Generates entangle pairs.

        Args:
            count: Count of pairs.
            args: Backend specific arguments.

        Returns:
            Request.
        """

        return QDNS.api.generate_entangle_pairs(self, count, *args)

    def _generate_ghz_pair(self, size, *args):
        """
        Generates ghz entangle pair.

        Args:
            size: Qubit count in ghz.
            args: Backend specific arguments.

        Returns:
            Request.
        """

        return QDNS.api.generate_ghz_pair(self, size, *args)

    def _run_qkd_protocol(self, target_device, key_lenght, method, side):
        """
        Makes qkd protocol request to application.

        Args:
            target_device: Identitier of device.
            key_lenght: Key length.
            method: QKD method.
            side: Side of party.

        Returns:
            Request or None.
        """

        return QDNS.api.run_qkd_protocol_request(self, target_device, key_lenght, method, side)

    def _apply_serial_transformation(self, list_of_gates):
        """
        Makes apply serial transformation request to simulation.

        Args:
            list_of_gates: List[Gate, GateArgs, List[Qubits]]

        Return:
            None.
        """

        return QDNS.api.apply_serial_transformations_request(self, list_of_gates)

    def _current_qkd_key(self):
        """
        Makes current qkd key request to QKD Layer.

        Returns:
            Request or None.
        """

        return QDNS.api.current_qkd_key_request(self)

    def _flush_qkd_key(self):
        """
        Apllication requests to remove key in QKD Layer.

        Returns:
            Request or None.
        """

        return QDNS.api.flush_qkd_key_request(self)

    """
    ================================================================================================
    #                                   some library.py calls                                      #
    ================================================================================================
    """

    def wait_next_package(self, source=None, timeout=None, check_old_packages=True):
        """
        Application waits next package from hinted device.

        Args:
            source: Hinted device.
            timeout: Expire time.
            check_old_packages: Checks old packages first.

        Returns:
             {"exit_code", "package"}
        """

        return QDNS.library.application_wait_next_package(
            self, source=source, timeout=timeout, check_old_packages=check_old_packages
        )

    def wait_next_protocol_package(self, source=None, timeout=None, check_old_packages=True):
        """
        Application waits next protocol package from hinted device.

        Args:
            source: Hinted device.
            timeout: Expire time.
            check_old_packages: Checks old packages first.

        Returns:
             {"exit_code", "package"}
        """

        return QDNS.library.application_wait_next_protocol_package(
            self, source=source, timeout=timeout, check_old_packages=check_old_packages
        )

    def wait_next_qubit(self, source=None, timeout=None, check_old_qubits=True):
        """
        Application waits qubit from hinted device.

        Args:
            source: Hinted device.
            timeout: Expire time.
            check_old_qubits: Check old unprocessed qubits..

        Returns:
             {"exit_code", "port_index", "sender", "time", "qubit"}
        """

        return QDNS.library.application_wait_next_qubit(
            self, source=source, timeout=timeout, check_old_qubits=check_old_qubits
        )

    def wait_next_qubits(self, count, source=None, timeout=None, check_old_qubits=True):
        """
        Application waits qubits from hinted device.

        Args:
            count: Qubit count.
            source: Hinted device.
            timeout: Expire time.
            check_old_qubits: Check old unprocessed qubits..

        Returns:
             {"exit_code", "qubits", "count"}
        """

        return QDNS.library.application_wait_next_qubits(
            self, count, source=source, timeout=timeout, check_old_qubits=check_old_qubits
        )

    def _wait_hinted_next_Trespond(self, request_id=None, request_type=None, timeout=None, check_old_responses=True):
        """
        Waits next threaded respond.

        Args:
            request_id: Request ID.
            request_type: Request Type.
            timeout: Expire time.
            check_old_responses: Check flag.

        Return:
            {"exit_code", "respond_exit_code", "respond_data"}
        """

        return QDNS.library.application_wait_next_Trespond(
            self, request_id=request_id, request_type=request_type, timeout=timeout, check_old_responses=check_old_responses
        )

    def _wait_hinted_next_Mrespond(self, request_id=None, request_type=None, timeout=None, check_old_responses=True):
        """
        Waits next multithreaded respond.

        Args:
            request_id: Request ID.
            request_type: Request Type.
            timeout: Expire time.
            check_old_responses: Check flag.

        Return:
            {"exit_code", "respond_exit_code", "respond_data"}
        """

        return QDNS.library.application_wait_next_Mrespond(
            self, request_id=request_id, request_type=request_type, timeout=timeout, check_old_responses=check_old_responses
        )

    def reveal_device_information(self):
        """
        Extract device information of an Application.

        Return:
            {"exit_code", "device_label", "device_unique_id"}
        """

        return QDNS.library.application_reveal_device_information(self)

    def reveal_socket_information(self, yield_all_string=False):
        """
        Extract socket information of the device of an Application.

        Args:
            yield_all_string: Yields SocketInformation object string.

        Return:
            {
                "exit_code", "socket_state", "classic_port_count", "quantum_port_count",
                "connected_classic_port", "connected_quantum_port", "object_string"
            }
        """

        return QDNS.library.application_reveal_socket_information(self, yield_all_string=yield_all_string)

    def reveal_connectivity_information(self, get_uuids=False):
        """
        Extract connectivity information.

        Args:
            get_uuids: Get target device uuids insetead of label.

        Return:
            {"exit_code", "classic_targets", "quantum_targets", "communication_state"}
        """

        return QDNS.library.application_reveal_connectivity_information(self, get_uuids=get_uuids)

    def reveal_connection_information(self, get_uuids=False):
        """
        Extract connection information.

        Args:
            get_uuids: Get target device uuids insetead of label.

        Return:
            {"exit_code", "classic_connections_group", "quantum_connections_group"}
        """

        return QDNS.library.application_reveal_connection_information(self, get_uuids=get_uuids)

    def reveal_port_information(self, port_key, search_classic=True, search_quantum=True):
        """
        Extract port information request to socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.

        Return:
            {"exit_code", "index", "type", "active", "connected", "channel_id", "target", "latency"}
        """

        return QDNS.library.application_reveal_port_information(
            self, port_key, search_classic=search_classic, search_quantum=search_quantum
        )

    def open_communication(self):
        """
        Application opens communication on socket.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_open_communication(self)

    def close_communication(self):
        """
        Application closes communication on socket.
        When communication is closed, nothing can pass thought the device socket, brokes route.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_close_communication(self)

    def activate_port(self, port_key, search_classic=True, search_quantum=True):
        """
        Activates port on socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_activate_port(self, port_key, search_classic=search_classic, search_quantum=search_quantum)

    def deactivate_port(self, port_key, search_classic=True, search_quantum=True):
        """
        Dectivates port on socket.

        Args:
            port_key: Port from key. (Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.

        Notes:
            Port still can be pinged. Brokes the routing.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_deactivate_port(self, port_key, search_classic=search_classic, search_quantum=search_quantum)

    def pause_socket(self):
        """
        Pauses socket request to socket.

        Notes:
            Applications of host device of socket cannot use socket. Did not interrupt incoming communication or routing.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_pause_socket(self)

    def resume_socket(self):
        """
        Resumes socket request to socket.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.application_resume_socket(self)

    def application_end_socket(self):
        """
        Makes end socket signal to socket.
        """

        return QDNS.library.application_end_socket(self)

    def terminate_socket(self):
        """
        Makes terminate socket signal to socket.
        """

        return QDNS.library.application_terminate_socket(self)

    def unconnect_channel(self, channel_key, search_classic=True, search_quantum=True):
        """
        Unconnects channel request to socket.

        Args:
            channel_key: Channel from key. (Port Index, Channel UUID, Target UUID, Target Label)
            search_classic: Search in classic ports.
            search_quantum: Search in quantum ports.

        Return:
            {"exit_code", "state_changed"}
        """

        return QDNS.library.socket_unconnect_channel(self, channel_key, search_classic=search_classic, search_quantum=search_quantum)

    def end_device_simulation(self):
        """
        Ends device simulation of an Application.
        Also terminates socket simulation.

        Returns:
            None.
        """

        return QDNS.api.end_device_simulation(self)

    def put_localhost(self, *values):
        """
        Puts values to application localhost.

        Args:
            values: Values.
        """

        return QDNS.library.application_put_localhost(self, *values)

    def put_simulation_result(self, *values):
        """
        Puts values to simulation result.

        Args:
            values: Values.
        """

        return QDNS.library.application_put_simulation_result(self, *values)

    def flush_route_data(self):
        """
        Flushes socket routing data.

        Returns:
            True if sending signal success.
        """

        return QDNS.library.application_flush_route_data(self)

    def allocate_qubit(self, *args):
        """
        Makes allocate qubit request to simulation.

        Args:
            *args: Backend specific arguments.

        Return:
             {"exit_code", "qubit"}
        """

        return QDNS.library.application_allocate_qubit(self, *args)

    def allocate_qubits(self, count, *args):
        """
        Makes allocate qubits request to simulation.

        Args:
            count: Count of qubit.
            *args: Backend specific arguments.

        Return:
             {"exit_code", "qubits"}
        """

        return QDNS.library.application_allocate_qubits(self, count, *args)

    def allocate_qframe(self, frame_size, *args):
        """
        Makes allocate qframe request to simulation.

        Args:
            frame_size: Qubit count of frame.
            *args: Backend specific arguments.

        Return:
             {"exit_code", "qubits"}
        """

        return QDNS.library.application_allocate_qframe(self, frame_size, *args)

    def allocate_qframes(self, frame_size, count, *args):
        """
        Makes allocate qframes request to simulation.

        Args:
            frame_size: Qubit count of frame.
            count: Count of qubit.
            *args: Backend specific arguments.

        Return:
             {"exit_code", "qubits"}
        """

        return QDNS.library.application_allocate_qframes(self, frame_size, count, *args)

    def deallocate_qubits(self, *qubits):
        """
        Deallocate qframes from app.

        Args:
            qubits: Qubits for deallocation.

        Return:
             None.
        """

        return QDNS.library.application_deallocate_qubits(self, *qubits)

    def extend_qframe(self, qubit_of_frame):
        """
        Exntend frame of qubit from back by 1.

        Args:
            qubit_of_frame: Qubit of frame.

        Return:
             {"exit_code", "qubit"}
        """

        return QDNS.library.application_extend_qframe(self, qubit_of_frame)

    def measure_qubits(self, qubits, *args):
        """
        Measures given qubits.

        Args:
            qubits: Qubits to measure.
            args: Backend specific arguments.

        Return:
             {"exit_code", "results"}
        """

        return QDNS.library.application_measure_qubits(self, qubits, *args)

    def reset_qubits(self, qubits, *args):
        """
        Measures given qubits.

        Args:
            qubits: Qubits to measure.
            args: Backend specific arguments.

        Return:
             None.
        """

        # Kernel does not respond this request.
        return QDNS.api.reset_qubits(self, qubits, *args)

    def apply_transformation(self, gate: gates.Gate, *qubits):
        """
        Makes apply transformation request to simulation.

        Args:
            qubits: Qubits to measure.
            gate: Gate object.

        Return:
            None.
        """

        if qubits.__len__() != gate.qubit_shape:
            logging.warning("Gate shape and qubit shape mismatch. {} != {}."
                            "Circuit simulation backends may raise errors."
                            .format(gate.qubit_shape, qubits.__len__()))

        return QDNS.library.application_apply_transformation(self, qubits, gate.gate_id, *gate.args())

    def send_classic_data(self, reciever, data, broadcast=False, routing=True):
        """
        Send classical data to target node.

        Args:
            reciever: Reciever node identifier.
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

        return QDNS.library.application_send_classic_data(
            self, reciever, data, broadcast=broadcast, routing=routing
        )

    def send_quantum(self, target, *qubits, routing=True):
        """
        Send quantum bits to another node.

        Args:
            target: Target node.
            qubits: Qubits to send.
            routing: Routing enable flag.

        Notes:
            Reciever must be node label or node id.

        Returns:
            {exit_code}
        """

        return QDNS.library.application_send_quantum(self, target, *qubits, routing=routing)

    def generate_entangle_pairs(self, count, *args):
        """
        Generates entangle pairs.

        Args:
            count: Count of pairs.
            args: Backend specific arguments.

        Returns:
            {"exit_code", "pairs"}
        """

        return QDNS.library.application_generate_entangle_pairs(self, count, *args)

    def generate_ghz_pair(self, size, *args):
        """
        Generates entangle pairs.

        Args:
            size: Qubit count in ghz state.
            args: Backend specific arguments.

        Returns:
            {"exit_code", "qubits"}
        """

        return QDNS.library.application_generate_ghz_pair(self, size, *args)

    def send_entangle_pairs(self, count, target, routing=True):
        """
        Sends entangle pairs to node.

        Args:
            count: Count of pairs.
            target: Target node.
            routing: Routing enable flag.

        Returns:
            {exit_code, my_pairs}
        """

        return QDNS.library.application_send_entangle_pairs(self, count, target, routing=routing)

    def broadcast_ghz_state(self):
        """
        Broadcasts ghz state to quantum connected nodes.

        Returns:
            {exit_code, my_qubit}
        """

        return QDNS.library.application_broadcast_ghz_state(self)

    def run_qkd_protocol(self, target_device, key_lenght, method):
        """
        Makes qkd protocol request to application.

        Args:
            target_device: Identitier of device.
            key_lenght: Key length.
            method: QKD method.

        Returns:
            {exit_code, key, lenght}
        """

        return QDNS.library.application_run_qkd_protocol(self, target_device, key_lenght, method)

    def wait_qkd(self, source=None):
        """
        Apllication waits QKD from source.

        Args:
            source: Initiater device identifier.

        Returns:
            {exit_code, key, lenght}
        """

        return QDNS.library.application_wait_qkd(self, source=source)

    def apply_serial_transformations(self, list_of_gates):
        """
        Makes apply serial transformation request to simulation.

        Args:
            list_of_gates: List[Gate, GateArgs, List[Qubits]]

        Return:
            None.
        """

        return QDNS.library.application_apply_serial_transformations(self, list_of_gates)

    def current_qkd_key(self):
        """
        Makes current qkd key request to QKD Layer.

        Returns:
            {exit_code, key, lenght}
        """

        return QDNS.library.application_current_qkd_key(self)

    def flush_qkd_key(self):
        """
        Apllication requests to remove key in QKD Layer.

        Returns:
            None.
        """

        return QDNS.library.application_flush_qkd_key(self)
