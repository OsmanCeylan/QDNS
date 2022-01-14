Noise
===============

QDNS offers a transparent and fully customizable structure to simulate noise.

Noise Types
-----------------------------

Noise patterns that QDNS can simulate::

    import QDNS
    print('channels = ', QDNS.noise_channels)

.. code-block:: python

    channels = (
        depolarisation_channel,
        bit_flip_channel,
        phase_flip_channel,
        bit_and_phase_flip_channel,
        reset_channel, no_noise_channel
    )

As its name mentions, no noise channel does nothing.

Noise Locations
-----------------------------

Noise is applied in many parts of the simulation.

:any:`State Prepair: This noise is applied right after qubit is allocated and resetted.`
:any:`Measure: This noise is applied before qubit is measured.`
:any:`Gate Error: This noise is applied immediately after any transformation.`
:any:`Scramble: This noise is applied when scramble is needed.`

``Also scramble method is applied qubits that passed quantum channel.``

Default noise pattern is::

    import QDNS
    print(QDNS.default_noise_pattern)

.. code-block:: python

    State Prepair: bit_flip_channel | 0.005
    Measure: bit_flip_channel | 0.005
    Gate Error: phase_flip_channel | 0.005
    Scramble Error: depolarisation | 0.577


Creating Noises
-----------------------------

The following part of code explains how to change the noise pattern before simulation::

    def main():
        ...
        net = QDNS.Network(...)
        conf = QDNS.BackendConfiguration(...)
        ...

        my_noise_pattern = QDNS.NoisePattern(
            0.05, 0.1, 0.2,
            sp_channel=QDNS.bit_flip_channel,
            measure_channel=QDNS.depolarisation_channel,
            gate_channel=QDNS.no_noise_channel,
            scramble_channel=QDNS.reset_channel
        )

        sim = QDNS.Simulator()
        sim.simulate(net, conf, noise_pattern=my_noise_pattern)

        # Or we can change default noise pattern before simulation too.
        # QDNS.change_default_noise_pattern(my_noise_pattern)

Quantum Channel Noise
-----------------------------

QDNS uses 1680 nanometer Rayleigh scattering on fibre cable formula to calculate the error rate in channel.
But this formula is can be changed easily before simulation::

    def my_channel_error_calculator(length: float) -> [float 0 to 1]:
        ...
        ...
        ...
        return rate

    def main():
        ...

        QDNS.change_default_altitude_formula(my_channel_error_calculator)
        sim = QDNS.Simulator()
        sim.simulate(...)

