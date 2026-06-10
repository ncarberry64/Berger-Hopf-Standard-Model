import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from formal_complement_stability import (
    FORMAL_COMPLEMENT_CONDITIONAL,
    build_formal_complement_stability_report,
    export_formal_complement_stability_json,
    export_formal_complement_stability_markdown,
)
from full_ht_theorem import build_full_ht_theorem_report
from ht_domain_bridge import (
    FULL_HT_THEOREM_PROVEN,
    HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG,
    build_ht_domain_bridge_report,
    export_ht_domain_bridge_json,
    export_ht_domain_bridge_markdown,
)
from infinite_basis_domain import (
    FORMAL_KERNEL_STATES,
    INFINITE_DOMAIN_CONDITIONAL,
    build_infinite_basis_domain_report,
    export_infinite_basis_domain_json,
    export_infinite_basis_domain_markdown,
)
from self_adjoint_closure import (
    SELF_ADJOINT_DOMAIN_CONDITIONAL,
    build_self_adjoint_closure_report,
    export_self_adjoint_closure_json,
    export_self_adjoint_closure_markdown,
)
from uniform_relative_bound import (
    UNIFORM_RELATIVE_BOUND_CONDITIONAL,
    build_uniform_relative_bound_report,
    export_uniform_relative_bound_json,
    export_uniform_relative_bound_markdown,
)


def test_infinite_basis_domain_uses_formal_kernel_not_coordinate_first():
    report = build_infinite_basis_domain_report()

    assert report.formal_kernel == FORMAL_KERNEL_STATES
    assert report.old_coordinate_first_kernel_used is False
    assert report.status == INFINITE_DOMAIN_CONDITIONAL
    assert "|ell,0,0,q=0,chi=-1>" in report.formal_kernel
    assert "|u,0,0,q=0,chi=-1>" in report.formal_kernel
    assert "|d,0,0,q=0,chi=-1>" in report.formal_kernel


def test_uniform_relative_bound_is_conditional_not_proven_from_scans():
    report = build_uniform_relative_bound_report()

    assert report.status == UNIFORM_RELATIVE_BOUND_CONDITIONAL
    assert report.theorem_complete is False
    assert report.all_a_below_one is True
    assert report.all_assumptions_proven is False
    assert report.total_relative_a_upper == 0.015621013485509948
    assert any(row.term_id == "K_sector" and row.status == UNIFORM_RELATIVE_BOUND_CONDITIONAL for row in report.terms)


def test_self_adjointness_requires_proven_uniform_bound():
    report = build_self_adjoint_closure_report()

    assert report.status == SELF_ADJOINT_DOMAIN_CONDITIONAL
    assert report.theorem_complete is False
    assert report.relative_bound_below_one is True
    assert report.relative_bound_proven is False
    assert report.essential_self_adjointness_follows is False


def test_formal_complement_stability_is_conditional():
    report = build_formal_complement_stability_report()

    assert report.status == FORMAL_COMPLEMENT_CONDITIONAL
    assert report.theorem_complete is False
    assert report.old_coordinate_first_artifact_reintroduced is False
    assert any(check.id == "operator_invariance" and not check.passes for check in report.checks)
    assert any(check.id == "finite_projector_limit" and not check.passes for check in report.checks)


def test_ht_domain_bridge_strengthens_but_does_not_prove_ht():
    bridge = build_ht_domain_bridge_report()
    ht = build_full_ht_theorem_report()

    assert bridge.domain_bridge_status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert bridge.domain_bridge_status != FULL_HT_THEOREM_PROVEN
    assert bridge.theorem_complete is False
    assert bridge.full_ht_theorem_status_improved is True
    assert ht.v1_8_domain_bridge_status == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG
    assert ht.theorem_complete is False


def test_v18_exports_generate(tmp_path):
    paths = {
        "domain_md": tmp_path / "domain.md",
        "domain_json": tmp_path / "domain.json",
        "relative_md": tmp_path / "relative.md",
        "relative_json": tmp_path / "relative.json",
        "self_md": tmp_path / "self.md",
        "self_json": tmp_path / "self.json",
        "complement_md": tmp_path / "complement.md",
        "complement_json": tmp_path / "complement.json",
        "bridge_md": tmp_path / "bridge.md",
        "bridge_json": tmp_path / "bridge.json",
    }

    export_infinite_basis_domain_markdown(paths["domain_md"])
    export_infinite_basis_domain_json(paths["domain_json"])
    export_uniform_relative_bound_markdown(paths["relative_md"])
    export_uniform_relative_bound_json(paths["relative_json"])
    export_self_adjoint_closure_markdown(paths["self_md"])
    export_self_adjoint_closure_json(paths["self_json"])
    export_formal_complement_stability_markdown(paths["complement_md"])
    export_formal_complement_stability_json(paths["complement_json"])
    export_ht_domain_bridge_markdown(paths["bridge_md"])
    export_ht_domain_bridge_json(paths["bridge_json"])

    assert json.loads(paths["domain_json"].read_text())["status"] == INFINITE_DOMAIN_CONDITIONAL
    assert json.loads(paths["relative_json"].read_text())["status"] == UNIFORM_RELATIVE_BOUND_CONDITIONAL
    assert json.loads(paths["self_json"].read_text())["status"] == SELF_ADJOINT_DOMAIN_CONDITIONAL
    assert json.loads(paths["complement_json"].read_text())["status"] == FORMAL_COMPLEMENT_CONDITIONAL
    assert json.loads(paths["bridge_json"].read_text())["domain_bridge_status"] == HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG


def test_v18_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "infinite_basis_domain.py",
            "uniform_relative_bound.py",
            "self_adjoint_closure.py",
            "formal_complement_stability.py",
            "ht_domain_bridge.py",
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


def test_v18_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_ht_domain_bridge_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_generated_v18_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "infinite_basis_domain_report.md",
        root / "theory" / "uniform_relative_bound_report.md",
        root / "theory" / "self_adjoint_closure_report.md",
        root / "theory" / "formal_complement_stability_report.md",
        root / "theory" / "ht_domain_bridge_report.md",
        root / "manuscript" / "BHSM_v1_8_infinite_basis_domain_note.md",
        root / "notebooks" / "48_infinite_basis_domain_proof.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    text = "\n".join(path.read_text() for path in paths if path.suffix == ".md")
    assert "HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG" in text
    assert "not prove" in text.lower() or "not a proof" in text.lower()
