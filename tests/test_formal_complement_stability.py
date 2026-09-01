import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complement_lower_bound_bridge import (
    COMPLEMENT_LOWER_BOUND_CONDITIONAL,
    build_complement_lower_bound_bridge_report,
    export_complement_lower_bound_bridge_json,
    export_complement_lower_bound_bridge_markdown,
)
from constants import S_OVERLAP
from finite_projector_convergence import (
    FINITE_PROJECTOR_CONVERGENCE_PROVEN,
    build_finite_projector_convergence_report,
    export_finite_projector_convergence_json,
    export_finite_projector_convergence_markdown,
)
from formal_complement_closure_decision import (
    HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR,
    build_formal_complement_closure_decision,
    export_formal_complement_closure_decision_json,
    export_formal_complement_closure_decision_markdown,
)
from formal_complement_projector import (
    FORMAL_COMPLEMENT_PROJECTOR_PROVEN,
    build_formal_complement_projector_report,
    export_formal_complement_projector_json,
    export_formal_complement_projector_markdown,
)
from formal_kernel_projector import (
    DEFAULT_FORMAL_COORDINATES,
    FORMAL_KERNEL_PROJECTOR_PROVEN,
    OLD_COORDINATE_FIRST_KERNEL,
    build_formal_kernel_projector_report,
    export_formal_kernel_projector_json,
    export_formal_kernel_projector_markdown,
)
from ht_domain_bridge import build_ht_domain_bridge_report
from projector_domain_stability import (
    PROJECTOR_DOMAIN_STABILITY_CONDITIONAL,
    build_projector_domain_stability_report,
    export_projector_domain_stability_json,
    export_projector_domain_stability_markdown,
)


def test_formal_kernel_is_exact_sector_labeled_triple_not_coordinate_first():
    report = build_formal_kernel_projector_report()

    assert report.status == FORMAL_KERNEL_PROJECTOR_PROVEN
    assert tuple(row.sector for row in report.kernel_basis) == ("lepton", "up", "down")
    assert tuple(row.coordinate_hint_kmax4 for row in report.kernel_basis) == DEFAULT_FORMAL_COORDINATES
    assert tuple(row.coordinate_hint_kmax4 for row in report.kernel_basis) != OLD_COORDINATE_FIRST_KERNEL
    assert report.old_coordinate_first_kernel_used is False
    assert report.old_coordinate_first_kernel_rejected is True


def test_complement_projector_algebra_is_proven_but_not_full_theorem():
    report = build_formal_complement_projector_report()

    assert report.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN
    assert report.idempotent is True
    assert report.self_adjoint is True
    assert report.orthogonal_to_kernel is True
    assert report.theorem_complete is False


def test_domain_stability_is_conditional_not_overclaimed():
    report = build_projector_domain_stability_report()

    assert report.status == PROJECTOR_DOMAIN_STABILITY_CONDITIONAL
    assert report.A0_domain_stable is True
    assert report.commutes_with_A0 is True
    assert report.perturbation_domain_stable is True
    assert report.theorem_complete is False
    assert report.remaining_commutators


def test_finite_projector_convergence_is_explicit_and_avoids_old_artifact():
    report = build_finite_projector_convergence_report()

    assert report.status == FINITE_PROJECTOR_CONVERGENCE_PROVEN
    assert report.strong_convergence is True
    assert report.graph_norm_convergence is True
    assert report.no_coordinate_first_artifact is True
    assert len(report.rows) >= 3
    assert all(not row.old_coordinate_first_used for row in report.rows)


def test_complement_lower_bound_applies_only_conditionally_to_hperp():
    report = build_complement_lower_bound_bridge_report()

    assert report.status == COMPLEMENT_LOWER_BOUND_CONDITIONAL
    assert report.applies_to_H_perp is True
    assert report.clears_required_threshold is True
    assert report.theorem_complete is False
    assert "index" in " ".join(report.open_obligations).lower()


def test_ht_dependency_moves_to_index_mirror_not_full_theorem():
    decision = build_formal_complement_closure_decision()
    bridge = build_ht_domain_bridge_report()

    assert decision.ht_dependency_status == HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR
    assert decision.theorem_complete is False
    assert bridge.domain_bridge_status == "HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG"
    assert bridge.theorem_complete is False


def test_v22_exports_generate(tmp_path):
    outputs = {
        "kernel_md": tmp_path / "kernel.md",
        "kernel_json": tmp_path / "kernel.json",
        "complement_md": tmp_path / "complement.md",
        "complement_json": tmp_path / "complement.json",
        "domain_md": tmp_path / "domain.md",
        "domain_json": tmp_path / "domain.json",
        "convergence_md": tmp_path / "convergence.md",
        "convergence_json": tmp_path / "convergence.json",
        "lower_md": tmp_path / "lower.md",
        "lower_json": tmp_path / "lower.json",
        "decision_md": tmp_path / "decision.md",
        "decision_json": tmp_path / "decision.json",
    }
    export_formal_kernel_projector_markdown(outputs["kernel_md"])
    export_formal_kernel_projector_json(outputs["kernel_json"])
    export_formal_complement_projector_markdown(outputs["complement_md"])
    export_formal_complement_projector_json(outputs["complement_json"])
    export_projector_domain_stability_markdown(outputs["domain_md"])
    export_projector_domain_stability_json(outputs["domain_json"])
    export_finite_projector_convergence_markdown(outputs["convergence_md"])
    export_finite_projector_convergence_json(outputs["convergence_json"])
    export_complement_lower_bound_bridge_markdown(outputs["lower_md"])
    export_complement_lower_bound_bridge_json(outputs["lower_json"])
    export_formal_complement_closure_decision_markdown(outputs["decision_md"])
    export_formal_complement_closure_decision_json(outputs["decision_json"])

    assert json.loads(outputs["kernel_json"].read_text())["status"] == FORMAL_KERNEL_PROJECTOR_PROVEN
    assert json.loads(outputs["complement_json"].read_text())["status"] == FORMAL_COMPLEMENT_PROJECTOR_PROVEN
    assert json.loads(outputs["domain_json"].read_text())["status"] == PROJECTOR_DOMAIN_STABILITY_CONDITIONAL
    assert json.loads(outputs["convergence_json"].read_text())["status"] == FINITE_PROJECTOR_CONVERGENCE_PROVEN
    assert json.loads(outputs["lower_json"].read_text())["status"] == COMPLEMENT_LOWER_BOUND_CONDITIONAL
    assert json.loads(outputs["decision_json"].read_text())["ht_dependency_status"] == HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR


def test_v22_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "formal_kernel_projector.py",
            "formal_complement_projector.py",
            "projector_domain_stability.py",
            "finite_projector_convergence.py",
            "complement_lower_bound_bridge.py",
            "formal_complement_closure_decision.py",
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


def test_v22_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_formal_complement_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
