# Two-Dimensional Dynamic Programming for Strings and Grids

Two-dimensional DP often appears when a state tracks progress through two sequences or two spatial coordinates. The two axes should have explicit meanings. For string problems, prefix lengths usually produce cleaner boundaries than raw character indices because an empty prefix becomes a valid table row or column.

## Longest common subsequence

Let `dp[i][j]` be the length of the longest common subsequence of the first i characters of one string and first j characters of another. If the final characters match, extend `dp[i - 1][j - 1]` by one. Otherwise, take the larger of dropping the final character from either prefix.

The first row and column are zero because an empty string has no nonempty common subsequence. A subsequence can skip characters; a substring must be contiguous and requires a different recurrence. For strings of lengths m and n, this table takes O(mn) time and O(mn) space before optimization.

## Edit distance and grid paths

Edit distance uses a similar state but considers insertion, deletion, and replacement costs. Initialize the empty-prefix row and column to their required edit counts. Matching characters incur no replacement cost. Write down which movement through the table corresponds to each operation to avoid swapping meanings accidentally.

For a grid with moves only right and down, a cell's path count can depend on its top and left neighbors. Blocked cells contribute zero. Whether a blocked starting cell has zero paths should be settled before initialization. If moves can form cycles, a simple row-by-row DP may no longer be valid.

## Space compression and reconstruction

When only the previous row and current row are needed, rolling arrays reduce space to O(n). A one-row implementation must preserve the old diagonal value before overwriting it. Update order determines whether a reference means the old row or the current row.

Recovering an actual subsequence or edit script usually needs additional decisions beyond the optimal value. Keep the full table or plan a separate reconstruction strategy. Do not promise the sequence when the implementation stores only its length.

Test empty strings, identical strings, no shared characters, a one-row grid, and blocked boundaries. Carefully distinguish prefix lengths from character positions: table position i commonly refers to character index i minus one.
