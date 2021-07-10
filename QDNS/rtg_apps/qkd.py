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

import threading
import numpy as np

from QDNS.architecture import signal, request, respond
from QDNS.device.application import Application
from QDNS.tools import application_tools
from QDNS.tools import architecture_tools
from QDNS.tools import exit_codes
from QDNS.tools import gates

BB84_METHOD = "BB84 QKD METHOD"
E91_METHOD = "E91 QKD METHOD"

BB84_GOODS_FIDELITY = 0.44
BB84_SAMPLE_FIDELITY = 0.67
BB84_SAMPLE_DIVISOR = 7

E91_SAMPLE_FIDELITY = 0.67
E91_SAMPLE_DIVISOR = 4

PTOTOCOL_SUCCESS_MESSAGE = ("Protocol is over successfuly.",)
PTOTOCOL_FAILED_MESSAGE = ("Protocol is failed to establish.",)

SENDER_SIDE = "Side of sender"
RECIEVER_SIDE = "Side of receiver"


def change_bb84_values(
        goods_fidelity: float = BB84_GOODS_FIDELITY,
        sample_fidelity: float = BB84_SAMPLE_FIDELITY,
        sample_divisor: int = BB84_SAMPLE_DIVISOR
):
    """
    Changes the values used in known BB84 Protocol

    Args:
        goods_fidelity: 0..1, Good mathup fidelity.
        sample_fidelity: 0..1, Sample mathup fidelity.
        sample_divisor: 1...16 Sample divisor.
    """

    global BB84_GOODS_FIDELITY
    global BB84_SAMPLE_FIDELITY
    global BB84_SAMPLE_DIVISOR

    BB84_GOODS_FIDELITY = goods_fidelity
    BB84_SAMPLE_FIDELITY = sample_fidelity
    BB84_SAMPLE_DIVISOR = sample_divisor


def change_e91_values(
        sample_fidelity: float = E91_SAMPLE_FIDELITY,
        sample_divisor: int = E91_SAMPLE_DIVISOR
):
    """
    Changes the values used in known E91 Protocol

    Args:
        sample_fidelity: 0..1, Sample mathup fidelity.
        sample_divisor: 1...16 Sample divisor.
    """

    global E91_SAMPLE_FIDELITY
    global E91_SAMPLE_DIVISOR

    E91_SAMPLE_FIDELITY = sample_fidelity
    E91_SAMPLE_DIVISOR = sample_divisor


class QKDLayer(Application):
    label = "QkdApp"

    def __init__(self, host_device, *args):
        app_settings = application_tools.ApplicationSettings(
            static=True, enabled=True, end_device_if_terminated=False,
            bond_end_with_device=False, delayed_start_time=0.02
        )

        self._current_key = None
        super(QKDLayer, self).__init__(self.label, host_device, self.qkd_run, *args, app_settings=app_settings)

    def qkd_run(top, self: Application):
        """ QKD run loop. """

        running_threads = list()
        top._current_key = None

        def respond_fail(request_id, app_label, exit_code):
            """
            Responses fail qkd attempts.

            Args:
                request_id: Request ID.
                app_label: Application label.
                exit_code: Exit code from codes.
            """

            app = self.host_device.appman.get_application_from(app_label)
            if app is None:
                self.logger.critical("QKD Layer of device {} cannot find requester.".format(self.host_label))
                return

            respond_ = respond.RunQKDProtocolRespond(request_id, exit_code, None)
            respond_.process(app.threaded_respond_queue)

        def respond_success(request_id, app_label, exit_code):
            """
            Responses success qkd attempts.

            Args:
                request_id: Request ID.
                app_label: Application label.
                exit_code: Exit code from codes.
            """

            app = self.host_device.appman.get_application_from(app_label)
            if app is None:
                self.logger.critical("QKD Layer of device {} cannot find requester.".format(self.host_label))
                return

            respond_ = respond.RunQKDProtocolRespond(request_id, exit_code, top._current_key)
            respond_.process(app.threaded_respond_queue)

        def run_bb84(request_id, app_label, target_device, key_lenght):
            """
            Runner of BB84 Initiater.

            Args:
                request_id: Request ID.
                app_label: Application label.
                target_device: Receiver device.
                key_lenght: Key lenght.
            """

            start_time = self.global_time
            self.logger.debug("#-------------------------------------------------------#")
            self.logger.debug("Device {}::QKD: is initiated with {} length.".format(self.host_label, key_lenght))

            # Allocate qubits count of key_lenght
            respond_ = self.allocate_qframes(1, key_lenght)
            if respond_ is None:
                self.logger.debug("Device {}::QKD is failed to allocate qubits::None.".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD is failed to allocate qubits::<0.".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            qubits = respond_["qubits"]
            if qubits is None:
                self.logger.debug("Device {}::QKD is failed to allocate qubits::None.".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Lets send about qkd protocol deatils first.
            self.logger.debug("Device {}::QKD sending protocol details to {}.".format(self.host_label, target_device))
            respond_ = self.send_classic_data(target_device, [BB84_METHOD, key_lenght], broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD is failed to send protocol details::None.".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD is failed to send protocol details::<0.".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_bits = np.random.choice([0, 1], size=key_lenght)
            alice_bases = np.random.choice(["X", "Z"], size=key_lenght)

            self.logger.debug("Device {}::QKD encoding qubits with bases.".format(self.host_label))
            list_of_gates = list()
            for i in range(key_lenght):
                if alice_bases[i] == "Z":
                    if alice_bits[i] == 0:
                        pass
                    else:
                        list_of_gates.append([gates.PauliX.gate_id, (), (qubits[i],)])

                else:
                    if alice_bits[i] == 0:
                        list_of_gates.append([gates.HGate.gate_id, (), (qubits[i],)])
                    else:
                        list_of_gates.append([gates.PauliX.gate_id, (), (qubits[i],)])
                        list_of_gates.append([gates.HGate.gate_id, (), (qubits[i],)])

            # Apply the gates by serial.
            self.apply_serial_transformations(list_of_gates)

            self.logger.debug("Device {}::QKD sending qubits to target.".format(self.host_label))
            respond_ = self.send_quantum(target_device, *qubits, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending qubits to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending qubits to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Get Bob's bases.
            self.logger.debug("Device {}::QKD waiting bases from target.".format(self.host_label))
            respond_ = self.wait_next_package(target_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive bases from target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive bases from target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_bases = respond_["package"].data

            # Send Alice's bases.
            self.logger.debug("Device {}::QKD sending bases to target.".format(self.host_label))
            respond_ = self.send_classic_data(target_device, alice_bases, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to send bases to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to send bases to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Select good bits.
            goods = list()
            for q in range(key_lenght):
                if alice_bases[q] == bob_bases[q]:
                    goods.append(alice_bits[q])

            # Needs good mathup fidelity.
            if not goods.__len__() / key_lenght > BB84_GOODS_FIDELITY:
                self.logger.debug("Device {}::QKD good bits fidelity not reached. {} < {}".format(
                    self.host_label, goods.__len__() / key_lenght, BB84_GOODS_FIDELITY)
                )
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            alice_sample = list()
            # Alice select random sample
            for i in range(int(goods.__len__() / BB84_SAMPLE_DIVISOR)):
                rand_ = np.random.randint(0, goods.__len__())
                alice_sample.append([rand_, goods[rand_]])

            # Send Alice's sample.
            self.logger.debug("Device {}::QKD sending {} sized samples to target.".format(self.host_label, alice_sample.__len__()))
            respond_ = self.send_classic_data(target_device, alice_sample, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending samples to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending samples to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Get Bob's verification.
            self.logger.debug("Device {}::QKD is waiting target's verification.".format(self.host_label))
            respond_ = self.wait_next_package(target_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive verification from target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive verification from target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_verificication = respond_["package"].data
            if bob_verificication:
                self.logger.debug("Device {}::QKD verification success. Passed time: {}.".format(self.host_label, self.global_time - start_time))
                top._current_key = goods
                respond_success(request_id, app_label, 0)
            else:
                self.logger.debug("Device {}::QKD verification failed. Passed time: {}.".format(self.host_label, self.global_time - start_time))
                top._current_key = None
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])

            self.logger.debug("#-------------------------------------------------------#")

        def run_bb84_reciever(request_id, app_label, source_device, key_length):
            """
            BB84 Receiver runner.

            Args:
                request_id: Request ID.
                app_label: Application label.
                source_device: Source device.
                key_length: Key lenght.
            """

            # Wait for qubits.
            self.logger.debug("Device {}::QKD waiting qubits from {}".format(self.host_label, source_device))
            respond_ = self.wait_next_qubits(key_length, source=source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive qubits from source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive qubits from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_qubits = respond_["qubits"]
            if alice_qubits is None:
                self.logger.debug("Device {}::QKD failed to receive qubits from source::None".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Generate Bob bases.
            self.logger.debug("Device {}::QKD measuring qubits acording to his bases".format(self.host_label))
            bob_bases = np.random.choice(["X", "Z"], size=key_length)
            list_of_gates = list()
            for i in range(key_length):
                if bob_bases[i] == "Z":
                    pass
                else:
                    list_of_gates.append([gates.HGate.gate_id, (), (alice_qubits[i],)])

            # Apply the gates by serial and measure.
            self.apply_serial_transformations(list_of_gates)
            respond_ = self.measure_qubits(alice_qubits)

            # No need to quantum OPs. Deallocate resources.
            self.deallocate_qubits(*alice_qubits)

            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to measuring qubits acording to his bases::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to measuring qubits acording to his bases::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_results = respond_["results"]

            # Send Bob bases.
            self.logger.debug("Device {}::QKD sending bases to source.".format(self.host_label))
            respond_ = self.send_classic_data(source_device, bob_bases, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending bases to source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending bases to source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Get Alice's bases.
            self.logger.debug("Device {}::QKD waiting bases from source.".format(self.host_label))
            respond_ = self.wait_next_package(source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive bases from source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive bases from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_bases = respond_["package"].data

            # Select good bits.
            goods = list()
            for q in range(key_length):
                if alice_bases[q] == bob_bases[q]:
                    goods.append(bob_results[q])

            # Needs good mathup fidelity.
            if not goods.__len__() / key_length > BB84_GOODS_FIDELITY:
                self.logger.debug("Device {}::QKD good bits fidelity not reached. {} < {}".format(
                    self.host_label, goods.__len__() / key_length, BB84_GOODS_FIDELITY)
                )
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            # Get Alice's sample.
            self.logger.debug("Device {}::QKD waiting samples from source.".format(self.host_label))
            respond_ = self.wait_next_package(source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive samples from source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive samples from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_sample = respond_["package"].data

            # Check sample matchup.
            matches = 0
            for sample in alice_sample:
                if goods[sample[0]] == sample[1]:
                    matches += 1

            if matches / alice_sample.__len__() > BB84_SAMPLE_FIDELITY:
                self.logger.debug("Device {}::QKD fidelity reached to {}. Sending success message to source.".format(
                    self.host_label, matches / alice_sample.__len__())
                )
                self.send_classic_data(source_device, PTOTOCOL_SUCCESS_MESSAGE, broadcast=False, routing=True)
                top._current_key = goods
                respond_success(request_id, app_label, 0)
            else:
                self.logger.debug("Device {}::QKD fidelity cannot reached expected value. {}>{}. Sending fail message to source.".format(
                    self.host_label, BB84_SAMPLE_FIDELITY, matches / alice_sample.__len__())
                )
                self.send_classic_data(source_device, PTOTOCOL_FAILED_MESSAGE, broadcast=False, routing=True)
                top._current_key = None
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])

        def run_e91(request_id, app_label, target_device, key_lenght):
            """
            Runner of e91 Initiater.

            Args:
                request_id: Request ID.
                app_label: Application label.
                target_device: Receiver device.
                key_lenght: Key lenght.
            """

            start_time = self.global_time
            self.logger.debug("#-------------------------------------------------------#")
            self.logger.debug("Device {}::QKD: is initiated with {} length.".format(self.host_label, key_lenght))

            # Lets send about qkd protocol deatils first.
            self.logger.debug("Device {}::QKD sending protocol details to target {}".format(self.host_label, target_device))
            respond_ = self.send_classic_data(target_device, [E91_METHOD, key_lenght], broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending protocol details to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending protocol details to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Send entagled pairs to Bob.
            self.logger.debug("Device {}::QKD sending epr to target.".format(self.host_label))
            respond_ = self.send_entangle_pairs(key_lenght, target_device, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending epr to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending epr to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_pairs = respond_["my_pairs"]

            # Alice measurese her pairs.
            self.logger.debug("Device {}::QKD measuring its pairs.".format(self.host_label))
            alice_bases = np.random.choice(["X", "Z"], size=key_lenght)

            list_of_gates = list()
            for i in range(key_lenght):
                if alice_bases[i] == "Z":
                    pass
                else:
                    list_of_gates.append([gates.HGate.gate_id, (), (alice_pairs[i],)])

            # Apply the gates by serial and measure.
            self.apply_serial_transformations(list_of_gates)
            respond_ = self.measure_qubits(alice_pairs)

            # No need to quantum OPs. Deallocate resources.
            self.deallocate_qubits(*alice_pairs)

            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to measuring its pairs::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to measuring its pairs::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_results = respond_["results"]

            # Send Alice's bases.
            self.logger.debug("Device {}::QKD sending its bases.".format(self.host_label))
            respond_ = self.send_classic_data(target_device, alice_bases, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending its bases::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending its bases::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Get Bob's bases.
            self.logger.debug("Device {}::QKD waiting bases from target.".format(self.host_label))
            respond_ = self.wait_next_package(target_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive bases from target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive bases from target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_bases = respond_["package"].data

            # Pick up goods.
            goods = list()
            for i in range(key_lenght):
                if alice_bases[i] == bob_bases[i]:
                    goods.append(alice_results[i])

            # Alice select random sample
            alice_sample = list()
            for i in range(int(goods.__len__() / E91_SAMPLE_DIVISOR)):
                rand_ = np.random.randint(0, goods.__len__())
                alice_sample.append([rand_, goods[rand_]])

            # Send Alice's sample.
            self.logger.debug("Device {}::QKD sending {} sized samples to target.".format(self.host_label, alice_sample.__len__()))
            respond_ = self.send_classic_data(target_device, alice_sample, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending samples to target::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending samples to target::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Get Bob's verification.
            self.logger.debug("Device {}::QKD is waiting target's verification.".format(self.host_label))
            respond_ = self.wait_next_package(target_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive target's verification::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive target's verification::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_verificication = respond_["package"].data
            if bob_verificication:
                self.logger.debug("Device {}::QKD verification success. Passed time: {}.".format(self.host_label, self.global_time - start_time))
                top._current_key = goods
                respond_success(request_id, app_label, 0)
            else:
                self.logger.debug("Device {}::QKD verification failed. Passed time: {}.".format(self.host_label, self.global_time - start_time))
                top._current_key = None
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
            self.logger.debug("#-------------------------------------------------------#")

        def run_e91_receiver(request_id, app_label, source_device, key_length):
            """
            E91 Receiver runner.

            Args:
                request_id: Request ID.
                app_label: Application label.
                source_device: Source device.
                key_length: Key lenght.
            """

            # Wait for qubits.
            self.logger.debug("Device {}::QKD waiting qubits from source {}".format(self.host_label, source_device))
            respond_ = self.wait_next_qubits(key_length, source=source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive qubits from some::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive qubits from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_pairs = respond_["qubits"]
            if bob_pairs is None:
                self.logger.debug("Device {}::QKD failed to receive qubits from source::None".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Bob measures her pairs.
            self.logger.debug("Device {}::QKD measuring its pairs.".format(self.host_label))
            bob_bases = np.random.choice(["X", "Z"], size=key_length)
            list_of_gates = list()
            for i in range(key_length):
                if bob_bases[i] == "Z":
                    pass
                else:
                    list_of_gates.append([gates.HGate.gate_id, (), (bob_pairs[i],)])

            # Apply the gates by serial and measure.
            self.apply_serial_transformations(list_of_gates)
            respond_ = self.measure_qubits(bob_pairs)

            # No need to quantum OPs. Deallocate resources.
            self.deallocate_qubits(*bob_pairs)

            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to measure its pairs::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to measure its pairs::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            bob_results = respond_["results"]

            # Get Alice's bases.
            self.logger.debug("Device {}::QKD waiting bases from source.".format(self.host_label))
            respond_ = self.wait_next_package(source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive bases from source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive bases from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_bases = respond_["package"].data

            # Send Bob bases.
            self.logger.debug("Device {}::QKD sending its bases to source.".format(self.host_label))
            respond_ = self.send_classic_data(source_device, bob_bases, broadcast=False, routing=True)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to sending its bases to source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to sending its bases to source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            # Pick up goods.
            goods = list()
            for i in range(key_length):
                if alice_bases[i] == bob_bases[i]:
                    goods.append(bob_results[i])

            # Get Alice's sample.
            self.logger.debug("Device {}::QKD waiting samples from source.".format(self.host_label))
            respond_ = self.wait_next_package(source_device)
            if respond_ is None:
                self.logger.debug("Device {}::QKD failed to receive samples from source::None".format(self.host_label))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                self.logger.debug("Device {}::QKD failed to receive samples from source::<0".format(self.host_label))
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            alice_sample = respond_["package"].data

            # Check sample matchup.
            matches = 0
            for sample in alice_sample:
                if goods[sample[0]] == sample[1]:
                    matches += 1

            if matches / alice_sample.__len__() > E91_SAMPLE_FIDELITY:
                self.logger.debug("Device {}::QKD fidelity reached to {}. Sending success message to source.".format(
                    self.host_label, matches / alice_sample.__len__())
                )
                self.send_classic_data(source_device, PTOTOCOL_SUCCESS_MESSAGE, broadcast=False, routing=True)
                top._current_key = goods
                respond_success(request_id, app_label, 0)
            else:
                self.logger.debug("Device {}::QKD fidelity cannot reached expected value. {}>{}. Sending fail message to source.".format(
                    self.host_label, E91_SAMPLE_FIDELITY, matches / alice_sample.__len__())
                )
                self.send_classic_data(source_device, PTOTOCOL_FAILED_MESSAGE, broadcast=False, routing=True)
                top._current_key = None
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])

        def run_reciever(request_id, app_label, source_device):
            """
            QKD Protocol receiver handler.

            Args:
                request_id: Request ID.
                app_label: Application label.
                source_device: Source device.
            """

            respond_ = self.wait_next_package(source=source_device)
            if respond_ is None:
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return

            if respond_["exit_code"] < 0:
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            package = respond_["package"]
            if package is None:
                respond_fail(request_id, app_label, respond_["exit_code"])
                return

            source_device = package.sender
            try:
                method = package.data[0]
                lenght = package.data[1]
            except Exception:
                self.logger.critical("There is an error while agreeing qkd protocol with device {}.".format(source_device))
                respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])
                return
            else:
                if method == BB84_METHOD:
                    run_bb84_reciever(request_id, app_label, source_device, lenght)
                elif method == E91_METHOD:
                    run_e91_receiver(request_id, app_label, source_device, lenght)
                else:
                    self.logger.critical("There is an error while agreeing qkd method with device {}.".format(source_device))
                    respond_fail(request_id, app_label, exit_codes.WAIT_RESPOND_TIMEOUT[0])

        def handle_signal(signal_):
            if isinstance(signal_, signal.EndQKDLayer):
                self.logger.warning("QKD Layer of device {} is ended manually.".format(self.host_label))
                return
            else:
                raise ModuleNotFoundError("Unknown signal is processed. What {}?".format(signal_))

        def handle_request(request_):
            # Only applications request to QKD.
            if request_.target_id != architecture_tools.ID_APPLICATION:
                raise AttributeError("Exepted device request but got {}.".format(request_.target_id))

            # Run protocol request.
            if isinstance(request_, request.RunQKDProtocolRequest):
                if request_.side == SENDER_SIDE:
                    if request_.method == BB84_METHOD:
                        thread_ = threading.Thread(target=run_bb84, args=(request_.generic_id, request_.asker_app, request_.target_device, request_.key_lenght))
                        running_threads.append(thread_)
                        thread_.start()

                    elif request_.method == E91_METHOD:
                        thread_ = threading.Thread(target=run_e91, args=(request_.generic_id, request_.asker_app, request_.target_device, request_.key_lenght))
                        running_threads.append(thread_)
                        thread_.start()

                    else:
                        raise ValueError("Unrecognized method for QKD. What \"{}\"?".format(request_.method))
                else:
                    thread_ = threading.Thread(target=run_reciever, args=(request_.generic_id, request_.asker_app, request_.target_device))
                    running_threads.append(thread_)
                    thread_.start()

            # Get current key request.
            elif isinstance(request_, request.CurrentQKDKeyRequest):
                if request_.want_respond:
                    respond_success(request_.generic_id, request_.asker_app, 0)

            # Flush current key requestç
            elif isinstance(request_, request.FlushQKDKey):
                top._current_key = None
                if request_.want_respond:
                    respond_success(request_.generic_id, request_.asker_app, 0)

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
