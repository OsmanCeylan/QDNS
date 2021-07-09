"""
Resetting qubits on QNDS are made as follows::

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.allocate_qframe(2)['qubits']
        app.apply_transformation(gates.PauliX(), qubits[0])
        app.apply_transformation(gates.PauliX(), qubits[1])
        app.reset_qubits(qubits)
        print('Results: ', app.measure_qubits(qubits)['results'])

.. code-block:: python

    Results:  [0, 0]
"""