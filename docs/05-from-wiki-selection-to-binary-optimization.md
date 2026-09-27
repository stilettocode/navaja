# From Wiki Selection to Binary Optimization

Think of each candidate page as a Boolean feature flag:

```text
breadth-first-search.md          -> x0
dijkstra-and-shortest-paths.md   -> x1
testing-and-debugging.md         -> x2
```

A bitstring such as `101` means include breadth-first search and testing, but omit Dijkstra. The ordinary Python objective sums the relevance of selected pages and subtracts similarity for each selected pair.

For exactly three pages from five candidates, only bitstrings with three `1` values are valid. Brute force checks those combinations and acts as our debugging oracle. The QUBO layer changes representation, not the underlying research question.
