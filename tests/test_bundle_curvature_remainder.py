import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_connection_curvature import build_bundle_connection_curvature_report, export_bundle_connection_curvature_json, export_bundle_connection_curvature_markdown
from complete_operator_identification_decision import build_complete_operator_identification_decision
from constants import S_OVERLAP
from curvature_remainder_audit import (
    FINAL_REMAINDER_CLASSIFICATIONS,
    REMAINDER_OPEN,
    REMAINDER_REAL_MISSING_TERM,
    build_curvature_remainder_audit_report,
    export_curvature_remainder_audit_json,
    export_curvature_remainder_audit_markdown,
)
from curvature_remainder_bound import build_curvature_remainder_bound_report, export_curvature_remainder_bound_json, export_curvature_remainder_bound_markdown
from curvature_remainder_closure_decision import (
    BHSM_THEOREM_FAILURE,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_curvature_remainder_closure_decision,
    export_curvature_remainder_closure_decision_json,
    export_curvature_remainder_closure_decision_markdown,
)
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import build_full_ht_theorem_closure_report
from lichnerowicz_bundle_curvature import REMAINDER_TERM_ID, build_lichnerowicz_bundle_curvature_report, export_lichnerowicz_bundle_curvature_json, export_lichnerowicz_bundle_curvature_markdown
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_operator_identification_theorem_report
from operator_term_inventory import build_operator_term_inventory_report


EXACT_GAP = "BUNDLE_CURVATURE_FORMULA_CONDITIONAL_GAP"


def test_lichnerowicz_remainder_inventory_is_explicit():
    report = build_lichnerowicz_bundle_curvature_report()

    assert report.remainder.term_id == REMAINDER_TERM_ID
    assert report.remainder.current_status == "FORMULA_AND_ACTION_NOT_DERIVED"
    assert report.remainder.acts_on_formal_kernel == "OPEN"
    assert report.remainder.acts_on_h_perp == "OPEN"
    assert report.theorem_complete is False


def test_bundle_connection_sources_are_inventoried_but_not_closed():
    report = build_bundle_connection_curvature_report()

    assert report.all_sources_inventoried is True
    assert report.theorem_complete is False
    assert "hopf_fiber_connection" in {row.component_id for row in report.components}
    assert report.unresolved_components


def test_remainder_is_classified_exactly_once_as_open():
    report = build_curvature_remainder_audit_report()
    passing = [row.disposition for row in report.checks if row.passes]

    assert report.term_id == REMAINDER_TERM_ID
    assert report.final_classification in FINAL_REMAINDER_CLASSIFICATIONS
    assert report.final_classification == REMAINDER_OPEN
    assert passing == [REMAINDER_OPEN]
    assert report.exact_remaining_gap == "BUNDLE_CURVATURE_REMAINDER_FORMULA_AND_BOUND_GAP"
    assert report.theorem_complete is False


def test_bound_report_does_not_recompute_lower_bound_for_open_remainder():
    report = build_curvature_remainder_bound_report()

    assert report.remainder_classification == REMAINDER_OPEN
    assert report.a_remainder is None
    assert report.b_remainder is None
    assert report.a_total is None
    assert report.lower_bound_recomputed is False
    assert report.lower_bound_safe is False
    assert report.theorem_complete is False


def test_closure_decision_names_next_gap_without_failure_overclaim():
    report = build_curvature_remainder_closure_decision()

    assert report.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert report.final_result != BHSM_THEOREM_FAILURE
    assert report.remainder_classification == REMAINDER_OPEN
    assert report.exact_remaining_gap == EXACT_GAP
    assert report.recommended_next_branch == "bhsm-v2.12-bundle-curvature-conditional-closure"
    assert report.final_paper_allowed is False


def test_complete_operator_cannot_be_proven_while_remainder_open():
    theorem = build_operator_identification_theorem_report()
    decision = build_complete_operator_identification_decision()
    inventory = build_operator_term_inventory_report()

    assert theorem.status != COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert theorem.theorem_complete is False
    assert decision.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert inventory.required_open_or_missing_terms == (REMAINDER_TERM_ID,)
    assert inventory.theorem_complete is False


def test_downstream_full_ht_and_bhsm_do_not_upgrade_from_curvature_gap():
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == EXACT_GAP
    assert ht.recommended_next_branch == "bhsm-v2.12-bundle-curvature-conditional-closure"
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False


def test_formal_kernel_still_sector_labeled_and_coordinate_first_rejected():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v27_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "lichnerowicz_bundle_curvature.py",
            "bundle_connection_curvature.py",
            "curvature_remainder_audit.py",
            "curvature_remainder_bound.py",
            "curvature_remainder_closure_decision.py",
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


def test_v27_exports_generate(tmp_path):
    exporters = (
        (export_lichnerowicz_bundle_curvature_markdown, export_lichnerowicz_bundle_curvature_json, "lichnerowicz"),
        (export_bundle_connection_curvature_markdown, export_bundle_connection_curvature_json, "connection"),
        (export_curvature_remainder_audit_markdown, export_curvature_remainder_audit_json, "audit"),
        (export_curvature_remainder_bound_markdown, export_curvature_remainder_bound_json, "bound"),
        (export_curvature_remainder_closure_decision_markdown, export_curvature_remainder_closure_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v27_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/lichnerowicz_bundle_curvature_report.md",
        "theory/lichnerowicz_bundle_curvature_report.json",
        "theory/bundle_connection_curvature_report.md",
        "theory/bundle_connection_curvature_report.json",
        "theory/curvature_remainder_audit.md",
        "theory/curvature_remainder_audit.json",
        "theory/curvature_remainder_bound_report.md",
        "theory/curvature_remainder_bound_report.json",
        "theory/curvature_remainder_closure_decision.md",
        "theory/curvature_remainder_closure_decision.json",
        "manuscript/BHSM_v2_7_bundle_curvature_remainder_note.md",
        "notebooks/57_bundle_curvature_remainder.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP in root.joinpath("theory/curvature_remainder_closure_decision.md").read_text()


def test_v27_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_curvature_remainder_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
