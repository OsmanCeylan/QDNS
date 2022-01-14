Eavesdropping to QKD Example
===============

We will rerun the same example as before.
But in this example, we have an listener who tries to attack QKD protocol::

    import QDNS
    import logging

We need to program Alice to initiate qkd protocol with Bob::

    class Alice(QDNS.Node):
        def __init__(self, *user_args):
            super().__init__("Alice")
            self.create_new_application(self.default_app, *user_args)

        @staticmethod
        def default_app(app: QDNS.Application, *user_args):
            # Lets use 512 lenght, E91 method.
            protocol = app.run_qkd_protocol("Bob", 512, QDNS.E91_METHOD)

            if protocol is None:
                print("{}: Protocol is failed to establish.".format(app.host_label))
            else:
                print("{}: QKD Key generated!".format(app.host_label))

For Bob, we need to make him wait for protocol::

    class Bob(QDNS.Node):
        def __init__(self, *user_args):
            super().__init__("Bob")
            self.create_new_application(self.default_app, *user_args)

        @staticmethod
        def default_app(app: QDNS.Application, *user_args):
            protocol = app.wait_qkd()

            if protocol is None:
                print("{}: Protocol is failed to establish.".format(app.host_label))
            else:
                print("{}: QKD Key generated!".format(app.host_label))

Now we got eavesdropper Eve. He will measure every qubit he got::

    class Eve(QDNS.Observer):
        def __init__(self):
            super().__init__("Eve")
            # Static flag is not essantial.
            self.create_new_application(self.eve_app, delayed_start_time=0, static=True)

        @staticmethod
        def eve_app(app: QDNS.Application, *user_args):
            # Listens the traffic on Eve node in loop.
            app.listener.set_interrupt(True)

            while True:
                communication = app.listener.get_communication_item()

                # Break if no traffic come.
                if communication is None:
                    break

                # Ignore classic packages.
                if isinstance(communication, QDNS.Package):
                    pass
                else:
                    # Eve secretly measures qubits.
                    app.measure_qubits(communication.qubits)

                # Release packets or qubits we got. We measured qubits.
                app.listener.release_item()

            print("Eve listening is over.")

Here is the main function for this example::

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice, bob, eve = Alice(), Bob(), Eve()
        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve, length=1.0) # km
        net.add_channels(eve, bob, length=1.0)

        conf = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, {2: 2048})

        # Before simulation we can change the qkd protocol default paramters.
        # 0.75 to good match threshold, 16 to sample divisor.
        # Since channel lengths are 2.0km total, this value to except from protocol.

        QDNS.change_e91_values(0.75, 16)

        # Let's ignore state_preapir, measure error, gate errors.
        # Set probabilty to 0, or set channel to QDNS.no_noise_channel.
        QDNS.change_default_noise_pattern(
            QDNS.NoisePattern(
                0.0, 0.0, 0.0,
                sp_channel=QDNS.bit_flip_channel,
                measure_channel=QDNS.bit_and_phase_flip_channel,
                gate_channel=QDNS.phase_flip_channel,
                scramble_channel=QDNS.depolarisation_channel,
            )
        )

        # Also noise pattern can be given to simulate() as paramater or
        # can be setted to default as shown as below.

        sim = QDNS.Simulator()
        results = sim.simulate(net, conf)

    if __name__ == "__main__":
        main()

This results are expected. If you set logging level to debug, you'll see that the match rate is around ~40%.

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:STIM backend is prepaired for simulation. Prepairation time: ~0.0001 sec

    Alice: Protocol is failed to establish.
    Bob: Protocol is failed to establish.

    WARNING:QDNS::Alice:Device simulation is idled after 1.0018 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0018 seconds.
    WARNING:QDNS::Eve:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.5046 seconds. Real raw time: 0.0717
