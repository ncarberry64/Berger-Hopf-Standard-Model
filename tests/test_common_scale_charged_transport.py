import hashlib
import json
import sys
from math import isclose, log
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import common_scale_charged_transport as transport


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
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


def test_same_sector_log_ratios_and_transport_are_formulaic():
    assert isclose(transport.transported_yukawa(2.0, 3.0), 6.0)
    ratios = transport.same_sector_log_ratios([8.0, 4.0, 1.0])
    assert isclose(ratios["ln_y_heavy_over_middle"], log(2.0))
    assert isclose(ratios["ln_y_middle_over_light"], log(4.0))
    assert isclose(ratios["ln_y_heavy_over_light"], log(8.0))
    transported = transport.transported_same_sector_ratios([8.0, 4.0, 1.0], [1.0, 2.0, 4.0])
    assert isclose(transported["ln_y_heavy_over_middle"], log(1.0))
    assert isclose(transported["ln_y_middle_over_light"], log(2.0))


def test_transport_validation_rejects_forbidden_feedback_configs():
    validation = transport.validate_transport_config(
        {
            "mixed_pole_running_comparison_allowed": True,
            "transport_factors_fit_to_residuals": True,
            "observed_masses_used_as_derivation_inputs": True,
            "empirical_targets_used": True,
            "fit_transport_to_residuals": True,
        }
    )
    assert validation.valid is False
    assert validation.mixed_pole_running_comparison_allowed is True
    assert validation.transport_factors_fit_to_residuals is True
    assert validation.observed_masses_used_as_derivation_inputs is True
    assert validation.empirical_targets_used is True
    assert "fit_transport_to_residuals" in validation.forbidden_keys_found


def test_transport_decomposition_includes_required_factors():
    template = transport.build_transport_decomposition_template()
    factors = template["transport_decomposition"]["T_f_i"]
    assert factors == [
        "T_gauge,f",
        "T_Yukawa,self,f_i",
        "T_threshold,f_i",
        "T_scheme,f",
    ]
    for sector in ("lepton", "up", "down"):
        meta = template["same_sector_cancellation"][sector]
        assert meta["ordinary_gauge_running_cancels_in_same_sector_ratios"] is True
        assert meta["cancellation_is_structural_not_mass_fit"] is True


def test_common_scale_target_schema_marks_empirical_values_as_comparison_only():
    schema = load_artifact("common_scale_charged_target_schema_v1.json")
    assert schema["empirical_targets_used"] is False
    assert schema["observed_masses_used_as_derivation_inputs"] is False
    for rows in schema["target_rows"].values():
        for row in rows:
            assert row["input_role"] == "EMPIRICAL_COMPARISON_INPUT"
            assert row["derivation_input"] is False
            assert row["value"] is None
            assert row["populated"] is False


def test_transport_artifacts_preserve_guardrails():
    for name in (
        "common_scale_charged_transport_interface_v1.json",
        "charged_transport_decomposition_template_v1.json",
        "common_scale_charged_target_schema_v1.json",
        "BHSM_prediction_package_skeleton_v1.json",
    ):
        payload = load_artifact(name)
        if name == "BHSM_prediction_package_skeleton_v1.json" and (
            ROOT / "artifacts" / "BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json"
        ).exists():
            assert payload["public_status"] == (
                "internal boundary no-fit package complete; external empirical comparison layer separate/open"
            )
        else:
            assert payload["public_status"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["empirical_targets_used"] is False
        assert payload["observed_masses_used_as_derivation_inputs"] is False
        assert payload["mixed_pole_running_comparison_allowed"] is False
        assert payload["transport_factors_fit_to_residuals"] is False
        assert payload["charged_precision_closure"] == "OPEN"


def test_prediction_package_skeleton_has_required_sections_and_no_empirical_inputs():
    payload = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    sections = payload["sections"]
    required = (
        "charged_same_sector_ratios",
        "charged_cross_sector_ratios",
        "neutral_mass_splittings",
        "PMNS_angles_and_phase",
        "CKM_angles_and_phase",
        "CP_Jarlskog_invariants",
        "gauge_couplings",
        "sin2_theta_W",
        "W_Z_Higgs_scale",
        "open_boundary_parameters",
        "claim_status",
        "forbidden_feedback",
    )
    for section in required:
        assert section in sections
        entry = sections[section]
        for key in ("status", "source_artifact", "uses_empirical_input", "comparison_ready", "open_blockers"):
            assert key in entry
        assert entry["uses_empirical_input"] is False
    assert sections["charged_same_sector_ratios"]["comparison_ready"] is False
    assert sections["charged_same_sector_ratios"]["source_artifact"] == (
        "artifacts/tau_response_curves_A_background_identity_v1.json"
    )


def test_open_gate_and_claim_status_are_updated_without_numerical_closure():
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    statuses = open_gate["statuses"]
    assert statuses["common_scale_charged_transport_interface"] == "IMPLEMENTED_CONDITIONAL"
    assert statuses["charged_transport_decomposition_template"] == "EXPORTED"
    assert statuses["common_scale_target_schema"] == "EXPORTED_EMPTY_COMPARISON_SCHEMA"
    assert statuses["prediction_package_skeleton"] == "EXPORTED_NOT_COMPARISON_READY"
    assert statuses["mixed_pole_running_comparison"] == "FORBIDDEN"
    assert statuses["transport_factors_fit_to_residuals"] == "FORBIDDEN"
    assert statuses["charged_precision_closure"] == "OPEN"
    assert statuses["oriented_jet_heat_response"] == "STRUCTURALLY_SUPPORTED_CANDIDATE"
    assert statuses["universal_tau_sigma_scaffold"] == "IMPLEMENTED_CONDITIONAL"
    claims = load_artifact("full_BHSM_claim_status_table_v2.json")
    rows = {row["claim"]: row["status"] for row in claims["claim_statuses"]}
    assert rows["Common-scale charged transport interface"] == "IMPLEMENTED_CONDITIONAL"
    assert rows["Comparison-ready prediction package skeleton"] == "EXPORTED_NOT_COMPARISON_READY"


def test_source_does_not_import_empirical_closure_modules():
    text = (ROOT / "src" / "common_scale_charged_transport.py").read_text(encoding="utf-8")
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
