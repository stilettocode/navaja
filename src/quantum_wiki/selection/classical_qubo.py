import itertools

import numpy as np

from .models import SelectionProblem, SelectionResult
from .scoring import score_selection


class QUBO:
    """A readable quadratic model whose minimum represents the best selection.

    Beginner translation: this object is a spreadsheet of costs. Each candidate
    page gets a 0/1 column, and ``evaluate`` totals the rewards, pair penalties,
    and exact-K penalty for one proposed row of bits.
    """

    def __init__(self, linear: np.ndarray, quadratic: np.ndarray, offset: float = 0.0):
        self.linear = np.asarray(linear, dtype=float)
        self.quadratic = np.asarray(quadratic, dtype=float)
        self.offset = float(offset)
        if self.quadratic.shape != (len(self.linear), len(self.linear)):
            raise ValueError("quadratic coefficients must be square")

    def evaluate(self, bits: np.ndarray | list[int]) -> float:
        bits_array = np.asarray(bits, dtype=float)
        return float(self.offset + bits_array @ self.linear + bits_array @ self.quadratic @ bits_array)


def problem_to_qubo(problem: SelectionProblem, constraint_penalty: float = 10.0) -> QUBO:
    """Convert maximize-score into minimize-energy using an exact-K penalty.

    The ordinary scorer says "bigger is better". QAOA conventionally minimizes
    an energy, so we negate the relevance reward. The exact-K constraint is
    added as ``P * (number_selected - K)^2``:

    * choosing exactly K pages gives a zero constraint cost;
    * choosing K+1 or K-1 pages gives a positive cost;
    * expanding the square creates linear terms and pairwise terms because
      binary variables satisfy x*x == x.

    This is why a simple page-count rule becomes a denser QUBO: every pair of
    page variables receives part of the expanded constraint penalty.
    """
    if problem.k is None:
        raise ValueError("QUBO conversion currently requires exact k")
    size = len(problem.page_ids)
    # Energy is negative score. Redundancy is a pairwise relationship, and the
    # source objective counts each pair once.
    linear = -problem.relevance.copy()
    quadratic = np.zeros((size, size), dtype=float)
    for left in range(size):
        for right in range(left + 1, size):
            # Minimizing negative score means redundancy becomes a positive cost.
            quadratic[left, right] = problem.similarity_matrix[left, right]

    # Expanding P * (sum(x) - K)^2 gives:
    #
    #   P * [sum(x_i) + 2*sum(x_i*x_j) - 2*K*sum(x_i) + K^2]
    #
    # The first sum is linear, the second is pairwise, and the final value is
    # an offset. Writing this out connects the code to the formula above.
    linear += constraint_penalty * (1 - 2 * problem.k)
    for left in range(size):
        for right in range(left + 1, size):
            quadratic[left, right] += 2 * constraint_penalty
    return QUBO(linear, quadratic, constraint_penalty * problem.k**2)


def select_classical_qubo(problem: SelectionProblem, constraint_penalty: float = 10.0) -> SelectionResult:
    qubo = problem_to_qubo(problem, constraint_penalty)
    best_bits = min(itertools.product((0, 1), repeat=len(problem.page_ids)), key=qubo.evaluate)
    indices = [index for index, bit in enumerate(best_bits) if bit]
    return SelectionResult(indices, score_selection(problem, indices), {"problem_size": len(problem.page_ids), "qubo_energy": qubo.evaluate(best_bits)})
