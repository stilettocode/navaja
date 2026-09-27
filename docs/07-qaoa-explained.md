# QAOA Explained

QAOA is a hybrid loop. A CPU chooses parameters called gamma and beta, a quantum circuit applies cost and mixer operations, measurements produce bitstrings, and the CPU updates the parameters. The circuit itself does not continuously converge.

```text
CPU parameters -> circuit -> shots/measurements -> classical objective -> CPU update
```

The cost layer turns score differences into phase differences. The mixer redistributes amplitude. Repeated layers use interference so some bitstrings can become more likely, but QAOA does not guarantee the optimum.

`p` is the number of cost/mixer repetitions and `shots` is how many measurements are taken. The repository uses PennyLane's `default.qubit` state-vector simulator when the `quantum` extra is installed. It also keeps a clearly labeled NumPy surrogate for environments without PennyLane. Neither path is a real quantum processor, and neither is evidence of quantum advantage.

For the exact-K selector, the QUBO includes a penalty for selecting the wrong number of pages. The circuit is allowed to explore all bitstrings, but bitstrings with the wrong number of `1` values receive a high energy and are rejected when samples are decoded. A future constrained mixer could avoid invalid states during the circuit itself, but the penalty method is easier to inspect first.
