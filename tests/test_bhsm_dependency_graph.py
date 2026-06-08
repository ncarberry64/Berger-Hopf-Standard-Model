import json
from math import isclose
from pathlib import Path

from bhsm_dependency_graph import (
    ADOPTION_CANDIDATE,
    BASIS_REALIZED,
    BOUNDARY_FUNCTIONAL_DERIVED,
    FINITE_BASIS_SCAFFOLD,
    FROZEN_PREDICTION,
    OPEN,
    PARENT_ACTION_REDUCED,
    SEMI_ANALYTIC_SCAFFOLD,
    build_dependency_graph_report,
)
from bhsm_theorem_ledger import build_theorem_status_ledger
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


def test_dependency_graph_contains_required_nodes_and_status_categories():
    report = build_dependency_graph_report()
    nodes = {node.id: node for node in report.nodes}

    for node_id in (
        "alpha_geometry",
        "overlap_width",
        "mode_ledger",
        "omega_f",
        "parent_action_scaffold",
        "formal_kernel",
        "ht_gap",
        "scalar_decoupling",
        "virtual_dressing",
        "qcd_rg_matching",
        "ckm_cp",
        "pmns_effective",
        "state_ontology",
    ):
        assert node_id in nodes

    statuses = {node.status for node in report.nodes}
    assert FROZEN_PREDICTION in statuses
    assert BOUNDARY_FUNCTIONAL_DERIVED in statuses
    assert PARENT_ACTION_REDUCED in statuses
    assert BASIS_REALIZED in statuses
    assert SEMI_ANALYTIC_SCAFFOLD in statuses
    assert FINITE_BASIS_SCAFFOLD in statuses
    assert ADOPTION_CANDIDATE in statuses
    assert OPEN in statuses


def test_dependency_graph_has_no_hidden_circularity_or_residual_dependency():
    report = build_dependency_graph_report()

    assert report.hidden_circularity_detected is False
    assert report.empirical_residual_dependency_detected is False
    assert report.theorem_complete is False
    assert report.open_obligations[0].startswith("Prove the full twisted Dirac")


def test_theorem_ledger_keeps_major_theorems_open():
    ledger = build_theorem_status_ledger()
    rows = {row.id: row for row in ledger["rows"]}

    assert ledger["theorem_complete"] is False
    assert rows["ht_gap"].completed is False
    assert rows["scalar_decoupling"].completed is False
    assert rows["qcd_rg"].status == OPEN
    assert rows["virtual_dressing"].status == ADOPTION_CANDIDATE
    assert "Do not claim no-extra-light-state theorem proven" in rows["ht_gap"].forbidden_upgrade


def test_dependency_graph_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_dependency_graph_report()
    build_theorem_status_ledger()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_dependency_graph_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "bhsm_v2_dependency_graph.md",
        root / "theory" / "bhsm_v2_dependency_graph.json",
        root / "theory" / "bhsm_theorem_status_ledger.md",
        root / "theory" / "bhsm_theorem_status_ledger.json",
        root / "manuscript" / "BHSM_v2_roadmap_note.md",
    )

    for path in paths:
        assert path.exists(), path

    graph = json.loads(paths[1].read_text())
    ledger = json.loads(paths[3].read_text())
    note = paths[4].read_text().lower()

    assert graph["hidden_circularity_detected"] is False
    assert graph["empirical_residual_dependency_detected"] is False
    assert ledger["theorem_complete"] is False
    assert "does not claim" in note
    assert "fully proven" not in note
