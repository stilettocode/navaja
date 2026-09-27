.DEFAULT_GOAL := help

ifeq ($(OS),Windows_NT)
PYTHON ?= .venv/Scripts/python.exe
else
PYTHON ?= .venv/bin/python
endif
BOOTSTRAP_PYTHON ?= python
QUERY ?= How do I solve shortest path and graph traversal problems on LeetCode?
CANDIDATES ?= 30
SINGLE_CANDIDATES ?= 6
K ?= 3
SELECTOR ?= mmr
SEED ?= 7
SHOTS ?= 128
ITERATIONS ?= 3
LAYERS ?= 1
QUBITS ?= 2
MAX_HARDWARE_CALLS ?= 46
OUTPUT ?= experiments/tournaments/runs.jsonl
ARGS ?=
TEST_ARGS ?=

CLI = "$(PYTHON)" -m quantum_wiki.cli
QUANTUM_FLAGS = --shots $(SHOTS) --iterations $(ITERATIONS) --layers $(LAYERS) --seed $(SEED)
TOURNAMENT_FLAGS = --candidates $(CANDIDATES) $(QUANTUM_FLAGS) --output "$(OUTPUT)" --max-hardware-calls $(MAX_HARDWARE_CALLS)
SINGLE_FLAGS = --candidates $(SINGLE_CANDIDATES) --k $(K)

.PHONY: help venv install install-ibm test demo tournament compare local-qaoa compare-local query compare-small debug plan plan-ibm-single run-ibm compare-ibm ibm-single

help:
	@echo "Setup: make venv, make install, make install-ibm"
	@echo "Tests: make test [TEST_ARGS=-q] - no IBM jobs"
	@echo "Local tournaments: make demo, make tournament SELECTOR=mmr, make compare"
	@echo "Local circuits: make local-qaoa, make compare-local"
	@echo "Small problems: make query SELECTOR=mmr, make compare-small, make debug"
	@echo "Offline IBM previews: make plan, make plan-ibm-single"
	@echo "Hardware: make ibm-single, make run-ibm, make compare-ibm"
	@echo "Hardware targets require ARGS=--confirm-submit; none confirm automatically."
	@echo "Options: QUERY, CANDIDATES=30, SINGLE_CANDIDATES=6, K=3, SEED=7"
	@echo "Circuit options: SHOTS=128, ITERATIONS=3, LAYERS=1, MAX_HARDWARE_CALLS=46"
	@echo "Other options: SELECTOR=mmr, QUBITS=2, OUTPUT, ARGS, PYTHON, BOOTSTRAP_PYTHON"
	@echo "Default full IBM tournament: 46 sampling calls, 5888 final shots; preview first."

venv: .venv/pyvenv.cfg

.venv/pyvenv.cfg:
	"$(BOOTSTRAP_PYTHON)" -m venv .venv

install: venv
	"$(PYTHON)" -m pip install -e ".[dev,quantum]"

install-ibm: venv
	"$(PYTHON)" -m pip install -e ".[dev,quantum,ibm]"

test:
	"$(PYTHON)" -m pytest $(TEST_ARGS)

demo:
	$(CLI) tournament "$(QUERY)" --selector mmr $(TOURNAMENT_FLAGS) $(ARGS)

tournament:
	$(CLI) tournament "$(QUERY)" --selector $(SELECTOR) $(TOURNAMENT_FLAGS) $(ARGS)

compare:
	$(CLI) compare-tournament "$(QUERY)" $(TOURNAMENT_FLAGS) $(ARGS)

local-qaoa:
	$(CLI) tournament "$(QUERY)" --selector qaoa $(TOURNAMENT_FLAGS) $(ARGS)

compare-local:
	$(CLI) compare-tournament "$(QUERY)" --include-qaoa $(TOURNAMENT_FLAGS) $(ARGS)

query:
	$(CLI) query "$(QUERY)" --selector $(SELECTOR) $(SINGLE_FLAGS) $(ARGS)

compare-small:
	$(CLI) compare "$(QUERY)" $(SINGLE_FLAGS) $(ARGS)

debug:
	$(CLI) debug-circuit --qubits $(QUBITS) $(ARGS)

plan:
	$(CLI) tournament "$(QUERY)" --selector ibm $(TOURNAMENT_FLAGS) $(ARGS) --dry-run

plan-ibm-single:
	$(CLI) run-ibm "$(QUERY)" $(SINGLE_FLAGS) $(QUANTUM_FLAGS) --max-hardware-calls 1 $(ARGS) --dry-run

run-ibm:
	$(CLI) tournament "$(QUERY)" --selector ibm $(TOURNAMENT_FLAGS) $(ARGS)

compare-ibm:
	$(CLI) compare-tournament "$(QUERY)" --include-ibm $(TOURNAMENT_FLAGS) $(ARGS)

ibm-single:
	$(CLI) run-ibm "$(QUERY)" $(SINGLE_FLAGS) $(QUANTUM_FLAGS) --max-hardware-calls 1 $(ARGS)
