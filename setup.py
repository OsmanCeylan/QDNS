from setuptools import setup

setup(
    name='QDNS',
    version='0.49',
    packages=['QDNS', 'QDNS.tools', 'QDNS.device', 'QDNS.backend', 'QDNS.commands', 'QDNS.rtg_apps', 'QDNS.networking', 'QDNS.simulation', 'QDNS.architecture', 'tests', 'tests.new', 'tests.zero', 'tests.kernel', 'tests.unitest'],
    url='github.com/OsmanCeylan/QDNS',
    license='',
    author='osman',
    author_email='osman.semi.ceylan@gmail.com',
    description='QDNS - Quantum Network Simulator on Python'
)
