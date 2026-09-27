# Testing, Debugging, and Tiny Brute-Force Oracles

A solution that passes the provided examples may still fail at boundaries or under a different input arrangement. Design tests from the algorithm's assumptions and invariants. Small, carefully chosen cases often reveal more than a large random example that is difficult to inspect.

## Cover structural boundaries

Test the smallest permitted input, one element, duplicate values, sorted and reverse-sorted data, and a case with no valid answer. For graphs, include disconnected components and cycles. For dynamic programming, exercise empty prefixes and unreachable states. For intervals, include touching endpoints so the inclusivity rule is tested explicitly.

Choose a case where the answer occurs at the beginning, at the end, and across the entire input. If a variable starts at zero, test whether all-negative values make that initialization invalid. If the algorithm mutates input, verify whether that behavior is allowed and whether later calls reuse the same data.

## Compare with a simple oracle

Implement a straightforward exhaustive method for tiny instances, then compare it with the optimized algorithm over many generated cases. For a maximum subarray sum, enumerate all subarrays on arrays of length at most eight. For a greedy selection rule, enumerate all valid small subsets.

Use a fixed random seed so failures can be reproduced. When outputs are not unique, compare validity and objective value rather than requiring identical arrangements. A shortest-path implementation may return different paths with the same correct length.

## Shrink and inspect a failure

When a random case fails, remove elements or simplify values while preserving the failure. A minimal counterexample often reveals the violated invariant immediately. Trace state transitions instead of printing every variable indiscriminately: show window boundaries, the DP state being updated, or the heap entry being relaxed.

Check update order. Many bugs come from recording a prefix too early, marking visited too late, or overwriting a DP value before its final use. Assertions about invariants can identify the first incorrect transition rather than only the wrong final answer.

## Separate correctness from speed

After correctness checks pass, assess complexity using larger representative inputs. Timing a tiny example does not establish scalability, and one fast run does not prove an asymptotic bound. Include output construction, sorting, recursion, and temporary copies in the analysis. Keep a brief regression test for each discovered bug so later refactoring preserves the corrected behavior.
