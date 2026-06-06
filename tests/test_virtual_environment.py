from math import isclose

import pytest

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from virtual_environment import (
    ADOPTED_CANONICAL,
    ALL_UP,
    DIAGNOSTIC_ONLY,
    GLOBAL,
    VIRTUAL_ENV_LINKED,
    VirtualDressingRule,
    apply_virtual_dressing,
    bare_to_observed_ratio,
    export_virtual_environment_json,
    export_virtual_environment_markdown,
    pure_fiber_middle_up_rule,
    virtual_dressing_candidates,
    virtual_environment_report,
)


def test_bare_canonical_ratios_are_unchanged():
    ratios = compute_yukawa_ratios(build_bhsm_model())

    virtual_environment_report(build_bhsm_model())

    assert compute_yukawa_ratios(build_bhsm_model()) == ratios
    assert isclose(ratios["up_quarks"]["middle"], 0.008310500554068288)


def test_bare_to_observed_ratio_multiplies_factor():
    assert bare_to_observed_ratio(0.008, 0.5) == 0.004


def test_pure_fiber_middle_up_rule_is_virtual_env_linked_not_adopted():
    rule = pure_fiber_middle_up_rule()

    assert rule.factor == 0.5
    assert rule.status == VIRTUAL_ENV_LINKED
    assert rule.status != ADOPTED_CANONICAL
    assert rule.mode == (6, 0)
    assert "j=0" in " ".join(rule.notes)


def test_diagnostic_candidates_are_not_adopted_by_default():
    candidates = virtual_dressing_candidates(build_bhsm_model())

    assert candidates
    assert {row.status for row in candidates} == {DIAGNOSTIC_ONLY}
    assert not any(row.status == ADOPTED_CANONICAL for row in candidates)


def test_dressed_ct_with_half_matches_phase_28():
    report = virtual_environment_report(build_bhsm_model())
    variants = {row["name"]: row for row in report["model_variants"]}
    dressed = variants["BHSM_VIRTUAL_DRESSED_DIAGNOSTIC"]

    assert isclose(dressed["ratios"]["up_quarks"]["middle"], 0.004155250277034144)
    assert dressed["canonical"] is False


def test_middle_up_dressing_leaves_ut_and_vub_unchanged():
    report = virtual_environment_report(build_bhsm_model())
    variants = {row["name"]: row for row in report["model_variants"]}
    bare = variants["BHSM_BARE_CANONICAL"]
    dressed = variants["BHSM_VIRTUAL_DRESSED_DIAGNOSTIC"]

    assert dressed["ratios"]["up_quarks"]["light"] == bare["ratios"]["up_quarks"]["light"]
    assert dressed["ckm"]["sin_theta_13"] == bare["ckm"]["sin_theta_13"]


def test_global_and_all_up_half_are_reported_separately_not_adopted():
    model = build_bhsm_model()
    global_rule = VirtualDressingRule("all", "all", "all", 0.5, "SCOPE_TEST", GLOBAL, DIAGNOSTIC_ONLY, ())
    all_up_rule = VirtualDressingRule("up_quarks", "all", "all", 0.5, "SCOPE_TEST", ALL_UP, DIAGNOSTIC_ONLY, ())

    global_ratios = apply_virtual_dressing(model, (global_rule,))
    all_up_ratios = apply_virtual_dressing(model, (all_up_rule,))

    assert isclose(global_ratios["down_quarks"]["middle"], 0.010966985747719737)
    assert isclose(all_up_ratios["down_quarks"]["middle"], 0.021933971495439474)
    assert isclose(all_up_ratios["up_quarks"]["light"], 6.3452315088030755e-06)
    assert global_rule.status == DIAGNOSTIC_ONLY
    assert all_up_rule.status == DIAGNOSTIC_ONLY


def test_no_empirical_residual_is_used_for_linkage():
    report = virtual_environment_report(build_bhsm_model())

    assert report["linkage_test"]["uses_empirical_residual"] is False
    assert report["linkage_test"]["passes"] is True
    assert report["canonical_changed"] is False


def test_adopted_canonical_rule_is_rejected_in_audit_application():
    rule = VirtualDressingRule("up_quarks", "middle", (6, 0), 0.5, "TEST", "MODE_SPECIFIC", ADOPTED_CANONICAL, ())

    with pytest.raises(ValueError):
        apply_virtual_dressing(build_bhsm_model(), (rule,))


def test_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "virtual.md"
    json_path = tmp_path / "virtual.json"

    export_virtual_environment_markdown(build_bhsm_model(), md_path)
    export_virtual_environment_json(build_bhsm_model(), json_path)

    assert "# BHSM Virtual-Environment Dressing Audit" in md_path.read_text()
    assert "BHSM_VIRTUAL_DRESSED_DIAGNOSTIC" in json_path.read_text()


def test_claim_status_is_not_upgraded_to_canonical_prediction():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
