from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT,
        text=True, capture_output=True, check=check, timeout=30,
    )


def test_cli_registry_and_status_json() -> None:
    registry = json.loads(_run("registry", "--format", "json").stdout)
    assert any(row["particle_key"] == "W_boson" for row in registry["entries"])
    w = json.loads(_run("status", "W_boson", "--format", "json").stdout)
    neutrino = json.loads(_run("status", "electron_neutrino", "--format", "json").stdout)
    assert w["can_be_calibration_anchor"] is True
    assert neutrino["comparison_kind"] == "upper_limit"


def test_cli_predict_and_report_json() -> None:
    w = json.loads(_run("predict", "--particle", "W_boson", "--mode", "calibration", "--format", "json").stdout)
    assert w["predictions"][0]["prediction_status"] == "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
    neutrino = json.loads(_run("predict", "--particle", "electron_neutrino", "--anchor", "W_boson", "--format", "json").stdout)
    assert neutrino["comparisons"][0]["reference"]["reference_kind"] == "upper_limit"
    report = json.loads(_run("report", "--anchor", "W_boson", "--particles", "W_boson,electron_neutrino", "--include-open-theorem", "--format", "json").stdout)
    assert report["internet_required"] is False
    assert report["pdg_dependency_required"] is False


def test_cli_help_and_unknown_status() -> None:
    for args in (("--help",), ("registry", "--help"), ("predict", "--help"), ("report", "--help")):
        assert _run(*args).returncode == 0
    unknown = _run("status", "not_registered", "--format", "json", check=False)
    assert unknown.returncode != 0
    assert json.loads(unknown.stdout)["status"] == "UNKNOWN_OR_UNREGISTERED"


def test_cli_manifest_is_offline_and_runtime_independent() -> None:
    manifest = json.loads((ROOT / "artifacts/BHSM_cli_manifest_v0_1.json").read_text())
    assert manifest["offline_safe"] is True
    for key in ("requires_pdg", "requires_internet", "requires_wolfram", "requires_feynrules", "requires_madgraph"):
        assert manifest[key] is False
