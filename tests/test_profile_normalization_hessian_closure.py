import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import profile_normalization_hessian_closure as closure


FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_radius_gate_is_not_reopened_and_radius_value_persists():
    artifact = closure.build_profile_normalization_hessian_closure_artifact(ROOT)
    assert artifact["radius_gate_status"] == closure.RADIUS_GATE_STATUS
    assert artifact["radius_fork_reopened"] is False
    assert artifact["r_internal_profile_squared"] == 1.0 / (4.0 * math.pi)
    assert artifact["r_internal_profile"] == 1.0 / math.sqrt(4.0 * math.pi)


def test_Z_H_closes_only_from_canonical_profile_normalization_theorem():
    z_h = closure.derive_Z_H_from_profile_normalization_if_possible(ROOT)
    assert z_h["status"] == closure.DERIVED_CONDITIONAL_FROM_PROFILE_NORMALIZATION
    assert z_h["promoted_status"] == closure.DERIVED_CONDITIONAL
    assert z_h["value"] == 1.0
    assert z_h["source_theorem"] == closure.CANONICAL_PROFILE_NORMALIZATION_THEOREM
    assert z_h["Z_H_set_to_one_by_habit"] is False
    assert z_h["Z_H_set_to_one_by_theorem"] is True
    assert z_h["observed_Higgs_used"] is False


def test_kappa_H_remains_blocked_and_mu_H_is_not_identified():
    kappa = closure.derive_kappa_H_from_profile_hessian_if_possible(ROOT)
    assert kappa["status"] == closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM
    assert kappa["derived"] is False
    assert kappa["value"] is None
    assert kappa["source_theorem"] == closure.CANONICAL_PROFILE_HESSIAN_THEOREM
    assert kappa["observed_Higgs_used"] is False
    assert kappa["kappa_H_chosen_to_set_tau"] is False
    assert kappa["mu_H_identified_with_kappa_H"] is False
    assert "profile Hessian theorem identifying a numerical curvature" in kappa["missing_objects"]


def test_sigma_tau_symbolic_after_Z_H_closure_but_not_numeric():
    sigma_tau = closure.derive_sigma_tau_if_possible(ROOT)
    assert sigma_tau["Z_H_status"] == closure.DERIVED_CONDITIONAL
    assert sigma_tau["Z_H_value"] == 1.0
    assert sigma_tau["kappa_H_status"] == closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM
    assert sigma_tau["sigma_from_boundary_geometry"] == closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H
    assert sigma_tau["tau_from_boundary_geometry"] == closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H
    assert sigma_tau["sigma_formula"] == "sigma(kappa_H) = (1/2)*sqrt(kappa_H)"
    assert sigma_tau["tau_formula"] == "tau(kappa_H) = 2*pi/sqrt(kappa_H)"
    assert sigma_tau["sigma_derived"] is False
    assert sigma_tau["tau_derived"] is False
    assert sigma_tau["tau_numeric_computed"] is False
    assert sigma_tau["missing_objects"] == ["kappa_H"]


def test_charged_outputs_are_not_exported_without_tau_closure():
    charged = closure.compute_charged_outputs_at_tau_if_possible(ROOT)
    assert charged["exported"] is False
    assert charged["status"] == closure.NO_FIT_OUTPUT_BLOCKED_BY_KAPPA_H
    assert charged["tau_derived"] is False
    assert charged["missing_objects"] == ["kappa_H"]
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert (ROOT / "artifacts" / "tau_sigma_boundary_values_v1.json").exists()
        assert (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_local_v1.json").exists()
        assert (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_background_identity_v1.json").exists()
    else:
        assert not (ROOT / "artifacts" / "tau_sigma_boundary_values_v1.json").exists()
        assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_local_v1.json").exists()
        assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_background_identity_v1.json").exists()


def test_generated_artifacts_have_required_guardrails_and_single_blocker():
    for name in (
        "profile_normalization_hessian_closure_v1.json",
        "Z_H_profile_normalization_value_or_obstruction_v2.json",
        "kappa_H_profile_hessian_value_or_obstruction_v2.json",
        "tau_sigma_profile_scale_closure_v1.json",
    ):
        payload = load_artifact(name)
        assert payload["public_status_before_gate"] == closure.PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["observed_masses_used"] is False
        assert payload["observed_Higgs_used"] is False
        assert payload["observed_gauge_values_used"] is False
        assert payload["tau_fit_to_masses"] is False
        assert payload["sigma_fit_to_masses"] is False
        assert payload["radius_gate_status"] == closure.RADIUS_GATE_STATUS
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert load_artifact("profile_normalization_hessian_closure_v1.json")["remaining_blockers"] == []
        assert load_artifact("tau_sigma_profile_scale_closure_v1.json")["tau_formula"] == "1/(4*pi^(3/2))"
    else:
        assert load_artifact("profile_normalization_hessian_closure_v1.json")["remaining_blockers"] == ["kappa_H"]
        assert load_artifact("tau_sigma_profile_scale_closure_v1.json")["tau_formula"] == (
            "tau(kappa_H) = 2*pi/sqrt(kappa_H)"
        )


def test_central_artifacts_record_Z_H_closure_without_global_numerical_closure():
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    package = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    assert central["public_status_after_sprint"] == closure.PUBLIC_STATUS
    assert {
        "gate": "Z_H_profile_normalization",
        "status": closure.DERIVED_CONDITIONAL,
    } in central["promoted_statuses"]
    followup = central["gates"]["tau_sigma"]["targeted_followup_from_profile_normalization_hessian_closure"]
    assert followup["Z_H_value"] == 1.0
    assert followup["remaining_blockers"] == ["kappa_H"]
    open_params = package["sections"]["open_boundary_parameters"]
    assert open_params["Z_H_status"] == closure.DERIVED_CONDITIONAL
    assert open_params["Z_H_value"] == 1.0
    assert open_params["refined_open_blockers_after_profile_normalization"] == ["kappa_H"]
    assert open_params["comparison_ready"] is False


def test_source_does_not_import_empirical_closure_modules_or_observed_inputs():
    text = (ROOT / "src" / "profile_normalization_hessian_closure.py").read_text(encoding="utf-8")
    for token in (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "observed_mass_fixture",
        "target_ratio_fixture",
        "m_H_observed",
        "CKM",
        "PMNS",
    ):
        assert token not in text


def test_forbidden_claims_absent_from_new_status_section():
    text = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## Z_H Profile Normalization And kappa_H Hessian Closure"
    assert marker in text
    section = text.split(marker, 1)[1]
    for phrase in (
        "BHSM is proven",
        "BHSM replaces the Standard Model",
        "predicted the Higgs mass",
        "experimentally confirmed",
    ):
        assert phrase not in section


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
