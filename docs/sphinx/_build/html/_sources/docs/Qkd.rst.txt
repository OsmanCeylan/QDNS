QKD Layer
===============

Each device has an QKD layer. Thanks to this layer, QKD protocol can be run with remote devices in the network.

QKD Methods
-----------------------------

QKD Layer coded to run BB84 and E91 protocols. QDNS allows to change threshold values of protocols.
Default thresholds are::

    print("BB84 Good Bits Fidelity: ", QDNS.BB84_GOODS_FIDELITY)
    print("BB84 Sample Divisor: ", QDNS.BB84_SAMPLE_DIVISOR)
    print("BB84 Sample Fidelity: ", QDNS.BB84_SAMPLE_FIDELITY)
    print("E91 Sample Divisor: ", QDNS.E91_SAMPLE_FIDELITY)
    print("E91 Sample Fidelity: ", QDNS.E91_SAMPLE_DIVISOR)

.. code-block:: python

    BB84 Good Bits Fidelity:  0.45
    BB84 Sample Divisor:  6
    BB84 Sample Fidelity:  0.66
    E91 Sample Divisor:  0.66
    E91 Sample Fidelity:  4


With the following method calls we can change the protocol threshold values::

    # For BB84
    QDNS.change_bb84_values(
        goods_fidelity=0.70,
        sample_fidelity=0.55,
        sample_divisor=8
    )

    # For E91
    QDNS.change_e91_values(
        sample_fidelity=0.55,
        sample_divisor=8
    )


Generating Keys
-----------------------------

Every device have only one QKD layer. So generated keys bounded to the device.
So all applications on the device uses the same key as long as key is not replaced by request.
A key generation between devices as simple as::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            # Lets try to generate with 256 qubits.
            operation = default_app.run_qkd_protocol("Bob", 256, QDNS.BB84_METHOD)

            if operation is None:
                print("QKD is failed to establish.")
                return

            key = operation[0]
            key_len = operation[1]
            print("Alice Key: ", key, "Len: ", key_len)

            key = np.array(key)

            # Basic string encode.
            message = "Hello Bob! This is private message"
            encoded_message = QDNS.string_encode(key, message)

            # Send encoded message to Bob.
            default_app.send_classic_data("Bob", encoded_message)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            # Lets request qkd layer for genertion.
            operation = default_app.wait_qkd()

            if operation is None:
                print("QKD is failed to establish.")
                return

            key = operation[0]
            key_len = operation[1]
            print("Bob Key:", key, "Len: ", key_len)

            # Now wait for encoded message from Alice.
            encoded_message = default_app.wait_next_package().data
            print("Bob recieves encoded: ", encoded_message)

            # Now decode message.
            print("Bob decodes message: ", QDNS.string_decode(key, encoded_message))


    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()
        net = QDNS.Network(alice, bob)

        # Lets add more length between them.
        net.add_channels(alice, bob, length=15.0) #km

        # Set the frames. We need total 256*1 frames.
        core_count = 4
        frames = {
            2: {
                1: int(256 / core_count),
                2: int(128 / core_count),
            }
        }
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, core_count, frames)

        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.1812 sec

    Alice Key:   [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1,
                  0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0,
                  1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                  1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0,
                  0, 1, 1, 1, 1, 0, 0, 0, 1] Len: 117

    Bob Key:     [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1,
                  0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                  1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0,
                  1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0,
                  0, 1, 1, 1, 0, 0, 0, 0, 1] Len: 117

    Bob recieves encoded:  'wqPClcKMwp3Cj1FiwqDCglFAwoXCiMKawpNQwonCpEDCocKSwpnClsKSwpTClUDCncKFwqPCk8KSwofClQ=='
    Bob decodes message:  'Hello!Bob! This is private message'

    WARNING:QDNS::Alice:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2553 seconds. Real raw time: 0.1441



Other Operations
-----------------------------

Any application on the device can request the key or flush the key::

    def alice_default_app(default_app: QDNS.Application, *user_args):
        ...

        default_app.flush_qkd_key()
        # Key lenght will be 0
        print(default_app.current_qkd_key())

        ...

.. code-block:: python

    ([], 0)
