# Hash Maps, Sets, and Frequency Counting

Use a hash map when a problem repeatedly asks about information associated with a key: an earlier index, an occurrence count, or the best value for a state. Use a set when only membership matters. This often replaces repeated linear scans with expected constant-time lookups.

## Complement lookup

For Two Sum, scan values from left to right. Before storing the current value, look for `target - value` in a map of earlier values to indices. Looking up first prevents using the same array element twice. With input `[3, 3]` and target 6, the second occurrence finds the first, so duplicates are handled correctly.

The invariant is that the map describes only the processed prefix. Each valid pair is detected when its later endpoint is visited. Expected time is O(n), and the map may hold O(n) entries. If the question asks for all pairs or the number of pairs, storing one index per value may no longer be sufficient.

## Frequency and canonical keys

An anagram comparison can count characters and compare the resulting frequency maps. To group anagrams, use a hashable canonical representation, such as a sorted string or a fixed-alphabet count tuple. Sorting a word costs O(L log L); building a frequency tuple costs O(L + A), where A is the alphabet size. Do not assume a 26-letter alphabet unless the input guarantees it.

For prefix-sum counting, map each prefix sum to its frequency, not merely its latest position. For longest-span problems, storing the earliest position may be the correct choice. The map's value should follow the information the future computation needs.

## Common mistakes and checks

Do not mutate a dictionary's size while iterating directly over it. Do not use a mutable list as a dictionary key; convert structural state to a tuple when appropriate. Be careful with missing counts, especially when decrementing a sliding-window frequency map: zero-valued entries may need removal if dictionary size represents distinct values.

Test duplicate values, a complement equal to the current value, absent answers, and empty input when permitted. Explain whether the map tracks seen elements, remaining elements, or the current window. Most subtle hash-map bugs come from updating the right information at the wrong time.
