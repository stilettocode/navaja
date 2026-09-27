# Monotonic Stacks and Next-Greater Elements

A monotonic stack keeps unresolved elements in increasing or decreasing order. It is useful when each position needs the next greater value, next smaller value, or the boundary over which it remains an extremum. Unlike an ordinary stack problem, the ordering of values determines when entries can be resolved permanently.

## Resolve earlier positions with the current value

For Daily Temperatures, store indices whose warmer day has not yet appeared. Their temperatures remain nonincreasing from bottom to top. When a new temperature is warmer than the top entry, pop that index and record the distance to the current day. Continue until the invariant is restored, then push the current index.

For temperatures `[70, 72, 71, 75]`, day 1 resolves day 0; day 3 resolves both days 2 and 1. Positions still on the stack at the end have no warmer future day. Store indices rather than only values because the answer requires distances and duplicate temperatures must remain distinguishable.

Every index is pushed once and popped at most once. The total time is O(n), even though popping occurs inside a loop. Worst-case auxiliary space is O(n), such as a decreasing sequence that never resolves until the end.

## Equal values change the invariant

Use a strict comparison when the problem asks for strictly greater values. If equal values count, change the comparison deliberately. Histogram and subarray-contribution problems often require asymmetric tie-breaking so equal minima are not counted twice or omitted.

For Largest Rectangle in Histogram, a shorter bar ends the possible rightward span of taller bars. When a bar is popped, the new stack top identifies its left boundary. A final sentinel-height step can resolve remaining bars, but its handling must not create invalid array accesses.

## Recognize the pattern carefully

A monotonic stack is appropriate when a newly encountered value can permanently settle older questions. A sliding-window maximum instead needs expiration from the opposite end and normally uses a monotonic deque. Binary search over stack values may solve other tasks, but is unnecessary for the basic next-greater scan.

Test all-equal values, strictly increasing and decreasing arrays, and a single element. Explain why a popped element never needs to return. That permanence argument is both the correctness proof and the reason the total work stays linear.
