import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from formal_kernel_action_origin import (
    FORMAL_KERNEL_ACTION_DERIVED,
    FORMAL_KERNEL_BASIS_DERIVED,
    FORMAL_KERNEL_BOUNDARY_DERIVED,
    basis_coordinate_for_sector_zero,
    build_formal_kernel_action_origin_report,
    derive_formal_kernel_projector,
    export_formal_kernel_action_origin_json,
    export_formal_kernel_action_origin_markdown,
    formal_kernel_action_rules,
    modes_per_chirality_sector,
)
from semi_analytic_complement_bound import (
    build_semi_analytic_complement_bound,
    diagonal_complement_modes,
    export_semi_analytic_complement_bound_json,
    export_semi_analytic_complement_bound_markdown,
)


def test_formal_kernel_coordinates_are_basis_derived_from_sector_ordering():
    assert modes_per_chirality_sector(4) == 9
    assert basis_coordinate_for_sector_zero("lepton", 4) == 0
    assert basis_coordinate_for_sector_zero("up", 4) == 18
    assert basis_coordinate_for_sector_zero("down", 4) == 36

    derivation = derive_formal_kernel_projector(4)

    assert derivation.protected_coordinates == (0, 18, 36)
    assert derivation.old_coordinate_first_coordinates == (0, 1, 2)
    assert derivation.protected_sectors == ("lepton", "up", "down")
    assert derivation.status == FORMAL_KERNEL_BASIS_DERIVED
    assert derivation.theorem_complete is False


def test_formal_kernel_action_rules_are_conservative_not_full_action_derived():
    rules = formal_kernel_action_rules()
    statuses = {rule.id: rule.status for rule in rules}

    assert statuses["R1_sector_labeled_kernel"] == FORMAL_KERNEL_BOUNDARY_DERIVED
    assert statuses["R4_basis_ordering"] == FORMAL_KERNEL_BASIS_DERIVED
    assert FORMAL_KERNEL_ACTION_DERIVED not in statuses.values()
    assert all(rule.limitations for rule in rules)


def test_action_origin_report_keeps_theorem_open():
    report = build_formal_kernel_action_origin_report()

    assert report.projector_derivation.protected_coordinates == (0, 18, 36)
    assert report.projector_derivation.projector_rank == 3
    assert report.projector_derivation.projector_idempotent is True
    assert report.theorem_scaffold.theorem_complete is False
    assert report.theorem_complete is False


def test_semi_analytic_complement_bound_clears_required_threshold():
    bound = build_semi_analytic_complement_bound()
    first = bound.first_diagonal_complement_mode

    assert bound.protected_coordinates == (0, 18, 36)
    assert bound.old_coordinate_first_coordinates == (0, 1, 2)
    assert first.coordinate == 1
    assert first.old_coordinate_first_protected is True
    assert first.protected_formal_kernel is False
    assert bound.diagonal_lower_bound > bound.required_dirac_lower_bound
    assert bound.gershgorin_lower_bound > bound.required_dirac_lower_bound
    assert bound.structured_relative_lower_bound > bound.required_dirac_lower_bound
    assert bound.clears_required_bound is True
    assert bound.theorem_complete is False


def test_diagonal_complement_modes_exclude_formal_kernel_not_old_coordinate_first():
    rows = diagonal_complement_modes()
    coordinates = [row.coordinate for row in rows]

    assert 0 not in coordinates
    assert 18 not in coordinates
    assert 36 not in coordinates
    assert 1 in coordinates
    assert 2 in coordinates


def test_no_forbidden_empirical_modules_are_imported_by_action_origin_modules():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("formal_kernel_action_origin.py", "semi_analytic_complement_bound.py")
    )
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_formal_kernel_action_origin_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_formal_kernel_action_origin_report()
    build_semi_analytic_complement_bound()

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


def test_action_origin_exports_generate_cleanly(tmp_path):
    action_md = tmp_path / "action.md"
    action_json = tmp_path / "action.json"
    bound_md = tmp_path / "bound.md"
    bound_json = tmp_path / "bound.json"

    export_formal_kernel_action_origin_markdown(action_md)
    export_formal_kernel_action_origin_json(action_json)
    export_semi_analytic_complement_bound_markdown(bound_md)
    export_semi_analytic_complement_bound_json(bound_json)

    assert "(0, 18, 36)" in action_md.read_text()
    assert json.loads(action_json.read_text())["projector_derivation"]["status"] == FORMAL_KERNEL_BASIS_DERIVED
    assert "SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES" in bound_md.read_text()
    assert json.loads(bound_json.read_text())["clears_required_bound"] is True


def test_generated_v1_3n_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "formal_kernel_action_origin_report.md",
        root / "theory" / "formal_kernel_action_origin_report.json",
        root / "theory" / "semi_analytic_complement_bound_report.md",
        root / "theory" / "semi_analytic_complement_bound_report.json",
        root / "manuscript" / "v1_3n_formal_kernel_action_origin_note.md",
        root / "notebooks" / "36_formal_kernel_action_origin.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    action_text = artifact_paths[0].read_text()
    bound_text = artifact_paths[2].read_text()
    action_data = json.loads(artifact_paths[1].read_text())
    note_text = artifact_paths[4].read_text()

    assert FORMAL_KERNEL_BASIS_DERIVED in action_text
    assert "SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES" in bound_text
    assert action_data["theorem_complete"] is False
    assert "does not prove" in note_text
    assert "fully proven" not in note_text.lower()
