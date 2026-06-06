from math import isclose

import pytest

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from quark_running import (
    FIXED_NF_APPROX,
    MZ,
    PIECEWISE_NF_APPROX,
    PLACEHOLDER_PRECISION_QCD,
    alpha_s_piecewise_one_loop,
    build_threshold_common_scale_references,
    charm_mode_diagnostic,
    charm_top_tension_report,
    compare_bhsm_to_common_scale,
    compare_bhsm_to_threshold_common_scale,
    default_thresholds,
    export_charm_top_tension_report_json,
    export_charm_top_tension_report_markdown,
    mass_running_piecewise,
    nf_at_scale,
    top_reference_audit,
)


def test_canonical_bhsm_predictions_do_not_change():
    ratios = compute_yukawa_ratios(build_bhsm_model())

    charm_top_tension_report(build_bhsm_model())

    after = compute_yukawa_ratios(build_bhsm_model())
    assert after == ratios
    assert isclose(after["up_quarks"]["middle"], 0.008310500554068288)
    assert isclose(after["up_quarks"]["light"], 1.2690463017606151e-05)


def test_thresholds_and_nf_are_explicit():
    thresholds = default_thresholds()

    assert [row.particle for row in thresholds] == ["c", "b", "t"]
    assert nf_at_scale(1.0, thresholds) == 3
    assert nf_at_scale(2.0, thresholds) == 4
    assert nf_at_scale(10.0, thresholds) == 5
    assert nf_at_scale(200.0, thresholds) == 6


def test_piecewise_alpha_s_is_finite_and_monotonic():
    assert alpha_s_piecewise_one_loop(10.0) > alpha_s_piecewise_one_loop(MZ)
    assert alpha_s_piecewise_one_loop(200.0) < alpha_s_piecewise_one_loop(MZ)


def test_running_policies_are_labeled_and_precision_placeholder_is_not_implemented():
    fixed = mass_running_piecewise(1.27, MZ, exponent_policy=FIXED_NF_APPROX)
    piecewise = mass_running_piecewise(1.27, MZ, exponent_policy=PIECEWISE_NF_APPROX)

    assert fixed > 0
    assert piecewise > 0
    assert not isclose(fixed, piecewise)
    with pytest.raises(NotImplementedError):
        mass_running_piecewise(1.27, MZ, exponent_policy=PLACEHOLDER_PRECISION_QCD)


def test_fixed_and_piecewise_ct_tension_is_reported():
    model = build_bhsm_model()
    fixed = next(row for row in compare_bhsm_to_common_scale(model, MZ) if row["id"] == "mass_ratio.up_quarks.middle")
    piecewise = next(row for row in compare_bhsm_to_threshold_common_scale(model, MZ) if row["id"] == "mass_ratio.up_quarks.middle")

    assert isclose(fixed["reference"], 0.004266868071316746)
    assert isclose(piecewise["reference"], 0.004251569034944846)
    assert fixed["relative_error"] > 0.9
    assert piecewise["relative_error"] > 0.9
    assert piecewise["status"] == "THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD"


def test_top_reference_variants_are_label_only_sensitivity():
    rows = top_reference_audit(build_bhsm_model(), MZ)
    variants = {row["top_reference_variant"] for row in rows}

    assert variants == {"CURRENT_AMBIGUOUS_TOP", "TOP_POLE_LIKE_CURRENT", "TOP_RUNNING_MASS_PLACEHOLDER"}
    assert all(row["sensitivity_only"] is True for row in rows)
    assert all("reuses current top value" in row["variant_note"] for row in rows)


def test_charm_mode_next_admissible_mode_overcorrects():
    diagnostic = charm_mode_diagnostic(build_bhsm_model())

    assert tuple(diagnostic["current_charm_mode"]["mode"]) == (6, 0)
    assert tuple(diagnostic["next_admissible_mode"]["mode"]) == (10, 1)
    assert diagnostic["next_admissible_mode"]["assessment_vs_threshold_reference"] == "overcorrects"
    assert diagnostic["ledger_changed"] is False


def test_simple_normalization_factor_is_diagnostic_only():
    diagnostic = charm_mode_diagnostic(build_bhsm_model())
    candidates = diagnostic["simple_factor_diagnostic"]

    assert candidates[0]["candidate"] == "1/2"
    assert all(row["diagnostic_only"] is True for row in candidates)
    assert diagnostic["adopted_factor"] is None


def test_threshold_references_are_marked_approximate():
    refs = build_threshold_common_scale_references(MZ)

    assert refs["c"].scheme == "COMMON_SCALE_THRESHOLD_APPROX"
    assert any("approximate threshold-aware scaffold" in note for note in refs["c"].notes)
    assert any("Top reference variant" in note for note in refs["t"].notes)


def test_tension_report_exports_cleanly(tmp_path):
    md_path = tmp_path / "ct.md"
    json_path = tmp_path / "ct.json"

    export_charm_top_tension_report_markdown(build_bhsm_model(), md_path)
    export_charm_top_tension_report_json(build_bhsm_model(), json_path)

    assert "# BHSM Charm/Top Tension Audit" in md_path.read_text()
    text = json_path.read_text()
    assert "piecewise_nf_reference" in text
    assert "model_changed" in text


def test_no_claim_status_is_upgraded():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
