"""
Noise patterns that QDNS can simulate::

    import QDNS
    print('channels = ', QDNS.noise_channels)

.. code-block:: python

    channels = (
        depolarisation_channel, bit_flip_channel, phase_flip_channel,
        asymmetric_depolarisation_channel, bit_and_phase_flip_channel,
        reset_channel, no_noise_channel
        )

As its name mentions, no noise channel does nothing.
"""