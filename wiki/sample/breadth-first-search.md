# Breadth-First Search and Unweighted Shortest Paths

Breadth-first search explores a graph in nondecreasing distance from its starting vertices when every edge has equal cost. It is the natural choice for minimum numbers of moves, shortest paths in unweighted graphs, and level-by-level expansion. Depth-first search does not generally provide this shortest-path guarantee.

## Discover each state once

Initialize a queue with the start and record distance zero. When removing a vertex, inspect each neighbor. If a neighbor has not been discovered, assign its distance as the current distance plus one, record its parent if needed, and enqueue it immediately.

Marking at enqueue time ensures a vertex enters the queue once. The first discovery is shortest because every shorter-distance frontier has already been processed. An adjacency-list traversal takes O(V + E) time and O(V) additional storage for the queue, distances, and optional parents.

## Multiple sources and path reconstruction

For distance to the nearest source, enqueue every source initially at distance zero. This handles problems such as distance to the nearest zero cell or simultaneous spreading. Running a separate BFS from every source repeats substantial work and is usually unnecessary.

To reconstruct a path, follow parent links backward from the destination and reverse the result. If the destination was never discovered, report unreachable according to the problem contract. Count edges versus visited vertices carefully: a path containing three vertices normally uses two moves.

## The state may be larger than a location

If movement depends on keys collected, remaining obstacle removals, or another resource, visited state must include that information. Reaching the same cell with a different key set can enable different futures. Marking only the cell can incorrectly discard a useful path.

For edge weights restricted to zero and one, a deque-based 0-1 BFS can process zero-cost edges at the front and unit-cost edges at the back while relaxing distances. Arbitrary nonnegative weights require an algorithm such as Dijkstra rather than ordinary FIFO BFS.

Test a source that is already the destination, an unreachable target, multiple shortest paths, and a graph containing cycles. Explain what makes two states equivalent and why the queue order matches distance order. Those two decisions determine whether the shortest-path argument actually applies.
