import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import b_to_s_mumu_operator_matching as op


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_b_to_s_mumu_operator_matching_killscreen_v5_2.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_artifact(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / op.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_v5_2_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in op.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_2_artifacts_exist_parse_and_keep_prediction_metadata_false():
    for key, filename in op.ARTIFACT_FILES.items():
        payload = load_artifact(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.2"
        assert payload["channel"] == "b -> s mu+ mu-"
        assert payload["primary_verdict"] == "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED"
        assert payload["empirical_inputs_used"] is False
        assert payload["rare_b_data_fitting_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["physics_model_logic_changed"] is False


def test_materialized_non_scan_artifacts_match_deterministic_builders():
    built = op.build_artifact_payloads(ROOT)
    for key, filename in op.ARTIFACT_FILES.items():
        if key in {"operator_source_inventory", "operator_matching_audit"}:
            continue
        materialized = (ARTIFACT_DIR / filename).read_text(encoding="utf-8")
        assert materialized == op.deterministic_json(built[key])


def test_inventory_records_sources_but_none_are_usable_for_physical_matching():
    payload = load_artifact("operator_source_inventory")
    assert payload["status"] == "RARE_B_OPERATOR_SOURCE_INVENTORY_ARTIFACTED"
    entries = payload["entries"]
    names = {entry["artifact_or_symbol"] for entry in entries}
    assert "CKM_no_fit_operator_output_v1" in names
    assert "BHSM_rare_b_transition_operator_interface_v5_1" in names
    assert "BHSM_neutral_action_closure_report_v1_5" in names
    assert all(entry["usable_for_matching"] is False for entry in entries)
    assert any("CKM matrix alone" in entry["blocking_reason"] for entry in entries)
    assert payload["repository_scan_summary"]["scan_verdict"].startswith("No scanned repository object closes")


def test_dependency_graph_has_no_closed_missing_edges_and_first_open_edge_is_fcnc():
    payload = load_artifact("transition_dependency_graph")
    assert payload["status"] == "B_TO_S_MUMU_TRANSITION_DEPENDENCY_GRAPH_ARTIFACTED"
    assert payload["first_open_edge"] == {
        "source": "b -> s flavor selector",
        "target": "FCNC generation mechanism",
        "blocking_dependency": "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
    }
    for edge in payload["edges"]:
        assert edge["provenance"]
        assert edge["status"] != "CLOSED"
        assert edge["units_transformation"]
        assert edge["normalization_transformation"]
        assert edge["blocking_dependency"]


def test_candidate_set_is_empty_and_external_o7_o9_o10_are_not_bhsm_derivations():
    payload = load_artifact("operator_matching_candidate")
    assert payload["status"] == "B_TO_S_MUMU_OPERATOR_MATCHING_CANDIDATE_EMPTY_BLOCKED"
    assert payload["candidate_operators"] == []
    assert payload["flavor_mechanism"] == "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
    patterns = {row["slot"]: row for row in payload["external_operator_patterns_not_derived"]}
    assert set(patterns) == {"O7", "O9", "O10"}
    assert all(row["status"] == "EXTERNAL_EFT_CONVENTION_NOT_BHSM_DERIVATION" for row in patterns.values())
    assert patterns["O7"]["C7_BHSM"] is None
    assert patterns["O9"]["C9_BHSM"] is None
    assert patterns["O10"]["C10_BHSM"] is None


def test_audit_answers_block_all_physical_matching_gates_but_preserve_v5_1_connection():
    answers = load_artifact("operator_matching_audit")["audit_answers"]
    assert answers == {
        "explicit_b_to_s_flavor_transition_exists": False,
        "explicit_bhsm_fcnc_mechanism_exists": False,
        "explicit_normalized_quark_current_exists": False,
        "explicit_normalized_muon_current_exists": False,
        "explicit_lorentz_structure_exists": False,
        "explicit_chirality_structure_exists": False,
        "action_attached_coefficient_exists": False,
        "loop_order_mechanism_exists": False,
        "dimensionful_coefficient_bridge_exists": False,
        "renormalization_scale_map_exists": False,
        "projection_into_O7_exists": False,
        "projection_into_O9_exists": False,
        "projection_into_O10_exists": False,
        "equivalent_basis_independent_map_exists": False,
        "numerical_wilson_coefficients_exist": False,
        "connection_to_v5_1_interface_exists": True,
    }


def test_kill_screens_reject_ckm_only_neutral_response_tree_fcnc_and_loop_resemblance():
    audit = load_artifact("operator_matching_audit")["kill_screens"]
    assert audit["flavor_changing_neutral_current"]["status"] == "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
    assert audit["flavor_changing_neutral_current"]["generic_neutral_current_is_sufficient"] is False
    assert audit["flavor_changing_neutral_current"]["tree_level_fcnc"]["allowed"] is False
    assert audit["loop_order"]["geometric_loop_factor_rejection"]["allowed"] is False
    assert audit["action_normalization"]["lambda_i_equals_alpha_i_derived"] is False
    assert audit["action_normalization"]["alpha2_equals_lambda2_derived"] is False
    assert audit["action_normalization"]["c_rel_squared_equals_4pi_derived"] is False
    assert audit["action_normalization"]["g2_BH_derived"] is False


def test_candidate_operator_validation_fails_for_required_missing_metadata():
    base = op.CandidateOperator(
        name="bad",
        channel="b -> s mu+ mu-",
        basis_convention="external",
        initial_flavor_state="b",
        final_flavor_state="s",
        lepton_current=None,
        lorentz_structure=None,
        chirality=None,
        coefficient_symbol=None,
        coefficient_dimensions=None,
        coefficient_provenance=None,
        action_attachment_status="OPEN_MISSING_RARE_B_OPERATOR_ACTION_NORMALIZATION",
        fcnc_mechanism_status="OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM",
        loop_order_status="OPEN_MISSING_RARE_B_LOOP_MATCHING_PRINCIPLE",
        dimensionful_bridge_status="OPEN_MISSING_RARE_B_OPERATOR_DIMENSIONFUL_BRIDGE",
        renormalization_scale_status="OPEN_MISSING_RARE_B_RENORMALIZATION_SCALE_MAP",
        wilson_slot="O9",
        numerical_wilson_value=None,
        prediction_claimed=False,
    )
    with pytest.raises(ValueError, match="FCNC"):
        op.validate_candidate_operator(base)

    missing_flavor = op.CandidateOperator(**{**base.to_dict(), "initial_flavor_state": None})
    with pytest.raises(ValueError, match="flavor states"):
        op.validate_candidate_operator(missing_flavor)


def test_numerical_wilson_q0_and_node_values_remain_null():
    verdict = load_artifact("operator_matching_verdict")
    screen = verdict["prediction_kill_screen"]
    assert screen["prediction_claimed"] is False
    assert screen["C7_BHSM"] is None
    assert screen["C9_BHSM"] is None
    assert screen["C10_BHSM"] is None
    assert screen["delta_C7_BHSM"] is None
    assert screen["delta_C9_BHSM"] is None
    assert screen["delta_C10_BHSM"] is None
    assert screen["q0_squared_value"] is None
    assert screen["microplateau_node_coordinates"] == []
    assert "wilson_matching_closed" in screen["blocking_gates"]


def test_verdict_preserves_historical_blockers_and_v5_1_interface():
    verdict = load_artifact("operator_matching_verdict")
    assert verdict["earliest_blocking_dependency"] == "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
    assert verdict["v5_1_interface_verdict_preserved"] == "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
    assert set(op.PRESERVED_STATUSES).issubset(verdict["preserved_historical_blockers"])
    assert "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM" in verdict["new_blockers"]
    assert verdict["recommended_next_sprint"] == "bhsm-rare-b-fcnc-generation-mechanism-v5-3"


def test_cli_status_reports_v5_2_verdict_and_null_prediction_state():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "b-to-s-mumu-operator-matching-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_verdict"] == "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED"
    assert payload["earliest_blocking_dependency"] == "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
    assert payload["prediction_state"]["C9_BHSM"] is None

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "b-to-s-mumu-operator-matching-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.2 b -> s mu+ mu- Operator-Matching Kill Screen" in markdown.stdout


def test_public_ledgers_include_v5_2_blocked_claim_boundary():
    text = focused_v5_2_text()
    assert "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED" in text
    assert "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM" in text
    assert "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE" in text
    assert "BHSM v5.2 does not derive a physical `b -> s mu+ mu-` transition operator" in text
    assert "Interface compatibility with `O7`, `O9`, or `O10` is not a BHSM derivation." in text


def test_forbidden_positive_rare_b_and_coupling_claims_are_absent_from_v5_2_public_package():
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, *(ARTIFACT_DIR / filename for filename in op.ARTIFACT_FILES.values())]
    )
    forbidden = (
        "BHSM predicts the rare-B anomaly",
        "BHSM explains LHCb",
        "BHSM derives Wilson coefficients from CKM alone",
        "BHSM produces FCNCs automatically",
        "BHSM derives a loop factor from geometric resemblance",
        "BHSM derives g2_BH",
        "BHSM derives alpha_i",
        "BHSM derives the CKM coefficient value or exponent",
        "BHSM predicts q0^2",
        "BHSM predicts micro-plateaus",
        "BHSM falsifies continuous QFT",
        "BHSM is complete",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    verdict = load_artifact("operator_matching_verdict")
    assert verdict["frozen_predictions_changed"] is False
    assert verdict["official_prediction_logic_changed"] is False
    assert verdict["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
