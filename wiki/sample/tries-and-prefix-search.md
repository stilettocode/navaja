# Tries and Prefix-Based String Search

A trie represents strings as paths of characters from a root. Shared prefixes share nodes, making it useful for prefix lookup, dictionary matching, and searching many words against a common stream or board. Each node needs a way to distinguish a complete stored word from a prefix of a longer word.

## Insert and search

To insert a word, follow or create one child per character, then mark the terminal node. Exact lookup follows the same path and requires the terminal marker at the end. Prefix lookup only requires the path to exist.

If `app` and `apple` are stored, the node after `app` is both terminal and the parent of a longer continuation. Forgetting this distinction can make a prefix look like a complete dictionary word or lose shorter words when longer ones are added.

For a word of length L, insertion and lookup take O(L) child accesses under ordinary dictionary assumptions. Storage is proportional to the total number of distinct prefix nodes, bounded by the total input character count. An array of children can be fast for a fixed small alphabet but wastes memory when the alphabet is sparse or large.

## Combine a trie with backtracking

In a board-word search, follow board neighbors and trie edges together. If the current prefix has no trie continuation, prune immediately rather than continuing a path that cannot form any target word. Mark board cells as used for the current path and restore them when backtracking.

The trie reduces wasted prefix exploration but does not remove the exponential worst-case nature of board path search. A cell generally cannot be reused within one word unless the problem explicitly permits it. Finding one word must not prevent finding another sharing its prefix.

## Deduplication and deletion

Store a full word or identifier at terminal nodes to avoid repeatedly building strings during search. Clearing a terminal marker after reporting a word can suppress duplicate output when each word is needed once, but this mutates the dictionary state. Do not do so when repeated occurrences must be counted.

Test a word that is another word's prefix, repeated insertions, an absent continuation, and the empty string if allowed. Deleting a word should clear its terminal marker while preserving nodes needed by other words. Trie correctness depends on separating shared structural prefixes from the independent membership of each complete word.
