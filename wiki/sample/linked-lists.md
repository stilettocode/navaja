# Linked Lists and Pointer Rewiring

Linked-list problems are about preserving reachability while changing connections. Nodes are distinct objects even when their values are equal. Unlike arrays, a list does not provide constant-time access to an arbitrary index, but it can change a known connection without shifting later elements.

## Reverse a singly linked list

Maintain `previous` and `current`. Before changing `current.next`, save the original next node. Point `current.next` to previous, move previous to current, and move current to the saved node. At termination, previous is the new head.

The invariant is that previous heads the reversed processed prefix and current heads the untouched suffix. Saving the next pointer first is essential; otherwise the remaining suffix may become unreachable. The algorithm takes O(n) time and O(1) extra space. A recursive reversal also works but uses O(n) call-stack space.

## Dummy heads simplify boundaries

A dummy node before the real head makes insertion, deletion, and merging more uniform. Removing the original first node becomes the same operation as removing an interior node. Return `dummy.next`, not the dummy itself. For merging two sorted lists, a tail pointer tracks where to attach the next chosen node.

If node reuse is allowed, merging can rewire existing nodes. If the inputs must remain unchanged, create copies and include their allocation cost. Read the problem's mutation contract before choosing either approach.

## Fast and slow pointers

Moving one pointer one step and another two steps finds a midpoint or detects a cycle. Always check that the fast pointer and its next node exist before taking two steps. In cycle detection, compare node identity, not equal values. After a meeting inside a cycle, moving one pointer from the head and one from the meeting point at equal speed locates the cycle entry.

For removing the nth node from the end, a fixed gap between two pointers allows one pass. A dummy head handles removal of the first node, and the gap must be derived carefully from where each pointer starts.

Test an empty list when allowed, a single node, two nodes, duplicate values, and changes at the head or tail. Draw arrows for a tiny example before coding. Pointer assignments should preserve an explicit partition between completed work and the remaining reachable structure.
