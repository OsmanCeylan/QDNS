"""
Generating key using QKD layer can be seen in the example below::

    import QDNS
    import logging


    def alice_default_app(app: QDNS.Application, *user_args):
        protocol = app.run_qkd_protocol('Bob', 256, QDNS.BB84_METHOD)  #Also supports E91 Method.

        if protocol['exit_code'] < 0:
            print('Generating key is failed.')
        else:
            print(app.host_label)
            print('Key: ', protocol['key'])
            print('Length: ', protocol['length'])


    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_qkd()

        if waiting['exit_code'] < 0:
            print('Generating key is failed.')
        else:
            print(app.host_label)
            print('Key: ', waiting['key'])
            print('Length: ', waiting['length'])


    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node('Alice')
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)


    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice
    Key:  [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0]
    Length:  137

    Bob
    Key:  [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0]
    Length:  137
    DEBUG:qudns:Device Alice::QKD verification success. Passed time: 0.011062591552734375.

``Generated keys can be used device-wide.``

QDNS also provides basic string encode and string decode methods suitable with these keys.
"""


def run_qkd_protocol(target_device, key_lenght, method):
    """
    Makes qkd protocol request to application.

    Args:
        target_device: Identitier of device.
        key_lenght: Key length.
        method: QKD method.

    Returns:
        {exit_code, key, lenght}
    """

    pass


def wait_qkd(source=None):
    """
    Apllication waits QKD from source.

    Args:
        source: Initiater device identifier.

    Returns:
        {exit_code, key, lenght}
    """


    pass
