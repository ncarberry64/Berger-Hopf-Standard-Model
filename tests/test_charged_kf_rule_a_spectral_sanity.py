import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import charged_kf_rule_a_spectral_sanity as sanity


DATA = ROOT / "data" / "charged_kf_rule_a_spectral_sanity_v1.json"
DOC = ROOT / "docs" / "charged_kf_rule_a_spectral_sanity_v1.md"
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


def test_rule_a_and_rule_b_eta_values():
    assert kf.eta_for_rule("lepton", kf.RULE_A_SINGLE_OPERATOR_TRACE) == Fraction(20, 147)
    assert kf.eta_for_rule("up", kf.RULE_A_SINGLE_OPERATOR_TRACE) == Fraction(38, 147)
    assert kf.eta_for_rule("down", kf.RULE_A_SINGLE_OPERATOR_TRACE) == Fraction(68, 147)

    assert kf.eta_for_rule("lepton", kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE) == Fraction(20, 3087)
    assert kf.eta_for_rule("up", kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE) == Fraction(38, 3087)
    assert kf.eta_for_rule("down", kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE) == Fraction(68, 3087)


def test_default_diagnostic_rule_is_rule_a_but_legacy_eta_remains_available():
    assert kf.DEFAULT_DIAGNOSTIC_SUPPRESSION_RULE == kf.RULE_A_SINGLE_OPERATOR_TRACE
    assert sanity.report_as_dict()["default_diagnostic_suppression_rule"] == kf.RULE_A_SINGLE_OPERATOR_TRACE
    assert kf.eta("lepton") == Fraction(20, 3087)
    assert kf.minimal_K_f("lepton", 1) == kf.minimal_K_f_for_rule(
        "lepton", 1, kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE
    )


def test_rule_a_changes_only_suppression_diagonals_not_bridge_ansatz():
    for sector in kf.CHARGED_SECTORS:
        for rho in kf.RHO_CH_BRANCHES:
            rule_a = kf.minimal_K_f_for_rule(sector, rho, kf.RULE_A_SINGLE_OPERATOR_TRACE)
            rule_b = kf.minimal_K_f_for_rule(
                sector, rho, kf.RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE
            )
            assert rule_a[0][1] == rule_b[0][1] == kf.beta(sector)
            assert rule_a[1][0] == rule_b[1][0] == kf.beta(sector)
            assert rule_a[1][2] == rule_b[1][2] == kf.kappa(sector, rho)
            assert rule_a[2][1] == rule_b[2][1] == kf.kappa(sector, rho)
            assert rule_a[0][2] == rule_b[0][2] == 0
            assert rule_a[2][0] == rule_b[2][0] == 0
            assert rule_a[1][1] > rule_b[1][1]
            assert rule_a[2][2] > rule_b[2][2]


def test_rule_a_diagonal_costs_match_required_formulas():
    for rho in kf.RHO_CH_BRANCHES:
        assert kf.diagonal_costs("lepton", rho) == (
            0,
            1 + 4 * rho,
            9 + 9 * rho,
        )
        assert kf.diagonal_costs("up", rho) == (
            0,
            36,
            64 + rho,
        )
        assert kf.diagonal_costs("down", rho) == (
            0,
            9 * rho,
            16 + 4 * rho,
        )


def test_threshold_scope_is_only_up_middle_ln2():
    insertions = kf.threshold_insertions()
    assert len(insertions) == 1
    insertion = insertions[0]
    assert insertion["sector"] == "up"
    assert insertion["slot"] == 1
    assert insertion["mode"] == [6, 0]
    assert insertion["value"] == "ln 2"

    report = sanity.report_as_dict()
    assert report["threshold_policy"]["no_other_threshold_dressings_added"] is True
    assert len(report["rule_a_up_threshold_rows"]) == len(kf.RHO_CH_BRANCHES)
    for row in report["rule_a_up_threshold_rows"]:
        assert row["only_threshold_is_up_middle_ln2"] is True


def test_json_artifact_records_rule_a_sanity_without_empirical_comparison():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == sanity.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["default_diagnostic_suppression_rule"] == "RULE_A_SINGLE_OPERATOR_TRACE"
    assert data["eta_values"]["RULE_A_SINGLE_OPERATOR_TRACE"] == {
        "lepton": "20/147",
        "up": "38/147",
        "down": "68/147",
    }
    assert data["eta_values"]["RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE"] == {
        "lepton": "20/3087",
        "up": "38/3087",
        "down": "68/3087",
    }
    assert len(data["rule_a_branch_rows"]) == 9
    assert len(data["rule_b_comparison_rows"]) == 9
    assert all("spectral_factors_exp_minus_gap" in row for row in data["rule_a_branch_rows"])


def test_no_empirical_imports_in_rule_a_modules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            Path(kf.__file__),
            Path(sanity.__file__),
        )
    )
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
        assert item not in combined


def test_status_docs_preserve_claim_boundaries():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        sanity.PUBLIC_STATUS,
        "charged_Kf_rule_A_suppression_propagation",
        "RULE_A_SINGLE_OPERATOR_TRACE=DERIVED_CONDITIONAL_ON_B_SUPP_TRACE_KERNEL",
        "RULE_B_DOUBLE_NORMALIZED_PHASE_CANDIDATE=CANDIDATE_REQUIRES_INDEPENDENT_PHASE_RESPONSE",
        "independent_phase_response_source=OPEN_LOCALIZABLE",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "numerical closure achieved",
        "official predictions updated",
        "charged masses are derived",
        "CKM closure achieved",
        "PMNS closure achieved",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = sanity.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
