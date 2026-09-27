# Graph Representation, DFS, and Components

A graph models objects and relationships. Before choosing a traversal, identify whether edges are directed, weighted, duplicated, or allowed to connect a vertex to itself. Decide whether all vertices are explicitly listed; vertices with no edges still belong to the graph and may form their own components.

## Build the right representation

An adjacency list stores neighbors for each vertex and usually uses O(V + E) space. An undirected edge must be added in both directions. An adjacency matrix uses O(V squared) space but supports direct edge lookup and may be appropriate for dense or small graphs.

For grids, neighbors can often be generated from coordinates instead of constructing adjacency lists. For word transformations or state puzzles, define an implicit graph whose neighbors are produced on demand. The graph model matters even when no explicit graph object appears in the code.

## Explore a connected region

Depth-first search follows one branch before returning to alternatives. Mark vertices visited before exploring their neighbors so cycles do not cause repeated recursion. To count components in an undirected graph, start a new traversal from every still-unvisited vertex, including isolated vertices.

Across all these traversals, each vertex and adjacency entry is processed a bounded number of times, yielding O(V + E) time. Recursive DFS may exceed Python's recursion depth on a long chain, so an explicit stack is often safer for large inputs. Pushing only newly discovered vertices avoids unnecessary repeated work.

## Directed cycles need more state

A single visited set answers reachability but does not distinguish a completed vertex from one currently on the recursion path. Directed cycle detection can use three colors: unseen, active, and complete. An edge to an active vertex identifies a cycle. In an undirected simple graph, ignore the immediate parent edge when detecting a cycle; parallel edges need extra care.

## Validate the model

Test disconnected graphs, an isolated vertex, a self-loop when allowed, and a cycle. Clarify whether the answer concerns connected components, strongly connected components, or reachability from one source; these are different questions for directed graphs.

When using iterative DFS for finishing-order algorithms, store entry and exit stages explicitly. A basic stack traversal gives reachability, but its pop order is not automatically the same as recursive postorder. Match the stored state to the proof the algorithm requires.
