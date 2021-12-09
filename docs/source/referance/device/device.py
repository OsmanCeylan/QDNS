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

from queue import Queue as TQueue
from typing import Optional
import numpy as np
import threading
import time
import uuid

from QDNS.device.network_adapter import NetworkSocket
from QDNS.device.tools.application_manager import ApplicationManager
from QDNS.device.tools import device_tools
from QDNS.device.tools import socket_tools
from QDNS.interactions import request, respond, signal
from QDNS.tools import layer, queue_manager
from QDNS.tools.state_handler import StateHandler
from QDNS.tools.various_tools import TerminatableThread


class Device(layer.Layer):
    def __init__(
            self, label: str, active: bool = True,
            device_settings=device_tools.default_device_settings,
            app_manager_settings=device_tools.default_application_manager_settings,
            socket_settings=socket_tools.default_socket_settings
    ):
        """
        Every node in topology must be a Device.

        Args:
            label: Label of device.
            device_settings: Device setting.
            app_manager_settings: Application manager setting.
            socket_settings: Socket setting.

        Notes:
            Label is not nessesarily be unique in topology,
            but setting them unique better for understanding.
        """

        self._active = active
        self._device_id = device_tools.DeviceIdentification(label=label, use_uuid=True)

        state_handler = StateHandler(
            layer.ID_DEVICE[0], True, *device_tools.device_states,
            GENERAL_STATE_NOT_STARTED=device_tools.DEVICE_NOT_STARTED,
            GENERAL_STATE_IS_RUNNING=device_tools.DEVICE_IS_RUNNING,
            GENERAL_STATE_IS_STOPPED=device_tools.DEVICE_IS_STOPPED,
            GENERAL_STATE_IS_FINISHED=device_tools.DEVICE_IS_FINISHED,
            GENERAL_STATE_IS_TERMINATED=device_tools.DEVICE_IS_TERMINATED,
            GENERAL_STATE_IS_PAUSED=device_tools.DEVICE_IS_PAUSED,
            GENERAL_STATE_MAY_END=device_tools.DEVICE_MAY_END
        )

        super(Device, self).__init__(
            layer.ID_DEVICE, layer.THREAD_LAYER,
            self.label, state_handler=state_handler,
            layer_settings=device_settings
        )

        # Initialize end check thread.
        self._end_check_thread = None

        # Add application manager module.
        self.add_module(ApplicationManager(self, app_manager_settings))

        # Add network socket layer.
        self._network_socket = NetworkSocket(self, socket_settings)

        # Create must layers.
        if self._network_socket.is_routing_enabled():
            self.appman.create_routing_app()
        if not self.otg_device and not self.observe_capability:
            self.appman.create_qkd_app()

        self._logger.info("Device is composed.")

    def prepair_layer(self, sim_request, miner_request, user_dump_queue):
        """
        Prepair device layer, modules and sub-layers for simulation.
        This method should called before simulation by kernel only.

        Args:
            sim_request: Kernel request queue.
            miner_request: Miner request queue.
            user_dump_queue: User dump queue.
        """

        # Check state.
        not_exepted = (
            device_tools.DEVICE_IS_RUNNING,
            device_tools.DEVICE_IS_PAUSED,
        )

        if self.state in not_exepted:
            raise ValueError("Device layer must prepair before simulations start.")

        # Set outside queues.
        self.queue_manager.add_queue(queue_manager.MINER_REQUEST_QUEUE, miner_request)
        self.queue_manager.add_queue(queue_manager.USER_DUMP_QUEUE, user_dump_queue)

        # Set layer queues.
        self.set_threaded_queues(TQueue(), None)
        self.set_state_report_queue(miner_request)

        # Initiazlize end checker thread.
        self._end_check_thread = TerminatableThread(self.check_finalize, daemon=True)

        # Prepair the other modules and layers.
        self._network_socket.prepair_layer(sim_request)
        self.appman.prepair_module()

        for application in self.appman.enabled_application_list:
            application.prepair_layer(sim_request, user_dump_queue)

        self.logger.info("Device is preapaired for simulation with {} application.".format(self.appman.enabled_application_count))

    def run(self):
        """ Runs the device. Only simulation kernel should call this method. """

        # Check if device is active.
        if not self.is_device_active():
            self.logger.warning("Device is not active. This device will not simulate.")
            self.change_state(device_tools.DEVICE_IS_FINISHED)
            return

        # Sleep start after delay.
        time.sleep(self.start_after_delay)

        # Start device.
        self.change_state(device_tools.DEVICE_IS_RUNNING)

        # Start sub-layers.
        self._network_socket.start_socket()
        self.appman.start_applications()

        # Start end checker thread.
        self._end_check_thread.start()

        # Handle interactions in loop.
        start_time = time.time()
        while 1:
            if self.state_handler.is_breakable():
                break

            action = self.threaded_request_queue.get()
            if isinstance(action, signal.SIGNAL):
                self.__handle_signal(action)

            elif isinstance(action, request.REQUEST):
                self.__handle_request(action)

            else:
                raise ValueError("Unrecognized action for device {}. What \"{}\"?".format(self.label, action))

        # Try terminate end checker.
        try:
            self._end_check_thread.terminate()
        except (KeyError, AttributeError):
            pass

        # Handle idle after simulation.
        if self.idle_after_device_ends:
            self.change_state(device_tools.DEVICE_MAY_END)

            end_time = time.time() - start_time
            end_time = np.around(end_time, 4)
            self.logger.warning("Device simulation is idled after {} seconds.".format(end_time))

            self.user_dump_queue.put([self.label, "DeviceLogs", self.logger.logs])
            self.__end_applications_simulation(user_applications=True)

            while 1:
                if self.state_handler.is_stopped():
                    break

                action = self.threaded_request_queue.get()
                if isinstance(action, signal.SIGNAL):
                    self.__handle_signal(action)

                else:
                    raise ValueError("Unrecognized action for device {}. What \"{}\"?".format(self.label, action))
        else:
            self.user_dump_queue.put([self.label, "DeviceLogs", self.logger.logs])

        # Terminate sub-layers.
        self.__end_applications_simulation(all_enabled=True)
        self.__end_socket_simulation()

        end_time = time.time() - start_time
        end_time = np.around(end_time, 4)
        self.logger.warning("Device simulation is ended in {} seconds.".format(end_time))

    def __handle_request(self, request_: request.REQUEST):
        """ Handles incoming request. """

        # Check if request is in right layer.
        if request_.target_id != layer.ID_DEVICE:
            raise ValueError("Exepted device request but got {}.".format(request_.target_id))

        # Device information request.
        if isinstance(request_, request.DeviceInformationRequest):
            di = self.device_id
            if request_.want_respond:
                respond.DeviceInformationRespond(
                    request_.generic_id, 0, di
                ).process(self.appman.get_application_from(request_.spesific_asker, _raise=True).threaded_respond_queue)

        else:
            raise ValueError("Unrecognized request for device {}. What \"{}\"?".format(self.label, request_))

    def __handle_signal(self, signal_: signal.SIGNAL):
        """ Handles incoming signals. """

        # State report.
        if isinstance(signal_, signal.StateReportSignal):
            self.appman.update_application_state(
                self.appman.get_application_from(signal_.source_emiter), signal_.new_state
            )

        # End device.
        elif isinstance(signal_, signal.EndDeviceSignal):
            self.__end_device(device_tools.DEVICE_IS_FINISHED)

        # End device, checker ver.
        elif isinstance(signal_, signal.EndDeviceSignalChVer):
            self.__end_device(signal_.new_state)

        else:
            raise ValueError("Unrecognized signal for device {}. What signal \"{}\"?".format(self.label, signal_))

    def check_finalize(self):
        """ Checks if device can endable in another thread. """

        time.sleep(1)
        while 1:
            excepted_states = (device_tools.DEVICE_IS_RUNNING,)
            if self.state in excepted_states and self.appman.is_device_endable():
                if self.idle_after_device_ends:
                    self.__end_device(device_tools.DEVICE_MAY_END)
                else:
                    self.__end_device(device_tools.DEVICE_IS_FINISHED)
                return
            time.sleep(0.25)

    def __end_device(self, new_state):
        """ Changing and endable state end device simulation. """

        if self.change_state(new_state):
            self.threaded_request_queue.put(signal.EndDeviceSignalChVer(new_state))

    def __end_applications_simulation(
            self, user_applications=False, default_applications=False, all_enabled=False
    ):
        """ Tries to terminate applications of device. """

        if all_enabled:
            self.appman.terminate_all_applications()
            return

        if default_applications:
            for application_label in self.appman.default_apps_dict:
                self.appman.terminate_application(self.appman.default_apps_dict[application_label])

        if user_applications:
            self.appman.terminate_application(*self.appman.user_applications)

    def __end_socket_simulation(self):
        """ Requests socket to terminate. """

        self.ntwk_socket.threaded_request_queue.put(signal.DeviceEndSocketSignal())
        time.sleep(1.0)
        self.ntwk_socket.terminate_socket()

    def create_new_application(
            self, function, *args, label: Optional[str] = None,
            static=None, enabled=None, end_device_if_terminated=None,
            bond_end_with_device=None, delayed_start_time=None
    ):

        """
        Creates new application.

        Args:
            function: Function of application.
            label: Label of application, default is "default".
            static: Setts application static.
            enabled: Setts application enabled.
            end_device_if_terminated: Ends device simulation if application is termiated.
            bond_end_with_device: Ends device simulation if application is finished.
            delayed_start_time: Starts application after delay.

        Examples:
        =================================================
        >>> self.create_new_application("function: bob_run", *args)
        >>> self.create_new_application("function: alice_run", *args, label="alice_app")
        >>> self.create_new_application("function: bob_run", *args, static=True)
        >>> self.create_new_application("function: bob_run", *args, enabled=False)

        See QDNS/device/applicaion.Application() for more details.

        Raises:
            ValueError: Same name application in device.

        Return:
            Application or None.
        """

        return self.appman.create_new_application(
            function, *args, label=label, static=static, enabled=enabled,
            end_device_if_terminated=end_device_if_terminated,
            bond_end_with_device=bond_end_with_device,
            delayed_start_time=delayed_start_time
        )

    def deactivate(self):
        """
        Deactivates device and causes device will not simulate.
        Call before simulation.
        """

        self._active = False

    def activate(self):
        """
        Activates device and causes device will simulate.
        Call before simulation.
        """

        self._active = True

    def is_device_active(self):
        """ Returns if device is active. """

        return self._active

    @property
    def device_id(self) -> device_tools.DeviceIdentification:
        return self._device_id

    @property
    def uuid(self) -> uuid.UUID:
        return self._device_id.uuid

    @property
    def label(self) -> str:
        return self._device_id.label

    @property
    def appman(self) -> ApplicationManager:
        return self.get_module(ApplicationManager.APP_MAN_NAME)

    @property
    def route_app(self):
        return self.appman.route_app

    @property
    def qkd_app(self):
        return self.appman.qkd_app

    @property
    def ntwk_socket(self) -> NetworkSocket:
        return self._network_socket

    @property
    def device_settings(self) -> device_tools.DeviceSettings:
        return self.layer_setting

    @property
    def otg_device(self) -> bool:
        return self.device_settings.otg_device

    @property
    def observe_capability(self) -> bool:
        return self.device_settings.observe_capability

    @property
    def active(self) -> bool:
        return self._active

    @property
    def idle_after_device_ends(self) -> bool:
        return self.device_settings.idle_after_device_ends

    @property
    def start_after_delay(self) -> float:
        return self.device_settings.start_after_delay

    @property
    def miner_request_queue(self):
        return self.queue_manager.get_queue(queue_manager.MINER_REQUEST_QUEUE)

    @property
    def user_dump_queue(self):
        return self.queue_manager.get_queue(queue_manager.USER_DUMP_QUEUE)

    @property
    def localhost(self):
        return self.appman.localhost_queue

    @property
    def end_check_thread(self) -> threading.Thread:
        return self._end_check_thread


class Observer(Device):
    def __init__(self, label: str):
        """
        Observer OTG device.
        """

        device_setting = device_tools.DeviceSettings(
            otg_device=True, observe_capability=True,
            idle_after_device_ends=True, start_after_delay=0
        )
        application_mananger_setting = device_tools.ApplicationManagerSettings(
            1, enable_localhost=False, disable_user_apps=False
        )
        socket_setting = socket_tools.SocketSettings(
            2, 2,
            auto_ping=False,
            clear_route_cache=False,
            enable_routing=False,
            enable_qkd=False
        )
        super(Observer, self).__init__(
            label, device_settings=device_setting,
            app_manager_settings=application_mananger_setting,
            socket_settings=socket_setting
        )


class Router(Device):
    def __init__(self, label: str):
        """
        Router device.
        """

        device_setting = device_tools.DeviceSettings(
            otg_device=False, observe_capability=True,
            idle_after_device_ends=True, start_after_delay=0
        )
        application_mananger_setting = device_tools.ApplicationManagerSettings(
            0, enable_localhost=False, disable_user_apps=True
        )
        socket_setting = socket_tools.SocketSettings(
            socket_tools.max_avaible_classic_connection,
            socket_tools.max_avaible_quantum_connection,
            auto_ping=False,
            clear_route_cache=True,
            enable_routing=True,
            enable_qkd=False
        )
        super(Router, self).__init__(
            label, device_settings=device_setting,
            app_manager_settings=application_mananger_setting,
            socket_settings=socket_setting
        )


class Node(Device):
    def __init__(self, label: str):
        """
        Node device using the default settings.
        """

        super(Node, self).__init__(label)
