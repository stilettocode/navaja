# Two Pointers on Arrays and Strings

Two pointers reduce a search space by moving through an ordered structure without restarting scans. Common forms include pointers approaching from opposite ends, a read pointer with a write pointer, and merging two sorted sequences. The crucial requirement is a reason each movement safely discards possibilities.

## Opposite ends of a sorted array

To find a target pair in a sorted array, begin at the first and last values. If their sum is too small, advance the left pointer. Every pair using that left value and a smaller right value would also be too small. If the sum is too large, decrease the right pointer for the symmetric reason.

For `[1, 2, 4, 7]` and target 6, the sum 8 moves the right pointer left; the sum 5 moves the left pointer right; then 2 + 4 succeeds. Each pointer moves at most n times, giving O(n) time after sorting. Sorting adds O(n log n) and may destroy original index information unless indices are retained.

## Read and write positions

Removing duplicates from a sorted array uses a read pointer to inspect every value and a write pointer to mark the next output position. Maintain the invariant that the prefix before the write pointer is already the correct compacted answer. This supports in-place transformations without repeated deletions that shift the array.

For palindrome checking, move inward while comparing matching characters. If punctuation or case should be ignored, normalize comparisons consistently and guard both pointers while skipping characters. An empty normalized string is usually a palindrome, but follow the problem's contract.

## Recognize when the argument fails

An unsorted pair-sum array does not support the same directional rule; use a hash map or sort first. Problems asking for all unique pairs need deliberate duplicate skipping. Three Sum combines sorting with an outer fixed index and a two-pointer inner search, yielding O(n squared) time.

Test equal values, crossed pointers, two-element inputs, and cases with no answer. Write down whether pointer equality is a valid state. Finally, explain the eliminated region of the search space; "move the pointer because the sum is small" is incomplete without the ordering argument that makes it safe.
