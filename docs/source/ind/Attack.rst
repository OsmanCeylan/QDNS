Eavesdropping
===============

QDNS provides user convenience to run network attacks. By routing ping packets, observer devices can easily infiltrate the network.
QDNS tries to abstracts the complexity of observe process and lets users to focus application.

Undetected Observer
-----------------------------
In the example below there is an observer between Alice and Bob::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            connection_info = default_app.reveal_connectivity_information()
            print("Alice Conn: ", connection_info)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            connection_info = default_app.reveal_connectivity_information()
            print("Bob Conn: ", connection_info)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()
        eve = QDNS.Observer("Eve")

        net = QDNS.Network(alice, bob, eve)

        # Add eve between them.
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        frames = {2: {1:1}}
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice Conn:
    Classic UUIDs: ['XLITMGL21EOM1ONR']
    Quantum UUIDs: ['QLVPYP5NS0MA8UXH']
    Classic Targets: ['Bob']
    Quantum Targets: ['Bob']
    Communication State: True

    Bob Conn:
    Classic UUIDs: ['WMI16GBB1JJO6D47']
    Quantum UUIDs: ['86WV8DZT4RUGO4O8']
    Classic Targets: ['Alice']
    Quantum Targets: ['Alice']
    Communication State: True

As can be seen above, Alice and Bob cannot detect Eve.

Observer Application
-----------------------------

Observer device can have only one application, the default application.
But still can access all traffic on its device regardless of destination application of package.
An observer device can defined as following::

    class Eve(QDNS.Observer):
        def __init__(self):
            super().__init__("Eve")
            self.create_new_application(self.eve_app, static=True)

        @staticmethod
        def eve_app(app: QDNS.Application, *user_args):
            # Listens the traffic on Eve node in loop.
            while True:
                communication = app.listener.get_communication_item()

                if communication is None:
                    break

                # Do whatever you want there about item.
                else:
                    app.listener.print_item(communication)

            print("Eve listening is over.")

The following example shows a use case::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            message = "Hello Bob! I hope no one will read this message."

            # Send message to Bob.
            default_app.send_classic_data("Bob", message)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            package = default_app.wait_next_package()

            print("Bob prints: ", package.data)

    class Eve(QDNS.Observer):
        def __init__(self):
            super().__init__("Eve")
            self.create_new_application(self.eve_app, static=True)

        @staticmethod
        def eve_app(app: QDNS.Application, *user_args):
            while True:
                communication = app.listener.get_communication_item()

                if communication is None:
                    break
                else:
                    app.listener.print_item(communication)
            print("Eve listening is over.")

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()
        eve = QDNS.Observer("Eve")

        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        frames = {2: {1:1}}
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.1115 sec

    ---------------
    Traffic on device:  Eve
    TYPE: CLASSIC DATA
    SENDER:  Alice
    RECEIVER:  Bob
    APP Label:  default_app
    Broadcast:  False
    Data:  "Hello Bob! I hope no one will read this message."

    Bob prints:  "Hello Bob! I hope no one will read this message."

    WARNING:QDNS::Alice:Device simulation is idled after 1.0013 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0019 seconds.
    WARNING:QDNS::Eve:Device simulation is idled after 1.0018 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.5033 seconds. Real raw time: 0.0086


Grabbing the Traffic
-----------------------------

QDNS also allows users to capture traffic on observer devices. Thus, the listener can filter the traffic.
In the example below, Alice sends a message and qubit to Bob but Eve will block qubit with using
:any:`app.listener.set_interrupt(True)`::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application):
            message = "Hello Bob! I hope no one will read this message."

            # Send message to Bob.
            default_app.send_classic_data("Bob", message)

            # Send bob a qubit.
            qubit = default_app.allocate_qubit()
            default_app.send_quantum("Bob", qubit)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application):
            # Wait for package.
            package = default_app.wait_next_package()

            if package is None:
                print("Bob did not received package.")
            else:
                print("Bob prints: ", package.data)

            # Wait for qubit.
            op = default_app.wait_next_qubit()
            if op is None:
                print("Bob did not receive qubit.")
            else:
                print("Qubit: ", op)

    class Eve(QDNS.Observer):
        def __init__(self):
            super().__init__("Eve")
            self.create_new_application(self.eve_app, static=True, delayed_start_time=0)

        @staticmethod
        def eve_app(app: QDNS.Application):
            # Set listener interrupt mode.
            app.listener.set_interrupt(True)

            while True:
                communication = app.listener.get_communication_item()

                if communication is None:
                    break
                else:
                    app.listener.print_item(communication)

                # Releases the packages on traffic.
                # Drops the qubits on traffic.
                if isinstance(communication, QDNS.Package):
                    app.listener.release_item()
                else:
                    app.listener.drop_item()

            print("Eve listening is over.")

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()
        eve = Eve()

        net = QDNS.Network(alice, bob, eve)

        # Add eve between them.
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        frames = {2: {1: 1}}
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    ---------------
    Traffic on device:  Eve
    TYPE: CLASSIC DATA
    SENDER:  Alice
    RECEIVER:  Bob
    APP Label:  default_app
    Broadcast:  False
    Data:  "Hello Bob! I hope no one will read this message."

    Bob prints: "Hello Bob! I hope no one will read this message."

    ---------------
    Traffic on device: Eve

    TYPE: QUANTUM DATA
    SENDER:  Alice
    RECEIVER:  Bob
    APP Label:  default_app
    Broadcast:  False
    Qubits:  ('1020000000',)

    Bob did not receive qubit.

As can seen above, Bob did not receive the qubit because Eve dropped the qubit with using its listener module.
``All devices have listener moudle but only observer devices can use listener module.``
