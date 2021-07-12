"""
QDNS is prepared to run on any platform where Python is present and running.
QDNS is tested on Windows, Linux and MacOS. We strongly recommend Linux.

Requirtments
#####
* Python >= 3.6
* numpy
* psutil
* cirq
* stim
* matplotlib
* networkx
* pandas
* setuptools

Commands
########

.. comment pip install -r requirements.txt

.. code-block:: python

    $ git clone https://github.com/OsmanCeylan/QDNS.git
    $ cd QDNS
    $ pip install -r requirements.txt
    $ pip install .

Troubleshot
########

If something goes wrong, you can install package in new python environment.

.. code-block:: python

    Windows: $ py -m venv env
             $ .\env\Scripts\\activate
             $ git clone https://github.com/OsmanCeylan/QDNS.git
             $ cd QDNS
             $ py -m pip install -r requirements.txt
             $ py -m pip install .

    Unix   : $ python3 -m venv env
             $ source env/bin/activate
             $ git clone https://github.com/OsmanCeylan/QDNS.git
             $ cd QDNS
             $ pip install -r requirements.txt
             $ pip install .

In addition, QDNS can be used by placing the framework folder to next to the executable code.
"""
