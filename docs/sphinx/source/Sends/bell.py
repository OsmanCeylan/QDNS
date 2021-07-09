"""
The code below contains a send bell pair example::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        send_op = app.send_entangle_pairs(6, 'Bob', routing=True)

        if send_op['exit_code'] < 0:
            print("Cannot send qubits to Bob!")
            return
        else:
            my_pairs = send_op['my_pairs']
            print('Alice pairs: ', my_pairs)


    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_qubits(6, "Alice")

        if waiting['exit_code'] < 0:
            print('Waited for qubits but time expired.')
        else:
            print('Bob pairs: ', waiting['qubits'])


    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node("Alice")
        bob = QDNS.Node("Bob")

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net)


    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice pairs:  ['020025600', '020025700', '020025800', '020025900', '020026000', '020026100']
    Bob pairs:  ['020025601', '020025701', '020025801', '020025901', '020026001', '020026101']
"""


def send_entangle_pairs(count, target, routing=True):
    """
    Sends entangle pairs to node.

    Args:
        count: Count of pairs.
        target: Target node identifier.
        routing: Routing enable flag.

    Returns:
        {exit_code, my_pairs}
    """

    pass