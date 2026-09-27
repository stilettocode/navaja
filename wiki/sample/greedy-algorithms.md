# Greedy Algorithms and Exchange Arguments

A greedy algorithm commits to a locally preferred choice without exploring all alternatives. It can be very efficient, but a plausible rule is not a proof. The key question is whether an optimal solution can always be transformed to include the greedy choice without becoming worse.

## Earliest finishing activities

To maximize the number of non-overlapping activities, sort by finishing time. Select the earliest-finishing available activity, then continue with activities compatible with it. Any optimal solution starts with some activity that finishes no earlier than the greedy choice. Replacing that first activity with the greedy one leaves at least as much room for the rest.

This exchange argument proves the first choice is safe; repeating it proves the full algorithm. Sorting costs O(n log n), followed by a linear scan. Define whether touching endpoints are compatible before writing the comparison.

## Track a sufficient frontier

For Jump Game reachability with nonnegative jump lengths, maintain the farthest reachable index. Process positions only while they are reachable and extend the frontier with each available jump. If the next index exceeds the frontier, no earlier reachable position can bridge the gap. This yields linear time and constant extra space.

The minimum-jump version requires a different invariant, often treating the current reachable range as one layer and extending the next layer's boundary. A reachability proof alone does not automatically justify a minimum-count implementation.

## Look for counterexamples

Choosing the largest coin first does not solve every coin system. With denominations 1, 3, and 4, making 6 greedily uses 4 + 1 + 1, while 3 + 3 uses fewer coins. Dynamic programming handles the general version because local choices can block better combinations.

Similarly, selecting the individually most valuable items can fail under a weight limit or a redundancy penalty. An exchange property, ordering structure, or other problem-specific reason is needed to justify irrevocable choices.

Test ties and adversarial examples where the locally attractive choice consumes a scarce resource. Compare the proposed rule against exhaustive search on tiny instances when developing an unfamiliar greedy method. State the maintained invariant and why the discarded alternatives cannot improve the answer. If that argument remains unclear, treat the method as a heuristic rather than claiming exactness.
