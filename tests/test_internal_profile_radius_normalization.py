import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import internal_profile_radius_normalization as norm


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
    "internal_profile_radius_normalization_v1.json",
    "Phi_profile_normal_form_v1.json",
    "Z_H_profile_normalization_closure_or_obstruction_v1.json",
    "kappa_H_profile_second_variation_closure_or_obstruction_v1.json",
    "profile_scale_tau_sigma_update_v1.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_radius_symbols_are_disambiguated_and_cosmology_not_used():
    rows = norm.disambiguate_radius_symbols(ROOT)
    by_id = {row.object_id: row for row in rows}
    assert by_id["r_internal_profile"].used_as_internal_profile_r is True
    assert by_id["r_internal_profile"].status == norm.BLOCKED_BY_MISSING_NORMALIZATION_THEOREM
    assert by_id["R_H_cosmological"].value == 24.0
    assert by_id["R_H_cosmological"].used_as_internal_profile_r is False
    assert by_id["rho_star_collar_depth"].used_as_internal_profile_r is False
    assert by_id["Lambda_BH_matching_scale"].used_as_internal_profile_r is False
    assert by_id["Lambda_squared_overlap"].used_as_internal_profile_r is False
    assert by_id["S_overlap_width"].used_as_internal_profile_r is False


def test_r_is_not_invented_if_normalization_theorem_missing():
    result = norm.attempt_internal_profile_radius_derivation(ROOT)
    assert result["status"] == norm.BLOCKED_BY_MISSING_NORMALIZATION_THEOREM
    assert result["derived"] is False
    assert result["value"] is None
    assert result["cosmological_R_H_used"] is False
    assert result["S_or_Lambda_silently_used_as_radius"] is False
    for item in (
        "Hopf fiber-radius normalization theorem",
        "Berger volume normalization theorem",
        "internal profile-domain measure theorem",
        "collar-depth matching condition",
        "Lambda-to-radius convention",
    ):
        assert item in result["missing_objects"]


def test_phi_normal_form_is_localized_but_phi0_not_numerical():
    profile = norm.attempt_phi_normal_form(ROOT)
    assert profile["status"] == norm.DERIVED_CONDITIONAL
    assert profile["Phi_profile"]["formula"] == "Phi(y)=Phi_0 exp[-sigma d_B(y,y_0)^2]"
    assert profile["symbolic_Phi_0"].startswith("1/sqrt")
    assert profile["Phi_0_numerical_assigned"] is False
    assert "sigma value" in profile["missing_objects"]
    assert profile["objects"]["Phi_0"]["value"].startswith("1/sqrt")
    assert profile["objects"]["Phi_0"]["status"] == norm.OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH


def test_Z_H_is_not_set_to_one_without_normalization_theorem():
    z_h = norm.attempt_Z_H_derivation(ROOT)
    assert z_h["status"] == norm.BLOCKED_BY_MISSING_PROFILE_MEASURE
    assert z_h["derived"] is False
    assert z_h["value"] is None
    assert z_h["Z_H_set_to_one"] is False
    assert z_h["normalized_profile_would_imply_Z_H_equals_one"] == "CONDITIONAL_ONLY"
    assert "profile normalization theorem identifying Z_H with unit norm" in z_h["missing_objects"]
    assert z_h["observed_Higgs_used"] is False


def test_kappa_H_is_not_observed_higgs_or_tau_fit():
    kappa = norm.attempt_kappa_H_derivation(ROOT)
    assert kappa["status"] == norm.BLOCKED_BY_MISSING_EFFECTIVE_ACTION
    assert kappa["derived"] is False
    assert kappa["value"] is None
    assert kappa["observed_Higgs_used"] is False
    assert kappa["kappa_H_chosen_to_set_tau"] is False
    assert "S_eff^(H) Higgs/profile effective action" in kappa["missing_objects"]
    assert "boundary potential curvature coefficients" in kappa["missing_objects"]


def test_current_sigma_tau_remains_blocked_with_exact_missing_objects():
    result = norm.attempt_sigma_tau_after_profile_scale_closure(repo_root=ROOT)
    assert result["boundary_profile_scale_closure"] == norm.BLOCKED_BY_MISSING_OBJECTS
    assert result["sigma_from_boundary_geometry"] == norm.OPEN_LOCALIZABLE
    assert result["tau_from_boundary_geometry"] == norm.OPEN_LOCALIZABLE
    assert result["sigma_derived"] is False
    assert result["tau_derived"] is False
    assert result["charged_outputs_at_tau_exported"] is False
    assert result["missing_objects"] == ["r_internal_profile", "Z_H", "kappa_H"]
    assert result["official_predictions_changed"] is False
    assert result["empirical_derivation_inputs_used"] is False
    assert result["tau_fit_to_masses"] is False
    assert result["sigma_fit_to_masses"] is False


def test_if_all_required_objects_close_sigma_tau_formulas_apply():
    overrides = {
        "r_internal_profile": {"status": norm.DERIVED_FIXED, "value": 2.0},
        "Z_H": {"status": norm.DERIVED_CONDITIONAL, "value": 8.0},
        "kappa_H": {"status": norm.DERIVED_CONDITIONAL, "value": 32.0},
    }
    result = norm.attempt_sigma_tau_after_profile_scale_closure(overrides=overrides)
    assert result["sigma_derived"] is True
    assert result["tau_derived"] is True
    assert result["sigma"] == 1.0
    assert result["tau"] == 1.0 / 16.0
    assert result["missing_objects"] == []


def test_generated_artifacts_have_guardrails_and_parse():
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


def test_previous_artifacts_record_pr47_followup_without_promotion():
    boundary = load_artifact("boundary_profile_scale_closure_v1.json")
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    package = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    assert boundary["targeted_followup_from_PR47"]["source_artifact"] == (
        "artifacts/internal_profile_radius_normalization_v1.json"
    )
    assert boundary["boundary_profile_scale_closure"] == norm.BLOCKED_BY_MISSING_OBJECTS
    assert central["gates"]["tau_sigma"]["targeted_followup_from_PR47"]["r_internal_profile_status"] == (
        norm.BLOCKED_BY_MISSING_NORMALIZATION_THEOREM
    )
    assert central["promoted_statuses"] == []
    assert package["sections"]["open_boundary_parameters"]["source_artifact"] == (
        "artifacts/profile_scale_tau_sigma_update_v1.json"
    )
    assert package["sections"]["open_boundary_parameters"]["comparison_ready"] is False


def test_no_boundary_tau_charged_outputs_exported():
    assert not (ROOT / "artifacts" / "tau_sigma_boundary_values_v1.json").exists()
    assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_local_v1.json").exists()
    assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_background_identity_v1.json").exists()


def test_new_status_section_has_no_forbidden_claims():
    text = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## Internal/Profile Radius And Higgs/Profile Normal Form Assault"
    assert marker in text
    section = text.split(marker, 1)[1]
    forbidden = (
        "BHSM is proven",
        "BHSM replaces the Standard Model",
        "predicted the Higgs mass",
        "experimentally confirmed",
    )
    for phrase in forbidden:
        assert phrase not in section


def test_sources_do_not_import_empirical_closure_modules():
    text = (ROOT / "src" / "internal_profile_radius_normalization.py").read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "observed_mass_fixture",
        "target_ratio_fixture",
    )
    for token in blocked:
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
