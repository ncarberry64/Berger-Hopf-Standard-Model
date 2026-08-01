from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface.envelopment import final_completion_gate_v10_4 as gate


ROOT = Path(__file__).resolve().parents[1]


def test_completion_gate_preserves_no_go_and_records_author_extension():
    payload = gate.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["primary_verdict"] == "BHSM_MULTIPLE_INEQUIVALENT_SUPPORT_ACTIONS_REMAIN_AFTER_AUTHOR_EXTENSION_SELECTION"
    assert payload["depth_verdict"] == "BHSM_PROPER_VOLUME_DEFICIT_HAS_NO_INDEPENDENT_PHYSICAL_SCALAR_AFTER_CONSTRAINT_REDUCTION"
    assert payload["physical_BHSM_complete"] is False
    assert payload["empirical_replacement_complete"] is False
    assert payload["physical_outputs"] == {"depth": None, "interference_energy": None, "masses": None, "CKM": None, "PMNS": None}
    assert payload["new_geometric_fields_adopted"] == [
        "upsilon (author-selected extension class; action normalization open)"
    ]
    assert payload["new_continuous_parameters_adopted"] == []
    assert payload["completion_marks"]["Mark_I_Foundation"] == "REACHED"
    assert payload["completion_marks"]["Mark_II_Conditional_architecture"] == "REACHED_CONDITIONALLY"
    assert payload["completion_marks"]["Mark_III_Physical_derivation"] == "NOT_REACHED"
    assert payload["completion_marks"]["Mark_IV_Empirical_replacement"] == "NOT_REACHED"


def test_artifacts_and_materializer_are_deterministic(tmp_path: Path):
    first = {key: gate.deterministic_json(value).encode() for key, value in gate.artifact_payloads().items()}
    second = {key: gate.deterministic_json(value).encode() for key, value in gate.artifact_payloads().items()}
    assert first == second
    assert {key: hashlib.sha256(value).hexdigest() for key, value in first.items()} == {
        key: hashlib.sha256(value).hexdigest() for key, value in second.items()
    }
    first_paths = gate.materialize(tmp_path)
    first_bytes = {path.name: path.read_bytes() for path in first_paths}
    second_paths = gate.materialize(tmp_path)
    assert first_bytes == {path.name: path.read_bytes() for path in second_paths}
    assert json.loads(first_bytes["BHSM_1_0_completion_gate.json"])["version"] == "v10.4"


def test_seven_current_cli_commands_render_json_and_markdown():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    for command in gate.COMMAND_SECTIONS:
        base = [sys.executable, "-m", "bhsm.interface", command]
        json_run = subprocess.run(base + ["--format", "json"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        markdown_run = subprocess.run(base + ["--format", "markdown"], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
        assert json.loads(json_run.stdout)["primary_verdict"] == gate.PRIMARY_VERDICT
        assert gate.PRIMARY_VERDICT in markdown_run.stdout


def test_checked_in_artifacts_match_implementation():
    for key, filename in gate.ARTIFACT_FILES.items():
        expected = gate.deterministic_json(gate.artifact_payloads()[key])
        assert (ROOT / "artifacts" / filename).read_text(encoding="utf-8") == expected
