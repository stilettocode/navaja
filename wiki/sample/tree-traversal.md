# Binary Tree Traversal and Recursive Contracts

Tree traversal is a framework for visiting nodes in an order that makes the needed information available. Preorder handles a node before its children, inorder places it between the children, and postorder handles it after both children. Breadth-first traversal visits nodes by depth using a queue.

## Define what a recursive call returns

For maximum tree depth, let the function return the depth of the subtree rooted at its argument. An empty subtree returns zero; a nonempty subtree returns one plus the larger child depth. This contract makes both the base case and combination rule straightforward.

For checking whether a tree is height-balanced, returning a height or a failure sentinel avoids recomputing subtree heights at every node. Each node combines already-computed child information once, giving O(n) time. Repeatedly calling a separate height function can become quadratic on a chain.

## Global answers versus return values

The maximum path sum illustrates two different quantities. A call may return the best downward path that can be extended by its parent, while a global answer considers a path passing through the current node and both children. Returning the two-branch path upward would create an invalid forked path.

Write down both meanings before implementing. Initialize answers so all-negative trees are handled correctly. Similarly, a subtree's diameter candidate can combine left and right depths even though the parent only needs one depth value.

## Iterative alternatives and complexity

Depth-first traversal uses O(h) stack space for tree height h, which becomes O(n) on an unbalanced tree. An iterative stack avoids language recursion-depth limits but does not eliminate the need to store pending work. Postorder can use `(node, visited)` entries or explicit frames to distinguish entering from finishing a node.

Level-order traversal uses a queue and may hold an entire wide level. Record the level's initial queue length if grouping results by depth. Do not use a list's front deletion repeatedly for a large queue.

Test an empty root, a single node, a long chain, and a tree with only one child at several levels. State whether height counts nodes or edges, and whether a path may be empty. Many tree bugs come from combining correct child results under an inconsistent definition.
