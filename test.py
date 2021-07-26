import QDNS
import logging


def alice_func(app: QDNS.Application):
    key = app.run_qkd_protocol("Bob", 512, QDNS.E91_METHOD)
    if key is not None:
        key = key[0]
    else:
        return

    app.send_classic_data("Bob", key, broadcast=False, routing=True)


def bob_func(app: QDNS.Application):
    key = app.wait_qkd()
    if key is not None:
        key = key[0]
    else:
        return

    alice_key = app.wait_next_package("Alice").data
    print("Alice Len: ", alice_key.__len__())
    print("Bob Len: ", key.__len__())

    if alice_key.__len__() != key.__len__():
        return

    match = 0
    for i in range(alice_key.__len__()):
        if alice_key[i] == key[i]:
            match += 1

    print("Match: ", match, "Percent: ", match / alice_key.__len__())


def test():
    logging.basicConfig(level=logging.DEBUG)

    frames = {
        2: {
            1: 516,
            2: 516,
            3: 16
        },

        3: {
            1: 8,
            2: 4
        }
    }

    alice = QDNS.Device("Alice")
    bob = QDNS.Device("Bob")
    r1 = QDNS.Router("R1")

    alice.create_new_application(alice_func)
    bob.create_new_application(bob_func)

    net = QDNS.Network(alice, bob, r1)
    net.add_channels(alice, r1)
    net.add_channels(r1, bob)

    k = QDNS.Simulator()

    conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, 1, frames)
    res = k.simulate(net, conf)

    print(res.backend_logs())


if __name__ == '__main__':
    test()
