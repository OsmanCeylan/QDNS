"""
Creation and connection of observer device::

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node('Alice')
        eve = QDNS.Observer("eve")
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)
        eve.create_new_application(eve_default_app)

        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)

``A observer device can only have a default application.``
``But they can read all network traffic passing over it, regardless of the application name.``

Eve application loop::

    def eve_default_application(app: QDNS.Application, *user_args):
        while True:
            communication = app.listener.get_communication_item()

            if communication is None:
                break
            else:
                app.listener.print_item(communication)
        print("Eve listening is over.")

Below is an full example of Alice sends classic message and two qubits to Bob while a observer device listening the network::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        message = ["Hello Bob!", "I hope no one sees the message.", "My secret number is: 45"]
        app.send_classic_data("Bob", message)
        app.send_quantum("Bob", *app.allocate_qframe(2)['qubits'])

    def bob_default_app(app: QDNS.Application, *user_args):
        package = app.wait_next_package()["package"]
        qubits = app.wait_next_qubits(2)['qubits']

        print("Bob received message: ", package.data)
        print("Bob recieved the message from: ", package.sender)
        print("Bob received qubits: ", qubits)

    def eve_default_application(app: QDNS.Application, *user_args):
        while True:
            communication = app.listener.get_communication_item()
            if communication is None:
                break
            else:
                app.listener.print_item(communication)
        print("Eve listening is over.")

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node('Alice')
        eve = QDNS.Observer("Eve")
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)
        eve.create_new_application(eve_default_application)

        net = QDNS.Network(alice, bob, eve)
        net.add_channels(alice, eve)
        net.add_channels(eve, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)

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
    Data:  ['Hello Bob!', 'I hope no one sees the message.', 'My secret number is: 45']


    ---------------
    Traffic on device:  Eve
    TYPE: QUANTUM DATA
    SENDER:  Alice
    RECEIVER:  Bob
    APP Label:  default_app
    Broadcast:  False
    Qubits:  ('000000', '000001')


    Bob received message:  ['Hello Bob!', 'I hope no one sees the message.', 'My secret number is: 45']
    Bob recieved the message from:  Alice
    Bob received qubits:  ['000000', '000001']
    Eve listening is over.
"""