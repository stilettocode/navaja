from itertools import combinations

from .models import SelectionProblem, SelectionResult
from .scoring import score_selection


def select_brute_force(problem: SelectionProblem) -> SelectionResult:
    if problem.k is None:
        raise ValueError("brute force currently supports exact k only")
    best_indices: tuple[int, ...] = ()
    best_score = float("-inf")
    for indices in combinations(range(len(problem.page_ids)), problem.k):
        score = score_selection(problem, list(indices))
        if score > best_score:
            best_score, best_indices = score, indices
    return SelectionResult(list(best_indices), best_score, {"problem_size": len(problem.page_ids), "exact": True})
