import time
from copy import deepcopy
from datetime import timedelta
from queue import Queue as TQueue, Empty
from typing import Optional, Union, Dict

import numpy as np

from QDNS.architecture import request, signal, respond
from QDNS.commands.api import make_channel_error_request
from QDNS.device.channel import ClassicChannel, QuantumChannel
from QDNS.rtg_apps.routing import RoutingLayer
from QDNS.tools import application_tools
from QDNS.tools import architecture_tools
from QDNS.tools import communication_tools
from QDNS.tools import exit_codes
from QDNS.tools import socket_tools
from QDNS.tools.simulation_tools import TerminatableThread

PING_CONTROL_JOB = "This thread control ping events"
CLASSIC_CONTROL_JOB = "This thread controls classic income queue"
QUANTUM_CONTROL_JOB = "This thread controls quantum income queue"
REQUEST_CONTROL_JOB = "This thread controls request income queue"


class NetworkSocket(architecture_tools.Layer):
    def __init__(self, host_device, socket_settings: Optional[socket_tools.SocketSettings] = None):
        self._label = "{}'s socket".format(host_device.label)
        self._socket_settings = socket_settings

        if socket_settings is None:
            self._socket_settings = socket_tools.default_socket_settings

        super(NetworkSocket, self).__init__(
            architecture_tools.ID_SOCKET, architecture_tools.THREAD_LAYER,
            self._label, layer_settings=self._socket_settings
        )

        state_handler = architecture_tools.StateHandler(
            self.layer_id, False, *socket_tools.socket_states,
            GENERAL_STATE_IS_RUNNING=socket_tools.SOCKET_IS_UP,
            GENERAL_STATE_IS_STOPPED=socket_tools.SOCKET_IS_DOWN,
            GENERAL_STATE_IS_PAUSED=socket_tools.SOCKET_PAUSED,
            GENERAL_STATE_IS_FINISHED=socket_tools.SOCKET_IS_OVER
        )
        self.set_state_handler(state_handler)

        # Worker threads.
        self.__ping_thread = None
        self.__request_thread = None
        self.__receive_classic_thread = None
        self.__receive_quantum_thread = None

        self._host_device = host_device
        self.add_module(socket_tools.PortManager(self.host_device_id, self.max_cc_count, self.max_qc_count))

        self.queue_manager.add_queue(architecture_tools.SIM_REQUEST_QUEUE, None)
        self.queue_manager.add_queue(architecture_tools.INCOME_CLASSIC_QUEUE, self.port_manager.classic_receive_queue)
        self.queue_manager.add_queue(architecture_tools.INCOME_QUANTUM_QUEUE, self.port_manager.quantum_receive_queue)
        self.queue_manager.add_queue(architecture_tools.PING_HANDLE_QUEUE, None)
        self.queue_manager.add_queue(architecture_tools.PING_REQUEST_QUEUE, None)
        self.queue_manager.add_queue(architecture_tools.OBSERVER_QUEUE, None)

        if self.host_device.otg_device and self.port_manager.classic_port_count > 2:
            raise AttributeError("Device {} is OTG. Cannot have more than 2 classic connection.".format(self.host_label))
        if self.host_device.otg_device and self.port_manager.quantum_port_count > 2:
            raise AttributeError("Device {} is OTG. Cannot have more than 2 quantum connection.".format(self.host_label))

        self.routing_app = None
        self.logger.debug("Socket added to device {} is added with total {} ports.".format(self.host_label, self.port_manager.all_port_count))

    def prepair_layer(self, sim_request_queue):
        """
        Sets threads and queues for simulation.
        Must call before its simulation.
        """

        self.set_threaded_queues(TQueue(), None)
        self.queue_manager.update_queue(architecture_tools.PING_HANDLE_QUEUE, TQueue())
        self.queue_manager.update_queue(architecture_tools.PING_REQUEST_QUEUE, TQueue())
        self.queue_manager.update_queue(architecture_tools.SIM_REQUEST_QUEUE, sim_request_queue)
        self.queue_manager.update_queue(architecture_tools.OBSERVER_QUEUE, TQueue())
        self.port_manager.set_sim_request_queue(sim_request_queue)

        self.__receive_classic_thread = TerminatableThread(self.run, args=(CLASSIC_CONTROL_JOB,), daemon=True)
        self.__receive_quantum_thread = TerminatableThread(self.run, args=(QUANTUM_CONTROL_JOB,), daemon=True)
        self.__request_thread = TerminatableThread(self.run, args=(REQUEST_CONTROL_JOB,), daemon=True)
        self.__ping_thread = TerminatableThread(self.run, args=(PING_CONTROL_JOB,), daemon=True)

        if self.is_routing_enabled():
            self.routing_app = self.host_device.appman.get_application_from(RoutingLayer.label, _raise=True)
        self.logger.debug("Socket of device {} prapair layer with jobs.".format(self.host_label))

    def start_socket(self):
        """ Starts socket simulation. """

        if self.__receive_classic_thread is None:
            raise Exception("Device {}'s socket layer probably did not prepaired.".format(self.host_label))
        if self.__receive_quantum_thread is None:
            raise Exception("Device {}'s socket layer probably did not prepaired.".format(self.host_label))
        if self.__request_thread is None:
            raise Exception("Device {}'s socket layer probably did not prepaired.".format(self.host_label))

        self.__request_thread.start()
        self.__receive_classic_thread.start()
        self.__receive_quantum_thread.start()

        # Otg devices cannot ping.
        if not self.host_device.otg_device:
            self.__ping_thread.start()

        self.change_state(socket_tools.SOCKET_IS_UP)

    def run(self, target_job):
        if target_job == REQUEST_CONTROL_JOB:
            while 1:
                if self.state_handler.is_finished():
                    break

                action = self.threaded_request_queue.get()
                if isinstance(action, request.REQUEST):
                    self.__handle_request(action)

                elif isinstance(action, signal.SIGNAL):
                    self.__handle_signal(action)

                else:
                    raise AttributeError("Socket of device {} got unrecognized action of {}.".format(self.host_label, action))

        elif target_job == CLASSIC_CONTROL_JOB:
            while 1:
                if self.state_handler.is_finished():
                    break

                port, package = self.port_manager.get_classic_receive()
                self.__handle_incoming_package(port, package)

        elif target_job == QUANTUM_CONTROL_JOB:
            while 1:
                if self.state_handler.is_finished():
                    break

                port, qupack = self.port_manager.get_quantum_receive()
                self.__handle_incoming_qupack(port, qupack)

        elif target_job == PING_CONTROL_JOB:
            ping_time = round(np.random.uniform(self.ping_time * 9 / 10, self.ping_time * 11 / 10), 2)
            port_states: Dict[socket_tools.Port, bool] = dict()
            refresh_requests = TQueue()
            first_time = True

            while 1:
                if self.state_handler.is_finished():
                    break

                port_states.clear()
                if first_time:
                    self.__broadcast_ping_protocol()
                else:
                    if self.auto_ping:
                        self.__broadcast_ping_protocol()
                    else:
                        action = self.ping_request_queue.get()
                        if isinstance(action, request.RefreshConnectionsRequest):
                            if action.want_respond:
                                refresh_requests.put(action)
                            self.__broadcast_ping_protocol()
                        else:
                            raise AttributeError("Ping thread or {} got unexpected request.".format(self.host_label))

                for port in self.port_manager.active_connected_quantum_ports:
                    port_states[port] = False

                for port in self.port_manager.active_connected_classic_ports:
                    port_states[port] = False

                start_time = time.time()
                while 1:
                    try:
                        port, ping_package = self.ping_handle_queue.get(timeout=1.75)
                    except Empty:
                        break
                    else:
                        port = self.port_manager.get_port(port, classic=True, quantum=True)
                        port.set_target_device_id(ping_package.device_id)
                        port.set_latency(time.time() - ping_package.ping_time)
                        port_states[port] = True

                for port in port_states:
                    if not port_states[port]:
                        self.logger.warning("Connection beetwen {} and {} is probably removed.".format(self.host_label, port.target_device_id.label))
                        self.port_manager.unconnect_port(port, soft=True)
                process_time = time.time() - start_time

                if self.auto_ping:
                    if process_time < ping_time:
                        time.sleep(ping_time - process_time)
                    else:
                        time.sleep(0.01)

                    if self.socket_settings.clear_route_cache:
                        signal_ = signal.FlushRouteData()
                        signal_.emit(self.routing_app.threaded_request_queue)

                else:
                    try:
                        request_ = refresh_requests.get_nowait()
                    except Empty:
                        pass
                    else:
                        port_dict = dict()
                        for port in port_states:
                            port_dict[port.channel_uuid] = port_states[port]

                        respond.RefreshConnectionsRespond(
                            request_.generic_id, exit_codes.REFRESH_CONNECTION_SUCCESS[0], port_dict, process_time
                        ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)
                    time.sleep(0.1)

                first_time = False
        else:
            raise ChildProcessError("Device {} socket got unknown thread job. {}?".format(self.host_label, target_job))

    def __handle_signal(self, signal_: signal.SIGNAL):
        """
        Handles signals.

        Args:
            signal_: The signal.
        """

        if isinstance(signal_, signal.DeviceEndSocketSignal):
            self.__end_socket()

        elif isinstance(signal_, signal.TerminateSocketSignal):
            self.terminate_socket()

        else:
            raise ValueError("Unrecognized signal for device {}'socket. What \"{}\"?".format(self.host_label, signal_))

    def __handle_request(self, request_: request.REQUEST):
        """
        Handles requests.

        Args:
            request_: The request.
        """

        # Layer check.
        if request_.target_id != architecture_tools.ID_SOCKET:
            raise ValueError("Exepted socket request but got {}.".format(request_.target_id))

        # State check.
        if self.state == self.state_handler.state_is_stopped:
            if isinstance(request_, request.ResumeSocketRequest):
                state_changed = self.change_state(socket_tools.SOCKET_IS_UP)
                if request_.want_respond:
                    respond.ResumeSocketRespond(
                        request_.generic_id, exit_codes.SOCKET_STATE_CHANGE_SUCCESS[0], state_changed
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

            else:
                if request_.want_respond:
                    respond.GenericRespond(
                        request_.generic_id, exit_codes.SOCKET_IS_DONW_STATE[0], None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)
            return

        # Socket information request.
        if isinstance(request_, request.SocketInformationRequest):
            ss = socket_tools.SocketInformation(self.state, self.host_device_id, self.socket_settings, self.port_manager)

            if request_.want_respond:
                respond.SocketInformationRespond(
                    request_.generic_id, exit_codes.GATHER_SOCKET_INFORMATION_SUCCESS[0], ss
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Connectivity information request.
        elif isinstance(request_, request.ConnectivityInformationRequest):
            ci = socket_tools.ConnectivityInformation(self.port_manager, request_.get_uuids)

            if request_.want_respond:
                respond.ConnectivityInformationRespond(
                    request_.generic_id, exit_codes.GATHER_CONNECTIVITY_INFORMATION_SUCCESS[0], ci
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Port information request.
        elif isinstance(request_, request.PortInformationRequest):
            port_ = self.port_manager.get_port(request_.port_key, classic=request_.search_classic, quantum=request_.search_quantum, _raise=False)

            if request_.want_respond:
                if port_ is None:
                    respond.PortInformationRespond(
                        request_.generic_id, exit_codes.FIND_PORT_FAILED[0], None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

                else:
                    pi = socket_tools.PortInformation(port_)
                    respond.PortInformationRespond(
                        request_.generic_id, exit_codes.GATHER_PORT_INFORMATION_SUCCESS[0], pi
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Open communication request.
        elif isinstance(request_, request.OpenCommunicationRequest):
            state_changed = self.port_manager.open_connectivity()

            if request_.want_respond:
                respond.OpenCommunicationRespond(
                    request_.generic_id, exit_codes.CLOSE_COMMUNICATION_SUCCESS[0], state_changed
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Close communication request.
        elif isinstance(request_, request.CloseCommunicationRequest):
            state_changed = self.port_manager.close_connectivity()

            if request_.want_respond:
                respond.CloseCommunicationRespond(
                    request_.generic_id, exit_codes.CLOSE_COMMUNICATION_FAILED[0], state_changed
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Activate port request.
        elif isinstance(request_, request.ActivatePortRequest):
            port_ = self.port_manager.get_port(request_.port_key, classic=request_.search_classic, quantum=request_.search_quantum, _raise=False)

            state_changed = None
            if port_ is not None:
                state_changed = self.port_manager.activate_port(port_)

            if request_.want_respond:
                if port_ is None:
                    respond.ActivatePortRespond(
                        request_.generic_id, exit_codes.FIND_PORT_FAILED[0], None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

                else:
                    respond.ActivatePortRespond(
                        request_.generic_id, exit_codes.ACTIVATE_PORT_SUCCESS[0], state_changed
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Deactivate port request.
        elif isinstance(request_, request.DeactivatePortRequest):
            port_ = self.port_manager.get_port(request_.port_key, classic=request_.search_classic, quantum=request_.search_quantum, _raise=False)

            state_changed = None
            if port_ is not None:
                state_changed = self.port_manager.deactivate_port(port_)

            if request_.want_respond:
                if port_ is None:
                    respond.DeactivatePortRespond(
                        request_.generic_id, exit_codes.FIND_PORT_FAILED[0], None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

                else:
                    respond.DeactivatePortRespond(
                        request_.generic_id, exit_codes.DEACTIVATE_PORT_SUCCESS[0], state_changed
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Resume socket request.
        elif isinstance(request_, request.ResumeSocketRequest):
            state_changed = self.change_state(socket_tools.SOCKET_IS_UP)

            if request_.want_respond:
                respond.ResumeSocketRespond(
                    request_.generic_id, exit_codes.SOCKET_STATE_CHANGE_SUCCESS[0], state_changed
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Pause socket request.
        elif isinstance(request_, request.PauseSocketRequest):
            state_changed = self.change_state(socket_tools.SOCKET_IS_DOWN)

            if request_.want_respond:
                respond.PauseSocketRespond(
                    request_.generic_id, exit_codes.SOCKET_STATE_CHANGE_SUCCESS[0], state_changed
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Refresh connections request.
        # ! Ping thread handles this request.
        elif isinstance(request_, request.RefreshConnectionsRequest):
            if self.auto_ping:
                if request_.want_respond:
                    respond.RefreshConnectionsRespond(
                        request_.generic_id, exit_codes.REFRESH_CONNECTION_FAILED[0], None, None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)
            else:
                self.ping_request_queue.put(request_)

        # Unconnect channel request.
        elif isinstance(request_, request.UnconnectChannelRequest):
            port_ = self.port_manager.get_port(request_.channel_key, classic=request_.search_classic, quantum=request_.search_quantum, _raise=False)

            state_changed = False
            if port_ is not None:
                state_changed = self.port_manager.unconnect_port(port_, soft=True)

            if request_.want_respond:
                if port_ is None:
                    respond.UnconnectChannelRespond(
                        request_.generic_id, exit_codes.FIND_PORT_FAILED[0], None
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

                else:
                    respond.UnconnectChannelRespond(
                        request_.generic_id, exit_codes.UNCONNECT_CHANNEL_SUCCESS[0], state_changed
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Reconnect channel request.
        elif isinstance(request_, request.ReconnectChannelRequest):
            port_ = self.port_manager.get_port(request_.channel_key, classic=request_.search_classic, quantum=request_.search_quantum, _raise=False)

            state_changed = False
            if port_ is not None:
                state_changed = self.port_manager.reconnect_port(port_)

            if request_.want_respond:
                if port_ is None:
                    respond.ReconnectChannelRespond(
                        request_.generic_id, exit_codes.FIND_PORT_FAILED[0]
                    ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

                else:
                    if state_changed:
                        respond.ReconnectChannelRespond(
                            request_.generic_id, exit_codes.RECONNECT_CHANNEL_SUCCESS[0]
                        ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)
                    else:
                        respond.ReconnectChannelRespond(
                            request_.generic_id, exit_codes.RECONNECT_CHANNEL_FAILED[0]
                        ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Send package request.
        elif isinstance(request_, request.SendPackageRequest):
            exit_code_, count = self.__send_package(request_.package, request_.target)

            if request_.want_respond:
                respond.SendPackageRespond(
                    request_.generic_id, exit_code_, count
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        # Send qupack request.
        elif isinstance(request_, request.SendQupackRequest):
            exit_code_, count = self.__send_qupack(request_.qupack, request_.target)

            if request_.want_respond:
                respond.SendQupackRespond(
                    request_.generic_id, exit_code_, count
                ).process(self.host_device.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        else:
            raise ValueError("Unrecognized request for device {}'socket. What \"{}\"?".format(self.host_label, request_))

    def __handle_incoming_package(self, port: socket_tools.Port, package: communication_tools.Package):
        """
        Handles incoming packages.

        Args:
            port: Incoming port.
            package: The package.
        """

        # Handle ping packages first.
        if isinstance(package, communication_tools.PingRequestPackage):
            if not port.is_unconnected():
                port.set_target_device_id(package.device_id)
                port.set_latency(time.time() - package.ping_time)

            if not self.host_device.otg_device:
                self.port_manager.send_classic_information(port, communication_tools.PingRespondPackage(self.host_device_id), check_active=False)
            else:
                target_port = None
                for port_ in self.port_manager.active_classic_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_classic_information(target_port, package)
            return

        if isinstance(package, communication_tools.PingRespondPackage):
            if not port.connected:
                self.port_manager.reconnect_port(port)
            if not self.host_device.otg_device:
                self.ping_handle_queue.put((port, package))
            else:
                target_port = None
                for port_ in self.port_manager.active_classic_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_classic_information(target_port, package)
            return

        if not port.active:
            return

        if package.is_drop():
            self.logger.warning("A package dropped on device {}'s socket.".format(self.host_label))
            return

        if self.host_device.observe_capability:
            app = self.device_default_app
            if app is None:
                self.logger.error("The package for application {} cannot delivered in device {}.".format(package.ip_layer.sender, self.host_label))
            else:
                app.listener_queue.put(deepcopy(package))
                if app.listener_interrupt:
                    message = self.observer_queue.get()
                    if message == socket_tools.DROP_PACKAGE:
                        return

        if package.ip_layer.receiver is None:
            if not self.host_device.otg_device:
                self.__put_package_to_application(package.app_layer.app_label, package)
            else:
                target_port = None
                for port_ in self.port_manager.active_classic_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_classic_information(target_port, package)

        elif package.ip_layer.receiver == self.host_label or package.ip_layer.receiver == self.host_uuid:
            self.__put_package_to_application(package.app_layer.app_label, package)

        else:
            route_data = package.ip_layer.route
            if route_data is None:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got package without route info. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_package(package, package.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_classic_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_classic_information(target_port, package)
                return

            if route_data[0] != self.host_uuid:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got package with corrupted route. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_package(package, package.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_classic_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_classic_information(target_port, package)
                return

            if route_data.__len__() <= 1:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got package with altered route. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_package(package, package.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_classic_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_classic_information(target_port, package)
                return

            if not self.host_device.otg_device:
                route_data.pop(0)
                self.__send_package(package, route_data[0])
            else:
                target_port = None
                for port_ in self.port_manager.active_classic_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_classic_information(target_port, package)

    def __handle_incoming_qupack(self, port: socket_tools.Port, qupack: communication_tools.Qupack):
        """
        Handles incoming qupacks.

        Args:
            port: Incoming port.
            qupack: The qupack.
        """

        # Handle ping packages first.
        if isinstance(qupack, communication_tools.PingRequestPackage):
            if not port.is_unconnected():
                port.set_target_device_id(qupack.device_id)
                port.set_latency(time.time() - qupack.ping_time)

            if not self.host_device.otg_device:
                self.port_manager.send_quantum_information(port, communication_tools.PingRespondPackage(self.host_device_id), check_active=False)
            else:
                target_port = None
                for port_ in self.port_manager.active_quantum_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_quantum_information(target_port, qupack)
            return

        if isinstance(qupack, communication_tools.PingRespondPackage):
            if not port.connected:
                self.port_manager.reconnect_port(port)

            if not self.host_device.otg_device:
                self.ping_handle_queue.put((port, qupack))
            else:
                target_port = None
                for port_ in self.port_manager.active_quantum_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_quantum_information(target_port, qupack)
            return

        # Port is not open.
        if not port.active:
            return

        make_channel_error_request(self.host_uuid, port.channel_uuid, qupack.qubits, self.sim_request_queue)

        if self.host_device.observe_capability:
            app = self.device_default_app
            if app is None:
                self.logger.error("The package for application {} cannot delivered in device {}.".format(qupack.ip_layer.sender, self.host_label))
            else:
                app.listener_queue.put(deepcopy(qupack))
                if app.listener_interrupt:
                    message = self.observer_queue.get()
                    if message == socket_tools.DROP_PACKAGE:
                        return

        if qupack.ip_layer.receiver is None:
            if not self.host_device.otg_device:
                self.__put_qupack_to_application(qupack.app_layer.app_label, port, qupack)
            else:
                target_port = None
                for port_ in self.port_manager.active_quantum_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_quantum_information(target_port, qupack)

        elif qupack.ip_layer.receiver == self.host_label or qupack.ip_layer.receiver == self.host_uuid:
            self.__put_qupack_to_application(qupack.app_layer.app_label, port, qupack)

        else:
            route_data = qupack.ip_layer.route
            if route_data is None:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got qupack without route info. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_qupack(qupack, qupack.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_quantum_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_quantum_information(target_port, qupack)
                return

            if route_data[0] != self.host_uuid:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got qupack without route info. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_qupack(qupack, qupack.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_quantum_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_quantum_information(target_port, qupack)
                return

            if route_data.__len__() <= 1:
                if not self.host_device.otg_device:
                    self.logger.critical("Device {} got qupack with altered route. Rerouting package, but this could be BUG.".format(self.host_label))
                    self.__send_qupack(qupack, qupack.ip_layer.receiver)
                else:
                    target_port = None
                    for port_ in self.port_manager.active_quantum_ports:
                        if port_.index != port.index:
                            target_port = port_
                            break
                    self.port_manager.send_quantum_information(target_port, qupack)
                return

            if not self.host_device.otg_device:
                route_data.pop(0)
                self.__send_qupack(qupack, route_data[0])
            else:
                target_port = None
                for port_ in self.port_manager.active_quantum_ports:
                    if port_.index != port.index:
                        target_port = port_
                        break
                self.port_manager.send_quantum_information(target_port, qupack)

    def __send_package(self, package: communication_tools.Package, target):
        """
        Network socket tries to send package to target.

        Args:
            package: Network package.
            target: Target device.

        Notes:
            Target can be device label, device uuid, channel uuid or index of port.
        """

        port_ = self.port_manager.get_port(target, classic=True, quantum=False, _raise=False)

        broadcast = package.ip_layer.broadcast
        routing = package.ip_layer.routing

        if broadcast:
            for port_ in self.port_manager.active_connected_classic_ports:
                package_temp = deepcopy(package)
                package_temp.ip_layer.change_receiver(None)
                self.port_manager.send_classic_information(port_, package_temp)
            return exit_codes.BROADCASTED_PACKAGE[0], self.port_manager.active_connected_classic_port_count

        if port_ is None:
            if not routing:
                return exit_codes.NO_DIRECT_CONNECTION_FOUND[0], 0
            else:
                if not self.is_routing_enabled():
                    return exit_codes.ROUTING_IS_DISABLED[0], 0
                else:
                    self.routing_app.threaded_request_queue.put(request.RoutePackageRequest(target, package))
                    return exit_codes.PACKAGE_IS_ROUTING[0], 1

        if not port_.active:
            return exit_codes.PORT_IS_DISABLE[0], 0

        self.port_manager.send_classic_information(port_, package)
        return exit_codes.PACKAGE_SENDED[0], 1

    def __send_qupack(self, qupack: communication_tools.Qupack, target):
        """
        Network socket tries to send qupack to target.

        Args:
            qupack: Qupack.
            target: Target device.

        Notes:
            Target can be device label, device uuid, channel uuid or index of port.
        """

        port_ = self.port_manager.get_port(target, classic=False, quantum=True, _raise=False)
        routing = qupack.ip_layer.routing

        if port_ is None:
            if not routing:
                return exit_codes.NO_DIRECT_CONNECTION_FOUND[0], 0
            else:
                if not self.is_routing_enabled():
                    return exit_codes.ROUTING_IS_DISABLED[0], 0
                else:
                    self.routing_app.threaded_request_queue.put(request.RouteQupackRequest(target, qupack))
                    return exit_codes.QUPACK_IS_ROUTING[0], qupack.ip_layer.data.__len__()

        if not port_.active:
            return exit_codes.PORT_IS_DISABLE[0], 0

        self.port_manager.send_quantum_information(port_, qupack)
        return exit_codes.QUPACK_SENDED[0], qupack.ip_layer.data.__len__()

    def __broadcast_ping_protocol(self) -> Dict[socket_tools.Port, bool]:
        """
        Broadcasts ping packages.
        """

        to_return_dict = dict()
        pp = communication_tools.PingRequestPackage(self.host_device_id)
        for port in self.port_manager.active_connected_classic_ports:
            to_return_dict[port] = self.port_manager.send_information(port, pp)

        for port in self.port_manager.active_connected_quantum_ports:
            to_return_dict[port] = self.port_manager.send_information(port, pp)

        return to_return_dict

    def __put_package_to_application(self, application, package: communication_tools.Package):
        """
        Puts package to the application in this device.

        Args:
            application: Application identifier.
            package: Package.
        """

        app = self.host_device.appman.get_application_from(application, _raise=False)
        if app is None:
            self.logger.error("The package for application {} cannot delivered in device {}.".format(package.ip_layer.sender, self.host_label))
            return
        app.income_package_queue.put(package)

    def __put_qupack_to_application(self, application, port: socket_tools.Port, qupack: communication_tools.Qupack):
        """
        Puts qubit to the applicaiton on this device.

        Args:
            application: Application identifier.
            port: Port.
            qupack: Qupack.
        """

        app = self.host_device.appman.get_application_from(application, _raise=False)
        if app is None:
            self.logger.error("The qupack for application {} cannot delivered in device {}.".format(qupack.ip_layer.sender, self.host_label))
            return

        qubits = qupack.ip_layer.data
        sender = qupack.ip_layer.sender
        qupack_date = qupack.creation_date

        for i, qubit in enumerate(qubits):
            app.income_qubit_queue.put([port.index, sender, qupack_date + timedelta(microseconds=i*7.5), qubit])

    def connect_classic_channel(self, channel: ClassicChannel) -> Union[socket_tools.Port, None]:
        """
        Connects channel to port.
        This operation must be done in two steps.
        Must be setted queues after connect.
        Redirects Port Manger module.

        Args:
            channel: Channel.

        Returns:
            Port or None.
        """

        return self.port_manager.connect_classic_channel(channel)

    def connect_quantum_channel(self, channel: QuantumChannel) -> Union[socket_tools.Port, None]:
        """
        Connects channel to port.
        This operation must be done in two steps.
        Must be setted queues after connect.
        Redirects Port Manger module.

        Args:
            channel: Channel.

        Returns:
            Port or None.
        """

        return self.port_manager.connect_quantum_channel(channel)

    def __end_socket(self):
        self.host_device.user_dump_queue.put([self.host_label, "SocketLogs", self.logger.logs])
        self.change_state(socket_tools.SOCKET_IS_OVER)
        self.threaded_request_queue.put(signal.DeviceEndSocketSignal(socket_tools.SOCKET_IS_OVER))
        self.logger.warning("Socket of device {} is ended.".format(self.host_label))

    def terminate_socket(self):
        self.host_device.user_dump_queue.put([self.host_label, "SocketLogs", self.logger.logs])
        self.logger.warning("Socket of device {} is terminating...".format(self.host_label))
        self.change_state(socket_tools.SOCKET_IS_OVER)

        if self.__request_thread.is_alive():
            self.__request_thread.terminate()

        if self.__receive_classic_thread.is_alive():
            self.__receive_classic_thread.terminate()

        if self.__receive_quantum_thread.is_alive():
            self.__receive_quantum_thread.terminate()

        self.__ping_thread.terminate()

    def is_routing_enabled(self):
        return self.socket_settings.is_routing_enabled()

    @property
    def host_device_id(self):
        return self._host_device.device_id

    @property
    def socket_settings(self) -> socket_tools.SocketSettings:
        return self.layer_setting

    @property
    def max_cc_count(self) -> int:
        return self.socket_settings.max_cc_count

    @property
    def max_qc_count(self) -> int:
        return self.socket_settings.max_qc_count

    @property
    def auto_ping(self) -> bool:
        return self.socket_settings.auto_ping

    @property
    def ping_time(self) -> float:
        return self.socket_settings.ping_time

    @property
    def remove_future_package(self) -> bool:
        return self.socket_settings.remove_future_packages

    @property
    def host_device(self):
        return self._host_device

    @property
    def host_label(self) -> str:
        return self._host_device.label

    @property
    def host_request_queue(self):
        return self._host_device.threaded_request_queue

    @property
    def host_uuid(self):
        return self._host_device.uuid

    @property
    def port_manager(self) -> socket_tools.PortManager:
        return self.get_module(socket_tools.PortManager.module_name)

    @property
    def income_classic_queue(self):
        return self.port_manager.classic_receive_queue

    @property
    def income_quantum_queue(self):
        return self.port_manager.quantum_receive_queue

    @property
    def ping_handle_queue(self):
        return self.queue_manager.get_queue(architecture_tools.PING_HANDLE_QUEUE)

    @property
    def ping_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.PING_REQUEST_QUEUE)

    @property
    def sim_request_queue(self):
        return self.queue_manager.get_queue(architecture_tools.SIM_REQUEST_QUEUE)

    @property
    def observer_queue(self):
        return self.queue_manager.get_queue(architecture_tools.OBSERVER_QUEUE)

    @property
    def device_default_app(self):
        return self.host_device.appman.get_application_from(application_tools.DEFAULT_APPLICATION_NAME, _raise=False)