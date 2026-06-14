import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_precision_closure import (
    CANDIDATE_NOT_OFFICIAL,
    LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL,
    LEPTON_DRESSING_REJECTED,
    LEPTON_PRECISION_DERIVED,
    LEPTON_PRECISION_WARNING_CONFIRMED,
    audit_payload,
    baseline_residuals,
    candidate_dressing_rows,
    precision_result,
)


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    LEPTON_PRECISION_DERIVED,
    LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL,
    LEPTON_PRECISION_WARNING_CONFIRMED,
    LEPTON_DRESSING_REJECTED,
}


def test_charged_lepton_precision_audit_json_validates():
    payload = json.loads(ROOT.joinpath("audits/charged_lepton_precision_closure_audit.json").read_text())

    assert payload["classification"] in ALLOWED
    assert payload["classification"] == LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL
    assert payload["candidate_status"] == CANDIDATE_NOT_OFFICIAL
    assert payload["status"] == "BLOCKS_FULL_COMPLETION"
    assert payload["blocker"] == "LEPTON_PRECISION_NOT_SOLVED"
    assert payload["closes_lepton_precision_blocker"] is False


def test_one_parameter_mode_rule_improves_held_out_e_over_tau():
    baseline = {row.rank: row for row in baseline_residuals()}
    rows = {row.rank: row for row in candidate_dressing_rows()}

    assert rows["middle"].fitted_input is True
    assert rows["light"].held_out is True
    assert rows["middle"].relative_error < baseline["middle"].relative_error
    assert rows["light"].relative_error < baseline["light"].relative_error
    assert rows["light"].relative_error < 0.01


def test_no_per_particle_fitted_factors_and_candidate_not_official():
    payload = audit_payload()
    result = precision_result()

    assert payload["candidate_rule"]["fit_input_ratio"] == "mu/tau"
    assert payload["candidate_rule"]["held_out_ratio"] == "e/tau"
    assert payload["candidate_rule"]["per_particle_fitted_factors_used"] is False
    assert result.candidate_status == CANDIDATE_NOT_OFFICIAL
    assert result.closes_lepton_precision_blocker is False
    assert result.official_lepton_ratios_changed is False


def test_frozen_prediction_files_unchanged_by_lepton_candidate():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()

    assert "charged_lepton_mode_norm_exponential" not in frozen_md
    assert "charged_lepton_mode_norm_exponential" not in frozen_json
    assert "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL" not in frozen_md
    assert "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL" not in frozen_json


def test_official_branches_unchanged_and_no_lepton_output_promotion():
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


def test_candidate_file_is_non_official_and_names_open_derivation():
    text = ROOT.joinpath("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md").read_text()

    assert "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL" in text
    assert "CANDIDATE_NOT_OFFICIAL" in text
    assert "Lepton precision blocker closed: `False`" in text
    assert "eta_l` is fit from `mu/tau`, not derived" in text


def test_no_forbidden_claims_in_lepton_outputs():
    text = "\n".join(
        [
            ROOT.joinpath("theory/charged_lepton_precision_closure.md").read_text(),
            ROOT.joinpath("audits/charged_lepton_precision_closure_audit.md").read_text(),
            ROOT.joinpath("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md").read_text(),
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


def test_damage_check_rejects_extension_outside_charged_leptons():
    payload = audit_payload()

    assert payload["damage_checks"]["extension_allowed"] is False
    assert payload["damage_checks"]["extended_to_quarks_or_ckm"] is False
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
