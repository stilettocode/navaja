# QAOA Circuit Walkthrough

For a tiny selection problem, map each page to one qubit. Prepare a broad state, apply a cost operation derived from the QUBO, apply a mixer, and measure. Inspecting the state after each stage should answer: which amplitudes changed, did probabilities change yet, and which later operation creates interference?

The current reliable walkthrough is the `debug-circuit` command. A true PennyLane cost/mixer trace is intentionally deferred until it can be tested against the QUBO evaluator.
