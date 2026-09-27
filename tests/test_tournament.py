import json

import numpy as np
import pytest

from quantum_wiki import cli
from quantum_wiki.selection.brute_force import select_brute_force
from quantum_wiki.selection.models import SelectionProblem, SelectionResult
from quantum_wiki.selection.scoring import score_selection
from quantum_wiki.selection.tournament import select_tournament, tournament_group_calls
from quantum_wiki.wiki.loader import load_markdown_pages


def problem_of_size(size):
    rng = np.random.default_rng(12)
    vectors = rng.random((size, 4))
    return SelectionProblem([str(i) for i in range(size)], rng.random(size),
                            vectors @ vectors.T, np.ones(size), k=8)


@pytest.mark.parametrize("size", range(8, 36))
def test_every_page_accounted_for_and_exact_targets(size):
    problem = problem_of_size(size)
    result = select_tournament(problem, select_brute_force)
    metadata = result.metadata
    assert metadata["group_calls"] == tournament_group_calls(size)
    primary = set(metadata["primary_indices"])
    recovery = set(metadata["recovery_indices"])
    discarded = set(metadata["discarded_indices"])
    assert len(primary) == 5 and len(recovery) == 3
    assert not primary & recovery
    assert not set(result.selected_indices) & discarded
    assert primary | recovery | discarded == set(range(size))
    assert len(metadata["recovery_pool_indices"]) == size - 5
    assert set(metadata["recovery_pool_indices"]) == recovery | discarded
    assert result.objective == score_selection(problem, result.selected_indices)
    assert result.bitstring.count("1") == 8
    for phase, initial, target in (("primary", set(range(size)), 5),
                                   ("recovery", recovery | discarded, 3)):
        pool = initial
        phase_events = [e for e in metadata["events"] if e["phase"] == phase]
        rounds = sorted({e["round"] for e in phase_events})
        for round_number in rounds:
            events = [e for e in phase_events if e["round"] == round_number]
            candidates = [i for e in events for i in e["candidate_indices"]]
            assert len(candidates) == len(set(candidates))
            assert set(candidates) == pool
            advanced = set()
            eliminated = set()
            for event in events:
                group = event["candidate_indices"]
                assert 1 <= len(group) <= 5
                advanced.update(event["advanced_indices"])
                eliminated.update(event["discarded_indices"])
                if not event["bye"]:
                    chosen = event["solver_selected_indices"]
                    survivor = event["random_survivor_index"]
                    assert survivor not in chosen
                    assert set(chosen + [survivor]) == set(event["advanced_indices"])
                    assert event["solver_bitstring"].count("1") == event["solver_k"]
                    assert event["advance_bitstring"].count("1") == len(chosen) + 1
                    assert [group[i] for i, bit in enumerate(event["solver_bitstring"]) if bit == "1"] == sorted(chosen, key=group.index)
            assert not advanced & eliminated
            assert advanced | eliminated == pool
            assert target <= len(advanced) < len(pool)
            pool = advanced
        assert len(pool) == target


def test_seed_reproduces_decisions_and_can_change_them():
    problem = problem_of_size(30)
    first = select_tournament(problem, select_brute_force, seed=7)
    second = select_tournament(problem, select_brute_force, seed=7)
    third = select_tournament(problem, select_brute_force, seed=8)
    strip_timing = lambda result: [{k: v for k, v in e.items() if k != "seconds"}
                                   for e in result.metadata["events"]]
    assert strip_timing(first) == strip_timing(second)
    assert strip_timing(first) != strip_timing(third)
    assert first.metadata["group_calls"] == 46


def test_recovery_scores_are_marginal_to_primary_winners():
    problem = problem_of_size(12)
    subproblems = []

    def recording_selector(subproblem):
        subproblems.append(subproblem)
        return select_brute_force(subproblem)

    result = select_tournament(problem, recording_selector)
    anchors = result.metadata["primary_indices"]
    events = [e for e in result.metadata["events"] if not e["bye"]]
    for event, subproblem in zip(events, subproblems, strict=True):
        if event["phase"] == "recovery":
            group = event["candidate_indices"]
            expected = problem.relevance[group] - problem.similarity_matrix[np.ix_(group, anchors)].sum(axis=1)
            np.testing.assert_allclose(subproblem.relevance, expected)
            local = list(range(subproblem.k))
            global_indices = [group[i] for i in local]
            assert score_selection(subproblem, local) == pytest.approx(
                score_selection(problem, anchors + global_indices) - score_selection(problem, anchors))


def test_invalid_group_result_fails_instead_of_losing_pages():
    with pytest.raises(ValueError, match="valid exact-k"):
        select_tournament(problem_of_size(10), lambda problem: SelectionResult([0, 0, 0], 0))


def test_wrong_final_target_is_rejected():
    problem = problem_of_size(10)
    problem.k = 5
    with pytest.raises(ValueError, match="k=8"):
        select_tournament(problem, select_brute_force)


def test_corpus_has_thirty_substantial_unique_pages():
    pages = load_markdown_pages(cli.SAMPLE_WIKI)
    assert len(pages) == 30
    assert len({page.id for page in pages}) == 30
    assert all(len(page.content.split()) >= 280 for page in pages)


def test_comparison_cli_logs_decisions_and_titles(monkeypatch, tmp_path, capsys):
    output = tmp_path / "decisions.jsonl"
    monkeypatch.setattr("sys.argv", ["quantum-wiki", "compare-tournament", "graph shortest paths",
                                    "--candidates", "10", "--output", str(output)])
    cli.main()
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    results = [row for row in rows if row["type"] == "result"]
    assert {row["algorithm"] for row in results} == {"topk", "mmr", "brute-force", "classical-qubo"}
    assert all(row["bitstring"].count("1") == 8 for row in results)
    text = capsys.readouterr().out
    assert "Solver bitstring:" in text and ".md)" in text
    assert "IBM: not run" in text


@pytest.mark.parametrize("arguments", [["tournament", "--selector", "ibm"],
                                       ["compare-tournament", "--include-ibm"]])
def test_hardware_tournament_requires_explicit_confirmation(monkeypatch, arguments):
    def forbidden():
        pytest.fail("must reject before accessing IBM configuration")
    monkeypatch.setattr(cli.IBMQuantumConfig, "from_environment", forbidden)
    monkeypatch.setattr("sys.argv", ["quantum-wiki", arguments[0], "graph", *arguments[1:]])
    with pytest.raises(SystemExit, match="confirm-submit"):
        cli.main()


def test_authorized_hardware_tournament_uses_remote_factory_without_network(monkeypatch, tmp_path):
    devices = []
    monkeypatch.setattr(cli.IBMQuantumConfig, "from_environment",
                        lambda: cli.IBMQuantumConfig("test-only"))
    def fake_factory(config, *, confirm_submit, max_calls, max_qubits):
        assert confirm_submit and max_calls == 6 and max_qubits == 5
        return lambda qubits, shots: devices.append((qubits, shots))
    monkeypatch.setattr(cli, "IBMDeviceFactory", fake_factory)

    class FakeQAOA:
        def __init__(self, config, device_factory):
            assert config.backend == "pennylane" and not config.use_warm_start
            self.config, self.factory = config, device_factory

        def select(self, problem):
            self.factory(len(problem.page_ids), self.config.shots)
            return select_brute_force(problem)

    monkeypatch.setattr(cli, "QAOASelector", FakeQAOA)
    monkeypatch.setattr("sys.argv", ["quantum-wiki", "tournament", "graph", "--selector", "ibm",
                                    "--confirm-submit", "--candidates", "10",
                                    "--output", str(tmp_path / "hardware.jsonl")])
    cli.main()
    assert len(devices) == 6
    assert all(qubits <= 5 and shots == 128 for qubits, shots in devices)
