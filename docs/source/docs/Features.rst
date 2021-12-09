Result
===============

QDNS presents a simulation result object to end of simulation.
This result object contains all user data dumpings and all internal logging.

Dump User Data
##############

QDNS lets users to put values for end of the simulation::

    import QDNS
    import logging

    class Alice(QDNS.Node):
        def __init__(self):
            super().__init__("Alice")
            self.create_new_application(self.alice_default_app)

        @staticmethod
        def alice_default_app(default_app: QDNS.Application):
            # Generate epr wuth Bob.
            my_pairs = default_app.send_entangle_pairs(10, "Bob")
            result = default_app.measure_qubits(my_pairs)

            # Put results to end of simulation.
            default_app.put_simulation_result(result)

    class Bob(QDNS.Node):
        def __init__(self):
            super().__init__("Bob")
            self.create_new_application(self.bob_default_app)

        @staticmethod
        def bob_default_app(default_app: QDNS.Application):
            my_pairs = default_app.wait_next_qubits(10)[0]
            result = default_app.measure_qubits(my_pairs)

            # Put results to end of simulation.
            default_app.put_simulation_result(result)

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        frames = {2: {2: 16}}
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 4, frames)

        sim = QDNS.Simulator()
        sim_results = sim.simulate(net, conf)

        alice_res = sim_results.user_dumpings("Alice", QDNS.DEFAULT_APPLICATION_NAME)
        bob_res = sim_results.user_dumpings("Alice", QDNS.DEFAULT_APPLICATION_NAME)

        print("Alice measured: ", alice_res)
        print("Bob measured: ", bob_res)

    if __name__ == '__main__':
        main()

.. code-block:: python

    WARNING:QDNS::Kernel::Backend:CIRQ backend is prepaired for simulation. Prepairation time: ~0.0381 sec
    WARNING:QDNS::Alice:Device simulation is idled after 1.0025 seconds.
    WARNING:QDNS::Bob:Device simulation is idled after 1.0017 seconds.
    WARNING:QDNS::Kernel:Simulation is ended in 1.2543 seconds. Real raw time: 0.0111

    Alice measured:  [1. 0. 1. 1. 0. 0. 0. 1. 0. 0.]
    Bob measured:  [1. 0. 1. 1. 0. 0. 0. 1. 0. 0.]

Internal Logging
##############

QDNS also holds a special logging in the integral parts of framework.
This internal logging settings can be changed before simulation:

.. code-block:: python

    QDNS.change_logger_name("QDNS")
    QDNS.change_logger_format("%H:%M:%S.%f")
    QDNS.change_default_logger_level(logging.DEBUG)

Now we run the same exapmle in the previous section.
But this time we add some lines in the main function::

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = Alice()
        bob = Bob()

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        frames = {2: {2: 16}}
        conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 4, frames)

        sim = QDNS.Simulator()
        sim_results = sim.simulate(net, conf)

        print("Simulation Logs: ")
        print(sim_results.simulation_logs())

        print("Backend Logs: ")
        print(sim_results.backend_logs())

        print("Alice Device Logs: ")
        print(sim_results.device_logs("Alice"))

        print("Alice Default Application Logs: ")
        print(sim_results.application_logs("Alice", QDNS.DEFAULT_APPLICATION_NAME))

.. code-block:: python

    Simulation Logs:
    23:49:59.484488: Kernel | INFO: Reserved process counts(devices, backend): 3,4
    23:49:59.526788: Kernel | INFO: Dumping devices to processes...
    23:49:59.544541: Kernel | LOG: :State: "simulation is not started" ---> "simulation is running"
    23:50:01.047818: Kernel | LOG: :State: "simulation is running" ---> "simulation is over"

    Backend Logs:
    23:49:59.524106: Kernel::Backend | WARNING: CIRQ backend is prepaired for simulation. Prepairation time: ~0.0395 sec
    23:49:59.745018: Kernel::Backend | DEBUG: Generate GHZ Pairs (10x2) -> [1020000000 ... 4020000101]
    23:49:59.753237: Kernel::Backend | DEBUG: Measure qubits (10) -> [1020000000 ... 4020000100] -> [1.0 ... 1.0]
    23:49:59.753890: Kernel::Backend | DEBUG: Apply channel error percent (0.026) -> (10) qubits
    23:49:59.757961: Kernel::Backend | DEBUG: Measure qubits (10) -> [1020000001 ... 4020000101] -> [1.0 ... 1.0]

    Alice Device Logs:
    23:49:59.481388: Alice | INFO: Device is composed.
    23:49:59.537650: Alice | INFO: Device is preapaired for simulation with 3 application.
    23:49:59.538684: Alice | LOG: :State: "device not started" ---> "device is running"
    23:50:00.544802: Alice | LOG: :State: "device is running" ---> "device may end"
    23:50:00.545608: Alice | WARNING: Device simulation is idled after 1.0019 seconds.

    Alice Default Application Logs:
    23:49:59.481868: Alice::default_app | DEBUG: Application is created.
    23:49:59.537624: Alice::default_app | DEBUG: Application prepaired successfuly.
    23:49:59.743651: Alice::default_app | INFO: Application is starting...
    23:49:59.743703: Alice::default_app | LOG: :State: "application is not started" ---> "application is running"
    23:49:59.754323: Alice::default_app | INFO: Application is ended in 0.0105 seconds.
    23:49:59.754345: Alice::default_app | LOG: :State: "application is running" ---> "application is finished"
