# Limitations and Honest Claims

- QAOA does not automatically provide quantum advantage.
- Classical Top-K, MMR, brute force, or integer optimization may vastly outperform it for these sizes.
- State-vector simulation is classical and needs roughly `2^N` amplitudes.
- Small experiments cannot demonstrate production speedup.
- Data loading and embedding costs matter in a real system.
- Current hardware introduces readout and gate noise, connectivity limits, transpilation overhead, and queue/network latency.
- The current deterministic hash embedding is a testable baseline, not a semantic model.
- The current NumPy QAOA path is explicitly a surrogate distribution, not a claim of PennyLane execution.

The repository succeeds when it makes these limitations measurable and understandable.
