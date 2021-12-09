Hardware Control
===============

Since QDNS designed to do the simulation dynamically, it gaves the user control over all the hardware of device.
Users can make any changes they want on the socket or the host device during the simulation phase.

Some useful socket commands used as below by Alice::

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            # Returns QDNS.SocketInformation
            print(default_app.reveal_socket_information())

            # Returns QDNS.PortInformation
            print(default_app.reveal_port_information(0, search_quantum=True))

            # Returns QDNS.ConnectivityInformation
            print(default_app.reveal_connectivity_information())

            # Open/ close communication.
            default_app.open_communication()
            default_app.close_communication()

            # Activate/ deactivate port.
            default_app.activate_port(0, search_quantum=True)
            default_app.deactivate_port(0, search_quantum=True)

            # Pause/ resume networking.
            default_app.pause_socket()
            default_app.resume_socket()

            # Terminate socket. !No return.
            default_app.terminate_socket()

            # Unconnect channel.
            default_app.unconnect_channel(0, search_quantum=True)

            # Flushes route data on routig layer of device.
            default_app.flush_route_data()

            # Ends host device simulation.
            # Other applications in same device will terminate.
            default_app.end_device_simulation()

Full Example
----------------------

Full example with outputs::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            # Returns QDNS.SocketInformation
            print(default_app.reveal_socket_information())

            # Returns QDNS.PortInformation
            print(default_app.reveal_port_information(0, search_quantum=True))

            # Returns QDNS.ConnectivityInformation
            print(default_app.reveal_connectivity_information())

            # Open/ close communication.
            default_app.open_communication()
            default_app.close_communication()

            # Activate/ deactivate port.
            default_app.activate_port(0, search_quantum=True)
            default_app.deactivate_port(0, search_quantum=True)

            # Pause/ resume networking.
            default_app.pause_socket()
            default_app.resume_socket()

            # Terminate socket. !No return.
            default_app.terminate_socket()

            # Unconnect channel.
            default_app.unconnect_channel(0, search_quantum=True)

            # Flushes route data on routig layer of device.
            default_app.flush_route_data()

            # Ends host device simulation.
            # Other applications in same device will terminate.
            default_app.end_device_simulation()

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application, *user_args):
            default_app.sleep(0.1)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()
        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        frames = {
            2: {
                1: 128,
                2: 64,
                3: 32,
                4: 16
            },

            3: {
                2: 8
            }

        }
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.0993 sec

    Socket state: "socket up"
    Device Identifier: Alice, ebc414f6-7108-4d70-92c1-64dfe68fcf67
    Auto Ping: True
    Ping Time: 2.5
    Enable Routing: True

    Port Manager of Alice
    Classic Port Capacity: 8
    Quantum Port Capacity: 8
    Classic Port Count: 8
    Quantum Port Count: 8
    Connected Classic Port Count: 1
    Connected Quantum Port Count: 1
    Communication State: "communication is up"
    Port used counts: {'C0': 4, 'C1': 0, 'C2': 0, 'C3': 0,
                       'C4': 0, 'C5': 0, 'C6': 0, 'C7': 0,
                       'Q0': 2, 'Q1': 0, 'Q2': 0, 'Q3': 0,
                       'Q4': 0, 'Q5': 0, 'Q6': 0, 'Q7': 0}

    Index: 0
    Type: Classic port type
    Active: True
    Connected: True
    Target: Bob, a42b2541-ecca-40ef-a3e3-f605a1c47244
    Latency: 0.00034

    Classic UUIDs: ['L1MT3GPERSEUA1GF']
    Quantum UUIDs: ['Q448570NC7I1O5VO']
    Classic Targets: ['Bob']
    Quantum Targets: ['Bob']
    Communication State: True

    WARNING:QDNS::Alice::Socket:Socket of device Alice is terminating.