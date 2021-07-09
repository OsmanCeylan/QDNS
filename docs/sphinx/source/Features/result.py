"""
QDNS lets users to put values for end of the simulation. Then combining with the logs simulation results generated::

    import QDNS
    import logging

    def alice_default_app(app: QDNS.Application, *user_args):
        message = ["Hello Bob!", "I hope no one sees the message.", "My secret number is: 45"]
        app.send_classic_data("Bob", message)
        app.put_simulation_result("Alice sents message to Bob.")

    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_package()

        if waiting["exit_code"] < 0:
            print("Bob waited for message but time is out.")
        else:
            app.put_simulation_result(waiting['package'].data)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node('Alice')
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)

        print("Alice dumped: ", res.user_dumpings("Alice", QDNS.DEFAULT_APPLICATION_NAME))
        print("Bob dumped: ", res.user_dumpings("Bob", QDNS.DEFAULT_APPLICATION_NAME))
        print("Simulation Logs: ", res.simulation_logs())
        print("Device Logs: ", res.device_logs("Alice"))

    if __name__ == '__main__':
        main()

.. code-block:: python

    Alice dumped:  Alice sents message to Bob.
    Bob dumped:  ['Hello Bob!', 'I hope no one sees the message.', 'My secret number is: 45']
    Simulation Logs:  07/09/2021, 20:18:05.912981: INFO: Starting backend...
    07/09/2021, 20:18:05.913002: INFO: Dumping devices to processes...
    07/09/2021, 20:18:05.913172: LOG: Kernel changes state to "simulation is running"
    07/09/2021, 20:18:10.420522: LOG: Kernel changes state to "simulation is over"
    07/09/2021, 20:18:10.420767: WARNING: Simulation is ended in 4.507566213607788 seconds. Raw 0.0075719356536865234 seconds.

    Device Logs:  07/09/2021, 20:18:05.907662: DEBUG: Application manager module of device Alice is created.
    07/09/2021, 20:18:05.910140: INFO: Application default_app is created inside of device Alice.
    07/09/2021, 20:18:05.916640: INFO: Application Manager module or device Alice setted 3 threads.
    07/09/2021, 20:18:05.916900: INFO: Device Alice preapaired for simulation with 3 application.
    07/09/2021, 20:18:05.917760: LOG: Alice changes state to "device is running"
    07/09/2021, 20:18:07.920386: LOG: Alice changes state to "device may end"
    07/09/2021, 20:18:10.420767: WARNING: Simulation is ended in 4.507566213607788 seconds. Raw 0.0075719356536865234 seconds.
"""