# Knapsack, Subset Sum, and Update Direction

Knapsack-style dynamic programming chooses items under a capacity or target-sum constraint. The state often records what can be achieved using a prefix of items and a current capacity. Determine whether each item may be used once, a bounded number of times, or indefinitely before deriving transitions.

## Zero-one subset sum

Let `reachable[s]` mean that some subset of processed items sums to s. Initialize only sum zero as reachable. For each positive item value v, update sums from the target downward, setting `reachable[s]` when `reachable[s - v]` was already true.

The descending order prevents using the same item repeatedly during one iteration. For a single item of value 3 and target 6, an ascending update would first mark 3 and then incorrectly use that new state to mark 6. This is the central distinction between zero-one and unbounded use.

For value-maximizing knapsack, replace booleans with the best attainable value at each capacity. Decide whether a state means exact capacity or at most that capacity. Unreachable exact states need an appropriate sentinel rather than zero, which may incorrectly imply feasibility.

## Unbounded choices and counting

When coins can be reused indefinitely, ascending amount updates allow the current coin to contribute multiple times. Counting combinations typically loops over coin types outside amounts; counting ordered sequences often loops over amounts outside coin types. These count different objects, so loop order is part of the problem definition.

For minimum coin count, initialize amount zero to zero and others to infinity, then minimize over valid transitions. If an amount remains unreachable, convert the sentinel to the required output. Duplicate denominations may overcount combinations unless handled consistently.

## Constraints and edge cases

An O(nW) table is pseudo-polynomial because W is a numeric value, not its encoded length. Large capacities may require alternative approaches, such as meet-in-the-middle for a small number of items. Negative item values also invalidate the usual bounded nonnegative-sum indexing scheme.

Test target zero, no usable item, one item that must not be reused, and multiple ways to reach the same amount. Explain which iteration's states each update reads. Correct capacity bounds and update direction are more important than memorizing a particular nested-loop template.
