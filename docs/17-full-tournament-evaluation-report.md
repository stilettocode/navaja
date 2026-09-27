# Full tournament comparison

This follow-up compares final eight-page selections from 30 candidates. The local study uses the same twelve synthetic queries, with tournament seeds 7, 17, and 27. QAOA uses one layer, three local training iterations, 256 measurements per group, and no warm starts. Each group has an independent deterministic simulation sampling seed. Production defaults are unchanged.

## Local results

| Method | Mean objective | New-query label coverage | Median selection time |
| --- | ---: | ---: | ---: |
| topk | -17.505979 | 55.6% | 0.024 ms |
| mmr | -16.545523 | 47.2% | 0.196 ms |
| greedy_swaps | -15.793151 | 13.9% | 0.672 ms |
| exact_tournament | -16.033303 | 46.3% | 3.657 ms |
| qaoa_tournament | -16.039638 | 46.3% | 1112.259 ms |
| feasible_random_tournament | -16.033303 | 46.3% | 59.341 ms |

Direct baselines have twelve observations each; tournament methods have 36 runs nested within twelve queries. Coverage averages the six newer queries and their seeds. Timing excludes retrieval, imports, and result-file writes. QAOA timing includes local training and sampling. The feasible-random baseline samples 256 valid subsets per group and keeps the highest-scoring draw. Its implementation scores repeated draws, so its timing is not an optimized random-sampling speed claim.

The exact tournament and feasible-random tournament have the same final scores in these runs. Simulated QAOA has nearly the same average score and the same aggregate label coverage, with much longer selection time. The earlier objective/usefulness mismatch remains: greedy plus swaps scores best but recovers fewer labelled relevant pages.

## Matched hardware tournament

The hardware query was fixed before new outcomes: **How can a monotonic stack find the next warmer day?** It is the first newer query by position; the grouping/survivor seed is 7. Relevant proxy labels are `monotonic-stacks` and `stacks-and-parsing`. Hardware outcomes drive later groups and recovery conditioning; this is an adaptive full tournament, not a replay of classical winners.

Hardware status: **completed**. Completed groups: 46/46. Provider-reported QPU usage: **82 seconds**.

The separate budget permits 46 submissions with a six-QPU-second execution ceiling each (276 seconds maximum requested, or 282 including the previous pilot). A durable ledger prevents automatic resubmission; the run stops on any error. No sessions are used. [IBM documents the limit as QPU usage](https://quantum.cloud.ibm.com/docs/en/guides/max-execution-time).

| Method, same query and seed | Objective | Label coverage | Selection time |
| --- | ---: | ---: | ---: |
| topk | -17.258089 | 100.0% | 0.000022 s |
| mmr | -15.552699 | 50.0% | 0.000203 s |
| greedy_swaps | -15.140547 | 0.0% | 0.000724 s |
| exact_tournament | -15.354358 | 50.0% | 0.003704 s |
| qaoa_tournament | -15.380283 | 50.0% | 1.110018 s |
| feasible_random_tournament | -15.354358 | 50.0% | 0.059828 s |
| hardware_tournament | -15.354358 | 50.0% | 412.043484 s |

Across completed hardware groups: **3568/11776 valid shots (30.3%)**, **338/11776 optimum shots (2.9%)**, **46/46 group selections reached the exact local score**, and **0 fallbacks**.

These group statistics include different problems and exact-K targets; they are descriptive totals, not independent repeats of one circuit. Each saved group includes its numeric problem, trained angles, ideal distribution, raw counts, and exact local score.

IBM returned zero `quantum_seconds` for 5 completed jobs. The usage total preserves provider values; zero is not interpreted as physically free execution. The submission guard reserves six seconds for every attempted job regardless of reported usage.

Hardware minus exact-tournament objective: **+0.000000**. The final sets share **8/8 articles**. Hardware total elapsed time was **6.87 minutes**. Elapsed time includes local training, network/provider waits, and incremental ledger writes.

**Final hardware articles:**

- monotonic-stacks
- linked-lists
- complexity-and-constraints
- tree-traversal
- bit-manipulation
- intervals-and-sweep-lines
- prefix-sums-and-difference-arrays
- topological-sort

## Interpretation: what the experiment actually established

**The full hardware pipeline worked, but it delivered the same final selection as a much faster classical tournament. The strongest product-quality concern remains the scoring formula: improving its score did not reliably recover more relevant articles.** These are separate findings. Successful execution is an engineering achievement; useful article selection and a quantum advantage require additional evidence.

### What went well, and why it matters

The experiment extended the earlier three-group pilot to a complete, adaptive tournament. All 46 hardware calls completed, each selected a locally optimal combination from its measurements, and no classical fallback was needed. Hardware selections fed into later rounds and the recovery stage. This validates the integration across a complete run: local parameter training, remote measurement, decoding, elimination, and final eight-page selection all worked together.

The hardware and exact classical tournament selected the same eight articles and obtained the same final score. That is a useful correctness reference: on this query and seed, replacing the exact group solver with sampled hardware results did not degrade the final selection. It does not establish that the eight articles were globally optimal or maximally useful.

The local comparison also shows that the sampled approach often reproduces the exact tournament. Simulated QAOA matched both its final score and article set in **33 of 36 query/seed runs**. The feasible-random baseline matched the exact tournament's final score in **all 36 runs**. These are descriptive counts across twelve queries, not 36 independent user tasks.

The budget controls worked as intended. The run completed within the authorized allowance, recorded job IDs and measurements, and required no retries. Together with the offline regression checks, this gives a useful foundation for further experiments. Passing tests establishes implementation consistency, not scientific or user-facing superiority.

### Why 46 out of 46 local optima is weaker evidence than it sounds

Each hardware group contained only five decision variables. Forty-five groups selected three articles, and the last selected two; either way, there were only **ten valid combinations**. A classical solver can score all ten and guarantee the best local answer.

The hardware received 256 attempts per group and the surrounding classical code kept the highest-scoring valid result. This best-of-many selection makes success likely even when individual measurements are unimpressive:

| Measurement-level observation | Meaning |
| --- | --- |
| 30.3% of measurements were valid | About seven in ten measurements selected the wrong number of articles and were discarded. |
| 2.9% of all measurements were optimal | Most individual measurements did not solve the group optimally. |
| 9.47% of valid measurements were optimal | Among valid answers, the observed pooled optimum rate was close to the 10% expected from uniform valid sampling. |
| Every group's best result was optimal | Repeated sampling plus classical scoring recovered the optimum despite weak individual-shot performance. |

Every measured group had one unique optimum. Uniform random five-bit strings would hit that optimum with probability 1/32 per attempt. With 256 independent attempts, the chance of at least one hit is about **99.97% per group**; under this idealized random model, succeeding in all 46 groups has probability about **98.65%**. This is an analytical reference, not a measured hardware control or a statistical test of the observed counts.

The implication is that this task is too easy at the group level for “we found the optimum” to distinguish useful quantum optimization from repeated guessing. The near-random pooled conditional rate does not prove all circuits behave identically to random sampling, but it provides no evidence of a strong preference for the best valid answer. The earlier simulator training sweep likewise suggested that training mainly improved the required article count, rather than discrimination among valid combinations.

### The most important weakness: the score and usefulness disagree

The objective rewards relevance and penalizes overlap between selected articles. Across the six labelled queries, greedy plus swaps achieved the best average internal score but recovered only **13.9%** of the listed relevant labels. Top-K recovered **55.6%**, and the three tournament methods each averaged **46.3%** in this follow-up. Identical aggregate coverage does not mean their selections were identical on every run.

The hardware query makes the disagreement concrete. The question asks about a monotonic stack for finding the next warmer day. The hardware selection included `monotonic-stacks` but omitted the other labelled guide, `stacks-and-parsing`. Top-K included both. Greedy plus swaps included neither, although it scored best. Several other hardware-selected pages concern different algorithm topics; this illustrates the need to assess relevance directly, but the incomplete labels do not establish that every unlabelled page is useless.

One plausible explanation is that the redundancy penalty overwhelms relevance: eight selected articles contribute eight relevance terms but 28 pairwise overlap penalties. The term counts alone do not prove an imbalance because their magnitudes also matter. The existing hashed word representation may also measure relevance and overlap poorly. These are mechanisms to investigate, not causes isolated by this experiment.

**A better optimizer cannot repair an objective that rewards the wrong article mix.** It can become more effective at making selections that look good numerically while missing useful material. This is why the results do not justify replacing the selection policy with greedy plus swaps solely because it wins on internal score—or declaring Top-K universally best solely from six incomplete label sets.

### What the speed results imply

On the matched query, the exact classical tournament took about **3.7 milliseconds**, simulated QAOA took **1.11 seconds**, and the hardware tournament took **412 seconds**. These are the implemented selection paths, not complete application response times: retrieval and language-model answer generation were not evaluated.

Hardware elapsed time includes local training, network/provider waits, and ledger writes. The experiment did not isolate how much each component contributed, so the difference cannot all be attributed to quantum gate execution. Nevertheless, the measured hardware path is far too slow to compete with the classical path for this small, interactive selection task. Even the local simulator is substantially slower without improving average coverage.

The **82 provider-reported QPU seconds** answer a different question: how much usage IBM reported, rather than how long a user waited. Including the previous pilot gives 88 reported seconds. Five completed jobs reported zero; those values are preserved without interpreting them as free physical execution. Remaining allowance is not by itself a reason to spend it on more repetitions of an easy benchmark.

### What the tournament design contributes—and loses

Matching exact group decisions establishes performance relative to the tournament, not to the best eight-page subset of the full pool. Early elimination restricts later choices, and the random survivor can change which articles remain available. Locally optimal groups therefore need not combine into the best global set.

Greedy plus swaps obtained a higher average objective than the exact tournament while taking less time. This suggests that the tournament structure adds cost and can sacrifice objective quality at this scale. It does not establish that greedy plus swaps is globally optimal for 30 candidates. The earlier smaller-pool oracle experiment provides separate evidence of tournament losses, but this follow-up does not compute a global 30-page oracle or isolate individual tournament mechanisms.

The tournament remains useful as an educational demonstration of a hybrid workflow and as a way to fit small problems onto a device. The present evidence does not establish it as the best production selector.

### What remains uncertain

- **Generality:** hardware covered one query, one seed, one backend, and one run. Forty-six dependent group problems are not 46 independent full-tournament replications.
- **Answer quality:** no independent reviewer or downstream answer evaluation determined whether the selected context produced more accurate or useful answers.
- **Hardware effects:** matching final winners can hide distribution differences. There was no hardware uniform control, repeated calibration-period comparison, or fixed physical layout; calibration snapshots were not retained.
- **Algorithm comparisons:** only one shallow circuit configuration and training budget were used here. Hardware outperforming the simulator's final score on this one query does not establish beneficial noise or a hardware advantage; finite sampling can miss a group optimum and change later groups.
- **Scaling:** many small five-variable solves do not demonstrate performance on a larger, hard optimization problem. No asymptotic speedup or quantum advantage follows from this experiment.

### Implications and next steps

1. **Validate usefulness first.** Have reviewers blindly grade article relevance and complementary coverage on separate queries, and evaluate resulting answers. Tune relevance and overlap weights only on development examples, then evaluate on held-out examples.
2. **Keep simple classical methods as serious baselines.** Top-K, MMR, and greedy plus swaps expose different tradeoffs between coverage and score. Compare them using user-facing quality and latency before choosing a default.
3. **Require measurement-level evidence for QAOA improvements.** Track validity, optimum probability conditional on validity, quality at equal shot budgets, and training time. Compare against exact enumeration and uniform valid sampling; best-of-256 success alone is insufficient here.
4. **Investigate circuit and constraint changes locally.** Test ways to preserve the required article count and compile the cost circuit more efficiently. Establish improved conditional quality or resource use before spending QPU time on another full tournament.
5. **Use future hardware runs to answer a specific unresolved question.** Replicate across preselected queries or calibration periods, or test a locally justified circuit improvement with matched controls. Another successful run of the same easy groups would add reliability evidence, but little evidence of optimization advantage.

The project now has evidence that a complete quantum-backed tournament can execute successfully within a modest usage budget. Its practical value as an article selector remains unproven: classical methods are faster, the final hardware result matched an exact classical tournament, and the scoring model needs independent usefulness validation.

## Data and reproduction

- [Raw data](../experiments/results/full-tournament-evaluation/): `protocol.json`, `local.json`, `hardware.json`, and the matched local event logs. This directory is ignored by Git.
- [Experiment source](../experiments/full_tournament_evaluation.py).
- [Offline report builder](../experiments/build_full_tournament_report.py) and [interpretation source](../experiments/full_tournament_interpretation.md).
- [Portable results archive](../experiments/results/full-tournament-evaluation-data.zip), including CSV tables.

Rebuild this report without QPU use:

```powershell
.venv/Scripts/python.exe experiments/build_full_tournament_report.py
```

Offline regression suite: **105 tests passed** after adding budget and resubmission guards. The initial sandboxed test attempts hit Windows temporary-directory permissions; the unrestricted offline run passed.
