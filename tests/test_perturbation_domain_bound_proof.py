import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from essential_self_adjointness import DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN, build_essential_self_adjointness_report
from graph_norm_domain import GRAPH_NORM_DOMAIN_PROVEN, build_graph_norm_domain_report
from hopf_boundary_infinite_bound import (
    HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL,
    build_hopf_boundary_infinite_bound_report,
    export_hopf_boundary_infinite_bound_json,
    export_hopf_boundary_infinite_bound_markdown,
)
from ht_domain_bridge import HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY, build_ht_domain_bridge_report
from perturbation_closure_decision import HT_THEOREM_CONDITIONAL_ON_COMPLEMENT
from lift_projector_domain import (
    LIFT_PROJECTOR_DOMAIN_CONDITIONAL,
    build_lift_projector_domain_report,
    export_lift_projector_domain_json,
    export_lift_projector_domain_markdown,
)
from perturbation_closure_decision import (
    KATO_RELLICH_CLOSURE_CONDITIONAL,
    LOWER_BOUND_BLOCKED_BY_COMPLEMENT,
    RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS,
    build_perturbation_closure_decision,
    export_perturbation_closure_decision_json,
    export_perturbation_closure_decision_markdown,
)
from perturbation_domain_proof import (
    COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL,
    build_perturbation_domain_proof_report,
    export_perturbation_domain_proof_json,
    export_perturbation_domain_proof_markdown,
)
from perturbation_symmetry_closure import (
    PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL,
    build_perturbation_symmetry_closure_report,
    export_perturbation_symmetry_closure_json,
    export_perturbation_symmetry_closure_markdown,
)
from sector_coupling_infinite_bound import (
    SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL,
    build_sector_coupling_infinite_bound_report,
    export_sector_coupling_infinite_bound_json,
    export_sector_coupling_infinite_bound_markdown,
)


def test_v19_reference_operator_proof_remains_intact():
    assert build_essential_self_adjointness_report().status == DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
    assert build_graph_norm_domain_report().status == GRAPH_NORM_DOMAIN_PROVEN


def test_common_domain_is_conditional_not_overclaimed():
    report = build_perturbation_domain_proof_report()

    assert report.status == COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL
    assert report.common_domain_equals_DA0 is True
    assert report.finite_core_common_core is True
    assert report.theorem_complete is False
    assert all(row.maps_DA0_to_H for row in report.terms)


def test_symmetry_is_termwise_conditional_not_finite_core_proof():
    report = build_perturbation_symmetry_closure_report()

    assert report.status == PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL
    assert report.all_symmetric_on_core is True
    assert report.all_termwise_symmetric_on_DA0 is True
    assert report.theorem_complete is False
    assert "complete operator" in " ".join(report.open_obligations)


def test_sector_coupling_infinite_bound_is_kmax_independent_but_conditional():
    report = build_sector_coupling_infinite_bound_report()

    assert report.status == SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL
    assert report.independent_of_kmax is True
    assert report.finite_scan_evidence_used is False
    assert report.relative_a == 0.015621013485509948
    assert report.relative_a < 1.0
    assert report.theorem_complete is False


def test_hopf_boundary_chi_and_lift_projector_statuses_are_explicit():
    hopf = build_hopf_boundary_infinite_bound_report()
    lift = build_lift_projector_domain_report()

    assert hopf.status == HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL
    assert hopf.total_relative_a == 0.0
    assert all(term.preserves_domain for term in hopf.terms)
    assert lift.status == LIFT_PROJECTOR_DOMAIN_CONDITIONAL
    assert lift.all_preserve_DA0 is True
    assert lift.theorem_complete is False


def test_relative_kato_lower_and_ht_decision_are_not_overclaimed():
    decision = build_perturbation_closure_decision()
    bridge = build_ht_domain_bridge_report()

    assert decision.relative_bound_status == RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS
    assert decision.a_less_than_one is True
    assert decision.kato_rellich_status == KATO_RELLICH_CLOSURE_CONDITIONAL
    assert decision.lower_bound_status == LOWER_BOUND_BLOCKED_BY_COMPLEMENT
    assert decision.ht_dependency_status == HT_THEOREM_CONDITIONAL_ON_COMPLEMENT
    assert decision.theorem_complete is False
    assert bridge.domain_bridge_status == HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY
    assert bridge.theorem_complete is False


def test_v21_exports_generate(tmp_path):
    outputs = {
        "domain_md": tmp_path / "domain.md",
        "domain_json": tmp_path / "domain.json",
        "sym_md": tmp_path / "sym.md",
        "sym_json": tmp_path / "sym.json",
        "sector_md": tmp_path / "sector.md",
        "sector_json": tmp_path / "sector.json",
        "hopf_md": tmp_path / "hopf.md",
        "hopf_json": tmp_path / "hopf.json",
        "lift_md": tmp_path / "lift.md",
        "lift_json": tmp_path / "lift.json",
        "decision_md": tmp_path / "decision.md",
        "decision_json": tmp_path / "decision.json",
    }
    export_perturbation_domain_proof_markdown(outputs["domain_md"])
    export_perturbation_domain_proof_json(outputs["domain_json"])
    export_perturbation_symmetry_closure_markdown(outputs["sym_md"])
    export_perturbation_symmetry_closure_json(outputs["sym_json"])
    export_sector_coupling_infinite_bound_markdown(outputs["sector_md"])
    export_sector_coupling_infinite_bound_json(outputs["sector_json"])
    export_hopf_boundary_infinite_bound_markdown(outputs["hopf_md"])
    export_hopf_boundary_infinite_bound_json(outputs["hopf_json"])
    export_lift_projector_domain_markdown(outputs["lift_md"])
    export_lift_projector_domain_json(outputs["lift_json"])
    export_perturbation_closure_decision_markdown(outputs["decision_md"])
    export_perturbation_closure_decision_json(outputs["decision_json"])

    assert json.loads(outputs["domain_json"].read_text())["status"] == COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL
    assert json.loads(outputs["sym_json"].read_text())["status"] == PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL
    assert json.loads(outputs["sector_json"].read_text())["status"] == SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL
    assert json.loads(outputs["hopf_json"].read_text())["status"] == HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL
    assert json.loads(outputs["lift_json"].read_text())["status"] == LIFT_PROJECTOR_DOMAIN_CONDITIONAL
    assert json.loads(outputs["decision_json"].read_text())["ht_dependency_status"] == HT_THEOREM_CONDITIONAL_ON_COMPLEMENT


def test_v21_theorem_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "perturbation_domain_proof.py",
            "perturbation_symmetry_closure.py",
            "sector_coupling_infinite_bound.py",
            "hopf_boundary_infinite_bound.py",
            "lift_projector_domain.py",
            "perturbation_closure_decision.py",
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


def test_v21_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_perturbation_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
