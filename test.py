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
            print("Sending pairs is failed.")
            return

        results = app.measure_qubits(my_pairs)
        app.put_simulation_result(results)


class Bob(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.bob_default_app)

    @staticmethod
    def bob_default_app(app: QDNS.Application):
        op = app.wait_next_qubits(512)
        my_pairs, pair_length = op

        results = app.measure_qubits(my_pairs)
        app.put_simulation_result(results)


def main(backend, length_: float):
    logging.basicConfig(level=logging.WARNING)

    # Build network
    alice, bob = Alice(), Bob()
    net = QDNS.Network(alice, bob)
    net.add_channels(alice, bob, length=length_)  # km

    # Set needed quantum resources.
    if backend == QDNS.STIM_BACKEND:
        frames = {2: 10000}
        core_count = 1
    else:
        core_count = int(QDNS.core_count / 2)
        frames = {
            2: {
                1: 64,
                2: 512
            }
        }

    # Create backend confuguration.
    backend_conf = QDNS.BackendConfiguration(backend, core_count, frames)

    # Simulate network.
    noise_pattern = QDNS. NoisePattern(
        0, 0, 0,
        scramble_channel=QDNS.bit_flip_channel,
    )

    sim = QDNS.Simulator()
    results = sim.simulate(net, backend_conf, noise_pattern)

    # Get the user values.
    alice_results = results.user_dumpings(alice.label, QDNS.DEFAULT_APPLICATION_NAME)
    bob_results = results.user_dumpings(bob.label, QDNS.DEFAULT_APPLICATION_NAME)

    # Return error rate.
    count = 0
    for i in range(alice_results.__len__()):
        if alice_results[i] == bob_results[i]:
            count += 1
    return count / alice_results.__len__()


def stub(length_: float):
    errors_ = list()
    rate = main(QDNS.QISKIT_BACKEND, length_)
    errors_.append(rate)
    rate = main(QDNS.CIRQ_BACKEND, length_)
    errors_.append(rate)
    rate = main(QDNS.STIM_BACKEND, length_)
    errors_.append(rate)
    return errors_


def test():
    error_rates = list()
    for i in range(1, 101, 25):
        error_rates.append([i, stub(i)])
    return error_rates


if __name__ == '__main__':
    lengths = list()
    plot_cirq = list()
    plot_qiskit = list()
    plot_stim = list()

    for errors in test():
        length, rates = errors
        qiskit, cirq, stim = rates

        print("L: ", length, "Q: ", qiskit, "C: ", cirq, "S: ", stim)
