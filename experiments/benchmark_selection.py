"""Offline exploratory benchmark; does not alter production tournament defaults.

Run: .venv/Scripts/python.exe experiments/benchmark_selection.py
Timings exclude imports, retrieval, and console/ledger I/O. Split experiments
use exact group solves to separate grouping effects from QAOA sampling noise.
"""

import json
from pathlib import Path
import random
from statistics import median
from time import perf_counter

import numpy as np

from quantum_wiki.cli import build_problem
from quantum_wiki.selection.brute_force import select_brute_force
from quantum_wiki.selection.mmr import select_mmr
from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.qaoa import QAOAConfig, QAOASelector
from quantum_wiki.selection.scoring import score_selection
from quantum_wiki.selection.tournament import select_tournament


QUERIES = [
    "How do I solve shortest path and graph traversal problems on LeetCode?",
    "How can I find contiguous subarrays with a target sum and negative numbers?",
    "How do I solve dynamic programming coin change and knapsack problems?",
    "How can I validate binary search trees and find their kth smallest element?",
    "How do I merge intervals and schedule overlapping meetings?",
    "How should I debug and test a backtracking solution with duplicate values?",
]


def split_tournament(problem, primary_count, seed, *, random_survivor=True, condition_recovery=True):
    """Experimental 4+4, 5+3, 6+2 variants; same shuffle/survival rules.

    Clamp elimination to the target if necessary; a final <=5 group keeps
    target-1 exact choices plus a random reject. These are benchmark-only rules.
    """
    grouping = random.Random(seed)
    survival = random.Random(seed + 1)
    calls = 0

    def reduce(pool, target, anchors):
        nonlocal calls
        discarded = []
        while len(pool) > target:
            grouping.shuffle(pool)
            next_pool = []
            removals_left = len(pool) - target
            for offset in range(0, len(pool), 5):
                group = pool[offset:offset + 5]
                if (len(group) < 5 and len(pool) > 5) or removals_left == 0:
                    next_pool.extend(group)
                    continue
                keep = target if len(pool) <= 5 else 4
                relevance = problem.relevance[group].copy()
                if anchors and condition_recovery:
                    relevance -= problem.similarity_matrix[np.ix_(group, anchors)].sum(axis=1)
                subproblem = SelectionProblem([problem.page_ids[i] for i in group], relevance,
                    problem.similarity_matrix[np.ix_(group, group)], problem.token_counts[group], k=keep-1 if random_survivor else keep)
                chosen = select_brute_force(subproblem).selected_indices
                rejected = [i for i in range(len(group)) if i not in chosen]
                survivor = survival.choice(rejected) if random_survivor else None
                next_pool.extend(group[i] for i in range(len(group)) if i in chosen or i == survivor)
                discarded.extend(group[i] for i in rejected if i != survivor)
                removals_left -= len(group) - keep
                calls += 1
            pool = next_pool
        return pool, discarded

    primary, rejects = reduce(list(range(len(problem.page_ids))), primary_count, [])
    recovery, _ = reduce(rejects, 8 - primary_count, primary)
    selected = sorted(primary + recovery)
    assert len(selected) == len(set(selected)) == 8
    return selected, calls


def greedy_with_swaps(problem):
    """Greedy marginal *sum* objective, followed by best improving one-swaps."""
    selected = []
    remaining = set(range(len(problem.page_ids)))
    while len(selected) < problem.k:
        choice = max(sorted(remaining), key=lambda i: problem.relevance[i]
                     - sum(problem.similarity_matrix[i, j] for j in selected))
        selected.append(choice)
        remaining.remove(choice)
    while True:
        improvement, swap = 1e-12, None
        for old in sorted(selected):
            rest = [i for i in selected if i != old]
            old_marginal = problem.relevance[old] - sum(problem.similarity_matrix[old, j] for j in rest)
            for new in sorted(remaining):
                gain = problem.relevance[new] - sum(problem.similarity_matrix[new, j] for j in rest) - old_marginal
                if gain > improvement:
                    improvement, swap = gain, (old, new)
        if swap is None:
            return sorted(selected)
        old, new = swap
        selected.remove(old)
        selected.append(new)
        remaining.remove(new)
        remaining.add(old)


def main():
    problems = [build_problem(query, 30, 8)[1] for query in QUERIES]
    rows = []
    for query, problem in zip(QUERIES, problems, strict=True):
        for primary in (4, 5, 6):
            for seed in range(20):
                selected, calls = split_tournament(problem, primary, seed)
                if primary == 5:
                    actual = select_tournament(problem, select_brute_force, seed=seed)
                    assert selected == actual.selected_indices
                    assert calls == actual.metadata["group_calls"]
                rows.append({"query": query, "primary": primary, "recovery": 8-primary,
                             "seed": seed, "score": score_selection(problem, selected), "calls": calls})
    timings = {}
    problem = problems[0]
    # Import before timing, and use independent cold parameters for each QAOA group.
    import pennylane  # noqa: F401
    for name, solver in {
        "direct_mmr": lambda: select_mmr(problem).selected_indices,
        "direct_greedy_swaps": lambda: greedy_with_swaps(problem),
        "tournament_mmr": lambda: select_tournament(problem, select_mmr, seed=7).selected_indices,
        "tournament_exact_groups": lambda: select_tournament(problem, select_brute_force, seed=7).selected_indices,
        "tournament_local_qaoa": lambda: select_tournament(problem, QAOASelector(QAOAConfig(
            iterations=3, shots=128, layers=1, seed=7, backend="pennylane", use_warm_start=False)).select,
            seed=7).selected_indices,
    }.items():
        durations = []
        for _ in range(3):
            start = perf_counter()
            selected = solver()
            durations.append(perf_counter() - start)
        timings[name] = {"median_seconds": median(durations), "score": score_selection(problem, selected)}

    splits = {}
    for primary in (4, 5, 6):
        subset = [row for row in rows if row["primary"] == primary]
        splits[f"{primary}+{8-primary}"] = {
            "mean_score": float(np.mean([row["score"] for row in subset])),
            "mean_within_query_seed_std": float(np.mean([
                np.std([row["score"] for row in subset if row["query"] == query]) for query in QUERIES])),
            "calls": sorted({row["calls"] for row in subset}),
        }
    baselines = []
    for query, problem in zip(QUERIES, problems, strict=True):
        baselines.append({"query": query, "direct_mmr": select_mmr(problem).objective,
                          "direct_greedy_swaps": score_selection(problem, greedy_with_swaps(problem)),
                          "seed7_tournament": select_tournament(problem, select_brute_force, seed=7).objective})
    seed_scores = {seed: float(np.mean([row["score"] for row in rows
                                       if row["primary"] == 5 and row["seed"] == seed])) for seed in range(20)}
    report = {"queries": QUERIES, "seeds": list(range(20)), "timings": timings,
              "splits": splits, "baselines": baselines, "seed_means_5_plus_3": seed_scores, "rows": rows,
              "caveat": "Exploratory current-objective scores, not held-out answer-quality evaluation or global optima."}
    destination = Path(__file__).resolve().parent / "results" / "selection-benchmark.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"rows", "queries", "seeds"}}, indent=2))
    print(f"Full report: {destination}")


if __name__ == "__main__":
    main()
