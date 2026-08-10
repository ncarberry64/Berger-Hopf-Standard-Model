from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import completion_gate as gate
from bhsm.interface.master_action import (
    CURRENT_MISSING_OBJECT,
    CURRENT_VERDICT,
    CURRENT_VERSION,
    unified_envelopment_status_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_four_completion_marks_are_exact_and_fail_closed():
    marks = gate.completion_marks()
    assert list(marks) == [
        "Mark_I_foundational_completion",
        "Mark_II_conditional_architecture_completion",
        "Mark_III_physical_derivation_completion",
        "Mark_IV_empirical_replacement",
    ]
    assert marks["Mark_I_foundational_completion"]["status"] == "REACHED"
    assert marks["Mark_II_conditional_architecture_completion"]["status"] == "REACHED_CONDITIONALLY"
    assert marks["Mark_III_physical_derivation_completion"]["status"] == "OPEN"
    assert marks["Mark_IV_empirical_replacement"]["status"] == "OPEN"


def test_primary_status_has_no_mass_or_matrix_promotion():
    payload = gate.completion_status()
    assert payload["primary_verdict"] == gate.PRIMARY_VERDICT
    assert payload["validation_passed"] is True
    assert payload["physical_mass_emitted"] is False
    assert payload["physical_CKM_emitted"] is False
    assert payload["physical_PMNS_emitted"] is False
    assert payload["new_continuous_parameters"] == []
    assert payload["new_elementary_fermions"] == []
    assert payload["new_mediators"] == []
    canonical = gate.canonical_completion_gate_payload()
    assert canonical["new_dynamical_field_introduced"] is True
    assert canonical["physical_particle_derivation_complete"] is False


def test_v10_master_action_api_remains_available_below_current_campaign():
    assert CURRENT_VERSION == "v15.9"
    assert CURRENT_VERDICT != gate.PRIMARY_VERDICT
    assert CURRENT_MISSING_OBJECT != gate.NEXT_EXACT_OBJECT
    assert unified_envelopment_status_payload()["primary_verdict"] == gate.PRIMARY_VERDICT


def test_canonical_gate_extends_v91_without_claiming_release():
    payload = gate.canonical_completion_gate_payload()
    assert payload["version"] == "v10.0"
    assert payload["action_extension_introduced"] is True
    assert payload["action_extension_classification"] == "STRUCTURAL_POSTULATE"
    assert payload["BHSM_1_0_release_complete"] is False
    assert payload["physical_matrix_promoted"] is False


def test_artifact_payloads_are_deterministic():
    first = {key: gate.deterministic_json(value).encode("utf-8") for key, value in gate.artifact_payloads().items()}
    second = {key: gate.deterministic_json(value).encode("utf-8") for key, value in gate.artifact_payloads().items()}
    assert first == second
    assert {key: hashlib.sha256(value).hexdigest() for key, value in first.items()} == {
        key: hashlib.sha256(value).hexdigest() for key, value in second.items()
    }


def test_materializer_is_idempotent(tmp_path: Path):
    first_paths = gate.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = gate.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert json.loads(first["BHSM_1_0_completion_gate.json"])["version"] == "v10.0"


def test_all_five_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    commands = (
        "unified-envelopment-status",
        "dynamic-envelope-status",
        "completion-marks-status",
        "global-scale-status",
        "particle-orbit-status",
    )
    for command in commands:
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        markdown_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["primary_verdict"] == gate.PRIMARY_VERDICT
        assert gate.PRIMARY_VERDICT in markdown_run.stdout
        assert "Physical matrix emitted: `false`" in markdown_run.stdout


def test_checked_in_artifacts_match_current_implementation():
    for key, filename in gate.ARTIFACT_FILES.items():
        expected = gate.deterministic_json(gate.artifact_payloads()[key])
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == expected
    canonical = json.loads((ROOT / "artifacts" / "BHSM_1_0_completion_gate.json").read_text(encoding="utf-8"))
    assert canonical["version"] == "v11.6"
    assert canonical["spectral_charged_current_kernel_action_derived"] is False
