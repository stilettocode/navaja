from dataclasses import dataclass
from collections import Counter

import numpy as np

from .classical_qubo import problem_to_qubo
from .models import SelectionProblem, SelectionResult
from .scoring import is_valid_selection, score_selection
from .warm_start import DEFAULT_WARM_START_PATH, load_parameters, save_parameters


@dataclass
class QAOAConfig:
    layers: int = 1
    shots: int = 512
    iterations: int = 30
    seed: int = 7
    backend: str = "auto"
    warm_start_path: str = str(DEFAULT_WARM_START_PATH)
    use_warm_start: bool = True


class QAOASelector:
    """Run small exact-K QAOA experiments with a transparent fallback.

    QAOA means *Quantum Approximate Optimization Algorithm*. In programmer
    terms, it is a parameterized circuit inside a classical optimization loop:

        CPU chooses gamma/beta -> circuit -> measurements -> CPU updates them

    ``gamma`` controls how strongly the QUBO energy changes phase. ``beta``
    controls how strongly the mixer moves amplitude between possibilities. The
    circuit is not continuously learning; the outer CPU loop repeats it with
    new parameter values.

    ``backend='auto'`` uses PennyLane when installed and the educational
    surrogate otherwise. The fallback is deliberately labeled as a surrogate:
    it is useful for a zero-dependency demo, but it is not a quantum circuit.
    """

    def __init__(self, config: QAOAConfig | None = None, device_factory=None, optimization_device_factory=None):
        self.config = config or QAOAConfig()
        # A factory keeps provider-specific connection code outside this
        # selector. For example, IBM can supply a remote PennyLane device while
        # tests continue using default.qubit with no credentials.
        self.device_factory = device_factory
        if optimization_device_factory is not None:
            raise ValueError("QAOA optimization must stay local; remote optimization is disabled")

    def select(self, problem: SelectionProblem) -> SelectionResult:
        if problem.k is None or problem.token_budget is not None:
            raise ValueError("QAOA currently supports exact k only")
        if (self.config.shots < 1 or self.config.layers < 1 or self.config.iterations < 0
                or self.config.seed < 0):
            raise ValueError("require shots >= 1, layers >= 1, iterations >= 0, seed >= 0")
        if len(problem.page_ids) > 12:
            raise ValueError("educational state-vector QAOA is limited to 12 candidates")
        if self.config.backend not in {"auto", "pennylane", "surrogate"}:
            raise ValueError("backend must be auto, pennylane, or surrogate")
        if self.device_factory and self.config.backend == "surrogate":
            raise ValueError("a remote device cannot be combined with the surrogate backend")
        if problem.k in (0, len(problem.page_ids)):
            indices = list(range(len(problem.page_ids))) if problem.k else []
            return SelectionResult(indices, score_selection(problem, indices), {
                "problem_size": len(problem.page_ids), "backend": "classical forced selection",
                "shots": 0, "iterations": 0, "fallback_used": False,
                "sampling_calls": 0, "reason": "exact k leaves only one possible selection",
            })
        if self.config.backend in {"auto", "pennylane"}:
            try:
                return self._select_pennylane(problem)
            except ImportError:
                if self.config.backend == "pennylane" or self.device_factory:
                    raise
        return self._select_surrogate(problem)

    def _energy_table(self, problem: SelectionProblem) -> np.ndarray:
        qubo = problem_to_qubo(problem)
        # PennyLane orders probabilities by the displayed bitstring index:
        # 00, 01, 10, ... . Building the table in that same order prevents a
        # measured bitstring from being decoded as the wrong set of pages.
        return np.array([
            qubo.evaluate([int(bit) for bit in format(state, f"0{len(problem.page_ids)}b")])
            for state in range(2 ** len(problem.page_ids))
        ])

    def _select_surrogate(self, problem: SelectionProblem) -> SelectionResult:
        rng = np.random.default_rng(self.config.seed)
        energies = self._energy_table(problem)
        probabilities = np.exp(-energies - np.max(-energies))
        probabilities /= probabilities.sum()
        samples = rng.choice(len(probabilities), size=self.config.shots, p=probabilities)
        valid = []
        for sample in samples:
            indices = [index for index, bit in enumerate(format(sample, f"0{len(problem.page_ids)}b")) if bit == "1"]
            if is_valid_selection(problem, indices):
                valid.append(indices)
        fallback_used = not valid
        if fallback_used:
            valid = [list(np.argsort(-problem.relevance)[: problem.k])]
        best = max(valid, key=lambda indices: score_selection(problem, indices))
        return SelectionResult(best, score_selection(problem, best), {
            "problem_size": len(problem.page_ids),
            "backend": "numpy educational surrogate",
            "shots": self.config.shots,
            "iterations": self.config.iterations,
            "fallback_used": fallback_used,
            "warning": "This is a transparent surrogate distribution, not a quantum-circuit result.",
        })

    def _select_pennylane(self, problem: SelectionProblem) -> SelectionResult:
        try:
            import pennylane as qml
            from pennylane import numpy as pnp
        except ImportError:
            raise ImportError(
                "PennyLane is required for backend='pennylane'. "
                "Use the project interpreter: .venv/Scripts/python.exe -m pip install -e \".[quantum,ibm]\""
            )

        qubits = len(problem.page_ids)
        energies = self._energy_table(problem)
        ideal_device = qml.device("default.qubit", wires=qubits, shots=None)
        cost_matrix = pnp.diag(energies)

        @qml.qnode(ideal_device, interface="autograd")
        def expectation(parameters):
            gamma = parameters[: self.config.layers]
            beta = parameters[self.config.layers :]
            for wire in range(qubits):
                qml.Hadamard(wires=wire)
            for layer in range(self.config.layers):
                # The diagonal unitary applies exp(-i * gamma * energy) to
                # each bitstring. This is the cost layer's phase encoding.
                qml.DiagonalQubitUnitary(pnp.exp(-1j * gamma[layer] * energies), wires=range(qubits))
                # RX mixes |0> and |1>, giving phase differences a chance to
                # become measurable probability differences through interference.
                for wire in range(qubits):
                    qml.RX(2 * beta[layer], wires=wire)
            return qml.expval(qml.Hermitian(cost_matrix, wires=range(qubits)))

        loaded_parameters = load_parameters(
            self.config.warm_start_path,
            candidate_count=qubits,
            k=problem.k,
            layers=self.config.layers,
        ) if self.config.use_warm_start else None
        warm_start_used = loaded_parameters is not None
        if loaded_parameters is None:
            # The first run starts from a neutral, small rotation. Later runs
            # can reuse JSON parameters as a warm start and refine them for
            # the new query's QUBO.
            loaded_parameters = np.array([0.1] * (2 * self.config.layers))
        parameters = pnp.array(loaded_parameters, requires_grad=True)
        optimizer = qml.AdamOptimizer(stepsize=0.1)
        history = []
        for iteration in range(self.config.iterations):
            parameters, energy = optimizer.step_and_cost(expectation, parameters)
            history.append(float(energy))

        optimized_parameters = np.asarray(parameters, dtype=float)
        if self.config.use_warm_start:
            save_parameters(
                self.config.warm_start_path,
                candidate_count=qubits,
                k=problem.k,
                layers=self.config.layers,
                parameters=optimized_parameters,
                objective=history[-1] if history else float(expectation(parameters)),
            )

        sample_device = (
            self.device_factory(qubits, self.config.shots)
            if self.device_factory
            else qml.device("default.qubit", wires=qubits, shots=None, seed=self.config.seed)
        )

        # Shots belong to this sampling QNode, not the device. Keeping the
        # analytic optimization QNode separate makes it clear that training
        # uses an expectation value while the final result uses measurements.
        @qml.qnode(sample_device, shots=self.config.shots)
        def sample():
            gamma = parameters[: self.config.layers]
            beta = parameters[self.config.layers :]
            for wire in range(qubits):
                qml.Hadamard(wires=wire)
            for layer in range(self.config.layers):
                qml.DiagonalQubitUnitary(pnp.exp(-1j * gamma[layer] * energies), wires=range(qubits))
                for wire in range(qubits):
                    qml.RX(2 * beta[layer], wires=wire)
            return qml.sample()

        measured = np.asarray(sample())
        if measured.ndim == 1:
            measured = measured.reshape(1, -1)
        counts = Counter("".join(str(int(bit)) for bit in row) for row in measured)
        candidates = []
        for measured_bits in measured:
            indices = [index for index, bit in enumerate(measured_bits) if int(bit) == 1]
            if is_valid_selection(problem, indices):
                candidates.append(indices)
        fallback_used = not candidates
        if fallback_used:
            candidates = [list(np.argsort(-problem.relevance)[: problem.k])]
        best = max(candidates, key=lambda indices: score_selection(problem, indices))
        return SelectionResult(best, score_selection(problem, best), {
            "problem_size": qubits,
            "backend": "remote PennyLane device" if self.device_factory else "PennyLane default.qubit",
            "shots": self.config.shots,
            "iterations": self.config.iterations,
            "layers": self.config.layers,
            "fallback_used": fallback_used,
            "optimization_backend": "PennyLane default.qubit",
            "sampling_calls": 1,
            "counts": dict(sorted(counts.items())),
            "valid_shots": sum(count for bits, count in counts.items() if bits.count("1") == problem.k),
            "warm_start_path": self.config.warm_start_path,
            "warm_start_used": warm_start_used,
            "energy_history": history,
            "gamma": [float(value) for value in parameters[: self.config.layers]],
            "beta": [float(value) for value in parameters[self.config.layers :]],
        })
