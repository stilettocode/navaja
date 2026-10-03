# Quantum Wiki

Quantum Wiki is an educational research project about choosing useful, non-redundant context from Markdown wiki pages.

The project follows this pipeline:

```text
user question
    -> retrieve up to 30 LeetCode guide pages
    -> tournament groups of 5: solver chooses 3, chance saves 1
    -> retain 5 primary pages
    -> tournament over discarded pages retains 3 more
    -> return 8 distinct pages
    -> compare classical and quantum approaches
```

The important research rule is:

> This repository does not assume or claim quantum advantage.

The [scientific evaluation report](docs/16-scientific-evaluation-report.md) includes a 12-query local study, exact-oracle checks, seed and survivor ablations, and a three-job IBM pilot. It records hardware usage, distributions, limitations, and the most useful next experiments.

For these small examples, classical methods are expected to be faster and often better. The goal is to understand the engineering and concepts honestly.

## Quick Start and Commands

Run these from the repository root with Python 3.12+ and GNU Make:

```bash
make install
make test TEST_ARGS=-q
make demo
make compare
make compare-local
```

All five commands above submit **zero IBM jobs**. Installation downloads Python packages; the experiments run locally. `make` or `make help` lists the available commands.

Customize a run without assembling CLI flags:

```bash
make compare QUERY="How do I solve shortest path problems?" CANDIDATES=30 SEED=7
make local-qaoa ITERATIONS=5 SHOTS=256
make query SELECTOR=mmr SINGLE_CANDIDATES=6 K=3
```

Preview hardware work offline before choosing to submit:

```bash
make plan
make plan-ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64
```

Previews require no credentials or IBM packages, perform no circuit execution, and write no ledger. A full 30-page hardware tournament plans **46 sampling calls / 5,888 final shots** at the default 128 shots. A single problem needs one sampling call; choosing all or zero candidates needs none.

After installing the IBM bridge and configuring `.env`, hardware commands still require explicit confirmation:

```bash
make ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64 ARGS=--confirm-submit
make compare-ibm ARGS=--confirm-submit
```

The optimizer, grouping, random survival, scoring, and fallback remain local. Only the final optimized numeric circuit for each nontrivial hardware group is sampled by IBM. The backend is selected once per run; hardware optimization is disabled. `MAX_HARDWARE_CALLS` caps the planned tournament workload before any connection (default 46). The runtime factory also enforces the exact plan, and the application does not automatically resubmit failed jobs.

See the **[complete command reference](docs/14-command-reference.md)** for every Make target, parameter defaults, direct Python equivalents, and troubleshooting. See the [hardware guide](docs/11-real-quantum-hardware.md) for the audited submission boundary.

## What Problem Are We Solving?

Suppose retrieval finds four candidate pages and we want to select two. Each page receives a binary decision:

```text
0 = leave this page out
1 = include this page
```

The selector rewards pages that appear relevant to the question and penalizes selecting pages that are very similar to each other. The ordinary Python scoring function is the source of truth. Every QUBO and QAOA result is checked against that same idea.

## Setup

The project uses a virtual environment in `.venv`. Make selects the Windows or Unix interpreter path automatically. From a terminal opened in the repository root:

```bash
make install
```

This creates `.venv` if missing and installs the development tools and local PennyLane simulator. Set `BOOTSTRAP_PYTHON=python3` if needed. The IBM hardware bridge is separate:

```bash
make install-ibm
```

The commands in this README use the project environment through the Makefile. If you run Python directly, use:

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli --help
```

If you use `python -m ...` without activating `.venv`, Windows may use a different Python installation that does not have PennyLane installed. To make `python` refer to the project environment in Git Bash, run:

```bash
source .venv/Scripts/activate
```

## First Learning Run

Run the tests first:

```bash
make test
```

Then run the classical tournament:

```bash
make demo
```

This uses MMR inside the tournament and returns five primary pages plus three recovery pages. MMR means Maximal Marginal Relevance. In plain language, it repeatedly chooses a relevant page while trying not to choose pages that repeat information already selected.

The output includes selected page titles and a score. The score is not a percentage or a universal quality rating. It is an internal comparison value calculated as:

```text
relevance reward - redundancy penalty
```

## Comparing Selectors

The default comparison now runs the full tournament with four classical group solvers:

```bash
make compare
make compare ARGS="--include-qaoa"
```

To include IBM hardware sampling for every solver group, after configuring the IBM bridge:

```bash
make compare-ibm ARGS="--shots 128 --iterations 3 --confirm-submit"
```

All methods begin with the same candidate order and grouping seed. Later pools depend on their choices. The table reports final eight-page scores, elapsed seconds, and group-call counts. Brute force is exact **inside each group**, not a global eight-page optimum. At 30 candidates, each tournament makes **46 group-solver calls**; the IBM variant samples each of those groups remotely. `--confirm-submit` authorizes the entire tournament. No hardware jobs are submitted by the ordinary comparison.

### Tournament rules and grouping

The wiki contains 30 original, roughly page-length LeetCode guides, covering problem analysis, arrays, strings, trees, graphs, dynamic programming, and testing. The default tournament considers all 30; `--candidates` can restrict retrieval to a smaller pool of at least eight.

1. Shuffle the active pool with a recorded seed and form disjoint groups of five.
2. Each full group keeps the solver's three choices plus one uniformly random survivor from its two rejects. Remember the fully discarded page.
3. Reshuffle survivors each round. A leftover group of one to four receives a bye when other full groups exist, so it loses no pages that round.
4. Stop the primary tournament at exactly five pages.
5. Run the same process on the complete primary discard pool, targeting three recovery pages. Once that pool fits in one group, choose two through the solver and one at random from the remaining candidates. If only three remain initially, all three advance without a solver call.
6. Return the five primary and three recovery winners together. Recovery discards stay in the ledger; they do not re-enter indefinitely.

During recovery, relevance is adjusted by similarity to the five fixed primary winners. This makes solver choices reward complementary material. The final eight-page score always uses the original objective. Random survivors are still selected uniformly, so they can reduce the objective; that is an intentional exploration rule.

Seeded shuffling is the initial grouping policy: it avoids hard-coding topic or retrieval-rank boundaries and makes classical runs reproducible. Small tails receive byes, so grouping still affects outcomes. Repeating comparisons with several seeds is a useful next experiment; the scheme is a heuristic, with no guarantee of globally optimal selection.

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli tournament \
  "How do I solve shortest path and graph traversal problems on LeetCode?" \
  --selector mmr --candidates 30 --seed 7

.venv/Scripts/python.exe -m quantum_wiki.cli compare-tournament \
  "How do I solve shortest path and graph traversal problems on LeetCode?" \
  --include-ibm --shots 128 --iterations 3 --confirm-submit
```

Every group prints its solver bitstring, its advancement bitstring after the random survivor is added, and each bit's page title, filename, and outcome. The final bitstring uses the **original retrieved candidate order**, with exactly eight ones. Output distinguishes five primary winners from three recovery winners.

An append-only JSONL ledger at `experiments/tournaments/runs.jsonl` records page identities, group order, random survivors, discarded pages, solver metadata, final scores, and timings. Set `--output PATH` to choose another file. Each event is flushed immediately, retaining completed work if a hardware call fails; automatic resumption is not implemented. Tournament QAOA disables shared warm-start state to avoid making one method depend on an earlier comparison run. Local sampling uses the seed; hardware measurements remain stochastic.

See [Tournament design and experiment notes](docs/13-tournament-selection.md) for edge cases and evaluation suggestions.

### Small single-problem comparisons

The original single-problem commands are still available for teaching and checking a global optimum on a tiny pool:

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli compare \
  "How do I solve shortest path problems?" --candidates 6 --k 3
```

This runs the same candidate problem through several algorithms:

| Selector | What it does | Why it exists |
| --- | --- | --- |
| `topk` | Chooses the pages with the highest individual relevance | Simple baseline; ignores redundancy |
| `mmr` | Greedily balances relevance and similarity to already-selected pages | Fast practical heuristic |
| `brute-force` | Tries every valid combination | Small-problem debugging oracle |
| `classical-qubo` | Evaluates the binary QUBO classically | Checks the optimization representation |
| `qaoa` | Runs the QAOA circuit and samples bitstrings | Quantum-computing experiment |

Example output looks like this:

```text
Algorithm          Score       Gap
--------------------------------------
brute-force        -0.3113    0.0000
mmr                -0.3192    0.0080
topk               -0.5086    0.1973
classical-qubo     -0.3113    0.0000
qaoa               -0.3113    0.0000
```

Interpret it this way:

- **Score** is the objective value for that selector's chosen pages.
- A higher score is better for this problem.
- A negative score is not automatically bad. It means redundancy penalties outweighed relevance rewards under the current toy embedding and weights.
- **Gap** is the difference from the brute-force result.
- A gap of `0.0000` means the selector found the same objective value as the best known small-problem solution.
- A larger gap means the selector produced a lower-quality selection according to this objective.
- Matching brute force does not mean an algorithm is fast, scalable, or quantum-advantaged.

### How to compare scores correctly

Assume two algorithms are solving the exact same problem:

```text
same question
same retrieved candidate pages
same candidate count N
same selection count K
same relevance/redundancy weights
```

Then compare their scores directly:

```text
Algorithm A: score = 2.40
Algorithm B: score = 2.10
```

Algorithm A is better according to this objective by `0.30` points. The score is not a percentage, probability, or universal measure of answer quality. It is a ruler defined by this particular problem's relevance values and similarity penalties.

The score is calculated as:

```text
score = selected relevance reward - selected pairwise redundancy penalty
```

For example, if a selection has:

```text
relevance reward:       2.80
redundancy penalty:     0.40
score:                  2.40
```

another selection with relevance `2.60` and redundancy `0.05` scores `2.55` and is preferred, even though its total relevance is slightly lower. That is the central reason Top-K can lose: it may choose individually relevant pages that repeat one another.

The gap is easier to interpret as a distance from the small-problem optimum:

```text
optimality gap = brute_force_score - algorithm_score
```

If brute force scores `2.713`:

```text
brute force: 2.713 -> gap 0.000
MMR:         2.645 -> gap 0.068
Top-K:       2.401 -> gap 0.312
```

MMR is closer to the best known answer than Top-K. A gap of zero means equal objective value, not necessarily identical page selection: different page combinations can tie under the same scoring function.

Do not compare a score from `N=4, K=2` with a score from `N=6, K=3`. Those are different optimization problems. More candidates create more possible combinations, and selecting more pages changes both the relevance total and the number of possible redundancy penalties. Also avoid comparing scores produced with different embedding models or objective weights.

For a meaningful experiment, record at least:

```text
query, candidate page IDs, N, K, relevance/redundancy weights,
algorithm, selected page IDs, score, gap, and runtime
```

Runtime is separate from score. A method can produce the best score and still be much slower, which is why this project reports both quality and execution cost.

Brute force is used as the reference because it checks every valid combination. It is trustworthy for small candidate sets but becomes impractical as the number of candidates grows.

## Running One Selector

You can choose a selector and control the problem size:

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli query \
  "How do I solve shortest path and graph traversal problems?" \
  --selector mmr \
  --candidates 4 \
  --k 2
```

Important options:

- `--selector`: chooses the algorithm.
- `--candidates`: number of retrieved pages given to the selector.
- `--k`: exact number of pages to select.

The retrieval stage happens before selection. The selector sees only the candidate pages, not the entire wiki.

## Running Local QAOA

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli query \
  "How do I solve shortest path and graph traversal problems?" \
  --selector qaoa \
  --candidates 4 \
  --k 2
```

This uses PennyLane's local `default.qubit` simulator. It is a real PennyLane circuit, but the circuit is simulated by your computer rather than executed on quantum hardware.

QAOA stands for Quantum Approximate Optimization Algorithm. At a beginner level, think of it as a loop:

```text
CPU chooses circuit parameters
    -> circuit runs
    -> measurements produce bitstrings
    -> classical code scores those bitstrings
    -> CPU updates the parameters
    -> repeat
```

The QAOA output includes a bitstring such as:

```text
Bitstring: 1001
```

For four candidates, this means:

```text
candidate 0: selected
candidate 1: not selected
candidate 2: not selected
candidate 3: selected
```

The selected page list is the human-readable decoding of that bitstring. Because this project requires exact `K`, a valid result should contain exactly `K` ones.

The QAOA result is probabilistic. It does not guarantee the optimum, and matching the brute-force answer on one small run is not evidence of quantum advantage.

### Warm starts

QAOA now saves locally optimized `gamma` and `beta` values in:

```text
experiments/warm_starts/qaoa_parameters.json
```

On a later run with the same number of candidates, `K`, and QAOA depth `p`, those values are loaded as the initial guess. The optimizer then refines them for the new QUBO. This is a warm start, not a guarantee that the old parameters are still good.

The file does not contain page text, API credentials, or a saved circuit. The circuit is generated from Python code, the current QUBO, and the parameters. Generated JSON warm starts are ignored by Git because they are local experiment state.

### What changes when pages change?

This is similar to machine-learning inference, but not exactly the same. QAOA has a reusable circuit template and tunable values such as `gamma` and `beta`. Those values are learned for an optimization problem, not permanently for the whole wiki.

When the retrieved pages change, their relevance and pairwise-similarity numbers usually change too. That produces a new QUBO, so the best QAOA parameters may also change. The circuit shape can often be reused, but the cost information and usually the parameters must be updated.

There are three useful levels of reuse:

1. **Reuse the circuit template.** The same cost-layer and mixer-layer code works for every problem with the same number of candidates.
2. **Warm-start the parameters.** A previous query's `gamma` and `beta` can be used as the starting guess for a similar new query. This may reduce local optimization work, but it is not guaranteed to help.
3. **Reuse parameters without retraining.** This is only an approximation. It can be a useful fast path when candidate sets and scores are similar, but the result must still be evaluated classically.

The pages are not loaded into qubits as raw text. Classical retrieval and embeddings turn the pages into a small numeric QUBO first. The quantum circuit receives that numeric cost representation.

## Understanding the Circuit Debugger

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli debug-circuit --qubits 2
```

This is a tiny teaching simulator. It starts at `00`, applies Hadamard gates, and prints each basis state's amplitude and probability.

Useful distinctions:

- **Amplitude** is the complex-valued quantity manipulated by quantum gates.
- **Probability** is the chance of measuring that basis state, calculated as the squared magnitude of its amplitude.
- **Measurement** gives a classical bitstring; it does not reveal the whole amplitude table.
- The debugger shows the full state vector because it is a classical simulator. Real hardware does not provide the entire state vector for free.

## IBM Quantum Hardware

IBM hardware is optional and can involve queue time, usage limits, and account-specific access. Install the bridge:

```bash
make install-ibm
```

Create `.env` from `.env.example` and configure:

```env
IBM_QUANTUM_TOKEN=your_api_key
IBM_QUANTUM_INSTANCE=your_instance_crn
IBM_QUANTUM_BACKEND=
IBM_QUANTUM_CHANNEL=ibm_quantum_platform
```

Where these values come from:

- `IBM_QUANTUM_TOKEN`: API key from your IBM Quantum account.
- `IBM_QUANTUM_INSTANCE`: CRN from the IBM Quantum Platform Instances page.
- `IBM_QUANTUM_BACKEND`: an exact available QPU name. Leave it blank to let IBM select an eligible backend.
- `IBM_QUANTUM_CHANNEL`: normally `ibm_quantum_platform`; leave it unchanged.

Never commit `.env` or share the token. Read [docs/11-real-quantum-hardware.md](docs/11-real-quantum-hardware.md) before submitting a job.

The default IBM workflow optimizes `gamma` and `beta` locally with PennyLane, then sends only the final optimized circuit to IBM for measurement. This avoids turning every gradient-estimation step into a remote workload.

Run a small hardware experiment only when ready:

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli run-ibm \
  "How do I solve shortest path problems?" \
  --candidates 4 --k 2 --shots 128 --iterations 3 --confirm-submit
```

For the complete 30-page IBM tournament instead, use `make run-ibm ARGS="--confirm-submit"`. For classical and hardware tournament results together, use `make compare-ibm ARGS="--confirm-submit"`.

The `--confirm-submit` flag is required whenever hardware sampling is planned. Without it, the program refuses to contact IBM. `--dry-run` always remains offline, even alongside confirmation. Hardware output should be interpreted as noisy sampled evidence, not as a guaranteed answer or a speed benchmark. Parameter optimization is always local; the former remote-optimizer API hook is rejected.

## Architecture

```text
Markdown wiki
    -> local embeddings
    -> cosine retrieval
    -> SelectionProblem: relevance, similarity, K
    -> Top-K / MMR / brute force / QUBO / QAOA
    -> selected pages and classical objective score
```

For IBM hardware, the final branch is:

```text
QAOASelector
    -> PennyLane circuit
    -> PennyLane-Qiskit bridge
    -> IBM Runtime
    -> IBM QPU
    -> measured bitstrings
    -> classical scoring
```

## Repository Structure

- `src/quantum_wiki/wiki`: Markdown loading and page models
- `src/quantum_wiki/retrieval`: deterministic embeddings and cosine search
- `src/quantum_wiki/selection`: common problem model and interchangeable selectors
- `src/quantum_wiki/quantum`: state-vector teaching tools and IBM adapter
- `wiki/sample`: 30 LeetCode guides with overlapping techniques and complementary topics
- `tests`: objective, QUBO, QAOA, IBM configuration, and integration checks
