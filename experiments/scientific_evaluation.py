"""Reproducible local study plus an explicitly guarded, at-most-three-job IBM pilot."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import random
from time import perf_counter

import numpy as np
import pennylane as qml

from benchmark_selection import QUERIES, greedy_with_swaps, split_tournament
from quantum_wiki.cli import ROOT, build_problem, load_ibm_config
from quantum_wiki.quantum.ibm import IBMDeviceFactory
from quantum_wiki.selection.brute_force import select_brute_force
from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.qaoa import QAOAConfig, QAOASelector
from quantum_wiki.selection.scoring import score_selection
from quantum_wiki.selection.topk import select_topk
from quantum_wiki.selection.mmr import select_mmr
from quantum_wiki.selection.tournament import select_tournament

OUT = ROOT / "experiments" / "results" / "scientific-evaluation"
NEW_QUERIES = [
    ("How can a monotonic stack find the next warmer day?", ["monotonic-stacks", "stacks-and-parsing"]),
    ("How do I find the largest k values using a heap?", ["heaps-and-top-k", "sorting-and-custom-ordering"]),
    ("How can union find detect redundant edges in an undirected graph?", ["union-find", "graph-representation-and-dfs"]),
    ("How do I reverse a linked list without losing nodes?", ["linked-lists"]),
    ("How does a trie help find dictionary words on a board?", ["tries-and-prefix-search", "backtracking", "grid-search-and-flood-fill"]),
    ("How do I binary search for the minimum feasible shipping capacity?", ["binary-search", "complexity-and-constraints"]),
]


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def serialize(problem):
    return {"page_ids": problem.page_ids, "relevance": problem.relevance.tolist(),
            "similarity_matrix": problem.similarity_matrix.tolist(),
            "token_counts": problem.token_counts.tolist(), "k": problem.k}


def deserialize(data):
    return SelectionProblem(data["page_ids"], np.array(data["relevance"]),
                            np.array(data["similarity_matrix"]), np.array(data["token_counts"]), k=data["k"])


def distribution(problem, parameters):
    energies = QAOASelector()._energy_table(problem)
    device = qml.device("default.qubit", wires=len(problem.page_ids))
    @qml.qnode(device)
    def circuit():
        for i in range(len(problem.page_ids)):
            qml.Hadamard(i)
        qml.DiagonalQubitUnitary(np.exp(-1j * parameters[0] * energies), wires=range(len(problem.page_ids)))
        for i in range(len(problem.page_ids)):
            qml.RX(2 * parameters[1], wires=i)
        return qml.probs(wires=range(len(problem.page_ids)))
    return np.asarray(circuit())


def distribution_metrics(problem, probabilities):
    size = len(problem.page_ids)
    scores = np.array([score_selection(problem, [i for i, bit in enumerate(f"{s:0{size}b}") if bit == "1"])
                       for s in range(2**size)])
    valid = np.array([s.bit_count() == problem.k for s in range(2**size)])
    optimum = max(scores[valid])
    optimal = valid & np.isclose(scores, optimum, atol=1e-10, rtol=0)
    mass = float(sum(probabilities[valid]))
    hit = float(sum(probabilities[optimal]))
    return {"valid_probability": mass, "optimal_probability": hit,
            "conditional_mean_score": float(probabilities[valid] @ scores[valid] / mass) if mass else None,
            "optimum": float(optimum), "optimal_states": int(sum(optimal)),
            "optimal_hit_chance_128": float(1-(1-hit)**128),
            "fallback_chance_128": float((1-mass)**128)}


def wilson(successes, total):
    z = 1.959963984540054
    p = successes / total
    center = (p + z*z/(2*total)) / (1 + z*z/total)
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / (1+z*z/total)
    return [center-radius, center+radius]


def sampled_metrics(problem, counts, ideal):
    total = sum(counts.values())
    probabilities = np.array([counts.get(f"{s:05b}", 0)/total for s in range(32)])
    metrics = distribution_metrics(problem, probabilities)
    valid_count = sum(n for b, n in counts.items() if b.count("1") == problem.k)
    optimal_count = round(metrics["optimal_probability"] * total)
    metrics.update({"shots": total, "valid_count": valid_count,
                    "valid_wilson_95": wilson(valid_count, total),
                    "optimal_count": optimal_count, "optimal_wilson_95": wilson(optimal_count, total),
                    "total_variation_from_ideal": float(.5*np.abs(probabilities-ideal).sum())})
    return metrics


def run_local():
    metadata = {"utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                "platform": platform.platform(), "versions": {p: importlib.metadata.version(p) for p in
                ["numpy", "pennylane", "pennylane-qiskit", "qiskit", "qiskit-ibm-runtime"]},
                "seeds": list(range(30)), "hardware_job_cap": 3, "hardware_shots_each": 256,
                "corpus_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted((ROOT / "wiki" / "sample").glob("*.md"))}}
    save("protocol.json", {**metadata, "queries": QUERIES + [q for q, _ in NEW_QUERIES],
                           "proxy_labels": dict(NEW_QUERIES), "group_selection": "first primary group for old queries 0 and 2; first recovery group for old query 0, exact tournament seed 7",
                           "iterations": [0, 3, 15, 40], "default_hardware_iterations": 3,
                           "stop_rule": "at most three jobs; stop on first hardware failure; never automatically resubmit"})
    rows, small, selected_ids = [], [], []
    queries = QUERIES + [q for q, _ in NEW_QUERIES]
    for qi, query in enumerate(queries):
        _, problem = build_problem(query, 30, 8)
        for name, solver in [("topk", select_topk), ("mmr", select_mmr),
                             ("greedy_swaps", lambda p: type("Result", (), {"selected_indices": greedy_with_swaps(p)})())]:
            times = []
            for _ in range(3):
                t = perf_counter(); result = solver(problem); times.append(perf_counter()-t)
            ids = [problem.page_ids[i] for i in result.selected_indices]
            rows.append({"query": qi, "method": name, "seed": None, "score": score_selection(problem, result.selected_indices),
                         "seconds": float(np.median(times)), "ids": ids})
        for seed in range(30):
            for primary in (4, 5, 6):
                t = perf_counter(); indices, calls = split_tournament(problem, primary, seed)
                rows.append({"query": qi, "method": f"split_{primary}_{8-primary}", "seed": seed,
                             "score": score_selection(problem, indices), "seconds": perf_counter()-t,
                             "calls": calls, "ids": [problem.page_ids[i] for i in indices]})
        # Exact global oracle on a *separate* smaller retrieved pool: C(12,8)=495.
        _, tiny = build_problem(query, 12, 8)
        optimum = select_brute_force(tiny).objective
        for name, indices in [("mmr", select_mmr(tiny).selected_indices), ("greedy_swaps", greedy_with_swaps(tiny))]:
            small.append({"query": qi, "method": name, "seed": None, "gap": optimum-score_selection(tiny, indices)})
        for seed in range(30):
            result = select_tournament(tiny, select_brute_force, seed=seed)
            small.append({"query": qi, "method": "split_5_3", "seed": seed, "gap": optimum-result.objective})
        print(f"Local query {qi+1}/{len(queries)} complete", flush=True)
    save("classical.json", {"rows": rows, "small_oracle": small})

    groups = []
    for qi, phase in [(0, "primary"), (2, "primary"), (0, "recovery")]:
        _, original = build_problem(queries[qi], 30, 8)
        result = select_tournament(original, select_brute_force, seed=7)
        event = next(e for e in result.metadata["events"] if e["phase"] == phase and not e["bye"])
        group = event["candidate_indices"]
        relevance = original.relevance[group].copy()
        if phase == "recovery":
            relevance -= original.similarity_matrix[np.ix_(group, result.metadata["primary_indices"])].sum(axis=1)
        problem = SelectionProblem([original.page_ids[i] for i in group], relevance,
            original.similarity_matrix[np.ix_(group, group)], original.token_counts[group], k=3)
        record = {"label": f"query{qi}_{phase}", "problem": serialize(problem), "training": []}
        for iterations in (0, 3, 15, 40):
            config = QAOAConfig(iterations=iterations, shots=256, seed=7, layers=1, backend="pennylane", use_warm_start=False)
            t = perf_counter(); result = QAOASelector(config).select(problem); elapsed = perf_counter()-t
            parameters = result.metadata["gamma"] + result.metadata["beta"]
            ideal = distribution(problem, parameters)
            record["training"].append({"iterations": iterations, "seconds": elapsed, "parameters": parameters,
                                       "ideal": ideal.tolist(), "metrics": distribution_metrics(problem, ideal),
                                       "counts": result.metadata["counts"], "best_score": result.objective})
        record["uniform_baseline"] = distribution_metrics(problem, np.full(32, 1/32))
        record["uniform_valid_baseline"] = distribution_metrics(problem, np.array([.1 if i.bit_count()==3 else 0 for i in range(32)]))
        ideal = np.array(record["training"][1]["ideal"])
        # Same shot budget baseline; distribution noise floor is a simulation, not hardware repetition.
        rng = np.random.default_rng(20260927)
        samples = rng.multinomial(256, ideal, size=2000) / 256
        record["ideal_sampling_tv_95_interval"] = np.quantile(.5*np.abs(samples-ideal).sum(axis=1), [.025,.975]).tolist()
        groups.append(record)
    save("quantum-local.json", groups)
    print("Local study saved; hardware jobs submitted: 0", flush=True)


def run_hardware():
    import pennylane_qiskit.qiskit_device as bridge
    from qiskit_ibm_runtime import SamplerV2
    groups = json.loads((OUT / "quantum-local.json").read_text())
    path = OUT / "hardware.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if previous.get("submission_attempts", 0):
            raise RuntimeError("A prior submission attempt exists; refusing automatic resubmission. Inspect hardware.json.")
    state = {"started_utc": datetime.now(timezone.utc).isoformat(), "submission_attempts": 0,
             "job_cap": 3, "shots_each": 256, "jobs": [], "results": []}
    save("hardware.json", state)
    config = load_ibm_config()
    factory = IBMDeviceFactory(config, confirm_submit=True, max_calls=3, max_qubits=5)

    class RecordedSampler(SamplerV2):
        def run(self, pubs, *, shots=None):
            if state["submission_attempts"] >= 3 or shots != 256 or len(pubs) != 1:
                raise RuntimeError("Pilot budget violation")
            state["submission_attempts"] += 1
            state["pending_label"] = groups[len(state["results"])]["label"]
            save("hardware.json", state)
            self.options.max_execution_time = 60
            job = super().run(pubs, shots=shots)
            circuit = pubs[0]
            row = {"id": job.job_id(), "backend": factory._backend.name,
                   "depth": circuit.depth(), "operations": dict(circuit.count_ops()),
                   "physical_qubits": circuit.num_qubits, "shots": shots, "max_execution_time_seconds": 60}
            state["jobs"].append(row); save("hardware.json", state)
            print(f"Submitted pilot job {len(state['jobs'])}/3: {row['id']} on {row['backend']}", flush=True)
            tracked_jobs.append(job)
            return job

    tracked_jobs = []
    original_sampler = bridge.Sampler
    bridge.Sampler = RecordedSampler
    try:
        for record in groups:
            problem = deserialize(record["problem"])
            t = perf_counter()
            result = QAOASelector(QAOAConfig(iterations=3, shots=256, seed=7, layers=1,
                backend="pennylane", use_warm_start=False), device_factory=factory).select(problem)
            local = next(x for x in record["training"] if x["iterations"] == 3)
            assert np.allclose(result.metadata["gamma"] + result.metadata["beta"], local["parameters"], atol=1e-12, rtol=0)
            row = {"label": record["label"], "wall_seconds": perf_counter()-t,
                   "score": result.objective, "metadata": result.metadata,
                   "metrics": sampled_metrics(problem, result.metadata["counts"], np.array(local["ideal"]))}
            state["results"].append(row); save("hardware.json", state)
            try:
                state["jobs"][-1]["metrics"] = tracked_jobs[-1].metrics()
                state["jobs"][-1]["usage"] = tracked_jobs[-1].usage()
            except Exception as error:
                state["jobs"][-1]["usage_error_type"] = type(error).__name__
            save("hardware.json", state)
            print(f"Completed {record['label']}: valid={row['metrics']['valid_probability']:.3f}, TV={row['metrics']['total_variation_from_ideal']:.3f}", flush=True)
        state["status"] = "completed"
    except Exception as error:
        message = str(error).replace(config.token, "<redacted>")
        if config.instance:
            message = message.replace(config.instance, "<instance>")
        state["status"] = "stopped_on_error"
        state["error"] = {"type": type(error).__name__, "message": message[:1800]}
        print(f"Hardware pilot stopped: {type(error).__name__}. Details recorded safely; no automatic retry.", flush=True)
    finally:
        bridge.Sampler = original_sampler
        save("hardware.json", state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true")
    parser.add_argument("--confirm-submit", action="store_true")
    args = parser.parse_args()
    if args.hardware:
        if not args.confirm_submit:
            parser.error("--hardware requires --confirm-submit; capped at three jobs of 256 shots")
        run_hardware()
    else:
        run_local()
