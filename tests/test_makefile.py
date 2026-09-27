"""Execute the public Make interface offline; never confirm a real IBM run."""

from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MAKE = shutil.which("make")
pytestmark = pytest.mark.skipif(MAKE is None, reason="GNU Make is not installed")


def run_make(*arguments):
    return subprocess.run([MAKE, "--no-print-directory", *arguments], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("target,expected", [
    ("help", "Offline IBM previews"),
    ("demo", "Final bitstring"),
    ("tournament", "Final bitstring"),
    ("compare", "classical-qubo"),
    ("local-qaoa", "qaoa tournament"),
    ("compare-local", "qaoa tournament"),
    ("query", "Selected pages"),
    ("compare-small", "Gap"),
    ("debug", "probability="),
    ("plan", "46 sampling calls"),
    ("plan-ibm-single", "1 sampling calls"),
])
def test_documented_offline_targets(target, expected, tmp_path):
    result = run_make(target, f"PYTHON={sys.executable}", "ITERATIONS=1", "SHOTS=32",
                      f"OUTPUT={tmp_path / 'decisions with spaces.jsonl'}")
    assert result.returncode == 0, result.stdout + result.stderr
    assert expected in result.stdout


@pytest.mark.parametrize("target", ["run-ibm", "compare-ibm", "ibm-single"])
def test_hardware_make_targets_refuse_without_confirmation(target):
    result = run_make(target, f"PYTHON={sys.executable}")
    assert result.returncode != 0
    assert "Refusing to submit" in result.stdout + result.stderr


@pytest.mark.parametrize("target", ["run-ibm", "compare-ibm", "ibm-single"])
def test_hardware_targets_offer_offline_preview_even_when_confirmed(target):
    result = run_make(target, f"PYTHON={sys.executable}", "ARGS=--confirm-submit --dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Dry run: no IBM contact" in result.stdout


def test_default_help_and_install_test_recipes():
    result = run_make()
    assert result.returncode == 0 and "Setup:" in result.stdout
    # Show installation/test recipes without downloading packages or recursing into pytest.
    result = run_make("-n", "venv", "install", "install-ibm", "test", "TEST_ARGS=-q")
    assert result.returncode == 0
    assert 'pip install -e ".[dev,quantum]"' in result.stdout
    assert 'pip install -e ".[dev,quantum,ibm]"' in result.stdout
    assert "-m pytest -q" in result.stdout


def test_make_passes_query_and_options_with_spaces(tmp_path):
    result = run_make("tournament", f"PYTHON={sys.executable}", "SELECTOR=topk",
                      "QUERY=Explain graph paths and traversal", "CANDIDATES=10", "SEED=9",
                      f"OUTPUT={tmp_path / 'named ledger.jsonl'}")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Query: Explain graph paths and traversal" in result.stdout
    assert "Candidates: 10 | Primary: 5 | Recovery: 3 | Seed: 9" in result.stdout
    assert "=== topk tournament ===" in result.stdout
