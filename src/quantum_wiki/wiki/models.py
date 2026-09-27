from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class WikiPage:
    id: str
    path: Path
    title: str
    content: str
    embedding: np.ndarray | None = None

    @property
    def token_count(self) -> int:
        return len(self.content.split())
