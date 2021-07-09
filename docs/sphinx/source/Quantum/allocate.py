"""
As expected from a quantum network simulator, QDNS can perform allocate qubit operations with different backends::

    def alice_default_app(app: QDNS.Application, *user_args):

        # STIM backend.
        qubit = app.allocate_qubit()['qubit']
        qubits = app.allocate_qubits(10)['qubits']

        # Cirq and sdqs backend.
        qubits = app.allocate_qframe(2)['qubits']
        qubits = app.allocate_qframes(2, 10)['qubits']

        print('Qubit pointers: ', app.allocated_qubits)

.. code-block:: python

    Qubit pointers: ['000000', '000001', '000002', '000003', '000004', '000005', '000006', '000007', '000008', '000009', '000010', '000011', '000012', '000013', '000014', '000015', '000016', '000017', '000018', '000019', '000020', '000021', '000022',
    '000023', '000024', '000025', '000026', '000027', '000028', '000029', '000030', '000031', '000032']

``allocate_qframe(s) function works as allocate_qubit(s) on STIM.``
"""