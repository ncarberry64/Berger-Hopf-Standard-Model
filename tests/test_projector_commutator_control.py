import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import HT_LOWER_BOUND_TRANSFER_GAP, PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP, build_full_ht_theorem_closure_report
from projector_commutator_closure import build_projector_commutator_closure_report
from projector_commutator_control import PROJECTOR_DEFINITION_PROVEN, build_projector_definition_audit_report, export_projector_commutator_control_json, export_projector_commutator_control_markdown
from projector_commutator_control_decision import PROJECTOR_COMMUTATOR_CONTROL_CLOSED, PROJECTOR_COMMUTATOR_CONTROL_PROVEN, build_projector_commutator_control_decision, export_projector_commutator_control_decision_json, export_projector_commutator_control_decision_markdown
from projector_commutator_domain_control import PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT, build_projector_commutator_domain_control_report, export_projector_commutator_domain_control_json, export_projector_commutator_domain_control_markdown
from projector_commutator_relative_bound import PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN, build_projector_commutator_relative_bound_report, export_projector_commutator_relative_bound_json, export_projector_commutator_relative_bound_markdown
from projector_operator_commutators import (
    BLOCKING_COMMUTATOR_CLASSIFICATIONS,
    build_projector_operator_commutators_report,
    export_projector_operator_commutators_json,
    export_projector_operator_commutators_markdown,
)
from projector_termwise_commutator_audit import TERMWISE_COMMUTATOR_AUDIT_CLOSED, build_projector_termwise_commutator_audit_report, export_projector_termwise_commutator_audit_json, export_projector_termwise_commutator_audit_markdown


EXPECTED_TERMS = {
    "D_diag^2",
    "V_Hopf",
    "V_boundary",
    "V_chi",
    "K_sector",
    "P_perp_lift",
    "V_PSD",
    "topographic_represented_sector",
    "complete_operator_curvature_topographic",
}


def test_projector_definition_is_formal_sector_labeled_not_coordinate_first():
    report = build_projector_definition_audit_report()
    basis = formal_kernel_basis_vectors()

    assert report.status == PROJECTOR_DEFINITION_PROVEN
    assert report.formal_kernel_coordinates == (0, 18, 36)
    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert report.old_coordinate_first_kernel_used is False
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert report.compatible_with_complete_operator_package is True


def test_every_complete_operator_term_has_commutator_classification():
    report = build_projector_operator_commutators_report()
    terms = {row.term_id for row in report.rows}

    assert terms == EXPECTED_TERMS
    assert report.all_terms_classified is True
    assert report.blocking_terms == ()
    assert report.theorem_complete is True
    assert not [row.term_id for row in report.rows if row.classification in BLOCKING_COMMUTATOR_CLASSIFICATIONS]


def test_nonzero_commutators_are_bound_or_lift_screened_safe():
    report = build_projector_operator_commutators_report()
    nonzero = [row for row in report.rows if not row.vanishes]

    assert {row.term_id for row in nonzero} == {
        "K_sector",
        "V_PSD",
        "topographic_represented_sector",
        "complete_operator_curvature_topographic",
    }
    assert all(row.bounded and row.relatively_bounded and row.lower_bound_safe for row in nonzero)
    assert any(row.term_id == "K_sector" and row.relative_a == 0.015621013485509948 for row in nonzero)


def test_relative_bound_total_is_below_one_and_lower_bound_safe():
    report = build_projector_commutator_relative_bound_report()

    assert report.status == PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN
    assert report.a_total == 0.015621013485509948
    assert report.b_total == 0.0
    assert report.a_total_less_than_one is True
    assert report.lower_bound_safe is True


def test_domain_control_supports_next_gate_without_closing_it():
    report = build_projector_commutator_domain_control_report()

    assert report.status == PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT
    assert report.supports_pperp_DA0V_subset_DA0V is True
    assert report.supports_lower_bound_transfer is True
    assert report.closes_projector_graph_domain is False
    assert report.next_gap_if_not_closed == PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP


def test_projector_commutator_decision_closes_and_downstream_moves_to_graph_domain():
    action = build_complete_operator_action_uniqueness_decision()
    operator = build_complete_operator_identification_closure_report()
    termwise = build_projector_termwise_commutator_audit_report()
    decision = build_projector_commutator_control_decision()
    closure = build_projector_commutator_closure_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
    assert operator.final_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert termwise.status == TERMWISE_COMMUTATOR_AUDIT_CLOSED
    assert decision.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED
    assert decision.commutator_status == PROJECTOR_COMMUTATOR_CONTROL_PROVEN
    assert closure.final_status == "PROJECTOR_COMMUTATORS_CONTROLLED"
    assert closure.theorem_complete is True
    assert ht.theorem_complete is False
    assert ht.single_named_gap == HT_LOWER_BOUND_TRANSFER_GAP
    assert ht.recommended_next_branch == "bhsm-v2.16-ht-lower-bound-transfer"
    assert bhsm.final_paper_allowed is False


def test_projector_commutator_proven_impossible_with_open_or_failed_terms():
    commutators = build_projector_operator_commutators_report()
    decision = build_projector_commutator_control_decision()

    if any(row.classification in {"COMMUTATOR_OPEN", "COMMUTATOR_FAILS", "COMMUTATOR_CONDITIONAL"} for row in commutators.rows):
        assert decision.final_result != PROJECTOR_COMMUTATOR_CONTROL_CLOSED
    else:
        assert decision.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED


def test_v214_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "projector_commutator_control.py",
            "projector_operator_commutators.py",
            "projector_termwise_commutator_audit.py",
            "projector_commutator_relative_bound.py",
            "projector_commutator_domain_control.py",
            "projector_commutator_control_decision.py",
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


def test_v214_exports_generate(tmp_path):
    exporters = (
        (export_projector_commutator_control_markdown, export_projector_commutator_control_json, "definition"),
        (export_projector_operator_commutators_markdown, export_projector_operator_commutators_json, "operators"),
        (export_projector_termwise_commutator_audit_markdown, export_projector_termwise_commutator_audit_json, "termwise"),
        (export_projector_commutator_relative_bound_markdown, export_projector_commutator_relative_bound_json, "bound"),
        (export_projector_commutator_domain_control_markdown, export_projector_commutator_domain_control_json, "domain"),
        (export_projector_commutator_control_decision_markdown, export_projector_commutator_control_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v214_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/projector_commutator_control_report.md",
        "theory/projector_commutator_control_report.json",
        "theory/projector_operator_commutators_report.md",
        "theory/projector_operator_commutators_report.json",
        "theory/projector_termwise_commutator_audit.md",
        "theory/projector_termwise_commutator_audit.json",
        "theory/projector_commutator_relative_bound_report.md",
        "theory/projector_commutator_relative_bound_report.json",
        "theory/projector_commutator_domain_control_report.md",
        "theory/projector_commutator_domain_control_report.json",
        "theory/projector_commutator_control_decision.md",
        "theory/projector_commutator_control_decision.json",
        "manuscript/BHSM_v2_14_projector_commutator_control_note.md",
        "notebooks/64_projector_commutator_control.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []


def test_v214_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_projector_commutator_control_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
