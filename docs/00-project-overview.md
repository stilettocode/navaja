# Project Overview

This project asks a practical question: after semantic retrieval finds a handful of relevant wiki pages, can a context selector choose pages that are useful without repeating the same information?

The pipeline is classical first: Markdown pages become embeddings, cosine similarity ranks candidates, and a selector chooses exactly `K` pages. The objective rewards relevance and penalizes pairwise redundancy.

The research question is whether a QUBO and QAOA representation helps us learn anything useful about this small optimization problem. **This repository does NOT assume or claim quantum advantage.** Classical heuristics may be much faster, and a simulator is itself a classical program.

A page decision is a bit: `0` means leave it out and `1` means include it. That simple representation lets us compare Top-K, greedy MMR, brute force, a classical QUBO evaluator, and a QAOA implementation through one interface.

The honest success condition is a functioning experiment and a clear negative result when classical methods win.
