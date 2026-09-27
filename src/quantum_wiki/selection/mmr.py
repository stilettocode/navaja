from .models import SelectionProblem, SelectionResult
from .scoring import score_selection


def select_mmr(problem: SelectionProblem, redundancy_weight: float = 1.0) -> SelectionResult:
    if problem.k is None:
        raise ValueError("MMR requires an exact k")
    selected: list[int] = []
    remaining = set(range(len(problem.page_ids)))
    while len(selected) < problem.k:
        choice = max(
            remaining,
            key=lambda index: problem.relevance[index]
            - redundancy_weight * max((problem.similarity_matrix[index, other] for other in selected), default=0.0),
        )
        selected.append(choice)
        remaining.remove(choice)
    return SelectionResult(selected, score_selection(problem, selected), {"problem_size": len(problem.page_ids)})
