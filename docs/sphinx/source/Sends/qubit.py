"""
The code below contains a send qubits example::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.allocate_qframe(2)['qubits']
        send_op = app.send_quantum('Bob', *qubits, routing=True)

        if send_op['exit_code'] < 0:
            print('Sending qubits to Bob is failed!')


    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_qubits(2)

        if waiting['exit_code'] < 0:
            print('Waited for qubits but time is out.')
        else:
            qubits = waiting['qubits']
            count = waiting['count']

            print('Qubits: ', qubits, 'Count: ', count)


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

    Qubits: ['000000', '000001'] Count: 2
"""


def wait_next_qubits(count, source=None, timeout=None, check_old_qubits=True):
    """
    Application waits qubits from hinted device.

    Args:
        count: Qubit count.
        source: Hinted device.
        timeout: Expire time.
        check_old_qubits: Check old unprocessed qubits..

    Returns:
         {"exit_code", "qubits", "count"}
    """

    pass