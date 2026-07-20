import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import rare_b_observable_map as rb


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_rare_b_observable_map_scaffold_v5_1.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_artifact(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / rb.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def v5_1_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in rb.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def focused_v5_1_public_text() -> str:
    paths = [
        DOC,
        *(ARTIFACT_DIR / filename for filename in rb.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_all_v5_1_artifacts_exist_parse_and_have_common_no_fit_metadata():
    for key, filename in rb.ARTIFACT_FILES.items():
        path = ARTIFACT_DIR / filename
        assert path.exists(), key
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["version"] == "v5.1"
        assert payload["empirical_inputs_used"] is False
        assert payload["rare_b_data_fitting_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["physics_model_logic_changed"] is False


def test_materialized_non_audit_artifacts_match_deterministic_builders():
    built = rb.build_artifact_payloads(ROOT)
    for key, filename in rb.ARTIFACT_FILES.items():
        if key == "observable_map_audit":
            continue
        materialized = (ARTIFACT_DIR / filename).read_text(encoding="utf-8")
        assert materialized == rb.deterministic_json(built[key])


def test_primary_verdict_and_layer_status_are_interface_complete_only():
    payload = load_artifact("scaffold_verdict")
    assert payload["primary_verdict"] == "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
    assert payload["layer_status"] == {
        "observable_convention": "RARE_B_OBSERVABLE_INTERFACE_ARTIFACTED",
        "transition_operator": "RARE_B_TRANSITION_OPERATOR_INTERFACE_ARTIFACTED",
        "wilson_interface": "RARE_B_WILSON_COEFFICIENT_SLOTS_ARTIFACTED_DERIVATION_OPEN",
        "hadronic_form_factor_interface": "RARE_B_HADRONIC_FORM_FACTOR_INTERFACE_ARTIFACTED",
        "bhsm_matching_map": "RARE_B_BHSM_MATCHING_MAP_OPEN_DEPENDENCY_GRAPH_ARTIFACTED",
        "afb_null_balance": "RARE_B_AFB_NULL_BALANCE_INTERFACE_ARTIFACTED",
        "q2_physical_bridge": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
        "numerical_q0_squared_prediction": "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
        "exact_microplateau_node_map": "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
    }


def test_observable_convention_validates_external_q2_coordinate():
    payload = load_artifact("observable_convention")
    q2 = payload["q2"]
    assert q2 == {
        "definition": "squared dimuon invariant mass",
        "units": "GeV^2",
        "source": "external observable coordinate",
        "bhsm_derivation_status": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
    }
    assert rb.validate_q2_coordinate(q2["units"], q2["source"], q2["bhsm_derivation_status"])["is_physical_bridge_closed"] is False
    with pytest.raises(ValueError, match="GeV\\^2"):
        rb.validate_q2_coordinate("MeV^2", q2["source"], q2["bhsm_derivation_status"])
    with pytest.raises(ValueError, match="mislabeled"):
        rb.validate_q2_coordinate("GeV^2", "BHSM-derived", q2["bhsm_derivation_status"])


def test_transition_operator_slots_are_artifacted_but_not_derived():
    payload = load_artifact("transition_operator_interface")
    assert payload["channel"] == "b -> s mu+ mu-"
    assert {"O7", "O9", "O10"}.issubset(payload["operator_basis_slots"])
    assert set(payload["wilson_coefficient_slots"]) == {"C7_eff", "C9_eff", "C10_eff"}
    assert all(
        row["status"] == "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION"
        for row in payload["wilson_coefficient_slots"].values()
    )
    assert payload["flavor_prefactor_slot"]["bhsm_status"] == "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING"
    assert "CKM geometry alone does not currently provide" in payload["flavor_prefactor_slot"]["note"]


def test_hadronic_interface_requires_form_factors_and_keeps_bhsm_derivation_open():
    payload = load_artifact("hadronic_interface")
    assert payload["exclusive_decay_channel"] == "B0 -> K*0 mu+ mu-"
    assert payload["form_factor_basis"]["required_symbols"] == [
        "V(q^2)",
        "A0(q^2)",
        "A1(q^2)",
        "A2(q^2)",
        "T1(q^2)",
        "T2(q^2)",
        "T3(q^2)",
    ]
    assert payload["bhsm_derivation_status"] == "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS"
    assert payload["exclusive_prediction_requires_hadronic_inputs"] is True


def test_afb_null_balance_is_symbolic_convention_interface_not_prediction():
    payload = load_artifact("afb_null_balance")
    assert payload["audit_classification"] == "EXPLICIT_BUT_EXTERNAL_CONVENTION_ONLY"
    assert payload["zero_condition"] == "N_FB(q0^2)=0"
    assert payload["nonzero_denominator_condition"] == "D_FB(q0^2) != 0"
    assert "Re[" in payload["symbolic_numerator"]
    assert {"C7_eff", "C9_eff", "C10_eff"}.issubset(payload["required_coefficient_inputs"])
    assert payload["required_physical_q2_input"]["bhsm_derivation_status"] == "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE"


def test_matching_dependency_graph_preserves_all_required_open_gates():
    payload = load_artifact("bhsm_matching_map")
    statuses = {row["status"] for row in payload["dependencies"]}
    assert {
        "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
        "ARTIFACT_BACKED_INPUT_NOT_OBSERVABLE_MAP",
        "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
        "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
        "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
        "OPEN_MISSING_SCALE_DEPENDENCE_CLOSURE",
        "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS",
        "OPEN_MISSING_OBSERVABLE_NORMALIZATION_CLOSURE",
    }.issubset(statuses)
    assert payload["physical_matching_closed"] is False
    assert payload["prediction_ready"] is False


def test_prediction_kill_screen_emits_no_q0_or_node_values():
    screen = rb.prediction_kill_screen()
    assert screen["prediction_claimed"] is False
    assert screen["q0_squared_value"] is None
    assert screen["q0_squared_units"] is None
    assert screen["microplateau_node_coordinates"] == []
    assert screen["all_required_gates_closed"] is False
    assert {
        "transition_operator_map_closed",
        "wilson_matching_closed",
        "q2_physical_bridge_closed",
        "normalization_closed",
        "scale_dependence_closed",
    }.issubset(screen["blocking_gates"])


def test_audit_answers_record_interfaces_present_and_physical_prediction_absent():
    answers = load_artifact("observable_map_audit")["audit_answers"]
    assert answers == {
        "b_to_s_mumu_transition_operator_map_exists": False,
        "wilson_coefficient_map_exists": False,
        "afb_numerator_interface_exists": True,
        "afb_null_balance_equation_exists": True,
        "physical_q2_bridge_exists": False,
        "hadronic_form_factor_interface_exists": True,
        "bhsm_derived_hadronic_map_exists": False,
        "exact_microplateau_node_map_exists": False,
        "numerical_q0_squared_prediction_exists": False,
    }


def test_cli_status_json_and_markdown_are_available_from_repo_local_src():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    json_run = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "rare-b-observable-map-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(json_run.stdout)
    assert payload["primary_verdict"] == "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
    assert payload["prediction_state"]["prediction_claimed"] is False

    markdown_run = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "rare-b-observable-map-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.1 Rare-B Observable Map Scaffold" in markdown_run.stdout
    assert "Prediction State" in markdown_run.stdout


def test_status_claims_docs_and_index_include_required_v5_1_claim_boundary():
    text = v5_1_text()
    assert "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE" in text
    assert "BHSM has artifacted the minimal rare-B observable-map interface needed to state the remaining matching problem precisely." in text
    assert "BHSM does not yet predict q0^2 or exact micro-plateau node positions." in text
    assert "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE" in text
    assert "RARE_B_AFB_ZERO_PREDICTION_BLOCKED" in text
    assert "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED" in text


def test_forbidden_positive_prediction_and_completion_phrases_are_absent():
    text = focused_v5_1_public_text()
    forbidden = (
        "BHSM predicts q0^2",
        "BHSM predicts the A_FB zero",
        "BHSM predicts rare-B micro-plateaus",
        "BHSM explains LHCb anomalies",
        "BHSM falsifies continuous QFT",
        "rare-B data were used to fit the prediction",
        "gauge-coupling normalization is solved",
        "alpha_i=lambda_i is derived",
        "alpha_2=lambda_2 is derived",
        "g2_BH is action-derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "full BHSM is complete",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    verdict = load_artifact("scaffold_verdict")
    assert verdict["frozen_predictions_changed"] is False
    assert verdict["official_prediction_logic_changed"] is False
    assert verdict["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
