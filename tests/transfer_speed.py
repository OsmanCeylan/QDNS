import QDNS
import logging


class Alice(QDNS.Node):
    def __init__(self):
        super().__init__("Alice")
        self.create_new_application(self.alice_default_app)

    @staticmethod
    def alice_default_app(app: QDNS.Application):
        qubits = app.allocate_qubits(10000)
        app.send_quantum("Bob", *qubits, routing=True)
        app.put_simulation_result(["Alice send Bob time", app.global_time])

        qubits = app.allocate_qubits(10000)
        app.send_quantum("Charlie", *qubits, routing=True)
        app.put_simulation_result(["Alice send Charlie time", app.global_time])


class Bob(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.bob_default_app)

    @staticmethod
    def bob_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(10000)

        if iterable is None:
            raise AttributeError("Bob did not reieved qubits!")

        if iterable[1] < 10000:
            raise ValueError("Bob did not receive 1000 qubits!")

        app.put_simulation_result(["Bob recieve time", app.global_time])


class Charlie(QDNS.Node):
    def __init__(self):
        super().__init__("Charlie")
        self.create_new_application(self.charlie_default_app)

    @staticmethod
    def charlie_default_app(app: QDNS.Application):
        iterable = app.wait_next_qubits(10000)

        if iterable is None:
            raise AttributeError("Bob did not reieved qubits!")

        if iterable[1] < 10000:
            raise ValueError("Bob did not receive 1000 qubits!")

        app.put_simulation_result(["Charlie recieve time", app.global_time])


class Eve(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.eve_default_app)

    @staticmethod
    def eve_default_app(app: QDNS.Application):
        pass


def main():
    logging.basicConfig(level=logging.WARNING)

    alice, bob, charlie, eve = Alice(), Bob(), Charlie(), Eve()
    r1, r2 = QDNS.Router("R1"), QDNS.Router("R2")
    net = QDNS.Network(alice, bob, charlie, eve, r1, r2)

    net.add_channels(alice, bob)
    net.add_channels(bob, r1)
    net.add_channels(r1, charlie)
    net.add_channels(charlie, r2)
    net.add_channels(r2, eve)

    frames = {2: 100000}
    backend_conf = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, frames)

    sim = QDNS.Simulator()
    results = sim.simulate(net, backend_conf)

    # Grap results from Alice and Bob.
    alice_res = results.user_dumpings(alice.label, QDNS.DEFAULT_APPLICATION_NAME)
    bob_res = results.user_dumpings(bob.label, QDNS.DEFAULT_APPLICATION_NAME)
    charlie_res = results.user_dumpings(charlie.label, QDNS.DEFAULT_APPLICATION_NAME)
    # eve_res = results.user_dumpings(eve.label, QDNS.DEFAULT_APPLICATION_NAME)

    print(alice_res, bob_res, charlie_res)


if __name__ == '__main__':
    main()
