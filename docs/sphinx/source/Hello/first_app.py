"""
Import QDNS and logging modules::

    import QDNS
    import logging

The very basics of a simulation can define as::

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

``We recommend to define devices and simulation objects in a main function.``

Now lets create default application method of device Alice above main function::

    def alice_default_app(app: QDNS.Application, *user_args):
        print("This application is hosted in: ", app.host_label)

        info=app.reveal_socket_information()
        print(info['socket_state'])
        print(info['classic_port_count'])
        print(info['quantum_port_count'])
        print(info['connected_classic_port'])

Default application of Alice will print us current socket information of device.

And this is default application of Bob which will print us current connectivity state::

    def bob_default_app(app: QDNS.Application, *user_args):
        print("This application is hosted in: ", app.host_label)

        info = app.reveal_connectivity_information()
        print(info['classic_targets'])
        print(info['quantum_targets'])


After the simulation ends, it writes something like this to the screen.

.. code-block:: python

    This application is hosted in:  Alice
    "socket up"
    8
    8
    1
    This application is hosted in:  Bob
    ['Alice']
    ['Alice']

    WARNING:qudns:Simulation is ended in 4.506177186965942 seconds. Raw 0.006177663803100586 seconds.

"""