import numpy as np

from .models import SelectionProblem, SelectionResult
from .scoring import score_selection


def select_topk(problem: SelectionProblem) -> SelectionResult:
    if problem.k is None:
        raise ValueError("Top-K requires an exact k")
    indices = list(np.argsort(-problem.relevance)[: problem.k])
    return SelectionResult(indices, score_selection(problem, indices), {"problem_size": len(problem.page_ids)})
