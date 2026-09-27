"""Small JSON persistence layer for reusable QAOA starting parameters."""

import json
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_WARM_START_PATH = Path("experiments/warm_starts/qaoa_parameters.json")


def _key(candidate_count: int, k: int, layers: int) -> str:
    return f"n={candidate_count};k={k};p={layers}"


def load_parameters(path: str | Path, candidate_count: int, k: int, layers: int) -> np.ndarray | None:
    """Load a compatible ``[gamma..., beta...]`` vector, if one exists.

    Compatibility is intentionally structural rather than page-specific. A
    new query can warm-start from an old query with the same circuit shape,
    even though its QUBO coefficients differ. The optimizer still refines the
    guess against the new problem.
    """
    file_path = Path(path)
    if not file_path.exists():
        return None
    try:
        document = json.loads(file_path.read_text(encoding="utf-8"))
        values = document.get("entries", {}).get(_key(candidate_count, k, layers), {}).get("parameters")
        if not isinstance(values, list) or len(values) != 2 * layers:
            return None
        return np.asarray(values, dtype=float)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def save_parameters(
    path: str | Path,
    candidate_count: int,
    k: int,
    layers: int,
    parameters: np.ndarray,
    objective: float,
) -> None:
    """Save parameters without ever saving page content or credentials."""
    file_path = Path(path)
    document: dict[str, Any] = {"version": 1, "entries": {}}
    if file_path.exists():
        try:
            loaded = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("entries"), dict):
                document = loaded
        except (OSError, json.JSONDecodeError):
            pass
    document.setdefault("version", 1)
    document.setdefault("entries", {})
    document["entries"][_key(candidate_count, k, layers)] = {
        "candidate_count": candidate_count,
        "k": k,
        "layers": layers,
        "parameters": [float(value) for value in parameters],
        "objective": float(objective),
    }
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
