# Qubits, States, and Amplitudes

Start with a map from bitstrings to complex-valued weights called amplitudes. For two qubits, a uniform state has amplitude `0.5` for `00`, `01`, `10`, and `11`; each probability is `|0.5|^2 = 0.25`. Probabilities must sum to one. A phase is the direction of a complex amplitude; it may change interference even when its immediate probability does not.

The formal notation is a state vector such as `1/sqrt(2) |0> + 1/sqrt(2) |1>`. The state debugger makes this representation visible for one to three qubits. Real hardware does not literally expose a Python array; this is the simulator's mathematical model.
