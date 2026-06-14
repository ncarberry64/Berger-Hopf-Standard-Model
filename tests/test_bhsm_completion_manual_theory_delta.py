import json
from math import pi, sqrt
from pathlib import Path

from bhsm_completion_manual_theory_delta import (
    CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED,
    CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED,
    HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN,
    LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED,
    NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY,
    PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED,
    SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED,
    audit_payload,
    frozen_sanity_payload,
    lepton_eta_delta_payload,
    light_up_three_coframe_payload,
)
from bhsm_v1 import compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY


ROOT = Path(__file__).resolve().parents[1]


def test_manual_delta_json_validates_and_candidate_statuses():
    payload = json.loads(ROOT.joinpath("audits/bhsm_completion_manual_theory_delta_audit.json").read_text())
    report = payload["report"]

    assert report["lepton_eta_status"] == SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED
    assert report["light_up_status"] == LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED
    assert report["ckm_projection_status"] == CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED
    assert report["pure_fiber_doublet_status"] == PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED
    assert report["neutrino_ledger_status"] == NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY
    assert report["cp_holonomy_status"] == CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED
    assert report["higgs_surface_mode_status"] == HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN


def test_frozen_files_and_official_branches_unchanged():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert "BHSM_COMPLETION_GAP_CLOSURE_V2" not in frozen_md
    assert "BHSM_COMPLETION_GAP_CLOSURE_V2" not in frozen_json
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert frozen_sanity_payload()["ckm_sin_theta_13_unchanged"] is True
    assert audit_payload()["report"].official_outputs_changed is False


def test_screened_eta_candidate_value_and_improvement():
    payload = lepton_eta_delta_payload()
    rows = {row.candidate: row for row in payload["rows"]}
    expected = 8.0 * (1.0 / ALPHA_INV_LOW_ENERGY) / (9.0 * pi)

    screened = rows["screened_8alpha_over_9pi"]
    baseline = rows["baseline_no_dressing"]
    assert screened.eta_l == expected
    assert screened.improves_mu_tau is True
    assert screened.improves_e_tau is True
    assert screened.mu_tau_relative_error < baseline.mu_tau_relative_error
    assert screened.e_tau_relative_error < baseline.e_tau_relative_error
    assert payload["status"] == SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED


def test_light_up_candidate_is_nonofficial_and_does_not_change_ckm_s13():
    payload = light_up_three_coframe_payload()
    official = payload["official_u_over_t"]["bare"]

    assert payload["status"] == LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED
    assert payload["candidate_u_over_t"] == official / sqrt(3.0)
    assert payload["ckm_sin_theta_13_unchanged"] is True
    assert payload["official_predictions_changed"] is False


def test_no_ordinary_ftl_or_mass_drift_claims():
    payload = audit_payload()
    text = "\n".join(
        [
            ROOT.joinpath("docs/BHSM_COMPLETION_GAP_CLOSURE_V2.md").read_text(),
            ROOT.joinpath("theory/mode_local_stochastic_projection_dressing_completion_note.md").read_text(),
            ROOT.joinpath("audits/bhsm_completion_manual_theory_delta_audit.md").read_text(),
        ]
    ).lower()

    assert payload["neutrino_leakage"]["ordinary_FTL_claim"] is False
    assert "ordinary faster-than-light" in text
    assert "ordinary_flt" not in text
    assert "ordinary mass-drift claim is made" not in text
    assert "bhsm is proven" not in text
    assert "replaces the standard model" not in text


def test_blockers_remain_open_and_no_retuning():
    payload = audit_payload()
    report = payload["report"]

    assert report.blockers_closed == ()
    assert len(report.blockers_remaining) >= 7
    assert payload["claim_discipline"]["no_retuning"] is True
    assert payload["claim_discipline"]["candidate_only"] is True
