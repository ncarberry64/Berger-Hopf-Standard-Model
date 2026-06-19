import importlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import charged_suppression_operator_kernel as kernel


DATA = ROOT / "data" / "charged_suppression_operator_kernel_v1.json"
DOC = ROOT / "docs" / "charged_suppression_operator_kernel_v1.md"
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


def test_rank_and_trace_normalization():
    assert kernel.INCIDENCE_RANKS == {"lepton": 3, "up": 6, "down": 12}
    assert kernel.total_charged_rank() == 21
    assert kernel.diagonal_incidence_weight() == Fraction(1, 21)
    assert kernel.B_supp_trace() == 1
    assert set(kernel.B_supp_diagonal_weights()) == {Fraction(1, 21)}
    assert len(kernel.B_supp_diagonal_weights()) == 21


def test_sector_trace_contractions_are_projection_fractions():
    assert kernel.sector_trace_contraction("lepton") == Fraction(1, 7)
    assert kernel.sector_trace_contraction("up") == Fraction(2, 7)
    assert kernel.sector_trace_contraction("down") == Fraction(4, 7)


def test_self_screening_counts_and_factors():
    assert kernel.self_screening_count("lepton") == 1
    assert kernel.self_screening_count("up") == 2
    assert kernel.self_screening_count("down") == 4
    assert kernel.single_operator_g_eff() == Fraction(1, 21)
    assert kernel.self_screening_factor("lepton") == Fraction(20, 21)
    assert kernel.self_screening_factor("up") == Fraction(19, 21)
    assert kernel.self_screening_factor("down") == Fraction(17, 21)


def test_contraction_rules_are_exact_and_distinct():
    assert kernel.eta_single_trace("lepton") == Fraction(20, 147)
    assert kernel.eta_single_trace("up") == Fraction(38, 147)
    assert kernel.eta_single_trace("down") == Fraction(68, 147)

    assert kernel.eta_double_normalized("lepton") == Fraction(20, 3087)
    assert kernel.eta_double_normalized("up") == Fraction(38, 3087)
    assert kernel.eta_double_normalized("down") == Fraction(68, 3087)

    assert kernel.eta_local_normalized("lepton") == Fraction(20, 441)
    assert kernel.eta_local_normalized("up") == Fraction(19, 441)
    assert kernel.eta_local_normalized("down") == Fraction(17, 441)


def test_rule_statuses_preserve_scientific_boundary():
    rules = kernel.contraction_rules()
    rule_a = rules["RULE_A_SINGLE_OPERATOR_TRACE"]
    rule_b = rules["RULE_B_DOUBLE_NORMALIZED"]
    rule_c = rules["RULE_C_LOCAL_SECTOR_NORMALIZATION"]

    assert rule_a.selected_by_kernel is True
    assert rule_a.requires_independent_phase_coupling is False
    assert rule_a.status == "DERIVED_CONDITIONAL_ON_B_SUPP_KERNEL"

    assert rule_b.selected_by_kernel is False
    assert rule_b.requires_independent_phase_coupling is True
    assert "REQUIRES_INDEPENDENT_PHASE_COUPLING" in rule_b.status

    assert rule_c.selected_by_kernel is False
    assert rule_c.status == "STRUCTURALLY_POSSIBLE_NOT_SELECTED"

    assert kernel.STATUS_TABLE["g_ch_independent_phase_response"] == "OPEN_LOCALIZABLE"
    assert kernel.STATUS_TABLE["numerical_closure"] == "OPEN"
    assert kernel.PUBLIC_STATUS == (
        "structural architecture integrated conditional; numerical closure open"
    )


def test_report_json_matches_kernel_and_validates():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == kernel.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["B_supp"]["trace"] == "1"
    assert data["B_supp"]["diagonal_weight"] == "1/21"
    assert data["selected_kernel_rule"] == "RULE_A_SINGLE_OPERATOR_TRACE"
    assert data["contraction_rules"]["RULE_A_SINGLE_OPERATOR_TRACE"]["eta_values"] == {
        "lepton": "20/147",
        "up": "38/147",
        "down": "68/147",
    }
    assert data["contraction_rules"]["RULE_B_DOUBLE_NORMALIZED"]["eta_values"] == {
        "lepton": "20/3087",
        "up": "38/3087",
        "down": "68/3087",
    }


def test_no_empirical_imports_and_no_kf_overwrite():
    source = Path(kernel.__file__).read_text(encoding="utf-8")
    blocked_imports = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
    )
    for item in blocked_imports:
        assert item not in source

    importlib.reload(kf)
    assert kf.eta("lepton") == Fraction(20, 3087)
    assert kf.eta("up") == Fraction(38, 3087)
    assert kf.eta("down") == Fraction(68, 3087)
    assert kernel.report_as_dict()["minimal_charged_Kf_generator_overwritten"] is False


def test_docs_and_status_backlog_record_ambiguity_without_overclaim():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        kernel.PUBLIC_STATUS,
        "B_supp=I_ch/21",
        "charged_suppression_single_operator_trace_rule",
        "charged_suppression_double_normalized_rule",
        "g_ch_independent_phase_response",
        "The older eta_f={20,38,68}/3087 package is the double-normalized candidate.",
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


def test_frozen_prediction_files_remain_unchanged_by_kernel():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = kernel.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
