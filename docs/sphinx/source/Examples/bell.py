"""
In this example, we generate bell pairs and send one qubit of pairs to Bob. Then, Alice and Bob measures these qubits and put results to simulation results::

    import QDNS
    import logging

    class Alice(QDNS.Device):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            qubits = app.send_entangle_pairs(128, "Bob", routing=True)["my_pairs"]
            results = app.measure_qubits(qubits)["results"]
            app.put_simulation_result(results)

    class Bob(QDNS.Device):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(app: QDNS.Application, *user_args):
            qubits = app.wait_next_qubits(128)["qubits"]
            results = app.measure_qubits(qubits)["results"]
            app.put_simulation_result(results)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob, length=10.0) # 10km.

        frames = {
            1: 256,
            2: 256
        }

        QDNS.change_default_cirq_qframe_configuretion(frames)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.CIRQ_BACKEND)

        alice_result = res.user_dumpings("Alice", QDNS.DEFAULT_APPLICATION_NAME)
        bob_result = res.user_dumpings("Bob", QDNS.DEFAULT_APPLICATION_NAME)

        match = 0
        for i in range(alice_result.__len__()):
            if alice_result[i] == bob_result[i]:
                match += 1

        print("Measurement results match rate: {}%.".format(match/alice_result.__len__()*100))

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:qudns:Simulation is ended in 4.506298303604126 seconds. Raw 0.0031002109527591415 seconds.
    Measurement results match rate: 84.375%
"""