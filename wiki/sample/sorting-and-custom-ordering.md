# Sorting as an Algorithmic Transformation

Sorting can expose structure that is hidden in the original order. Once values are ordered, duplicates become adjacent, pair searches become directional, and interval relationships become easier to maintain. Before sorting, check whether the task depends on original positions or requires preserving the input.

## Choose a key that supports the proof

Sorting intervals by start time supports merging because no unseen interval begins earlier than the current one. Sorting activities by finish time supports a different greedy objective: maximizing how many non-overlapping activities can be selected. These keys are not interchangeable merely because both problems involve intervals.

For records with several fields, make tie-breaking explicit. A tuple key orders lexicographically. Some nesting problems sort the first coordinate ascending and the second descending so equal first coordinates cannot accidentally form a strictly increasing subsequence. The tie rule is part of correctness, not cosmetic formatting.

## Preserve the information the answer needs

If the output asks for original indices, sort pairs such as `(value, original_index)`. If input mutation is disallowed, use a sorted copy and count its space. In Python, `list.sort()` changes a list and returns `None`; `sorted()` produces a new list. Assigning the return value of `sort()` is a frequent implementation mistake.

Sorting is typically O(n log n) comparison work. A key function can hide additional cost, such as sorting each string to construct an anagram key. When values lie in a small bounded integer range, frequency counting or bucket methods can sometimes replace comparison sorting, but their memory depends on that range.

## Derive what sorting eliminates

For closest-pair values on a number line, a minimum-gap pair must be adjacent after sorting; any intervening value would create an equal or smaller gap. This argument reduces checking all pairs to checking neighbors. For duplicate detection, adjacency similarly removes the need for a membership structure, at the expense of sorting.

Test ties, already sorted data, reverse order, and records with equal primary keys. Avoid comparison functions that violate transitivity; the sorting algorithm assumes consistent ordering. Explain both the preprocessing cost and the scan afterward, and verify that rearranging the input has not changed the problem being solved.
