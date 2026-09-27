# Grid Search, Flood Fill, and Boundary Traversal

A grid is an implicit graph whose vertices are cells and whose edges represent allowed moves. Common tasks include counting islands, filling a region, finding a shortest path, and identifying cells connected to a boundary. Define whether neighbors are four-directional or eight-directional before writing traversal code.

## Flood fill a component

Starting from an eligible cell, use DFS or BFS to visit all connected eligible cells. Mark a cell when adding it to the worklist so multiple neighbors do not schedule it repeatedly. A scan over the entire grid can start a new fill whenever an unvisited land cell appears; the number of fills is the number of islands.

For an R by C grid, each cell and its constant number of neighbors are processed at most a bounded number of times, giving O(RC) time. The worklist or visited set can use O(RC) space. Modifying the grid can replace a separate visited structure only when input mutation is allowed.

## Work backward from the boundary

For surrounded regions, first mark cells connected to the outer boundary. Those cells cannot be captured. After the boundary flood fill, flip remaining eligible cells and restore temporary marks. This reverses the question from "is each region enclosed?" to "which cells can escape?"

For distance to the nearest source or spreading across a grid, use multi-source BFS. Put all initial sources into the queue before traversal. Simultaneous expansion produces minimum arrival times without repeatedly searching from individual cells.

## Implementation details that affect correctness

Check row and column bounds before indexing. In Python, negative indices access from the end, so accidentally reading row -1 does not necessarily raise an error. Keep coordinate ordering consistent, and avoid making a matrix with repeated references such as `[[0] * cols] * rows` when rows will be mutated.

If flood fill replaces one color with another, handle the case where the replacement equals the original color; otherwise marking may not distinguish visited cells. If a state includes resources or collected items, coordinates alone are not enough for visited tracking.

Test a one-cell grid, a single row, a single column, all water, all land, and diagonal-only contact. State whether rectangular input is guaranteed. Use an iterative traversal when a long winding region could exceed the language's recursive call limit.
