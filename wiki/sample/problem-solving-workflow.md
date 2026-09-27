# A Practical LeetCode Problem-Solving Workflow

Begin by restating the task as a precise input-output contract. Determine whether the answer is a value, an index, a count, a path, or every valid arrangement. Ask whether duplicates, negative numbers, empty inputs, and disconnected components are allowed. These details often determine the algorithm more strongly than the story around the problem.

## Turn examples into a model

Work through one small example by hand. Write down the information needed to make each decision. For Two Sum, checking every pair suggests that the missing information is whether a previously seen value equals the current complement. That observation leads naturally to a hash map. The useful step is identifying repeated work, rather than recognizing a memorized title.

Write a straightforward solution first, at least in pseudocode. Estimate its cost from the constraints. Then identify its bottleneck: repeated scans, repeated subproblems, unnecessary sorting, or exploration of impossible states. Improve that specific bottleneck using an appropriate data structure or invariant.

## Explain before implementing

A short plan should include the state, how it changes, when the answer is updated, and why no valid answer is skipped. For a sliding window, define exactly what the window contains and what makes it valid. For dynamic programming, define what each table entry means before writing its recurrence.

Implementation is easier when these choices are explicit. Use variable names that describe roles, such as `left`, `best_length`, or `remaining_indegree`. Avoid mixing inclusive and exclusive endpoints. Keep problem-specific decisions separate from mechanical traversal where practical.

## Validate the finished solution

Trace the smallest valid input, a boundary case, repeated values, and a case where the optimal answer occurs at the end. Check return types and whether mutating the input is allowed. State time and auxiliary-space complexity, including recursion depth and output size when relevant.

After solving, record the decisive observation and one failure mode. A useful learning note is "negative values break the monotone-sum window," not merely "this was a sliding-window problem." Practice explaining why the method works without referring to the original example; that is a stronger sign of understanding than reproducing code.
