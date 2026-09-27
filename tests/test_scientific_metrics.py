"""Analytical controls for the research metrics; no hardware calls."""
import importlib
from pathlib import Path

import numpy as np
import pytest

from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.scoring import score_selection


@pytest.fixture
def study(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "experiments"))
    return importlib.import_module("scientific_evaluation")


def problem():
    return SelectionProblem(list("abcde"), np.array([1., .8, .6, .2, .1]), np.zeros((5,5)), np.ones(5), k=3)


def test_uniform_controls_and_hit_probability(study):
    result=study.distribution_metrics(problem(), np.full(32, 1/32))
    assert result["valid_probability"] == 10/32
    assert result["optimal_probability"] == 1/32
    assert result["optimal_states"] == 1
    assert result["optimal_hit_chance_128"] == pytest.approx(1-(31/32)**128)
    valid=study.distribution_metrics(problem(), np.array([.1 if i.bit_count()==3 else 0 for i in range(32)]))
    assert valid["valid_probability"] == pytest.approx(1)
    assert valid["optimal_probability"] == .1


def test_histogram_metrics_preserve_bit_order_and_invalid_mass(study):
    # abc is the unique optimum; the invalid all-zero shot must stay in the denominator.
    result=study.sampled_metrics(problem(), {"11100": 9, "00000": 1}, np.full(32, 1/32))
    assert result["valid_count"] == result["optimal_count"] == 9
    assert result["valid_probability"] == .9
    assert result["conditional_mean_score"] == pytest.approx(score_selection(problem(), [0,1,2]))
    assert 0 <= result["valid_wilson_95"][0] < .9 < result["valid_wilson_95"][1] <= 1


def test_no_feasible_samples_remain_distinct_from_a_classical_fallback(study):
    result=study.sampled_metrics(problem(), {"00000": 256}, np.full(32, 1/32))
    assert result["valid_count"] == result["optimal_count"] == 0
    assert result["conditional_mean_score"] is None


def test_zero_angle_distribution_is_uniform(study):
    np.testing.assert_allclose(study.distribution(problem(), [0.,0.]), np.full(32, 1/32), atol=1e-12)
