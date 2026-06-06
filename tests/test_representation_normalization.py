from math import isclose

import pytest

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from representation_normalization import (
    ADOPTED_CANONICAL,
    ACTION_LINKED,
    DIAGNOSTIC_ONLY,
    RepresentationNormalization,
    apply_normalization_to_ratios,
    candidate_normalization_factors,
    compare_normalized_ratios,
    export_representation_normalization_json,
    export_representation_normalization_markdown,
    normalization_from_representation,
    up_sector_normalization_diagnostic,
)


def test_canonical_unnormalized_ratios_remain_unchanged():
    ratios = compute_yukawa_ratios(build_bhsm_model())

    up_sector_normalization_diagnostic(build_bhsm_model())

    after = compute_yukawa_ratios(build_bhsm_model())
    assert after == ratios
    assert isclose(after["up_quarks"]["middle"], 0.008310500554068288)


def test_candidate_factors_are_diagnostic_not_adopted():
    candidates = candidate_normalization_factors()

    assert {row.status for row in candidates} == {DIAGNOSTIC_ONLY}
    assert all(row.factor > 0 for row in candidates)
    assert not any(row.status == ADOPTED_CANONICAL for row in candidates)


def test_normalization_from_representation_is_not_action_linked_by_default():
    rule = normalization_from_representation(
        "up_quarks",
        (6, 0),
        {"source_rule": "WEAK_DOUBLE_PROJECTION", "applies_to": "pure_fiber_up_nonzero_j0"},
        {},
    )

    assert rule.factor == 0.5
    assert rule.status == DIAGNOSTIC_ONLY
    assert rule.status != ACTION_LINKED


def test_half_factor_on_charm_mode_reduces_ct_near_threshold_reference():
    report = up_sector_normalization_diagnostic(build_bhsm_model())
    weak = next(row for row in report["candidate_factors"] if row["source_rule"] == "WEAK_DOUBLE_PROJECTION")

    assert isclose(weak["factor"], 0.5)
    assert isclose(weak["c_over_t"], 0.004155250277034144)
    assert weak["c_over_t_relative_error"] < 0.03
    assert weak["adopted"] is False


def test_half_factor_all_up_changes_ut_and_ckm_vub():
    report = up_sector_normalization_diagnostic(build_bhsm_model())
    all_up = next(row for row in report["scope_diagnostics"] if row["scope"] == "all_up_sector_modes")
    no_modes = next(row for row in report["scope_diagnostics"] if row["scope"] == "no_modes")

    assert all_up["u_over_t"] != no_modes["u_over_t"]
    assert isclose(all_up["u_over_t"], 6.3452315088030755e-06)
    assert isclose(all_up["sin_theta_13"], 0.0025189742969715027)
    assert all_up["adopted"] is False


def test_pure_fiber_scope_preserves_light_up_ratio():
    report = up_sector_normalization_diagnostic(build_bhsm_model())
    pure = next(row for row in report["scope_diagnostics"] if row["scope"] == "pure_fiber_up_nonzero_j0")
    base = report["base_ratios"]["up_quarks"]["light"]

    assert pure["u_over_t"] == base
    assert pure["c_over_t_relative_error"] < 0.03


def test_apply_normalization_rejects_adopted_canonical_rules_in_audit():
    ratios = compute_yukawa_ratios(build_bhsm_model())
    rule = RepresentationNormalization("up_quarks", (6, 0), 0.5, "TEST", ADOPTED_CANONICAL, "middle_up_mode_only", ())

    with pytest.raises(ValueError):
        apply_normalization_to_ratios(ratios, (rule,))


def test_no_empirical_residual_selects_a_factor():
    report = up_sector_normalization_diagnostic(build_bhsm_model())

    assert report["status_counts"][ACTION_LINKED] == 0
    assert report["status_counts"][ADOPTED_CANONICAL] == 0
    assert "numerically suggestive" in report["conclusion"]


def test_compare_normalized_ratios_reports_ckm_diagnostic():
    rule = RepresentationNormalization("up_quarks", (6, 0), 0.5, "TEST", DIAGNOSTIC_ONLY, "all_up_sector_modes", ())
    comparison = compare_normalized_ratios(build_bhsm_model(), (rule,))

    assert comparison["adopted"] is False
    assert comparison["ckm"]["status"] == DIAGNOSTIC_ONLY
    assert comparison["ckm"]["sin_theta_13"] > 0


def test_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "normalization.md"
    json_path = tmp_path / "normalization.json"

    export_representation_normalization_markdown(build_bhsm_model(), md_path)
    export_representation_normalization_json(build_bhsm_model(), json_path)

    assert "# BHSM Representation-Normalization Audit" in md_path.read_text()
    assert "WEAK_DOUBLE_PROJECTION" in json_path.read_text()


def test_no_claim_status_is_upgraded():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
