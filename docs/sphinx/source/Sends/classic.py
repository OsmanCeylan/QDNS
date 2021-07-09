"""
The code below contains a classic communication example::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        data = ['Hello Bob!', 'I am Alice!']
        send_op = app.send_classic_data('Bob', data, broadcast=False, routing=True)

        if send_op['exit_code'] < 0:
            print('Sending message to Bob is failed!')


    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_package()

        if waiting['exit_code'] < 0:
            print('Waited for message but time expired.')

        print('Message: ', waiting['package'].data)


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

    Message: ['Hello Bob!', 'I am Alice!']
"""


def wait_next_package(source=None, timeout=None, check_old_packages=True):
    """
    Application waits next package from hinted device.

    Args:
        source: Hinted device identification.
        timeout: Expire time.
        check_old_packages: Checks old packages first.

    Returns:
         {"exit_code", "package"}
    """

    pass
