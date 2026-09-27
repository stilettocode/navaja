import numpy as np

from .models import SelectionProblem


def score_selection(problem: SelectionProblem, selected_indices: list[int]) -> float:
    """Source of truth: reward relevance and penalize redundant selected pairs.

    Think of this as the ordinary Python version that we trust first. If a
    QUBO or quantum circuit disagrees with this function on a small bitstring,
    the representation is wrong; the quantum code does not get to redefine
    what a good context means.
    """
    selected = sorted(set(selected_indices))
    if any(index < 0 or index >= len(problem.page_ids) for index in selected):
        raise ValueError("selected index is outside the problem")
    # A selected page contributes its individual usefulness to the query.
    relevance = float(np.sum(problem.relevance[selected])) if selected else 0.0
    # Count each pair once. Similarity is a penalty only when both pages are
    # present, which is exactly what the binary product x_i * x_j expresses.
    redundancy = sum(
        float(problem.similarity_matrix[left, right])
        for position, left in enumerate(selected)
        for right in selected[position + 1 :]
    )
    return relevance - redundancy


def is_valid_selection(problem: SelectionProblem, selected_indices: list[int]) -> bool:
    selected = sorted(set(selected_indices))
    if problem.k is not None and len(selected) != problem.k:
        return False
    if problem.token_budget is not None and sum(problem.token_counts[selected]) > problem.token_budget:
        return False
    return True
