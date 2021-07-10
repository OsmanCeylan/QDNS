from setuptools import setup
from QDNS import __version__

setup(
    name='QDNS',
    version=str(__version__),
    packages=['QDNS', 'QDNS.tools', 'QDNS.device', 'QDNS.backend', 'QDNS.commands', 'QDNS.rtg_apps', 'QDNS.networking', 'QDNS.simulation', 'QDNS.architecture'],
    url='github.com/OsmanCeylan/QDNS',
    license='BSD',
    author='COMU Team',
    author_email='osman.semi.ceylan@gmail.com',
    description='QDNS - Quantum Network Simulator on Python'
)
