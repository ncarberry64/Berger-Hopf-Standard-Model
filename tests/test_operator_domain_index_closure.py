import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from full_ht_theorem import build_full_ht_theorem_report
from operator_domain_index_closure import (
    HT_THEOREM_BLOCKED_BY_DOMAIN,
    INDEX_THEOREM_OPEN,
    MIRROR_EXCLUSION_OPEN,
    RELATIVE_BOUND_CONDITIONAL,
    build_operator_domain_index_closure_report,
    build_relative_bound_audit_report,
    export_index_mirror_closure_json,
    export_index_mirror_closure_markdown,
    export_operator_domain_index_closure_json,
    export_operator_domain_index_closure_markdown,
    export_self_adjoint_domain_json,
    export_self_adjoint_domain_markdown,
)
from self_adjoint_domain import SELF_ADJOINT_DOMAIN_OPEN


def test_v17_formal_kernel_is_sector_labeled_not_coordinate_first():
    report = build_operator_domain_index_closure_report()

    assert report.formal_kernel == (
        "|ell,0,0,q=0,chi=-1>",
        "|u,0,0,q=0,chi=-1>",
        "|d,0,0,q=0,chi=-1>",
    )
    assert report.old_coordinate_first_kernel_rejected == (0, 1, 2)
    assert report.index_mirror_report.sector_labels == ("ell", "u", "d")


def test_relative_bound_audit_is_conditional_not_proven():
    report = build_relative_bound_audit_report()

    assert report.status == RELATIVE_BOUND_CONDITIONAL
    assert report.theorem_complete is False
    assert report.all_bounds_below_one is True
    assert report.all_infinite_basis_compatible is False
    assert report.max_relative_a == 0.015621013485509948
    assert any(term.term_id == "K_sector" and term.below_one for term in report.terms)


def test_domain_index_mirror_chain_blocks_ht_without_overclaim():
    report = build_operator_domain_index_closure_report()
    ht = build_full_ht_theorem_report()

    assert report.domain_status == SELF_ADJOINT_DOMAIN_OPEN
    assert report.index_status == INDEX_THEOREM_OPEN
    assert report.mirror_status == MIRROR_EXCLUSION_OPEN
    assert report.ht_dependency_status == HT_THEOREM_BLOCKED_BY_DOMAIN
    assert report.theorem_complete is False
    assert ht.v1_7_dependency_status == HT_THEOREM_BLOCKED_BY_DOMAIN


def test_mirror_risks_are_not_hidden():
    report = build_operator_domain_index_closure_report()

    assert report.index_mirror_report.chiral_channel_excludes_generated_mirrors is True
    assert report.index_mirror_report.higgs_u1_channel_closed is False
    assert report.index_mirror_report.boundary_functional_channel_closed is False
    assert any("Higgs-selected U(1)" in item or "Higgs-selected" in item for item in report.index_mirror_report.open_obligations)


def test_operator_domain_index_exports(tmp_path):
    closure_md = tmp_path / "closure.md"
    closure_json = tmp_path / "closure.json"
    domain_md = tmp_path / "domain.md"
    domain_json = tmp_path / "domain.json"
    index_md = tmp_path / "index.md"
    index_json = tmp_path / "index.json"

    export_operator_domain_index_closure_markdown(closure_md)
    export_operator_domain_index_closure_json(closure_json)
    export_self_adjoint_domain_markdown(domain_md)
    export_self_adjoint_domain_json(domain_json)
    export_index_mirror_closure_markdown(index_md)
    export_index_mirror_closure_json(index_json)

    data = json.loads(closure_json.read_text())
    assert data["ht_dependency_status"] == HT_THEOREM_BLOCKED_BY_DOMAIN
    assert data["theorem_complete"] is False
    assert "Relative-Bound Audit" in closure_md.read_text()
    assert json.loads(domain_json.read_text())["status"] == SELF_ADJOINT_DOMAIN_OPEN
    assert json.loads(index_json.read_text())["mirror_status"] == MIRROR_EXCLUSION_OPEN


def test_operator_domain_index_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "operator_domain_index_closure.py",
            "full_operator_domain.py",
            "self_adjoint_domain.py",
            "twisted_dirac_index_theorem.py",
            "mirror_exclusion_theorem.py",
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


def test_operator_domain_index_closure_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_operator_domain_index_closure_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_generated_v17_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "operator_domain_index_closure_report.md",
        root / "theory" / "operator_domain_index_closure_report.json",
        root / "theory" / "self_adjoint_domain_report.md",
        root / "theory" / "self_adjoint_domain_report.json",
        root / "theory" / "index_mirror_closure_report.md",
        root / "theory" / "index_mirror_closure_report.json",
        root / "manuscript" / "BHSM_v1_7_operator_domain_index_note.md",
        root / "notebooks" / "47_operator_domain_index_closure.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    text = paths[0].read_text() + paths[6].read_text()
    assert "HT_THEOREM_BLOCKED_BY_DOMAIN" in text
    assert "does not prove" in text.lower()

