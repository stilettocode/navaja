# Classical Optimizer Loop

The CPU owns the outer loop:

```text
params = initial_guess()
while not_done:
    measurements = run_quantum_circuit(params)
    value = evaluate_classically(measurements)
    params = optimizer.update(params, value)
```

Gamma controls cost-layer phase strength; beta controls mixer strength. Neither is a magic answer. They are tunable knobs updated by a classical optimizer across repeated circuit executions.

For this repository's IBM workflow, the repeated training circuit runs on the local PennyLane simulator. After the CPU finds a useful parameter set, a separate shot-based run sends the final circuit to IBM hardware. This avoids turning every gradient-estimation step into a remote workload.

The parameters are therefore more like query-specific optimization settings than universal model weights. Similar queries may warm-start from the same settings, but a changed QUBO can require new optimization.
