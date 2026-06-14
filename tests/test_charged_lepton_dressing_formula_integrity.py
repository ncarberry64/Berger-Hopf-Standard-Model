import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_dressing_formula_integrity import (
    CANDIDATE_NOT_OFFICIAL,
    FORMULA_CONSISTENT,
    audit_payload,
    candidate_norm_results,
    formula_integrity_report,
    implemented_mode_exponents,
)
from charged_lepton_precision_closure import candidate_dressing_rows


ROOT = Path(__file__).resolve().parents[1]


def test_formula_integrity_audit_json_validates():
    payload = json.loads(
        ROOT.joinpath("audits/charged_lepton_dressing_formula_integrity_audit.json").read_text()
    )

    assert payload["classification"] == FORMULA_CONSISTENT
    assert payload["candidate_status"] == CANDIDATE_NOT_OFFICIAL
    assert payload["documentation_and_code_match"] is True
    assert payload["prior_candidate_result_remains_valid"] is True
    assert payload["lepton_precision_blocker_closed"] is False


def test_implemented_exponents_are_hopf_charge_not_k_coordinate():
    rows = {row.rank: row for row in implemented_mode_exponents()}

    assert rows["middle"].mode == (5, 2)
    assert rows["middle"].q_hopf == 1
    assert rows["middle"].implemented_exponent == 5.0
    assert rows["light"].mode == (9, 3)
    assert rows["light"].q_hopf == 3
    assert rows["light"].implemented_exponent == 18.0
    assert "k-2j" in rows["middle"].implemented_expression


def test_candidate_norm_eta_values_are_reproducible():
    rows = {row.norm_name: row for row in candidate_norm_results()}

    assert rows["q^2+j^2"].mu_exponent == 5.0
    assert rows["q^2+j^2"].electron_exponent == 18.0
    assert rows["q^2+j^2"].eta_from_mu_tau == 0.0020443439144236667
    assert rows["q^2+j^2"].electron_held_out_prediction == 0.0002865501268883495
    assert rows["q"].eta_from_mu_tau == 0.010221719572118334
    assert rows["2q"].eta_from_mu_tau == 0.005110859786059167


def test_prior_candidate_matches_q_squared_plus_j_squared_row():
    prior = {row.rank: row for row in candidate_dressing_rows()}
    row = next(item for item in candidate_norm_results() if item.norm_name == "q^2+j^2")

    assert prior["middle"].dressed_prediction == row.mu_dressed_prediction
    assert prior["light"].dressed_prediction == row.electron_held_out_prediction


def test_best_candidate_reported_but_not_promoted_official():
    report = formula_integrity_report()

    assert report.best_numerical_candidate == "q"
    assert report.best_structurally_motivated_candidate == "q^2+j^2"
    assert report.candidate_status == CANDIDATE_NOT_OFFICIAL
    assert report.official_lepton_ratios_changed is False
    assert report.lepton_precision_blocker_closed is False


def test_official_branches_and_frozen_prediction_files_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()

    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert "charged_lepton_dressing_formula_integrity" not in frozen_md
    assert "charged_lepton_dressing_formula_integrity" not in frozen_json
    assert audit_payload()["official_outputs_changed"] is False


def test_no_forbidden_claims_in_formula_integrity_outputs():
    text = "\n".join(
        [
            ROOT.joinpath("audits/charged_lepton_dressing_formula_integrity_audit.md").read_text(),
            ROOT.joinpath("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md").read_text(),
            ROOT.joinpath("theory/charged_lepton_precision_closure.md").read_text(),
        ]
    ).lower()
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "official lepton dressing",
        "lepton precision blocker closed: `true`",
    )
    for phrase in forbidden:
        assert phrase not in text
