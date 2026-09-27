# Binary Search Trees and Ordered Queries

A binary search tree places smaller keys on one side and larger keys on the other according to a chosen duplicate policy. This ordering enables search, range queries, predecessor and successor queries, and sorted traversal. The height determines performance: an ordinary unbalanced tree can degrade into a chain.

## Validate inherited bounds

Checking that each node is larger than its left child and smaller than its right child is not enough. Every node must satisfy bounds inherited from all ancestors. In a strict BST, recurse left with the current value as the upper bound and recurse right with it as the lower bound.

For example, a value 12 inside the left subtree of root 10 violates the root's constraint even if its immediate parent comparison looks valid. Open lower and upper bounds capture the full requirement. Decide how duplicates are handled rather than silently accepting equality.

## Inorder traversal exposes sorted order

An inorder traversal visits strict BST keys in increasing order. This supports finding the kth smallest value by counting visits and stopping at k. An explicit stack performs this lazily without constructing the entire sorted list. Worst-case time is O(h + k) for the prefix traversal, with O(h) auxiliary space.

If many rank queries are required and the tree can be maintained with subtree sizes, order-statistic traversal can skip entire subtrees. Updating those sizes correctly becomes part of insertion and deletion. A one-off interview solution usually does not need that additional machinery.

## Exploit order without overclaiming balance

To find a lowest common ancestor when both nodes are guaranteed present, move left if both keys are smaller and right if both are larger. Otherwise the current node is the split point. This uses O(h) time, not automatically O(log n).

Range-sum queries can prune a left subtree when all its values are too small or a right subtree when all are too large. Validation itself still needs to inspect every node. Deletion with two children commonly substitutes an inorder successor and then removes that successor from its original location.

Test ancestor-bound violations, duplicate keys, extreme values, missing query keys if allowed, and a completely skewed tree. Distinguish node identity from value equality when the task refers to particular nodes. Always attach logarithmic complexity claims to a balancing assumption.
