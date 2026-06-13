import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_JSON = (
    "audits/z_virt_u2_closure_audit.json",
    "audits/ckm_mixing_exponent_1_16_closure_audit.json",
    "audits/boundary_operator_closure_audit.json",
    "audits/charged_lepton_precision_closure_audit.json",
    "audits/common_scale_quark_rg_closure_audit.json",
    "audits/gauge_coupling_precision_closure_audit.json",
    "audits/scalar_higgs_gap_closure_audit.json",
    "docs/BHSM_HARD_CLOSURE_STATUS.json",
)


def _read(path: str) -> str:
    return ROOT.joinpath(path).read_text(encoding="utf-8")


def test_all_closure_json_files_exist_and_have_allowed_statuses():
    allowed = {"CLOSED_SOLVED", "CLOSED_REJECTED", "BLOCKS_FULL_COMPLETION"}

    for path in REQUIRED_JSON:
        payload = json.loads(_read(path))
        if path.endswith("BHSM_HARD_CLOSURE_STATUS.json"):
            for result in payload["results"]:
                assert result["status"] in allowed
        else:
            assert payload["status"] in allowed


def test_full_completion_ready_is_blocked_by_p0_p1_open_items():
    payload = json.loads(_read("docs/BHSM_HARD_CLOSURE_STATUS.json"))

    p0_p1_blockers = [
        row for row in payload["remaining_blockers"]
        if row["issue_id"].startswith("P0") or row["issue_id"].startswith("P1")
    ]
    assert p0_p1_blockers
    assert payload["final_status"] == "PARTIAL_COMPLETION_WITH_BLOCKERS"
    assert payload["promotion_allowed"] is False


def test_no_official_frozen_files_changed_by_hard_closure():
    text_md = _read("docs/frozen_predictions.md")
    text_json = _read("docs/frozen_predictions.json")

    assert "BHSM_HARD_CLOSURE_STATUS" not in text_md
    assert "BHSM_HARD_CLOSURE_STATUS" not in text_json


def test_official_branches_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_no_forbidden_positive_claims_in_hard_closure_docs():
    paths = [
        "docs/BHSM_HARD_CLOSURE_STATUS.md",
        "theory/z_virt_u2_derivation.md",
        "theory/ckm_mixing_exponent_1_16_derivation.md",
        "theory/boundary_operator_action_derivation.md",
        "theory/scalar_higgs_gap_full_solution.md",
    ]
    text = "\n".join(_read(path) for path in paths).lower()

    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "standard model replacement",
    )
    for phrase in forbidden:
        assert phrase not in text
