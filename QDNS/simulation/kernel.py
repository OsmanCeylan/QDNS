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

import multiprocessing
import threading
import time
import uuid

from typing import Union, Optional

from QDNS.device.device import Device
from QDNS.architecture import request, signal, respond
from QDNS.backend.backend_wrapper import BackendWrapper
from QDNS.networking.network import Network
from QDNS.rtg_apps.routing import RoutingLayer
from QDNS.simulation.miner_controller import MinerController
from QDNS.tools import architecture_tools
from QDNS.tools import simulation_tools
from QDNS.tools import exit_codes


class Kernel(architecture_tools.Layer):
    def __init__(self, miner_settings=None):
        super(Kernel, self).__init__(
            architecture_tools.ID_SIMULATION, architecture_tools.PROCESS_LAYER, "Kernel",
            request_queue=multiprocessing.Queue()
        )

        # Set a state handler to kernel layer.
        state_handler = architecture_tools.StateHandler(
            self.layer_id, False,
            *simulation_tools.simulation_states,
            GENERAL_STATE_NOT_STARTED=simulation_tools.SIMULATION_NOT_STARTED,
            GENERAL_STATE_IS_RUNNING=simulation_tools.SIMULATION_IS_RUNNING,
            GENERAL_STATE_IS_STOPPED=simulation_tools.SIMULATON_IS_STOPPED,
            GENERAL_STATE_IS_FINISHED=simulation_tools.SIMULATION_IS_FINISHED,
            GENERAL_STATE_IS_TERMINATED=simulation_tools.SIMULATON_IS_TERMINATED,
            GENERAL_STATE_IS_PAUSED=simulation_tools.SIMULATION_IS_PAUSED
        )
        self.set_state_handler(state_handler)

        self.set_queues(multiprocessing.Queue(), None)
        self.queue_manager.add_queue(architecture_tools.USER_DUMP_QUEUE, multiprocessing.Queue())

        # Add modules.
        self.add_module(MinerController(self.request_queue, self.user_dump_queue, miner_settings))
        self.add_module(BackendWrapper())

        # Prepair modules.
        self.miner_controller.prepair_module()
        self.backend_wrapper.prepair_module()

        self._running_network: Optional[Network] = None
        self.__end_check_thread = None

    def simulate(self, network: Network, noise_pattern=None, backend=None) -> simulation_tools.SimulationResults:
        """ Simulation is starting here. """

        self.logger.info("Starting backend...")
        self.backend_wrapper.start_module(noise=noise_pattern, backend_type=backend)

        self.logger.info("Dumping devices to processes...")
        for i, dev in enumerate(network.get_all_devices()):
            self.miner_controller.add_device_to_next(dev)

        self._running_network = network
        self.__end_check_thread = threading.Thread(target=self.__end_checker, daemon=True)
        self.__end_check_thread.start()

        start_time = time.time()
        self.change_state(simulation_tools.SIMULATION_IS_RUNNING)
        self.miner_controller.start_all_processes()

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

        self.logger.warning("Simulation is ended in {} seconds. Raw {} seconds.".format(
            time.time() - start_time, time.time() - start_time - 4.50275)
        )

        dump_list = dict()
        dump_list["SimulationLogs"] = self.logger.logs
        while not self.user_dump_queue.empty():
            item = self.user_dump_queue.get()
            if self.get_device(item[0], _raise=False) is not None:
                dev = item[0]
                app = item[1]
                message = [item[i] for i in range(2, item.__len__())]

                try:
                    _ = dump_list[dev]
                except KeyError:
                    dump_list[dev] = dict()

                try:
                    _ = dump_list[dev][app]
                except KeyError:
                    dump_list[dev][app] = list()

                dump_list[dev][app].append(message)

        return simulation_tools.SimulationResults(dump_list)

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
                            architecture_tools.ID_APPLICATION, signal.FlushRouteData(), RoutingLayer.label
                        ).emit(miner.request_queue)
            else:
                raise ValueError("Connection change signal. What{}?".format(signal_.data_(3)))
        else:
            raise ValueError("Unrecognized singal for kernel. What \"{}\"?".format(signal_))

    def __handle_request(self, request_: request.REQUEST):
        """ Handles request. """

        if request_.target_id != architecture_tools.ID_SIMULATION:
            raise AttributeError("Exepted kernel request but got {}.".format(request_.target_id))

        # Find classic route request.
        if isinstance(request_, request.FindClassicRouteRequest):
            start_uuid = self.get_device(request_.start_uuid, _raise=True).uuid
            end_uuid = self.get_device(request_.end_uuid, _raise=True).uuid

            route = self._running_network.get_classic_channel_route(start_uuid, end_uuid)

            if request_.want_respond:
                if route is None:
                    exit_code = exit_codes.FIND_CLASSIC_ROUTE_FAILED[0]
                else:
                    exit_code = exit_codes.FIND_CLASSIC_ROUTE_SUCCESS[0]

                respond.FindClassicRouteRespond(request_.generic_id, exit_code, route).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Find quantum route request.
        elif isinstance(request_, request.FindQuantumRouteRequest):
            start_uuid = self.get_device(request_.start_uuid, _raise=True).uuid
            end_uuid = self.get_device(request_.end_uuid, _raise=True).uuid

            route = self._running_network.get_quantum_channel_route(start_uuid, end_uuid)

            if request_.want_respond:
                if route is None:
                    exit_code = exit_codes.FIND_QUANTUM_ROUTE_FAILED[0]
                else:
                    exit_code = exit_codes.FIND_QUANTUM_ROUTE_SUCCESS[0]

                respond.FindQuantumRouteRespond(request_.generic_id, exit_code, route).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Allocate qubit request.
        elif isinstance(request_, request.AllocateQubitRequest):
            qubit = self.backend_wrapper.allocate_qubit(*request_.args)
            exit_code = exit_codes.ALLOCATE_QUBIT_SUCCESS[0]
            respond.AllocateQubitRespond(request_.generic_id, exit_code, qubit).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qubits request.
        elif isinstance(request_, request.AllocateQubitsRequest):
            qubits = self.backend_wrapper.allocate_qubits(request_.count, *request_.args)
            exit_code = exit_codes.ALLOCATE_QUBIT_SUCCESS[0]
            respond.AllocateQubitsRespond(request_.generic_id, exit_code, qubits).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qframe request.
        elif isinstance(request_, request.AllocateQFrameRequest):
            qubits = self.backend_wrapper.allocate_qframe(request_.frame_size, *request_.args)
            exit_code = exit_codes.ALLOCATE_QUBIT_SUCCESS[0]
            respond.AllocateQFrameRespond(request_.generic_id, exit_code, qubits).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Allocate qframes request.
        elif isinstance(request_, request.AllocateQFramesRequest):
            qubits = self.backend_wrapper.allocate_qframes(request_.frame_size, request_.count, *request_.args)
            exit_code = exit_codes.ALLOCATE_QUBIT_SUCCESS[0]
            respond.AllocateQFramesRespond(request_.generic_id, exit_code, qubits).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Dellocate qubits request.
        elif isinstance(request_, request.DeallocateQubitRequest):
            result = self.backend_wrapper.deallocate_qubits(request_.qubits)
            if request_.want_respond:
                if result:
                    exit_code = exit_codes.DEALLOCATE_QUBIT_SUCCESS[0]
                else:
                    exit_code = exit_codes.DEALLOCATE_QUBIT_FAILED[0]

                respond.DeallocateQubitRespond(request_.generic_id, exit_code).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Extend frame request.
        elif isinstance(request_, request.ExtendQFrameRequest):
            qubit = self.backend_wrapper.extend_circuit(request_.qubit_of_frame)
            exit_code = exit_codes.ALLOCATE_QUBIT_SUCCESS[0]

            respond.ExtendQFrameRespond(request_.generic_id, exit_code, qubit).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Measure qubits request.
        elif isinstance(request_, request.MeasureQubitsRequest):
            results = self.backend_wrapper.measure(request_.qubits, *request_.args)

            # Else program terminates anyway.
            exit_code = exit_codes.MEASURE_QUBIT_SUCCESS[0]

            respond.MeasureQubitsRespond(request_.generic_id, exit_code, results).process(
                self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                    request_.spesific_asker, _raise=True
                ).respond_queue
            )

        # Reset qubits request.
        elif isinstance(request_, request.ResetQubitsRequest):
            results = self.backend_wrapper.reset_qubits(request_.qubits, *request_.args)

            # Else program terminates anyway.
            exit_code = exit_codes.RESET_QUBIT_SUCCESS[0]

            if request_.want_respond:
                respond.ResetQubitsRespond(request_.generic_id, exit_code, results).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply transformation request.
        elif isinstance(request_, request.ApplyTransformationRequest):
            results = self.backend_wrapper.apply_transformation(request_.gate_id, request_.gate_args, request_.qubits)

            # Else program terminates anyway.
            exit_code = exit_codes.RESET_QUBIT_SUCCESS[0]

            if request_.want_respond:
                respond.ApplyTransformationRespond(request_.generic_id, exit_code, results).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Generate epr request.
        elif isinstance(request_, request.GenerateEPRRequest):
            qubits = self.backend_wrapper.generate_epr_pairs(request_.count, *request_.args)

            if qubits is None:
                exit_code = exit_codes.GENERATE_EPR_FAILED[0]
            else:
                exit_code = exit_codes.GENERATE_EPR_SUCCESS[0]

            if request_.want_respond:
                respond.GenerateEPRRespond(request_.generic_id, exit_code, qubits).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Generate ghz request.
        elif isinstance(request_, request.GenerateGHZRequest):
            qubits = self.backend_wrapper.generate_ghz_pair(request_.size, *request_.args)

            if qubits is None:
                exit_code = exit_codes.GENERATE_GHZ_FAILED[0]
            else:
                exit_code = exit_codes.GENERATE_GHZ_SUCCESS[0]

            if request_.want_respond:
                respond.GenerateGHZRespond(request_.generic_id, exit_code, qubits).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply channel errors request.
        elif isinstance(request_, request.ApplyChannelError):
            channel = self._running_network.get_channel(request_.channel_uuid, raise_=True)
            result = self.backend_wrapper.process_channel_error(request_.qubits, channel.percentage)

            if request_.want_respond:
                respond.ApplyChannelErrorRespond(request_.generic_id, 0, result).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        # Apply serial transformation request.
        elif isinstance(request_, request.ApplySerialTransformationsRequest):
            results = self.backend_wrapper.apply_serial_transformations(request_.list_of_gates)

            # Else program terminates anyway.
            exit_code = exit_codes.RESET_QUBIT_SUCCESS[0]

            if request_.want_respond:
                respond.ApplySerialTransformationsRespond(request_.generic_id, exit_code, results).process(
                    self.get_device(request_.asker_uuid, _raise=True).appman.get_application_from(
                        request_.spesific_asker, _raise=True
                    ).respond_queue
                )

        else:
            raise ValueError("Unrecognized request for kernel. What \"{}\"?".format(request_))

    def get_device(self, key: Union[int, str, uuid.UUID], _raise=True) -> Union[Device, None]:
        """
        Finds the device by given key.

        Args:
            key: Device identifier.
            _raise: Raise flag.

        Return:
            Device or None.
        """

        if isinstance(key, int):
            for i, device in enumerate(self._running_network.get_all_devices()):
                if i == key:
                    return device

            if _raise:
                raise ValueError("Device is not found by key {}.".format(key))
            return None

        elif isinstance(key, str):
            for device in self._running_network.get_all_devices():
                if device.label == key or device.uuid == key:
                    return device

            if _raise:
                raise ValueError("Device is not found by key {}.".format(key))
            return None

        elif isinstance(key, uuid.UUID):
            for device in self._running_network.get_all_devices():
                if device.uuid == key:
                    return device

            if _raise:
                raise ValueError("Device is not found by key {}.".format(key))
            return None

        else:
            if _raise:
                raise ValueError("Device cannot found by given type {}.".format(type(key)))
            return None

    def __end_checker(self):
        time.sleep(0.5)
        while 1:
            expected_states = (simulation_tools.SIMULATION_IS_RUNNING, simulation_tools.SIMULATION_IS_PAUSED,)
            if self.state in expected_states:
                if self.miner_controller.is_simulation_endable():
                    self.request_queue.put(signal.EndSimulationSignal())
                    return
            time.sleep(1)

    def __end_simulation(self):
        self.change_state(simulation_tools.SIMULATION_IS_FINISHED)
        self.request_queue.put(signal.EndSimulationSignal())

    @property
    def user_dump_queue(self):
        return self.queue_manager.get_queue(architecture_tools.USER_DUMP_QUEUE)

    @property
    def miner_controller(self) -> MinerController:
        return self.get_module(MinerController.module_name)

    @property
    def backend_wrapper(self) -> BackendWrapper:
        return self.get_module(BackendWrapper.module_name)
