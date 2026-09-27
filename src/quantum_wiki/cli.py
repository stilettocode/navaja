import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from dotenv import load_dotenv

from quantum_wiki.quantum.state_debugger import H, StateDebugger
from quantum_wiki.quantum.ibm import IBMQuantumConfig, IBMDeviceFactory
from quantum_wiki.retrieval.retriever import Retriever
from quantum_wiki.selection.brute_force import select_brute_force
from quantum_wiki.selection.classical_qubo import select_classical_qubo
from quantum_wiki.selection.mmr import select_mmr
from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.qaoa import QAOAConfig, QAOASelector
from quantum_wiki.selection.scoring import score_selection
from quantum_wiki.selection.topk import select_topk
from quantum_wiki.selection.tournament import select_tournament, tournament_group_calls
from quantum_wiki.wiki.loader import load_markdown_pages


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_WIKI = ROOT / "wiki" / "sample"

def load_ibm_config() -> IBMQuantumConfig:
    """Read credentials only after an actual hardware workload is authorized."""
    load_dotenv(ROOT / ".env")
    return IBMQuantumConfig.from_environment()


def build_problem(query: str, candidates: int, k: int) -> tuple[list, SelectionProblem]:
    if candidates < 1 or not 0 <= k <= candidates:
        raise ValueError("require positive candidates and 0 <= k <= candidates")
    pages = load_markdown_pages(SAMPLE_WIKI)
    retrieved = Retriever(pages).retrieve(query, candidates)
    embeddings = np.array([item.page.embedding for item in retrieved])
    similarity = embeddings @ embeddings.T
    problem = SelectionProblem(
        [item.page.id for item in retrieved],
        np.array([item.relevance for item in retrieved]),
        similarity,
        np.array([item.page.token_count for item in retrieved]),
        k=k,
    )
    return retrieved, problem


def run_selector(name: str, problem: SelectionProblem):
    selectors = {
        "topk": select_topk,
        "mmr": select_mmr,
        "brute-force": select_brute_force,
        "classical-qubo": select_classical_qubo,
        "qaoa": QAOASelector().select,
    }
    try:
        return selectors[name](problem)
    except KeyError as error:
        raise ValueError(f"unknown selector: {name}") from error


def query_command(args: argparse.Namespace) -> None:
    retrieved, problem = build_problem(args.query, args.candidates, args.k)
    result = run_selector(args.selector, problem)
    print(f"Query: {args.query}\nCandidates: {len(retrieved)}\nSelect: {args.k}\n")
    print(f"Selector: {args.selector}\nScore: {result.objective:.4f}\nBitstring: {result.bitstring}")
    print("\nSelected pages:")
    for index in result.selected_indices:
        print(f"- {retrieved[index].page.title} ({retrieved[index].page.id})")
    if result.metadata.get("warning"):
        print(f"\nNote: {result.metadata['warning']}")


def compare_command(args: argparse.Namespace) -> None:
    retrieved, problem = build_problem(args.query, args.candidates, args.k)
    results = {name: run_selector(name, problem) for name in ("brute-force", "mmr", "topk", "classical-qubo", "qaoa")}
    optimum = results["brute-force"].objective
    print(f"Query: {args.query}\nCandidates: {len(retrieved)}\nSelect: {args.k}\n")
    print("Algorithm          Score       Gap")
    print("--------------------------------------")
    for name, result in results.items():
        print(f"{name:<18} {result.objective:>7.4f}  {optimum - result.objective:>8.4f}")
    print("\nThis comparison reports quality gaps; it does not claim quantum advantage.")


def debug_command(args: argparse.Namespace) -> None:
    debugger = StateDebugger(args.qubits)
    for qubit in range(args.qubits):
        debugger.apply(H, qubit, f"after H on qubit {qubit}")
    for snapshot in debugger.snapshots:
        print(f"\n{snapshot.label}")
        for index, amplitude in enumerate(snapshot.amplitudes):
            print(f"{index:0{args.qubits}b}  {amplitude.real:+.3f}{amplitude.imag:+.3f}i  probability={abs(amplitude) ** 2:.3f}")


def validate_quantum_options(args: argparse.Namespace) -> None:
    if args.shots < 1 or args.layers < 1 or args.iterations < 0 or args.seed < 0:
        raise ValueError("require shots >= 1, layers >= 1, iterations >= 0, seed >= 0")
    if args.max_hardware_calls < 0:
        raise ValueError("max-hardware-calls must be nonnegative")


def check_hardware_plan(args: argparse.Namespace, calls: int) -> None:
    print(f"Hardware workload: {calls} sampling calls, {calls * args.shots} requested final shots.")
    print("Parameter optimization, scoring, random survivors, and byes stay local.")
    if calls > args.max_hardware_calls:
        raise ValueError(f"planned {calls} hardware calls exceeds --max-hardware-calls={args.max_hardware_calls}")
    if calls and not args.dry_run and not args.confirm_submit:
        raise SystemExit("Refusing to submit to IBM Quantum. Preview with --dry-run; add --confirm-submit to authorize this workload.")


def run_ibm_command(args: argparse.Namespace) -> None:
    validate_quantum_options(args)
    retrieved, problem = build_problem(args.query, args.candidates, args.k)
    if len(problem.page_ids) > 12:
        raise ValueError("single QAOA problems are limited to 12 candidates; use tournament for larger pools")
    calls = int(0 < problem.k < len(problem.page_ids))
    check_hardware_plan(args, calls)
    print(f"Candidates: {len(retrieved)} | Select: {args.k} | Layers: {args.layers} | Local iterations: {args.iterations}")
    if args.dry_run:
        print("Dry run: no IBM contact, circuit execution, or ledger writes; credentials are not required.")
        return
    factory = None
    if calls:
        config = load_ibm_config()
        print(f"IBM Quantum settings: {config.display_summary()}")
        factory = IBMDeviceFactory(config, confirm_submit=True, max_calls=calls,
                                   max_qubits=len(problem.page_ids))
    result = QAOASelector(
        QAOAConfig(layers=args.layers, shots=args.shots, iterations=args.iterations,
                   seed=args.seed, backend="pennylane"),
        device_factory=factory,
    ).select(problem)
    print(f"Backend: {result.metadata['backend']}\nScore: {result.objective:.4f}\nBitstring: {result.bitstring}")
    if result.metadata.get("fallback_used"):
        print("No valid QAOA samples; classical relevance fallback used. No automatic hardware retry.")
    print("\nSelected pages:")
    for index in result.selected_indices:
        print(f"- {retrieved[index].page.title} ({retrieved[index].page.path.name})")


def tournament_command(args: argparse.Namespace) -> None:
    comparing = args.command == "compare-tournament"
    names = ["topk", "mmr", "brute-force", "classical-qubo"] if comparing else [args.selector]
    if comparing and args.include_qaoa:
        names.append("qaoa")
    if comparing and args.include_ibm:
        names.append("ibm")
    validate_quantum_options(args)
    if args.candidates < 8:
        raise ValueError("tournament requires candidates >= 8")
    retrieved, problem = build_problem(args.query, args.candidates, 8)
    calls = tournament_group_calls(len(retrieved))
    print(f"Query: {args.query}\nCandidates: {len(retrieved)} | Primary: 5 | Recovery: 3 | Seed: {args.seed}")
    print(f"Planned solver calls per algorithm: {calls}")
    print(f"Algorithms: {', '.join(names)}")
    if "ibm" in names:
        check_hardware_plan(args, calls)
    else:
        print("Hardware workload: 0 calls (local algorithms only).")
    if args.dry_run:
        print("Dry run: no IBM contact, circuit execution, or ledger writes; credentials are not required.")
        return
    config = load_ibm_config() if "ibm" in names else None
    if config:
        print(f"IBM Quantum settings: {config.display_summary()}")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    results = []

    def page_label(index):
        page = retrieved[index].page
        return f"{page.title} ({page.path.name})"

    # Append and flush every event, retaining completed groups if a remote call fails.
    with output.open("a", encoding="utf-8") as ledger:
        def record(event):
            ledger.write(json.dumps(event) + "\n")
            ledger.flush()

        record({"type": "run_start", "query": args.query, "seed": args.seed,
                "algorithms": names, "shots": args.shots, "iterations": args.iterations,
                "layers": args.layers, "planned_group_calls": calls,
                "planned_hardware_calls": calls if "ibm" in names else 0,
                "relevance": problem.relevance.tolist(),
                "similarity_matrix": problem.similarity_matrix.tolist(),
                "pages": [{"id": item.page.id, "title": item.page.title,
                           "filename": item.page.path.name} for item in retrieved]})
        for name in names:
            print(f"\n=== {name} tournament ===")
            if name in {"qaoa", "ibm"}:
                selector = QAOASelector(
                    QAOAConfig(layers=args.layers, shots=args.shots, iterations=args.iterations,
                               seed=args.seed, backend="pennylane", use_warm_start=False),
                    device_factory=IBMDeviceFactory(config, confirm_submit=True, max_calls=calls, max_qubits=5)
                    if name == "ibm" else None,
                ).select
            else:
                selector = lambda subproblem, algorithm=name: run_selector(algorithm, subproblem)

            def on_event(event):
                record({"type": "group", "algorithm": name, **event})
                print(f"\n{event['phase']} round {event['round']}, group {event['group']}")
                if event["bye"]:
                    print(f"Bye (no solver call); advancing: {event['advance_bitstring']}")
                else:
                    print(f"Solver bitstring: {event['solver_bitstring']} | With random survivor: {event['advance_bitstring']}")
                    print(f"Group solver score: {event['solver_score']:.4f}")
                    if event["solver_metadata"].get("fallback_used"):
                        print("No valid QAOA samples; classical relevance fallback used.")
                for position, index in enumerate(event["candidate_indices"]):
                    status = "discarded"
                    if event["bye"]:
                        status = "bye"
                    elif index == event["random_survivor_index"]:
                        status = "random survivor"
                    elif index in event["solver_selected_indices"]:
                        status = "solver choice"
                    print(f"  bit {position}: {page_label(index)} -> {status}")

            started = perf_counter()
            try:
                result = select_tournament(problem, selector, seed=args.seed, on_event=on_event)
            except Exception as error:
                record({"type": "run_error", "algorithm": name, "error_type": type(error).__name__})
                raise
            elapsed = perf_counter() - started
            results.append((name, result, elapsed))
            summary = {key: value for key, value in result.metadata.items() if key != "events"}
            record({"type": "result", "algorithm": name, "bitstring": result.bitstring,
                    "selected_indices": result.selected_indices, "score": result.objective,
                    "seconds": elapsed, **summary})
            print(f"\nFinal bitstring (original candidate order): {result.bitstring}\nScore: {result.objective:.4f}")
            for label, key in (("Primary", "primary_indices"), ("Recovery", "recovery_indices")):
                print(f"{label} pages:")
                for index in result.metadata[key]:
                    print(f"  bit {index}: {page_label(index)}")
        print("\nAlgorithm          Final score    Seconds    Group calls")
        for name, result, elapsed in results:
            print(f"{name:<18} {result.objective:>11.4f} {elapsed:>10.2f} {result.metadata['group_calls']:>14}")
        print("Brute force and classical QUBO are exact within groups, not global tournament optima.")
        print("Same initial pool and seed; later groups depend on each algorithm's survivors. No quantum advantage claimed.")
        if comparing and "ibm" not in names:
            print("IBM: not run. Use --include-ibm --confirm-submit for the hardware comparison.")
        print(f"Full decision ledger: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational wiki context-selection laboratory")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command, handler in (("query", query_command), ("compare", compare_command)):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("query")
        subparser.add_argument("--selector", default="mmr", choices=("topk", "mmr", "brute-force", "classical-qubo", "qaoa"))
        subparser.add_argument("--candidates", type=int, default=6)
        subparser.add_argument("--k", type=int, default=3)
        subparser.set_defaults(handler=handler)
    debug = subparsers.add_parser("debug-circuit")
    debug.add_argument("--qubits", type=int, default=2)
    debug.set_defaults(handler=debug_command)
    ibm = subparsers.add_parser("run-ibm", help="submit a small QAOA job to IBM Quantum hardware")
    ibm.add_argument("query")
    ibm.add_argument("--candidates", type=int, default=4)
    ibm.add_argument("--k", type=int, default=2)
    ibm.add_argument("--layers", type=int, default=1)
    ibm.add_argument("--shots", type=int, default=128)
    ibm.add_argument("--iterations", type=int, default=3)
    ibm.add_argument("--seed", type=int, default=7)
    ibm.add_argument("--confirm-submit", action="store_true")
    ibm.add_argument("--dry-run", action="store_true", help="preview locally without credentials or IBM contact")
    ibm.add_argument("--max-hardware-calls", type=int, default=1, help="refuse plans exceeding this sampling-call budget")
    ibm.set_defaults(handler=run_ibm_command)
    for command in ("tournament", "compare-tournament"):
        tournament = subparsers.add_parser(command, help="five-page groups, five primary winners plus three recovery winners")
        tournament.add_argument("query")
        tournament.add_argument("--candidates", type=int, default=30)
        tournament.add_argument("--seed", type=int, default=7)
        tournament.add_argument("--layers", type=int, default=1)
        tournament.add_argument("--shots", type=int, default=128)
        tournament.add_argument("--iterations", type=int, default=3)
        tournament.add_argument("--output", default="experiments/tournaments/runs.jsonl")
        tournament.add_argument("--confirm-submit", action="store_true")
        tournament.add_argument("--dry-run", action="store_true", help="preview locally without credentials, execution, or ledger writes")
        tournament.add_argument("--max-hardware-calls", type=int, default=46, help="refuse plans exceeding this sampling-call budget")
        if command == "tournament":
            tournament.add_argument("--selector", default="mmr", choices=("topk", "mmr", "brute-force", "classical-qubo", "qaoa", "ibm"))
        else:
            tournament.add_argument("--include-qaoa", action="store_true", help="also run real local PennyLane circuits")
            tournament.add_argument("--include-ibm", action="store_true", help="also sample each group on IBM hardware")
        tournament.set_defaults(handler=tournament_command)
    args = parser.parse_args()
    try:
        args.handler(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
