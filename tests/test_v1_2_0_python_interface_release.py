from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    "docs/bhsm_v1_2_0_release_scope.md",
    "docs/bhsm_v1_2_0_python_quickstart.md",
    "docs/bhsm_v1_2_0_cli_command_table.md",
    "docs/bhsm_v1_2_0_prediction_claim_status.md",
    "docs/bhsm_v1_2_0_release_checklist.md",
    "RELEASE_NOTES_v1.2.0.md",
)
ARTIFACTS = (
    "artifacts/BHSM_v1_2_0_python_interface_release_manifest.json",
    "artifacts/BHSM_v1_2_0_cli_quickstart_index.json",
    "artifacts/BHSM_v1_2_0_prediction_registry_status.json",
    "artifacts/BHSM_v1_2_0_claim_status.json",
    "artifacts/BHSM_v1_2_0_release_checklist.json",
)
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def _cli(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT,
        text=True, capture_output=True, check=True, timeout=30,
    )
    return json.loads(result.stdout)


def test_release_files_exist_and_artifacts_parse() -> None:
    for path in DOCS:
        assert (ROOT / path).is_file()
    for path in ARTIFACTS:
        assert json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_release_manifest_is_offline_and_tag_collision_is_explicit() -> None:
    manifest = json.loads((ROOT / ARTIFACTS[0]).read_text())
    assert manifest["offline_safe"] is True
    for key in ("internet_required", "pdg_required", "wolfram_required", "feynrules_required", "madgraph_required"):
        assert manifest[key] is False
    assert manifest["tag_collision"] is True
    assert manifest["tag_ready"] is False


def test_registry_release_status_and_policies() -> None:
    status = json.loads((ROOT / ARTIFACTS[2]).read_text())
    assert status["entries_count"] == 11
    assert status["contains_W_boson"] and status["contains_electron_neutrino"]
    assert status["contains_CKM_PMNS_entries"]
    assert status["contains_open_theorem_blockers"]
    assert status["contains_runtime_disabled_gates"]
    claim = json.loads((ROOT / ARTIFACTS[3]).read_text())
    assert claim["empirical_validation_status"] == "not claimed"


def test_readme_preserves_v11_and_adds_guarded_v12_section() -> None:
    readme = (ROOT / "docs/archive/README_status_history_pre_v0_7.md").read_text()
    assert "## BHSM v1.1.0 HEP handoff status" in readme
    assert "## BHSM v1.2.0 Python computational interface" in readme
    assert "not counted as an independent prediction" in readme
    assert "upper-limit based by default" in readme
    assert "will not be moved or overwritten" in readme


def test_cli_semantics_remain_offline_and_guarded() -> None:
    registry = _cli("registry", "--format", "json")
    assert {"W_boson", "electron_neutrino"} <= {row["particle_key"] for row in registry["entries"]}
    w = _cli("predict", "--particle", "W_boson", "--mode", "calibration", "--format", "json")
    assert w["predictions"][0]["prediction_status"] == "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
    neutrino = _cli("predict", "--particle", "electron_neutrino", "--anchor", "W_boson", "--format", "json")
    assert neutrino["comparisons"][0]["reference"]["reference_kind"] == "upper_limit"
    assert neutrino["internet_required"] is False
    assert neutrino["pdg_dependency_required"] is False


def test_frozen_predictions_and_physics_sources_are_unchanged() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    changed_src = subprocess.run(
        ["git", "diff", "--name-only", "origin/main", "--", "src"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    changed = [line for line in changed_src.stdout.splitlines() if line]
    assert all(path.startswith("src/bhsm/interface/") for path in changed)
