# Commands and Everyday Usage

Run commands from the repository root. Python 3.12 or newer and GNU Make are required for the Make interface. `make` by itself prints help; it does not install packages, run experiments, or contact IBM. The Makefile selects `.venv/Scripts/python.exe` on Windows and `.venv/bin/python` elsewhere. Override `PYTHON` if your environment lives elsewhere.

## Setup

```bash
make install
make test TEST_ARGS=-q
```

`make install` creates `.venv` if its configuration file does not exist, then installs the core package, development dependencies, and local PennyLane simulator. `make venv` creates only the environment. `BOOTSTRAP_PYTHON` selects the interpreter used to create it, for example `make venv BOOTSTRAP_PYTHON=python3`. An existing environment is reused; these commands do not upgrade its Python version.

Install the IBM bridge only when you intend to experiment with hardware:

```bash
make install-ibm
```

Installation downloads Python packages; it does not connect to your IBM account or submit circuits. Copy `.env.example` to `.env` if needed and fill in the IBM settings described in [the hardware guide](11-real-quantum-hardware.md). Existing `.env` files are never overwritten by a Make target. Local commands and previews need no IBM credentials.

## Choose a command

| Command | Purpose | IBM sampling calls by default |
| --- | --- | --- |
| `make help` or `make` | Print commands and options | 0 |
| `make demo` | Full MMR tournament, 5 primary plus 3 recovery pages | 0 |
| `make tournament SELECTOR=topk` | Tournament with a chosen solver | 0 for local selectors |
| `make compare` | Compare Top-K, MMR, group brute force, and group QUBO | 0 |
| `make local-qaoa` | Full tournament using local PennyLane circuits | 0 |
| `make compare-local` | Classical tournament comparison plus local QAOA | 0 |
| `make query` | One small selection problem with MMR | 0 |
| `make compare-small` | Small-problem comparison, including local QAOA and a global brute-force reference | 0 |
| `make debug` | Teaching state-vector circuit debugger | 0 |
| `make plan` | Offline preview of the full IBM tournament | 0; reports a plan of 46 |
| `make plan-ibm-single` | Offline preview of one small IBM selection | 0; reports a plan of 1 |
| `make ibm-single ARGS=--confirm-submit` | One small hardware selection | 1 |
| `make run-ibm ARGS=--confirm-submit` | Full hardware tournament | 46 |
| `make compare-ibm ARGS=--confirm-submit` | Four classical tournaments plus one hardware tournament | 46 total |
| `make test` | Run the offline regression suite, including mocked IBM boundaries and Make commands | 0 |

Hardware targets refuse to proceed without explicit confirmation. `SELECTOR=ibm` also requires confirmation. `--confirm-submit` alone does not turn a local selector into a hardware selector. Any hardware command can be previewed by passing `ARGS=--dry-run`; dry-run takes precedence even if confirmation is also present. No Make target adds confirmation for you.

## Common examples

```bash
make compare QUERY="How do I solve shortest path problems?"
make tournament SELECTOR=brute-force CANDIDATES=10 SEED=11
make compare-local ITERATIONS=5 SHOTS=256 OUTPUT="experiments/tournaments/local comparison.jsonl"
make query QUERY="How does sliding window work?" SINGLE_CANDIDATES=6 K=3 SELECTOR=mmr
make compare-small SINGLE_CANDIDATES=5 K=3
make debug QUBITS=3
```

For a small hardware experiment, preview exactly the settings you intend to run:

```bash
make plan-ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64
make ibm-single SINGLE_CANDIDATES=4 K=2 SHOTS=64 ARGS=--confirm-submit
```

For the full tournament:

```bash
make plan
make compare-ibm SHOTS=128 ITERATIONS=3 ARGS=--confirm-submit
```

The default plan is 46 application sampling calls and 5,888 requested final shots. The four classical comparisons add no IBM work. Each call optimizes parameters locally before sampling one final circuit. Counts describe this application's calls and requested shots, not a guarantee about provider job accounting, retries inside provider libraries, or billing.

## Options

| Make variable | Default | Applies to |
| --- | --- | --- |
| `QUERY` | Graph-traversal LeetCode question | All selection commands |
| `CANDIDATES` | `30` | Tournaments and tournament preview; at least 8 |
| `SINGLE_CANDIDATES` | `6` | `query`, `compare-small`, `ibm-single`, single preview |
| `K` | `3` | Single-problem commands; tournaments always return 5 + 3 |
| `SELECTOR` | `mmr` | `query` and `tournament`; `demo` always uses MMR |
| `SEED` | `7` | Tournaments and single IBM runs/previews |
| `SHOTS` | `128` | Tournament QAOA/IBM and single IBM runs/previews |
| `ITERATIONS` | `3` | Local parameter optimization for tournament QAOA/IBM and single IBM |
| `LAYERS` | `1` | QAOA depth for tournament QAOA/IBM and single IBM |
| `MAX_HARDWARE_CALLS` | `46` | Tournament hardware-call ceiling; single IBM commands default to 1 |
| `OUTPUT` | `experiments/tournaments/runs.jsonl` | Append-only tournament ledger |
| `QUBITS` | `2` | Circuit debugger |
| `ARGS` | Empty | Additional CLI options for the chosen command |
| `TEST_ARGS` | Empty | Additional pytest options |
| `PYTHON` | Platform-specific `.venv` interpreter | Package and test commands |
| `BOOTSTRAP_PYTHON` | `python` | Creating `.venv` |

Available tournament selectors are `topk`, `mmr`, `brute-force`, `classical-qubo`, `qaoa`, and `ibm`. `query` supports the same list except `ibm`; use `ibm-single` instead. Legacy `query --selector qaoa` and `compare-small` retain their own local QAOA defaults (512 shots, 30 iterations, one layer, warm starts); Make's `SHOTS` and `ITERATIONS` variables apply to the explicit tournament and IBM targets listed above.

The hardware-call ceiling is checked before connecting. For example, a 30-page plan with `MAX_HARDWARE_CALLS=10` fails rather than running a partial tournament. A 10-page tournament needs six sampling calls, so `make plan CANDIDATES=10 MAX_HARDWARE_CALLS=6` succeeds. A runtime factory also enforces the exact planned count; failures do not trigger application-level automatic resubmission.

## Reading output and records

Each group shows the solver bitstring and advancement bitstring, with page titles and filenames next to their positions. The random survivor is explicit. Final results separate the primary five from the recovered three, and the final bitstring uses original retrieval order. JSONL records preserve candidate IDs, numerical scores, discards, and solver metadata. Previews do not create or append a ledger.

Repeated real hardware commands request fresh measurements. Existing ledgers are audit records, not a cache or resume mechanism. If a run fails, inspect completed records before deciding whether to submit another full run. There is no automatic loop that retries until hardware returns a better answer; invalid-cardinality samples use a labeled local fallback.

## Without Make and troubleshooting

The CLI is equivalent and works in PowerShell without Make. Prefix examples with `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Unix:

```bash
.venv/Scripts/python.exe -m quantum_wiki.cli --help
.venv/Scripts/python.exe -m quantum_wiki.cli tournament "Graph shortest paths" --selector mmr
.venv/Scripts/python.exe -m quantum_wiki.cli compare-tournament "Graph shortest paths" --include-qaoa
.venv/Scripts/python.exe -m quantum_wiki.cli tournament "Graph shortest paths" --selector ibm --dry-run
.venv/Scripts/python.exe -m quantum_wiki.cli run-ibm "Graph shortest paths" --candidates 4 --k 2 --dry-run
```

If Make or Python is missing, install GNU Make or use the CLI, and install Python 3.12+ before creating the environment. If PennyLane cannot be imported, run `make install` using the same interpreter as execution. If the IBM bridge is missing, run `make install-ibm`. A dry run checks local inputs and planned workload, not credentials, package compatibility, backend availability, quotas, or hardware execution.

Quote questions and paths with spaces as shown. For complex literal text containing shell metacharacters, use the Python CLI with your shell's quoting rules.
