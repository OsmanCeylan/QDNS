"""
Measurements on QNDS are made as follows::

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.allocate_qframe(5)['qubits']

        operation = app.measure_qubits(qubits)
        if operation['exit_code'] < 0:
            print('Measure qubits is failed.')
        else:
            print('Results: ', operation['results'])

        # More simple.
        print('Results: ', app.measure_qubits(qubits)['results'])

        # Non-destructive
        print('Results: ', app.measure_qubits(qubits, True)['results'])

        # Measure in other dimensions. Works on CIRQ
        print('Results: ', app.measure_qubits(qubits, True, 2)['results'])

.. code-block:: python

    Results:  [0, 0, 0, 0, 0]
    Results:  [0, 0, 1, 0, 1]
    Results:  [1, 1, 0, 0, 1]
    Results:  [1, 1, 0, 0, 1]
"""