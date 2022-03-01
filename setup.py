from setuptools import setup

import os

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(
    name='QDNS',
    version='0.56',
    packages=['QDNS', 'QDNS.tools', 'QDNS.device', 'QDNS.device.tools', 'QDNS.backend', 'QDNS.backend.tools', 'QDNS.commands', 'QDNS.rtg_apps', 'QDNS.networking', 'QDNS.simulation',
              'QDNS.interactions'],
    url='https://github.com/OsmanCeylan/QDNS',
    license='BSD',
    author='osman semi ceylan',
    author_email='osman.semi.ceylanq@gmail.com',
    description='QDNS - Quantum Dynamic Network Simulator',
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'cirq': ['cirq>=0.9.1'],
        'qiskit': ['qiskit>=0.20.0'],
        'stim': ['stim>=1.3.0']
    }
)
