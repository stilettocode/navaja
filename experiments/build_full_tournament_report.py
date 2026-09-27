"""Build the full-tournament report from saved data; never contacts IBM."""
import json
import csv
from statistics import mean, median
from zipfile import ZipFile, ZIP_DEFLATED

from full_tournament_evaluation import OUT, ROOT


def main():
    rows = json.loads((OUT/'local.json').read_text())
    hw = json.loads((OUT/'hardware.json').read_text()) if (OUT/'hardware.json').exists() else {}
    lines = ['# Full tournament comparison', '',
        'This follow-up compares final eight-page selections from 30 candidates. '
        'The local study uses the same twelve synthetic queries, with tournament seeds 7, 17, and 27. '
        'QAOA uses one layer, three local training iterations, 256 measurements per group, and no warm starts. '
        'Each group has an independent deterministic simulation sampling seed. Production defaults are unchanged.', '',
        '## Local results', '',
        '| Method | Mean objective | New-query label coverage | Median selection time |',
        '| --- | ---: | ---: | ---: |']
    for method in dict.fromkeys(r['method'] for r in rows):
        group = [r for r in rows if r['method'] == method]
        coverage = mean(r['coverage'] for r in group if r['coverage'] is not None)
        lines.append(f"| {method} | {mean(r['objective'] for r in group):.6f} | {coverage:.1%} | {median(r['seconds'] for r in group)*1000:.3f} ms |")
    lines += ['', 'Direct baselines have twelve observations each; tournament methods have 36 runs '
        'nested within twelve queries. Coverage averages the six newer queries and their seeds. '
        'Timing excludes retrieval, imports, and result-file writes. QAOA timing includes local training and sampling. '
        'The feasible-random baseline samples 256 valid subsets per group and keeps the highest-scoring draw. '
        'Its implementation scores repeated draws, so its timing is not an optimized random-sampling speed claim.', '',
        'The exact tournament and feasible-random tournament have the same final scores in these runs. '
        'Simulated QAOA has nearly the same average score and the same aggregate label coverage, with much longer selection time. '
        'The earlier objective/usefulness mismatch remains: greedy plus swaps scores best but recovers fewer labelled relevant pages.', '',
        '## Matched hardware tournament', '',
        'The hardware query was fixed before new outcomes: **How can a monotonic stack find the next warmer day?** '
        'It is the first newer query by position; the grouping/survivor seed is 7. Relevant proxy labels are '
        '`monotonic-stacks` and `stacks-and-parsing`. Hardware outcomes drive later groups and recovery conditioning; '
        'this is an adaptive full tournament, not a replay of classical winners.', '',
        f"Hardware status: **{hw.get('status', 'not started')}**. Completed groups: {len(hw.get('groups', []))}/46. "
        f"Provider-reported QPU usage: **{hw.get('quantum_seconds', 0)} seconds**.", '',
        'The separate budget permits 46 submissions with a six-QPU-second execution ceiling each '
        '(276 seconds maximum requested, or 282 including the previous pilot). '
        'A durable ledger prevents automatic resubmission; the run stops on any error. '
        'No sessions are used. [IBM documents the limit as QPU usage](https://quantum.cloud.ibm.com/docs/en/guides/max-execution-time).', '',
        '| Method, same query and seed | Objective | Label coverage | Selection time |',
        '| --- | ---: | ---: | ---: |']
    matched = [r for r in rows if r['query']==6 and r['seed'] in (None, 7)]
    if 'summary' in hw:
        matched.append(hw['summary'])
    for r in matched:
        lines.append(f"| {r['method']} | {r['objective']:.6f} | {r['coverage']:.1%} | {r['seconds']:.6f} s |")
    if hw.get('error'):
        lines += ['', f"Stopped with `{hw['error']['type']}`; inspect the local ledger for details. No full hardware result is claimed."]
    if hw.get('groups'):
        groups = hw['groups']
        shots = sum(g['metrics']['shots'] for g in groups)
        valid = sum(g['metrics']['valid_count'] for g in groups)
        optimal = sum(g['metrics']['optimal_count'] for g in groups)
        exact = sum(abs(g['objective']-g['exact_objective']) < 1e-10 for g in groups)
        fallback = sum(g['metadata']['fallback_used'] for g in groups)
        lines += ['', f'Across completed hardware groups: **{valid}/{shots} valid shots ({valid/shots:.1%})**, '
            f'**{optimal}/{shots} optimum shots ({optimal/shots:.1%})**, '
            f'**{exact}/{len(groups)} group selections reached the exact local score**, and **{fallback} fallbacks**.', '',
            'These group statistics include different problems and exact-K targets; they are descriptive totals, '
            'not independent repeats of one circuit. Each saved group includes its numeric problem, trained angles, '
            'ideal distribution, raw counts, and exact local score.']
        zeros = sum(j.get('quantum_seconds') == 0 for j in hw['jobs'])
        lines += ['', f'IBM returned zero `quantum_seconds` for {zeros} completed jobs. '
                  'The usage total preserves provider values; zero is not interpreted as physically free execution. '
                  'The submission guard reserves six seconds for every attempted job regardless of reported usage.']
    if hw.get('summary'):
        hardware_row = hw['summary']
        exact_row = next(r for r in matched if r['method']=='exact_tournament')
        lines += ['', f"Hardware minus exact-tournament objective: **{hardware_row['objective']-exact_row['objective']:+.6f}**. "
            f"The final sets share **{len(set(hardware_row['ids']) & set(exact_row['ids']))}/8 articles**. "
            f"Hardware total elapsed time was **{hardware_row['seconds']/60:.2f} minutes**. "
            'Elapsed time includes local training, network/provider waits, and incremental ledger writes.']
        lines += ['', '**Final hardware articles:**', ''] + ['- '+i for i in hw['summary']['ids']]
    interpretation = ROOT/'experiments/full_tournament_interpretation.md'
    if hw.get('status') == 'completed':
        lines += ['', interpretation.read_text(encoding='utf-8').strip(), '']
    else:
        lines += ['', '## Interpretation pending', '',
                  'The full interpretation applies to the completed study. No completed hardware result is claimed.', '']
    lines += [
        '## Data and reproduction', '',
        '- [Raw data](../experiments/results/full-tournament-evaluation/): `protocol.json`, `local.json`, '
        '`hardware.json`, and the matched local event logs. This directory is ignored by Git.',
        '- [Experiment source](../experiments/full_tournament_evaluation.py).',
        '- [Offline report builder](../experiments/build_full_tournament_report.py) and '
        '[interpretation source](../experiments/full_tournament_interpretation.md).',
        '- [Portable results archive](../experiments/results/full-tournament-evaluation-data.zip), including CSV tables.', '',
        'Rebuild this report without QPU use:', '', '```powershell',
        '.venv/Scripts/python.exe experiments/build_full_tournament_report.py', '```', '',
        'Offline regression suite: **105 tests passed** after adding budget and resubmission guards. '
        'The initial sandboxed test attempts hit Windows temporary-directory permissions; the unrestricted offline run passed.', '']
    (ROOT/'docs/17-full-tournament-evaluation-report.md').write_text('\n'.join(lines), encoding='utf-8')
    with (OUT/'comparison.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows + ([hw['summary']] if 'summary' in hw else []))
    if hw.get('status') in ('completed', 'stopped_on_error'):
        with ZipFile(OUT.parent/'full-tournament-evaluation-data.zip', 'w', ZIP_DEFLATED) as archive:
            files = list(OUT.glob('*.json')) + list(OUT.glob('*.csv'))
            files += [ROOT/'docs/17-full-tournament-evaluation-report.md',
                      ROOT/'experiments/full_tournament_evaluation.py',
                      ROOT/'experiments/build_full_tournament_report.py',
                      interpretation,
                      ROOT/'experiments/scientific_evaluation.py',
                      ROOT/'experiments/benchmark_selection.py', ROOT/'pyproject.toml']
            files += list((ROOT/'src').rglob('*.py')) + list((ROOT/'wiki/sample').glob('*.md'))
            for path in files:
                archive.write(path, path.relative_to(ROOT))


if __name__ == '__main__':
    main()
