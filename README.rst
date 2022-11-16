QDNS
====

Event Driven Dynamic Quantum Network Simulator
----------------------------------------------

Quantum Dynamic Network Simulator (QDNS) is an event driven quantum
network simulation framework written in Python. QDNS allows users to
program quantum network protocols over a dynamic and uncertain
environment.

Requirtments
------------

-  Python >= 3.7 Linux, Windows, macOS Environment
-  numpy
-  psutil
-  cirq[Opt]: For CIRQ Backend
-  qiskit[Opt]: For QISKIT Backend
-  stim[Opt]: For STIM Backend
-  matplotlib
-  networkx
-  pandas

Installation
------------

.. code:: sh

   git clone https://github.com/OsmanCeylan/QDNS.git
   cd QDNS
   pip install .

Stim on Windows requeires Visual C++ 14.0 from Visual Studio. Stim
version 1.5 on Linux may fail to install. Try version 1.3.

Documentation
-------------

Documentation can be found here:

https://qdns.readthedocs.io/en/master/


Documentations can also compiled from **docs** folder.

::

    cd QDNS
    sphinx-build -b html docs/source/ docs/build/html

Examples
--------

Few examples can be found in both documentation and **examples** folder.
All examples are in Python notebook format.

Note
----

SDQS Backend benched because of performance regressions. It will back
after re-optimization patch.

Citiation
----------
Please cite this software follows:
Ceylan, Osman Semi, and İhsan Yılmaz. "QDNS: Quantum Dynamic Network Simulator Based on Event Driving." 2021 International Conference on Information Security and Cryptology (ISCTURKEY). IEEE, 2021.

License
-------

This project licensed under BSD License.
