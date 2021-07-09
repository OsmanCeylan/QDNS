"""
This method extends the frame of qubit from back by one qubit. Extend function is only effective on Cirq and Sdqs backend::

    def alice_default_app(app: QDNS.Application, *user_args):
        # 2 Qubit Frame --> 3 Qubit Frame
        qubits = app.allocate_qframe(2)['qubits']
        app.extend_qframe(qubits[0])

"""