"""
QDNS also allows users to capture traffic on observer devices. Thus, the listener can filter the traffic.
In the example below, Alice sends a message to Bob, but Eve drops this packet::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        app.sleep(0.1)
        message = ["Hello Bob!", "I hope no one sees the message.", "My secret number is: 45"]
        app.send_classic_data("Bob", message)

    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_package()

        if waiting["exit_code"] < 0:
            print("Bob waited for message but time is out.")
        else:
            print("Bob received message: ", waiting['package'].data)

    def eve_default_application(app: QDNS.Application, *user_args):
        # Set eve to grap traffic mode.
        app.listener.set_interrupt(True)
        while True:
            communication = app.listener.get_communication_item()
            if communication is None:
                break
            else:
                app.listener.print_item(communication)

            # Drops Package or Qubits.
            app.listener.drop_item()

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


    Bob waited for message but time is out.
    Eve listening is over.

Eve can release the package or qubits with using \"app.listener.release_item()\" if he wants.
Using the grap method can filter the communication but makes simulation more slower. Also quantum network attacks are still possible even if interrupts does not happen at Eve.
"""