# QDNS
## Event Driven Dynamic Quantum Network Simulator

Quantum Dynamic Network Simulator (QDNS) is a event driven quantum network simulation framework written in Python. QDNS allows users to program quantum network protocols over a dynamic and uncertain environment.

## Requirtments
- Python >= 3.7 Linux, Windows, macOS Environment
- numpy
- psutil
- cirq[Opt]: For CIRQ Backend
- qiskit[Opt]: For QISKIT Backend
- stim[Opt]: For STIM Backend
- matplotlib
- networkx
- pandas

## Installation

```sh
git clone https://github.com/OsmanCeylan/QDNS.git
cd QDNS
pip install .
```

Stim on Windows requeires Visual C++ 14.0 from Visual Studio.
Stim version 1.5 on Linux may fail to install. Try version 1.3.

## Documentation

Sphinx documentation can be found in **docs/sphinx** folder.
```
cd docs/sphinx
make html
```

## Examples

Few examples can be found in both documentation and **examples** folder. All examples are in Python notebook format.

## Note

SDQS Backend benched because of performance regressions. It will back after re-optimization patch.

## License

This project licensed under BSD License.
