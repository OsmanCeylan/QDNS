"""
## =========================================#
##  Header of QF/rtg_apps/routing.py        #
## =========================================#

## =========================================#
## Brief                                    #
## Contains Routing Application             #
## =========================================#
"""

from copy import deepcopy

from QDNS.device.application import Application
from QDNS.tools import application_tools
from QDNS.architecture import signal, request
from QDNS.tools import architecture_tools

ROUTE_WAIT_SEND_RESPOND = False
ROUTE_REQUEST_TIMEOUT = 4.0


class RoutingLayer(Application):
    label = "Routing"

    def __init__(self, host_device, *args):
        app_settings = application_tools.ApplicationSettings(
            static=True, enabled=True, end_device_if_terminated=False,
            bond_end_with_device=False, delayed_start_time=0.01
        )

        super(RoutingLayer, self).__init__(self.label, host_device, self.routing_run, *args, app_settings=app_settings)

    @staticmethod
    def routing_run(self: Application):
        """ Routing run loop. """

        known_classic_routes = dict()
        known_quantum_routes = dict()

        active_request_packages = dict()
        active_request_qupacks = dict()
        route_timings = list()

        def send_routed_package(route, package):
            route = deepcopy(route)
            route.pop(0)
            package.ip_layer.set_route_data(route)
            self._send_package_request(route[0], package, want_respond=ROUTE_WAIT_SEND_RESPOND)

            if ROUTE_WAIT_SEND_RESPOND:
                resp = self._wait_next_Trespond(timeout=ROUTE_WAIT_SEND_RESPOND)
                if resp is None:
                    self.logger.critical("Route could not get respond from socket.")
                    return

                if resp.exit_code < 0:
                    self.logger.critical("Routing package probably failed.")

        def send_routed_qupack(route, qupack):
            route = deepcopy(route)
            route.pop(0)
            qupack.ip_layer.set_route_data(route)
            self._send_qupack_request(route[0], qupack, want_respond=ROUTE_WAIT_SEND_RESPOND)

            if ROUTE_WAIT_SEND_RESPOND:
                resp = self._wait_next_Trespond(timeout=ROUTE_WAIT_SEND_RESPOND)
                if resp is None:
                    self.logger.critical("Route could not get respond from socket.")
                    return

                if resp.exit_code < 0:
                    self.logger.critical("Routing qupack probably failed.")

        def handle_signal(signal_):
            if isinstance(signal_, signal.FlushRouteData):
                known_quantum_routes.clear()
                known_classic_routes.clear()
                self.logger.debug("Host {} route cache cleared!".format(self.host_label))
            else:
                raise ModuleNotFoundError("Unknown signal is processed. What {}?".format(signal_))

        def handle_request(request_):
            if request_.target_id != architecture_tools.ID_APPLICATION:
                raise AttributeError("Exepted device request but got {}.".format(request_.target_id))

            if isinstance(request_, request.RoutePackageRequest):
                try:
                    the_route = known_classic_routes[request_.target]
                except KeyError:
                    pass
                else:
                    send_routed_package(the_route, request_.package)
                    return

                new_request_time = self.global_time
                new_request = self._find_classic_route_request(self.host_uuid, request_.target, want_respond=True)
                active_request_packages[new_request.generic_id] = request_.package
                resp = self._wait_next_Mrespond(timeout=ROUTE_REQUEST_TIMEOUT)

                if resp is None:
                    self.logger.error("Kernel is down or simulation run so slow. Route find failed.")
                    return

                route_timings.append(self.global_time - new_request_time)
                if resp.exit_code < 0:
                    self.logger.warning("There is no classical route with {}.".format(request_.target))
                    return

                route = resp.route
                if route.__len__() <= 1:
                    self.logger.critical("Routing encontered an length error.")
                    return

                req_ = self._find_active_request(request_id=resp.generic_id)
                if req_ is None:
                    self.logger.critical("Routing request is missing.")
                    return
                self._delete_from_active_request(request_id=req_.generic_id)

                try:
                    package = active_request_packages[resp.generic_id]
                except KeyError:
                    self.logger.critical("Routing package is missing from dict.")
                    return
                else:
                    known_classic_routes[request_.target] = route
                    send_routed_package(route, package)

            elif isinstance(request_, request.RouteQupackRequest):
                try:
                    the_route = known_quantum_routes[request_.target]
                except KeyError:
                    pass
                else:
                    send_routed_qupack(the_route, request_.qupack)
                    return

                new_request_time = self.global_time
                new_request = self._find_quantum_route_request(self.host_uuid, request_.target, want_respond=True)
                active_request_qupacks[new_request.generic_id] = request_.qupack
                resp = self._wait_next_Mrespond(timeout=ROUTE_REQUEST_TIMEOUT)

                if resp is None:
                    self.logger.error("Kernel is down or simulation run so slow. Route find failed.")
                    return

                route_timings.append(self.global_time - new_request_time)
                if resp.exit_code < 0:
                    self.logger.warning("There is no quantum route with {}.".format(request_.target))
                    return

                route = resp.route
                if route.__len__() <= 1:
                    self.logger.critical("Routing encontered an length error.")
                    return

                req_ = self._find_active_request(request_id=resp.generic_id)
                if req_ is None:
                    self.logger.critical("Routing request is missing.")
                    return
                self._delete_from_active_request(request_id=req_.generic_id)

                try:
                    qupack = active_request_qupacks[resp.generic_id]
                except KeyError:
                    self.logger.critical("Routing qupack is missing from dict.")
                    return
                else:
                    known_quantum_routes[request_.target] = route
                    send_routed_qupack(route, qupack)
            else:
                raise ValueError("Unrecognized request for {}. What \"{}\"?".format(self.label, request_))

        while 1:
            action = self.threaded_request_queue.get()

            if isinstance(action, signal.SIGNAL):
                handle_signal(action)

            elif isinstance(action, request.REQUEST):
                handle_request(action)

            else:
                raise ValueError("Unrecognized action for {}. What \"{}\"?".format(self.label, action))
