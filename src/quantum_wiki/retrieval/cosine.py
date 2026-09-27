import numpy as np


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Compare vector direction: similar meaning points in a similar direction."""
    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))
