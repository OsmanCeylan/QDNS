"""
Initiater node prepairs ghz state and broadcast each of them to connected nodes.
The code below contains a broadcast ghz state example::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        # Charlie < --- Alice --- > Bob
        op = app.broadcast_ghz_state()

        if op['exit_code'] < 0:
            print('Broadcasting GHZ state is failed!')
        else:
            print('Alice qubit: ', op['my_qubit'])

    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_qubit()

        if waiting['exit_code'] < 0:
            print('Waited for qubit but time is out!')
        else:
            print('Bob qubit: ', waiting['qubit'])

    def charlie_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_qubit()

        if waiting['exit_code'] < 0:
            print('Waited for qubit but time is out!')
        else:
            print('Charlie qubit: ', waiting['qubit'])

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

        sim = QDNS.Simulator()
        res = sim.simulate(net)

    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice qubit:  020038400
    Bob qubit:  020038401
    Charlie qubit:  020038402
"""


def broadcast_ghz_state():
    """
    Broadcasts ghz state to quantum connected nodes.

    Returns:
        {exit_code, my_qubit}
    """