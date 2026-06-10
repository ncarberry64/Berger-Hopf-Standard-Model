import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_curvature_formula_decision import BUNDLE_CURVATURE_FORMULA_CLOSED, build_bundle_curvature_formula_decision
from complete_operator_action_uniqueness_decision import (
    COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED,
    build_complete_operator_action_uniqueness_decision,
    export_complete_operator_action_uniqueness_decision_json,
    export_complete_operator_action_uniqueness_decision_markdown,
)
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from complete_operator_identification_decision import build_complete_operator_identification_decision
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_complete_twisted_dirac_operator_report
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP, build_full_ht_theorem_closure_report
from mixed_coefficient_rule_decision import MIXED_COEFFICIENT_RULE_CLOSED, build_mixed_coefficient_rule_decision
from operator_action_uniqueness import (
    BLOCKING_INGREDIENT_STATUSES,
    build_operator_action_uniqueness_report,
    export_operator_action_uniqueness_json,
    export_operator_action_uniqueness_markdown,
)
from operator_alternative_term_audit import (
    BLOCKING_CLASSIFICATIONS,
    build_operator_alternative_term_audit_report,
    export_operator_alternative_term_audit_json,
    export_operator_alternative_term_audit_markdown,
)
from operator_axiom_uniqueness import (
    COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN,
    build_operator_axiom_uniqueness_report,
    export_operator_axiom_uniqueness_json,
    export_operator_axiom_uniqueness_markdown,
)
from operator_identification_theorem import build_operator_identification_theorem_report
from operator_variation_audit import VARIATION_AUDIT_CLOSED, build_operator_variation_audit_report, export_operator_variation_audit_json, export_operator_variation_audit_markdown
from parent_action_to_operator import OPERATOR_DERIVED_FROM_ACTION, build_parent_action_to_operator_report, export_parent_action_to_operator_json, export_parent_action_to_operator_markdown


def test_action_ingredients_are_all_classified_without_open_inputs():
    report = build_operator_action_uniqueness_report()

    assert report.all_ingredients_classified is True
    assert report.blocking_ingredients == ()
    assert report.theorem_complete is True
    assert not [row for row in report.ingredients if row.status in BLOCKING_INGREDIENT_STATUSES]


def test_parent_action_reduces_to_complete_operator_package():
    report = build_parent_action_to_operator_report()

    assert report.status == OPERATOR_DERIVED_FROM_ACTION
    assert report.theorem_complete is True
    assert report.missing_operator_terms == ()
    assert report.represented_operator_package == (
        "A0",
        "V_Hopf",
        "V_boundary",
        "V_chi",
        "K_sector",
        "P_perp_lift",
        "V_PSD",
        "topographic represented sector",
    )


def test_variation_and_alternative_term_audits_close_without_empirical_selection():
    variation = build_operator_variation_audit_report()
    alternatives = build_operator_alternative_term_audit_report()

    assert variation.status == VARIATION_AUDIT_CLOSED
    assert variation.open_variations == ()
    assert alternatives.all_alternatives_classified is True
    assert alternatives.real_missing_terms == ()
    assert alternatives.open_terms == ()
    assert alternatives.uniqueness_breaking_terms == ()
    assert not [row for row in alternatives.alternatives if row.classification in BLOCKING_CLASSIFICATIONS]
    assert {row.term_id for row in alternatives.alternatives} >= {
        "additional_hopf_base_mixed",
        "additional_boundary_coframe",
        "additional_chirality_mixing",
        "additional_sector_off_diagonal",
        "additional_higgs_u1_mirror",
        "additional_scalar_topographic_leakage",
        "additional_psd_profile",
        "torsion_like_term",
        "connection_curvature_remainder",
        "independent_free_mixed_coefficient",
    }


def test_operator_action_uniqueness_closes_and_upgrades_identification():
    uniqueness = build_operator_axiom_uniqueness_report()
    decision = build_complete_operator_action_uniqueness_decision()
    twisted = build_complete_twisted_dirac_operator_report()
    theorem = build_operator_identification_theorem_report()
    v26 = build_complete_operator_identification_decision()
    closure = build_complete_operator_identification_closure_report()

    assert uniqueness.status == COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN
    assert decision.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
    assert decision.complete_operator_identification_may_upgrade is True
    assert twisted.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert theorem.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert v26.final_result == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert closure.final_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert closure.theorem_complete is True


def test_full_ht_is_not_overclaimed_after_operator_identification_closes():
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert ht.complete_operator_status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert ht.theorem_complete is False
    assert ht.final_result == "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
    assert ht.single_named_gap == PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP
    assert ht.recommended_next_branch == "bhsm-v2.15-projector-graph-domain-stability"
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False
    assert bhsm.recommended_target_theorem == PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP


def test_v211_v212_topographic_closures_remain_intact():
    mixed = build_mixed_coefficient_rule_decision()
    curvature = build_bundle_curvature_formula_decision()

    assert mixed.final_result == MIXED_COEFFICIENT_RULE_CLOSED
    assert curvature.final_result == BUNDLE_CURVATURE_FORMULA_CLOSED
    assert curvature.r_bundle_classification == "REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"


def test_formal_kernel_remains_sector_labeled_and_not_coordinate_first():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v213_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "operator_action_uniqueness.py",
            "parent_action_to_operator.py",
            "operator_variation_audit.py",
            "operator_alternative_term_audit.py",
            "operator_axiom_uniqueness.py",
            "complete_operator_action_uniqueness_decision.py",
        )
    )
    forbidden = (
        "from prediction_ledger",
        "import prediction_ledger",
        "from residual_audit",
        "import residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "compute_ckm",
        "compute_pmns",
        "relative_error",
    )
    assert all(token not in source for token in forbidden)


def test_v213_exports_generate(tmp_path):
    exporters = (
        (export_operator_action_uniqueness_markdown, export_operator_action_uniqueness_json, "action"),
        (export_parent_action_to_operator_markdown, export_parent_action_to_operator_json, "parent"),
        (export_operator_variation_audit_markdown, export_operator_variation_audit_json, "variation"),
        (export_operator_alternative_term_audit_markdown, export_operator_alternative_term_audit_json, "alternatives"),
        (export_operator_axiom_uniqueness_markdown, export_operator_axiom_uniqueness_json, "axiom"),
        (export_complete_operator_action_uniqueness_decision_markdown, export_complete_operator_action_uniqueness_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v213_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/operator_action_uniqueness_report.md",
        "theory/operator_action_uniqueness_report.json",
        "theory/parent_action_to_operator_report.md",
        "theory/parent_action_to_operator_report.json",
        "theory/operator_variation_audit.md",
        "theory/operator_variation_audit.json",
        "theory/operator_alternative_term_audit.md",
        "theory/operator_alternative_term_audit.json",
        "theory/operator_axiom_uniqueness_report.md",
        "theory/operator_axiom_uniqueness_report.json",
        "theory/complete_operator_action_uniqueness_decision.md",
        "theory/complete_operator_action_uniqueness_decision.json",
        "manuscript/BHSM_v2_13_complete_operator_action_uniqueness_note.md",
        "notebooks/63_complete_operator_action_uniqueness.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []


def test_v213_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_complete_operator_action_uniqueness_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
