Backends
===============

QDNS has 4 backens to work with and each has different advantages.

Backend Configuration
-----------------------------

Before starting any simulation Backend Configuration must be created.

.. code-block:: python

    class BackendConfiguration(backend_flag: str, process_count: int, frame_dict: dict):
        """
        Args:
            Backend Flag: One of QDNS.supported_backends.
            Process count: Process count.
            Frame Dict: Backend specific frame dictionary.
        """

Backend flag must be in the avaible in the system.
QDNS tries to import the all supported backends and checks for avaiblity::

    print(QDNS.supported_backends)
    print(QDNS.avaible_backends)

.. code-block:: python

    ('CIRQ backend', 'QISKIT backend', 'STIM backend', 'SDQS backend')
    ['CIRQ backend', 'QISKIT backend', 'STIM backend', 'SDQS backend']

Process count is sets the how many process should work for backend.
As more process work for backend simulation became more faster.
We prefer give half of the real core count to work for backend::

    print("My real core count: " QDNS.core_count)

.. code-block:: python

    8

Frame dict is varies between backends.
The numbers we set in this dictionary shapes the pre-allocation process.
We mention this in the section of the backend.

CIRQ
-----------------------------

CIRQ can simulate quantum circuits.
Therefore, resource consumption is quite high and uses frames for allocation operations.
With using Cirq, QDNS can simulate networks with higher dimension qubits or known as qudits.
Terminology is
:any:`frames = {"dim": {"qudit_count": "circuit_count"}}` ::

    """
    The code below pre-allocates:
    2 dimension {1 Qubit: 256 circuit, 2 Qubit: 128 circuit, 3 Qubit: 64 circuit}
    3 dimension {1 Qutrit: 64 circuit, 2 Qutrit: 32 circuit}
    """

    cpu_count = QDNS.core_count / 2
    frames = {
        2: {
            1: 256 / cpu_count,
            2: 128 / cpu_count,
            3: 64 / cpu_count,
        },

        3: {
            1: 64 / cpu_count,
            2: 32 / cpu_count,
        }
    }
    config = QDNS.BackendConfiguration(QDNS.CIRQ_BACKEND, cpu_count, frames)

QISKIT
-----------------------------

Prepairation Qiskit is same as Cirq. But Qiskit does not support higher dimensions so other than key 2 is dismissed.
Terminology is
:any:`frames = {"dim": {"qudit_count": "circuit_count"}}` ::

    """
    The code below pre-allocates:
    2 dimension {1 Qubit: 256 circuit, 2 Qubit: 128 circuit, 3 Qubit: 64 circuit}
    """

    cpu_count = QDNS.core_count / 2
    frames = {
        2: {
            1: 256 / cpu_count,
            2: 128 / cpu_count,
            3: 64 / cpu_count,
        },

        3: {
            1: 64 / cpu_count,
            2: 32 / cpu_count,
        }
    }
    config = QDNS.BackendConfiguration(QDNS.QISKIT_BACKEND, cpu_count, frames)


SDQS
-----------------------------

Sdqs is a circuit simulator we coded for QDNS. It uses same configuration as Cirq or Qiskit.
Terminology is
:any:`frames = {"dim": {"qudit_count": "circuit_count"}}` ::

    """
    The code below pre-allocates:
    2 dimension {1 Qubit: 256 circuit, 2 Qubit: 128 circuit, 3 Qubit: 64 circuit}
    """

    cpu_count = QDNS.core_count / 2
    frames = {
        2: {
            1: 256 / cpu_count,
            2: 128 / cpu_count,
            3: 64 / cpu_count,
        },

        3: {
            1: 64 / cpu_count,
            2: 32 / cpu_count,
        }
    }
    config = QDNS.BackendConfiguration(QDNS.SDQS_BACKEND, cpu_count, frames)

STIM
-----------------------------

Unlike the others, STIM simulates quantum stabilizer circuit::

    # Sets the qubit limit count to 100000.
    frames = { 2: 100000 }
    config = QDNS.BackendConfiguration(QDNS.STIM_BACKEND, 1, frames)

While STIM works fastest among them, it does not use transformation matrix.
So effective gate count on STIM is limited.

Supported Gates
#################

#. gates.IDGate
#. gates.PauliX
#. gates.PauliY
#. gates.PauliZ
#. gates.HGate
#. gates.SGate
#. gates.SWAPGate
#. gates.ISWAPGate
#. gates.CXGate
#. gates.CYGate
#. gates.CZGate
