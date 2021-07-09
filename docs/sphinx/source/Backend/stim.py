"""
Unlike the others, STIM simulates quantum stabilizer circuit. STIM does not need any frame configuration and uses both allocate_frame(s) or allocate_qubit(s) methods.
While STIM works fastest among them, it does not use transformation matrix. So effective gate count on STIM is limited.

Supported Gates:
#################
* gates.IDGate
* gates.PauliX
* gates.PauliY
* gates.PauliZ
* gates.HGate
* gates.SGate
* gates.SWAPGate
* gates.ISWAPGate
* gates.CXGate
* gates.CYGate
* gates.CZGate

``STIM is the default backend.``
"""