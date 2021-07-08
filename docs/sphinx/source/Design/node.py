"""
As can be seen in the figure above, there is the simulation kernel at the top.
QDNS uses kernel backend handlers with a wrapper. Dynamic connections are allowed because the core hosts the topology.
Devices are evenly distributed over each processor core except for the simulation kernel.
The highest performance is obtained when the number of nodes in the topology is equal to or less than the number of cores.
"""