"""
Observer device cannot detected by both sides::

    import QDNS
    import logging


    def alice_default_app(app: QDNS.Application, *user_args):
        info = app.reveal_connection_information()
        print('Alice classic_connections_group: ', info['classic_connections_group'])
        print('Alice quantum_connections_group: ', info['quantum_connections_group'])

    def bob_default_app(app: QDNS.Application, *user_args):
        info = app.reveal_connection_information()
        print('Bob classic_connections_group: ', info['classic_connections_group'])
        print('Bob quantum_connections_group: ', info['quantum_connections_group'])

    def eve_default_application(app: QDNS.Application, *user_args):
        app.sleep(1.0)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node('Alice')
        eve = QDNS.Observer("Eve")
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)
        eve.create_new_application(eve_default_application)

        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)

    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice classic_connections_group: [('AB04VP12DYDDYQ55', 'Bob')]
    Alice quantum_connections_group: [('9H2KP0L7XWZ8GLG7', 'Bob')]

    Bob classic_connections_group: [('3A7RS60DXTKWHJ6C', 'Alice')]
    Bob quantum_connections_group: [('DF1TCJQF59JO23R3', 'Alice')]}
"""