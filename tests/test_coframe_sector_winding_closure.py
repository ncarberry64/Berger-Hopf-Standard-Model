import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from coframe_sector_winding_closure import (
    COFRAME_AND_WINDING_DERIVED,
    COFRAME_MULTIPLIER_NOT_DERIVED,
    SECTOR_WINDING_RULE_NOT_DERIVED,
    STRUCTURALLY_MOTIVATED_NOT_DERIVED,
    audit_payload,
    closure_result,
    coframe_multiplier_audit,
    sector_winding_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_coframe_sector_winding_files_exist_and_json_validates():
    paths = [
        ROOT / "theory/coframe_sector_winding_closure.md",
        ROOT / "audits/coframe_sector_winding_closure_audit.py",
        ROOT / "audits/coframe_sector_winding_closure_audit.md",
        ROOT / "audits/coframe_sector_winding_closure_audit.json",
    ]
    for path in paths:
        assert path.exists()

    payload = json.loads((ROOT / "audits/coframe_sector_winding_closure_audit.json").read_text())
    assert payload["classification"] == STRUCTURALLY_MOTIVATED_NOT_DERIVED
    assert payload["boundary_blocker"] == "BOUNDARY_OPERATORS_NOT_ACTION_DERIVED"


def test_coframe_and_winding_remain_specific_open_blockers():
    payload = audit_payload()

    assert payload["specific_blockers"] == (
        COFRAME_MULTIPLIER_NOT_DERIVED,
        SECTOR_WINDING_RULE_NOT_DERIVED,
    )
    assert coframe_multiplier_audit().derived is False
    assert sector_winding_audit().derived is False
    assert coframe_multiplier_audit().status == COFRAME_MULTIPLIER_NOT_DERIVED
    assert sector_winding_audit().status == SECTOR_WINDING_RULE_NOT_DERIVED


def test_closure_false_unless_both_rules_are_derived():
    result = closure_result()

    assert result.classification != COFRAME_AND_WINDING_DERIVED
    assert result.coefficients_forced is False
    assert result.coefficients_inserted is False
    assert result.closes_boundary_blocker is False
    assert result.omega_l_recovered is True
    assert result.omega_u_recovered is True
    assert result.omega_d_recovered is True


def test_candidate_remains_non_official_unless_fully_derived():
    payload = audit_payload()

    assert payload["candidate_remains_non_official"] is True
    assert payload["closes_boundary_blocker"] is False
    assert payload["result"].classification == STRUCTURALLY_MOTIVATED_NOT_DERIVED


def test_frozen_prediction_files_unchanged():
    frozen_md = (ROOT / "docs/frozen_predictions.md").read_text()
    frozen_json = (ROOT / "docs/frozen_predictions.json").read_text()

    assert "coframe_sector_winding_closure" not in frozen_md
    assert "coframe_sector_winding_closure" not in frozen_json
    assert "COFRAME_MULTIPLIER_NOT_DERIVED" not in frozen_md
    assert "SECTOR_WINDING_RULE_NOT_DERIVED" not in frozen_json


def test_official_branches_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert comparison["branches"] == ("BHSM_BARE_V1", "BHSM_DRESSED_V1_CANDIDATE")
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert next(row for row in comparison["rows"] if row["quantity"] == "u/t")["changed"] is False
    assert next(row for row in comparison["rows"] if row["quantity"] == "sin_theta_13")[
        "changed"
    ] is False


def test_no_forbidden_claims_in_coframe_winding_outputs():
    text = "\n".join(
        [
            (ROOT / "theory/coframe_sector_winding_closure.md").read_text(),
            (ROOT / "audits/coframe_sector_winding_closure_audit.md").read_text(),
            (ROOT / "audits/coframe_sector_winding_closure_audit.json").read_text(),
        ]
    ).lower()
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "boundary operators action_derived",
        "coframe_and_winding_derived",
    )
    for phrase in forbidden:
        assert phrase not in text


def test_z_and_ckm_blockers_not_helped():
    result = closure_result()

    assert result.helps_z_virt_u2 is False
    assert result.helps_ckm_1_16 is False
