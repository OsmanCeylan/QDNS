Hello QDNS
===============

First Simulation
-----------------------------

Import QDNS and logging modules::

    import QDNS
    import logging
    print(QDNS.__version_string__)

.. code-block:: python

    0.55-stable

In order to run a simulation we need at least the following:

#. Nodes that contain applications to run
#. Network that contain nodes
#. Quantum backend configuration
#. Simulation kernel to run network

Creating Applications on Node
######

First, let's create a node called "Alice"::

    # Alice Node
    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            print("This application is: ", default_app.label)
            print("This application on device: ",

As seen above, node Alice and its default application are created.
Since QDNS allows users to create multi applications on a node, every node must have a default application.
When we simulate the node in the next step, this application will print its name and device on the screen.

Creating the Network
######

Now we need to create a network and add Alice to new network::

    net = QDNS.Network(Alice())

or::

    net = QDNS.Network()
    net.add_device(Alice())


Composing Backend Configuration
######

QDNS supports CIRQ, QISKIT, STIM and SDQS Backends to simulate quantum operations.
In order to make a simulation, we have to choose one of them.
For now, we continue with STIM. In the future, we will have a section that explains backends::

    config = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, {2: 10000})


Simulate Network
#####

For the last step we need to create a simulation and call simulate::

    sim = QDNS.Simulator()
    sim.simulate(net, conf)

After the simulation ends, it writes something like this to the screen.

.. code-block:: python

    This application is:  default_app
    This application on device:  Device Identifier: Alice, 91f8706c-ad6f-4f12-9dab-e83c8749be00

Full Example
-----------------------------

Here is the full hello application::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application, *user_args):
            print("This application is: ", default_app.label)
            print("This application on device: ", default_app.reveal_device_information())

    def main():
        logging.basicConfig(level=logging.WARNING)

        net = QDNS.Network(Alice())

        conf = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, {2: 10000})
        sim = QDNS.Simulator()
        sim.simulate(net, conf)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:STIM backend is prepaired for simulation. Prepairation time: ~0.0002 sec

    This application is:  default_app
    This application on device:  Device Identifier: Alice, e9c1529e-0bab-4fbe-b1a6-4d7dfe09067a

    WARNING:QDNS::Alice:Device simulation is idled after 1.0012 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2525 seconds. Raw time: 0.0048
