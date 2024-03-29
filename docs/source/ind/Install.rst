Introduction
===============

What is QDNS?
-----------------------------

Quantum Dynamic Network Simulator (QDNS) is a event driven quantum network simulation framework written in Python.
QDNS allows users to program quantum network protocols over a dynamic and uncertain environment.

Installation of QDNS
-----------------------------

QDNS is prepared to run on any platform where Python is present and running.
QDNS is tested on Windows, Linux and MacOS. We strongly recommend Linux.

Requirtments
#######

.. code-block:: python

    * Python >= 3.7
    * numpy
    * psutil
    * cirq
    * stim
    * qiskit
    * matplotlib
    * networkx
    * pandas
    * setuptools

Commands
########

.. code-block:: python

    $ git clone https://github.com/OsmanCeylan/QDNS.git
    $ cd QDNS
    $ pip install .

Troubleshot
########

If something goes wrong, you can install package in new python environment.

.. code-block:: python

    Windows: $ py -m venv env
             $ .\env\Scripts\\activate
             $ git clone https://github.com/OsmanCeylan/QDNS.git
             $ cd QDNS
             $ py -m pip install .

    Unix   : $ python3 -m venv env
             $ source env/bin/activate
             $ git clone https://github.com/OsmanCeylan/QDNS.git
             $ cd QDNS
             $ pip install .

In addition, QDNS can be used by placing the framework folder to next to the executable code.

Stim
_______

Stim on Windows requeires Visual C++ 14.0 from Visual Studio.

Stim version 1.5 on Linux may fail to install. Try version 1.3.