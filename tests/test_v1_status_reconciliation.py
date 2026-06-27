import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CURRENT_STATUS = (
    "BHSM v1.0.0 internal boundary no-fit package complete/exported; "
    "external empirical comparison layer separate/open"
)
OLD_STATUS = "structural architecture integrated conditional; numerical closure open"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


def test_current_public_docs_use_v1_status_split() -> None:
    readme = read("docs/archive/README_status_history_pre_v0_7.md")
    current = read("docs/current_status.md")
    boundaries = read("docs/claim_boundaries.md")

    assert f"Current status: {CURRENT_STATUS}." in readme
    assert f"Current status: {CURRENT_STATUS}." in current
    assert f"Current status: {CURRENT_STATUS}." in boundaries

    first_readme_block = "\n".join(readme.splitlines()[:25])
    assert OLD_STATUS not in first_readme_block
    assert "Historical pre-v1.0.0" in readme
    assert "External empirical comparison layer: SEPARATE / OPEN." in readme
    assert "External empirical comparison layer: SEPARATE / OPEN." in current
    assert "External empirical comparison layer: SEPARATE / OPEN." in boundaries


def test_release_manifests_use_reconciled_machine_status() -> None:
    for relative in [
        "artifacts/BHSM_v1_release_manifest.json",
        "artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json",
    ]:
        payload = load(relative)
        assert payload["public_status"] == CURRENT_STATUS
        assert payload["BHSM_internal_boundary_package"] == "COMPLETE_EXPORTED"
        assert payload["BHSM_boundary_no_fit_prediction_package"] == "COMPLETE_EXPORTED"
        assert payload["external_empirical_comparison_layer"] == (
            "IMPLEMENTED_COMPARISON_ONLY_LAYER"
        )
        assert payload["external_empirical_comparison_status"] == "OPEN_SEPARATE_LAYER"
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False


def test_current_open_gate_ledger_no_longer_lists_exported_boundary_package_as_open() -> None:
    payload = load("artifacts/full_BHSM_open_gate_ledger_v2.json")
    statuses = payload["statuses"]

    assert payload["public_status"] == CURRENT_STATUS
    assert statuses["BHSM_internal_boundary_package"] == "COMPLETE_EXPORTED"
    assert statuses["BHSM_boundary_no_fit_prediction_package"] == "COMPLETE_EXPORTED"
    assert statuses["tau_sigma_gate"] == "DERIVED_CONDITIONAL_EXPORTED"
    assert statuses["charged_no_fit_outputs"] == "COMPLETE_EXPORTED"
    assert statuses["common_scale_transport_population"] == (
        "BOUNDARY_TRANSPORT_IDENTITY_EXPORTED"
    )
    assert statuses["PMNS_numerical_output"] == "PMNS_BOUNDARY_NO_FIT_OUTPUT_EXPORTED"
    assert statuses["CKM_numerical_output"] == "CKM_BOUNDARY_NO_FIT_OUTPUT_EXPORTED"
    assert statuses["CP_numerical_output"] == "CP_BOUNDARY_HOLONOMY_OUTPUT_EXPORTED"
    assert statuses["external_empirical_comparison_status"] == "OPEN_SEPARATE_LAYER"
    assert statuses["empirical_derivation_inputs_used"] is False
    assert statuses["boundary_predictions_modified_by_comparison"] is False

    blockers = " | ".join(payload["remaining_open_blockers"]).lower()
    for stale in [
        "charged lepton operator at boundary-derived tau",
        "final up/down charged operators at boundary-derived tau",
        "ckm numerical lock",
        "closed ckm operator",
        "closed pmns operator",
        "common-scale transport population",
    ]:
        assert stale not in blockers
    assert payload["remaining_external_open_items"]


def test_claim_status_table_uses_internal_complete_external_open_split() -> None:
    payload = load("artifacts/full_BHSM_claim_status_table_v2.json")
    assert payload["public_status"] == CURRENT_STATUS
    assert payload["BHSM_internal_boundary_package"] == "COMPLETE_EXPORTED"
    assert payload["BHSM_boundary_no_fit_prediction_package"] == "COMPLETE_EXPORTED"
    assert payload["external_empirical_comparison_status"] == "OPEN_SEPARATE_LAYER"
    assert payload["empirical_derivation_inputs_used"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False

    rows = {row["claim"]: row for row in payload["claim_statuses"]}
    assert rows["BHSM boundary no-fit prediction package"]["status"] == "COMPLETE_EXPORTED"
    assert rows["External empirical validation"]["status"] == "OPEN_SEPARATE_LAYER"
    assert "empirical validation is claimed" in rows["External empirical validation"]["boundary"]


def test_reconciliation_does_not_introduce_validation_or_fake_doi_claims() -> None:
    combined = "\n".join(
        [
            read("docs/archive/README_status_history_pre_v0_7.md"),
            read("docs/current_status.md"),
            read("docs/claim_boundaries.md"),
            read("artifacts/BHSM_v1_release_manifest.json"),
            read("artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json"),
        ]
    )
    forbidden = [
        "BHSM is empirically proven",
        "BHSM has experimentally replaced the Standard Model",
        "BHSM is validated by DESI",
        "Observed masses were used to derive constants",
        "External empirical comparison is complete",
        "Zenodo DOI assigned",
    ]
    for phrase in forbidden:
        assert phrase not in combined
    assert "PENDING_ZENODO_RELEASE" in combined
