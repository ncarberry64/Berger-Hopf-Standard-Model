import json
from math import isclose
from pathlib import Path

from action_dependency_closure import (
    build_action_dependency_closure_report,
    empirical_residual_dependency_detected,
    export_action_dependency_closure_json,
    export_action_dependency_closure_markdown,
    export_unified_action_json,
    export_unified_action_markdown,
)
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from unified_bhsm_action import ACTION_SCAFFOLD_WITH_OPEN_NODES, FULL_ACTION_CLOSED, hidden_cycle_detected, unified_action_nodes


def test_unified_action_reports_open_nodes_not_full_closure():
    report = build_action_dependency_closure_report()

    assert report.status == ACTION_SCAFFOLD_WITH_OPEN_NODES
    assert report.status != FULL_ACTION_CLOSED
    assert report.theorem_complete is False
    assert report.open_nodes
    assert "ht_gap" in report.open_nodes
    assert "qcd_rg" in report.open_nodes


def test_unified_action_contains_required_dependencies():
    nodes = {node.id: node for node in unified_action_nodes()}

    for node_id in (
        "alpha_geometry",
        "overlap_width",
        "omega_f",
        "mode_ledger",
        "ckm_cp",
        "formal_kernel",
        "ht_gap",
        "scalar_topographic",
        "virtual_dressing",
        "qcd_rg",
        "state_ontology",
    ):
        assert node_id in nodes
    assert "formal_kernel" in nodes["ht_gap"].depends_on
    assert "mode_ledger" in nodes["ckm_cp"].depends_on


def test_unified_action_has_no_hidden_cycle_or_residual_dependency():
    report = build_action_dependency_closure_report()

    assert hidden_cycle_detected() is False
    assert report.hidden_circularity_detected is False
    assert empirical_residual_dependency_detected() is False
    assert report.empirical_residual_dependency_detected is False


def test_unified_action_exports_generate_cleanly(tmp_path):
    md = tmp_path / "action.md"
    data_path = tmp_path / "action.json"
    unified_md = tmp_path / "unified.md"
    unified_json = tmp_path / "unified.json"

    export_action_dependency_closure_markdown(md)
    export_action_dependency_closure_json(data_path)
    export_unified_action_markdown(unified_md)
    export_unified_action_json(unified_json)

    data = json.loads(data_path.read_text())
    assert data["status"] == ACTION_SCAFFOLD_WITH_OPEN_NODES
    assert data["theorem_complete"] is False
    assert "FULL_ACTION_CLOSED" not in md.read_text()


def test_unified_action_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_action_dependency_closure_report()

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


def test_generated_gate4_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "unified_bhsm_action_report.md",
        root / "theory" / "unified_bhsm_action_report.json",
        root / "theory" / "action_dependency_closure_report.md",
        root / "theory" / "action_dependency_closure_report.json",
        root / "manuscript" / "BHSM_unified_action_closure_note.md",
        root / "notebooks" / "46_unified_bhsm_action.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    data = json.loads(paths[3].read_text())
    assert data["status"] == ACTION_SCAFFOLD_WITH_OPEN_NODES
    assert data["theorem_complete"] is False
    assert "open nodes" in paths[4].read_text().lower()
