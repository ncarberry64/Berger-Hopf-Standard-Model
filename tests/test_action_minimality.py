from math import isclose
from pathlib import Path

from action_minimality import build_minimality_audit, evaluate_minimality_variant, minimality_variants
from action_minimality import export_minimality_audit_json, export_minimality_audit_markdown
from action_uniqueness import (
    UniquenessStatus,
    build_uniqueness_audit,
    evaluate_uniqueness_variant,
    export_uniqueness_audit_json,
    export_uniqueness_audit_markdown,
    uniqueness_variants,
)
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


def test_minimality_failures_are_explicit_for_removed_terms():
    report = build_minimality_audit()

    assert report.status == "MINIMAL_UNDER_TESTED_PARENT_TERMS"
    assert report.theorem_complete is False
    assert all(criterion.passes for criterion in report.criteria)
    assert {criterion.removed_term for criterion in report.criteria} == {
        "I_HOPF",
        "I_U1",
        "I_BASE",
        "I_WEAK",
        "I_COF",
        "I_BDY",
    }


def test_removing_required_terms_does_not_silently_keep_coefficients():
    by_term = {variant.removed_terms[0]: variant for variant in minimality_variants()}

    for term in ("I_HOPF", "I_U1"):
        outcomes = evaluate_minimality_variant(by_term[term])
        assert all(outcome.fiber_status == "OPEN" for outcome in outcomes)
    for term in ("I_BASE", "I_WEAK", "I_COF"):
        outcomes = evaluate_minimality_variant(by_term[term])
        assert all(outcome.base_status == "OPEN" for outcome in outcomes)
    outcomes = evaluate_minimality_variant(by_term["I_BDY"])
    assert all(outcome.target_status == "OPEN" for outcome in outcomes)


def test_uniqueness_variants_are_reported_not_hidden():
    variants = uniqueness_variants()
    report = build_uniqueness_audit()

    assert {variant.id for variant in variants} == {criterion.variant_id for criterion in report.criteria}
    assert report.theorem_complete is False
    assert all(criterion.status in set(UniquenessStatus) for criterion in report.criteria)


def test_controlled_variants_do_not_recover_mode_ledger_under_current_axioms():
    report = build_uniqueness_audit()

    assert report.status == "UNIQUE_UNDER_BHSM_AXIOMS"
    assert all(not criterion.recovers_mode_ledger for criterion in report.criteria)
    assert all(criterion.frozen_outputs_would_change_if_adopted for criterion in report.criteria)
    assert all(criterion.status == UniquenessStatus.FAILS_SM_LEDGER for criterion in report.criteria)


def test_specific_variants_change_expected_equations_or_open_them():
    by_id = {variant.id: variant for variant in uniqueness_variants()}

    flipped = evaluate_uniqueness_variant(by_id["flip_hopf_orientation"])
    disabled = evaluate_uniqueness_variant(by_id["disable_higgs_u1"])

    assert flipped.equations["up"] != "Omega_u = q-2j = 6"
    assert "OPEN" in disabled.equations["lepton"]
    assert disabled.status == UniquenessStatus.FAILS_SM_LEDGER


def test_no_forbidden_empirical_modules_are_imported_by_action_audits():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("action_minimality.py", "action_uniqueness.py")
    )
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_minimality_uniqueness_audits_do_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_minimality_audit()
    build_uniqueness_audit()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_action_audit_exports_generate_cleanly(tmp_path):
    min_md = tmp_path / "minimality.md"
    min_json = tmp_path / "minimality.json"
    uniq_md = tmp_path / "uniqueness.md"
    uniq_json = tmp_path / "uniqueness.json"

    export_minimality_audit_markdown(min_md)
    export_minimality_audit_json(min_json)
    export_uniqueness_audit_markdown(uniq_md)
    export_uniqueness_audit_json(uniq_json)

    assert "Parent-Action Minimality Audit" in min_md.read_text()
    assert "MINIMAL_UNDER_TESTED_PARENT_TERMS" in min_json.read_text()
    assert "Parent-Action Uniqueness Audit" in uniq_md.read_text()
    assert "UNIQUE_UNDER_BHSM_AXIOMS" in uniq_json.read_text()
