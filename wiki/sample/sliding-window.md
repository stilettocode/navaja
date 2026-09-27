# Sliding Windows for Contiguous Subarrays

A sliding window maintains information about a contiguous interval while its boundaries move forward. It is useful for longest or shortest substrings, fixed-length sums, and subarrays with bounded counts. A window works when changing a boundary has a predictable effect on validity or when the size is fixed.

## Fixed-size windows

For the maximum sum of k consecutive values, add each new value and remove the value that leaves the interval. Update the answer only after the window reaches size k. This uses O(n) time and constant auxiliary space for a running sum. Negative values are perfectly compatible with fixed-size windows; initialize the best value correctly rather than assuming zero is attainable.

## Variable-size windows

For the longest substring without repeated characters, keep character counts for the current interval. Add the new rightmost character, then move the left boundary until every count is at most one. Update the maximum length after restoring validity.

With `abba`, inserting the second `b` requires removing both the old `a` and old `b` before the window becomes valid. A single `if` removal is insufficient; use a loop. Each character enters and leaves once, so the total work is linear despite the nested loops.

For the shortest subarray with sum at least a positive target, a sum-based shrinking window works when values are nonnegative. Once the sum reaches the target, repeatedly shrink while recording valid lengths. With negative values, removing or adding an element no longer changes the sum predictably; a prefix-sum method or monotonic deque may be needed.

## Counting variants and pitfalls

Counting subarrays with exactly k distinct values can be expressed as the count with at most k minus the count with at most k minus one. This requires a correct at-most counting window and careful handling of k = 0. For each right endpoint, count all valid starting positions, not just the longest interval.

Always define whether the interval is closed or half-open. Keep counts synchronized with boundary changes, remove zero-count keys when using map size, and test repeated characters, all-invalid input, and an answer spanning the whole array. The validity invariant determines the order of updates.
