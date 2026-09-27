# Intervals, Merging, and Sweep Lines

Interval problems describe occupancy over a line: meetings, covered ranges, bookings, or segments. Start by deciding whether endpoints are inclusive. Closed intervals `[1, 2]` and `[2, 3]` intersect, while half-open intervals `[1, 2)` and `[2, 3)` do not. This distinction changes comparisons and event ordering.

## Merge overlapping intervals

Sort intervals by start position. Maintain a current merged interval. If the next start overlaps the current end, extend the end to the larger endpoint. Otherwise, emit the current interval and begin a new one. Emit the final interval after the loop.

For `[1, 4]`, `[2, 3]`, and `[6, 8]`, the nested interval must not shrink the first interval's end. Using `max(current_end, next_end)` preserves the covered region. Sorting costs O(n log n); the scan is linear. The returned intervals themselves may require O(n) output space.

## Count simultaneous activity

A sweep line converts each interval into start and end events, sorts them, and updates an active count. The maximum count is the number of simultaneous resources needed. For half-open meetings, process departures before arrivals at the same timestamp so back-to-back meetings can reuse a room.

An alternative sorts starts and uses a min-heap of current end times. Remove finished meetings before allocating the next one. Keeping only currently active intervals gives a direct interpretation of heap size. Specify whether the algorithm removes all finished intervals or uses a different heap invariant.

## Related problems require different decisions

To remove as few intervals as possible to eliminate overlap, selecting intervals by earliest finish supports a greedy solution. To merge coverage, sorting by start is appropriate. To answer many static point queries, sorted endpoints or prefix events may help. Dynamic additions and range queries can require a more advanced data structure.

Test nested intervals, identical intervals, touching endpoints, zero-length intervals if allowed, and a single interval. Write the overlap condition in words before coding it. A correct interval algorithm depends on the endpoint model and objective, not merely on sorting pairs and comparing numbers.
