import sys
from types import SimpleNamespace

import numpy as np
import pytest

from quantum_wiki import cli
from quantum_wiki.quantum.ibm import IBMDeviceFactory, IBMQuantumConfig, create_ibm_device
from quantum_wiki.selection.models import SelectionProblem
from quantum_wiki.selection.qaoa import QAOAConfig, QAOASelector


def small_problem(k=2):
    return SelectionProblem(["a", "b", "c"], np.array([.9, .7, .1]),
                            np.zeros((3, 3)), np.ones(3), k=k)


@pytest.fixture
def forbid_ibm(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("this command must not access IBM configuration or devices")
    monkeypatch.setattr(cli.IBMQuantumConfig, "from_environment", forbidden)
    monkeypatch.setattr(cli, "IBMDeviceFactory", forbidden)
    monkeypatch.setattr(cli, "load_dotenv", forbidden)


@pytest.mark.parametrize("command", [
    ["query", "graph", "--candidates", "4", "--k", "2"],
    ["compare", "graph", "--candidates", "4", "--k", "2"],
    ["debug-circuit", "--qubits", "2"],
    ["tournament", "graph", "--candidates", "8"],
    ["tournament", "graph", "--selector", "qaoa", "--candidates", "8", "--iterations", "0"],
    ["compare-tournament", "graph", "--candidates", "8", "--include-qaoa", "--iterations", "0"],
])
def test_local_commands_never_access_ibm(command, forbid_ibm, monkeypatch, tmp_path):
    if "tournament" in command[0]:
        command = command + ["--output", str(tmp_path / "local.jsonl")]
    monkeypatch.setattr(sys, "argv", ["quantum-wiki", *command])
    cli.main()


@pytest.mark.parametrize("command,calls", [
    (["run-ibm", "graph"], 1),
    (["tournament", "graph", "--selector", "ibm"], 46),
    (["compare-tournament", "graph", "--include-ibm"], 46),
])
def test_dry_run_never_configures_or_executes_any_solver(command, calls, forbid_ibm, monkeypatch, tmp_path, capsys):
    output = tmp_path / "must-not-exist.jsonl"
    if "tournament" in command[0]:
        command = command + ["--output", str(output)]
    monkeypatch.setattr(cli, "QAOASelector", lambda *a, **k: pytest.fail("dry run must not optimize"))
    monkeypatch.setattr(sys, "argv", ["quantum-wiki", *command, "--dry-run", "--confirm-submit"])
    cli.main()
    assert f"{calls} sampling calls" in capsys.readouterr().out
    assert not output.exists()


@pytest.mark.parametrize("command", [
    ["run-ibm", "graph"],
    ["tournament", "graph", "--selector", "ibm"],
    ["compare-tournament", "graph", "--include-ibm"],
])
def test_every_hardware_entrypoint_refuses_without_confirmation(command, forbid_ibm, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["quantum-wiki", *command])
    with pytest.raises(SystemExit, match="confirm-submit"):
        cli.main()


@pytest.mark.parametrize("command", [
    ["run-ibm", "graph", "--shots", "0"],
    ["run-ibm", "graph", "--iterations", "-1"],
    ["run-ibm", "graph", "--seed", "-1"],
    ["run-ibm", "graph", "--layers", "0"],
    ["run-ibm", "graph", "--candidates", "13"],
    ["run-ibm", "graph", "--max-hardware-calls", "0"],
    ["tournament", "graph", "--selector", "ibm", "--max-hardware-calls", "45"],
    ["compare-tournament", "graph", "--include-ibm", "--candidates", "7"],
])
def test_invalid_or_overbudget_runs_fail_before_ibm(command, forbid_ibm, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["quantum-wiki", *command, "--confirm-submit"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2


@pytest.mark.parametrize("k", [0, 3])
def test_forced_selections_skip_both_optimization_and_hardware(k, forbid_ibm, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["quantum-wiki", "run-ibm", "graph", "--candidates", "3", "--k", str(k)])
    cli.main()
    assert "classical forced selection" in capsys.readouterr().out
    selector = QAOASelector(device_factory=lambda *a: pytest.fail("forced choice needs no circuit"))
    assert selector.select(small_problem(k)).metadata["sampling_calls"] == 0


def test_adapter_requires_confirmation_before_environment_or_imports(monkeypatch):
    monkeypatch.setattr(IBMQuantumConfig, "from_environment", lambda: pytest.fail("no config access"))
    with pytest.raises(ValueError, match="confirm_submit"):
        create_ibm_device(3, 128)
    with pytest.raises(ValueError, match="confirm_submit"):
        IBMDeviceFactory(IBMQuantumConfig("test"))


def test_adapter_reuses_backend_and_enforces_call_budget(monkeypatch):
    calls = []
    backend = SimpleNamespace(num_qubits=7, name="fake")

    class Service:
        def __init__(self, **kwargs):
            calls.append("connect")

        def least_busy(self, **kwargs):
            assert kwargs == {"operational": True, "simulator": False, "min_num_qubits": 5}
            calls.append("lookup")
            return backend

    def device(name, **kwargs):
        assert name == "qiskit.remote" and kwargs["backend"] is backend
        calls.append("device")
        return object()

    monkeypatch.setitem(sys.modules, "qiskit_ibm_runtime", SimpleNamespace(QiskitRuntimeService=Service))
    monkeypatch.setitem(sys.modules, "pennylane", SimpleNamespace(device=device))
    factory = IBMDeviceFactory(IBMQuantumConfig("test"), confirm_submit=True, max_calls=2)
    assert calls == []
    factory(5, 128)
    factory(4, 128)
    with pytest.raises(RuntimeError, match="budget exhausted"):
        factory(5, 128)
    assert calls == ["connect", "lookup", "device", "device"]


def test_remote_optimizer_hook_is_disabled():
    with pytest.raises(ValueError, match="optimization must stay local"):
        QAOASelector(optimization_device_factory=lambda *a: pytest.fail("must not call"))


@pytest.mark.parametrize("iterations", [0, 3, 8])
def test_only_one_final_sampling_execution_regardless_of_training_iterations(iterations, monkeypatch):
    import pennylane as qml

    device = qml.device("default.qubit", wires=3, seed=4)
    execute = device.execute
    executions = []
    factories = []

    def tracked_execute(circuits, *args, **kwargs):
        executions.extend(circuits)
        return execute(circuits, *args, **kwargs)

    def factory(qubits, shots):
        factories.append((qubits, shots))
        return device

    monkeypatch.setattr(device, "execute", tracked_execute)
    result = QAOASelector(QAOAConfig(iterations=iterations, shots=32, backend="pennylane",
                                    use_warm_start=False), device_factory=factory).select(small_problem())
    assert factories == [(3, 32)]
    assert len(executions) == 1 and executions[0].shots.total_shots == 32
    assert result.metadata["optimization_backend"] == "PennyLane default.qubit"


def test_local_optimization_failure_never_creates_remote_device(monkeypatch):
    selector = QAOASelector(QAOAConfig(backend="pennylane", use_warm_start=False),
                            device_factory=lambda *a: pytest.fail("local failure must prevent hardware"))
    def fail(problem):
        raise RuntimeError("local failure")
    monkeypatch.setattr(selector, "_energy_table", fail)
    with pytest.raises(RuntimeError, match="local failure"):
        selector.select(small_problem())


def test_remote_import_failure_is_not_silently_replaced_by_surrogate(monkeypatch):
    selector = QAOASelector(QAOAConfig(backend="auto"), device_factory=lambda *a: None)
    def fail(problem):
        raise ImportError("missing provider bridge")
    monkeypatch.setattr(selector, "_select_pennylane", fail)
    with pytest.raises(ImportError, match="missing provider bridge"):
        selector.select(small_problem())
