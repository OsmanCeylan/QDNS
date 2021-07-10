"""
In this example, we generate keys with using the QKD protocol. Then Alice sends an encrypted message to Bob::

    import QDNS
    import logging

    class Alice(QDNS.Device):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            protocol = app.run_qkd_protocol("Bob", 256, QDNS.BB84_METHOD)

            if protocol["exit_code"] < 0:
                print("Key generation is failed.")
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
                print("Key generation is failed.")
                return

            key = protocol["key"]
            message = app.wait_next_package()["package"].data
            print("Bob recieved message is: ", message)
            print("Bob decrypts message: ", QDNS.string_decode(key, message))

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = Alice()
        bob = Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

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

    Bob recieved message is:  xQs RPzQ£ª¡¥P¤¤Q¤¤^
    Bob decrypts message:  Hello!Bob! I encrypted this message.
    WARNING:qudns:Simulation is ended in 4.506694078445435 seconds. Raw 0.003496224212646837 seconds.

"""