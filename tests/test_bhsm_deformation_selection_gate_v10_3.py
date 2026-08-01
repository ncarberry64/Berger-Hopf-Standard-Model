from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import deformation_selection_gate_v10_3 as gate


ROOT = Path(__file__).resolve().parents[1]


def test_common_mode_equivalence_fails_closed_before_nonuniqueness():
    payload = gate.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["primary_verdict"] == (
        "BHSM_COMMON_ENVELOPMENT_MODE_EQUIVALENCE_BLOCKED_BY_UNDERIVED_CROSS_DOMAIN_HESSIAN"
    )
    assert payload["minimality"]["fully_admissible_candidates"] == []
    assert payload["minimality"]["buoyancy_physical_scalar_count"] == 0
    assert payload["new_fields_adopted"] == []
    assert payload["new_continuous_parameters"] == []
    assert payload["equivalence_status"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["seam_fold_hopf_physically_inequivalent"] is False


def test_v102_no_go_and_claim_firewall_are_preserved():
    payload = gate.completion_payload()
    assert payload["v10_2_no_go_preserved"] is True
    assert payload["topological_buoyancy_claimed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["measured_inputs_used"] is False
    assert payload["physical_mass_or_matrix_emitted"] is False


def test_artifacts_are_deterministic_and_canonical_gate_advances():
    first = {key: gate.deterministic_json(value).encode() for key, value in gate.artifact_payloads().items()}
    second = {key: gate.deterministic_json(value).encode() for key, value in gate.artifact_payloads().items()}
    assert first == second
    assert {key: hashlib.sha256(value).hexdigest() for key, value in first.items()} == {
        key: hashlib.sha256(value).hexdigest() for key, value in second.items()
    }
    canonical = gate.canonical_completion_gate_payload()
    assert canonical["version"] == "v10.3"
    assert canonical["buoyancy_physical_scalar_count"] == 0
    assert canonical["BHSM_1_0_release_complete"] is False


def test_materializer_is_idempotent(tmp_path: Path):
    first_paths = gate.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = gate.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert json.loads(first["BHSM_1_0_completion_gate.json"])["version"] == "v10.3"


def test_nine_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    commands = (
        "deformation-domain-status", "embedding-constraint-status", "local-radion-status",
        "common-stress-pullback-status", "global-zero-mode-status", "deformation-selection-status",
        "common-envelopment-mode-status", "deformation-intertwiner-status",
        "coupled-deformation-rank-status",
    )
    for command in commands:
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        markdown_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["primary_verdict"] == gate.PRIMARY_VERDICT
        assert gate.PRIMARY_VERDICT in markdown_run.stdout


def test_checked_in_artifacts_match_implementation():
    for key, filename in gate.ARTIFACT_FILES.items():
        expected = gate.deterministic_json(gate.artifact_payloads()[key])
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == expected
