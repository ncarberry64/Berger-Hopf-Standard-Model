from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def _run_example(path: str) -> tuple[str, dict[str, object]]:
    completed = subprocess.run(
        [sys.executable, path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    start = completed.stdout.find("{")
    assert start >= 0
    return completed.stdout, json.loads(completed.stdout[start:])


def test_w_and_neutrino_example_runs_offline_with_required_warnings() -> None:
    output, payload = _run_example("examples/bhsm_solve_w_and_neutrino.py")
    assert "W is used as calibration anchor, not independent prediction." in output
    assert "Electron-neutrino comparison is against upper limit" in output
    assert payload["w_boson_result"]["prediction_status"] == (
        "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
    )
    assert payload["comparison_metadata"]["electron_neutrino"]["reference"][
        "reference_kind"
    ] == "upper_limit"
    assert payload["interface_status"] == "DEMONSTRATION_ONLY_NOT_EMPIRICAL_VALIDATION"


def test_custom_scan_runs_without_validation_claim() -> None:
    _output, payload = _run_example("examples/bhsm_custom_geometry_scan.py")
    assert payload["status"] == "CUSTOM_INTERFACE_SCAN_NOT_BHSM_VALIDATION"
    assert len(payload["rows"]) == 3


def test_interface_artifacts_and_docs_are_guarded() -> None:
    required = [
        "artifacts/BHSM_python_interface_manifest_v0_1.json",
        "artifacts/BHSM_python_interface_validation_policy_v0_1.json",
        "artifacts/BHSM_python_interface_example_results_v0_1.json",
        "docs/python_interface.md",
        "docs/python_interface_quickstart.md",
        "docs/python_interface_validation_policy.md",
    ]
    for relative in required:
        assert ROOT.joinpath(relative).is_file()
    manifest = json.loads(ROOT.joinpath(required[0]).read_text(encoding="utf-8"))
    assert manifest["claim_boundaries"]["empirical_validation_claimed"] is False
    combined = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8") for path in required)
    for forbidden in (
        "BHSM proves the Standard Model",
        "BHSM has replaced the Standard Model",
        "BHSM fully derives the Standard Model",
        "official CERN integration achieved",
        "FeynRules/UFO/MadGraph validated",
    ):
        assert forbidden not in combined


def test_frozen_prediction_files_are_byte_identical() -> None:
    for relative, expected in FROZEN_HASHES.items():
        digest = hashlib.sha256(ROOT.joinpath(relative).read_bytes()).hexdigest()
        assert digest == expected
