# Prefix Sums and Difference Arrays

Prefix sums turn repeated range sums into constant-time subtraction. Define `prefix[0] = 0` and `prefix[i + 1] = prefix[i] + nums[i]`. The sum over the half-open interval `[left, right)` is then `prefix[right] - prefix[left]`. The extra initial zero makes intervals beginning at index zero work without a special case.

## Count subarrays with a target sum

At a current prefix sum s, any earlier prefix equal to `s - target` defines a subarray ending here with the desired sum. Store frequencies of earlier prefix sums, starting with `{0: 1}`. Add the frequency of `s - target` to the answer before recording s.

For `[1, -1, 1]` and target 1, the three valid subarrays are the first element, the last element, and the entire array. Repeated prefix values represent different starting positions, so a set would lose answers. This approach handles negative numbers, unlike a simple monotone-sum sliding window. Expected time and auxiliary space are O(n).

To find the longest target-sum subarray, store the earliest index for each prefix instead of its frequency. For divisibility questions, equal prefix remainders identify ranges whose sums are divisible by the modulus. Choose the stored information according to whether the task asks for existence, count, or maximum length.

## Difference arrays reverse the perspective

When many operations add a value v to every position in an inclusive range `[left, right]`, update a difference array at two boundaries: add v at left and subtract v at right + 1 when that position exists. One prefix scan reconstructs the final values. This costs O(n + q) for q offline updates.

Difference arrays do not directly support arbitrary interleaved updates and queries. A Fenwick tree or segment tree is appropriate when answers are needed between changes. Two-dimensional prefix sums similarly support static rectangular sums using inclusion-exclusion over four corners.

Test single-element ranges, ranges touching either edge, a zero target, and repeated prefix sums. Most errors involve interval conventions, recording the current prefix too early, or forgetting the initial empty prefix that represents a subarray starting at the beginning.
