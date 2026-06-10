import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_curvature_formula_closure import BUNDLE_CURVATURE_FORMULA_CLOSED, build_bundle_curvature_formula_closure_report, export_bundle_curvature_formula_closure_json, export_bundle_curvature_formula_closure_markdown
from bundle_curvature_formula_decision import build_bundle_curvature_formula_decision, export_bundle_curvature_formula_decision_json, export_bundle_curvature_formula_decision_markdown
from bundle_curvature_term_map import CURVATURE_OPEN, CURVATURE_REAL_MISSING_TERM, build_bundle_curvature_term_map_report, export_bundle_curvature_term_map_json, export_bundle_curvature_term_map_markdown
from constants import S_OVERLAP
from curvature_remainder_after_mixed_rule import REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, build_curvature_remainder_after_mixed_rule_report, export_curvature_remainder_after_mixed_rule_json, export_curvature_remainder_after_mixed_rule_markdown
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import build_full_ht_theorem_closure_report
from mixed_coefficient_rule_decision import MIXED_COEFFICIENT_RULE_CLOSED, build_mixed_coefficient_rule_decision
from mixed_connection_closure_decision import MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, build_mixed_connection_closure_decision
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_operator_identification_theorem_report
from topographic_curvature_representation import TOPOGRAPHIC_CURVATURE_REPRESENTATION_CLOSED, build_topographic_curvature_representation_report, export_topographic_curvature_representation_json, export_topographic_curvature_representation_markdown


def test_v211_mixed_rule_remains_closed_and_not_reopened():
    rule = build_mixed_coefficient_rule_decision()
    mixed = build_mixed_connection_closure_decision()

    assert rule.final_result == MIXED_COEFFICIENT_RULE_CLOSED
    assert mixed.mixed_connection_classification == MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert mixed.exact_remaining_gap == ""


def test_every_bundle_curvature_contribution_is_classified_once():
    report = build_bundle_curvature_term_map_report()
    ids = [row.contribution_id for row in report.rows]

    assert len(ids) == len(set(ids))
    assert report.all_contributions_classified_once is True
    assert report.open_or_missing_terms == ()
    assert all(row.classification not in {CURVATURE_OPEN, CURVATURE_REAL_MISSING_TERM} for row in report.rows)
    assert report.r_bundle_contributors == ()


def test_topographic_curvature_representation_closes_independent_r_bundle():
    topo = build_topographic_curvature_representation_report()
    remainder = build_curvature_remainder_after_mixed_rule_report()

    assert topo.status == TOPOGRAPHIC_CURVATURE_REPRESENTATION_CLOSED
    assert topo.contributes_independent_r_bundle is False
    assert topo.lower_bound_requires_new_term is False
    assert remainder.r_bundle_classification == REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert remainder.relative_bound_added == 0.0
    assert remainder.lower_bound_requires_new_term is False
    assert remainder.mirror_leakage_introduced is False
    assert remainder.formal_kernel_sector_labeled is True


def test_bundle_curvature_formula_decision_closes_without_final_paper():
    closure = build_bundle_curvature_formula_closure_report()
    decision = build_bundle_curvature_formula_decision()

    assert closure.status == BUNDLE_CURVATURE_FORMULA_CLOSED
    assert closure.r_bundle_classification == REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert decision.final_result == BUNDLE_CURVATURE_FORMULA_CLOSED
    assert decision.exact_remaining_gap == ""
    assert decision.final_paper_allowed is False
    assert decision.theorem_complete is True


def test_complete_operator_and_full_ht_are_not_overclaimed():
    operator = build_operator_identification_theorem_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert operator.status != COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert operator.next_target_theorem == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP"
    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == "COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP"
    assert bhsm.final_paper_allowed is False


def test_formal_kernel_remains_sector_labeled_and_not_coordinate_first():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v212_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "bundle_curvature_formula_closure.py",
            "bundle_curvature_term_map.py",
            "curvature_remainder_after_mixed_rule.py",
            "topographic_curvature_representation.py",
            "bundle_curvature_formula_decision.py",
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
    )
    assert all(token not in source for token in forbidden)


def test_v212_exports_generate(tmp_path):
    exporters = (
        (export_bundle_curvature_formula_closure_markdown, export_bundle_curvature_formula_closure_json, "closure"),
        (export_bundle_curvature_term_map_markdown, export_bundle_curvature_term_map_json, "term_map"),
        (export_curvature_remainder_after_mixed_rule_markdown, export_curvature_remainder_after_mixed_rule_json, "remainder"),
        (export_topographic_curvature_representation_markdown, export_topographic_curvature_representation_json, "topographic"),
        (export_bundle_curvature_formula_decision_markdown, export_bundle_curvature_formula_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v212_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/bundle_curvature_formula_closure_report.md",
        "theory/bundle_curvature_formula_closure_report.json",
        "theory/bundle_curvature_term_map_report.md",
        "theory/bundle_curvature_term_map_report.json",
        "theory/curvature_remainder_after_mixed_rule_report.md",
        "theory/curvature_remainder_after_mixed_rule_report.json",
        "theory/topographic_curvature_representation_report.md",
        "theory/topographic_curvature_representation_report.json",
        "theory/bundle_curvature_formula_decision.md",
        "theory/bundle_curvature_formula_decision.json",
        "manuscript/BHSM_v2_12_bundle_curvature_formula_closure_note.md",
        "notebooks/62_bundle_curvature_formula_closure.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []


def test_v212_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_bundle_curvature_formula_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]

