import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_connection_components import (
    BLOCKING_COMPONENT_STATUSES,
    MISSING,
    build_bundle_connection_components_report,
    export_bundle_connection_components_json,
    export_bundle_connection_components_markdown,
)
from bundle_curvature_closure_decision import (
    COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_bundle_curvature_closure_decision,
    export_bundle_curvature_closure_decision_json,
    export_bundle_curvature_closure_decision_markdown,
)
from bundle_curvature_formula import CURVATURE_FORMULA_OPEN, build_bundle_curvature_formula_report, export_bundle_curvature_formula_json, export_bundle_curvature_formula_markdown
from complete_bundle_connection import build_complete_bundle_connection_report, export_complete_bundle_connection_json, export_complete_bundle_connection_markdown
from constants import S_OVERLAP
from curvature_formula_to_operator_map import build_curvature_formula_to_operator_map_report, export_curvature_formula_to_operator_map_json, export_curvature_formula_to_operator_map_markdown
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import build_full_ht_theorem_closure_report
from lichnerowicz_curvature_action import build_lichnerowicz_curvature_action_report, export_lichnerowicz_curvature_action_json, export_lichnerowicz_curvature_action_markdown
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_PROVEN, build_operator_identification_theorem_report


EXACT_GAP = "MIXED_CONNECTION_COEFFICIENT_RULE_GAP"
MISSING_COMPONENT = "mixed_hopf_base_boundary_coframe_connection"


def test_every_connection_component_is_classified_and_missing_component_is_named():
    report = build_bundle_connection_components_report()

    assert report.all_components_classified is True
    assert report.exact_missing_component == MISSING_COMPONENT
    assert MISSING_COMPONENT in report.blocking_components
    assert any(row.component_id == MISSING_COMPONENT and row.status == MISSING for row in report.components)
    assert all(row.status for row in report.components)
    assert report.theorem_complete is False


def test_complete_bundle_connection_stays_open_until_mixed_component_defined():
    report = build_complete_bundle_connection_report()

    assert report.status == "COMPLETE_BUNDLE_CONNECTION_OPEN"
    assert report.exact_missing_component == MISSING_COMPONENT
    assert report.theorem_complete is False
    assert "nabla_mixed" in report.decomposition


def test_every_curvature_contribution_is_mapped_and_remainder_is_open_once():
    report = build_bundle_curvature_formula_report()
    mapping = build_curvature_formula_to_operator_map_report()

    assert report.status == CURVATURE_FORMULA_OPEN
    assert report.all_contributions_mapped is True
    assert report.open_contributions == ("mixed_curvature_remainder",)
    assert mapping.all_contributions_classified is True
    assert mapping.r_bundle_rows == ("mixed_curvature_remainder",)
    assert mapping.r_bundle_classification == "REMAINDER_OPEN"


def test_lichnerowicz_action_is_open_on_required_targets():
    report = build_lichnerowicz_curvature_action_report()
    targets = {row.target for row in report.rows}

    assert report.status == "LICHNEROWICZ_CURVATURE_ACTION_OPEN"
    assert {"lepton_sector", "up_sector", "down_sector", "formal_kernel", "H_perp", "mirror_channels"}.issubset(targets)
    assert all(row.action_status == "OPEN" for row in report.rows)
    assert report.theorem_complete is False


def test_bundle_curvature_closure_decision_names_next_gap_without_overclaim():
    report = build_bundle_curvature_closure_decision()

    assert report.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert report.final_result != COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED
    assert report.exact_remaining_gap == EXACT_GAP
    assert report.exact_missing_component == MISSING_COMPONENT
    assert report.recommended_next_branch == "bhsm-v2.11-mixed-connection-coefficient-rule"
    assert report.final_paper_allowed is False
    assert report.theorem_complete is False


def test_complete_operator_and_full_ht_do_not_upgrade_from_missing_mixed_connection():
    operator = build_operator_identification_theorem_report()
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert operator.status != COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert operator.next_target_theorem == EXACT_GAP
    assert ht.theorem_complete is False
    assert ht.recommended_target_theorem == EXACT_GAP
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False


def test_formal_kernel_remains_sector_labeled_not_coordinate_first():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL


def test_v29_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "complete_bundle_connection.py",
            "bundle_connection_components.py",
            "bundle_curvature_formula.py",
            "lichnerowicz_curvature_action.py",
            "curvature_formula_to_operator_map.py",
            "bundle_curvature_closure_decision.py",
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
    assert all(token not in source for token in forbidden)


def test_v29_exports_generate(tmp_path):
    exporters = (
        (export_complete_bundle_connection_markdown, export_complete_bundle_connection_json, "connection"),
        (export_bundle_connection_components_markdown, export_bundle_connection_components_json, "components"),
        (export_bundle_curvature_formula_markdown, export_bundle_curvature_formula_json, "curvature"),
        (export_lichnerowicz_curvature_action_markdown, export_lichnerowicz_curvature_action_json, "action"),
        (export_curvature_formula_to_operator_map_markdown, export_curvature_formula_to_operator_map_json, "map"),
        (export_bundle_curvature_closure_decision_markdown, export_bundle_curvature_closure_decision_json, "decision"),
    )
    for export_md, export_json, stem in exporters:
        md_path = tmp_path / f"{stem}.md"
        json_path = tmp_path / f"{stem}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v29_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/complete_bundle_connection_report.md",
        "theory/complete_bundle_connection_report.json",
        "theory/bundle_connection_components_report.md",
        "theory/bundle_connection_components_report.json",
        "theory/bundle_curvature_formula_report.md",
        "theory/bundle_curvature_formula_report.json",
        "theory/lichnerowicz_curvature_action_report.md",
        "theory/lichnerowicz_curvature_action_report.json",
        "theory/curvature_formula_to_operator_map.md",
        "theory/curvature_formula_to_operator_map.json",
        "theory/bundle_curvature_closure_decision.md",
        "theory/bundle_curvature_closure_decision.json",
        "manuscript/BHSM_v2_9_complete_bundle_connection_curvature_note.md",
        "notebooks/59_complete_bundle_connection_curvature.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP in root.joinpath("theory/bundle_curvature_closure_decision.md").read_text()


def test_v29_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_bundle_curvature_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
