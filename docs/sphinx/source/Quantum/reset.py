"""
Resetting qubits on QNDS are made as follows::

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.allocate_qframe(5)['qubits']
        app.reset_qubits(qubits):
        print('Results: ', app.measure_qubits(qubits)['results'])

.. code-block:: python

    pass
"""