import QDNS
import logging


class Alice(QDNS.Node):
    def __init__(self):
        super().__init__("Alice")
        self.create_new_application(self.alice_default_app)

    @staticmethod
    def alice_default_app(app: QDNS.Application):
        qubits_bob = app.allocate_qubits(1000)
        app.put_simulation_result(["AtoE", app.global_time])
        app.send_quantum("Bob", *qubits_bob, routing=True)

        qubits_charlie = app.allocate_qubits(1000)
        app.put_simulation_result(["AtoC", app.global_time])
        app.send_quantum("Charlie", *qubits_charlie, routing=True)

        qubits_eve = app.allocate_qubits(1000)
        app.put_simulation_result(["AtoE", app.global_time])
        app.send_quantum("Eve", *qubits_eve, routing=True)

        qubits_freya = app.allocate_qubits(1000)
        app.put_simulation_result(["AtoF", app.global_time])
        app.send_quantum("Freya", *qubits_freya, routing=True)


class Bob(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.bob_default_app)

    @staticmethod
    def bob_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(1000)

        if iterable is None:
            raise AttributeError("Bob did not reieved qubits!")

        if iterable[1] < 1000:
            raise ValueError("Bob did not receive 1000 qubits!")

        app.put_simulation_result(["Bob recieve time", app.global_time])


class Charlie(QDNS.Node):
    def __init__(self):
        super().__init__("Charlie")
        self.create_new_application(self.charlie_default_app)

    @staticmethod
    def charlie_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(1000)

        if iterable is None:
            raise AttributeError("Charlie did not reieved qubits!")

        if iterable[1] < 1000:
            raise ValueError("Charlie did not receive 1000 qubits!")

        app.put_simulation_result(["Charlie recieve time", app.global_time])


class Eve(QDNS.Node):
    def __init__(self):
        super().__init__("Eve")
        self.create_new_application(self.eve_default_app)

    @staticmethod
    def eve_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(1000)

        if iterable is None:
            raise AttributeError("Eve did not reieved qubits!")

        if iterable[1] < 1000:
            raise ValueError("Eve did not receive 1000 qubits!")

        app.put_simulation_result(["Eve recieve time", app.global_time])


class Freya(QDNS.Node):
    def __init__(self):
        super().__init__("Freya")
        self.create_new_application(self.freya_default_app)

    @staticmethod
    def freya_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(1000)

        if iterable is None:
            raise AttributeError("Freya did not reieved qubits!")

        if iterable[1] < 1000:
            raise ValueError("Freya did not receive 1000 qubits!")

        app.put_simulation_result(["Freya recieve time", app.global_time])


def main():
    logging.basicConfig(level=logging.WARNING)

    alice, bob, charlie, eve, freya = Alice(), Bob(), Charlie(), Eve(), Freya()
    r1, r2, r3 = QDNS.Router("R1"), QDNS.Router("R2"), QDNS.Router("R3")
    net = QDNS.Network(alice, bob, charlie, eve, freya, r1, r2, r3)

    net.add_channels(alice, bob)
    net.add_channels(bob, r1)
    net.add_channels(r1, charlie)
    net.add_channels(charlie, r2)
    net.add_channels(r2, eve)
    net.add_channels(eve, r3)
    net.add_channels(r3, freya)

    frames = {2: 50000}
    backend_conf = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, frames)

    QDNS.set_respond_expire_time(10.0)
    QDNS.set_qubit_expire_time(10.0)

    sim = QDNS.Simulator()
    results = sim.simulate(net, backend_conf)

    # Grap results from Alice and Bob.
    alice_res = results.user_dumpings(alice.label, QDNS.DEFAULT_APPLICATION_NAME)
    bob_res = results.user_dumpings(bob.label, QDNS.DEFAULT_APPLICATION_NAME)
    charlie_res = results.user_dumpings(charlie.label, QDNS.DEFAULT_APPLICATION_NAME)
    eve_res = results.user_dumpings(eve.label, QDNS.DEFAULT_APPLICATION_NAME)
    freya_res = results.user_dumpings(freya.label, QDNS.DEFAULT_APPLICATION_NAME)

    to_bob = alice_res[0][0][1]
    to_charlie = alice_res[1][0][1]
    to_eve = alice_res[2][0][1]
    to_freya = alice_res[3][0][1]

    bob_time = bob_res[1]
    charlie_time = charlie_res[1]
    eve_time = eve_res[1]
    freya_time = freya_res[1]

    print(bob_time - to_bob)
    print(charlie_time - to_charlie)
    print(eve_time - to_eve)
    print(freya_time - to_freya)


if __name__ == '__main__':
    main()
