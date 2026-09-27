# Bit Manipulation and Compact State Masks

Bit operations treat an integer as a compact collection of binary flags. They are useful for subset enumeration, parity, set membership over a small universe, and problems with cancellation properties. Before using a trick, identify the assumptions about value range, duplicates, and integer width.

## Flags and subsets

For a small universe of indexed items, bit i represents whether item i is present. Set it with OR, test it with AND, toggle it with XOR, and clear it with an inverted single-bit mask. A subset of n items corresponds to an integer from zero through 2 to the n minus one.

A bitmask can be part of a memoization state, such as `(current_vertex, visited_mask)` for a small traveling-salesperson-style problem. It compresses representation but does not remove the exponential number of possible subsets. Estimate state count before choosing this approach.

## Cancellation and low bits

XOR satisfies `x ^ x == 0` and `x ^ 0 == x`. Therefore, XORing an array finds the unique value when every other value occurs exactly twice. It does not solve arbitrary frequency problems; values appearing three times require a different argument.

For a positive integer x, `x & (x - 1)` removes its lowest set bit. Repeating this operation counts set bits in time proportional to the number of ones. The condition `x > 0 and x & (x - 1) == 0` recognizes powers of two; the positivity test prevents zero from being accepted.

## Integer-model pitfalls

Python integers are arbitrary precision, and bitwise operations on negative values behave as though sign bits extend indefinitely. Algorithms that assume a fixed 32-bit word may need an explicit mask and conversion back to a signed result. Do not copy overflow-dependent code from another language without adapting the model.

The expression `~x` is not simply a fixed-width inversion unless a width is enforced. Parentheses make mixed shifts, arithmetic, and comparisons easier to audit even when operator precedence would technically work.

Test zero, one set bit, several set bits, duplicate values, and negative inputs if permitted. Explain what each bit means in the problem domain. Prefer a clear set-based solution when bit manipulation adds complexity without a useful performance or state-representation benefit.
