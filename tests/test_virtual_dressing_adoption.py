from math import isclose

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from virtual_environment import (
    ADOPTED_CANONICAL_DRESSED,
    ADOPTION_CANDIDATE,
    VIRTUAL_ENV_LINKED,
    adoption_report,
    bare_vs_dressed_prediction_ledger,
    compare_bare_vs_dressed_model,
    evaluate_dressing_adoption,
    export_bare_vs_dressed_prediction_ledger_json,
    export_bare_vs_dressed_prediction_ledger_markdown,
    export_virtual_dressing_adoption_json,
    export_virtual_dressing_adoption_markdown,
    pure_fiber_middle_up_rule,
    virtual_dressed_model_variant,
)


def test_bare_canonical_model_remains_unchanged():
    model = build_bhsm_model()
    before = compute_yukawa_ratios(model)

    adoption_report(model, pure_fiber_middle_up_rule())

    assert compute_yukawa_ratios(model) == before
    assert isclose(before["up_quarks"]["middle"], 0.008310500554068288)


def test_dressed_candidate_applies_only_to_ct():
    model = build_bhsm_model()
    report = adoption_report(model, pure_fiber_middle_up_rule())

    assert report["changed_outputs"] == ("up_quarks.middle",)
    assert report["unrelated_sectors_changed"] == ()
    assert report["canonical_model_mutated"] is False


def test_ut_and_ckm_sin13_remain_unchanged():
    model = build_bhsm_model()
    comparison = compare_bare_vs_dressed_model(model, (pure_fiber_middle_up_rule(),))
    bare, dressed = comparison["variants"]

    assert dressed["ratios"]["up_quarks"]["light"] == bare["ratios"]["up_quarks"]["light"]
    assert dressed["ckm"]["sin_theta_13"] == bare["ckm"]["sin_theta_13"]


def test_criteria_c1_through_c6_are_explicitly_evaluated():
    evaluation = evaluate_dressing_adoption(pure_fiber_middle_up_rule(), build_bhsm_model())
    criteria = {criterion.id: criterion for criterion in evaluation["criteria"]}

    assert set(criteria) == {"C1", "C2", "C3", "C4", "C5", "C6"}
    assert all(criterion.passes for criterion in criteria.values())
    assert all(criterion.evidence for criterion in criteria.values())
    assert all(criterion.limitations for criterion in criteria.values())


def test_no_empirical_residual_is_used_to_derive_rule():
    report = adoption_report(build_bhsm_model(), pure_fiber_middle_up_rule())
    c2 = next(row for row in report["criteria"] if row["id"] == "C2")

    assert c2["passes"] is True
    assert "not by c/t residual" in " ".join(c2["evidence"])


def test_status_becomes_adoption_candidate_if_all_criteria_pass():
    rule = pure_fiber_middle_up_rule()
    report = adoption_report(build_bhsm_model(), rule)

    assert rule.status == VIRTUAL_ENV_LINKED
    assert report["all_criteria_pass"] is True
    assert report["rule_status_after_audit"] == ADOPTION_CANDIDATE
    assert report["rule_status_after_audit"] != ADOPTED_CANONICAL_DRESSED


def test_no_rule_is_marked_adopted_canonical_dressed():
    report = adoption_report(build_bhsm_model(), pure_fiber_middle_up_rule())
    ledger = bare_vs_dressed_prediction_ledger(build_bhsm_model(), pure_fiber_middle_up_rule())

    assert report["adopted_canonical_dressed"] is False
    assert all(row["status"] != ADOPTED_CANONICAL_DRESSED for row in ledger)


def test_virtual_dressed_model_variant_is_candidate_not_canonical():
    variant = virtual_dressed_model_variant(build_bhsm_model(), (pure_fiber_middle_up_rule(),), adopted=False)

    assert variant["name"] == "BHSM_DRESSED_CANDIDATE"
    assert variant["canonical"] is False
    assert variant["adopted"] is False
    assert isclose(variant["ratios"]["up_quarks"]["middle"], 0.004155250277034144)


def test_bare_vs_dressed_prediction_ledger_has_two_variants():
    ledger = bare_vs_dressed_prediction_ledger(build_bhsm_model(), pure_fiber_middle_up_rule())
    variants = {row["variant"] for row in ledger}

    assert variants == {"BHSM_BARE_CANONICAL", "BHSM_DRESSED_CANDIDATE"}
    assert any(row["quantity"] == "c/t" and row["value"] == 0.004155250277034144 for row in ledger)


def test_exports_generate_cleanly(tmp_path):
    model = build_bhsm_model()
    rule = pure_fiber_middle_up_rule()
    adoption_md = tmp_path / "adoption.md"
    adoption_json = tmp_path / "adoption.json"
    ledger_md = tmp_path / "ledger.md"
    ledger_json = tmp_path / "ledger.json"

    export_virtual_dressing_adoption_markdown(model, rule, adoption_md)
    export_virtual_dressing_adoption_json(model, rule, adoption_json)
    export_bare_vs_dressed_prediction_ledger_markdown(model, rule, ledger_md)
    export_bare_vs_dressed_prediction_ledger_json(model, rule, ledger_json)

    assert "ADOPTION_CANDIDATE" in adoption_md.read_text()
    assert "C1" in adoption_json.read_text()
    assert "BHSM_DRESSED_CANDIDATE" in ledger_md.read_text()
    assert "BHSM_BARE_CANONICAL" in ledger_json.read_text()
