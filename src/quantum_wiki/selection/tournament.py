"""Seeded elimination with a second-chance tournament over all eliminated pages."""

from collections.abc import Callable
import random
from time import perf_counter

import numpy as np

from .models import SelectionProblem, SelectionResult
from .scoring import score_selection


def tournament_group_calls(candidate_count: int, group_size: int = 5) -> int:
    """Count solver calls before any work is submitted to hardware."""
    if candidate_count < 8:
        raise ValueError("tournament requires at least 8 candidates")
    if not 5 <= group_size <= 12:
        raise ValueError("group_size must be between 5 and 12")
    ordinary_keep = (group_size + 1) // 2 + 1
    calls = 0
    for size, target in ((candidate_count, 5), (candidate_count - 5, 3)):
        while size > target:
            if size <= group_size:
                calls += 1
                size = target
            else:
                full_groups = size // group_size
                calls += full_groups
                size -= full_groups * (group_size - ordinary_keep)
    return calls


def select_tournament(
    problem: SelectionProblem,
    selector: Callable[[SelectionProblem], SelectionResult],
    *,
    seed: int = 7,
    group_size: int = 5,
    on_event: Callable[[dict], None] | None = None,
) -> SelectionResult:
    """Select five primary pages and three distinct recovery pages.

    Full groups keep ceil(group_size/2) solver choices plus one random reject.
    Tails smaller than group_size receive a bye until the pool fits in one group.
    That last group keeps exactly the target, including one random survivor.
    Recovery relevance is conditioned on the fixed primary set, so its score
    is the marginal contribution to the final eight-page objective.
    """
    size = len(problem.page_ids)
    tournament_group_calls(size, group_size)  # Validate before any selector call.
    if size < 8 or problem.k != 8 or problem.token_budget is not None:
        raise ValueError("tournament requires at least 8 candidates, k=8, and no token budget")
    if len(set(problem.page_ids)) != size:
        raise ValueError("tournament page IDs must be unique")
    grouping_rng = random.Random(seed)
    survivor_rng = random.Random(seed + 1)
    events: list[dict] = []

    def emit(event):
        events.append(event)
        if on_event:
            on_event(event)

    def reduce_pool(pool, target, phase, anchors):
        discarded = []
        round_number = 0
        while len(pool) > target:
            round_number += 1
            pool = pool.copy()
            grouping_rng.shuffle(pool)
            next_pool = []
            for offset in range(0, len(pool), group_size):
                group = pool[offset : offset + group_size]
                final_group = len(pool) <= group_size
                keep = target if final_group else (group_size + 1) // 2 + 1
                if len(group) < group_size and not final_group:
                    next_pool.extend(group)
                    emit({"phase": phase, "round": round_number,
                          "group": offset // group_size + 1, "candidate_indices": group,
                          "candidate_ids": [problem.page_ids[i] for i in group],
                          "bye": True, "advance_bitstring": "1" * len(group),
                          "advanced_indices": group, "discarded_indices": []})
                    continue
                best_count = keep - 1
                relevance = problem.relevance[group].copy()
                if anchors:
                    relevance -= problem.similarity_matrix[np.ix_(group, anchors)].sum(axis=1)
                subproblem = SelectionProblem(
                    [problem.page_ids[i] for i in group], relevance,
                    problem.similarity_matrix[np.ix_(group, group)],
                    problem.token_counts[group], k=best_count,
                )
                started = perf_counter()
                result = selector(subproblem)
                elapsed = perf_counter() - started
                chosen = [int(i) for i in result.selected_indices]
                if (len(chosen) != best_count or len(set(chosen)) != best_count
                        or any(i < 0 or i >= len(group) for i in chosen)):
                    raise ValueError("group selector did not return a valid exact-k selection")
                rejected = [i for i in range(len(group)) if i not in chosen]
                survivor = survivor_rng.choice(rejected)
                advanced = [group[i] for i in range(len(group)) if i in chosen or i == survivor]
                eliminated = [group[i] for i in rejected if i != survivor]
                next_pool.extend(advanced)
                discarded.extend(eliminated)
                emit({"phase": phase, "round": round_number,
                      "group": offset // group_size + 1, "candidate_indices": group,
                      "candidate_ids": subproblem.page_ids, "bye": False,
                      "solver_k": best_count,
                      "solver_bitstring": "".join("1" if i in chosen else "0" for i in range(len(group))),
                      "advance_bitstring": "".join("1" if group[i] in advanced else "0" for i in range(len(group))),
                      "solver_selected_indices": [group[i] for i in chosen],
                      "random_survivor_index": group[survivor],
                      "advanced_indices": advanced, "discarded_indices": eliminated,
                      "solver_score": float(result.objective), "seconds": elapsed,
                      "solver_metadata": result.metadata})
            pool = next_pool
        return pool, discarded

    primary, recovery_pool = reduce_pool(list(range(size)), 5, "primary", [])
    recovery, final_discarded = reduce_pool(recovery_pool.copy(), 3, "recovery", primary)
    selected = sorted(primary + recovery)
    return SelectionResult(selected, score_selection(problem, selected), {
        "problem_size": size, "seed": seed, "group_size": group_size,
        "primary_indices": primary, "recovery_indices": recovery,
        "recovery_pool_indices": recovery_pool,
        "discarded_indices": final_discarded,
        "group_calls": sum(not event["bye"] for event in events),
        "events": events,
    })
