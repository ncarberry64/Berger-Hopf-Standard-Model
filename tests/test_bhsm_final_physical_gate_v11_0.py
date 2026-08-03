from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import final_physical_gate_v11_0 as gate


ROOT = Path(__file__).resolve().parents[1]


def test_completion_gate_advances_only_the_exact_support_results():
    payload = gate.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["support_composition"]["validation_passed"] is True
    assert payload["support_constraint_analysis"]["physical_support_pairs"] == 1
    assert payload["supported_parent_action"]["support_weights_fixed"] is False
    assert payload["physical_BHSM_complete"] is False
    assert payload["physical_outputs"] == {
        "masses": None,
        "CKM": None,
        "PMNS": None,
        "transition_amplitudes": None,
    }
    assert payload["completion_marks"] == {
        "Mark_I_Canonical_ontology": "REACHED",
        "Mark_II_Complete_conditional_architecture": "NOT_REACHED",
        "Mark_III_Physical_derivation": "NOT_REACHED",
        "Mark_IV_Empirical_replacement": "NOT_REACHED",
    }


def test_materialization_is_byte_deterministic(tmp_path: Path):
    first_paths = gate.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    first_hashes = {name: hashlib.sha256(value).hexdigest() for name, value in first.items()}
    second_paths = gate.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert first_hashes == {name: hashlib.sha256(value).hexdigest() for name, value in second.items()}
    assert json.loads(second["BHSM_1_0_completion_gate.json"])["version"] == "v11.0"


def test_all_v11_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    for command in gate.COMMAND_SECTIONS:
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        markdown_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["primary_verdict"] == gate.PRIMARY_VERDICT
        assert gate.PRIMARY_VERDICT in markdown_run.stdout


def test_checked_in_artifacts_match_implementation():
    expected = gate.artifact_payloads()
    for key, filename in gate.ARTIFACT_FILES.items():
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == gate.deterministic_json(expected[key])
    canonical = ROOT / "artifacts" / "BHSM_1_0_completion_gate.json"
    from bhsm.interface.completion import completion_gate_v11_5 as current

    assert canonical.read_text(encoding="utf-8") == gate.deterministic_json(current.canonical_completion_gate_payload())
