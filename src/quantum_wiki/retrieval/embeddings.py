import hashlib
import re

import numpy as np


class HashEmbeddingModel:
    """Deterministic local baseline; useful when model downloads are undesirable."""

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def encode(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimensions, dtype=float)
        words = re.findall(r"[a-z0-9]+", text.lower())
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            vector[index] += 1.0
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector
