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

from typing import Optional
import multiprocessing
import threading
import time

from QDNS.backend.tools.config import BackendConfiguration
from QDNS.backend.tools.noise import default_noise_pattern
from QDNS.interactions import request, signal, respond
from QDNS.backend.backend_wrapper import BackendWrapper
from QDNS.networking.network import Network
from QDNS.rtg_apps.routing import RoutingLayer
from QDNS.simulation.controller import MinerController
from QDNS.tools import layer, queue_manager
from QDNS.simulation import tools
from QDNS.tools.state_handler import StateHandler


class Kernel(layer.Layer):
    def __init__(self, process_controller_settings=tools.default_controller_settings):
        """
        Simulation kernel.

        Args:
            process_controller_settings: Process controller setting.
        """

        # Set a state handler to kernel layer.
        state_handler = StateHandler(
            layer.ID_SIMULATION[0], False, *tools.simulation_states,
            GENERAL_STATE_NOT_STARTED=tools.SIMULATION_NOT_STARTED,
            GENERAL_STATE_IS_RUNNING=tools.SIMULATION_IS_RUNNING,
            GENERAL_STATE_IS_STOPPED=tools.SIMULATON_IS_STOPPED,
            GENERAL_STATE_IS_FINISHED=tools.SIMULATION_IS_FINISHED,
            GENERAL_STATE_IS_TERMINATED=tools.SIMULATON_IS_TERMINATED,
            GENERAL_STATE_IS_PAUSED=tools.SIMULATION_IS_PAUSED
        )

        super(Kernel, self).__init__(
            layer.ID_SIMULATION, layer.THREAD_LAYER,
            tools.kernel_layer_label,
            state_handler=state_handler
        )

        # Add and set queues.
        self.set_queues(multiprocessing.Queue(), None)
        self.queue_manager.add_queue(queue_manager.USER_DUMP_QUEUE, multiprocessing.Queue())

        # Add modules.
        self.add_module(MinerController(self.request_queue, self.user_dump_queue, process_controller_settings))
        self.add_module(BackendWrapper())

        self._running_network: Optional[Network] = None
        self.__end_check_thread = None

    def simulate(
            self, network: Network,
            backend_conf: BackendConfiguration,
            noise_pattern=default_noise_pattern,
    ) -> tools.SimulationResults:
        """
        Simulation is starting here.

        Args:
            network: Network to simulate.
            backend_conf: Backend Configuration.
            noise_pattern: Noise pattern for backend.
        """

        self.logger.info(
            "Reserved process counts(devices, backend): {},{}"
            .format(
                self.miner_controller.max_process_count,
                backend_conf.process_count)
        )

        # Start Backend.
        self.backend_wrapper.start_module(backend_conf, noise_pattern)
        self.miner_controller.prepair_module()

        # Dump devices to processes.
        self.logger.info("Dumping devices to processes...")
        for dev in network.get_active_devices():
            self.miner_controller.add_device_to_next(dev)

        # Set running network.
        self._running_network = network

        # Start processes.
        self.miner_controller.start_module()

        # Start end check thread.
        self.__end_check_thread = threading.Thread(target=self.__end_checker, daemon=True)
        self.__end_check_thread.start()

        # Start simulation.
        start_time = time.time()
        self.change_state(tools.SIMULATION_IS_RUNNING)

        # Handle requests and signals in loop.
        while 1:
            if self.state_handler.is_breakable():
                break

            action = self.request_queue.get()
            if isinstance(action, signal.SIGNAL):
                self.__handle_signal(action)

            elif isinstance(action, request.REQUEST):
                self.__handle_request(action)

            else:
                raise ValueError("Unrecognized action for kernel. What \"{}\"?".format(action))

        # Generate simulation result.
        dump_list = dict()
        dump_list["SimulationLogs"] = self.logger.logs
        dump_list["BackendLogs"] = self.backend_wrapper.get_logs()

        times = list()
        while not self.user_dump_queue.empty():
            item = self.user_dump_queue.get()
            if self._running_network.get_device(item[0], _raise=False) is not None:
                dev = item[0]
                app = item[1]
                message = [item[i] for i in range(2, item.__len__())]

                if app == "EndTime":
                    times.append(message[0])
                else:
                    try:
                        _ = dump_list[dev]
                    except KeyError:
                        dump_list[dev] = dict()

                    try:
                        _ = dump_list[dev][app]
                    except KeyError:
                        dump_list[dev][app] = list()

                    dump_list[dev][app].append(message)

        # Find out max time consumed application.
        try:
            max_time = max(times)
            max_time += max_time * 0.05
        except ValueError:
            max_time = "Unknown"

        self.logger.warning("Simulation is ended in {} seconds. Raw time: {}".format(time.time() - start_time, max_time))
        return tools.SimulationResults(dump_list)

    def __handle_signal(self, signal_: signal.SIGNAL):
        """ Handles signals. """

        if isinstance(signal_, signal.StateReportSignal):
            self.miner_controller.update_miner_state(self.miner_controller.get_miner(signal_.source_emiter), signal_.new_state)

        elif isinstance(signal_, signal.EndSimulationSignal):
            self.__end_simulation()

        elif isinstance(signal_, signal.ConnectionChangedSignal):
            if signal_.data_(3) == "DROP":
                changed = False
                for channel in self._running_network.classic_channels:
                    if signal_.data_(2) == channel.uuid or signal_.data_(2) == channel.label:
                        self._running_network.unconnect_channel(signal_.data_(0), signal_.data_(1), classic=True, quantum=False)
                        changed = True
                        break

                if not changed:
                    for channel in self._running_network.quantum_channels:
                        if signal_.data_(2) == channel.uuid or signal_.data_(2) == channel.label:
                            self._running_network.unconnect_channel(signal_.data_(0), signal_.data_(1), classic=False, quantum=True)
                            changed = True
                            break

                if changed:
                    for miner in self.miner_controller.miner_list:
                        signal.DistrabuteAction(
                            layer.ID_APPLICATION, signal.FlushRouteData(), RoutingLayer.label
                        ).emit(miner.request_queue)
            else:
                raise ValueError("Connection change signal. What{}?".format(signal_.data_(3)))
        else:
            raise ValueError("Unrecognized singal for kernel. What \"{}\"?".format(signal_))

    def __handle_request(self, request_: request.REQUEST):
        """ Handles request. """

        if request_.target_id != layer.ID_SIMULATION:
            raise AttributeError("Exepted kernel request but got {}.".format(request_.target_id))

        # Find classic route request.
        if isinstance(request_, request.FindClassicRouteRequest):
            start_uuid = self._running_network.get_device(request_.start_uuid, _raise=True).uuid
            end_uuid = self._running_network.get_device(request_.end_uuid, _raise=True).uuid

            route = self._running_network.get_classic_channel_route(start_uuid, end_uuid)

            if request_.want_respond:
                if route is None:
                    exit_code = -1
                else:
                    exit_code = 0

                respond.FindClassicRouteRespond(request_.generic_id, exit_code, route).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Find quantum route request.
        elif isinstance(request_, request.FindQuantumRouteRequest):
            start_uuid = self._running_network.get_device(request_.start_uuid, _raise=True).uuid
            end_uuid = self._running_network.get_device(request_.end_uuid, _raise=True).uuid

            route = self._running_network.get_quantum_channel_route(start_uuid, end_uuid)

            if request_.want_respond:
                if route is None:
                    exit_code = -1
                else:
                    exit_code = 0

                respond.FindQuantumRouteRespond(request_.generic_id, exit_code, route).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Allocate qubit request.
        elif isinstance(request_, request.AllocateQubitRequest):
            qubit = self.backend_wrapper.allocate_qubits(1, *request_.args)[0]
            exit_code = 0
            respond.AllocateQubitRespond(request_.generic_id, exit_code, qubit).process(
                self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qubits request.
        elif isinstance(request_, request.AllocateQubitsRequest):
            qubits = self.backend_wrapper.allocate_qubits(request_.count, *request_.args)
            exit_code = 0
            respond.AllocateQubitsRespond(request_.generic_id, exit_code, qubits).process(
                self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qframe request.
        elif isinstance(request_, request.AllocateQFrameRequest):
            qubits = self.backend_wrapper.allocate_qframes(request_.frame_size, 1, *request_.args)[0]
            exit_code = 0
            respond.AllocateQFrameRespond(request_.generic_id, exit_code, qubits).process(
                self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qframes request.
        elif isinstance(request_, request.AllocateQFramesRequest):
            qubits = self.backend_wrapper.allocate_qframes(request_.frame_size, request_.count, *request_.args)
            exit_code = 0
            respond.AllocateQFramesRespond(request_.generic_id, exit_code, qubits).process(
                self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Dellocate qubits request.
        elif isinstance(request_, request.DeallocateQubitRequest):
            result = self.backend_wrapper.deallocate_qubits(request_.qubits)
            if request_.want_respond:
                if result:
                    exit_code = 0
                else:
                    exit_code = -1

                respond.DeallocateQubitRespond(request_.generic_id, exit_code).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Measure qubits request.
        elif isinstance(request_, request.MeasureQubitsRequest):
            results = self.backend_wrapper.measure_qubits(request_.qubits, *request_.args)

            # Else program terminates anyway.
            exit_code = 1

            respond.MeasureQubitsRespond(request_.generic_id, exit_code, results).process(
                self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Reset qubits request.
        elif isinstance(request_, request.ResetQubitsRequest):
            results = self.backend_wrapper.reset_qubits(request_.qubits)
            exit_code = 1

            if request_.want_respond:
                respond.ResetQubitsRespond(request_.generic_id, exit_code, results).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply transformation request.
        elif isinstance(request_, request.ApplyTransformationRequest):
            results = self.backend_wrapper.apply_transformation(request_.gate_id, request_.gate_args, request_.qubits)

            # Else program terminates anyway.
            exit_code = 1

            if request_.want_respond:
                respond.ApplyTransformationRespond(request_.generic_id, exit_code, results).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Generate epr request.
        elif isinstance(request_, request.GenerateEPRRequest):
            qubits = self.backend_wrapper.generate_ghz_pair(2, request_.count)

            if qubits is None:
                exit_code = -1
            else:
                exit_code = 0

            if request_.want_respond:
                respond.GenerateEPRRespond(request_.generic_id, exit_code, qubits).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Generate ghz request.
        elif isinstance(request_, request.GenerateGHZRequest):
            qubits = self.backend_wrapper.generate_ghz_pair(request_.size, request_.count)

            if qubits is None:
                exit_code = -1
            else:
                exit_code = 0

            if request_.want_respond:
                respond.GenerateGHZRespond(request_.generic_id, exit_code, qubits).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply channel errors request.
        elif isinstance(request_, request.ApplyChannelError):
            channel = self._running_network.get_channel(request_.channel_uuid, raise_=True)
            result = self.backend_wrapper.process_channel_error(request_.qubits, channel.percentage)

            if request_.want_respond:
                respond.ApplyChannelErrorRespond(request_.generic_id, 0, result).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply serial transformation request.
        elif isinstance(request_, request.ApplySerialTransformationsRequest):
            results = self.backend_wrapper.apply_serial_transformations(request_.list_of_gates)

            # Else program terminates anyway.
            exit_code = 0

            if request_.want_respond:
                respond.ApplySerialTransformationsRespond(request_.generic_id, exit_code, results).process(
                    self._running_network.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        else:
            raise ValueError("Unrecognized request for kernel. What \"{}\"?".format(request_))

    def __end_checker(self):
        """ End checker thread run. """

        time.sleep(1)
        while 1:
            expected_states = (tools.SIMULATION_IS_RUNNING, tools.SIMULATION_IS_PAUSED,)
            if self.state in expected_states:
                if self.miner_controller.is_simulation_endable():
                    self.request_queue.put(signal.EndSimulationSignal())
                    return
            time.sleep(0.25)

    def __end_simulation(self):
        """ Ends simulation (rec). """

        self.change_state(tools.SIMULATION_IS_FINISHED)
        self.request_queue.put(signal.EndSimulationSignal())

    @property
    def user_dump_queue(self):
        return self.queue_manager.get_queue(queue_manager.USER_DUMP_QUEUE)

    @property
    def miner_controller(self) -> MinerController:
        return self.get_module(MinerController.controller_module_name)

    @property
    def backend_wrapper(self) -> BackendWrapper:
        return self.get_module(BackendWrapper.backend_module_label)
