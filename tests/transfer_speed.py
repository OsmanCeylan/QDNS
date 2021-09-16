import QDNS
import logging


class Alice(QDNS.Node):
    def __init__(self):
        super().__init__("Alice")
        self.create_new_application(self.alice_default_app)

    @staticmethod
    def alice_default_app(app: QDNS.Application):
        my_pairs = app.send_entangle_pairs(512, "Bob")

        if my_pairs is None:
            print("Something gone wrong on Alice side.")
            return

        result = app.measure_qubits(my_pairs)
        app.put_simulation_result(result)


class Bob(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.bob_default_app)

    @staticmethod
    def bob_default_app(app: QDNS.Application):
        op = app.wait_next_qubits(512)

        if op is None:
            print("Bob did not receive qubits.")
            return

        my_pairs, count = op[0], op[1]

        result = app.measure_qubits(my_pairs)
        app.put_simulation_result(result)


def main(length_):
    logging.basicConfig(level=logging.WARNING)

    alice, bob = Alice(), Bob()
    net = QDNS.Network(alice, bob)
    net.add_channels(alice, bob, length=length_)  # km

    # Create configuration, we need 512x2 frames.
    core_count = 4
    frames = {
        2: {
            2: int(600 / core_count)
        }
    }
    backend_conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, core_count, frames)

    sim = QDNS.Simulator()
    results = sim.simulate(net, backend_conf)

    # Grap results from Alice and Bob.
    alice_res = results.user_dumpings(alice.label, QDNS.DEFAULT_APPLICATION_NAME)
    bob_res = results.user_dumpings(bob.label, QDNS.DEFAULT_APPLICATION_NAME)

    count = 0
    for i in range(alice_res.__len__()):
        if alice_res[i] == bob_res[i]:
            count += 1
    rate = count / alice_res.__len__() * 100
    return rate


if __name__ == '__main__':
    print("Match rate: ", main(10.0))
