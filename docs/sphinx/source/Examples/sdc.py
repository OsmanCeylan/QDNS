"""
In this example, we run simple superdense coding example between Alice and Bob::

    import QDNS
    import logging
    import QDNS.tools.gates as gates

    class Alice(QDNS.Device):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            intended_message = [1, 1]
            my_qubit = app.send_entangle_pairs(1, "Bob")["my_pairs"][0]

            if intended_message[0] == 1:
                app.apply_transformation(gates.PauliX(), my_qubit)
            if intended_message[1] == 1:
                app.apply_transformation(gates.PauliZ(), my_qubit)

            app.send_quantum("Bob", my_qubit)
            app.put_simulation_result(intended_message)

    class Bob(QDNS.Device):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(app: QDNS.Application, *user_args):
            my_qubit = app.wait_next_qubit()["qubit"]
            alice_qubit = app.wait_next_qubit()["qubit"]

            app.apply_transformation(gates.CXGate(), alice_qubit, my_qubit)
            app.apply_transformation(gates.HGate(), alice_qubit)
            result = app.measure_qubits((alice_qubit, my_qubit))["results"]
            app.put_simulation_result(result)

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = Alice()
        bob = Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        frames = {
            1: 16,
            2: 16,
        }

        QDNS.change_default_cirq_qframe_configuretion(frames)

        # Set all noise to 0% or set pattern to no_noise_channel. Both work.
        my_noise = QDNS.NoisePattern(0, 0, 0, 0.67)

        sim = QDNS.Simulator()
        res = sim.simulate(net, noise_pattern=my_noise, backend=QDNS.CIRQ_BACKEND)

        alice_sended = res.user_dumpings("Alice", QDNS.DEFAULT_APPLICATION_NAME)
        bob_measured = res.user_dumpings("Bob", QDNS.DEFAULT_APPLICATION_NAME)

        print("Alice sended: ", alice_sended)
        print("Bob measured: ", bob_measured)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:qudns:Simulation is ended in 4.505201816558838 seconds. Raw 0.0024522933959962856 seconds.
    Alice sended: [1, 1]
    Bob measured: [1, 1]
"""