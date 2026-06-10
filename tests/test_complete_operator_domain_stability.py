import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complete_operator_bound_transfer import (
    HT_LOWER_BOUND_TRANSFER_CONDITIONAL,
    build_complete_operator_bound_transfer_report,
    export_complete_operator_bound_transfer_json,
    export_complete_operator_bound_transfer_markdown,
)
from complete_operator_domain_stability import (
    HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG,
    PERTURBATION_DOMAIN_STABILITY_CONDITIONAL,
    build_complete_operator_domain_stability_report,
    export_complete_operator_domain_stability_json,
    export_complete_operator_domain_stability_markdown,
)
from complete_twisted_dirac_operator import (
    COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL,
    COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
    build_complete_twisted_dirac_operator_report,
    export_complete_twisted_dirac_operator_json,
    export_complete_twisted_dirac_operator_markdown,
)
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL
from ht_domain_bridge import build_ht_domain_bridge_report
from ht_domain_stability_decision import (
    build_ht_domain_stability_decision,
    export_ht_domain_stability_decision_json,
    export_ht_domain_stability_decision_markdown,
)
from perturbation_projector_commutator import (
    PROJECTOR_COMMUTATORS_CONDITIONAL,
    build_perturbation_projector_commutator_report,
    export_perturbation_projector_commutator_json,
    export_perturbation_projector_commutator_markdown,
)
from projector_graph_domain_stability import (
    PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL,
    PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN,
    build_projector_graph_domain_stability_report,
    export_projector_graph_domain_stability_json,
    export_projector_graph_domain_stability_markdown,
)


def test_complete_operator_identification_is_conditional_not_overclaimed():
    report = build_complete_twisted_dirac_operator_report()

    assert report.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert report.theorem_candidate_model is True
    assert report.exact_complete_operator is True
    assert report.theorem_complete is True
    assert report.formal_kernel_coordinates == DEFAULT_FORMAL_COORDINATES
    assert report.formal_kernel_coordinates != OLD_COORDINATE_FIRST_KERNEL
    assert report.old_coordinate_first_kernel_used is False


def test_perturbation_domain_stability_requires_termwise_checks():
    report = build_complete_operator_domain_stability_report()

    assert report.perturbation_domain_stability_status == PERTURBATION_DOMAIN_STABILITY_CONDITIONAL
    assert report.all_termwise_checks_pass is True
    assert {row.term_id for row in report.perturbation_terms} == {
        "V_Hopf",
        "V_boundary",
        "V_chi",
        "K_sector",
        "P_perp_lift",
        "PSD_profile",
    }
    assert all(row.maps_DA0_to_H and row.preserves_common_domain for row in report.perturbation_terms)
    assert report.theorem_complete is False


def test_projector_graph_domain_stability_is_proven_with_commutator_checks():
    projector = build_projector_graph_domain_stability_report()
    commutator = build_perturbation_projector_commutator_report()

    assert projector.status == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
    assert projector.Pperp_DA0_subset_DA0 is True
    assert projector.Pperp_DA0V_subset_DA0V is True
    assert projector.commutes_with_A0 is True
    assert projector.V_commutator_controlled is True
    assert commutator.status == PROJECTOR_COMMUTATORS_CONDITIONAL
    assert commutator.all_commutators_controlled is True
    assert commutator.all_complete_operator_proven is False
    assert any(not row.vanishes and row.relatively_bounded for row in commutator.rows)


def test_lower_bound_transfer_is_conditional_not_proven_with_index_mirror_open():
    transfer = build_complete_operator_bound_transfer_report()

    assert transfer.status == HT_LOWER_BOUND_TRANSFER_CONDITIONAL
    assert transfer.applies_to_H_perp is True
    assert transfer.clears_required_threshold is True
    assert transfer.theorem_complete is False
    assert "index" in " ".join(transfer.open_obligations).lower()
    assert "mirror" in " ".join(transfer.open_obligations).lower()


def test_v24_decision_updates_ht_dependency_without_claiming_full_theorem():
    domain = build_complete_operator_domain_stability_report()
    decision = build_ht_domain_stability_decision()
    bridge = build_ht_domain_bridge_report()

    assert domain.status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert decision.ht_dependency_status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert bridge.domain_bridge_status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert decision.theorem_complete is False
    assert decision.final_paper_allowed is False
    assert bridge.theorem_complete is False


def test_v24_exports_generate(tmp_path):
    outputs = {
        "operator_md": tmp_path / "operator.md",
        "operator_json": tmp_path / "operator.json",
        "comm_md": tmp_path / "comm.md",
        "comm_json": tmp_path / "comm.json",
        "projector_md": tmp_path / "projector.md",
        "projector_json": tmp_path / "projector.json",
        "transfer_md": tmp_path / "transfer.md",
        "transfer_json": tmp_path / "transfer.json",
        "domain_md": tmp_path / "domain.md",
        "domain_json": tmp_path / "domain.json",
        "decision_md": tmp_path / "decision.md",
        "decision_json": tmp_path / "decision.json",
    }
    export_complete_twisted_dirac_operator_markdown(outputs["operator_md"])
    export_complete_twisted_dirac_operator_json(outputs["operator_json"])
    export_perturbation_projector_commutator_markdown(outputs["comm_md"])
    export_perturbation_projector_commutator_json(outputs["comm_json"])
    export_projector_graph_domain_stability_markdown(outputs["projector_md"])
    export_projector_graph_domain_stability_json(outputs["projector_json"])
    export_complete_operator_bound_transfer_markdown(outputs["transfer_md"])
    export_complete_operator_bound_transfer_json(outputs["transfer_json"])
    export_complete_operator_domain_stability_markdown(outputs["domain_md"])
    export_complete_operator_domain_stability_json(outputs["domain_json"])
    export_ht_domain_stability_decision_markdown(outputs["decision_md"])
    export_ht_domain_stability_decision_json(outputs["decision_json"])

    assert json.loads(outputs["operator_json"].read_text())["status"] == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert json.loads(outputs["comm_json"].read_text())["status"] == PROJECTOR_COMMUTATORS_CONDITIONAL
    assert json.loads(outputs["projector_json"].read_text())["status"] == PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
    assert json.loads(outputs["transfer_json"].read_text())["status"] == HT_LOWER_BOUND_TRANSFER_CONDITIONAL
    assert json.loads(outputs["domain_json"].read_text())["status"] == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert json.loads(outputs["decision_json"].read_text())["ht_dependency_status"] == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG


def test_requested_v24_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/complete_operator_domain_stability_report.md",
        "theory/complete_operator_domain_stability_report.json",
        "theory/complete_twisted_dirac_operator_report.md",
        "theory/complete_twisted_dirac_operator_report.json",
        "theory/perturbation_projector_commutator_report.md",
        "theory/perturbation_projector_commutator_report.json",
        "theory/projector_graph_domain_stability_report.md",
        "theory/projector_graph_domain_stability_report.json",
        "theory/complete_operator_bound_transfer_report.md",
        "theory/complete_operator_bound_transfer_report.json",
        "theory/ht_domain_stability_decision.md",
        "theory/ht_domain_stability_decision.json",
        "manuscript/BHSM_v2_4_complete_operator_domain_stability_note.md",
        "notebooks/54_complete_operator_domain_stability.ipynb",
    )

    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG in root.joinpath("theory/ht_domain_stability_decision.md").read_text()
    assert "not a completed proof" in root.joinpath("manuscript/BHSM_v2_4_complete_operator_domain_stability_note.md").read_text()


def test_v24_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "complete_operator_domain_stability.py",
            "complete_twisted_dirac_operator.py",
            "perturbation_projector_commutator.py",
            "projector_graph_domain_stability.py",
            "complete_operator_bound_transfer.py",
            "ht_domain_stability_decision.py",
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
    assert all(token not in sources for token in forbidden)


def test_v24_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_ht_domain_stability_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
