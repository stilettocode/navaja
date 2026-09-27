# Complexity Analysis and Reading Constraints

Constraints help choose which algorithms are plausible. An array of a few dozen items may permit subset search; an array of hundreds of thousands usually requires a near-linear or logarithmic-per-item method. These are clues rather than universal timing rules: language overhead, constant factors, memory, and the judge's limits still matter.

## Count the work that actually happens

Two nested loops are not automatically quadratic. If a left pointer only moves forward while a right pointer also moves forward, the total pointer movement can be linear. Conversely, a loop that slices an increasingly long list may do quadratic copying even though there is only one visible loop.

For a recurrence such as merge sort, each recursion level processes all n elements and there are logarithmically many levels, giving O(n log n) time. For backtracking, count branching choices and depth, then include the cost of copying each output. Producing all subsets already requires exponential output in the worst case.

## Distinguish different kinds of bounds

Hash-table lookup is expected constant time under ordinary assumptions, not an unconditional worst-case guarantee. A monotonic stack offers amortized linear time because each item is pushed and popped at most once. A recursive tree traversal takes O(n) time but may use O(n) stack space on a chain, even if balanced trees use logarithmic depth.

Separate auxiliary memory from returned output. A two-pointer algorithm may use constant extra storage while returning a large collection. A supposedly in-place algorithm that creates `nums[:]` uses an additional linear-size copy. Python integers also grow with their magnitude, so very large arithmetic is not literally fixed-cost.

## Use constraints to reject a plan early

For n = 100,000, checking all pairs creates about five billion comparisons. Sorting once is a much more promising starting point when order can be changed. For a capacity-based dynamic program, inspect the numeric capacity as well as the number of items: O(nW) is pseudo-polynomial and may be enormous when W is large.

Before coding, state the input parameters explicitly. Graph complexity uses both vertices V and edges E; matrix complexity uses rows and columns. After coding, inspect library operations and temporary allocations. A correct asymptotic argument should describe the implemented program, not only the high-level idea.
