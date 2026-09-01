import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from boundary_action_closure_candidate import (
    BOUNDARY_ACTION_DERIVED,
    CANDIDATE_NOT_OFFICIAL,
    SPECTRAL_BOUNDARY_DERIVED,
    STRUCTURALLY_MOTIVATED_CANDIDATE,
    audit_payload,
    build_boundary_generators,
    candidate_result,
    selected_mode_checks,
)


ROOT = Path(__file__).resolve().parents[1]
DERIVED_CLASSIFICATIONS = {BOUNDARY_ACTION_DERIVED, SPECTRAL_BOUNDARY_DERIVED}


def test_boundary_action_candidate_files_exist_and_json_validates():
    paths = [
        ROOT / "theory/boundary_action_closure_candidate.md",
        ROOT / "audits/boundary_action_closure_candidate_audit.py",
        ROOT / "audits/boundary_action_closure_candidate_audit.md",
        ROOT / "audits/boundary_action_closure_candidate_audit.json",
        ROOT / "candidates/BHSM_BOUNDARY_ACTION_V1_CANDIDATE.md",
        ROOT / "candidates/BHSM_BOUNDARY_ACTION_V1_CANDIDATE.json",
    ]
    for path in paths:
        assert path.exists()

    payload = json.loads((ROOT / "audits/boundary_action_closure_candidate_audit.json").read_text())
    assert payload["candidate_name"] == "BHSM_BOUNDARY_ACTION_V1_CANDIDATE"
    assert payload["classification"] == STRUCTURALLY_MOTIVATED_CANDIDATE


def test_candidate_status_is_not_official_unless_derived():
    payload = audit_payload()

    if payload["classification"] in DERIVED_CLASSIFICATIONS:
        assert payload["status"] != CANDIDATE_NOT_OFFICIAL
        assert payload["closes_boundary_operator_blocker"] is True
    else:
        assert payload["status"] == CANDIDATE_NOT_OFFICIAL
        assert payload["closes_boundary_operator_blocker"] is False


def test_candidate_reproduces_omega_values_from_structural_inputs():
    generators = build_boundary_generators()

    assert generators["lepton"].fiber_coefficient == -1
    assert generators["lepton"].base_coefficient == 2
    assert generators["lepton"].target == 3
    assert generators["up"].fiber_coefficient == 1
    assert generators["up"].base_coefficient == -2
    assert generators["up"].target == 6
    assert generators["down"].fiber_coefficient == 1
    assert generators["down"].base_coefficient == 4
    assert generators["down"].target == 12
    assert all(row["matches_target"] for row in selected_mode_checks())


def test_closure_false_when_candidate_rules_are_not_forced():
    result = candidate_result()

    assert result.classification == STRUCTURALLY_MOTIVATED_CANDIDATE
    assert result.coefficients_forced is False
    assert result.used_fitted_coefficients is False
    assert result.closes_boundary_blocker is False
    assert result.helps_z_virt_u2 is False
    assert result.helps_ckm_1_16 is False


def test_frozen_prediction_files_unchanged_by_candidate():
    frozen_md = (ROOT / "docs/frozen_predictions.md").read_text()
    frozen_json = (ROOT / "docs/frozen_predictions.json").read_text()

    assert "BHSM_BOUNDARY_ACTION_V1_CANDIDATE" not in frozen_md
    assert "BHSM_BOUNDARY_ACTION_V1_CANDIDATE" not in frozen_json
    assert "boundary_action_closure_candidate" not in frozen_md
    assert "boundary_action_closure_candidate" not in frozen_json


def test_official_branches_remain_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert comparison["branches"] == ("BHSM_BARE_V1", "BHSM_DRESSED_V1_CANDIDATE")
    assert len(changed) == 1
    assert changed[0]["quantity"] == "c/t"
    assert next(row for row in comparison["rows"] if row["quantity"] == "u/t")["changed"] is False
    assert next(row for row in comparison["rows"] if row["quantity"] == "sin_theta_13")[
        "changed"
    ] is False


def test_forbidden_claims_absent_from_candidate_files():
    forbidden = (
        "BHSM is proven",
        "confirmed Standard Model replacement",
        "fully proven",
        "complete derivation of the Standard Model",
    )
    text = "\n".join(
        [
            (ROOT / "theory/boundary_action_closure_candidate.md").read_text(),
            (ROOT / "audits/boundary_action_closure_candidate_audit.md").read_text(),
            (ROOT / "candidates/BHSM_BOUNDARY_ACTION_V1_CANDIDATE.md").read_text(),
        ]
    )

    for phrase in forbidden:
        assert phrase not in text


def test_audit_reports_promotion_and_rejection_criteria():
    payload = json.loads((ROOT / "audits/boundary_action_closure_candidate_audit.json").read_text())

    assert payload["promotion_criteria"]
    assert payload["rejection_criteria"]
    assert payload["coefficients_inserted"] is False
    assert payload["coefficients_forced"] is False
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
