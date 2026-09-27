# Scientific Evaluation of Quantum Wiki Selection

## Main findings

This study completed **three real IBM hardware jobs**, 256 shots each, on **ibm_fez**. IBM reported **2 quantum seconds per job, 6 total**. No full hardware tournament was run, and no failed job was resubmitted. All three best-of-256 outputs matched the exact optimum for their five-page group. That outcome alone is weak evidence: even uniform sampling of all 32 bitstrings has a 98.28% chance of encountering the unique optimum within 128 shots.

The scientifically useful distinctions are (1) whether a selector improves the global eight-page objective, (2) whether that objective represents useful context, (3) whether QAOA changes the probability of feasible and high-quality solutions, and (4) how hardware changes the same fixed circuit's distribution. This report measures these separately.

The default three-iteration QAOA circuit did **not** consistently improve on uniform sampling: its per-shot optimum probability was below 1/32 on both primary test groups. Longer training mainly improved exact-cardinality probability in those groups; among valid selections, the optimum still received approximately one tenth of the mass.

**The most consequential quality finding is an objective/coverage mismatch.** Whole-pool greedy plus swaps achieved the highest internal score, yet recovered only 13.9% of the explicitly relevant topic-guide labels on the six new queries, versus 55.6% for Top-K. The labels are a limited proxy, but this reverses the ranking implied by objective score alone. Validate the relevance/redundancy model before spending more QPU time optimizing it.

## Questions, protocol, and budget

The protocol and query/seed choices were saved before the new outcomes were observed. Six queries repeat the earlier exploratory benchmark; six newly written queries test other topics. These are synthetic, author-chosen tasks over one fixed corpus, not a representative user sample or independently administered test set.

| Experiment | Scope | Purpose |
| --- | --- | --- |
| Whole-pool classical baselines | 12 queries, 30 candidates, exactly 8 winners | Separate tournament effects from ordinary selection |
| Split and seed sweep | 3 splits × 12 queries × 30 seeds = 1,080 tournaments | Estimate grouping/survivor sensitivity |
| Small global oracle | 12 queries, top 12 candidates, K=8; 30 tournament seeds each | Measure true global gaps on 495 feasible subsets |
| QAOA training sweep | 3 fixed five-page groups × 4 iteration budgets | Separate parameter training from best-of-many postselection |
| Hardware pilot | 3 jobs × 256 shots, p=1, 3 local iterations | Compare identical numeric problems and parameters with ideal distributions |
| Exploratory ablations | 2 changes × 12 queries × 30 seeds = 720 tournaments | Test random survival and recovery conditioning separately |

The ablations were chosen after reviewing the main results and are explicitly exploratory. All split/ablation groups use exact classical solves, eliminating quantum sampling noise as a confound. Production defaults remain 5+3, seed 7. No production selection policy was changed.

Hardware groups were selected by position, not by observed QAOA success: first primary group of original query 0, first primary group of original query 2, and first recovery group of original query 0, each from the seed-7 exact-group tournament. Recovery coefficients include redundancy against the five fixed primary winners. Each has N=5, K=3 and ten feasible subsets.

A durable attempt counter limited the pilot to three submissions, with a requested 60-second execution ceiling per job. The experiment stopped automatically on any error. Local optimization used the production PennyLane implementation; hardware used the production IBM device factory and PennyLane-Qiskit bridge. The experiment wrapped SamplerV2 only to enforce the cap, set the execution ceiling, and retain job IDs and circuit statistics. It did not replace the production ansatz with a different circuit.

## What was measured

- **Final objective:** relevance sum minus all selected pairwise similarities; higher is better. No ratios are used because scores can be negative.
- **Exact optimality gap:** brute-force optimum minus selected score, only for the separate N=12 problems or individual N=5 groups. No global N=30 optimum is claimed.
- **Feasible probability:** fraction of shots with exactly three ones, before any fallback.
- **Optimum probability:** fraction of all shots belonging to any optimum state; ties counted using absolute tolerance 1e-10.
- **Conditional quality:** mean score among valid shots, and optimum probability conditional on validity.
- **Distribution discrepancy:** total variation distance, one half the sum of absolute differences over all 32 states.
- **Runtime and resources:** local selection time, group calls, transpiled depth/two-qubit operations, hardware wall time, and provider-reported usage separately.
- **Topic coverage proxy:** fraction of 1–3 explicitly named relevant guide IDs recovered in eight selections on each new query. Labels were recorded before execution, but are author-created, incomplete, and not an answer-quality gold standard.

Seed outcomes are not treated as independent queries. Split comparisons first average the 30 seeds within each query; paired bootstrap intervals resample queries (10,000 resamples, bootstrap seed 271828). With only six new questions, these are descriptive sensitivity intervals, not strong population-level evidence. Multiple comparisons were not corrected, and no significance-based winner is declared.

## Classical selection and objective validity

| Method | Mean objective, all 12 queries | New-query topic coverage proxy | Median local selection time (ms) |
| --- | ---: | ---: | ---: |
| topk | -17.5060 | 55.6% | 0.021 |
| mmr | -16.5455 | 47.2% | 0.196 |
| greedy_swaps | -15.7932 | 13.9% | 0.690 |
| split_4_4 | -15.9497 | 38.5% | 3.488 |
| split_5_3 | -15.9982 | 40.7% | 3.345 |
| split_6_2 | -16.1075 | 46.0% | 3.172 |

Timing excludes corpus loading, retrieval, imports, console output, ledger writes, and network access. Direct baselines use a median of three invocations per query; tournament timings are individual runs pooled across seeds. These are engineering measurements on one machine, not speedup claims.

Top-K optimizes individual relevance only. Existing MMR uses maximum similarity to the selected set, whereas `greedy_swaps` uses the actual sum-based marginal objective and best improving single-page swaps. It terminates at a one-swap local optimum, not necessarily the global optimum.

The topic-coverage column is recall of the listed guide IDs, averaged equally across the six new queries. It does not penalize unlabelled useful pages and is not precision or answer accuracy. A uniformly random eight-page subset of this 30-page corpus would have expected label recall 8/30 = 26.7%. That analytical reference highlights the need for independent relevance evaluation; it is not a statistical test against a measured random control. The 4+4 split improves internal score but has lower topic-label coverage than 5+3, so the present evidence does not justify calling it a better user-facing default.

| Paired comparison on the six new queries | Mean objective change versus 5+3 | Descriptive query-bootstrap 95% interval |
| --- | ---: | --- |
| split_4_4 | +0.0431 | [+0.0160, +0.0710] |
| split_6_2 | -0.1194 | [-0.1337, -0.1029] |
| greedy_swaps | +0.1963 | [+0.1592, +0.2298] |

The 4+4, 5+3, and 6+2 splits require 48, 46, and 44 group calls respectively at N=30. A split changes the number of final primary and recovery winners; it does not mean every early survivor becomes a final winner. No seed was chosen as a new default after looking at these results.

### True global gaps on smaller candidate pools

| Method, N=12 and K=8 | Mean gap | Maximum gap | Exact-optimum fraction |
| --- | ---: | ---: | ---: |
| mmr | 0.18909 | 0.37812 | 0.0% |
| greedy_swaps | 0.00000 | 0.00000 | 100.0% |
| split_5_3 | 0.12885 | 0.52850 | 16.4% |

Direct methods have 12 observations; the tournament has 360 seed outcomes nested within 12 queries. These are different candidate pools from the N=30 experiment, so the absolute scores are not compared across pool sizes. The tournament gap includes elimination and grouping effects even though every local group solve is exact.

### Exploratory mechanism ablations

| Change to 5+3 | Mean final objective | Paired change versus default | Query-bootstrap 95% interval |
| --- | ---: | ---: | --- |
| no_random_survivor | -15.8222 | +0.1760 | [+0.1528, +0.1981] |
| no_recovery_conditioning | -16.3051 | -0.3069 | [-0.3519, -0.2632] |

`no_random_survivor` chooses the best four jointly in ordinary groups, and the best three in the last recovery group, instead of three-plus-random and two-plus-random respectively. It preserves the survivor count and 46-call schedule, but changes the local exact-K objective. It is not a test of simply deleting the extra survivor. `no_recovery_conditioning` leaves random survival intact but stops subtracting similarity to primary winners during recovery. Both variants reuse grouping seeds, although later group membership necessarily diverges.

## Simulator findings: feasibility is not the same as useful optimization

| Group | Local iterations | Exact valid probability | Exact optimum probability | Optimum given valid | Chance to see optimum within 128 shots |
| --- | ---: | ---: | ---: | ---: | ---: |
| query0_primary | 0 | 11.70% | 1.16% | 9.93% | 77.59% |
| query0_primary | 3 | 26.74% | 2.62% | 9.79% | 96.65% |
| query0_primary | 15 | 54.08% | 5.34% | 9.87% | 99.91% |
| query0_primary | 40 | 55.51% | 5.47% | 9.85% | 99.92% |
| query2_primary | 0 | 11.72% | 1.16% | 9.92% | 77.61% |
| query2_primary | 3 | 26.69% | 2.60% | 9.75% | 96.58% |
| query2_primary | 15 | 54.11% | 5.33% | 9.86% | 99.91% |
| query2_primary | 40 | 54.03% | 5.31% | 9.83% | 99.91% |
| query0_recovery | 0 | 13.58% | 1.33% | 9.81% | 82.03% |
| query0_recovery | 3 | 34.07% | 3.40% | 9.97% | 98.80% |
| query0_recovery | 15 | 26.11% | 2.62% | 10.02% | 96.64% |
| query0_recovery | 40 | 28.74% | 2.88% | 10.02% | 97.62% |

These are exact ideal probabilities, not estimates from the local 256-shot samples. All groups have a unique optimum. At zero iterations the initial angles are gamma=beta=0.1, **not** a uniform circuit. Uniform distributions are evaluated separately as analytical controls.

For uniform random five-bit strings: P(valid)=10/32=31.25%, P(optimum)=1/32=3.125%. For uniform sampling restricted to valid three-page subsets: P(valid)=100%, P(optimum)=1/10=10%. The latter is a cheap classical feasible-sampling baseline and reaches approximately 99.99986% optimum-hit probability at 128 draws. Without replacement, enumerating all ten feasible subsets guarantees the optimum.

The probability of at least one optimum in S independent shots is 1-(1-p)^S. This is why a high best-of-many success rate can coexist with little or no learned preference for the optimal feasible subset. Increasing iterations from 3 to 15 improved feasibility on the two primary groups, but did not consistently help the recovery group. It would be premature to increase all hardware training budgets based on three cases.

## Hardware pilot

| Group | Valid shots / 256 (95% Wilson interval) | Optimal shots / 256 | Best-score gap | TV from ideal | Ideal finite-shot TV central 95% band |
| --- | --- | ---: | ---: | ---: | --- |
| query0_primary | 81 (26.3%–37.6%) | 13 | 0.000000 | 0.2008 | [0.1013, 0.1760] |
| query2_primary | 74 (23.7%–34.7%) | 7 | 0.000000 | 0.1991 | [0.1008, 0.1754] |
| query0_recovery | 91 (29.9%–41.6%) | 6 | 0.000000 | 0.2098 | [0.1019, 0.1753] |

The finite-shot band comes from 2,000 simulated multinomial samples of 256 shots from each exact ideal distribution, using RNG seed 20260927. All observed hardware TV distances exceed these per-circuit reference bands. That is evidence of a mismatch with the ideal distribution in this pilot, not a noise-source diagnosis, a calibrated fidelity estimate, or a multiple-testing-corrected claim. Hardware temporal correlations and drift are not modeled by the multinomial calculation.

All three groups had valid samples and zero best-score gap, so no classical fallback was needed. We did not run a uniform-control hardware circuit or repeat the jobs across calibration periods. Thus hardware-vs-ideal differences cannot establish an advantage or stable performance ranking.

| Group | Ideal conditional mean score | Hardware conditional mean score | Hardware per-shot optimum probability (95% Wilson interval) |
| --- | ---: | ---: | --- |
| query0_primary | -1.531201 | -1.502151 | 5.08% [2.99%, 8.49%] |
| query2_primary | -1.723128 | -1.731080 | 2.73% [1.33%, 5.54%] |
| query0_recovery | -11.917874 | -11.956936 | 2.34% [1.08%, 5.02%] |

Conditional means include only exact-three samples and use each group's own objective. Recovery-group scores include the primary-set conditioning and must not be compared numerically with primary-group scores.

| IBM job ID | Backend | Transpiled depth | CZ gates | End-to-end pilot call (s) | Reported quantum usage (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| `dasn332hcrkc73dt1mog` | ibm_fez | 112 | 42 | 17.83 | 2 |
| `dasn35jg95ks73efodn0` | ibm_fez | 115 | 44 | 6.90 | 2 |
| `dasn37bojkfs738phle0` | ibm_fez | 170 | 42 | 6.34 | 2 |

Every circuit has **five logical decision qubits and five measurements**. The transpiled circuit object has 156 wire slots because it is laid out on the backend; this is not a 156-decision-variable experiment. Circuit depths above 100 despite p=1 reflect generic diagonal-unitary decomposition and routing. Backend layout, physical-qubit IDs, calibration snapshots, explicit transpiler seed, and mitigation configuration were not retained; these are important missing controls for a subsequent hardware replication. This run uses provider/plugin defaults rather than claiming their values.

IBM distinguishes QPU usage from queue and wall-clock duration; the usage values above are read from the completed jobs, not inferred from elapsed time. [IBM workload usage](https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time). The local-optimize/final-sample separation follows the usual hybrid workflow described in [IBM's QAOA tutorial](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm).

## Most useful next experiments, in priority order

1. **Validate the objective against independent usefulness labels.** Have a person grade relevance and complementary coverage on separate queries, without showing method identity. Tune relevance/redundancy weights on development queries only. Current hashed raw-word embeddings and 28 pairwise penalties versus eight relevance terms can reward the wrong article mix. The topic proxy here is only a diagnostic.
2. **Add exact and feasible-random baselines to every group-level quantum report.** Report the whole histogram, feasible mass, optimal mass, conditional score, fallback count, and matched shot budgets. Stop using a single winning bitstring as the primary evidence for quantum performance.
3. **Evaluate direct marginal greedy plus swaps and the no-random-survivor ablation on new tasks.** Compare final quality and latency while holding the original candidate pool and eight-page target fixed. Do not mistake exact group solutions for a global oracle.
4. **Test a constraint-preserving mixer or revised penalty/angle scaling locally.** The current optimizer appears to spend effort controlling cardinality without strongly discriminating among feasible answers. Compare conditional solution quality, not only energy or feasibility. This is a proposed mechanism test, not a conclusion that another ansatz will win.
5. **Compile the QUBO cost as single-Z and pairwise-ZZ terms before more hardware trials.** Compare ideal-state equivalence up to global phase, transpiled two-qubit gates, and depth against the generic diagonal-unitary implementation. A local compilation experiment costs no QPU usage.
6. **If hardware is repeated, use a small controlled replication.** Freeze parameters and physical layout; include a known-state bit-order check and a uniform reference; collect timestamps, calibration, transpilation seed, all options, and repeated jobs across time. Budget these separately rather than running a 46-call tournament or many seeds on hardware.

## Verification

The final offline regression run, `make test TEST_ARGS=-q`, passed **100 tests**. Checks include local-only and guarded hardware boundaries, tournament conservation and exact winner counts, histogram totals and bit order, analytical uniform controls, no-valid-shot handling, and zero-angle uniform probabilities. The saved pilot ledger was separately checked for exactly three submissions/results and 768 measured shots. These checks validate implementation consistency, not external scientific validity.

## Reproducibility and data

Local protocol timestamp: `2026-09-27T19:41:33.366665+00:00`. Python: `3.13.5`. Platform: `Windows-10-10.0.19045-SP0`.

| Package | Version |
| --- | --- |
| numpy | 2.5.3 |
| pennylane | 0.45.1 |
| pennylane-qiskit | 0.45.0 |
| qiskit | 2.3.0 |
| qiskit-ibm-runtime | 0.45.1 |

The protocol stores SHA-256 hashes for all 30 source pages. Exact group coefficients, parameters, ideal probabilities, raw local and hardware histograms, job IDs, operation counts, usage metrics, and all per-query/seed results are saved locally under `experiments/results/scientific-evaluation/`. This generated directory is intentionally ignored by Git; archive it separately alongside this report when sharing or publishing the study. No API token or instance identifier is written to the dataset. A local [reproduction archive](../experiments/results/scientific-evaluation-data.zip) includes the measured JSON data, source files, study scripts, corpus, package manifest, and this report, with no credentials or virtual environment.

```bash
# Local data collection only
.venv/Scripts/python.exe experiments/scientific_evaluation.py
# Analyze saved data and rebuild this report; does not call IBM
.venv/Scripts/python.exe experiments/build_scientific_report.py
# Run the offline regression suite
make test TEST_ARGS=-q
```

The hardware collection command is `.venv/Scripts/python.exe experiments/scientific_evaluation.py --hardware --confirm-submit`. It refuses to submit again when its saved state contains an earlier submission attempt. The three-job budget has already been used; reproducing the local analysis needs no new hardware jobs.

### Query list and limited topic labels

- Q0: How do I solve shortest path and graph traversal problems on LeetCode? Previously explored query.
- Q1: How can I find contiguous subarrays with a target sum and negative numbers? Previously explored query.
- Q2: How do I solve dynamic programming coin change and knapsack problems? Previously explored query.
- Q3: How can I validate binary search trees and find their kth smallest element? Previously explored query.
- Q4: How do I merge intervals and schedule overlapping meetings? Previously explored query.
- Q5: How should I debug and test a backtracking solution with duplicate values? Previously explored query.
- Q6: How can a monotonic stack find the next warmer day? Proxy IDs: `monotonic-stacks`, `stacks-and-parsing`.
- Q7: How do I find the largest k values using a heap? Proxy IDs: `heaps-and-top-k`, `sorting-and-custom-ordering`.
- Q8: How can union find detect redundant edges in an undirected graph? Proxy IDs: `union-find`, `graph-representation-and-dfs`.
- Q9: How do I reverse a linked list without losing nodes? Proxy IDs: `linked-lists`.
- Q10: How does a trie help find dictionary words on a board? Proxy IDs: `tries-and-prefix-search`, `backtracking`, `grid-search-and-flood-fill`.
- Q11: How do I binary search for the minimum feasible shipping capacity? Proxy IDs: `binary-search`, `complexity-and-constraints`.

### Measured five-page group identities

- `query0_primary`: `topological-sort`, `bit-manipulation`, `dijkstra-and-shortest-paths`, `sliding-window`, `grid-search-and-flood-fill`.
- `query2_primary`: `breadth-first-search`, `graph-representation-and-dfs`, `hash-maps-and-frequency-counting`, `heaps-and-top-k`, `grid-search-and-flood-fill`.
- `query0_recovery`: `intervals-and-sweep-lines`, `string-and-grid-dp`, `sorting-and-custom-ordering`, `problem-solving-workflow`, `dynamic-programming-fundamentals`.

### Hardware histogram appendix

Bit position zero is the first listed page in the corresponding group. These are decoded production-selector counts, before validity filtering. Each column sums to 256.

| Bitstring | Q0 primary | Q2 primary | Q0 recovery |
| --- | ---: | ---: | ---: |
| `00000` | 12 | 17 | 15 |
| `00001` | 7 | 12 | 3 |
| `00010` | 2 | 10 | 4 |
| `00011` | 2 | 4 | 3 |
| `00100` | 5 | 14 | 6 |
| `00101` | 3 | 8 | 7 |
| `00110` | 3 | 4 | 9 |
| `00111` | 6 | 8 | 13 |
| `01000` | 18 | 7 | 5 |
| `01001` | 3 | 4 | 8 |
| `01010` | 10 | 5 | 8 |
| `01011` | 6 | 7 | 9 |
| `01100` | 9 | 10 | 10 |
| `01101` | 14 | 6 | 4 |
| `01110` | 6 | 13 | 7 |
| `01111` | 7 | 5 | 16 |
| `10000` | 9 | 3 | 3 |
| `10001` | 4 | 4 | 4 |
| `10010` | 4 | 7 | 11 |
| `10011` | 7 | 5 | 13 |
| `10100` | 4 | 11 | 11 |
| `10101` | 5 | 5 | 8 |
| `10110` | 6 | 13 | 11 |
| `10111` | 8 | 15 | 8 |
| `11000` | 14 | 1 | 6 |
| `11001` | 13 | 9 | 8 |
| `11010` | 8 | 3 | 12 |
| `11011` | 8 | 9 | 17 |
| `11100` | 10 | 5 | 6 |
| `11101` | 15 | 9 | 5 |
| `11110` | 3 | 7 | 5 |
| `11111` | 25 | 16 | 1 |

### Fixed hardware circuit parameters

| Group | gamma | beta |
| --- | ---: | ---: |
| query0_primary | 0.3207498508671629 | -0.1658536407905253 |
| query2_primary | 0.3206666203063684 | -0.1652350807983665 |
| query0_recovery | 0.3370612638218759 | -0.08228135924911681 |

## Limits on conclusions

This is a small engineering and mechanism study: one corpus, twelve synthetic queries, one QPU, one layer, three hardware jobs, and no independent answer-quality judgments. The six new queries are a limited extension of prior work, not a fully independent benchmark. The recovery hardware group is conditioned on a classical primary set; it is not evidence about an entire hardware tournament's final eight pages. There is no end-to-end language-model answer evaluation, no global N=30 optimality proof, no repeated hardware reliability estimate, and no basis for a quantum-advantage claim. Recommendations are candidates for subsequent tests, not scientifically established universal defaults.
