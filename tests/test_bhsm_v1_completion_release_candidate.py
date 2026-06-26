import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import bhsm_external_comparison_package as completion


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


def test_completion_manifest_exists_and_references_core_artifacts():
    manifest = load_artifact("BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json")
    assert manifest["release_candidate"] == "BHSM_COMPLETE_V1"
    assert manifest["internal_boundary_package"] == completion.INTERNAL_COMPLETE
    assert manifest["boundary_no_fit_prediction_package"] == completion.INTERNAL_COMPLETE
    assert manifest["external_empirical_comparison_package"] == completion.COMPARISON_LAYER
    assert manifest["external_empirical_comparison_status"] == "DATA_OPTIONAL_OR_DATA_ABSENT"
    assert manifest["empirical_derivation_inputs_used"] is False
    assert manifest["boundary_predictions_modified_by_comparison"] is False
    assert manifest["official_predictions_changed"] is False
    assert manifest["public_status"] == completion.PUBLIC_STATUS
    assert set(completion.CORE_PR52_ARTIFACTS).issubset(set(manifest["core_artifacts"]))
    for name in completion.CORE_PR52_ARTIFACTS:
        assert (ROOT / "artifacts" / name).exists()


def test_external_target_schema_is_comparison_only_and_data_absent():
    schema = load_artifact("BHSM_external_comparison_target_schema_v1.json")
    assert schema["external_empirical_comparison_package"] == completion.COMPARISON_LAYER
    assert schema["external_targets_present"] is False
    assert schema["comparison_result"] == completion.DATA_ABSENT
    for family in completion.TARGET_FAMILIES:
        row = schema["target_families"][family]
        for key in (
            "source",
            "date_or_version",
            "units",
            "scheme",
            "scale",
            "covariance_available",
            "comparison_only",
            "not_derivation_input",
        ):
            assert key in row["required_metadata"]
        assert row["comparison_only"] is True
        assert row["not_derivation_input"] is True


def test_external_transport_layer_keeps_internal_completion_unblocked():
    transport = load_artifact("BHSM_external_transport_layer_v1.json")
    assert transport["internal_boundary_transport"]["T_boundary_to_boundary"] == 1
    assert transport["internal_boundary_transport"]["status"] == "DERIVED_FIXED_IDENTITY_AT_BHSM_BOUNDARY_SCALE"
    assert transport["external_empirical_transport"]["status"] == "OPEN_COMPARISON_LAYER"
    assert transport["external_empirical_transport"]["not_derivation_input"] is True
    assert transport["external_transport_population"] == "DATA_OR_SCHEME_DEPENDENT"
    assert transport["internal_boundary_package_complete"] is True


def test_falsification_gates_exist_and_data_absent_is_not_failure():
    gates = load_artifact("BHSM_falsification_gates_v1.json")
    assert gates["profile_scale_identity_gate"]["status"] == "PASSED_INTERNAL_IDENTITY"
    assert gates["no_empirical_derivation_gate"]["empirical_derivation_inputs_used"] is False
    assert gates["boundary_package_integrity_gate"]["status"] == "PASSED"
    assert gates["comparison_layer_separation_gate"]["external_comparison_can_modify_internal_constants"] is False
    assert gates["charged_sector_comparison_gate"]["status"] == completion.NOT_EVALUATED_DATA_ABSENT
    assert gates["CKM_PMNS_CP_comparison_gate"]["status"] == completion.NOT_EVALUATED_DATA_ABSENT
    assert gates["cosmology_DESI_gate"]["status"] == completion.NOT_EVALUATED_DATA_ABSENT


def test_external_comparison_package_is_data_absent_and_one_way():
    payload = load_artifact("BHSM_external_empirical_comparison_package_v1.json")
    assert payload["external_empirical_comparison_package"] == completion.COMPARISON_LAYER
    assert payload["external_targets_present"] is False
    assert payload["comparison_result"] == completion.DATA_ABSENT
    assert payload["empirical_derivation_inputs_used"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["comparison_data_required_for_internal_completion"] is False
    assert payload["residuals"]["residuals"] == []
    assert payload["chi2"]["chi2_computed"] is False


def test_prediction_package_and_ledgers_mark_internal_complete_external_open():
    prediction = load_artifact("BHSM_prediction_package_skeleton_v1.json")
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    claims = load_artifact("full_BHSM_claim_status_table_v2.json")
    assert prediction["package_status"] == "BHSM_COMPLETE_V1_RELEASE_CANDIDATE"
    assert prediction["BHSM_boundary_no_fit_prediction_package"] == completion.INTERNAL_COMPLETE
    assert prediction["external_empirical_comparison_package"] == completion.COMPARISON_LAYER
    assert prediction["external_empirical_comparison_result"] == completion.DATA_ABSENT
    statuses = open_gate["statuses"]
    assert statuses["BHSM_COMPLETE_V1_RELEASE_CANDIDATE"] == "EXPORTED"
    assert statuses["BHSM_internal_boundary_package"] == completion.INTERNAL_COMPLETE
    assert statuses["external_empirical_comparison_package"] == completion.COMPARISON_LAYER
    closed_terms = {
        "boundary-derived tau/sigma",
        "charged outputs at boundary tau",
        "boundary no-fit prediction package",
        "kappa_H",
        "Z_H",
    }
    assert closed_terms.isdisjoint(set(open_gate["remaining_open_blockers"]))
    assert "external target data population" in open_gate["remaining_open_blockers"]
    assert any(row["claim"] == "BHSM complete v1 release candidate" for row in claims["claim_statuses"])


def test_docs_and_readme_use_correct_status_split_without_forbidden_claims():
    paths = [
        ROOT / "README.md",
        ROOT / "docs" / "current_status.md",
        ROOT / "docs" / "claim_boundaries.md",
        ROOT / "docs" / "falsification_criteria.md",
        ROOT / "docs" / "reproducibility.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "complete internal no-fit boundary prediction package" in combined
    assert "separate comparison-only layer" in combined
    assert "externally unevaluated" in combined
    assert "Empirical data are not used to derive BHSM constants" in combined
    for phrase in (
        "BHSM is empirically proven",
        "BHSM fully replaces the Standard Model experimentally",
        "BHSM is validated by DESI",
        "BHSM predicts observed masses exactly",
    ):
        assert phrase not in combined


def test_source_does_not_import_prediction_or_residual_feedback_modules():
    text = (ROOT / "src" / "bhsm_external_comparison_package.py").read_text(encoding="utf-8")
    for token in (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "target_ratio_fixture",
        "observed_mass_fixture",
    ):
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
