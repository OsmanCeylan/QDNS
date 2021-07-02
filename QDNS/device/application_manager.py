"""
## ==============================================##
##  Header of QF/device/application_manager.py   ##
## ==============================================##

## ==============================================##
## Brief                                         ##
## Contains Application Manager                  ##
## ==============================================##
"""

import threading
from queue import Queue as TQueue
from typing import Optional, List, Dict, Union

from QDNS.architecture import signal
from QDNS.device.application import Application
from QDNS.tools.simulation_tools import TerminatableThread
from QDNS.tools import application_tools
from QDNS.tools import device_tools
from QDNS.rtg_apps.routing import RoutingLayer
from QDNS.rtg_apps.qkd import QKDLayer


class ApplicationManager(device_tools.DeviceModule):
    APP_MAN_NAME = "Application Manager"

    def __init__(self, host_device, application_manager_settings: Optional[device_tools.ApplicationManagerSettings] = None):
        """
        Application manager module of a device.
        """

        if application_manager_settings is None:
            application_manager_settings = device_tools.default_application_manager_settings

        super(ApplicationManager, self).__init__(
            self.APP_MAN_NAME, can_disable=False, can_removable=False, can_restartable=False,
            can_pausable=True, no_state_module=True, module_settings=application_manager_settings
        )

        self._host_device = host_device

        self._all_application_list: List[Application] = list()
        self._enabled_application_list: List[Application] = list()
        self._static_application_list: List[Application] = list()
        self._default_apps: Dict[str, Application] = dict()
        self._user_apps: List[Application] = list()

        self._application_states: Dict[Application, str] = dict()
        self._application_thread_dict: Dict[Application, TerminatableThread] = dict()
        self._localhost_queue = None

        self.logger.debug("Application manager module of device {} is created.".format(self.host_label))

    def create_new_application(
            self, function, *args, label: Optional[str] = None,
            static=None, enabled=None, end_device_if_terminated=None,
            bond_end_with_device=None, delayed_start_time=None
    ) -> Application:

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

        if label is None:
            label = application_tools.DEFAULT_APPLICATION_NAME

        if self.is_have_this_application(label):
            raise ValueError("Device {} had application named {}".format(self._host_device, label))

        if self.application_count >= self.max_application_count:
            raise OverflowError("Device {} had maximum application count of {}".format(self.host_label, self.application_count))

        if static is None:
            static = application_tools.default_application_settings.static

        if enabled is None:
            enabled = application_tools.default_application_settings.enabled

        if self.disable_user_apps:
            self.logger.critical("Device {} disables user applications.".format(self.host_label))
            raise KeyError("Device {} disables user applications.".format(self.host_label))

        if end_device_if_terminated is None:
            end_device_if_terminated = application_tools.default_application_settings.end_device_if_terminated

        if delayed_start_time is None:
            delayed_start_time = application_tools.default_application_settings.delayed_start_time

        if bond_end_with_device is None:
            bond_end_with_device = application_tools.default_application_settings.bond_end_with_device

        applicaton_settings = application_tools.ApplicationSettings(
            static=static, enabled=enabled, end_device_if_terminated=end_device_if_terminated,
            bond_end_with_device=bond_end_with_device, delayed_start_time=delayed_start_time
        )
        for_return = Application(label, self.host_device, function, *args, app_settings=applicaton_settings)

        if for_return.is_static():
            self._static_application_list.append(for_return)

        if for_return.is_enabled():
            self._enabled_application_list.append(for_return)

        self._user_apps.append(for_return)
        self._all_application_list.append(for_return)
        self._application_states[for_return] = application_tools.APPLICATION_NOT_STARTED

        self.logger.info("Application {} is created inside of device {}.".format(for_return.label, self.host_label))
        return for_return

    def is_have_this_application(self, item: Union[int, str, Application]) -> bool:
        """
        Checks if application is exist in this device.

        Args:
            item: Unique Identifier of application.

        Item can be int, string, Application.

        Returns:
            True if application found in this device.
            False if applicaion cannot found in this device.
        """

        if isinstance(item, Application):
            for application in self._all_application_list:
                if application == item:
                    return True
            return False

        elif isinstance(item, str):
            for application in self._all_application_list:
                if application.label == item:
                    return True
            return False

        elif isinstance(item, int):
            for i, app in self._all_application_list:
                if i == item:
                    return True
            return False

        else:
            self.logger.warning(
                "Application cannot found with given {}, this may cause errors."
                "Accepted key types are int, str, Application.".format(item)
            )
            return False

    def get_application_from(
            self, item: Union[str, int, Application], _raise: bool = False
    ) -> Union[Application, None]:

        """
        Find and gets application from given list in this device.

        Args:
            item: Unique identifier of application.
            _raise: Raise if cannot found.

        Returns:
            Application or None.

        Raises:
            ValueError if cannot find the application from given key while raise flag active.
        """

        if not self.is_have_this_application(item):
            if _raise:
                raise ValueError("Application {} is not found in this device {}.".format(item, self._host_device.label))
            return None

        elif isinstance(item, str):
            for application in self._all_application_list:
                if application.label == item:
                    return application

        elif isinstance(item, Application):
            return item

        else:
            if _raise:
                raise ValueError("Application {} is not found in this device {}.".format(item, self._host_device.label))
            return None

    def prepair_module(self, from_list=None):
        """
        Prepairs module.
        Defaults enabled application list if from list is None.
        """

        if self.enable_localhost:
            self._localhost_queue = TQueue()

        if from_list is None:
            from_list = self.enabled_application_list
        for application in from_list:
            self._application_thread_dict[application] = TerminatableThread(application.run, daemon=True)
        self.logger.info(
            "Application Manager module or device {} setted {} threads.".format(self.host_label, from_list.__len__())
        )

    def start_applications(self, application: Optional[Application] = None, from_list=None):
        """
        Starts applications.
        ! Threads must be setted before.
        """

        if application is not None:
            try:
                self._application_thread_dict[application].start()
            except KeyError:
                raise KeyError("Application {} is not prepared for simulation.".format(application.label))
            return

        if from_list is None:
            from_list = self.enabled_application_list

        for application in from_list:
            self._application_thread_dict[application].start()

    def update_application_state(self, application: Application, new_state):
        """
        Updates state of application.

        Args:
            application: Application object.
            new_state: New state of application.

        Raises:
            KeyError if application is not found.
        """

        try:
            self._application_states[application] = new_state
        except KeyError:
            raise KeyError("Application {} is not found on device {}".format(application.label, self.host_label))

    def update_application_matched_states(self):
        """
        Updates application states in dict.
        This is needed for tracking terminated applications.
        """

        for app in self.application_states:
            thread = self._application_thread_dict[app]
            if not thread.is_alive() and self._application_states[app] == application_tools.APPLICATION_IS_RUNNING:
                self._application_states[app] = application_tools.APPLICATION_IS_TERMINATED
                self.logger.warning("Application {} of device {} is probably terminated.".format(app.label, self.host_label))
                if app.end_device_if_terminated:
                    signal.EndDeviceSignal(app.label).emit(self.host_device.threaded_request_queue)

            if not thread.is_alive() and self._application_states[app] == application_tools.APPLICATION_IS_PAUSED:
                self._application_states[app] = application_tools.APPLICATION_IS_TERMINATED
                self.logger.warning("Application {} of device {} is probably terminated.".format(app.label, self.host_label))
                signal.EndDeviceSignal(app.label).emit(self.host_device.threaded_request_queue)

    def is_device_endable(self) -> bool:
        """
        Checks application states for if device simulation is endable.
        Returns true if device simulation can enable.
        """

        self.update_application_matched_states()
        for application in self.application_thread_dict:
            if self.application_thread_dict[application].is_alive() and not application.is_static():
                return False
        return True

    def append_application(self, application: Application, _raise=False) -> bool:
        """
        Appends new application to this device.
        Must call before any simulations.
        Append method add application to DEFAULT_APPS list.

        Args:
            application: Application
            _raise: Raise flag.

        Raises:
            ValueError if device had same labeled applicaion.

        Return:
            True if succesess.
        """

        if self.is_have_this_application(application.label):
            if _raise:
                raise ValueError("Device {} had application named {}".format(self._host_device, application.label))
            else:
                return False

        application.change_host_device(self._host_device)
        self._all_application_list.append(application)

        if application.is_static():
            self._static_application_list.append(application)

        if application.is_enabled():
            self._enabled_application_list.append(application)

        self._default_apps[application.label] = application
        self._application_states[application] = application_tools.APP_STATE_IS_NOT_STARTED
        return True

    def create_routing_app(self):
        """
        Creater routing app. No user shall create route app manually.
        """

        if self.get_application_from(RoutingLayer.label) is not None:
            return False

        routing = RoutingLayer(self.host_device)

        self.all_application_list.append(routing)

        if routing.is_enabled():
            self.enabled_application_list.append(routing)

        if routing.is_static():
            self.static_application_list.append(routing)

        self._application_states[routing] = application_tools.APPLICATION_NOT_STARTED
        return True

    def create_qkd_app(self):
        """
        Creater qkd app. No user shall create qkd app manually.
        """

        if self.get_application_from(QKDLayer.label) is not None:
            return False

        qkd = QKDLayer(self.host_device)
        self.all_application_list.append(qkd)

        if qkd.is_enabled():
            self.enabled_application_list.append(qkd)

        if qkd.is_static():
            self.static_application_list.append(qkd)

        self._application_states[qkd] = application_tools.APPLICATION_NOT_STARTED
        return True

    def terminate_application(self, *applications, _raise=False) -> bool:
        """
        Terminates the given application.

        Args:
            applications: Tuple / List of applications.
            _raise: Raise flag.

        Return:
            True if termination successfull.

        Raises:
             KeyError if application not found when raise flag active.
        """

        for application in applications:
            try:
                thread = self._application_thread_dict[application]
                thread.terminate()

            except (KeyError, AttributeError) as e:
                if _raise and isinstance(e, KeyError):
                    raise KeyError("Application {} is not found in app manager.".format(application.label))
                if _raise and isinstance(e, AttributeError):
                    raise AttributeError("Cannot terminate device {} applications this way."
                                         .format(self._host_device))
                return False
        return True

    def terminate_all_applications(self) -> None:
        """ Tries to terminate all applications. """

        self.terminate_application(*self.enabled_application_list)

    @property
    def host_device(self):
        return self._host_device

    @property
    def host_label(self) -> str:
        return self._host_device.label

    @property
    def manager_settings(self) -> device_tools.ApplicationManagerSettings:
        return self.module_settings

    @property
    def max_application_count(self) -> int:
        return self.manager_settings.max_application_count

    @property
    def enable_localhost(self) -> bool:
        return self.manager_settings.enable_localhost

    @property
    def application_count(self) -> int:
        return self._all_application_list.__len__()

    @property
    def all_application_list(self) -> List[Application]:
        return self._all_application_list

    @property
    def enabled_application_list(self) -> List[Application]:
        return self._enabled_application_list

    @property
    def enabled_application_count(self) -> int:
        return self._enabled_application_list.__len__()

    @property
    def static_application_list(self) -> List[Application]:
        return self._static_application_list

    @property
    def default_apps_dict(self) -> Dict[str, Application]:
        return self._default_apps

    @property
    def application_states(self) -> Dict[Application, str]:
        return self._application_states

    @property
    def logger(self):
        """ Application Manager and its Device shares same logger instance. """
        return self._host_device.logger

    @property
    def localhost_queue(self):
        return self._localhost_queue

    @property
    def route_app(self):
        return self.get_application_from(RoutingLayer.label, _raise=False)

    @property
    def qkd_app(self):
        return self.get_application_from(QKDLayer.label, _raise=False)

    @property
    def disable_user_apps(self):
        return self.manager_settings.disable_user_apps

    @property
    def application_thread_dict(self) -> Dict[Application, threading.Thread]:
        return self._application_thread_dict

    @property
    def user_applications(self) -> List[Application]:
        return self._user_apps
