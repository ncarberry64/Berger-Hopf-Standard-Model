import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numerical_gate_closure_assault as assault
import tau_sigma_numerical_gate_closure as tau_gate


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}
ALLOWED_STATUSES = {
    "OPEN_LOCALIZABLE",
    "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
    "BLOCKED_BY_MISSING_TRANSPORT_OBJECTS",
    "STRONGLY_SUPPORTED_CANDIDATE",
    "PMNS_BLOCKED_BY_NEUTRAL_OPERATOR_OPEN",
    "CKM_BLOCKED_BY_UP_OPERATOR_OPEN",
    "CP_NUMERICAL_CLOSURE_OPEN",
    "BLOCKED_BY_MISSING_OBJECTS",
    "MOCK_OR_SCAFFOLD_ONLY",
    "NO_FIT_OUTPUT_CANDIDATE_EXPORTED",
}
EXPECTED_AUTHOR_RADIUS_PROMOTIONS = [
    {
        "gate": "internal_berger_radius_selection_theorem",
        "status": "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
    },
    {"gate": "r_internal_profile", "status": "DERIVED_CONDITIONAL"},
]
EXPECTED_PROFILE_NORMALIZATION_PROMOTION = {
    "gate": "Z_H_profile_normalization",
    "status": "DERIVED_CONDITIONAL",
}
EXPECTED_BOUNDARY_NO_FIT_PROMOTIONS = [
    {"gate": "kappa_H_profile_hessian", "status": "DERIVED_CONDITIONAL"},
    {"gate": "profile_scale_closure", "status": "DERIVED_CONDITIONAL"},
    {"gate": "charged_outputs_at_boundary_tau", "status": "NO_FIT_OUTPUT_CANDIDATE_EXPORTED"},
]


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_tau_sigma_refuses_to_invent_missing_boundary_objects():
    artifact = tau_gate.build_tau_sigma_closure_or_obstruction_artifact(ROOT)
    assert artifact["status"] == "OPEN_LOCALIZABLE"
    assert artifact["sigma_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
    assert artifact["tau_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
    assert artifact["sigma_result"]["value"] is None
    assert artifact["tau_result"]["value"] is None
    for item in ("kappa_H", "Z_H", "r"):
        assert item in artifact["missing_objects"]


def test_tau_sigma_artifact_records_exact_missing_objects():
    artifact = load_artifact("tau_sigma_boundary_derivation_closure_or_obstruction_v1.json")
    assert artifact["public_status_before_gate"] == PUBLIC_STATUS
    assert artifact["official_predictions_changed"] is False
    assert artifact["empirical_derivation_inputs_used"] is False
    assert artifact["observed_masses_used"] is False
    assert artifact["target_ratios_used"] is False
    assert artifact["missing_objects"] == ["kappa_H", "Z_H", "r"]


def test_central_report_has_all_gates_and_no_empirical_derivation_inputs():
    report = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    assert report["public_status_before_sprint"] == PUBLIC_STATUS
    assert report["public_status_after_sprint"] == PUBLIC_STATUS
    assert report["official_predictions_changed"] is False
    assert report["empirical_derivation_inputs_used"] is False
    for gate in (
        "tau_sigma",
        "charged_outputs_at_tau",
        "common_scale_transport",
        "neutral_parameters",
        "PMNS",
        "CKM",
        "CP",
        "Higgs_EW",
        "cosmology_DESI",
    ):
        assert gate in report["gates"]
        assert report["gates"][gate]["status"] in ALLOWED_STATUSES


def test_gate_specific_obstruction_artifacts_preserve_guardrails():
    for name in (
        "common_scale_transport_closure_or_obstruction_v1.json",
        "neutral_parameter_closure_or_obstruction_v1.json",
        "PMNS_obstruction_v1.json",
        "CKM_obstruction_v1.json",
        "CP_obstruction_v1.json",
        "Higgs_EW_closure_or_obstruction_v1.json",
        "hyperspherical_cosmology_desi_pipeline_v1.json",
    ):
        payload = load_artifact(name)
        assert payload["official_predictions_changed"] is False
        assert payload["empirical_derivation_inputs_used"] is False
    assert load_artifact("common_scale_transport_closure_or_obstruction_v1.json")["status"] == (
        "BLOCKED_BY_MISSING_TRANSPORT_OBJECTS"
    )
    assert load_artifact("neutral_parameter_closure_or_obstruction_v1.json")["status"] == (
        "STRONGLY_SUPPORTED_CANDIDATE"
    )
    assert load_artifact("hyperspherical_cosmology_desi_pipeline_v1.json")["actual_DESI_data_used"] is False
    assert load_artifact("hyperspherical_cosmology_desi_pipeline_v1.json")["DESI_validation_claimed"] is False


def test_prediction_package_is_not_marked_comparison_ready():
    package = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    assert package["official_predictions_changed"] is False
    assert package["empirical_derivation_inputs_used"] is False
    for section in package["sections"].values():
        assert section["uses_empirical_input"] is False
        assert section["comparison_ready"] is False
    assert package["package_status"] == "EXPORTED_NOT_COMPARISON_READY"


def test_promoted_statuses_require_source_artifacts():
    report = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    if (ROOT / "artifacts" / "internal_berger_radius_selection_theorem_v1.json").exists():
        expected = list(EXPECTED_AUTHOR_RADIUS_PROMOTIONS)
        if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
            expected.append(EXPECTED_PROFILE_NORMALIZATION_PROMOTION)
        if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
            expected.extend(EXPECTED_BOUNDARY_NO_FIT_PROMOTIONS)
        assert report["promoted_statuses"] == expected
        followup = report["gates"]["tau_sigma"]["targeted_followup_from_author_radius_selection"]
        assert followup["source_artifact"] == "artifacts/internal_berger_radius_selection_theorem_v1.json"
        assert followup["r_internal_profile_status"] == "DERIVED_CONDITIONAL"
        assert followup["remaining_blockers"] == ["Z_H", "kappa_H"]
        if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
            profile_followup = report["gates"]["tau_sigma"][
                "targeted_followup_from_profile_normalization_hessian_closure"
            ]
            assert profile_followup["Z_H_value"] == 1.0
            if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
                package_followup = report["gates"]["tau_sigma"][
                    "targeted_followup_from_boundary_no_fit_package_completion"
                ]
                assert package_followup["remaining_blockers"] == []
            else:
                assert profile_followup["remaining_blockers"] == ["kappa_H"]
    else:
        assert report["promoted_statuses"] == []
    for row in report["blocked_gates"]:
        assert row["status"] in ALLOWED_STATUSES


def test_open_gate_ledger_records_assault_statuses_without_official_change():
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    statuses = open_gate["statuses"]
    assert open_gate["official_predictions_changed"] is False
    assert statuses["numerical_gate_closure_assault"] == "RAN"
    assert statuses["tau_sigma_gate"] == "OPEN_LOCALIZABLE"
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert statuses["charged_no_fit_outputs"] == "NO_FIT_OUTPUT_CANDIDATE_EXPORTED"
    else:
        assert statuses["charged_no_fit_outputs"] == "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION"
    assert statuses["common_scale_transport_population"] == "BLOCKED_BY_MISSING_TRANSPORT_OBJECTS"
    assert statuses["neutral_parameter_derivation"] == "OPEN_LOCALIZABLE"
    assert statuses["empirical_derivation_inputs_used"] is False
    assert statuses["official_predictions"] == "UNCHANGED"


def test_sources_do_not_import_empirical_closure_modules():
    combined = "\n".join(
        (ROOT / "src" / name).read_text(encoding="utf-8")
        for name in (
            "tau_sigma_numerical_gate_closure.py",
            "common_scale_transport_closure_audit.py",
            "neutral_parameter_closure_audit.py",
            "numerical_gate_closure_assault.py",
        )
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "observed_mass_fixture",
        "target_ratio_fixture",
    )
    for token in blocked:
        assert token not in combined


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
