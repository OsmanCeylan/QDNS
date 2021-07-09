import QDNS
import logging


def alice_default_app(app: QDNS.Application, *user_args):
    print(app.reveal_connection_information())


def bob_default_app(app: QDNS.Application, *user_args):
    print(app.reveal_connection_information())


def eve_default_application(app: QDNS.Application, *user_args):
    pass


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
