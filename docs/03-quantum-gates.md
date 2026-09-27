# Quantum Gates

Think of a gate as a pure transformation: `new_state = gate_matrix @ old_state`. X flips a bit, H creates or removes a balanced superposition, Z changes a phase sign, RX and RZ rotate around axes, and CNOT conditionally flips a target based on a control. Matrices exist because multiplying a state vector by a matrix is a precise, composable description of these transformations.

The state debugger currently demonstrates H. The remaining matrices are represented in `quantum/state_debugger.py` as the next teaching surface.
