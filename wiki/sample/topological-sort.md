# Topological Sorting and Dependency Graphs

A topological ordering places every prerequisite before the item that depends on it. It exists exactly for directed acyclic graphs. Course scheduling, build dependencies, and ordering tasks often reduce to this model. Carefully decide edge direction: if A must happen before B, use an edge from A to B.

## Kahn's indegree algorithm

Compute each vertex's indegree, the number of incoming dependency edges. Add every zero-indegree vertex to a queue. Remove one, append it to the ordering, and decrement the indegree of each outgoing neighbor. A neighbor becomes available when its remaining indegree reaches zero.

The invariant is that queued vertices have no unmet prerequisites among unprocessed vertices. Each edge is removed conceptually once, so the algorithm takes O(V + E) time with adjacency lists. If fewer than V vertices are processed, the remaining graph contains a directed cycle and no complete ordering exists.

For prerequisites A before C and B before C, either A or B may appear first, but C must follow both. Multiple valid outputs are normal. If the problem requires the lexicographically smallest ordering, use a min-heap for currently available vertices and include its logarithmic overhead.

## DFS and dynamic programming alternatives

DFS can produce a topological order by reversing finishing order, provided active-path cycle detection is included. A visited set alone cannot reliably detect directed cycles. An iterative implementation needs explicit finishing events to reproduce postorder.

Once a DAG is ordered, process it to compute longest paths, counts of paths, or accumulated prerequisite values. The order guarantees each predecessor's result is ready. Unlike general graphs, longest paths in a DAG can be computed efficiently using this structure.

## Modeling and edge cases

Include vertices with no edges. If duplicate dependency pairs are possible, either deduplicate consistently or count and remove each duplicate consistently. Counting an edge twice but traversing it once can leave a vertex incorrectly blocked.

Test an empty dependency list, a self-dependency, a cycle inside one disconnected component, and several simultaneously available vertices. Distinguish returning any order from deciding only whether an order exists. Do not apply topological sorting to undirected graphs without first constructing a meaningful directed dependency model; direction is essential to the invariant.
