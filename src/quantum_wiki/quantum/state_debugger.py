from dataclasses import dataclass

import numpy as np


def _single_qubit_matrix(matrix: np.ndarray, qubit: int, qubits: int) -> np.ndarray:
    result = np.array([[1.0 + 0j]])
    for position in range(qubits):
        result = np.kron(result, matrix if position == qubit else np.eye(2))
    return result


@dataclass
class StateSnapshot:
    label: str
    amplitudes: np.ndarray


class StateDebugger:
    """A deliberately small simulator for seeing the state after each operation.

    A simulator stores the full state vector so we can teach the concepts. A
    physical device does not hand us this complete list of amplitudes, which is
    one reason a simulator should not be confused with freely readable
    massively parallel classical storage.
    """

    def __init__(self, qubits: int):
        if not 1 <= qubits <= 3:
            raise ValueError("the educational debugger supports one to three qubits")
        self.qubits = qubits
        self.state = np.zeros(2**qubits, dtype=complex)
        self.state[0] = 1.0
        self.snapshots = [StateSnapshot("initial", self.state.copy())]

    def apply(self, matrix: np.ndarray, qubit: int, label: str) -> None:
        if not 0 <= qubit < self.qubits:
            raise ValueError("qubit index out of range")
        self.state = _single_qubit_matrix(matrix, qubit, self.qubits) @ self.state
        self.snapshots.append(StateSnapshot(label, self.state.copy()))

    def table(self) -> list[dict[str, float | str]]:
        rows = []
        for index, amplitude in enumerate(self.state):
            rows.append({
                "bitstring": format(index, f"0{self.qubits}b"),
                "amplitude": f"{amplitude.real:.3f} {amplitude.imag:+.3f}i",
                "magnitude": float(abs(amplitude)),
                "phase": float(np.angle(amplitude)),
                "probability": float(abs(amplitude) ** 2),
            })
        return rows


X = np.array([[0, 1], [1, 0]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def rx(angle: float) -> np.ndarray:
    return np.cos(angle / 2) * np.eye(2) - 1j * np.sin(angle / 2) * X


def rz(angle: float) -> np.ndarray:
    return np.array([[np.exp(-1j * angle / 2), 0], [0, np.exp(1j * angle / 2)]])
