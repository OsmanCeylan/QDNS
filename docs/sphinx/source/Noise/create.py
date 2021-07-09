"""
The following part of code explains how to change the noise pattern before simulation::

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node("Alice")
        bob = QDNS.Node("Bob")
        charlie = QDNS.Node("Charlie")

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)
        charlie.create_new_application(charlie_default_app)

        net = QDNS.Network(alice, bob, charlie)
        net.add_channels(alice, bob)
        net.add_channels(alice, charlie)

        my_noise_pattern = QDNS.NoisePattern(
            0.05, 0.01, 0.002, 0.667,
            sp_channel=QDNS.bit_flip_channel,
            measure_channel=QDNS.depolarisation_channel,
            gate_channel=QDNS.no_noise_channel,
            scramble_channel=QDNS.reset_channel
        )

        sim = QDNS.Simulator()
        res = sim.simulate(net, noise_pattern=my_noise_pattern)
"""