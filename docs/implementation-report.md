# Implementation Report

## Implemented

- Source-layout Python package with editable installation.
- Markdown wiki loader and seven overlapping sample pages.
- Deterministic hash embeddings and cosine retrieval fallback.
- Shared `SelectionProblem` and `SelectionResult` models.
- Top-K, greedy MMR, brute-force oracle, and classical exact-K QUBO solver.
- QUBO equivalence tests against the normal Python objective.
- One-to-three-qubit state debugger with amplitude, magnitude, phase, and probability output.
- Query, compare, and debug-circuit CLI commands.
- PennyLane `default.qubit` QAOA backend with configurable layers, shots, iterations, seed, parameter history, and explicit NumPy fallback.
- Optional IBM Quantum adapter through PennyLane-Qiskit's `qiskit.remote` device and environment-only credentials.
- IBM workflow separates local parameter optimization from remote final sampling by default.
- JSON warm-start layer for compatible QAOA parameter shapes.
- Educational overview, binary optimization, QUBO, QAOA, and limitations documents.

## Verified

The current suite passes nine tests. PennyLane 0.45.1, PennyLane-Qiskit 0.45.0, IBM Runtime 0.45.1, and NumPy 2.5.3 were installed in the project environment. The sample query, QAOA query, selector comparison, and two-qubit debugger were executed locally. Warm-start round-trip and compatibility tests pass. IBM configuration was tested without making a network or hardware request. The comparison reports objective gaps and does not report a quantum speed claim.

## Intentionally deferred

A parameterized PennyLane circuit and optional IBM adapter are now implemented. A real IBM submission has not been made because it requires the user's account, credentials, backend choice, queue, and usage consent. Token-budget/slack-variable mode, richer optimization reports, noise experiments, plots, notebooks, and real embedding model integration remain follow-up milestones.

## Design choices

The ordinary scorer is authoritative. QUBO converts maximization to energy minimization with an exact-K penalty. QAOA uses an analytic expectation-value QNode on `default.qubit` for local training and a separate shot-based QNode for final sampling. The simulator is still classical, so results are not hardware results.

## Learning demo

Run `python -m quantum_wiki.cli debug-circuit --qubits 2`, then read `docs/05-from-wiki-selection-to-binary-optimization.md` and `docs/06-qubo-explained.md`. Run the comparison command to see that quality and runtime claims must be measured rather than assumed.

## Extending

Add a selector accepting `SelectionProblem` and returning `SelectionResult`, then register it in `src/quantum_wiki/cli.py`. Change relevance or redundancy in `selection/scoring.py`, add an equivalence test, and rerun the suite. A hardware adapter should consume the same QUBO and return measured bitstrings without leaking backend details into retrieval.
