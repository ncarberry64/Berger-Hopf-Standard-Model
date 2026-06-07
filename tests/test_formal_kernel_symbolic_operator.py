import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from coordinate_free_subspace import (
    BASIS_REALIZED,
    FULL_OPERATOR_PROVEN,
    basis_realization_map,
    basis_realization_scan,
    build_coordinate_free_subspace_report,
    export_coordinate_free_subspace_json,
    export_coordinate_free_subspace_markdown,
    formal_kernel_subspace,
)
from formal_kernel_operator import DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
from formal_kernel_symbolic_operator import (
    build_symbolic_formal_kernel_report,
    export_symbolic_formal_kernel_json,
    export_symbolic_formal_kernel_markdown,
    symbolic_complement_bound,
    symbolic_operator_terms,
)


def test_coordinate_free_formal_kernel_is_exact_sector_triple():
    subspace = formal_kernel_subspace()

    assert subspace.name == "K_formal"
    assert subspace.sectors == ("lepton", "up", "down")
    assert subspace.spanning_states == (
        "|ell,0,0,q=0,chi=-1>",
        "|u,0,0,q=0,chi=-1>",
        "|d,0,0,q=0,chi=-1>",
    )
    assert subspace.k == 0
    assert subspace.j == 0
    assert subspace.q == 0
    assert subspace.chirality == -1
    assert subspace.dimension == 3
    assert subspace.theorem_complete is False


def test_basis_formula_gives_formal_coordinates_for_kmax_4():
    realization = basis_realization_map(4)

    assert realization.modes_per_chirality_sector == 9
    assert realization.sector_coordinates == {"lepton": 0, "up": 18, "down": 36}
    assert realization.realized_coordinates == (0, 18, 36)
    assert realization.operator_coordinates == (0, 18, 36)
    assert realization.old_coordinate_first_block == (0, 1, 2)
    assert realization.realized_coordinates != realization.old_coordinate_first_block
    assert realization.matches_current_basis is True
    assert realization.status == BASIS_REALIZED


def test_basis_formula_matches_current_operator_for_multiple_kmax_values():
    rows = basis_realization_scan((4, 6, 8, 10, 12))

    assert len(rows) == 5
    assert all(row.matches_current_basis for row in rows)
    assert all(row.status == BASIS_REALIZED for row in rows)
    assert rows[0].realized_coordinates == (0, 18, 36)
    assert rows[1].realized_coordinates == (0, 32, 64)
    assert all(row.realized_coordinates != (0, 1, 2) for row in rows)


def test_symbolic_operator_terms_are_classified_and_preserve_kernel():
    terms = symbolic_operator_terms()
    by_id = {term.id: term for term in terms}

    assert {"D_diag_squared", "V_Hopf", "V_boundary", "V_chi", "K_sector", "P_lift_perp", "PSD_profile"} <= set(by_id)
    assert by_id["K_sector"].classification == "OFF_DIAGONAL_BOUNDED"
    assert by_id["P_lift_perp"].classification == "PSD_EXACT"
    assert by_id["PSD_profile"].can_lower_complement_gap is False
    assert all(term.classification for term in terms)
    assert all(term.vanishes_on_k_formal for term in terms)
    assert all(term.preserves_k_formal for term in terms)
    assert all(term.limitations for term in terms)


def test_symbolic_complement_bound_clears_threshold_without_theorem_completion():
    bound = symbolic_complement_bound()

    assert bound.model_level == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert bound.structured_relative_lower_bound > bound.required_dirac_lower_bound
    assert bound.clears_required_dirac_bound is True
    assert bound.clears_mu_h_after_heat_lift is True
    assert bound.heat_lift_lower_bound >= bound.mu_h
    assert bound.theorem_complete is False


def test_symbolic_report_is_not_labeled_full_proof():
    report = build_symbolic_formal_kernel_report()

    assert report.model_level == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert report.basis_realization.realized_coordinates == (0, 18, 36)
    assert report.theorem_complete is False
    assert FULL_OPERATOR_PROVEN not in {term.status for term in report.terms}
    assert report.complement_bound.status != FULL_OPERATOR_PROVEN
    assert "does not prove" in report.correct_claim


def test_no_forbidden_empirical_modules_are_imported_by_symbolic_modules():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("coordinate_free_subspace.py", "formal_kernel_symbolic_operator.py")
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


def test_symbolic_formal_kernel_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_coordinate_free_subspace_report()
    build_symbolic_formal_kernel_report()

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


def test_symbolic_exports_generate_cleanly(tmp_path):
    subspace_md = tmp_path / "subspace.md"
    subspace_json = tmp_path / "subspace.json"
    operator_md = tmp_path / "operator.md"
    operator_json = tmp_path / "operator.json"

    export_coordinate_free_subspace_markdown(subspace_md)
    export_coordinate_free_subspace_json(subspace_json)
    export_symbolic_formal_kernel_markdown(operator_md)
    export_symbolic_formal_kernel_json(operator_json)

    assert "K_formal" in subspace_md.read_text()
    assert json.loads(subspace_json.read_text())["basis_realization"]["realized_coordinates"] == [0, 18, 36]
    assert "D_FK^2" in operator_md.read_text()
    assert json.loads(operator_json.read_text())["theorem_complete"] is False


def test_generated_v1_3o_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "formal_kernel_symbolic_operator.md",
        root / "theory" / "formal_kernel_symbolic_operator.json",
        root / "theory" / "coordinate_free_subspace_report.md",
        root / "theory" / "coordinate_free_subspace_report.json",
        root / "manuscript" / "v1_3o_symbolic_formal_kernel_note.md",
        root / "notebooks" / "37_symbolic_formal_kernel_operator.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    operator_text = artifact_paths[0].read_text()
    subspace_data = json.loads(artifact_paths[3].read_text())
    note_text = artifact_paths[4].read_text().lower()

    assert "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL" in operator_text
    assert subspace_data["basis_realization"]["realized_coordinates"] == [0, 18, 36]
    assert subspace_data["theorem_complete"] is False
    assert "full operator proven" not in note_text
    assert "fully proven" not in note_text
