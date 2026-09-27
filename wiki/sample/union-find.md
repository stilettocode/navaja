# Union-Find for Dynamic Connectivity

Union-find, also called disjoint-set union, maintains a partition of elements into connected groups. It supports finding an element's representative and merging two groups. Use it when connections are added over time and queries ask whether two items belong to the same component.

## Representatives and merging

Initialize each element as its own parent. `find(x)` follows parent links to a representative. To connect x and y, find both representatives and attach one root to the other if they differ. Attaching an arbitrary non-root node is not a correct replacement for merging roots.

Track component sizes or ranks to attach the smaller tree under the larger one. Path compression makes visited nodes point closer to or directly at the representative during `find`. Together, these techniques give nearly constant amortized operation cost, conventionally expressed using the inverse Ackermann function.

## Recognize useful applications

To count connected components, start with V components and decrement the count only when a union joins two previously separate groups. An edge within an existing component does not reduce the count. To detect a redundant edge in an undirected graph, check whether its endpoints already share a representative before joining them.

For merging accounts, model shared email addresses as connections. After all unions, group addresses by representative and construct the required output. The data structure discovers groups, but sorting names or addresses for the final answer has its own cost.

Kruskal's minimum-spanning-tree algorithm sorts edges by weight and uses union-find to accept edges that connect different components. The sorting step usually dominates the runtime. The representative value itself has no semantic meaning unless the implementation deliberately maintains extra metadata.

## Limits and careful implementation

Ordinary union-find supports merging, not arbitrary deletion or splitting. If a problem removes edges, consider reversing an offline sequence or using a more specialized method. It also does not directly answer directed reachability or strongly connected components.

Test repeated edges, self-loops, isolated vertices, and unions performed in a long chain. Update size information only at roots and only after a successful merge. If keys are strings, map them to indices or use dictionaries consistently.

State the invariant as a partition: two elements have the same representative exactly when the processed connections put them in the same component. This distinguishes connectivity from path reconstruction; union-find can answer whether a connection exists without storing the actual route.
