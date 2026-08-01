from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src/bhsm/interface/master_action/topographic_profile_component_selection.py"
)
SPEC = importlib.util.spec_from_file_location("bhsm_v85", MODULE_PATH)
assert SPEC and SPEC.loader
v85 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v85)


def test_reproducing_kernel_selectors_are_normalized():
    ledger = v85.component_selector_ledger()
    assert all(row["norm_squared"] == 1 for rows in ledger.values() for row in rows)
    assert ledger["up"][1]["identity_frame_coefficients"] == [0, 0, 0, 0, 0, 0, 1]
    assert ledger["down"][1]["identity_frame_coefficients"] == [0, 0, 0, 1, 0, 0, 0]


def test_right_u1_neutral_profile_has_rank_at_most_one():
    audit = v85.right_u1_invariant_profile_audit()
    assert audit["required_right_weights"] == [[0, 0, -2], [3, 3, 1], [4, 4, 2]]
    assert audit["surviving_support_mask"] == [[1, 1, 0], [0, 0, 0], [0, 0, 0]]
    assert audit["maximum_possible_rank"] == 1
    assert audit["full_rank_CKM_possible"] is False


def test_every_determinant_term_requires_three_hopf_weights():
    audit = v85.full_rank_moment_requirement()
    assert audit["all_terms_require_three_distinct_right_weights"] is True
    assert audit["minimum_independent_Hopf_weight_moments"] == 3
    assert len(audit["determinant_permutation_weight_sets"]) == 6


def test_heat_kernel_sector_matrices_are_real_symmetric():
    for sector in ("charged_lepton", "up", "down"):
        matrix = v85.heat_kernel_sector_matrix(sector)
        assert matrix.shape == (3, 3)
        assert np.allclose(matrix, matrix.T, atol=1e-13)


def test_heat_kernel_cross_matrix_is_full_rank_but_not_unitary():
    matrix = v85.heat_kernel_cross_matrix()
    assert matrix.shape == (3, 3)
    assert np.linalg.matrix_rank(matrix, tol=1e-12) == 3
    assert abs(np.linalg.det(matrix) - 0.00209979914245694) < 2e-14
    assert not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-12)


def test_direct_profile_dressing_breaks_frozen_ratios():
    audit = v85.direct_profile_dressing_audit()
    assert audit["all_frozen_ratios_preserved"] is False
    assert all(
        row["frozen_ratios_preserved"] is False
        for row in audit["sectors"].values()
    )
    assert audit["sectors"]["up"]["multiplicative_shift"][1] > 2.5


def test_isospectral_orientation_preserves_ratios_but_is_ambiguous_and_cp_even():
    audit = v85.isospectral_orientation_audit()
    assert audit["frozen_singular_values_preserved_by_construction"] is True
    assert audit["joint_assignments"] == 36
    assert audit["distinct_absolute_overlap_matrices"] == 36
    assert audit["all_jarlskog_zero"] is True
    assert audit["action_selects_assignment"] is False


def test_status_report_is_fail_closed_and_validated():
    report = v85.status_report()
    assert report["validation_passed"] is True
    assert report["physical_mass_emitted"] is False
    assert report["CKM_matrix_emitted"] is False
    assert report["frozen_predictions_changed"] is False
    assert report["new_free_parameter_added"] is False
    assert report["final_verdict"] == v85.FINAL_VERDICT

