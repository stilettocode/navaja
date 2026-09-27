import numpy as np

from quantum_wiki.selection.warm_start import load_parameters, save_parameters


def test_warm_start_round_trip(tmp_path):
    path = tmp_path / "parameters.json"
    parameters = np.array([0.2, 0.4])
    save_parameters(path, candidate_count=4, k=2, layers=1, parameters=parameters, objective=1.5)
    loaded = load_parameters(path, candidate_count=4, k=2, layers=1)
    assert np.allclose(loaded, parameters)


def test_warm_start_rejects_incompatible_shape(tmp_path):
    path = tmp_path / "parameters.json"
    save_parameters(path, candidate_count=4, k=2, layers=1, parameters=np.array([0.2, 0.4]), objective=1.5)
    assert load_parameters(path, candidate_count=6, k=2, layers=1) is None