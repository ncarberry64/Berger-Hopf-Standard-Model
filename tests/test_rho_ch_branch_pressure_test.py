import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import rho_ch_branch_pressure_test as rpt


DATA = ROOT / "data" / "rho_ch_branch_pressure_test_v1.json"
DOC = ROOT / "docs" / "rho_ch_branch_pressure_test_v1.md"
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


def test_all_three_rho_branches_are_emitted():
    data = rpt.report_as_dict()
    assert [row["rho_ch"] for row in data["branch_reports"]] == [1, 2, 3]
    assert set(data["branch_classifications"]) == {"1", "2", "3"}
    assert data["all_branches_viable"] is True


def test_rule_a_eta_values_are_used_and_rule_b_is_not_default():
    data = rpt.report_as_dict()
    assert data["suppression_rule"] == kf.RULE_A_SINGLE_OPERATOR_TRACE
    assert data["rule_b_used_as_default"] is False
    assert data["rule_a_eta_values"] == {
        "lepton": "20/147",
        "up": "38/147",
        "down": "68/147",
    }
    for sector in kf.CHARGED_SECTORS:
        assert kf.eta_for_rule(sector, data["suppression_rule"]) != kf.eta_for_rule(
            sector, kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE
        )


def test_threshold_insertion_remains_only_up_middle_ln2():
    data = rpt.report_as_dict()
    policy = data["threshold_policy"]
    assert policy["only_up_middle_ln2"] is True
    assert policy["no_other_threshold_dressings_added"] is True
    assert len(policy["insertions"]) == 1
    insertion = policy["insertions"][0]
    assert insertion["sector"] == "up"
    assert insertion["slot"] == 1
    assert insertion["mode"] == [6, 0]
    assert insertion["value"] == "ln 2"


def test_branch_classification_does_not_select_winner():
    data = rpt.report_as_dict()
    assert data["winning_branch_selected"] is False
    assert data["rho_ch_exact_value_status"] == "OPEN_LOCALIZABLE"
    assert data["branch_classifications"] == {
        "1": "BRANCH_CANDIDATE",
        "2": "BRANCH_CANDIDATE",
        "3": "STRUCTURALLY_INTERESTING_BRANCH",
    }
    assert data["statuses"]["rho_ch_exact_value"] == "OPEN_LOCALIZABLE"
    assert data["statuses"]["numerical_closure"] == "OPEN"


def test_down_rho_three_is_interesting_but_not_selected():
    data = rpt.report_as_dict()
    splits = {
        row["rho_ch"]: row["down_degeneracy_measure"] for row in data["branch_reports"]
    }
    assert splits[3] < splits[2] < splits[1]
    rho3 = [row for row in data["branch_reports"] if row["rho_ch"] == 3][0]
    assert rho3["branch_status"] == "STRUCTURALLY_INTERESTING_BRANCH"
    assert rho3["recommended_scientific_status"] == "REQUIRES_ACTION_SELECTION"
    assert rho3["violates_internal_consistency"] is False


def test_up_threshold_reordering_is_reported_not_hidden():
    data = rpt.report_as_dict()
    rows = data["branch_reports"]
    assert all("up_threshold_causes_reordering" in row for row in rows)
    assert all(row["up_threshold_causes_reordering"] is False for row in rows)
    assert data["statuses"]["up_threshold_branch_reordering"] == (
        "DIAGNOSTIC_REPORTED_NO_EMPIRICAL_SELECTION"
    )


def test_no_empirical_imports_in_pressure_test_module():
    source = Path(rpt.__file__).read_text(encoding="utf-8")
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


def test_json_artifact_validates_public_status_and_guardrails():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == rpt.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["winning_branch_selected"] is False
    assert len(data["branch_reports"]) == 3


def test_docs_and_status_backlog_preserve_claim_boundary():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        rpt.PUBLIC_STATUS,
        "rho_ch_branch_pressure_test_v1",
        "rho_ch_1_isotropic_branch=BRANCH_CANDIDATE",
        "rho_ch_2_weak_involution_branch=BRANCH_CANDIDATE",
        "rho_ch_3_rank_three_branch=STRUCTURALLY_INTERESTING_BRANCH",
        "rho_ch_exact_value=OPEN_LOCALIZABLE",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "winning rho_ch branch",
        "rho_ch exact value derived",
        "numerical closure achieved",
        "official predictions updated",
        "charged masses are derived",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = rpt.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
