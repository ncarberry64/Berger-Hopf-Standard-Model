import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import b_to_s_mumu_operator_matching as v52
from bhsm.interface import rare_b_fcnc_generation_mechanism as fcnc
from bhsm.interface import rare_b_observable_map as v51


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_rare_b_fcnc_generation_mechanism_v5_3.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_artifact(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / fcnc.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_v5_3_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in fcnc.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def public_v5_3_text() -> str:
    paths = [DOC, *(ARTIFACT_DIR / filename for filename in fcnc.ARTIFACT_FILES.values())]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_3_artifacts_exist_parse_and_preserve_no_fit_metadata():
    for key, filename in fcnc.ARTIFACT_FILES.items():
        payload = load_artifact(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.3"
        assert payload["sprint"] == "bhsm-rare-b-fcnc-generation-mechanism-v5-3"
        assert payload["primary_verdict"] == "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED"
        assert payload["empirical_inputs_used"] is False
        assert payload["rare_b_data_fitting_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["physics_model_logic_changed"] is False


def test_materialized_artifacts_match_deterministic_builders():
    built = fcnc.build_artifact_payloads(ROOT)
    for key, filename in fcnc.ARTIFACT_FILES.items():
        materialized = (ARTIFACT_DIR / filename).read_text(encoding="utf-8")
        assert materialized == fcnc.deterministic_json(built[key])


def test_neutral_current_audit_rejects_tree_level_b_s_by_default():
    payload = load_artifact("neutral_current_flavor_structure_audit")
    assert payload["status"] == "RARE_B_NEUTRAL_CURRENT_FLAVOR_STRUCTURE_AUDIT_ARTIFACTED"
    assert payload["tree_level_b_s_permitted"] is False
    assert payload["tree_level_b_s_derived"] is False
    assert payload["diagonal_off_diagonal_status"] == "NO_EXPLICIT_ACTION_BACKED_OFF_DIAGONAL_NEUTRAL_CURRENT"
    assert "No explicit action-backed off-diagonal neutral current" in payload["claim_safe_rule"]
    rejection = fcnc.reject_tree_level_fcnc_without_theorem("OPEN")
    assert rejection["allowed"] is False
    assert rejection["status"] == "TREE_LEVEL_FCNC_FORBIDDEN_OR_UNPROVED"


def test_ckm_geometry_and_generic_neutral_response_cannot_close_fcnc_gate():
    objects = {row.symbol_or_artifact: row for row in fcnc.audited_mechanism_objects()}
    assert objects["CKM_no_fit_operator_output_v1"].supports_composition is False
    assert objects["CKM_no_fit_operator_output_v1"].can_generate_off_diagonal_neutral_matrix_element is False
    assert objects["BHSM_neutral_action_closure_report_v1_5"].can_generate_off_diagonal_neutral_matrix_element is False
    assert objects["BHSM_neutral_action_closure_report_v1_5"].blocking_dependency == "OPEN_MISSING_RARE_B_INDUCED_NEUTRAL_KERNEL"


def test_charged_current_pair_composition_requires_all_explicit_maps():
    payload = load_artifact("charged_current_pair_composition")
    candidate = payload["candidate"]
    assert payload["status"] == "RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION_BLOCKED"
    assert candidate["initial_flavor"] == "b"
    assert candidate["final_flavor"] == "s"
    assert candidate["first_current_insertion"] is None
    assert candidate["second_current_insertion"] is None
    assert candidate["intermediate_state"] is None
    assert candidate["flavor_orientation"] is None
    assert candidate["complex_conjugation"] is None
    assert candidate["internal_response_object"] is None
    assert candidate["closure_status"] == "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION"
    with pytest.raises(ValueError, match="charged-current pair composition missing"):
        fcnc.validate_charged_current_pair(fcnc.charged_current_pair_candidate())


def test_intermediate_response_inventory_keeps_kernel_absent_for_fcnc_generation():
    payload = load_artifact("intermediate_response_inventory")
    assert payload["status"] == "RARE_B_INTERMEDIATE_RESPONSE_KERNEL_ABSENT"
    assert payload["absent"] is True
    assert payload["derived"] is False
    assert payload["conditional"] is False
    assert all(row["usable_for_fcnc_generation"] is False for row in payload["inventory"])
    assert any("not a flavor intermediate-state propagator" in row["blocking_reason"] for row in payload["inventory"])


def test_generation_candidate_is_empty_and_nonzero_transition_is_not_established():
    payload = load_artifact("fcnc_generation_candidate")
    assert payload["status"] == "RARE_B_FCNC_GENERATION_CANDIDATE_EMPTY_BLOCKED"
    assert payload["candidate_expression"] is None
    assert payload["symbolic_template_not_promoted"] == "A_bs = sum_i F_flavor(i; b,s) R_internal(i)"
    assert payload["candidate_nonzero_status"] == "NONZERO_TRANSITION_NOT_ESTABLISHED"
    assert payload["connection_to_v5_2"]["v5_3_refinement"] == "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION"
    rejection = fcnc.reject_symbolic_sum_as_nonzero_proof(payload["candidate_expression"], None)
    assert rejection["nonzero_established"] is False


def test_generation_sum_and_cancellation_law_remain_open():
    payload = load_artifact("gim_like_cancellation_audit")
    assert payload["status"] == "RARE_B_GIM_LIKE_CANCELLATION_THEOREM_ABSENT"
    assert payload["bhsm_generation_sum_exists"] is False
    assert payload["degeneracy_cancellation_proved"] is False
    assert payload["nonzero_mode_splitting_defined"] is False
    assert payload["result_action_connected"] is False
    assert payload["result_normalized"] is False
    assert payload["cancellation_theorem_status"] == "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW"


def test_loop_factor_and_one_loop_status_cannot_be_inferred():
    rejection = fcnc.reject_loop_factor_without_provenance("1/(16*pi^2)", None)
    assert rejection["allowed"] is False
    assert rejection["status"] == "LOOP_FACTOR_PROVENANCE_REJECTED"
    verdict = load_artifact("verdict")
    assert verdict["perturbative_order_status"] == "OPEN_MISSING_RARE_B_FCNC_PERTURBATIVE_ORDER"
    assert "two named charged-current labels are not a loop" in "\n".join(verdict["invalidated_or_downgraded"])


def test_dependency_graph_extends_v5_2_and_marks_first_open_edge():
    payload = load_artifact("dependency_graph")
    assert payload["status"] == "RARE_B_FCNC_GENERATION_DEPENDENCY_GRAPH_ARTIFACTED"
    assert payload["first_open_edge"] == {
        "source": "charged-current flavor transport",
        "target": "first charged-current insertion",
        "blocking_dependency": "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION",
    }
    statuses = {edge["status"] for edge in payload["edges"]}
    assert "BLOCKED" in statuses
    assert all(edge["provenance"] for edge in payload["edges"])
    assert all(edge["blocking_dependency"] for edge in payload["edges"])


def test_verdict_preserves_v5_1_v5_2_and_refines_open_blockers():
    verdict = load_artifact("verdict")
    assert verdict["primary_verdict"] == "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED"
    assert verdict["earliest_blocking_dependency"] == "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION"
    assert verdict["nonzero_transition_established"] is False
    assert "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE" in verdict["preserved_statuses"]
    assert "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED" in verdict["preserved_statuses"]
    assert set(fcnc.REFINED_OPEN_BLOCKERS).issubset(verdict["new_or_refined_open_blockers"])
    assert "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM" in verdict["still_open"]
    assert verdict["recommended_next_sprint"] == "bhsm-charged-current-pair-composition-v5-4"


def test_v5_1_and_v5_2_regression_surfaces_remain_preserved():
    v51_report = v51.rare_b_status_report(ROOT)
    v52_report = v52.b_to_s_mumu_status_report(ROOT)
    assert v51_report["primary_verdict"] == "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
    assert v52_report["primary_verdict"] == "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED"
    assert v52_report["earliest_blocking_dependency"] == "OPEN_MISSING_RARE_B_FCNC_GENERATION_MECHANISM"
    assert v51_report["prediction_state"]["prediction_claimed"] is False
    assert v52_report["prediction_state"]["prediction_claimed"] is False


def test_audit_answers_and_prediction_state_remain_null():
    report = fcnc.rare_b_fcnc_generation_status_report(ROOT)
    answers = report["audit_answers"]
    assert answers["explicit_tree_level_b_s_neutral_current_exists"] is False
    assert answers["explicit_bhsm_charged_current_pair_composition_exists"] is False
    assert answers["explicit_intermediate_response_kernel_exists"] is False
    assert answers["explicit_generation_sum_exists"] is False
    assert answers["explicit_gim_like_or_degeneracy_cancellation_theorem_exists"] is False
    assert answers["physical_fcnc_mechanism_derived"] is False
    state = report["prediction_state"]
    assert state["prediction_claimed"] is False
    assert state["C7_BHSM"] is None
    assert state["C9_BHSM"] is None
    assert state["C10_BHSM"] is None
    assert state["q0_squared_value"] is None
    assert state["microplateau_node_coordinates"] == []


def test_cli_status_reports_v5_3_verdict_and_null_outputs():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "rare-b-fcnc-generation-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_verdict"] == "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED"
    assert payload["earliest_blocking_dependency"] == "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION"
    assert payload["prediction_state"]["C9_BHSM"] is None

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "rare-b-fcnc-generation-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.3 Rare-B FCNC Generation-Mechanism Kill Screen" in markdown.stdout


def test_public_ledgers_include_v5_3_claim_boundary_and_open_gates():
    text = focused_v5_3_text()
    assert "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED" in text
    assert "OPEN_MISSING_RARE_B_CHARGED_CURRENT_PAIR_COMPOSITION" in text
    assert "OPEN_MISSING_RARE_B_INTERMEDIATE_RESPONSE_KERNEL" in text
    assert "OPEN_MISSING_RARE_B_DEGENERACY_CANCELLATION_LAW" in text
    assert "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE" in text
    assert "B_TO_S_MUMU_OPERATOR_MATCHING_BLOCKED" in text
    assert "prediction_claimed=false" in text


def test_forbidden_positive_rare_b_fcnc_claims_are_absent_from_public_v5_3_package():
    text = public_v5_3_text()
    forbidden = (
        "BHSM automatically produces FCNCs.",
        "BHSM reproduces the Standard Model penguin.",
        "BHSM derives a loop factor from geometry.",
        "BHSM explains LHCb anomalies by predicting rare-B anomalies.",
        "BHSM derives Wilson coefficients.",
        "BHSM predicts q0^2.",
        "BHSM predicts micro-plateaus.",
        "BHSM falsifies QFT.",
        "BHSM is complete.",
        "lambda_i = alpha_i is derived",
        "alpha2 = lambda2 is derived",
        "c_rel^2 = 4*pi is derived",
        "g2_BH is derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    verdict = load_artifact("verdict")
    assert verdict["frozen_predictions_changed"] is False
    assert verdict["official_prediction_logic_changed"] is False
    assert verdict["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
