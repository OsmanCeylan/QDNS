"""
We recommend using these functions to create bell::

    def alice_default_app(app: QDNS.Application, *user_args):
        pairs = app.generate_entangle_pairs(5)['pairs']
        print('Pairs': pairs)

.. code-block:: python

    Pairs: [['020025600', '020025601'], ['020025700', '020025701'], ['020025800', '020025801'], ['020025900', '020025901'], ['020026000', '020026001']]

We recommend using these functions to create ghz state::

    def alice_default_app(app: QDNS.Application, *user_args):
        qubits = app.generate_ghz_pair(3)['qubits']
        print('Qubits': qubits)

.. code-block:: python

    Qubits: ['020038400', '020038401', '020038402']
"""


def generate_entangle_pairs(self, count, *args):
    """
    Generates entangle pairs.

    Args:
        count: Count of pairs.
        args: Backend specific arguments.

    Returns:
        {"exit_code", "pairs"}
    """

    pass


def generate_ghz_pair(self, size, *args):
    """
    Generates entangle pairs.

    Args:
        size: Qubit count in ghz state.
        args: Backend specific arguments.

    Returns:
        {"exit_code", "qubits"}
    """

    pass
