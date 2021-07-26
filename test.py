import QDNS
import logging


def alice_func(app: QDNS.Application):
    protocol = app.run_qkd_protocol("Bob", 512, QDNS.BB84_METHOD)

    if protocol is None:
        return

    app.send_classic_data("Bob", protocol[0], broadcast=False, routing=True)


def bob_func(app: QDNS.Application):
    protocol = app.wait_qkd()

    if protocol is None:
        return

    key = protocol[0]
    alice_key = app.wait_next_package().data

    count = 0
    for i in range(key.__len__()):
        if alice_key[i] == key[i]:
            count += 1

    print("Count: ", count, "Rate: ", count / key.__len__())


def test():
    logging.basicConfig(level=logging.DEBUG)

    core_count = 6

    frames = {
        2: {
            1: int(512 / core_count) + 1,
            2: 16,
            3: 8
        },

        3: {
            1: 8,
            2: 4
        }
    }

    alice = QDNS.Device("Alice")
    bob = QDNS.Device("Bob")

    alice.create_new_application(alice_func)
    bob.create_new_application(bob_func)

    net = QDNS.Network(alice, bob)
    net.add_channels(alice, bob)

    k = QDNS.Simulator()

    noise = QDNS.NoisePattern(
        0, 0, 0,
        QDNS.no_noise_channel,
        QDNS.no_noise_channel,
        QDNS.no_noise_channel,
        QDNS.no_noise_channel
    )
    conf = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, core_count, frames)
    res = k.simulate(net, conf, noise)
    print(res.backend_logs())


if __name__ == '__main__':
    test()
