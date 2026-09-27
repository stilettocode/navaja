# Binary Search and Boundary Invariants

Binary search locates a boundary in an ordered search space. It applies to sorted arrays and to any predicate that is false before a boundary and true afterward. The main challenge is defining the boundary and preserving the interval invariant, rather than computing the midpoint.

## A half-open lower-bound template

To find the first index whose value is at least target, initialize `left = 0` and `right = len(nums)`. While left is less than right, choose the midpoint. If its value is below target, set left to midpoint + 1; otherwise set right to midpoint. At termination, left is the insertion position and may equal the array length.

The invariant is that every position before left is too small and every position at or after right is large enough. Each update excludes the midpoint from the unresolved region or makes it the upper boundary, ensuring progress. For `[1, 3, 3, 7]` and target 3, the result is index 1, not an arbitrary matching occurrence.

Finding the first value strictly greater than target changes the comparison. Together, lower and upper bounds give the count of repeated target values. An exact search must check that the returned position is in bounds and actually equals the target.

## Search the answer space

For minimum shipping capacity within a given number of days, a candidate capacity is either feasible or infeasible. Larger capacities preserve feasibility, so search for the first feasible capacity. Start with bounds justified by the problem: at least the largest package and at most the total weight. A linear feasibility check makes total time O(n log R), where R is the capacity range.

Do not assume monotonicity merely because answers are numeric. Explain why changing the candidate in one direction cannot reverse feasibility. Floating-point searches need a precision or iteration stopping rule instead of integer endpoint updates.

Test empty arrays when allowed, one element, targets outside the data range, all-equal values, and a boundary at either endpoint. Mixing closed-interval updates with a half-open loop is a common source of nontermination and missed values. Pick one invariant and derive every update from it.
