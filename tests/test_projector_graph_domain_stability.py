import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complete_operator_action_uniqueness_decision import COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED, build_complete_operator_action_uniqueness_decision
from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import HT_LOWER_BOUND_TRANSFER_GAP, build_full_ht_theorem_closure_report
from interacting_graph_domain import (
    GRAPH_DOMAIN_DEFINITIONS_PROVEN,
    INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN,
    build_graph_domain_definitions_report,
    build_interacting_graph_domain_report,
    export_interacting_graph_domain_json,
    export_interacting_graph_domain_markdown,
)
from projector_commutator_control_decision import PROJECTOR_COMMUTATOR_CONTROL_CLOSED, build_projector_commutator_control_decision
from projector_domain_closure_decision import (
    PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED,
    PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN,
    build_projector_domain_closure_decision,
    export_projector_domain_closure_decision_json,
    export_projector_domain_closure_decision_markdown,
)
from projector_domain_invariance import (
    BLOCKING_DOMAIN_STABILITY_CLASSIFICATIONS,
    SAFE_DOMAIN_STABILITY_CLASSIFICATIONS,
    build_projector_domain_invariance_report,
    export_projector_domain_invariance_json,
    export_projector_domain_invariance_markdown,
)
from projector_graph_domain_stability import build_projector_graph_domain_stability_report, export_projector_graph_domain_stability_json, export_projector_graph_domain_stability_markdown
from projector_graph_norm_control import (
    PROJECTOR_GRAPH_NORM_CONTROL_PROVEN,
    build_projector_graph_norm_control_report,
    export_projector_graph_norm_control_json,
    export_projector_graph_norm_control_markdown,
)


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


def test_graph_domain_definitions_and_interacting_domain_are_proven():
    definitions = build_graph_domain_definitions_report()
    interacting = build_interacting_graph_domain_report()

    assert definitions.status == GRAPH_DOMAIN_DEFINITIONS_PROVEN
    assert interacting.status == INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN
    assert interacting.D_A0V_equals_D_A0 is True
    assert interacting.graph_norms_equivalent is True
    assert interacting.perturbation_relative_a_less_than_one is True
    assert interacting.perturbation_relative_a < 1.0
    assert interacting.complete_operator_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert interacting.action_uniqueness_status == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
    assert interacting.commutator_control_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED


def test_projector_domain_invariance_classifies_every_complete_operator_term():
    report = build_projector_domain_invariance_report()
    terms = {row.term_id for row in report.rows}

    assert terms == EXPECTED_TERMS
    assert report.all_terms_classified is True
    assert report.blocking_terms == ()
    assert report.Pperp_DA0_subset_DA0 is True
    assert report.Pperp_DA0V_subset_DA0V is True
    assert all(row.classification in SAFE_DOMAIN_STABILITY_CLASSIFICATIONS for row in report.rows)
    assert not [row.term_id for row in report.rows if row.classification in BLOCKING_DOMAIN_STABILITY_CLASSIFICATIONS]


def test_projector_graph_norm_control_is_explicit_and_proven():
    report = build_projector_graph_norm_control_report()

    assert report.status == PROJECTOR_GRAPH_NORM_CONTROL_PROVEN
    assert report.projector_bounded_on_H is True
    assert report.projector_bounded_on_D_A0 is True
    assert report.projector_bounded_on_D_A0V is True
    assert report.control_constant > 0.0
    assert "||P_perp psi||_(A0+V)" in report.inequality


def test_projector_graph_domain_closes_and_downstream_moves_to_lower_bound_transfer():
    action = build_complete_operator_action_uniqueness_decision()
    operator = build_complete_operator_identification_closure_report()
    commutator = build_projector_commutator_control_decision()
    decision = build_projector_domain_closure_decision()
    graph = build_projector_graph_domain_stability_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert action.final_result == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
    assert operator.final_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
    assert commutator.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED
    assert decision.final_result == PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED
    assert decision.graph_domain_status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
    assert decision.Pperp_DA0V_subset_DA0V is True
    assert graph.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
    assert graph.theorem_complete is True
    assert ht.theorem_complete is False
    assert ht.single_named_gap == HT_LOWER_BOUND_TRANSFER_GAP
    assert ht.recommended_next_branch == "bhsm-v2.16-ht-lower-bound-transfer"
    assert bhsm.final_paper_allowed is False


def test_projector_graph_domain_proven_impossible_with_open_failed_or_uncontrolled_conditional_terms():
    invariance = build_projector_domain_invariance_report()
    graph_norm = build_projector_graph_norm_control_report()
    decision = build_projector_domain_closure_decision()

    if any(row.classification in {"DOMAIN_STABLE_OPEN", "DOMAIN_STABLE_FAILS", "DOMAIN_STABLE_CONDITIONAL"} for row in invariance.rows):
        assert decision.final_result != PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED
    elif graph_norm.status in {"PROJECTOR_GRAPH_NORM_CONTROL_OPEN", "PROJECTOR_GRAPH_NORM_CONTROL_FAILS", "PROJECTOR_GRAPH_NORM_CONTROL_CONDITIONAL"}:
        assert decision.final_result != PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED
    else:
        assert decision.final_result == PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED


def test_v215_uses_formal_sector_labeled_kernel_not_coordinate_first():
    basis = formal_kernel_basis_vectors()
    decision = build_projector_domain_closure_decision()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert decision.Pperp_DA0V_subset_DA0V is True


def test_v215_exports_generate(tmp_path):
    exporters = (
        (export_interacting_graph_domain_markdown, export_interacting_graph_domain_json, "interacting"),
        (export_projector_domain_invariance_markdown, export_projector_domain_invariance_json, "invariance"),
        (export_projector_graph_norm_control_markdown, export_projector_graph_norm_control_json, "norm"),
        (export_projector_domain_closure_decision_markdown, export_projector_domain_closure_decision_json, "decision"),
        (export_projector_graph_domain_stability_markdown, export_projector_graph_domain_stability_json, "stability"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v215_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/projector_graph_domain_stability_report.md",
        "theory/projector_graph_domain_stability_report.json",
        "theory/interacting_graph_domain_report.md",
        "theory/interacting_graph_domain_report.json",
        "theory/projector_domain_invariance_report.md",
        "theory/projector_domain_invariance_report.json",
        "theory/projector_graph_norm_control_report.md",
        "theory/projector_graph_norm_control_report.json",
        "theory/projector_domain_closure_decision.md",
        "theory/projector_domain_closure_decision.json",
        "manuscript/BHSM_v2_15_projector_graph_domain_stability_note.md",
        "notebooks/65_projector_graph_domain_stability.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []


def test_v215_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "interacting_graph_domain.py",
            "projector_domain_invariance.py",
            "projector_graph_norm_control.py",
            "projector_domain_closure_decision.py",
            "projector_graph_domain_stability.py",
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


def test_v215_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_projector_domain_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
