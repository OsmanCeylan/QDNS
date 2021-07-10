"""
We will rerun the same example as before. But in this example, we have an listener who tries to attack QKD protocol::

    import QDNS
    import logging


    class Alice(QDNS.Device):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            app.sleep(0.2)
            protocol = app.run_qkd_protocol("Bob", 256, QDNS.BB84_METHOD)

            if protocol["exit_code"] < 0:
                print("Key generation is failed. There can be a listener on the network.")
                return

            key = protocol["key"]
            message = "Hello Bob! I encrypted this message."
            message = QDNS.string_encode(key, message)
            app.send_classic_data("Bob", message)


    class Bob(QDNS.Device):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(app: QDNS.Application, *user_args):
            protocol = app.wait_qkd()

            if protocol["exit_code"] < 0:
                print("Key generation is failed. There can be a listener on the network.")
                return

            key = protocol["key"]
            message = app.wait_next_package()["package"].data
            print("Bob recieved message is: ", message)
            print("Bob decrypts message: ", QDNS.string_decode(key, message))


    class Eve(QDNS.Observer):
        def __init__(self):
            super().__init__("Eve")
            self.create_new_application(self.eve_default_app)

        @staticmethod
        def eve_default_app(app: QDNS.Application, *user_args):
            while True:
                communication = app.listener.get_communication_item(timeout=1.0)
                if communication is None:
                    break
                else:
                    if not isinstance(communication, QDNS.Package):
                        app.measure_qubits(communication.qubits)
            print("Eve listening is over.")


    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = Alice()
        bob = Bob()
        eve = Eve()

        print("This value must be reached for detecting Eve in QKD Protocol: ", QDNS.BB84_SAMPLE_FIDELITY)
        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve, length=10.0)
        net.add_channels(eve, bob, length=10.0)

        frames = {
            1: 256,
            2: 256,
        }

        QDNS.change_default_cirq_qframe_configuretion(frames)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.CIRQ_BACKEND)


    if __name__ == '__main__':
        main()

.. code-block:: python

    ...
    This value must be reached for detecting Eve in QKD Protocol:  0.67
    DEBUG:qudns:#-------------------------------------------------------#
    DEBUG:qudns:Device Alice::QKD: is initiated with 256 length.
    DEBUG:qudns:Device Alice::QKD sending protocol details to Bob.
    DEBUG:qudns:Device Alice::QKD encoding qubits with bases.
    DEBUG:qudns:Device Bob::QKD waiting qubits from Alice
    DEBUG:qudns:Device Alice::QKD sending qubits to target.
    DEBUG:qudns:Device Alice::QKD waiting bases from target.
    DEBUG:qudns:Device Bob::QKD measuring qubits acording to his bases
    DEBUG:qudns:Device Bob::QKD sending bases to source.
    DEBUG:qudns:Device Bob::QKD waiting bases from source.
    DEBUG:qudns:Device Alice::QKD sending bases to target.
    DEBUG:qudns:Device Alice::QKD sending 18 sized samples to target.
    DEBUG:qudns:Device Bob::QKD waiting samples from source.
    DEBUG:qudns:Device Alice::QKD is waiting target's verification.
    DEBUG:qudns:Device Bob::QKD fidelity cannot reached expected value. 0.67>0.5555555555555556. Sending fail message to source.
    DEBUG:qudns:#-------------------------------------------------------#
    ...
    Key generation is failed. There can be a listener on the network.
    Key generation is failed. There can be a listener on the network.
    Eve listening is over.
    ...
    WARNING:qudns:Simulation is ended in 5.514228820800781 seconds. Raw 1.011480251312256 seconds.
"""