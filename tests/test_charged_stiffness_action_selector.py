import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_stiffness_action_selector as selector
import rho_ch_branch_pressure_test as pressure


DATA = ROOT / "data" / "charged_stiffness_action_selector_v1.json"
DOC = ROOT / "docs" / "charged_stiffness_action_selector_v1.md"
CLAIMS = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_stiffness_action_and_rho_definition_are_exact():
    assert selector.STIFFNESS_ACTION_FORM == "S_stiffness,ch = k_q q^2 + k_j j^2"
    assert selector.RHO_DEFINITION == "rho_ch = k_j/k_q"
    assert selector.stiffness_action(2, 3, Fraction(5), Fraction(7)) == 5 * 4 + 7 * 9
    assert selector.rho_from_stiffness(Fraction(2), Fraction(6)) == 3
    assert selector.has_cross_term() is False


def test_selector_candidates_emit_rho_one_two_three_with_statuses():
    candidates = selector.selector_candidates()
    assert [item.rho_ch for item in candidates] == [Fraction(1), Fraction(2), Fraction(3)]
    by_id = {item.selector_id: item for item in candidates}
    assert by_id["A_ISOTROPIC_PRIMITIVE_STIFFNESS"].status == (
        "STRUCTURALLY_SUPPORTED_CANDIDATE"
    )
    assert by_id["B_WEAK_INVOLUTION_WEIGHTED_STIFFNESS"].status == (
        "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert by_id["C_RANK_THREE_CLOSURE_WEIGHTED_STIFFNESS"].status == (
        "STRUCTURALLY_INTERESTING_BRANCH"
    )
    for item in candidates:
        assert item.evidence_summary
        assert item.reason_not_selected
        assert item.selected is False


def test_selector_honesty_no_unique_branch_selected():
    verdict = selector.selector_verdict()
    assert verdict.selected_rho_ch is None
    assert verdict.rho_ch_exact_value_status == "OPEN_LOCALIZABLE"
    assert verdict.verdict == "NO_UNIQUE_ACTION_SELECTOR_FOUND"
    assert verdict.theorem_complete is False
    report = selector.report_as_dict()
    assert report["rho_ch_exact_value_status"] == "OPEN_LOCALIZABLE"
    assert report["statuses"]["numerical_closure"] == "OPEN"
    assert report["statuses"]["charged_Hessian_from_S_index_trace"] == (
        "INVALIDATED_DO_NOT_CLAIM"
    )


def test_rho_three_not_selected_from_down_near_degeneracy():
    report = selector.report_as_dict()
    candidate = [
        item for item in report["selector_candidates"] if item["rho_ch"] == "3"
    ][0]
    assert candidate["status"] == "STRUCTURALLY_INTERESTING_BRANCH"
    assert candidate["selected"] is False
    assert "Down near-degeneracy" in candidate["reason_not_selected"]
    assert report["verdict"]["selected_rho_ch"] is None


def test_no_empirical_imports_in_selector_module():
    source = Path(selector.__file__).read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
    )
    for item in blocked:
        assert item not in source


def test_pr30_pressure_classifications_remain_unchanged():
    report = selector.report_as_dict()
    assert report["pressure_test_classifications_preserved"] == pressure.report_as_dict()[
        "branch_classifications"
    ]
    assert report["pressure_test_classifications_preserved"] == {
        "1": "BRANCH_CANDIDATE",
        "2": "BRANCH_CANDIDATE",
        "3": "STRUCTURALLY_INTERESTING_BRANCH",
    }


def test_json_artifact_validates_status_and_guardrails():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == selector.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["charged_stiffness_has_qj_cross_term"] is False
    assert data["S_index_trace_hessian_source_status"] == "INVALIDATED_DO_NOT_CLAIM"
    assert data["verdict"]["verdict"] == "NO_UNIQUE_ACTION_SELECTOR_FOUND"


def test_docs_and_status_backlog_preserve_claim_boundary():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        selector.PUBLIC_STATUS,
        "charged_stiffness_action_selector_v1",
        "rho_ch_1_isotropic_action_selector",
        "rho_ch_2_weak_involution_action_selector",
        "rho_ch_3_rank_three_action_selector",
        "rho_ch_exact_value=OPEN_LOCALIZABLE",
        "charged_Hessian_from_S_index_trace=INVALIDATED_DO_NOT_CLAIM",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "rho_ch exact value derived",
        "winning rho_ch branch",
        "numerical closure achieved",
        "official predictions updated",
        "charged masses are derived",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = selector.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
