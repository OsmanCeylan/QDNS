"""
As expected from a quantum network simulator, QDNS can perform allocate qubit operations with different backends::

    def alice_default_app(app: QDNS.Application, *user_args):

        # STIM backend.
        qubit = app.allocate_qubit()['qubit']
        qubits = app.allocate_qubits(10)['qubits']

        # Cirq and sdqs backend.
        qubits = app.allocate_qframe(2)['qubits']
        qubits = app.allocate_qframes(2, 10)['qubits']

``allocate_qframe(s) function works as allocate_qubit(s) on STIM.``
"""