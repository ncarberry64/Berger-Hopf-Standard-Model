import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_eta_derivation import (
    ALLOWED_CLASSIFICATIONS,
    ETA_L_DERIVED,
    ETA_L_NUMERICAL_COINCIDENCE_REJECTED,
    ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED,
    audit_payload,
    best_independent_candidate,
    candidate_eta_values,
    eta_derivation_report,
)
from charged_lepton_precision_closure import CANDIDATE_NOT_OFFICIAL, fit_eta_from_mu_tau


ROOT = Path(__file__).resolve().parents[1]


def test_eta_derivation_audit_json_validates():
    payload = json.loads(ROOT.joinpath("audits/charged_lepton_eta_derivation_audit.json").read_text())

    assert payload["classification"] in ALLOWED_CLASSIFICATIONS
    assert payload["classification"] == ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED
    assert payload["closes_lepton_blocker"] is False
    assert payload["candidate_status"] == CANDIDATE_NOT_OFFICIAL


def test_fitted_eta_is_reported_but_not_derived():
    report = eta_derivation_report()

    assert report.fitted_eta_l == fit_eta_from_mu_tau()
    assert report.classification != ETA_L_DERIVED
    assert all(candidate.derived is False for candidate in report.candidate_eta_values)
    assert report.closes_lepton_blocker is False


def test_candidate_inventory_contains_only_predeclared_sources():
    ids = {candidate.id for candidate in candidate_eta_values()}

    assert "fine_structure_alpha" in ids
    assert "fine_structure_alpha_over_pi" in ids
    assert "gauge_alpha_1" in ids
    assert "universal_overlap_width" in ids
    assert "overlap_width_per_boundary_sum" in ids
    assert "inverse_hopf_gap" in ids
    assert "zvirt_log_per_boundary_sum" in ids


def test_best_independent_candidate_is_structural_not_closing():
    best = best_independent_candidate()

    assert best is not None
    assert best.id == "fine_structure_alpha_over_pi"
    assert best.independent_of_lepton_residuals is True
    assert best.structurally_motivated is True
    assert best.derived is False
    assert best.improves_both is True
    assert best.closes_lepton_blocker is False


def test_numerical_coincidences_cannot_close_blocker():
    candidates = {candidate.id: candidate for candidate in candidate_eta_values()}

    assert candidates["alpha_per_lepton_boundary"].numerical_coincidence_only is True
    assert candidates["alpha_per_lepton_boundary"].closes_lepton_blocker is False
    assert candidates["zvirt_log_per_64pi"].numerical_coincidence_only is True
    assert candidates["zvirt_log_per_64pi"].closes_lepton_blocker is False
    assert audit_payload()["classification"] != ETA_L_NUMERICAL_COINCIDENCE_REJECTED


def test_frozen_prediction_files_and_official_branches_unchanged():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert "charged_lepton_eta_derivation" not in frozen_md
    assert "charged_lepton_eta_derivation" not in frozen_json
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert audit_payload()["official_outputs_changed"] is False
    assert audit_payload()["official_lepton_ratios_changed"] is False


def test_lepton_blocker_closes_only_if_eta_derived():
    payload = audit_payload()
    any_derived = any(payload["whether_candidate_is_derived"].values())

    assert any_derived is False
    assert payload["closes_lepton_blocker"] is False
    assert payload["classification"] != ETA_L_DERIVED


def test_no_forbidden_claims_in_eta_outputs():
    text = "\n".join(
        [
            ROOT.joinpath("theory/charged_lepton_eta_derivation.md").read_text(),
            ROOT.joinpath("audits/charged_lepton_eta_derivation_audit.md").read_text(),
        ]
    ).lower()
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "lepton blocker closed: `true`",
        "eta_l is derived",
    )
    for phrase in forbidden:
        assert phrase not in text
