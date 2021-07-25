from QDNS.device.device import Device
from QDNS.device.application import Application
from QDNS.backend.tools.config import CIRQ_BACKEND
from QDNS.networking.network import Network
from QDNS.rtg_apps.qkd import BB84_METHOD
from QDNS.simulation.kernel import Kernel
from QDNS.tools import communication
from QDNS.commands import library
from QDNS.device.tools.socket_tools import SocketSettings
from QDNS.tools import gates

import logging


def alice_func(app: Application):
    """
    al = communication.ApplicationLayer(app.label)
    il = communication.InternetLayer(app.host_label, "Bob", None, ("000000001", "000000002"), broadcast=False, routing=True)
    pkg = communication.Package(al, il)
    req = app._send_package_request("Bob", pkg, want_respond=True)
    print(app._wait_hinted_next_Trespond(request_id=req.generic_id))
    """

    """
    qubits = app.allocate_qframe(3)
    app.apply_transformation(gates.HGate(), qubits[0])
    app.apply_transformation(gates.CXGate(), qubits[0], qubits[1])
    print(app.measure_qubits(qubits))
    """

    print(app.run_qkd_protocol("Bob", 64, BB84_METHOD))


def bob_func(app: Application):
    print(app.wait_qkd())


logging.basicConfig(level=logging.DEBUG)

frames = {
    2: {
        1: 64,
        2: 64,
        3: 16
    },

    3: {
        1: 8,
        2: 4
    }
}

alice = Device("Alice")
bob = Device("Bob")

alice.create_new_application(alice_func)
bob.create_new_application(bob_func)

net = Network(alice, bob)
net.add_channels(alice, bob)

k = Kernel()
res = k.simulate(net, CIRQ_BACKEND, frames)
