# Heaps, Priority Queues, and Top-K Selection

A heap efficiently exposes the smallest or largest current item without keeping every item fully sorted. Use it for repeated best-next choices, merging sorted streams, retaining a fixed number of candidates, and shortest-path frontiers. A heap is partially ordered: its root is special, but the entire underlying array is not sorted.

## Retain the k largest values

Maintain a min-heap of at most k values. Insert values until it is full. For each later value, replace the root only if the new value is larger. The root represents the weakest retained candidate, so discarding it preserves the k largest values seen so far.

This takes O(n log k) time and O(k) auxiliary space. For k close to n, sorting may be simpler. If the result must be returned in sorted order, include the cost of sorting the retained heap. A zero or invalid k requires an explicit policy before accessing the root.

## Merge sorted sources

To merge k sorted lists, put the first available element from each source into a min-heap. Pop the smallest, append it to the output, and insert the next item from the same source. The heap contains at most one frontier item per source. For N total values, the process takes O(N log k) time.

Store enough information to identify the source and position. In Python, tuples compare later fields when priorities tie. If those fields contain non-orderable objects, include a unique numeric tie-breaker before the object. This prevents equal priorities from causing comparison errors.

## Changing priorities

Python's common heap interface does not directly update an arbitrary entry's priority in place. A practical approach inserts a new entry and ignores stale entries when popped. Dijkstra's algorithm uses this pattern by comparing a popped distance with the current best distance.

Test duplicate priorities, empty sources, negative values, and a heap of size one. Avoid sorting the heap after every insertion; that defeats its purpose. Explain why the next globally useful item must appear among the heap's current candidates, and count both heap operations and any extra output work.

API reference: [Python heapq documentation](https://docs.python.org/3/library/heapq.html).
