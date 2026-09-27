# Stacks for Nested Structure and Parsing

A stack stores unresolved work in last-in, first-out order. It naturally models nested parentheses, expression contexts, undo operations, and iterative depth-first traversal. In Python, a list with `append()` and `pop()` provides the usual stack operations at the end.

## Matching delimiters

When reading an opening bracket, push its type. When reading a closing bracket, require a nonempty stack whose top is the matching opener, then pop it. At the end, the stack must be empty. Counting opening and closing brackets alone is insufficient because `([)]` has balanced counts but invalid nesting.

The invariant is that the stack contains precisely the unmatched opening delimiters in encounter order. A closing delimiter must match the most recent unresolved opener. Each character is processed once, giving O(n) time and O(n) worst-case space for deeply nested input.

## Store enough context

For decoding a string such as `3[a2[c]]`, each nested section needs both its repeat count and the previously accumulated prefix. Push that context on an opening bracket and restore it on the matching close. Parse multi-digit counts as complete numbers, and reset temporary state when entering a new section.

The runtime must include the length of the decoded output; a short encoded string can expand dramatically. Repeated immutable-string concatenation can add copying overhead, so use lists of pieces when appropriate. Do not describe a decoder as linear in input length if it must produce much more output.

## Expressions and traversal

Expression evaluation may need separate stacks for operators and values, or a recursive parser whose call stack represents nested expressions. Unary minus, precedence, and associativity are separate rules. Do not assume a delimiter stack alone solves arbitrary arithmetic parsing.

For iterative tree traversal, stack entries can include a node and a processing stage. This makes recursive enter/exit behavior explicit and is useful when an answer depends on children being processed first.

Test an unexpected closing bracket, leftover opening brackets, empty input, deep nesting, and repeated adjacent groups. Ask what each stack entry represents and what event resolves it. If the answer is merely "a previous value," the invariant likely needs to be more precise.
