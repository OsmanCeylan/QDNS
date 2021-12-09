QKD Example
===============

In this example, we generate keys with using the QKD protocol. Then Alice sends an encrypted message to Bob::

    import QDNS
    import logging

After importing the modules, we need to program node Alice::

    class Alice(QDNS.Node):
        def __init__(self, *user_args):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app, *user_args)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            key_length = user_args[0]
            message = user_args[1]

            # Run QKD.
            protocol = app.run_qkd_protocol("Bob", key_length, QDNS.BB84_METHOD)
            if protocol is None:
                print("Protocol is failed to establish.")

            key, length = protocol

            # Encrypte the message.
            encrypted = QDNS.string_encode(key, message)

            # Send classic data.
            app.send_classic_data("Bob", encrypted)

Now we need to program Bob acording the protocol::

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(app: QDNS.Application):
            # Waits QKD prtocol
            protocol = app.wait_qkd()
            if protocol is None:
                print("Protocol is failed to establish.")

            key, length = protocol

            # Wait encrypted message from Alice.
            encrypted = app.wait_next_package().data

            print("Bob recieves encrypted: ", encrypted)
            print("Bob decryptes: ", QDNS.string_decode(key, encrypted))

For the last thing, we need to compose nodes in the network and simulate it::

    def main():
        logging.basicConfig(level=logging.WARNING)

        key_length = 512
        message = "Hello Bob! This is very very private message."

        # Pass the length and message to node Alice.
        alice, bob = Alice(key_length, message), Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob, length=5.0) #km

        # Calculate needed qubits for simulation.
        core_count = int(QDNS.core_count / 2)
        frames = {
            2: {
                1: int(key_length / core_count) + 16,
            }
        }
        backend_conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, core_count, frames)

        sim = QDNS.Simulator()
        results = sim.simulate(net, backend_conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.0799 sec

    Bob recieves encrypted:  wqPClcKMwpzCj1Biwp_CglFAwoXCiMKawpNRwonCpEDCp8KFwqPCmVHClsKVwpLCqkDCocKSwpnClsKSwpTClkDCncKFwqPCk8KRwofClk4=
    Bob decryptes: "Hello Bob! This!is very verz prhvate message."

    WARNING:QDNS::Alice:Device simulation is idled after 1.0018 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0019 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.5054 seconds. Real raw time: 0.3187
