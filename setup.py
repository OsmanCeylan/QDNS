from setuptools import setup
from QDNS import __version__

setup(
    name='QDNS',
    version=__version__,
    packages=['QDNS', 'QDNS.tools', 'QDNS.device', 'QDNS.device.tools', 'QDNS.backend', 'QDNS.backend.tools', 'QDNS.commands', 'QDNS.rtg_apps', 'QDNS.networking', 'QDNS.simulation',
              'QDNS.interactions'],
    url='https://github.com/OsmanCeylan/QDNS',
    license='BSD',
    author='osman semi ceylan',
    author_email='osman.semi.ceylanq@gmail.com',
    description='QDNS - Quantum Dynamic Network Simulator'
)
