from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import buoyancy_gate_v10_2 as gate


ROOT = Path(__file__).resolve().parents[1]


def test_completion_gate_is_a_current_action_no_go():
    payload = gate.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["primary_verdict"] == "BHSM_CURRENT_PARENT_ACTION_CANNOT_GENERATE_TOPOLOGICAL_BUOYANCY"
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["measured_values_used"] is False
    assert payload["action"]["new_terms"] == []
    assert payload["action"]["new_continuous_parameters"] == []


def test_canonical_gate_advances_without_release_or_buoyancy_claim():
    payload = gate.canonical_completion_gate_payload()
    assert payload["version"] == "v10.2"
    assert payload["topological_buoyancy_derived"] is False
    assert payload["current_action_exhausted_for_buoyancy"] is True
    assert payload["new_terms_in_v10_2"] == []
    assert payload["new_continuous_parameters_in_v10_2"] == []
    assert payload["BHSM_1_0_release_complete"] is False


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
    assert json.loads(first["BHSM_1_0_completion_gate.json"])["version"] == "v10.2"


def test_five_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    for command in (
        "normal-radion-status", "global-constraint-status", "topological-buoyancy-status",
        "local-backreaction-status", "buoyancy-weak-field-status",
    ):
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        markdown_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["primary_verdict"] == gate.PRIMARY_VERDICT
        assert gate.PRIMARY_VERDICT in markdown_run.stdout
        assert "Proxy R promoted to physical depth: `false`" in markdown_run.stdout


def test_checked_in_artifacts_match_current_implementation():
    for key, filename in gate.ARTIFACT_FILES.items():
        expected = gate.deterministic_json(gate.artifact_payloads()[key])
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == expected
