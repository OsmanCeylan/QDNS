Communication
===============

QDNS offers tools for applications to communicate with each others.

Send Classic Data
-----------------------------

Sending a classic data follows as::

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            message = ["Hello Bob!", 42, (1, 2, 3), "AnyPickable"]
            default_app.send_classic_data("Bob", message, broadcast=False, routing=True)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            package = default_app.wait_next_package()
            print("Bob prints: ", package.data)

            # Also the following paramaters accepted.
            # default_app.wait_next_package(source="Alice")
            # default_app.wait_next_package(timeout=1.0)

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.1001 sec
    Bob prints:  ['Hello Bob!', 42, (1, 2, 3), 'AnyPickable']
    WARNING:QDNS::Alice:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0016 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2541 seconds. Real raw time: 0.0104

Send Qubits
-----------------------------

Sending a qubits follows as::

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            qubits = default_app.allocate_qframe(2)
            default_app.send_quantum("Bob", qubits[0], routing=True)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            port, source, date, qubit = default_app.wait_next_qubit()
            print("Bob prints: ", port, source, date, qubit)

            # Also usable, waits counted qubits.
            # default_app.wait_next_qubits(1)

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.0953 sec
    Bob prints: 0 Alice 2021-07-27 05:15:15.025744 1020012800
    WARNING:QDNS::Alice:Device simulation is idled after 1.0016 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2542 seconds. Real raw time: 0.0055

Send Bell Pairs
-----------------------------

Sending epr pairs follows as::

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            my_pairs = default_app.send_entangle_pairs(16, "Bob", routing=True)
            print("Alice pairs: ", my_pairs)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            my_pairs = default_app.wait_next_qubits(16)
            print("Bob pairs: ", my_pairs[0], "Count: ", my_pairs[1])

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.1007 sec
    Alice pairs: ['1020012800', '1020012900', '1020013000', '1020013100', '1020013200', '1020013300', '1020013400', '1020013500',
                  '1020013600', '1020013700', '1020013800', '1020013900', '1020014000', '1020014100', '1020014200', '1020014300']
    Bob pairs:   ['1020012801', '1020012901', '1020013001', '1020013101', '1020013201', '1020013301', '1020013401', '1020013501',
                  '1020013601', '1020013701', '1020013801', '1020013901', '1020014001', '1020014101', '1020014201', '1020014301']
    Count:  16
    WARNING:QDNS::Alice:Device simulation is idled after 1.002 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2556 seconds. Real raw time: 0.0224


Broadcast GHZ State
-----------------------------

Broadcasting ghz state follows as::

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            size, my_qubit = default_app.broadcast_ghz_state()
            print("GHZ size: ", size, "Alice qubit: ", my_qubit)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            _, _ , _ , qubit = default_app.wait_next_qubit()
            print("Bob qubit: ", qubit)

    class Charlie(QDNS.Node):
        def __init__(self):
            super().__init__("Charlie")
            self.create_new_application(self.charlie_default_app)

        @staticmethod
        def charlie_default_app(default_app: QDNS.Application, *user_args):
            _, _ , _ , qubit = default_app.wait_next_qubit()
            print("Charlie qubit: ", qubit)

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.0938 sec
    GHZ size: 2 Alice qubit: 1020019200
    Bob qubit: 1020019201
    Charlie qubit: 1020019202
    WARNING:QDNS::Alice:Device simulation is idled after 1.0018 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0009 seconds.
    WARNING:QDNS::Charlie:Device simulation is idled after 1.0019 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.505 seconds. Real raw time: 0.0156
