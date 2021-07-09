"""
Assume a application method that linked to device and ready to simulation like below::

    def alice_default_app(app: QDNS.Application, *user_args):
        pass

Parameter "app" refers to the current application in this scope. And *user_args is the arguments passed from the creation of application by user before the simulation.
Most of the usefull functions is embeded to application class. Some have an easy job, while others do more complex operations. So most operations returns a dictionary with exit code.

Lets try look device, connection and port information on application::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        print(app.reveal_device_information())
        print(app.reveal_connection_information(get_uuids=False))
        print(app.reveal_port_information(0, search_classic=True))

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


.. code-block:: python

    {'exit_code': 20, 'device_label': 'Alice', 'device_unique_id': UUID('d7f341dc-8661-4077-9df0-8495af0556db')}
    {'exit_code': 30, 'classic_connections_group': ['Bob'], 'quantum_connections_group': ['Bob']}
    {'exit_code': 40, 'index': 0, 'type': 'Classic port type', 'active': True, 'connected': True, 'channel_id': 'AS2L82LIWOE59D09', 'target': 'Bob', 'latency': 0.00017

As can be seen above, many methods embedded in the application class returns a dictionary containing an exit code. Positive exit codes means operation is successful.

As we continue, we will describe the important methods in application class.
"""