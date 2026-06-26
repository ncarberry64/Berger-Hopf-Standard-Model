import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import full_architecture_freeze_status as freeze


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
V1_CURRENT_STATUS = (
    "BHSM v1.0.0 internal boundary no-fit package complete/exported; "
    "external empirical comparison layer separate/open"
)
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def squash(text: str) -> str:
    return " ".join(text.split())


def test_architecture_freeze_artifact_preserves_status_and_sectors():
    payload = load_artifact("full_BHSM_architecture_freeze_v1.json")
    assert payload["public_status"] == PUBLIC_STATUS
    assert payload["official_predictions_changed"] is False
    for sector in freeze.ARCHITECTURE_SECTORS:
        assert sector in payload["architecture_sectors"]
    assert payload["charged_status"]["K_collar_stack_verdict"] == (
        "STACK_COLLAR_REJECTED_AS_PRIMARY"
    )
    assert payload["charged_status"][
        "minimal_positive_diagonal_K_collar_as_primary_charged_precision_route"
    ] == "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
    assert payload["charged_status"]["charged_precision_closure"] == "OPEN"


def test_readme_and_status_docs_preserve_public_status_without_overclaiming():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    current = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    boundaries = (ROOT / "docs" / "claim_boundaries.md").read_text(encoding="utf-8")
    for text in (readme, current, boundaries):
        assert V1_CURRENT_STATUS in text
        assert PUBLIC_STATUS in text
    assert "not a\nproven replacement" in readme or "not a proven replacement" in readme
    assert (
        "does not claim empirical validation" in readme
        or "does not claim empirical\nvalidation" in readme
    )
    assert "What Is Integrated Conditionally" in current
    assert "What Has Been Downgraded Or Rejected As Primary" in current
    assert "What Remains Open" in current
    assert "What Is Forbidden To Claim" in current
    assert "Latest PR / Checkpoint Summary" in current
    for forbidden in freeze.FORBIDDEN_CLAIMS:
        assert forbidden in boundaries
    assert squash(freeze.ALLOWED_STRONGEST_CLAIM) in squash(boundaries)


def test_claim_boundaries_do_not_introduce_forbidden_assertions_as_claims():
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "current_status.md",
        ROOT / "docs" / "claim_boundaries.md",
    ]
    blocked_phrases = (
        "BHSM is proven.",
        "BHSM replaces the Standard Model.",
        "BHSM predicts all particle masses.",
        "BHSM has solved CKM/PMNS.",
        "BHSM has predicted the Higgs mass.",
        "BHSM is experimentally confirmed.",
    )
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for phrase in blocked_phrases:
            assert phrase not in text


def test_zvirt_scope_and_branch_distinctions_remain_guarded():
    assert kf.threshold_insertions() == [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]
    status = load_artifact("a_background_collar_dependency_order_v1.json")
    assert status["A_background_dependency_order_verified"] is True
    assert status["B_diagnostic_preserved"] is True
    b_diag = load_artifact("charged_branch_matrices_v2_B_diagnostic.json")
    assert b_diag["branch"] == "B-diagnostic"
    assert b_diag["not_A_background"] is True
    assert b_diag["sectors"]["up"]["Z_virt_scope"] == (
        "up sector, middle mode (q,j)=(6,0) only"
    )


def test_k_collar_downgrade_is_recorded_without_precision_closure():
    a_bg_audit = load_artifact("K_collar_response_audit_A_background_identity_v2.json")
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    assert a_bg_audit["stack_verdict"] == "STACK_COLLAR_REJECTED_AS_PRIMARY"
    assert all(
        row["sector_verdict"] == "COLLAR_COMPRESSES_HIERARCHY"
        for row in a_bg_audit["sector_responses"].values()
    )
    statuses = open_gate["statuses"]
    assert statuses["K_collar_stack_verdict"] == "STACK_COLLAR_REJECTED_AS_PRIMARY"
    assert statuses[
        "minimal_positive_diagonal_K_collar_as_primary_charged_precision_route"
    ] == "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
    assert statuses["charged_precision_closure"] == "OPEN"
    assert statuses["chi_from_mass_fit"] == "FORBIDDEN"


def test_new_artifacts_preserve_public_status_and_official_prediction_guardrail():
    current_artifacts = {
        "full_BHSM_open_gate_ledger_v2.json",
        "full_BHSM_claim_status_table_v2.json",
    }
    artifact_names = [
        "full_BHSM_architecture_freeze_v1.json",
        "full_BHSM_open_gate_ledger_v2.json",
        "full_BHSM_claim_status_table_v2.json",
        "forbidden_claim_audit_v2.json",
        "a_background_collar_dependency_order_v1.json",
        "K_collar_response_audit_A_local_v2.json",
        "K_collar_response_audit_A_background_identity_v2.json",
    ]
    for name in artifact_names:
        payload = load_artifact(name)
        expected_status = V1_CURRENT_STATUS if name in current_artifacts else PUBLIC_STATUS
        assert payload["public_status"] == expected_status
        assert payload["official_predictions_changed"] is False


def test_no_empirical_fixture_introduced_in_freeze_source():
    text = (ROOT / "src" / "full_architecture_freeze_status.py").read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "observed_mass",
        "empirical_target",
        "CKM data",
        "PMNS data",
        "neutrino data",
        "Higgs mass data",
        "cosmology",
    )
    for token in blocked:
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
