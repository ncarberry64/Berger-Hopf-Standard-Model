from math import isclose

from bhsm_config import canonical_geometry_config
from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from constants import S_OVERLAP
from flavor_diagnostics import (
    ckm_rule_breakdown,
    compare_overlap_constants,
    flavor_root_cause_report,
    scan_up_admissible_modes,
    up_sector_diagnostic,
)
from prediction_ledger import build_prediction_ledger
from residual_audit import build_residual_audit


def test_flavor_diagnostic_builds_from_bhsm_model():
    report = flavor_root_cause_report(build_bhsm_model())

    assert report["model_changed"] is False
    assert "up_sector" in report
    assert "ckm_rule_breakdown" in report


def test_current_up_sector_residual_is_reproduced():
    diagnostic = up_sector_diagnostic(build_bhsm_model())
    canonical = canonical_geometry_config()

    assert isclose(diagnostic["relative_error"]["u_over_t"], 0.014590767828891764)
    assert isclose(diagnostic["relative_error"]["c_over_t"], 0.13003176431657681)
    assert diagnostic["a"] == canonical.a
    assert diagnostic["S"] == S_OVERLAP


def test_current_ckm_sin13_residual_is_reproduced():
    diagnostic = up_sector_diagnostic(build_bhsm_model())

    assert isclose(diagnostic["predicted"]["sqrt_u_over_t"], 0.0035623676140463315)
    assert isclose(diagnostic["relative_error"]["sin_theta_13"], 0.06744303297216456)


def test_admissible_up_modes_are_listed_and_ledger_unchanged():
    scan = scan_up_admissible_modes(k_max=40)

    assert len(scan["first_five"]) >= 5
    assert [tuple(row["mode"]) for row in scan["first_five"][:3]] == [(6, 0), (10, 1), (14, 2)]
    assert scan["ledger_changed"] is False


def test_sensitivity_scans_do_not_modify_model_defaults():
    before = compute_yukawa_ratios(build_bhsm_model())

    constants = compare_overlap_constants()
    flavor_root_cause_report(build_bhsm_model())

    after = compute_yukawa_ratios(build_bhsm_model())
    assert constants["current"]["a"] == canonical_geometry_config().a
    assert constants["current"]["S"] == S_OVERLAP
    assert before == after


def test_exploratory_ckm_alternatives_are_marked_exploratory():
    report = ckm_rule_breakdown(build_bhsm_model())

    assert report["adopted_alternative"] is None
    assert report["exploratory_alternatives"]
    assert all(row["status"] == "EXPLORATORY_ONLY" for row in report["exploratory_alternatives"])


def test_no_claim_status_is_upgraded_by_diagnostic():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN


def test_no_empirical_ckm_value_tunes_a_correction_factor():
    report = ckm_rule_breakdown(build_bhsm_model())
    ledger = build_prediction_ledger(build_bhsm_model())
    audit = build_residual_audit(ledger)

    assert "correction_factor" not in report
    assert report["current_rule"]["status"] == "IMPLEMENTED_SCREEN"
    assert any(row.prediction_id == "ckm.sin_theta_13" for row in audit)
