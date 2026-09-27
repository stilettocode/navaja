import numpy as np

from quantum_wiki.selection.brute_force import select_brute_force
from quantum_wiki.selection.classical_qubo import problem_to_qubo
from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.scoring import score_selection
from quantum_wiki.selection.qaoa import QAOAConfig, QAOASelector


def make_problem() -> SelectionProblem:
    return SelectionProblem(
        ["a", "b", "c"],
        np.array([0.9, 0.8, 0.2]),
        np.array([[0, 0.9, 0.0], [0.9, 0, 0.0], [0.0, 0.0, 0]]),
        np.array([10, 10, 10]),
        k=2,
    )


def test_redundancy_changes_optimum():
    result = select_brute_force(make_problem())
    assert result.selected_indices == [0, 2]
    assert result.objective == score_selection(make_problem(), [0, 2])


def test_qubo_matches_negative_score_for_valid_bitstrings():
    problem = make_problem()
    qubo = problem_to_qubo(problem)
    for bits in ([1, 1, 0], [1, 0, 1], [0, 1, 1]):
        selected = [index for index, bit in enumerate(bits) if bit]
        assert np.isclose(qubo.evaluate(bits), -score_selection(problem, selected))


def test_pennylane_qaoa_returns_a_valid_exact_k_result():
    result = QAOASelector(QAOAConfig(layers=1, shots=32, iterations=2, seed=3, backend="pennylane")).select(make_problem())
    assert len(result.selected_indices) == make_problem().k
    assert result.metadata["backend"] == "PennyLane default.qubit"
    assert len(result.metadata["gamma"]) == 1
    assert len(result.metadata["beta"]) == 1
    assert sum(result.metadata["counts"].values()) == 32
    assert result.metadata["valid_shots"] == sum(n for bits, n in result.metadata["counts"].items() if bits.count("1") == 2)
    assert all(len(bits) == 3 and set(bits) <= {"0", "1"} for bits in result.metadata["counts"])


def test_seeded_qaoa_without_warm_starts_does_not_read_or_write_shared_state(tmp_path):
    path = tmp_path / "parameters.json"
    config = QAOAConfig(shots=32, iterations=1, backend="pennylane", seed=9,
                        use_warm_start=False, warm_start_path=str(path))
    first = QAOASelector(config).select(make_problem())
    second = QAOASelector(config).select(make_problem())
    assert first.selected_indices == second.selected_indices
    assert first.metadata["gamma"] == second.metadata["gamma"]
    assert not first.metadata["warm_start_used"]
    assert not path.exists()
