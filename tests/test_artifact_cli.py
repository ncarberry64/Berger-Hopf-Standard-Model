import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=60).stdout


def test_artifact_cli_json_commands_work_offline():
    sources = json.loads(run("artifact-sources", "--format", "json"))
    formulas = json.loads(run("formula-registry", "--format", "json"))
    predictions = json.loads(run("artifact-predictions", "--format", "json"))
    report = json.loads(run("artifact-report", "--anchor", "W_boson", "--format", "json"))
    assert sources["internet_required"] is False
    assert formulas["available_artifact_backed"]
    assert predictions["empirical_derivation_inputs_used"] is False
    assert report["internet_required"] is False


def test_compute_artifact_commands_and_markdown_report():
    for key in ("CKM_matrix_BHSM", "PMNS_matrix_BHSM", "cp_holonomy_phase_attachment", "boundary_constants", "mass_ratios"):
        assert json.loads(run("compute-artifact", key))["source_status"] == "DISCOVERED"
    assert "BHSM Artifact-Backed Prediction Report" in run("artifact-report", "--format", "markdown")
