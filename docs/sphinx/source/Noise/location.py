"""
Noise is applied in many parts of the simulation.

* State Prepair: This noise is applied right after qubit is allocated and resetted.
* Measure: This noise is applied before qubit is measured.
* Gate Error: This noise is applied immediately after any transformation.
* Scramble: This noise is applied when scramble is needed. Also its **method** is applied qubits that passed quantum channel.

Default noise pattern is::

    import QDNS
    print(QDNS.default_noise_pattern)

.. code-block:: python

    State Prepair: bit_flip_channel | (0.007,)
    Measure: bit_flip_channel | (0.005,)
    Gate Error: phase_flip_channel | (0.005,)
    Scramble Error: depolarisation | (0.667,)
"""
