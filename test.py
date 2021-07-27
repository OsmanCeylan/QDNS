import QDNS
import logging


class Alice(QDNS.Node):
    def __init__(self):
        super().__init__("Alice")
        self.create_new_application(self.alice_default_app)

    @staticmethod
    def alice_default_app(default_app: QDNS.Application):
        message = "Hello Bob! I hope no one will read this message."

        # Send message to Bob.
        default_app.send_classic_data("Bob", message)

        # Send bob a qubit.
        qubit = default_app.allocate_qubit()
        default_app.send_quantum("Bob", qubit)


class Bob(QDNS.Node):
    def __init__(self):
        super().__init__("Bob")
        self.create_new_application(self.bob_default_app)

    @staticmethod
    def bob_default_app(default_app: QDNS.Application):
        # Wait for package.
        package = default_app.wait_next_package()

        if package is None:
            print("Bob did not received package.")
        else:
            print("Bob prints: ", package.data)

        # Wait for qubit.
        op = default_app.wait_next_qubit()
        if op is None:
            print("Bob did not receive qubit.")
        else:
            print("Qubit: ", op)


class Eve(QDNS.Observer):
    def __init__(self):
        super().__init__("Eve")
        self.create_new_application(self.eve_app, static=True, delayed_start_time=0)

    @staticmethod
    def eve_app(app: QDNS.Application):
        # Set listener interrupt mode.
        app.listener.set_interrupt(True)

        while True:
            communication = app.listener.get_communication_item()

            if communication is None:
                break
            else:
                app.listener.print_item(communication)

            # Releases the packages on traffic.
            # Drops the qubits on traffic.
            if isinstance(communication, QDNS.Package):
                app.listener.release_item()
            else:
                app.listener.drop_item()

        print("Eve listening is over.")


def main():
    logging.basicConfig(level=logging.WARNING)

    alice = Alice()
    bob = Bob()
    eve = Eve()

    net = QDNS.Network(alice, bob, eve)

    # Add eve between them.
    net.add_channels(alice, eve)
    net.add_channels(eve, bob)

    frames = {2: {1: 1}}
    conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
    sim = QDNS.Simulator()
    res = sim.simulate(net, conf)


if __name__ == '__main__':
    main()


QDNS.change_logger_name("QDNS")
QDNS.change_logger_format("%H:%M:%S.%f")
QDNS.change_default_logger_level(logging.DEBUG)