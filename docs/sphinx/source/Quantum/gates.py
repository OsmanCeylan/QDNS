"""
QDNS predefines many gates for users to use.
"QDNS.tools.gates" module must be imported to use transformations on qubit::

    import QDNS.tools.gates as gates
    print(gates.gate_id_to_gate_name)


.. code-block:: python

    {10: 'IDGate', 11: 'RXGate', 12: 'RYGate', 13: 'RZ', 14: 'PauliX', 15: 'PauliY', 16: 'PauliZ', 17: 'SGate', 18: 'TGate', 19: 'HGate', 20: 'Psedo-HGate', 21: 'CRXGate', 22: 'CXGate', 23: 'CRYGate', 24: 'CYGate', 25: 'CRZGate',
    26: 'CYGate', 27: 'CSGate', 28: 'CTGate', 29: 'CHGate', 30: 'IIGate', 31: 'SWAPGate', 32: 'iSWAPGate', 33: 'XXGate', 34: 'YYGate', 35: 'ZZGate', 36: 'MSGate', 37: 'MagicGate', 38: 'CVGate', 39: 'XYGate', 40: 'DCXGate',
    41: 'bSWAPGate', 42: 'QFTGate', 43: 'WGate', 44: 'CCXGate', 45: 'CSWAPGate', 46: 'CCZGate'}

Apply gates on application::

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.allocate_qframe(2)['qubits']
        app.apply_transformation(gates.HGate(), qubits[0])
        app.apply_transformation(gates.CXGate(), qubits[0], qubits[1])
        print('Results: ', app.measure_qubits(qubits)['results'])

.. code-block:: python

    Results:  [1, 1]
"""