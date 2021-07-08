"""
As can be seen in the image above, its internal structure design of a device.
Each device has a network socket that performs communication. It has ports according to the socket type.
On the quantum side, it has a photon pump and quantum memory. These photons are actually pointers to a qubits from backend.
Every device has an QKD layer that can be used device-wide.
Since the software allows simulating multiple applications, there is a default application and user applications that are connected via localhost.

Classes derived from the Device
#####

* Node: Device with generic settings.
* Router: Device with only routing layer.
* Observer: Device that capable of middleman attacks.
"""