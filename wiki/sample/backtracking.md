# Backtracking, Search Trees, and Pruning

Backtracking explores choices incrementally, abandoning a partial construction when it cannot lead to a valid answer. It is useful for permutations, combinations, board placements, partitions, and constraint puzzles. The key design questions are what a partial state means, which choices remain, and how changes are undone.

## Choose, explore, undo

For permutations, maintain a path and a record of used positions. Choose an unused position, append its value, recurse, then remove the value and mark that position unused again. When the path reaches the input length, append a copy to the results. Appending the path object itself makes later mutations corrupt earlier answers.

For combinations, pass a starting index so choices only move forward. This avoids generating different orders of the same combination. For subsets, each element can be included or excluded, producing 2 to the n possible subsets. The output-copying cost is part of the runtime, not an implementation detail to omit.

## Prune only with a valid argument

If the task chooses k elements and too few positions remain to fill the path, stop that branch. In a positive-number combination-sum problem, a candidate larger than the remaining target can prune later sorted candidates too. That argument fails if negative values are permitted because later choices could reduce the sum.

For duplicate inputs, sorting and skipping equal choices at the same recursion depth avoids duplicate outputs. This is different from banning equal values everywhere: a valid answer may use two distinct positions containing the same value. Define whether identity is by position or value.

## Separate validity from completion

A partial board may satisfy every current constraint without being complete. Conversely, reaching a target length does not guarantee validity unless invalid states were pruned earlier. Keep the completion condition and constraint checks explicit.

Search time is often exponential or factorial, so use constraints to assess feasibility. Memoization can help when many paths reach equivalent future states, but listing all distinct outputs still requires producing them. A global visited set can be incorrect when different prefixes must generate different answers.

Test no-solution inputs, repeated values, empty choices, and solutions that require undoing several levels. After each recursive return, verify that the state is exactly what it was before the choice. This restoration invariant is the foundation of reliable backtracking.
