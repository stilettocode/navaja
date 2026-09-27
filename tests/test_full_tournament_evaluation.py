"""Offline checks for the separately authorized tournament hardware budget."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def study(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'experiments'))
    return importlib.import_module('full_tournament_evaluation')


def test_all_calls_fit_budget_and_extra_call_is_blocked(study):
    state = {'submission_attempts': 0}
    for _ in range(46):
        study.reserve(state, 256, 1)
    assert state['submission_attempts'] * study.JOB_SECONDS + 6 <= 300
    with pytest.raises(RuntimeError):
        study.reserve(state, 256, 1)
    assert state['submission_attempts'] == 46


@pytest.mark.parametrize('shots,pubs', [(512, 1), (256, 2), (256, 0)])
def test_unexpected_workload_blocked_without_reserving(study, shots, pubs):
    state = {'submission_attempts': 0}
    with pytest.raises(RuntimeError):
        study.reserve(state, shots, pubs)
    assert state['submission_attempts'] == 0


def test_existing_ledger_blocks_network_even_if_incomplete(study, monkeypatch, tmp_path):
    monkeypatch.setattr(study, 'OUT', tmp_path)
    (tmp_path/'hardware.json').write_text('{}')
    monkeypatch.setattr(study, 'load_ibm_config', lambda: pytest.fail('Must not connect'))
    with pytest.raises(RuntimeError, match='refusing automatic resubmission'):
        study.hardware()
