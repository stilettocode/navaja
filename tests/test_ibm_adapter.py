import pytest

from quantum_wiki.quantum.ibm import IBMQuantumConfig


def test_ibm_configuration_requires_a_token(monkeypatch):
    monkeypatch.delenv("IBM_QUANTUM_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="IBM_QUANTUM_TOKEN"):
        IBMQuantumConfig.from_environment()


def test_ibm_configuration_reads_non_secret_settings(monkeypatch):
    monkeypatch.setenv("IBM_QUANTUM_TOKEN", "test-token")
    monkeypatch.setenv("IBM_QUANTUM_INSTANCE", "test-instance")
    monkeypatch.setenv("IBM_QUANTUM_BACKEND", "test-backend")
    config = IBMQuantumConfig.from_environment()
    assert config.instance == "test-instance"
    assert config.backend_name == "test-backend"


def test_ibm_summary_does_not_expose_token():
    config = IBMQuantumConfig(token="secret-token", instance="instance", backend_name="backend")
    summary = config.display_summary()
    assert "secret-token" not in summary
    assert "token=<configured>" in summary