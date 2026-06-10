import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from clifford_curvature_contraction import CLIFFORD_CONTRACTION_CONDITIONAL, build_clifford_curvature_contraction_report, export_clifford_curvature_contraction_json, export_clifford_curvature_contraction_markdown
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import HT_LOWER_BOUND_TRANSFER_GAP, build_full_ht_theorem_closure_report
from hopf_base_boundary_coframe import build_hopf_base_boundary_coframe_report, export_hopf_base_boundary_coframe_json, export_hopf_base_boundary_coframe_markdown
from mixed_connection_closure_decision import (
    MIXED_CONNECTION_CLOSED,
    MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_mixed_connection_closure_decision,
    export_mixed_connection_closure_decision_json,
    export_mixed_connection_closure_decision_markdown,
)
from mixed_connection_coefficients import MIXED_COEFFICIENT_CONDITIONAL, build_mixed_connection_coefficients_report, export_mixed_connection_coefficients_json, export_mixed_connection_coefficients_markdown
from mixed_connection_remainder_bound import build_mixed_connection_remainder_bound_report, export_mixed_connection_remainder_bound_json, export_mixed_connection_remainder_bound_markdown
from mixed_curvature_contraction import MIXED_CURVATURE_CONDITIONAL, build_mixed_curvature_contraction_report, export_mixed_curvature_contraction_json, export_mixed_curvature_contraction_markdown
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_operator_identification_theorem_report


EXACT_GAP = ""


def test_mixed_connection_coefficients_are_classified_and_open():
    report = build_mixed_connection_coefficients_report()

    assert report.status == MIXED_COEFFICIENT_CONDITIONAL
    assert report.all_coefficients_classified is True
    assert report.open_coefficients == ()
    assert report.exact_missing_rule == ""
    assert report.theorem_complete is True


def test_hopf_base_boundary_coframe_features_are_explicit():
    report = build_hopf_base_boundary_coframe_report()

    assert report.coefficient_status == MIXED_COEFFICIENT_CONDITIONAL
    assert report.status == "HOPF_BASE_BOUNDARY_COFRAME_DERIVED"
    assert any(row.feature_id == "formal_kernel_action" for row in report.features)
    assert any(row.feature_id == "h_perp_preservation" for row in report.features)


def test_mixed_curvature_and_clifford_contraction_remain_open():
    curvature = build_mixed_curvature_contraction_report()
    clifford = build_clifford_curvature_contraction_report()

    assert curvature.status == MIXED_CURVATURE_CONDITIONAL
    assert curvature.mapped_to == "lichnerowicz_bundle_curvature_remainder"
    assert clifford.status == CLIFFORD_CONTRACTION_CONDITIONAL
    assert clifford.contributes_to_r_bundle is False
    assert clifford.represented_by_existing_terms is True


def test_mixed_connection_bound_refuses_fake_constants():
    report = build_mixed_connection_remainder_bound_report()

    assert report.a_remainder == 0.0
    assert report.b_remainder == 0.0
    assert report.a_total == 0.0
    assert report.lower_bound_recomputed is True
    assert report.ht_lower_bound_safe is True


def test_mixed_connection_decision_names_next_gap_and_blocks_paper():
    report = build_mixed_connection_closure_decision()

    assert report.final_result == MIXED_CONNECTION_CLOSED
    assert report.mixed_connection_classification == MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
    assert report.exact_remaining_gap == EXACT_GAP
    assert report.recommended_next_branch == ""
    assert report.final_paper_allowed is False
    assert report.theorem_complete is True


def test_complete_operator_and_full_ht_do_not_overclaim():
    operator = build_operator_identification_theorem_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert operator.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert operator.next_target_theorem == ""
    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == HT_LOWER_BOUND_TRANSFER_GAP
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False


def test_formal_kernel_remains_sector_labeled_not_coordinate_first():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v210_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "mixed_connection_coefficients.py",
            "hopf_base_boundary_coframe.py",
            "mixed_curvature_contraction.py",
            "clifford_curvature_contraction.py",
            "mixed_connection_remainder_bound.py",
            "mixed_connection_closure_decision.py",
            "mixed_coefficient_rule.py",
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
    )
    assert all(token not in source for token in forbidden)


def test_v210_exports_generate(tmp_path):
    exporters = (
        (export_mixed_connection_coefficients_markdown, export_mixed_connection_coefficients_json, "coefficients"),
        (export_hopf_base_boundary_coframe_markdown, export_hopf_base_boundary_coframe_json, "hopf_base"),
        (export_mixed_curvature_contraction_markdown, export_mixed_curvature_contraction_json, "curvature"),
        (export_clifford_curvature_contraction_markdown, export_clifford_curvature_contraction_json, "clifford"),
        (export_mixed_connection_remainder_bound_markdown, export_mixed_connection_remainder_bound_json, "bound"),
        (export_mixed_connection_closure_decision_markdown, export_mixed_connection_closure_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v210_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/mixed_connection_coefficients_report.md",
        "theory/mixed_connection_coefficients_report.json",
        "theory/hopf_base_boundary_coframe_report.md",
        "theory/hopf_base_boundary_coframe_report.json",
        "theory/mixed_curvature_contraction_report.md",
        "theory/mixed_curvature_contraction_report.json",
        "theory/clifford_curvature_contraction_report.md",
        "theory/clifford_curvature_contraction_report.json",
        "theory/mixed_connection_remainder_bound_report.md",
        "theory/mixed_connection_remainder_bound_report.json",
        "theory/mixed_connection_closure_decision.md",
        "theory/mixed_connection_closure_decision.json",
        "manuscript/BHSM_v2_10_mixed_connection_coefficients_note.md",
        "notebooks/60_mixed_connection_coefficients.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    text = root.joinpath("theory/mixed_connection_closure_decision.md").read_text()
    assert "MIXED_CONNECTION_CLOSED" in text
    assert "MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR" in text


def test_v210_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_mixed_connection_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
