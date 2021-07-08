"""
Some useful socket commands used as below by Alice::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        print(app.reveal_socket_information())
        print(app.reveal_connection_information(get_uuids=False))
        print(app.reveal_port_information(0, search_classic=True))
        print(app.reveal_connectivity_information())

        # Open/ close communication.
        app.open_communication()
        app.close_communication()

        # Activate/ deactivate port.
        app.activate_port(0, search_quantum=True)
        app.deactivate_port(0, search_quantum=True)

        # Pause/ resume networking.
        app.pause_socket()
        app.resume_socket()

        # Terminate socket. !No return.
        app.terminate_socket()

        # Unconnect channel.
        app.unconnect_channel(0, search_quantum=True)

        # Flushes route data on routig layer of device.
        app.flush_route_data()

        # Ends host device simulation.
        # Other applications in same device will terminate.
        app.end_device_simulation()

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node("Alice")
        bob = QDNS.Node("Bob")

        alice.create_new_application(alice_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net)

    if __name__ == '__main__':
        main()

As can be seen above, an application can control the socket in the device it is in. More about these method can found in Modules.Application
"""