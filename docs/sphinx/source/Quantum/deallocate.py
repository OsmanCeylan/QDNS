"""
In order to use the hardware resources more effectively, the qubits whose work is finished should be released::

    def alice_default_app(app: QDNS.Application, *user_args):
        # Cirq and sdqs backend.
        qubits = app.allocate_qframe(2)['qubits']
        qubits = app.allocate_qframes(2, 10)['qubits']

        app.deallocate_qubits(*qubits)

``This process is especially necessary in circuit simulators such as Cirq and Sdqs backends.``
"""