# Queues and Monotonic Deques

A queue processes work in first-in, first-out order. It appears in breadth-first search, level-order traversal, and simulations where events must be handled in arrival order. A deque also supports insertion and removal at both ends, enabling sliding-window algorithms with an ordered set of candidates.

## Use an efficient queue

In Python, `collections.deque` supports adding on the right and removing on the left without shifting every remaining element. Repeatedly removing index zero from a list performs linear shifting and can turn an otherwise linear traversal into quadratic work. A list with a separate read index is another possible queue representation, though consumed references may remain stored.

For breadth-first traversal, enqueue an item when first discovering it and mark it visited at that time. Marking only when removing it can enqueue the same state repeatedly. If processing levels, capture the current queue length before processing that level; newly added nodes belong to the next level.

## Sliding-window maximum

Maintain a deque of indices whose values decrease from front to back. Before reading the answer for a window, remove front indices that have fallen outside it. When adding a new index, remove smaller or equal values from the back because the new value is at least as good and expires later.

For `[1, 3, 2, 5]` with window size 3, the first maximum is 3. Adding 5 removes weaker candidates from the back, and the next maximum becomes 5. The front always contains the maximum of the current window. Each index enters once and leaves at most once, giving O(n) time and O(k) space.

## Keep two removal rules separate

Front removal handles expiration by position; back removal handles domination by value. Confusing them can retain expired maxima or discard values that are still needed. Storing values alone makes expiration ambiguous when duplicates occur, so indices are usually clearer.

Test k = 1, k equal to the input length, duplicate maxima, and decreasing input. Reject or define invalid window sizes explicitly. For a general online priority problem, a heap may be more appropriate; the deque achieves linear time because both time order and value domination have special structure.

API reference: [Python deque documentation](https://docs.python.org/3/library/collections.html#collections.deque).
