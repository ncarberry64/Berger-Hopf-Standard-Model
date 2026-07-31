import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.master_action import complex_profile_isospectral_attachment as v86
from bhsm.interface.master_action import topographic_profile_component_selection as v85


def test_polar_unitary_is_unitary_and_unique_full_rank_route():
    transfer = v85.heat_kernel_cross_matrix()
    unitary = v86.polar_unitary(transfer)
    assert np.allclose(unitary.conj().T @ unitary, np.eye(3), atol=1e-12)


def test_minimum_trace_alignment_removes_all_discrete_assignments():
    report = v86.isospectral_alignment_audit()
    assert report["slot_assignments_remaining"] == 0
    assert all(row["trace_minimum_verified"] for row in report["sectors"].values())
    assert all(row["frozen_spectrum_preserved"] for row in report["sectors"].values())


def test_single_hopf_shift_is_rephasing_only_for_cross_polar():
    report = v86.single_hopf_shift_no_go()
    assert report["magnitudes_unchanged"]
    assert abs(report["jarlskog_base"]) < 1e-14
    assert abs(report["jarlskog_shifted"]) < 1e-14


def test_oriented_incidence_candidate_is_close_but_not_complete():
    report = v86.oriented_incidence_candidate_audit()
    assert abs(report["relative_angle_errors"]["sin_theta_12"]) < 0.04
    assert abs(report["relative_angle_errors"]["sin_theta_23"]) < 0.10
    assert abs(report["relative_angle_errors"]["sin_theta_13"]) > 0.60
    assert abs(report["candidate_jarlskog"]) < 1e-14
    assert not report["all_within_declared_ten_percent"]


def test_g2_c3_optimistic_complex_candidate_generates_cp_but_fails_tolerance():
    report = v86.g2_c3_profile_audit()["optimistic_mixed_normalization"]
    assert report["nonzero_CP"]
    assert report["candidate_jarlskog"] > 0
    assert not report["all_within_declared_ten_percent"]
    assert not report["promotion_allowed"]


def test_character_normalized_profile_is_not_the_frozen_ckm_solution():
    report = v86.g2_c3_profile_audit()["character_normalized_profile"]
    assert report["nonzero_CP"]
    assert abs(report["relative_angle_errors"]["sin_theta_12"]) > 0.5
    assert not report["all_within_declared_ten_percent"]


def test_status_report_fail_closes_without_new_parameters():
    report = v86.status_report()
    assert report["validation_passed"]
    assert report["new_continuous_parameter_added"] is False
    assert report["frozen_predictions_changed"] is False
    assert report["physical_CKM_emitted"] is False
    assert report["physical_mass_emitted"] is False

