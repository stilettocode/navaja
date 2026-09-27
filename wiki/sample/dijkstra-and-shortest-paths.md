# Dijkstra and Weighted Shortest Paths

Dijkstra's algorithm finds shortest paths from a source when all edge weights are nonnegative. It repeatedly expands the currently smallest tentative distance using a priority queue. Ordinary breadth-first search is simpler when all edges have equal cost, but does not handle arbitrary weighted distances correctly.

## Relax edges from the best frontier

Initialize the source distance to zero and every other distance to infinity. Push `(0, source)` into a min-heap. Pop a distance and vertex; if that distance no longer matches the recorded best value, skip the stale entry. Otherwise, try each outgoing edge and update a neighbor whenever the new route is strictly shorter.

For edges A to B costing 5, A to C costing 1, and C to B costing 1, B first receives tentative distance 5 and later improves to 2. The heap may contain both entries. Skipping the old entry avoids reprocessing an obsolete route without requiring an in-place heap priority update.

## Why nonnegative weights matter

When the smallest valid tentative distance is removed, no later route through an unsettled vertex can improve it: reaching that vertex is already at least as expensive, and further edges cannot decrease the cost. A negative edge breaks this argument. Use an appropriate alternative, such as Bellman-Ford, when negative weights are allowed and its cost fits the constraints.

For a simple graph with a binary heap, the familiar bound is O((V + E) log V). A lazy heap can store O(E) entries; for graphs allowing arbitrarily many parallel edges, describe the heap-size dependence explicitly. Adjacency storage also uses O(V + E) space.

## Model the complete state

If using a discount coupon changes future costs, a state might be `(vertex, coupon_used)`. Distances must distinguish these states. Keeping only one distance per vertex can discard a slightly longer arrival that preserves a valuable resource.

Record parents when a shortest route itself is required. Early exit is valid when the destination is popped with its current best distance, not when it is first inserted. Test unreachable vertices, zero-weight edges, multiple competing routes, and duplicate heap entries. Always verify the weight assumptions before selecting the algorithm.
