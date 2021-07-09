"""
Any application on the device can request the key or flush the key::

    def alice_default_app(app: QDNS.Application, *user_args):
        request = app.current_qkd_key()
        print('Key: ', request['key'])
        print('Length: ', request['length'])

        app.flush_qkd_key()
        request = app.current_qkd_key()
        print('Key: ', request['key'])
        print('Length: ', request['length'])

.. code-block:: python

    Key:  [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0]
    Length:  137

    Key: None
    Length: 0

Also QDNS lets users to change default QKD match rates on QKD protocols such as::

    # Use before simulation.
    QDNS.change_bb84_values(goods_fidelity=0.65, sample_fidelity=0.5, sample_divisor=4)
"""


def current_qkd_key():
    """
    Makes current qkd key request to QKD Layer.

    Returns:
        {exit_code, key, lenght}
    """

    pass


def flush_qkd_key():
    """
    Apllication requests to remove key in QKD Layer.

    Returns:
        None.
    """

    pass
