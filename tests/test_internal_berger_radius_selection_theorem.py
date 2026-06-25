import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import internal_berger_radius_selection_theorem as theorem


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}
NEW_ARTIFACTS = (
    "internal_berger_radius_selection_theorem_v1.json",
    "internal_profile_radius_value_v1.json",
    "internal_radius_route_consistency_matrix_v1.json",
    "internal_radius_equivalence_classes_v1.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_author_axiom_encodes_required_equalities():
    axiom = theorem.author_supplied_overlap_radius_axiom(ROOT)
    assert axiom["status"] == theorem.THEOREM_STATUS
    assert axiom["S_formula"] == "S = 1/(4*pi)"
    assert axiom["Lambda_squared_formula"] == "Lambda_squared = 1/(4*pi)"
    assert axiom["r_squared_formula"] == "r_internal_profile^2 = S = Lambda_squared = 1/(4*pi)"
    assert axiom["r_formula"] == "r_internal_profile = sqrt(S) = 1/sqrt(4*pi)"
    assert axiom["empirical_inputs_used"] is False


def test_lambda_squared_equals_overlap_width_and_radius_value():
    equality = theorem.validate_lambda_squared_equals_overlap_width(ROOT)
    radius = theorem.derive_internal_profile_radius_from_overlap(ROOT)
    expected_s = 1.0 / (4.0 * math.pi)
    expected_r = 1.0 / math.sqrt(4.0 * math.pi)
    assert equality["equal"] is True
    assert equality["S_value"] == expected_s
    assert equality["Lambda_squared_value"] == expected_s
    assert radius["r_internal_profile_squared"] == expected_s
    assert radius["r_internal_profile"] == expected_r
    assert radius["r_internal_profile_formula"] == "1/sqrt(4*pi)"
    assert radius["cosmological_R_H_used"] is False


def test_route_verdicts_match_author_normalization():
    verdicts = {row.route_id: row for row in theorem.route_verdicts(ROOT)}
    assert verdicts["unit_internal_radius"].verdict == theorem.REJECTED_BY_AUTHOR_NORMALIZATION
    assert verdicts["unit_internal_radius"].selected is False
    assert verdicts["lambda_radius"].verdict == theorem.SELECTED_BY_AUTHOR_AXIOM
    assert verdicts["lambda_radius"].selected is True
    assert verdicts["overlap_width_radius"].verdict == theorem.SELECTED_BY_AUTHOR_AXIOM
    assert verdicts["overlap_width_radius"].selected is True
    assert verdicts["berger_volume_normalization"].verdict == theorem.NOT_PRIMARY_ROUTE
    assert verdicts["collar_depth_matching"].verdict == theorem.NOT_PRIMARY_ROUTE


def test_lambda_overlap_equivalence_is_semantic_and_source_traced():
    artifact = theorem.build_author_radius_selection_artifact(ROOT)
    equivalence = artifact["lambda_overlap_equivalence"]
    assert equivalence["equal"] is True
    assert "not as a post-hoc numerical coincidence" in equivalence["semantic_equivalence"]
    assert equivalence["source_trace"]
    assert artifact["radius_normalization_fork"] == theorem.FORK_STATUS
    assert artifact["internal_berger_radius_selection_theorem"] == theorem.THEOREM_STATUS


def test_tau_symbolic_dependency_after_radius_substitution_and_no_numeric_tau():
    chain = theorem.propagate_radius_to_tau_sigma_obstruction_chain(ROOT)
    assert chain["r_internal_profile_status"] == theorem.RADIUS_STATUS
    assert chain["Z_H_status"] == theorem.OPEN_LOCALIZABLE
    assert chain["kappa_H_status"] == theorem.OPEN_LOCALIZABLE
    assert chain["tau_symbolic_after_radius_substitution"] == "tau(Z_H,kappa_H) = 2*pi*sqrt(Z_H/kappa_H)"
    assert chain["tau_numeric_computed"] is False
    assert chain["tau_derived"] is False
    assert chain["sigma_derived"] is False
    assert chain["charged_outputs_at_tau_exported"] is False
    assert chain["remaining_blockers"] == ("Z_H", "kappa_H")


def test_generated_artifacts_have_guardrails_and_radius_selection():
    for name in NEW_ARTIFACTS:
        payload = load_artifact(name)
        assert payload["public_status_before_gate"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["observed_masses_used"] is False
        assert payload["observed_Higgs_used"] is False
        assert payload["observed_gauge_values_used"] is False
        assert payload["tau_fit_to_masses"] is False
        assert payload["sigma_fit_to_masses"] is False
        assert payload["radius_selected_by"] == theorem.AUTHOR_SELECTION


def test_profile_scale_update_moves_blocker_to_Z_H_and_kappa_H_only():
    payload = load_artifact("profile_scale_tau_sigma_update_v1.json")
    update = payload["profile_scale_tau_sigma_update"]
    assert update["r_internal_profile_status"] == theorem.RADIUS_STATUS
    if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
        assert update["Z_H_status"] == "DERIVED_CONDITIONAL"
        assert update["Z_H"] == 1.0
        assert update["missing_objects"] == ["kappa_H"]
        assert update["tau_formula_after_Z_H_substitution"] == "tau(kappa_H) = 2*pi/sqrt(kappa_H)"
    else:
        assert update["missing_objects"] == ["Z_H", "kappa_H"]
    assert update["tau_formula_after_radius_substitution"] == "tau(Z_H,kappa_H) = 2*pi*sqrt(Z_H/kappa_H)"
    assert update["tau_derived"] is False
    assert update["sigma_derived"] is False
    assert update["charged_outputs_at_tau_exported"] is False


def test_prior_artifacts_record_radius_gate_promotion_without_global_closure():
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    claims = load_artifact("full_BHSM_claim_status_table_v2.json")
    statuses = load_artifact("full_BHSM_open_gate_ledger_v2.json")["statuses"]
    promoted = central["promoted_statuses"]
    assert {"gate": "internal_berger_radius_selection_theorem", "status": theorem.THEOREM_STATUS} in promoted
    assert {"gate": "r_internal_profile", "status": theorem.RADIUS_STATUS} in promoted
    assert statuses["internal_berger_radius_selection_theorem"] == theorem.THEOREM_STATUS
    assert statuses["internal_profile_radius_normalization"] == theorem.RADIUS_STATUS
    assert statuses["boundary_profile_scale_closure"] == "BLOCKED_BY_MISSING_OBJECTS"
    assert any(row["claim"] == "Internal profile radius value" for row in claims["claim_statuses"])


def test_Z_H_is_not_set_to_one_and_kappa_H_not_invented():
    boundary = load_artifact("boundary_profile_scale_closure_v1.json")
    profile = load_artifact("profile_scale_tau_sigma_update_v1.json")
    if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
        assert boundary["Z_H_result"]["value"] == 1.0
        assert boundary["Z_H_result"]["Z_H_set_to_one_by_theorem"] is True
        assert boundary["Z_H_result"]["Z_H_set_to_one_by_habit"] is False
        assert profile["profile_scale_tau_sigma_update"]["missing_objects"] == ["kappa_H"]
    else:
        assert profile["profile_scale_tau_sigma_update"]["missing_objects"] == ["Z_H", "kappa_H"]
    assert boundary["Z_H"]["value"] is None
    assert boundary["kappa_H"]["value"] is None


def test_public_status_section_has_no_forbidden_claims():
    text = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## Author-Supplied Internal Berger Radius Selection"
    assert marker in text
    section = text.split(marker, 1)[1]
    for phrase in (
        "BHSM is proven",
        "BHSM replaces the Standard Model",
        "predicted the Higgs mass",
        "experimentally confirmed",
    ):
        assert phrase not in section


def test_sources_do_not_import_empirical_closure_modules():
    text = (ROOT / "src" / "internal_berger_radius_selection_theorem.py").read_text(encoding="utf-8")
    for token in (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "observed_mass_fixture",
        "target_ratio_fixture",
    ):
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
