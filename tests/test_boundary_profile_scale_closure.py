import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import boundary_profile_scale_closure as closure


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}
FORBIDDEN_PHRASES = (
    "BHSM is proven",
    "BHSM replaces the Standard Model",
    "predicted the Higgs mass",
    "experimentally confirmed",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_radius_symbols_are_disambiguated():
    rows = closure.disambiguate_radius_symbols(ROOT)
    by_symbol = {row.symbol: row for row in rows}
    assert by_symbol["r"].profile_radius_candidate is True
    assert by_symbol["r"].status == closure.BLOCKED_BY_MISSING_OBJECT
    assert by_symbol["R_H_Gpc"].profile_radius_candidate is False
    assert by_symbol["Lambda_squared"].profile_radius_candidate is False
    assert by_symbol["S"].profile_radius_candidate is False
    assert by_symbol["rho / collar depth"].profile_radius_candidate is False
    assert by_symbol["Lambda_BH / mu_ref"].profile_radius_candidate is False


def test_Z_H_and_kappa_H_are_not_derived_from_observed_higgs():
    z_h = closure.derive_Z_H_if_possible(repo_root=ROOT)
    kappa = closure.derive_kappa_H_if_possible(repo_root=ROOT)
    assert z_h["observed_Higgs_used"] is False
    assert kappa["observed_Higgs_used"] is False
    assert z_h["derived"] is False
    assert kappa["derived"] is False
    assert z_h["status"] == closure.OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH
    assert kappa["status"] == closure.OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH
    assert "observed" not in " ".join(z_h["source_trace"]).lower()
    assert "observed" not in " ".join(kappa["source_trace"]).lower()


def test_current_artifact_lists_exact_missing_objects_and_preserves_status():
    artifact = closure.build_boundary_profile_scale_closure_artifact(ROOT)
    assert artifact["public_status_before_gate"] == PUBLIC_STATUS
    assert artifact["public_status_after_gate"] == PUBLIC_STATUS
    assert artifact["boundary_profile_scale_closure"] == closure.BLOCKED_BY_MISSING_OBJECTS
    assert artifact["missing_objects"] == ["kappa_H", "Z_H", "r"]
    assert artifact["sigma_tau_result"]["missing_objects"] == ["kappa_H", "Z_H", "r"]
    assert artifact["official_predictions_changed"] is False
    assert artifact["empirical_derivation_inputs_used"] is False
    assert artifact["observed_masses_used"] is False
    assert artifact["tau_fit_to_masses"] is False
    assert artifact["sigma_fit_to_masses"] is False
    assert artifact["charged_outputs_at_tau_exported"] is False


def test_if_required_objects_exist_sigma_and_tau_formulas_apply():
    sources = {
        "kappa_H": closure.ScaleSource(
            "kappa_H",
            closure.DERIVED_CONDITIONAL,
            32.0,
            "test kappa",
            ("synthetic-test-source",),
            "test",
            (),
            "test only",
        ),
        "Z_H": closure.ScaleSource(
            "Z_H",
            closure.DERIVED_CONDITIONAL,
            8.0,
            "test Z",
            ("synthetic-test-source",),
            "test",
            (),
            "test only",
        ),
        "r": closure.ScaleSource(
            "r",
            closure.DERIVED_FIXED,
            2.0,
            "test r",
            ("synthetic-test-source",),
            "test",
            (),
            "test only",
        ),
    }
    result = closure.derive_sigma_tau_if_possible(sources)
    assert result["sigma_derived"] is True
    assert result["tau_derived"] is True
    assert result["sigma"] == 1.0
    assert result["tau"] == 1.0 / 16.0
    assert result["missing_objects"] == []


def test_generated_artifacts_have_required_guardrails():
    for name in (
        "boundary_profile_scale_closure_v1.json",
        "radius_symbol_disambiguation_v1.json",
        "Z_H_closure_or_obstruction_v1.json",
        "kappa_H_closure_or_obstruction_v1.json",
    ):
        payload = load_artifact(name)
        assert payload["public_status_before_gate"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["observed_masses_used"] is False
        assert payload["observed_Higgs_used"] is False
        assert payload["observed_gauge_values_used"] is False
        assert payload["tau_fit_to_masses"] is False
        assert payload["sigma_fit_to_masses"] is False


def test_no_charged_outputs_exported_without_boundary_tau():
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert (ROOT / "artifacts" / "tau_sigma_boundary_values_v1.json").exists()
        assert (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_local_v1.json").exists()
        assert (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_background_identity_v1.json").exists()
    else:
        assert not (ROOT / "artifacts" / "tau_sigma_boundary_values_v1.json").exists()
        assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_local_v1.json").exists()
        assert not (ROOT / "artifacts" / "charged_outputs_at_boundary_tau_A_background_identity_v1.json").exists()


def test_pr46_artifacts_record_targeted_followup_without_promotion():
    tau = load_artifact("tau_sigma_boundary_derivation_closure_or_obstruction_v1.json")
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    package = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    assert tau["targeted_followup"]["targeted_first_blocker_from_PR_46"] is True
    assert central["gates"]["tau_sigma"]["targeted_followup"]["targeted_first_blocker_from_PR_46"] is True
    if (ROOT / "artifacts" / "internal_berger_radius_selection_theorem_v1.json").exists():
        expected = [
            {
                "gate": "internal_berger_radius_selection_theorem",
                "status": "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
            },
            {"gate": "r_internal_profile", "status": "DERIVED_CONDITIONAL"},
        ]
        if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
            expected.append({"gate": "Z_H_profile_normalization", "status": "DERIVED_CONDITIONAL"})
        if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
            expected.extend(
                [
                    {"gate": "kappa_H_profile_hessian", "status": "DERIVED_CONDITIONAL"},
                    {"gate": "profile_scale_closure", "status": "DERIVED_CONDITIONAL"},
                    {
                        "gate": "charged_outputs_at_boundary_tau",
                        "status": "NO_FIT_OUTPUT_CANDIDATE_EXPORTED",
                    },
                ]
            )
        assert central["promoted_statuses"] == expected
        followup = central["gates"]["tau_sigma"]["targeted_followup_from_author_radius_selection"]
        assert followup["remaining_blockers"] == ["Z_H", "kappa_H"]
        if (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
            profile_followup = central["gates"]["tau_sigma"][
                "targeted_followup_from_profile_normalization_hessian_closure"
            ]
            if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
                assert central["gates"]["tau_sigma"]["targeted_followup_from_boundary_no_fit_package_completion"][
                    "remaining_blockers"
                ] == []
            else:
                assert profile_followup["remaining_blockers"] == ["kappa_H"]
    else:
        assert central["promoted_statuses"] == []
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert package["sections"]["open_boundary_parameters"]["status"] == closure.DERIVED_CONDITIONAL
        assert package["sections"]["open_boundary_parameters"]["open_blockers"] == []
    else:
        assert package["sections"]["open_boundary_parameters"]["status"] == closure.BLOCKED_BY_MISSING_OBJECTS
        assert package["sections"]["open_boundary_parameters"]["open_blockers"] == ["kappa_H", "Z_H", "r"]


def test_forbidden_claims_absent_from_new_docs_and_artifacts():
    current_status = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## Boundary/Profile Scale Closure Assault"
    assert marker in current_status
    new_status_section = current_status.split(marker, 1)[1]
    paths = [
        ROOT / "artifacts" / "boundary_profile_scale_closure_v1.json",
        ROOT / "artifacts" / "radius_symbol_disambiguation_v1.json",
        ROOT / "artifacts" / "Z_H_closure_or_obstruction_v1.json",
        ROOT / "artifacts" / "kappa_H_closure_or_obstruction_v1.json",
    ]
    combined = new_status_section + "\n" + "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in combined


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
