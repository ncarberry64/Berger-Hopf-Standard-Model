import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from curvature_remainder_basis_action import REMAINDER_BASIS_ACTION_OPEN, build_curvature_remainder_basis_action_report, export_curvature_remainder_basis_action_json, export_curvature_remainder_basis_action_markdown
from curvature_remainder_formula import REMAINDER_FORMULA_OPEN, build_curvature_remainder_formula_report, export_curvature_remainder_formula_json, export_curvature_remainder_formula_markdown
from curvature_remainder_formula_decision import (
    FINAL_CLASSIFICATIONS,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_curvature_remainder_formula_decision,
    export_curvature_remainder_formula_decision_json,
    export_curvature_remainder_formula_decision_markdown,
)
from curvature_remainder_kernel_action import REMAINDER_KERNEL_COMPLEMENT_OPEN, build_curvature_remainder_kernel_action_report, export_curvature_remainder_kernel_action_json, export_curvature_remainder_kernel_action_markdown
from curvature_remainder_lower_bound_transfer import build_curvature_remainder_lower_bound_transfer_report, export_curvature_remainder_lower_bound_transfer_json, export_curvature_remainder_lower_bound_transfer_markdown
from curvature_remainder_relative_bound import build_curvature_remainder_relative_bound_report, export_curvature_remainder_relative_bound_json, export_curvature_remainder_relative_bound_markdown
from curvature_remainder_sector_action import build_curvature_remainder_sector_action_report, export_curvature_remainder_sector_action_json, export_curvature_remainder_sector_action_markdown
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP, build_full_ht_theorem_closure_report
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_operator_identification_theorem_report


EXACT_GAP = PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP


def test_formula_status_is_explicit_and_open():
    report = build_curvature_remainder_formula_report()

    assert report.status == REMAINDER_FORMULA_OPEN
    assert report.term_id == "lichnerowicz_bundle_curvature_remainder"
    assert "D_BH^2" in report.lichnerowicz_identity
    assert "R_bundle" in report.remainder_formula
    assert report.exact_missing_input == "COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP"
    assert report.theorem_complete is False


def test_basis_sector_and_kernel_actions_are_explicitly_open():
    basis = build_curvature_remainder_basis_action_report()
    sector = build_curvature_remainder_sector_action_report()
    kernel = build_curvature_remainder_kernel_action_report()

    assert basis.status == REMAINDER_BASIS_ACTION_OPEN
    assert all(row.status == "OPEN" for row in basis.features)
    assert sector.status == "REMAINDER_SECTOR_ACTION_OPEN"
    assert tuple(row.sector for row in sector.rows) == ("lepton", "up", "down")
    assert kernel.status == REMAINDER_KERNEL_COMPLEMENT_OPEN
    assert any(row.check_id == "commutator_Pperp_R" for row in kernel.checks)


def test_relative_bound_and_lower_bound_transfer_are_not_faked():
    relative = build_curvature_remainder_relative_bound_report()
    transfer = build_curvature_remainder_lower_bound_transfer_report()

    assert relative.a_remainder is None
    assert relative.b_remainder is None
    assert relative.a_total is None
    assert relative.a_total_less_than_one is None
    assert transfer.nonzero_remainder_included is False
    assert transfer.lower_bound_recomputed is False
    assert transfer.ht_survives_if_included is None


def test_formula_decision_uses_exact_allowed_final_classification():
    decision = build_curvature_remainder_formula_decision()

    assert decision.final_result == "CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED"
    assert decision.final_classification in FINAL_CLASSIFICATIONS
    assert decision.final_classification == "REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
    assert decision.exact_remaining_gap == ""
    assert decision.recommended_next_branch == ""
    assert decision.final_paper_allowed is False
    assert decision.theorem_complete is True


def test_complete_operator_and_downstream_theorems_do_not_overclaim():
    operator = build_operator_identification_theorem_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert operator.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert operator.next_target_theorem == ""
    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == EXACT_GAP
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False


def test_formal_kernel_remains_sector_labeled_not_coordinate_first():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v28_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "curvature_remainder_formula.py",
            "curvature_remainder_basis_action.py",
            "curvature_remainder_sector_action.py",
            "curvature_remainder_kernel_action.py",
            "curvature_remainder_relative_bound.py",
            "curvature_remainder_lower_bound_transfer.py",
            "curvature_remainder_formula_decision.py",
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


def test_v28_exports_generate(tmp_path):
    exporters = (
        (export_curvature_remainder_formula_markdown, export_curvature_remainder_formula_json, "formula"),
        (export_curvature_remainder_basis_action_markdown, export_curvature_remainder_basis_action_json, "basis"),
        (export_curvature_remainder_sector_action_markdown, export_curvature_remainder_sector_action_json, "sector"),
        (export_curvature_remainder_kernel_action_markdown, export_curvature_remainder_kernel_action_json, "kernel"),
        (export_curvature_remainder_relative_bound_markdown, export_curvature_remainder_relative_bound_json, "relative"),
        (export_curvature_remainder_lower_bound_transfer_markdown, export_curvature_remainder_lower_bound_transfer_json, "transfer"),
        (export_curvature_remainder_formula_decision_markdown, export_curvature_remainder_formula_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v28_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/curvature_remainder_formula_report.md",
        "theory/curvature_remainder_formula_report.json",
        "theory/curvature_remainder_basis_action_report.md",
        "theory/curvature_remainder_basis_action_report.json",
        "theory/curvature_remainder_sector_action_report.md",
        "theory/curvature_remainder_sector_action_report.json",
        "theory/curvature_remainder_kernel_action_report.md",
        "theory/curvature_remainder_kernel_action_report.json",
        "theory/curvature_remainder_relative_bound_report.md",
        "theory/curvature_remainder_relative_bound_report.json",
        "theory/curvature_remainder_lower_bound_transfer_report.md",
        "theory/curvature_remainder_lower_bound_transfer_report.json",
        "theory/curvature_remainder_formula_decision.md",
        "theory/curvature_remainder_formula_decision.json",
        "manuscript/BHSM_v2_8_curvature_remainder_formula_bound_note.md",
        "notebooks/58_curvature_remainder_formula_bound.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert "CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED" in root.joinpath("theory/curvature_remainder_formula_decision.md").read_text()


def test_v28_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_curvature_remainder_formula_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
