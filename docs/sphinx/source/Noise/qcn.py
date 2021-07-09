"""
QDNS uses 1680 nanometer Rayleigh scattering on fibre cable formula to calculate the error rate in channel.
But this formula is can be changed easily before simulation::

    def my_channel_error_rate_calculator(length: float):
        ...
        ...
        ...
        return rate

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node('Alice')
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        QDNS.change_default_altitude_formula(my_channel_error_rate_calculator)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net)
"""