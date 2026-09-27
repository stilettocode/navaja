# Local Performance and Tournament Parameter Review

This is an exploratory measurement of the current 30-page corpus and scoring function. It does not change the production 5+3 split or seed 7. No IBM calls were made.

Reproduce with:

```bash
.venv/Scripts/python.exe experiments/benchmark_selection.py
```

The script writes `experiments/results/selection-benchmark.json` (ignored by Git). It contains the six query texts, all 360 split/seed results, direct baselines, and timing measurements. Experimental split implementations live only in this script. Its 5+3 results and call counts are checked against the production implementation for all six queries and 20 seeds.

## Local runtime

For the default graph-traversal query, medians of three calls on the development machine were:

| Method | Selection time | Final objective |
| --- | ---: | ---: |
| Direct whole-pool MMR | 0.21 ms | -17.0023 |
| Direct marginal-score greedy plus improving one-page swaps | 1.14 ms | -16.2406 |
| MMR tournament | 1.96 ms | -16.5431 |
| Exact classical group tournament | 3.43 ms | -16.5673 |
| Local QAOA tournament | 1,148 ms | -16.5673 |

Timings exclude imports, retrieval, terminal output, and ledger writes. QAOA uses one layer, three optimization iterations per group, 128 shots, seed 7, and no warm-start files. This is one machine and one timed query; it is not an end-to-end service benchmark. Smaller times will vary with system load.

A five-page exact-three group has only ten feasible combinations. Simulating and optimizing a QAOA circuit is much more work than enumerating those combinations. The quantum workflow remains useful as an experiment, but is not the most time-efficient classical selector.

The direct greedy experiment uses the actual marginal change in the repository's sum-of-pairwise-similarities objective. It then tries replacing one selected page with one unselected page until no improving swap remains. Existing MMR instead penalizes maximum similarity to a selected page. These optimize different local choice rules. Greedy plus swaps beat the seed-7 exact-group tournament on all six tested queries, but is still a local heuristic, not a certified global optimum.

The QAOA implementation also builds a dense diagonal Hermitian matrix for local expectation calculations. At five qubits that matrix is small. For larger local circuits, computing expected energy as the dot product of basis probabilities and the energy vector would avoid the dense matrix. PennyLane supports [computational-basis probabilities](https://docs.pennylane.ai/en/stable/code/api/pennylane.probs.html). This is a proposed local optimization, not an implemented change or evidence of faster hardware circuits.

## Splits and seeds

Each split used the same six queries and seeds 0 through 19, with exact classical group solves. All final results contain eight pages. Higher scores are better.

| Primary + recovery | Mean final score | Mean within-query standard deviation across seeds | Group calls |
| --- | ---: | ---: | ---: |
| 4 + 4 | -16.0928 | 0.1145 | 48 |
| 5 + 3 | -16.1478 | 0.1363 | 46 |
| 6 + 2 | -16.2390 | 0.1684 | 44 |

The 4+4 split is a promising comparison candidate: a modestly higher mean objective and lower seed variability at the cost of two more group calls. The evidence is limited to this corpus, embedding representation, hand-written queries, and exact group solver. It does not establish better answer quality or predict the same ordering on noisy hardware.

For 5+3, seed 4 had the best mean score among the tested seeds; seed 7 was neither best nor worst. Selecting seed 4 after seeing this benchmark would tune to the evaluation set. Keep a fixed seed for reproducibility, and evaluate a predeclared list of seeds when comparing changes. Validate a proposed default on separate queries before calling it better. Running several seeds locally and selecting the best-scoring result is also a valid heuristic, but its extra work and selection rule must be reported consistently across methods.

## Priorities

For practical speed, use exact small-group classical solves or evaluate the whole-pool greedy-plus-swap baseline. For quantum experiments, the current five-qubit simulator is manageable; reducing the number of group solves matters more than polishing a 32-state representation. Five-to-four elimination is deliberately conservative and causes 46 calls in the default two-stage workflow.

For selection quality, inspect the scoring model before fine-tuning a seed. The current embedding hashes raw word counts into 256 dimensions, and the objective subtracts 28 pairwise similarities for eight chosen pages while adding eight relevance values. Shared vocabulary, collisions, and the balance between relevance and redundancy can strongly influence the selected pages. A better internal objective score is not a measurement of usefulness to a reader.

## Ignore-file review

Existing rules already covered `.env`, virtual environments, Python caches, root logs including `tournament-verification.log`, tournament JSONL ledgers, warm-start JSON, and generated experiment results. The review added `.env.*` variants while explicitly allowing `.env.example` and `.env.*.example`, plus coverage output and common tool caches.

Ten ignored artifact paths and five visible source/template paths were checked using Git in a separate temporary repository. The working folder has no accessible `.git` metadata, so tracked files and commit history could not be audited. Ignore rules do not affect files already tracked by Git; see the [Git documentation](https://git-scm.com/docs/gitignore).
