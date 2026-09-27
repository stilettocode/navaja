"""Matched full-tournament study. Hardware is opt-in, capped, and never retried."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from time import perf_counter

import numpy as np

from scientific_evaluation import (ROOT, QUERIES, NEW_QUERIES, serialize, deserialize,
    distribution, sampled_metrics, build_problem, greedy_with_swaps, select_topk,
    select_mmr, select_brute_force, select_tournament, QAOAConfig, QAOASelector,
    IBMDeviceFactory, load_ibm_config, score_selection)
from quantum_wiki.selection.models import SelectionResult

OUT = ROOT / 'experiments/results/full-tournament-evaluation'
SEEDS = [7, 17, 27]
JOB_CAP = 46
JOB_SECONDS = 6


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2, default=str) + '\n', encoding='utf-8')
    temp.replace(path)


def config(seed=7):
    return QAOAConfig(iterations=3, shots=256, seed=seed, layers=1,
                      backend='pennylane', use_warm_start=False)


def summarize(problem, result, query, method, seed, seconds):
    ids = [problem.page_ids[i] for i in result.selected_indices]
    labels = NEW_QUERIES[query-6][1] if query >= 6 else []
    events = [e for e in result.metadata.get('events', []) if not e['bye']]
    return dict(query=query, method=method, seed=seed, seconds=seconds,
                objective=result.objective, ids=ids,
                coverage=len(set(ids) & set(labels))/len(labels) if labels else None,
                group_calls=len(events),
                fallback_count=sum(e['solver_metadata'].get('fallback_used', False) for e in events),
                shots=sum(e['solver_metadata'].get('shots', 0) for e in events),
                valid_shots=sum(e['solver_metadata'].get('valid_shots', 0) for e in events))


def local():
    if (OUT / 'hardware.json').exists():
        raise RuntimeError('Hardware ledger exists; preserve its frozen local protocol')
    queries = QUERIES + [q for q, _ in NEW_QUERIES]
    problems = [build_problem(q, 30, 8)[1] for q in queries]
    save('protocol.json', dict(utc=datetime.now(timezone.utc).isoformat(), queries=queries,
         problems=[serialize(p) for p in problems], seeds=SEEDS, hardware_query=6,
         hardware_seed=7, shots=256, iterations=3, warm_start=False,
         job_cap=JOB_CAP, max_execution_time=JOB_SECONDS, previous_pilot_seconds=6,
         maximum_requested_total_seconds=JOB_CAP*JOB_SECONDS+6,
         corpus_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted((ROOT/'wiki/sample').glob('*.md'))},
         stop_rule='Stop on any error; no automatic resume or resubmission',
         selection_rule='First newer query by position, fixed before new results'))
    rows = []
    for qi, problem in enumerate(problems):
        for method, solver in [('topk', select_topk), ('mmr', select_mmr),
                               ('greedy_swaps', lambda p: SelectionResult(
                                   (ix := greedy_with_swaps(p)), score_selection(p, ix)))]:
            times = []
            for _ in range(3):
                start = perf_counter(); result = solver(problem); times.append(perf_counter()-start)
            rows.append(summarize(problem, result, qi, method, None, float(np.median(times))))
        for seed in SEEDS:
            # Independent deterministic per-call sampling seeds, matching hardware's seed-7 run.
            for method in ['exact_tournament', 'qaoa_tournament', 'feasible_random_tournament']:
                calls = 0
                def solver(p):
                    nonlocal calls
                    calls += 1
                    if method == 'exact_tournament':
                        return select_brute_force(p)
                    if method == 'qaoa_tournament':
                        return QAOASelector(config(seed*1000+calls)).select(p)
                    from itertools import combinations
                    choices = list(combinations(range(len(p.page_ids)), p.k))
                    rng = np.random.default_rng(seed*1000+calls)
                    draws = rng.integers(len(choices), size=256)
                    best = max((list(choices[i]) for i in draws), key=lambda ix: score_selection(p, ix))
                    return SelectionResult(best, score_selection(p, best),
                                           dict(shots=256, valid_shots=256, fallback_used=False))
                start = perf_counter()
                result = select_tournament(problem, solver, seed=seed)
                rows.append(summarize(problem, result, qi, method, seed, perf_counter()-start))
                if qi == 6 and seed == 7:
                    save(method + '-matched.json', result.metadata)
        save('local.json', rows)
        print(f'Local query {qi+1}/12 complete', flush=True)


def reserve(state, shots, pub_count):
    if state['submission_attempts'] >= JOB_CAP or shots != 256 or pub_count != 1:
        raise RuntimeError('Hardware submission budget violation')
    if (state['submission_attempts']+1)*JOB_SECONDS + 6 > 300:
        raise RuntimeError('Five-minute total QPU ceiling exceeded')
    state['submission_attempts'] += 1


def hardware():
    import pennylane_qiskit.qiskit_device as bridge
    from qiskit_ibm_runtime import SamplerV2
    if (OUT/'hardware.json').exists():
        raise RuntimeError('Hardware ledger exists; refusing automatic resubmission')
    protocol = json.loads((OUT/'protocol.json').read_text())
    rows = json.loads((OUT/'local.json').read_text())
    if len(rows) != 144:
        raise RuntimeError('Complete local comparison required before hardware')
    problem = deserialize(protocol['problems'][6])
    state = dict(started_utc=datetime.now(timezone.utc).isoformat(), submission_attempts=0,
                 jobs=[], groups=[], events=[], status='running', job_cap=JOB_CAP,
                 max_execution_time_seconds=JOB_SECONDS)
    save('hardware.json', state)
    settings = load_ibm_config()
    factory = IBMDeviceFactory(settings, confirm_submit=True, max_calls=JOB_CAP, max_qubits=5)
    tracked = []

    class RecordedSampler(SamplerV2):
        def run(self, pubs, *, shots=None):
            reserve(state, shots, len(pubs))
            save('hardware.json', state)
            self.options.max_execution_time = JOB_SECONDS
            circuit = pubs[0]
            job = super().run(pubs, shots=shots)
            tracked.append(job)
            state['jobs'].append(dict(id=job.job_id(), backend=factory._backend.name,
                depth=circuit.depth(), operations=dict(circuit.count_ops()),
                layout=str(circuit.layout), options=str(self.options), shots=shots,
                submitted_utc=datetime.now(timezone.utc).isoformat()))
            save('hardware.json', state)
            print(f'Submitted group {len(tracked)}/46: {job.job_id()}', flush=True)
            return job

    def solver(p):
        start = perf_counter()
        result = QAOASelector(config(7000+len(state['groups'])+1), device_factory=factory).select(p)
        elapsed = perf_counter()-start
        ideal = distribution(p, result.metadata['gamma']+result.metadata['beta'])
        metrics = tracked[-1].metrics()
        usage = metrics['usage']['quantum_seconds']
        if not isinstance(usage, (float, int)) or usage < 0:
            raise RuntimeError('Missing trustworthy provider usage')
        state['jobs'][-1]['metrics'] = metrics
        state['jobs'][-1]['quantum_seconds'] = usage
        state['groups'].append(dict(problem=serialize(p), metadata=result.metadata,
            ideal=ideal.tolist(), metrics=sampled_metrics(p, result.metadata['counts'], ideal),
            selected_indices=result.selected_indices, objective=result.objective,
            exact_objective=select_brute_force(p).objective, wall_seconds=elapsed))
        state['quantum_seconds'] = sum(j['quantum_seconds'] for j in state['jobs'])
        save('hardware.json', state)
        print(f'Completed {len(state["groups"])}/46; QPU usage {state["quantum_seconds"]}s', flush=True)
        if usage > JOB_SECONDS or state['quantum_seconds']+6 > 300:
            raise RuntimeError('Provider usage exceeds requested ceiling; stopping')
        return result

    original = bridge.Sampler
    bridge.Sampler = RecordedSampler
    start = perf_counter()
    try:
        def event(e):
            state['events'].append(e)
            save('hardware.json', state)
        result = select_tournament(problem, solver, seed=7, on_event=event)
        state['summary'] = summarize(problem, result, 6, 'hardware_tournament', 7, perf_counter()-start)
        state['status'] = 'completed'
    except Exception as error:
        state['status'] = 'stopped_on_error'
        message = str(error).replace(settings.token, '<redacted>')
        if settings.instance:
            message = message.replace(settings.instance, '<instance>')
        state['error'] = dict(type=type(error).__name__, message=message[:1800])
        print(f'Stopped: {type(error).__name__}; no automatic retry', flush=True)
    finally:
        bridge.Sampler = original
        save('hardware.json', state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hardware', action='store_true')
    parser.add_argument('--confirm-submit', action='store_true')
    args = parser.parse_args()
    if args.hardware:
        if not args.confirm_submit:
            parser.error('--hardware requires --confirm-submit')
        hardware()
    else:
        local()
