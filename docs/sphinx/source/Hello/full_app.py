"""
Full example of first simulation::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        print("This application is hosted in: ", app.host_label)

        info=app.reveal_socket_information()
        print(info['socket_state'])
        print(info['classic_port_count'])
        print(info['quantum_port_count'])
        print(info['connected_classic_port'])

    def bob_default_app(app: QDNS.Application, *user_args):
        print("This application is hosted in: ", app.host_label)

        info = app.reveal_connectivity_information()
        print(info['classic_targets'])
        print(info['quantum_targets'])

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node("Alice")
        bob = QDNS.Node("Bob")

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        sim.simulate(net)

    if __name__ == '__main__':
        main()
"""