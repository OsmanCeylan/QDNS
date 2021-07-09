import numpy as np

i = np.complex(0, 1)


class Gate(object):
    gate_id = -1
    gate_name = None
    qubit_shape = 1
    dimension = 2
    stim_alias = None

    def __init__(self, matrix):
        self.matrix = matrix

    def __int__(self):
        return self.gate_id

    def __str__(self):
        return self.gate_name

    def _unitary_(self):
        return self.matrix

    # Must inherit.
    def args(self):
        return self.matrix,


class IDGate(Gate):
    """
    Applies Id gate on single qubit.
    """

    gate_id = 10
    gate_name = "IDGate"
    qubit_shape = 1
    dimension = 2
    stim_alias = "I"

    def __init__(self):
        super(IDGate, self).__init__(
            np.array([[1, 0], [0, 1]], dtype=complex)
        )

    def args(self):
        return ()


class RXGate(Gate):
    """
    Applies RX transformation on single qubit.
    """

    gate_id = 11
    gate_name = "RXGate"
    qubit_shape = 1
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.cos(angle / 2), 6), np.round(-i * np.sin(angle / 2), 6)],
            [np.round(-i * np.sin(angle / 2), 6), np.round(np.cos(angle / 2), 6)]
        ], dtype=complex)
        super(RXGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class RYGate(Gate):
    """
    Applies RY transformation on single qubit.
    """

    gate_id = 12
    gate_name = "RYGate"
    qubit_shape = 1
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.cos(angle / 2), 6), np.round(-np.sin(angle / 2), 6)],
            [np.round(np.sin(angle / 2), 6), np.round(np.cos(angle / 2), 6)]
        ], dtype=complex)
        super(RYGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class RZGate(Gate):
    """
    Applies RZ transformation on single qubit.
    """

    gate_id = 13
    gate_name = "RZ"
    qubit_shape = 1
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.exp(-i * angle / 2), 6), 0],
            [0, np.round(np.exp(i * angle / 2), 6)]
        ], dtype=complex)
        super(RZGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class PauliX(Gate):
    """
    Applies X gate on single qubit.
    """

    gate_id = 14
    gate_name = "PauliX"
    qubit_shape = 1
    dimension = 2
    stim_alias = "X"

    def __init__(self):
        super(PauliX, self).__init__(
            np.array([[0, 1], [1, 0]], dtype=complex)
        )

    def args(self):
        return ()


class PauliY(Gate):
    """
    Applies Y gate on single qubit.
    """

    gate_id = 15
    gate_name = "PauliY"
    qubit_shape = 1
    dimension = 2
    stim_alias = "Y"

    def __init__(self):
        _matrix = np.array([
            [0, -i],
            [i, 0]
        ], dtype=complex)
        super(PauliY, self).__init__(_matrix)

    def args(self):
        return ()


class PauliZ(Gate):
    """
    Applies Z gate on single qubit.
    """

    gate_id = 16
    gate_name = "PauliZ"
    qubit_shape = 1
    dimension = 2
    stim_alias = "Z"

    def __init__(self):
        _matrix = np.array([
            [1, 0],
            [0, -1]
        ], dtype=complex)
        super(PauliZ, self).__init__(_matrix)

    def args(self):
        return ()


class SGate(Gate):
    """
    Applies S gate on single qubit.
    """

    gate_id = 17
    gate_name = "SGate"
    qubit_shape = 1
    dimension = 2
    stim_alias = "S"

    def __init__(self):
        _matrix = np.array([
            [1, 0],
            [0, i]
        ], dtype=complex)
        super(SGate, self).__init__(_matrix)

    def args(self):
        return ()


class TGate(Gate):
    """
    Applies T gate on single qubit.
    """

    gate_id = 18
    gate_name = "TGate"
    qubit_shape = 1
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0],
            [0, np.round(np.exp(i * np.pi / 4), 6)]
        ], dtype=complex)
        super(TGate, self).__init__(_matrix)

    def args(self):
        return ()


class HGate(Gate):
    """
    Applies Hadamard gate on single qubit.
    """

    gate_id = 19
    gate_name = "HGate"
    qubit_shape = 1
    dimension = 2
    stim_alias = "H"

    def __init__(self):
        _matrix = np.array([
            [1, 1],
            [1, -1]
        ], dtype=complex) * 1 / np.sqrt(2)
        super(HGate, self).__init__(_matrix)

    def args(self):
        return ()


class PsedoHGate(Gate):
    """
    Applies Psedo-Hadamard gate on single qubit.
    """

    gate_id = 20
    gate_name = "Psedo-HGate"
    qubit_shape = 1
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 1],
            [-1, 1]
        ], dtype=complex) * 1 / np.sqrt(2)
        super(PsedoHGate, self).__init__(_matrix)

    def args(self):
        return ()


class CRXGate(Gate):
    """
    Applies Controlled-RX on two qubits.
    """

    gate_id = 21
    gate_name = "CRXGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.round(np.cos(angle / 2), 6), np.round(-i * np.sin(angle / 2), 6)],
            [0, 0, np.round(-i * np.sin(angle / 2), 6), np.round(np.cos(angle / 2), 6)]
        ], dtype=complex)
        super(CRXGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class CXGate(Gate):
    """
    Applies Controlled-X on two qubits.
    """

    gate_id = 22
    gate_name = "CXGate"
    qubit_shape = 2
    dimension = 2
    stim_alias = "CNOT"

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        super(CXGate, self).__init__(_matrix)

    def args(self):
        return ()


class CRYGate(Gate):
    """
    Applies Controlled-RY on two qubits.
    """

    gate_id = 23
    gate_name = "CRYGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.round(np.cos(angle / 2), 6), np.round(-np.sin(angle / 2), 6)],
            [0, 0, np.round(np.sin(angle / 2), 6), np.round(np.cos(angle / 2), 6)]
        ], dtype=complex)
        super(CRYGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class CYGate(Gate):
    """
    Applies Controlled-Y on two qubits.
    """

    gate_id = 24
    gate_name = "CYGate"
    qubit_shape = 2
    dimension = 2
    stim_alias = "CY"

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, -i],
            [0, 0, i, 0]
        ], dtype=complex)

        super(CYGate, self).__init__(_matrix)

    def args(self):
        return ()


class CRZGate(Gate):
    """
    Applies Controlled-RZ on two qubits.
    """

    gate_id = 25
    gate_name = "CRZGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.round(np.exp(-i * angle / 2), 6), 0],
            [0, 0, 0, np.round(np.exp(i * angle / 2), 6)]
        ], dtype=complex)
        super(CRZGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class CZGate(Gate):
    """
    Applies Controlled-Z on two qubits.
    """

    gate_id = 26
    gate_name = "CYGate"
    qubit_shape = 2
    dimension = 2
    stim_alias = "CZ"

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1]
        ], dtype=complex)

        super(CZGate, self).__init__(_matrix)

    def args(self):
        return ()


class CSGate(Gate):
    """
    Applies Controlled-S on two qubits.
    """

    gate_id = 27
    gate_name = "CSGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, i]
        ], dtype=complex)

        super(CSGate, self).__init__(_matrix)

    def args(self):
        return ()


class CTGate(Gate):
    """
    Applies Controlled-T on two qubits.
    """

    gate_id = 28
    gate_name = "CTGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, np.round(np.exp(i * np.pi / 4), 6)]
        ], dtype=complex)

        super(CTGate, self).__init__(_matrix)

    def args(self):
        return ()


class CHGate(Gate):
    """
    Applies Controlled-T on two qubits.
    """

    gate_id = 29
    gate_name = "CHGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1 / np.sqrt(2), 1 / np.sqrt(2)],
            [0, 0, 1 / np.sqrt(2), -1 / np.sqrt(2)]
        ], dtype=complex)

        super(CHGate, self).__init__(_matrix)

    def args(self):
        return ()


class IIGate(Gate):
    """
    Applies II on two qubits.
    """

    gate_id = 30
    gate_name = "IIGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=complex)

        super(IIGate, self).__init__(_matrix)

    def args(self):
        return ()


class SWAPGate(Gate):
    """
    Applies SWAP on two qubits.
    """

    gate_id = 31
    gate_name = "SWAPGate"
    qubit_shape = 2
    dimension = 2
    stim_alias = "SWAP"

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)

        super(SWAPGate, self).__init__(_matrix)

    def args(self):
        return ()


class ISWAPGate(Gate):
    """
    Applies iSWAP on two qubits.
    """

    gate_id = 32
    gate_name = "iSWAPGate"
    qubit_shape = 2
    dimension = 2
    stim_alias = "ISWAP"

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, i, 0],
            [0, i, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)

        super(ISWAPGate, self).__init__(_matrix)

    def args(self):
        return ()


class XXGate(Gate):
    """
    Applies XX on two qubits.
    """

    gate_id = 33
    gate_name = "XXGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.cos(angle), 6), 0, 0, np.round(-i * np.sin(angle), 6)],
            [0, np.round(np.cos(angle), 6), np.round(-i * np.sin(angle), 6), 0],
            [0, np.round(-i * np.sin(angle), 6), np.round(np.cos(angle), 6), 0],
            [np.round(-i * np.sin(angle), 6), 0, 0, np.round(np.cos(angle), 6)]
        ], dtype=complex)

        super(XXGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class YYGate(Gate):
    """
    Applies YY on two qubits.
    """

    gate_id = 34
    gate_name = "YYGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.cos(angle), 6), 0, 0, np.round(i * np.sin(angle), 6)],
            [0, np.round(np.cos(angle), 6), np.round(-i * np.sin(angle), 6), 0],
            [0, np.round(-i * np.sin(angle), 6), np.round(np.cos(angle), 6), 0],
            [np.round(i * np.sin(angle), 6), 0, 0, np.round(np.cos(angle), 6)]
        ], dtype=complex)

        super(YYGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class ZZGate(Gate):
    """
    Applies ZZ on two qubits.
    """

    gate_id = 35
    gate_name = "ZZGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [np.round(np.exp(i * angle / 2), 6), 0, 0, 0],
            [0, np.round(np.exp(-i * angle / 2), 6), 0, 0],
            [0, 0, np.round(np.exp(-i * angle / 2), 6), 0],
            [0, 0, 0, np.round(np.exp(i * angle / 2), 6)]
        ], dtype=complex)

        super(ZZGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class MSGate(Gate):
    """
      Applies Mølmer-Sørensen on two qubits.
    """

    gate_id = 36
    gate_name = "MSGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, i],
            [0, 1, i, 0],
            [0, i, 1, 0],
            [i, 0, 0, 1]
        ], dtype=complex)

        super(MSGate, self).__init__(_matrix)

    def args(self):
        return ()


class MagicGate(Gate):
    """
      Applies Magic on two qubits.
    """

    gate_id = 37
    gate_name = "MagicGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, i, 0, 0],
            [0, 0, i, 1],
            [0, 0, i, -1],
            [1, -i, 0, 0]
        ], dtype=complex)

        super(MagicGate, self).__init__(_matrix)

    def args(self):
        return ()


class CVGate(Gate):
    """
      Applies Controlled-V on two qubits.
    """

    gate_id = 38
    gate_name = "CVGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, (1 + i) / 2, (1 - i) / 2],
            [0, 0, (1 - i) / 2, (1 + i) / 2]
        ], dtype=complex)

        super(CVGate, self).__init__(_matrix)

    def args(self):
        return ()


class XYGate(Gate):
    """
      Applies XY on two qubits.
    """

    gate_id = 39
    gate_name = "XYGate"
    qubit_shape = 2
    dimension = 2
    default_angle = np.pi

    def __init__(self, angle=None):
        self.angle = angle
        if angle is None:
            self.angle = self.default_angle

        _matrix = np.array([
            [1, 0, 0, 0],
            [0, np.round(np.cos(angle), 6), np.round(-i * np.sin(angle), 6), 0],
            [0, np.round(-i * np.sin(angle), 6), np.round(np.cos(angle), 6), 0],
            [0, 0, 0, 1]
        ], dtype=complex)

        super(XYGate, self).__init__(_matrix)

    def args(self):
        return self.angle,


class DCXGate(Gate):
    """
      Applies Double Controlled-X gate on two qubits.
    """

    gate_id = 40
    gate_name = "DCXGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 1, 0, 0],
            [0, 0, 1, 0]
        ], dtype=complex)

        super(DCXGate, self).__init__(_matrix)

    def args(self):
        return ()


class BSWAPGate(Gate):
    """
      Applies bSWAP gate on two qubits.
    """

    gate_id = 41
    gate_name = "bSWAPGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [0, 0, 0, -i],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-i, 0, 0, 0]
        ], dtype=complex)

        super(BSWAPGate, self).__init__(_matrix)

    def args(self):
        return ()


class QFTGate(Gate):
    """
      Applies QFTGate gate on two qubits.
    """

    gate_id = 42
    gate_name = "QFTGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 1, 1, 1],
            [1, i, -1, -i],
            [1, -1, 1, -1],
            [1, -i, -1, i]
        ], dtype=complex) * 1 / 2

        super(QFTGate, self).__init__(_matrix)

    def args(self):
        return ()


class WGate(Gate):
    """
      Applies WGate gate on two qubits.
    """

    gate_id = 43
    gate_name = "WGate"
    qubit_shape = 2
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0],
            [0, 1 / np.sqrt(2), 1 / np.sqrt(2), 0],
            [0, 1 / np.sqrt(2), -1 / np.sqrt(2), 0],
            [0, 0, 0, 1]
        ], dtype=complex)

        super(WGate, self).__init__(_matrix)

    def args(self):
        return ()


class CCXGate(Gate):
    """
      Applies CCXGate gate on two qubits.
    """

    gate_id = 44
    gate_name = "CCXGate"
    qubit_shape = 3
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0]
        ], dtype=complex)

        super(CCXGate, self).__init__(_matrix)

    def args(self):
        return ()


class CSWAPGate(Gate):
    """
      Applies Controlled-SWAP on two qubits.
    """

    gate_id = 45
    gate_name = "CSWAPGate"
    qubit_shape = 3
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1]
        ], dtype=complex)

        super(CSWAPGate, self).__init__(_matrix)

    def args(self):
        return ()


class CCZGate(Gate):
    """
      Applies CCZ on two qubits.
    """

    gate_id = 46
    gate_name = "CCZGate"
    qubit_shape = 3
    dimension = 2

    def __init__(self):
        _matrix = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, -1]
        ], dtype=complex)

        super(CCZGate, self).__init__(_matrix)

    def args(self):
        return ()


predefined_gates: list[Gate] = [
    IDGate, RXGate, RYGate, RZGate, PauliX, PauliY, PauliZ,
    SGate, TGate, HGate, PsedoHGate, CRXGate, CXGate,
    CRYGate, CYGate, CRZGate, CZGate, CSGate, CTGate, CHGate,
    IIGate, SWAPGate, ISWAPGate, XXGate, YYGate, ZZGate,
    MSGate, MagicGate, CVGate, XYGate, DCXGate, BSWAPGate,
    QFTGate, WGate, CCXGate, CSWAPGate, CCZGate
]

gate_id_to_gate = dict()
gate_id_to_gate_name = dict()

gate_to_gate_id = dict()
gate_to_gate_name = dict()

for gate in predefined_gates:
    gate_id_to_gate[gate.gate_id] = gate
    gate_id_to_gate_name[gate.gate_id] = gate.gate_name
    gate_to_gate_id[gate] = gate.gate_id
    gate_to_gate_name[gate] = gate.gate_name
