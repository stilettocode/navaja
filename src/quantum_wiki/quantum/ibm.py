"""Optional IBM Quantum device integration.

This module is intentionally separate from the selector. Retrieval, scoring,
and the simulator remain usable without an IBM account or network access.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class IBMQuantumConfig:
    """Connection settings read from the environment, never hard-coded."""

    token: str
    instance: str | None = None
    backend_name: str | None = None
    channel: str = "ibm_quantum_platform"

    @classmethod
    def from_environment(cls) -> "IBMQuantumConfig":
        token = os.environ.get("IBM_QUANTUM_TOKEN")
        if not token:
            raise RuntimeError("Set IBM_QUANTUM_TOKEN before using IBM Quantum hardware")
        return cls(
            token=token,
            instance=os.environ.get("IBM_QUANTUM_INSTANCE") or None,
            backend_name=os.environ.get("IBM_QUANTUM_BACKEND") or None,
            channel=os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform"),
        )

    def display_summary(self) -> str:
        """Return safe-to-print settings without exposing the API token."""
        return (
            f"channel={self.channel}, "
            f"instance={self.instance or '<account default>'}, "
            f"backend={self.backend_name or '<least-busy eligible backend>'}, "
            "token=<configured>"
        )


class IBMDeviceFactory:
    """Lazily connect once per authorized run, with a fixed device-call budget.

    Construction does not import provider packages or contact IBM. The QAOA
    selector calls this only after local parameter optimization succeeds.
    The budget bounds application sampling calls, not provider billing/jobs.
    """

    def __init__(self, config: IBMQuantumConfig, *, confirm_submit: bool = False,
                 max_calls: int = 1, max_qubits: int = 5):
        if not confirm_submit:
            raise ValueError("IBM requires explicit confirm_submit=True")
        if max_calls < 1 or not 1 <= max_qubits <= 12:
            raise ValueError("require max_calls >= 1 and 1 <= max_qubits <= 12")
        self.config = config
        self.max_calls = max_calls
        self.max_qubits = max_qubits
        self.calls = 0
        self._backend = None

    def __call__(self, qubits: int, shots: int):
        if not 1 <= qubits <= self.max_qubits or shots < 1:
            raise ValueError("invalid IBM device size or shot count")
        if self.calls >= self.max_calls:
            raise RuntimeError("IBM hardware-call budget exhausted; no additional device created")
        # Reserve the call before any provider work; failures do not silently retry.
        self.calls += 1
        import pennylane as qml
        from qiskit_ibm_runtime import QiskitRuntimeService

        if self._backend is None:
            settings = self.config
            service = QiskitRuntimeService(
                channel=settings.channel, token=settings.token, instance=settings.instance,
            )
            backend = (service.backend(settings.backend_name) if settings.backend_name
                       else service.least_busy(operational=True, simulator=False,
                                               min_num_qubits=self.max_qubits))
            if backend.num_qubits < self.max_qubits:
                raise ValueError(f"IBM backend {backend.name} has fewer than {self.max_qubits} qubits")
            self._backend = backend
        # Shots belong to the final sampling QNode. Page text and IDs are not
        # passed to the provider; it receives the numeric circuit and shots.
        return qml.device("qiskit.remote", wires=qubits, backend=self._backend)


def create_ibm_device(qubits: int, shots: int, config: IBMQuantumConfig | None = None,
                      *, confirm_submit: bool = False):
    """Explicitly authorized one-off device; tournaments reuse IBMDeviceFactory."""
    if not confirm_submit:
        raise ValueError("IBM requires explicit confirm_submit=True")
    return IBMDeviceFactory(config or IBMQuantumConfig.from_environment(),
                            confirm_submit=True, max_qubits=qubits)(qubits, shots)
