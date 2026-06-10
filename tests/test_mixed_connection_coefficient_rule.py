import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from boundary_coframe_compatibility import (
    BOUNDARY_COFRAME_OPEN,
    build_boundary_coframe_compatibility_report,
    export_boundary_coframe_compatibility_json,
    export_boundary_coframe_compatibility_markdown,
)
from bundle_separation_axiom import (
    BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION,
    BUNDLE_SEPARATION_AXIOM_FORMALIZED,
    build_bundle_separation_axiom_report,
    export_bundle_separation_axiom_json,
    export_bundle_separation_axiom_markdown,
)
from coframe_compatibility_rule import (
    COFRAME_COMPATIBILITY_OPEN,
    build_coframe_compatibility_rule_report,
    export_coframe_compatibility_rule_json,
    export_coframe_compatibility_rule_markdown,
)
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import build_full_ht_theorem_closure_report
from hopf_base_mixed_rule import (
    HOPF_BASE_MIXED_OPEN,
    build_hopf_base_mixed_rule_report,
    export_hopf_base_mixed_rule_json,
    export_hopf_base_mixed_rule_markdown,
)
from mixed_coefficient_minimality import (
    MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS,
    build_mixed_coefficient_minimality_report,
    export_mixed_coefficient_minimality_json,
    export_mixed_coefficient_minimality_markdown,
)
from mixed_coefficient_rule import (
    MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    build_mixed_coefficient_rule_report,
    export_mixed_coefficient_rule_json,
    export_mixed_coefficient_rule_markdown,
)
from mixed_coefficient_rule_decision import (
    MIXED_COEFFICIENT_RULE_CLOSED,
    build_mixed_coefficient_rule_decision,
    export_mixed_coefficient_rule_decision_json,
    export_mixed_coefficient_rule_decision_markdown,
)
from mixed_connection_closure_decision import MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, build_mixed_connection_closure_decision
from topographic_representation_rule import (
    TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED,
    build_topographic_representation_rule_report,
    export_topographic_representation_rule_json,
    export_topographic_representation_rule_markdown,
)


EXACT_GAP = ""
NEXT_BRANCH = ""


def test_every_mixed_coefficient_slot_is_classified_without_values():
    report = build_mixed_coefficient_rule_report()

    assert report.rule_status == MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert report.all_slots_classified is True
    assert report.exact_missing_axiom == EXACT_GAP
    assert report.theorem_complete is True
    assert {row.slot for row in report.rows} == {
        "hopf_fiber_base_cross",
        "base_boundary_cross",
        "boundary_coframe_cross",
        "hopf_boundary_coframe_mixed",
        "chirality_dependence",
        "sector_dependence",
    }
    assert all(row.independent_free_coefficient_forbidden for row in report.rows)
    assert all(row.contributes_to_r_bundle is False for row in report.rows)


def test_bundle_separation_and_topographic_representation_axioms_are_explicit():
    axiom = build_bundle_separation_axiom_report()
    topo = build_topographic_representation_rule_report()

    assert axiom.axiom_id == BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION
    assert axiom.status == BUNDLE_SEPARATION_AXIOM_FORMALIZED
    assert axiom.forbids_free_mixed_coefficient is True
    assert axiom.allows_topographic_representation is True
    assert topo.status == TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED
    assert topo.all_slots_represented_or_zero is True
    assert topo.real_missing_terms == ()


def test_coframe_boundary_and_hopf_base_reports_keep_rule_open():
    coframe = build_coframe_compatibility_rule_report()
    boundary = build_boundary_coframe_compatibility_report()
    hopf = build_hopf_base_mixed_rule_report()

    assert coframe.status != COFRAME_COMPATIBILITY_OPEN
    assert coframe.triplet_required is True
    assert coframe.singlet_variant_fails is True
    assert coframe.coefficient_rule_fixed is True
    assert boundary.status != BOUNDARY_COFRAME_OPEN
    assert boundary.missing_axiom == EXACT_GAP
    assert hopf.status != HOPF_BASE_MIXED_OPEN
    assert hopf.missing_axiom == EXACT_GAP
    assert hopf.preserves_formal_kernel is True


def test_minimality_and_variant_audit_is_present_but_not_unique():
    report = build_mixed_coefficient_minimality_report()

    assert report.minimality_status == MINIMALITY_AUDIT_PASSES_UNDER_BHSM_AXIOMS
    assert report.uniqueness_status == "UNIQUE_REPRESENTATION_RULE_UNDER_BHSM_AXIOMS"
    assert {row.variant_id for row in report.variants} >= {
        "coefficient_zero",
        "sign_flipped",
        "coframe_singlet",
        "chirality_blind",
        "sector_blind",
    }
    assert report.theorem_complete is True


def test_rule_decision_blocks_mixed_connection_and_names_next_gap():
    decision = build_mixed_coefficient_rule_decision()
    mixed = build_mixed_connection_closure_decision()

    assert decision.final_result == MIXED_COEFFICIENT_RULE_CLOSED
    assert decision.exact_remaining_gap == EXACT_GAP
    assert decision.recommended_next_branch == NEXT_BRANCH
    assert decision.mixed_connection_may_close is True
    assert decision.final_paper_allowed is False
    assert mixed.mixed_connection_classification == MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert mixed.exact_remaining_gap == EXACT_GAP
    assert mixed.recommended_next_branch == NEXT_BRANCH


def test_formal_kernel_is_sector_labeled_and_coordinate_first_not_used():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_full_ht_and_bhsm_package_do_not_overclaim():
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP"
    assert ht.recommended_next_branch == "bhsm-v2.13-complete-operator-action-uniqueness"
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False
    assert bhsm.recommended_target_theorem == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP"


def test_v211_modules_do_not_import_empirical_or_residual_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "mixed_coefficient_rule.py",
            "bundle_separation_axiom.py",
            "topographic_representation_rule.py",
            "coframe_compatibility_rule.py",
            "boundary_coframe_compatibility.py",
            "hopf_base_mixed_rule.py",
            "mixed_coefficient_minimality.py",
            "mixed_coefficient_rule_decision.py",
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
        "reference_mass",
        "relative_error",
    )
    assert all(token not in source for token in forbidden)


def test_v211_exports_generate(tmp_path):
    exporters = (
        (export_mixed_coefficient_rule_markdown, export_mixed_coefficient_rule_json, "rule"),
        (export_bundle_separation_axiom_markdown, export_bundle_separation_axiom_json, "axiom"),
        (export_topographic_representation_rule_markdown, export_topographic_representation_rule_json, "topographic"),
        (export_coframe_compatibility_rule_markdown, export_coframe_compatibility_rule_json, "coframe"),
        (export_boundary_coframe_compatibility_markdown, export_boundary_coframe_compatibility_json, "boundary"),
        (export_hopf_base_mixed_rule_markdown, export_hopf_base_mixed_rule_json, "hopf"),
        (export_mixed_coefficient_minimality_markdown, export_mixed_coefficient_minimality_json, "minimality"),
        (export_mixed_coefficient_rule_decision_markdown, export_mixed_coefficient_rule_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_v211_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_mixed_coefficient_rule_decision()
    build_mixed_connection_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_requested_v211_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/mixed_coefficient_rule_report.md",
        "theory/mixed_coefficient_rule_report.json",
        "theory/bundle_separation_axiom_report.md",
        "theory/bundle_separation_axiom_report.json",
        "theory/topographic_representation_rule_report.md",
        "theory/topographic_representation_rule_report.json",
        "theory/coframe_compatibility_rule_report.md",
        "theory/coframe_compatibility_rule_report.json",
        "theory/boundary_coframe_compatibility_report.md",
        "theory/boundary_coframe_compatibility_report.json",
        "theory/hopf_base_mixed_rule_report.md",
        "theory/hopf_base_mixed_rule_report.json",
        "theory/mixed_coefficient_minimality_report.md",
        "theory/mixed_coefficient_minimality_report.json",
        "theory/mixed_coefficient_rule_decision.md",
        "theory/mixed_coefficient_rule_decision.json",
        "manuscript/BHSM_v2_11_mixed_connection_coefficient_rule_note.md",
        "notebooks/61_mixed_connection_coefficient_rule.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
