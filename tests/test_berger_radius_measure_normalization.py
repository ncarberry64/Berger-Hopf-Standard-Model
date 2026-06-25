import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import berger_radius_measure_normalization as radius


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
    "berger_radius_measure_normalization_v1.json",
    "internal_radius_normalization_forks_v1.json",
    "berger_measure_domain_v1.json",
    "internal_profile_radius_closure_or_obstruction_v2.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_all_radius_like_symbols_are_classified_and_cosmology_is_not_used():
    rows = radius.collect_radius_measure_sources(ROOT)
    assert set(rows) == {
        "r_internal_profile",
        "R_H_cosmological",
        "rho_star_collar_depth",
        "Lambda_BH_matching_scale",
        "Lambda_squared_overlap",
        "S_overlap_width",
    }
    assert rows["r_internal_profile"].used_as_internal_profile_r is True
    assert rows["R_H_cosmological"].value == 24.0
    assert rows["R_H_cosmological"].used_as_internal_profile_r is False
    assert rows["R_H_cosmological"].status == radius.REJECTED_BY_REPO_CONVENTIONS


def test_normalization_forks_are_explicit_and_unselected():
    forks = radius.build_radius_normalization_forks(ROOT)
    by_id = {fork.route_id: fork for fork in forks}
    assert set(by_id) == {
        "unit_internal_radius",
        "lambda_radius",
        "overlap_width_radius",
        "berger_volume_normalization",
        "collar_depth_matching",
    }
    assert by_id["unit_internal_radius"].status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    assert by_id["lambda_radius"].status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    assert by_id["overlap_width_radius"].status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    assert by_id["berger_volume_normalization"].status == radius.NORMALIZATION_FORK_OPEN
    assert by_id["collar_depth_matching"].status == radius.NORMALIZATION_FORK_OPEN
    for fork in forks:
        assert fork.selected is False
        assert fork.rejection_or_blocker == radius.MISSING_SELECTION_THEOREM


def test_unit_lambda_overlap_routes_are_not_promoted_without_theorem():
    assert radius.derive_unit_radius_if_repo_implies(ROOT).status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    assert radius.derive_lambda_radius_if_repo_implies(ROOT).status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    assert radius.derive_overlap_radius_if_repo_implies(ROOT).status == radius.STRUCTURALLY_SUPPORTED_CANDIDATE
    selection = radius.select_unique_radius_normalization_if_possible(ROOT)
    assert selection["status"] == radius.NORMALIZATION_FORK_OPEN
    assert selection["selected_route"] is None
    assert selection["r_internal_profile"] is None
    assert selection["missing_theorem"] == radius.MISSING_SELECTION_THEOREM


def test_berger_volume_route_does_not_assume_wrong_sigma_convention():
    fork = radius.derive_berger_volume_measure_if_possible(ROOT)
    assert fork.status == radius.NORMALIZATION_FORK_OPEN
    assert fork.candidate_value is None
    assert "depends on the sigma_i/Maurer-Cartan convention" in fork.candidate_formula
    assert "Does not assume SU(2), unit S^3, Hopf-coordinate" in fork.notes


def test_collar_depth_route_remains_fork_open():
    fork = radius.derive_collar_matched_radius_if_possible(ROOT)
    assert fork.status == radius.NORMALIZATION_FORK_OPEN
    assert fork.candidate_value is None
    assert "rho_*" in fork.candidate_formula
    assert fork.selected is False


def test_measure_domain_remains_fork_open_and_profile_normalization_not_supported():
    measure = radius.build_berger_measure_domain_artifact(ROOT)
    assert measure["dmu_Berger_domain_status"] == radius.NORMALIZATION_FORK_OPEN
    assert measure["profile_normalization_supported"] is False
    assert measure["berger_measure_domain"]["missing_theorem"] == radius.MISSING_SELECTION_THEOREM


def test_radius_measure_closure_names_single_missing_theorem():
    artifact = radius.build_radius_measure_closure_or_obstruction_artifact(ROOT)
    assert artifact["public_status_before_gate"] == PUBLIC_STATUS
    assert artifact["r_internal_profile_status"] == radius.NORMALIZATION_FORK_OPEN
    assert artifact["r_internal_profile_value"] is None
    assert artifact["selected_route"] is None
    assert artifact["missing_theorem"] == radius.MISSING_SELECTION_THEOREM
    assert artifact["dmu_Berger_domain_status"] == radius.NORMALIZATION_FORK_OPEN
    assert artifact["Z_H_updated"] is False
    assert artifact["sigma_derived"] is False
    assert artifact["tau_derived"] is False
    assert artifact["charged_outputs_at_tau_exported"] is False
    assert artifact["official_predictions_changed"] is False
    assert artifact["empirical_derivation_inputs_used"] is False


def test_generated_artifacts_have_guardrails_and_author_followup_radius_value_file():
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
    value_path = ROOT / "artifacts" / "internal_profile_radius_value_v1.json"
    if (ROOT / "artifacts" / "internal_berger_radius_selection_theorem_v1.json").exists():
        value = load_artifact("internal_profile_radius_value_v1.json")
        assert value_path.exists()
        assert value["radius_selected_by"] == "AUTHOR_SUPPLIED_BHSM_OVERLAP_NORMALIZATION"
        assert value["r_internal_profile_status"] == "DERIVED_CONDITIONAL"
    else:
        assert not value_path.exists()


def test_previous_artifacts_record_pr48_followup_without_breaking_legacy_blockers():
    boundary = load_artifact("boundary_profile_scale_closure_v1.json")
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    package = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    assert boundary["targeted_followup_from_PR48"]["missing_theorem"] == radius.MISSING_SELECTION_THEOREM
    assert boundary["missing_objects"] == ["kappa_H", "Z_H", "r"]
    assert boundary["refined_missing_objects_from_PR48_followup"] == ["r_internal_profile", "Z_H", "kappa_H"]
    assert central["gates"]["tau_sigma"]["targeted_followup_from_PR48"]["missing_theorem"] == (
        radius.MISSING_SELECTION_THEOREM
    )
    if (ROOT / "artifacts" / "internal_berger_radius_selection_theorem_v1.json").exists():
        assert central["promoted_statuses"] == [
            {
                "gate": "internal_berger_radius_selection_theorem",
                "status": "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
            },
            {"gate": "r_internal_profile", "status": "DERIVED_CONDITIONAL"},
        ]
        assert central["gates"]["tau_sigma"]["targeted_followup_from_author_radius_selection"][
            "remaining_blockers"
        ] == ["Z_H", "kappa_H"]
        assert package["sections"]["open_boundary_parameters"]["refined_open_blockers_after_radius_selection"] == [
            "Z_H",
            "kappa_H",
        ]
    else:
        assert central["promoted_statuses"] == []
    assert package["sections"]["open_boundary_parameters"]["open_blockers"] == ["kappa_H", "Z_H", "r"]
    assert package["sections"]["open_boundary_parameters"]["comparison_ready"] is False


def test_Z_H_is_not_set_to_one_and_tau_sigma_not_fit():
    artifact = load_artifact("berger_radius_measure_normalization_v1.json")
    assert artifact["Z_H_updated"] is False
    assert artifact["tau_fit_to_masses"] is False
    assert artifact["sigma_fit_to_masses"] is False
    assert artifact["observed_masses_used"] is False


def test_new_status_section_has_no_forbidden_claims():
    text = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## Internal Berger Radius And Measure Normalization Assault"
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
    text = (ROOT / "src" / "berger_radius_measure_normalization.py").read_text(encoding="utf-8")
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
