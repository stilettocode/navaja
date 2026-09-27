from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SelectionProblem:
    page_ids: list[str]
    relevance: np.ndarray
    similarity_matrix: np.ndarray
    token_counts: np.ndarray
    k: int | None = None
    token_budget: int | None = None

    def __post_init__(self):
        size = len(self.page_ids)
        if self.relevance.shape != (size,):
            raise ValueError("relevance must have one value per page")
        if self.similarity_matrix.shape != (size, size):
            raise ValueError("similarity_matrix must be square")
        if self.token_counts.shape != (size,):
            raise ValueError("token_counts must have one value per page")
        if self.k is None and self.token_budget is None:
            raise ValueError("provide k or token_budget")
        if self.k is not None and not 0 <= self.k <= size:
            raise ValueError("k must be between zero and the number of pages")
        if self.token_budget is not None and self.token_budget < 0:
            raise ValueError("token_budget cannot be negative")


@dataclass
class SelectionResult:
    selected_indices: list[int]
    objective: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def bitstring(self) -> str:
        size = self.metadata.get("problem_size", max(self.selected_indices, default=-1) + 1)
        selected = set(self.selected_indices)
        return "".join("1" if index in selected else "0" for index in range(size))
