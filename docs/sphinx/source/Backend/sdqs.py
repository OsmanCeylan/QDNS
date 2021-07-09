"""
Sdqs is a circuit simulator like Cirq. While it does not support qudits but work more faster than Cirq.
Configuring frames follows as::

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = QDNS.Node("Alice")
        net = QDNS.Network(alice)

        # Total 1x256 + 2x128 + 3x64 qubits pre-allocated.
        qubit_frames = {
            1: 256,
            2: 128,
            3: 64
        }

        QDNS.change_default_sdqs_qframe_configuretion(qubit_frames)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.SDQS_BACKEND)
"""