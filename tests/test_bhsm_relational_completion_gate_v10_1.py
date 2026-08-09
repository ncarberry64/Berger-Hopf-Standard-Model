from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import relational_completion_gate as gate
from bhsm.interface.envelopment.relational_axioms import doctrine_sha256
from bhsm.interface.master_action import CURRENT_MISSING_OBJECT, CURRENT_VERDICT, CURRENT_VERSION
from bhsm.interface.aether_nonlinear_norman_cycle_bvp_v15_7 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT


ROOT = Path(__file__).resolve().parents[1]


def test_completion_gate_is_conditional_and_fail_closed():
    payload = gate.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["primary_verdict"] == "BHSM_RELATIONAL_ENVELOPMENT_PARENT_ACTION_CONSTRAINTS_CONSTRUCTED_CONDITIONALLY"
    assert payload["action_limit_verdict"] == "BHSM_CURRENT_PARENT_ACTION_DOES_NOT_DERIVE_ALL_RELATIONAL_ENVELOPMENT_AXIOMS"
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["new_elementary_particles"] == []
    assert payload["new_gravity_mediator"] is False
    assert payload["fundamental_dissipation_introduced"] is False


def test_current_master_api_advances_while_historical_gate_stays_v101():
    assert CURRENT_VERSION == "v15.7"
    assert CURRENT_VERDICT == PRIMARY_VERDICT
    assert CURRENT_MISSING_OBJECT == EXACT_NEXT_OBJECT
    canonical = gate.canonical_completion_gate_payload()
    assert canonical["version"] == "v10.1"
    assert canonical["author_doctrine_integrated"] is True
    assert canonical["author_doctrine_promoted_to_physical_theorem"] is False
    assert canonical["new_terms_in_v10_1"] == []
    assert canonical["new_continuous_parameters_in_v10_1"] == []
    assert canonical["BHSM_1_0_release_complete"] is False


def test_six_artifacts_are_deterministic_and_doctrine_hash_is_recorded():
    first = {key: gate.deterministic_json(value).encode("utf-8") for key, value in gate.artifact_payloads().items()}
    second = {key: gate.deterministic_json(value).encode("utf-8") for key, value in gate.artifact_payloads().items()}
    assert first == second
    assert len(first) == 6
    assert hashlib.sha256(first["doctrine"]).hexdigest() == doctrine_sha256()
    assert gate.artifact_payloads()["constraints"]["canonical_doctrine_sha256"] == doctrine_sha256()


def test_materializer_is_idempotent(tmp_path: Path):
    first_paths = gate.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = gate.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert json.loads(first["BHSM_1_0_completion_gate.json"])["version"] == "v10.1"


def test_current_v101_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    for command in (
        "relational-envelopment-status", "global-conservation-status", "boundary-complementarity-status",
        "neutrino-identity-status", "relational-constraint-status",
    ):
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        md_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["author_axiom_promoted_to_theorem"] is False
        assert gate.PRIMARY_VERDICT in md_run.stdout


def test_historical_v101_topological_payload_remains_available_directly():
    payload = gate.command_payload("topological-buoyancy-status")
    assert payload["version"] == "v10.1"
    assert payload["primary_verdict"] == gate.PRIMARY_VERDICT


def test_checked_in_artifacts_match_implementation():
    for key, filename in gate.ARTIFACT_FILES.items():
        expected = gate.deterministic_json(gate.artifact_payloads()[key])
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == expected
