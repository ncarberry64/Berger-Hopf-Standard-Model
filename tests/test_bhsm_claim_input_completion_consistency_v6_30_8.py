from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import claim_input_completion_consistency as audit


def test_version_source_and_primary_verdict_are_pinned():
    assert audit.VERSION == "v6.30.8"
    assert audit.SOURCE_MAIN_SHA == "258cb9ce8dd0a14b2d3ddacd28baddbd73db6f82"
    assert audit.PRIMARY_VERDICT == "BHSM_SCALAR_QUARTIC_PARAMETERIZED_NOT_PREDICTED"


def test_every_retained_claim_has_traceable_evidence():
    assert audit.claim_rows()
    for row in audit.claim_rows():
        if row["retained"]:
            assert row["evidence"], row["claim_id"]
            assert row["locations"], row["claim_id"]
            assert "lambda5_dependency" in row


def test_typed_inputs_are_exclusive_and_honest():
    rows = audit.typed_input_rows()
    assert rows
    assert all(row["type"] in audit.INPUT_TYPES for row in rows)
    assert all(not (row["derived"] and row["calibrated"]) for row in rows)
    assert all(not row["allowed_in_parent_action"] for row in rows if row["type"] == "EXTERNAL_COMPARISON_DATA")
    assert all(not row["advertised_as_prediction"] for row in rows if row["type"] == "INDEPENDENT_THEORY_INPUT")
    assert {row["input_id"]: row["type"] for row in rows}["lambda5"] == "INDEPENDENT_THEORY_INPUT"


def test_candidate_branch_is_never_official():
    rows = audit.frozen_dependency_rows(ROOT)
    dressed = [row for row in rows if "DRESSED" in row["branch"]]
    assert dressed
    assert all(row["official_status"] == "CANDIDATE_NOT_OFFICIAL" for row in dressed)


def test_every_frozen_output_has_complete_path_and_no_lambda_dependency():
    rows = audit.frozen_dependency_rows(ROOT)
    typed = {row["input_id"] for row in audit.typed_input_rows()}
    source = json.loads((ROOT / "theory" / "bhsm_v1_frozen_prediction_set.json").read_text(encoding="utf-8"))
    expected = sum(
        len(audit._leaf_paths(value, category))
        for item in source["prediction_sets"]
        for category, value in item["outputs"].items()
    )
    assert len(rows) == expected
    for row in rows:
        assert row["exact_computation_path"]
        assert row["direct_inputs"]
        assert row["fitted_inputs"] == []
        assert row["comparison_data_in_computation"] == []
        assert set(row["direct_inputs"] + row["transitive_inputs"] + row["candidate_inputs"]) <= typed
        assert row["unselected_inputs"] == []
        assert row["excluded_unselected_inputs"] == ["lambda5"]
        assert row["lambda5_appears"] is False
        assert row["G5_appears"] is False
        assert row["Z5_appears"] is False
        assert row["kappa1_appears"] is False
        assert row["output_can_vary_with_lambda5"] is False


def test_lambda5_is_narrowed_not_selected_or_predicted():
    payload = audit.lambda_relevance_payload()
    assert payload["classification"] == "INDEPENDENT_THEORY_INPUT"
    assert payload["value_selected"] is False
    assert payload["sign_selected"] is False
    assert payload["appears_in_frozen_predictions"] is False
    assert payload["secondary_verdict"] == "BHSM_LAMBDA5_RECLASSIFIED_AS_PARAMETER_FREE_EXTENSION_BLOCKER"


def test_rebuilt_dag_has_no_stale_release_blocker_and_rb02_is_narrowed():
    rows = {row["blocker_id"]: row for row in audit.blocker_rows()}
    assert len(rows) == 16
    assert rows["RB-02"]["classification"] == "PARAMETER_FREE_EXTENSION_BLOCKER"
    assert rows["RB-02"]["release_blocking"] is False
    assert all(row["affected_retained_claims"] for row in rows.values())
    assert not any(row["stale_as_release_blocker"] for row in rows.values())
    release_ids = audit.blocker_dag_payload()["release_blocker_ids"]
    assert "RB-02" not in release_ids
    assert len(release_ids) == 15


def test_scale_permission_remains_denied_for_actual_dependencies():
    payload = audit.scale_reassessment_payload()
    assert payload["verdict"] == "BHSM_SCALE_PHASE_STILL_BLOCKED_INDEPENDENTLY_OF_LAMBDA5"
    assert payload["lambda5_is_scale_permission_dependency"] is False
    assert payload["scale_phase_permission"] == "DENIED"
    assert {"RB-01", "RB-09", "RB-12", "RB-13"} <= set(payload["actual_open_dependencies"])


def test_next_target_is_highest_upstream_parent_action():
    assert audit.next_target_payload()["target"] == "RB-01_UNIFIED_PARENT_ACTION_PROVENANCE"
    rb01 = {row["blocker_id"]: row for row in audit.blocker_rows()}["RB-01"]
    assert rb01["depends_on"] == []


def test_completion_gate_tracks_current_v8_0_tier_status():
    payload = audit.canonical_completion_gate_payload()
    assert payload["version"] == "v8.0"
    assert payload["BHSM_1_0_release_complete"] is False
    assert payload["next_highest_upstream_blocker"] == (
        "UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION"
    )
    assert payload["current_tier_status"]["Tier_A"] == "COMPLETE"
    assert payload["current_tier_status"]["Tier_B"] == "COMPLETE"
    assert payload["parameter_free_extension_blocker"] == "RB-02"


def test_all_guards_are_false_and_frozen_hashes_match():
    assert all(value is False for value in audit.GUARDS.values())
    assert audit.frozen_hashes_match(ROOT)
    for path, expected in audit.FROZEN_HASHES.items():
        assert audit.frozen_file_sha256(ROOT / path) == expected


def test_validation_contract_passes():
    checks = audit.validate(ROOT)
    assert checks
    assert all(checks.values()), checks


def test_ten_versioned_artifacts_are_deterministic_and_current():
    assert len(audit.ARTIFACT_FILES) == 10
    first = audit.artifact_bytes(ROOT)
    second = audit.artifact_bytes(ROOT)
    assert first == second
    for name, content in first.items():
        assert (ROOT / "artifacts" / name).read_bytes() == content
        json.loads(content)


def test_materializer_is_idempotent_and_updates_canonical_gate():
    script = ROOT / "scripts" / "materialize_claim_input_completion_consistency_v6_30_8.py"
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {name: (ROOT / "artifacts" / name).read_bytes() for name in audit.ARTIFACT_FILES.values()}
    canonical_first = (ROOT / "artifacts" / "BHSM_1_0_completion_gate.json").read_bytes()
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {name: (ROOT / "artifacts" / name).read_bytes() for name in audit.ARTIFACT_FILES.values()}
    canonical_second = (ROOT / "artifacts" / "BHSM_1_0_completion_gate.json").read_bytes()
    assert first == second == audit.artifact_bytes(ROOT)
    assert canonical_first == canonical_second
    assert json.loads(canonical_second)["version"] == "v8.0"
