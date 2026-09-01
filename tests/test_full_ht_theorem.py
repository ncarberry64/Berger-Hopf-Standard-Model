import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from full_ht_theorem import (
    FULL_HT_THEOREM_PROVEN,
    FORMAL_KERNEL_SCAFFOLD_STRONG,
    build_full_ht_theorem_report,
    export_full_ht_theorem_json,
    export_full_ht_theorem_markdown,
)
from infinite_basis_ht_bound import (
    INFINITE_BASIS_OPEN,
    build_infinite_basis_ht_bound_report,
    export_infinite_basis_ht_bound_json,
    export_infinite_basis_ht_bound_markdown,
)
from twisted_dirac_kernel_theorem import INDEX_THEOREM_OPEN, formal_kernel_coordinates_kmax4, kernel_theorem_nodes


def test_full_ht_theorem_attempt_stops_at_open_nodes():
    report = build_full_ht_theorem_report()

    assert report.status == FORMAL_KERNEL_SCAFFOLD_STRONG
    assert report.status != FULL_HT_THEOREM_PROVEN
    assert report.theorem_complete is False
    assert report.formal_kernel_coordinates == (0, 18, 36)
    assert "infinite-basis" in " ".join(report.remaining_open_nodes)
    assert any("topological index theorem" in item for item in report.remaining_open_nodes)


def test_infinite_basis_report_keeps_full_bound_open():
    report = build_infinite_basis_ht_bound_report()
    statuses = {node.status for node in report.nodes}

    assert report.status == FORMAL_KERNEL_SCAFFOLD_STRONG
    assert report.theorem_complete is False
    assert INFINITE_BASIS_OPEN in statuses
    assert report.structured_relative_lower_bound == 6.729508865520464
    assert report.exact_finite_lower_bound == 6.8171156827281205
    assert report.heat_lift_lower_bound == 19591.98933512353


def test_kernel_nodes_keep_index_theorem_open():
    nodes = kernel_theorem_nodes()

    assert formal_kernel_coordinates_kmax4() == (0, 18, 36)
    assert any(node.status == INDEX_THEOREM_OPEN for node in nodes)
    assert any("dim ker D_twist = 3" in node.statement for node in nodes)


def test_full_ht_theorem_exports_generate_cleanly(tmp_path):
    ht_md = tmp_path / "full_ht.md"
    ht_json = tmp_path / "full_ht.json"
    inf_md = tmp_path / "infinite.md"
    inf_json = tmp_path / "infinite.json"

    export_full_ht_theorem_markdown(ht_md)
    export_full_ht_theorem_json(ht_json)
    export_infinite_basis_ht_bound_markdown(inf_md)
    export_infinite_basis_ht_bound_json(inf_json)

    ht = json.loads(ht_json.read_text())
    inf = json.loads(inf_json.read_text())
    assert ht["status"] == FORMAL_KERNEL_SCAFFOLD_STRONG
    assert ht["theorem_complete"] is False
    assert inf["theorem_complete"] is False
    assert "FULL_HT_THEOREM_PROVEN" in ht_md.read_text()
    assert "Status: `FORMAL_KERNEL_SCAFFOLD_STRONG`" in ht_md.read_text()


def test_full_ht_theorem_modules_do_not_import_empirical_or_residual_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "full_ht_theorem.py",
            "infinite_basis_ht_bound.py",
            "twisted_dirac_kernel_theorem.py",
        )
    )
    forbidden_tokens = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in sources for token in forbidden_tokens)


def test_full_ht_theorem_attempt_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_full_ht_theorem_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert bare_after.outputs["up_quark_ratios"]["light"] == dressed_after.outputs["up_quark_ratios"]["light"]
    assert bare_after.outputs["ckm"]["angles"]["sin_theta_13"] == dressed_after.outputs["ckm"]["angles"]["sin_theta_13"]
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_generated_gate1_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "full_ht_theorem_report.md",
        root / "theory" / "full_ht_theorem_report.json",
        root / "theory" / "infinite_basis_ht_bound_report.md",
        root / "theory" / "infinite_basis_ht_bound_report.json",
        root / "manuscript" / "BHSM_full_ht_theorem_attempt.md",
        root / "notebooks" / "43_full_ht_theorem_attempt.ipynb",
    )

    for path in paths:
        assert path.exists(), path

    data = json.loads(paths[1].read_text())
    assert data["status"] == FORMAL_KERNEL_SCAFFOLD_STRONG
    assert data["theorem_complete"] is False
    assert "not prove" in paths[4].read_text().lower()
