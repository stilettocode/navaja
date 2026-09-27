# Real Quantum Hardware

A simulator stores an explicit mathematical state; a QPU samples physical measurements. Hardware adds shots, queue and network overhead, limited connectivity, two-qubit gate errors, readout errors, circuit depth, and transpilation.

This repository's optional IBM adapter uses PennyLane-Qiskit's `qiskit.remote` device. It creates a `QiskitRuntimeService`, selects either `IBM_QUANTUM_BACKEND` or an operational non-simulator backend with enough qubits, and injects that device into the same QAOA selector. The adapter reads `IBM_QUANTUM_TOKEN`, `IBM_QUANTUM_INSTANCE`, and related settings from the environment; credentials are never stored in source code.

The device factory is separate from the selector so tests and ordinary simulator runs never contact IBM. Start with a tiny problem and a small shot count. Parameter training always uses the local analytic simulator; remote optimization is disabled. Treat the first hardware run as an execution and measurement experiment, not as a performance benchmark.

The current integration uses PennyLane 0.45.x, PennyLane-Qiskit 0.45.0, and IBM Runtime's current service client. Provider APIs can change, so verify the installed package versions before a real submission.

The tournament commands reuse this adapter for each group. `make compare-ibm ARGS="--confirm-submit"` runs four classical tournaments and one hardware tournament; `make run-ibm ARGS="--confirm-submit"` runs the hardware tournament alone. With the default 30-page pool, each hardware tournament makes 46 group-level sampling calls after local parameter optimization. The flag authorizes all those calls, not just the first group. See [tournament selection](13-tournament-selection.md) for the rules, decision ledger, and exact call counts.

## Audited execution boundary

1. Validate candidate counts, exact selection size, shots, layers, iteration count, and seed locally.
2. Calculate the planned number of sampling calls. Refuse a workload above the configured ceiling before reading IBM configuration or constructing a client.
3. If `--dry-run` is present, print the plan and stop. Credentials and IBM packages are unnecessary; nothing is submitted or written to the ledger.
4. Require explicit confirmation for a nonzero hardware workload. Neither installed credentials nor `make install-ibm` enable hardware automatically.
5. Optimize each group's parameters on local `default.qubit` with analytic expectation values. No optimizer iteration contacts IBM. Local failures stop before remote-device creation.
6. On the first final sampling call, create one service client and select one eligible backend for the run. Reuse that backend for later groups, including smaller final groups.
7. Execute one finite-shot sampling circuit per nontrivial group. Decode and score the returned samples locally. Invalid-cardinality results use a labeled classical fallback instead of triggering another submission.

The only payload constructed for the hardware device is a numeric circuit plus execution settings such as shots. The adapter never supplies Markdown content, page titles, filenames, query text, or embeddings as provider metadata. Authentication credentials are used by the provider client in the normal way.

Byes, random survivor choices, classical comparisons, final scoring, and forced all/none selections do not need a quantum circuit. The full tournament's 46 calls remain necessary **to perform the requested hardware experiment at every solver group**; hardware is not necessary to select these pages classically. The application does not claim a quantum speedup or use hardware in default commands.

The factory requires explicit authorization even when called directly from Python. It enforces the exact planned device-call count and retains a backend only within that run. A failure consumes its attempted-call slot and propagates; the application does not retry, search alternate backends, or automatically resubmit. Provider libraries may have their own transport/job behavior, so application call counts are not a billing guarantee.

## Preview, submit, and limit work

```bash
make plan
make plan CANDIDATES=10 MAX_HARDWARE_CALLS=6
make plan-ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64
make ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64 ARGS=--confirm-submit
```

The default tournament cap is 46 calls, and the single-problem CLI cap is one. An over-budget plan fails before execution rather than returning a partial selection. `--dry-run` also works on `run-ibm`, `tournament`, and `compare-tournament`. It previews counts without checking account access, backend availability, installed bridge compatibility, or provider quotas.

Hardware runs are never cached automatically. Re-running a confirmed command requests fresh hardware measurements. The JSONL ledger retains completed tournament groups after a failure, but automatic resume is not implemented. See the [command reference](14-command-reference.md) for all commands and their defaults.
