# Tournament Selection: Five Primary Pages Plus Three Recovery Pages

The tournament is a classical coordinator around an interchangeable group solver. Top-K, MMR, exhaustive subset search, exhaustive QUBO search, local QAOA, and IBM-backed QAOA all use the same grouping and survivor rules. Pages retain their original identities throughout; the coordinator never treats a winning group as one synthetic page.

## Exact interpretation of the rules

For a full five-page group, ask the solver for exactly three pages. Randomly choose one of its two rejects with equal probability. Four pages advance and one enters the primary discard pool. The solver bitstring contains three ones; the advancement bitstring contains four. Calling a solver choice "best" means best according to that solver: only exhaustive group solvers guarantee the group optimum.

Shuffle the remaining pages at the beginning of each round. Consume full groups of five and carry a smaller tail unchanged. A bye does not execute a circuit and is printed explicitly. This keeps ordinary solver calls at five candidates and guarantees progress whenever the active pool exceeds five.

The primary tournament stops at five. All pages it fully eliminated, each appearing once, become the recovery pool. A random survivor has not been fully eliminated and therefore does not enter the discard pool unless it loses in a later round.

Recovery uses the same reductions until at most five remain. For a final group of four or five, the solver chooses two and a random reject supplies the third. If the recovery pool already has three pages, it needs no calls. Five primary winners and three recovery winners are disjoint, producing exactly eight final selections. Recovery's fully discarded pages remain recorded but are not recycled into further tournaments.

At least eight distinct candidates are required. The tournament uses exact page counts and does not support a token budget. The underlying single-problem selectors and CLI commands remain available separately.

## Example with thirty candidates

```text
Primary:  30 -> 24 -> 20 -> 16 -> 13 -> 11 -> 9 -> 8 -> 7 -> 6 -> 5
Recovery: 25 -> 20 -> 16 -> 13 -> 11 ->  9 -> 8 -> 7 -> 6 -> 5 -> 3
Final:    five primary + three recovery = eight distinct pages
```

The primary stage makes 25 solver calls. Recovery makes 21, including its final two-plus-one selection. Total: 46 calls per algorithm, with at most five decision qubits per QAOA circuit. At 128 shots, that requests 5,888 final sampling shots across the groups. Runtime may entail additional provider overhead; this count is not an estimate of billing or wall-clock duration.

## Why shuffle instead of grouping by topic?

The first implementation uses seeded random shuffling. Grouping solely by descending relevance could force excellent pages to eliminate each other early. Topic grouping could eliminate useful alternatives within one topic or impose unintended per-topic quotas. Random grouping avoids those fixed boundaries, but adds variance and grants byes to some pages. It is an experimental baseline, not a proven best grouping method.

The grouping generator and random-survivor generator use separate streams derived from the seed. All compared algorithms start with the same pool and first partition. Their later page memberships differ because their earlier decisions differ. Reproducibility does not mean later subproblems are identical, nor does it make hardware measurements deterministic.

## Recovery should complement primary winners

The original objective rewards relevance and subtracts pairwise redundancy. Let P be the fixed primary set and R a candidate recovery set. The final score can be written as:

```text
score(P union R) = score(P)
                  + sum over r in R [relevance(r) - sum over p in P similarity(r,p)]
                  - redundancy among pairs in R
```

Accordingly, recovery subproblems subtract similarity to all five primary pages from each candidate's relevance. Similarities within each recovery group are preserved. This is an exact conditional rewriting of the objective for the symmetric similarity matrix built by retrieval; the tournament's grouping and stochastic survival remain heuristic. Cross-group relationships are considered only when surviving pages eventually meet.

The final union is scored once against the original problem. Do not add group scores, compare primary and recovery scores directly, or label a tournament brute-force result as a global optimum. The random survivor is allowed to hurt the score, and neither MMR nor QAOA guarantees the optimum even within a group.

## Records and hardware behavior

The terminal lists titles and filenames beside local bit positions. JSONL run-start records define the global candidate order. Group records retain local and global mappings, solver choices, random survivors, byes, discards, timing, and available solver metadata. Result records identify the two winner sets and remaining discards. Records are appended and flushed after each completed group. A failure leaves the completed prefix available for inspection, but the ledger is not an automatic resume mechanism.

IBM mode optimizes each group's circuit locally and obtains final samples using a lazy, authorized IBM device factory. The factory selects a backend once per run and enforces the exact planned call count. It requires an explicit `--confirm-submit` for the entire tournament. Use `make plan` or `--dry-run` for an offline preview; an over-budget plan is rejected before connecting. No remote calls are made in the ordinary classical comparison. QAOA rejects invalid-cardinality samples; if none are valid, the existing relevance fallback is labeled in the console and metadata without a hardware retry. A fallback choice should not be described as a successful hardware selection.

Tournament runs disable warm-start file reads and writes, avoiding dependence on earlier algorithms or sessions. Local sampling is seeded. IBM executions remain affected by sampling and hardware conditions. Group calls currently execute sequentially; provider batching and job resumption would be separate engineering work.

## Useful next experiments

- Compare several seeds on the same query, original candidate set, final count, and objective. Report score distributions and runtimes rather than one favorable run.
- Compare final tournament scores with direct whole-pool Top-K and MMR selecting eight. This isolates whether the tournament helps the task rather than merely showing agreement between group solvers.
- On a sufficiently small candidate pool, compute a direct eight-page brute-force optimum. Exhaustive five-page solves do not establish global optimality.
- Try topic-balanced or similarity-aware partitions as explicitly labeled alternatives to random grouping. Evaluate before selecting a default.
- Inspect retrieval relevance manually. The current hashed word-count embeddings are a deterministic teaching baseline; shared vocabulary and guide-writing style may dominate semantic usefulness.
- Track the frequency of QAOA classical fallback and the contribution of random survivors. A final score alone cannot explain where the selected pages came from.

These experiments can evaluate quality and engineering tradeoffs. They do not by themselves demonstrate quantum advantage.
