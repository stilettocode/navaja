# Dynamic Programming: States and Recurrences

Dynamic programming reuses solutions to overlapping subproblems. Start by defining a state whose information completely determines the remaining problem. Then describe transitions, base cases, and evaluation order. A table without a precise meaning for each entry is difficult to reason about and easy to misuse.

## Derive a recurrence from choices

For House Robber, let `dp[i]` be the best value obtainable from the first i houses. The final decision either skips house i minus one, retaining `dp[i - 1]`, or takes it, adding its value to `dp[i - 2]`. Choose the better valid option.

This state summarizes the processed prefix sufficiently because only adjacency to the most recent house affects the next choice. Handle zero and one house explicitly, or use a consistent initialization that covers them. If negative values are allowed, clarify whether choosing no houses is permitted before selecting base values.

## Top-down and bottom-up

Top-down memoization expresses the recurrence as a function and caches results by state. It evaluates only reached states but consumes recursion stack space. Bottom-up tabulation processes states in dependency order and often avoids recursion limits. Both should implement the same mathematical recurrence.

Estimate time as the number of distinct states times the work per transition, then include any nonconstant operations. A cached function that slices a string on every call may have more work than the state count alone suggests. Memoization keys must include every variable that changes future choices.

## Optimize space after correctness

If each state depends only on the previous two values, keep a rolling pair instead of an entire table. Name the old and new values carefully so updates do not overwrite information still needed. Reconstructing the selected choices may require retaining parent decisions or recomputing information later.

Do not apply DP merely because a problem asks for a maximum. A greedy argument may avoid exploring multiple choices, while a graph search may better represent the state space. The important evidence for DP is reusable substructure under a complete state definition.

Test the base cases, a tie between choices, and a case where the locally largest value is not globally optimal. Explain why every optimal solution must arise from one of the recurrence's transitions and why each transition combines compatible subproblems.
