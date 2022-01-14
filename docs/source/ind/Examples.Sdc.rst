Superdense Coding Example
===============

In this example, we run simple superdense coding example between Alice and Bob.
Lets start with importing libraries::

    import QDNS
    from QDNS import gates

    import logging
    from copy import copy

We need to program Alice::

    class Alice(QDNS.Node):
        def __init__(self, *user_args):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app, *user_args)

        @staticmethod
        def alice_default_app(app: QDNS.Application, *user_args):
            message = user_args[0]
            bt = ''.join('{0:08b}'.format(ord(x), 'b') for x in message)
            qubit_count = int(bt.__len__() / 2)

            app.send_classic_data("Bob", qubit_count)
            my_pairs = app.send_entangle_pairs(qubit_count, "Bob")

            for i in range(qubit_count):
                if bt[2 * i] == '1':
                    app.apply_transformation(gates.PauliX(), my_pairs[i])
                if bt[2 * i + 1] == '1':
                    app.apply_transformation(gates.PauliZ(), my_pairs[i])
            app.send_quantum("Bob", *my_pairs)
            app.put_simulation_result(bt)

We set a message for Alice and give her before any simulation.
Then Alice transforms the message to bits.
With using super dense conding, Alice sends his pairs to Bob.

::

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(app: QDNS.Application):
            qubit_count = app.wait_next_package().data
            my_pairs = app.wait_next_qubits(qubit_count)[0]

            qubits_to_measure = list()
            results = list()

            alice_pairs = app.wait_next_qubits(qubit_count)[0]

            for i in range(qubit_count):
                app.apply_transformation(gates.CXGate(), alice_pairs[i], my_pairs[i])
                app.apply_transformation(gates.HGate(), alice_pairs[i])
                qubits_to_measure.append(copy(my_pairs[i]))
                qubits_to_measure.append(copy(alice_pairs[i]))

            message = ""
            chars = ""
            results = app.measure_qubits(qubits_to_measure)
            for i in range(0, results.__len__(), 8):
                char = ''.join(str(j) for j in results[i: i + 8])
                chars += char
                message += chr(int(char, 2))
            print("Bob prints: ", message)
            app.put_simulation_result(chars)

After receiving the pairs from Alice, Bob aplies gates and measures the qubits.
Bob then rearranges the message and puts the results to the end of the simulation.

::

    def main():
        logging.basicConfig(level=logging.WARNING)

        QDNS.set_respond_expire_time(5.0)
        QDNS.set_qubit_expire_time(5.0)

        message = "Hello Bob! I am Alice. Nice to meet you."
        alice, bob = Alice(message), Bob()
        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob, length=1.0)

        core_count = int(QDNS.core_count / 2)

        frames = {
            2: {
                1: 64,
                2: int(message.__len__() * 4)
            }
        }

        backend_conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, core_count, frames)
        sim = QDNS.Simulator()
        results = sim.simulate(net, backend_conf)

        message = results.user_dumpings(alice.label, QDNS.DEFAULT_APPLICATION_NAME)
        bob_receives = results.user_dumpings(bob.label, QDNS.DEFAULT_APPLICATION_NAME)

        count = 0
        for i in range(bob_receives.__len__()):
            if bob_receives[i] == message[i]:
                count += 1
        print("Match rate: ", count/ bob_receives.__len__())

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.2396 sec

    Bob prints: "H¥olo Âon! I am Aljb%. ^ice to meet you>"

    WARNING:QDNS::Alice:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0019 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2542 seconds. Real raw time: 0.2012

    Match rate:  0.959375

Event through match rate is high, message is kinda unreadable.
Its because every 8 qubits forms a character.
So if one of qubit in a character measured inaccurate, entire character changes based on ASCII coding.