# QUBO Explained

QUBO is easiest to read as a score written with binary variables. `+0.9 A` rewards choosing page A. `+0.7 A B` is a cost in an energy-minimization convention: it makes choosing two highly similar pages less attractive. The exact sign depends on whether we maximize score or minimize energy.

The source objective is:

```text
score = sum(relevance[i] * xi) - sum(similarity[i,j] * xi * xj)
```

An exact-K penalty adds `penalty * (sum(xi) - K)^2`. For binary values, `xi^2 = xi`, so this expands into linear and pairwise coefficients. In matrix notation, `x^T Q x` means multiply a vector of bits by a coefficient matrix and combine its linear/quadratic terms. The matrix is a compact representation of the same evaluator, not new business logic.

`tests/test_selection.py` checks every valid small bitstring against the ordinary scorer. We do this before involving quantum terminology.
