"""
CIRQ can simulate quantum circuits. Therefore, resource consumption is quite high and uses frames for allocation operations.
With using Cirq, QDNS can simulate networks with higher dimension qubits or known as qudits.

The software already allocates a certain amount of frames but the number of frames to be used in the simulation should be calculated in advance::

    def main():
        logging.basicConfig(level=logging.DEBUG)

        alice = Alice()
        net = QDNS.Network(alice)

        # Total 1x256 + 2x128 + 3x64 qubits pre-allocated.
        qubit_frames = {
            1: 256,
            2: 128,
            3: 64
        }

        # Total 1x64 + 2x32 + 3x16 qutrits pre-allocated.
        qutrit_frames = {
            1: 64,
            2: 32,
            3: 16
        }

        QDNS.change_default_cirq_qframe_configuretion(qubit_frames, qutrit_frames)
        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.CIRQ_BACKEND)

Because of pre-allocation process and internal workflow of Cirq, this backend is slowest among them.
"""