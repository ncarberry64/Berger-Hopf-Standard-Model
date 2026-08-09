from __future__ import annotations

from fractions import Fraction

import numpy as np
from sympy import Rational, sqrt

from bhsm.interface.completion.moduli_clifford_matcher_zeta_v14_43 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    clifford_residual,
    clifford_square_residual,
    completion_payload,
    euclidean_gamma_matrices_4,
    field_rescaling_kinetic_coefficient,
    matcher_payload,
    materialize,
    minimum_complex_clifford_module_rank,
    moduli_clifford_payload,
    normalization_payload,
    orbital_cg_factors,
    orbital_spin_recoupling_factor,
    round_s3_abs_dirac_zeta_minus_one_times_radius,
    round_s3_abs_dirac_zeta_zero,
    round_s3_two_component_fermion_casimir_times_radius,
    spinor_recoupling_payload,
    spinor_total_j_branches,
    transmission_residual,
    unitarity_residual,
    zeta_payload,
)


def test_fr_line_has_exact_clifford_rank_obstruction() -> None:
    assert minimum_complex_clifford_module_rank(3) == 2
    assert minimum_complex_clifford_module_rank(4) == 4
    assert 1 < minimum_complex_clifford_module_rank(4)


def test_explicit_cl4_representation_and_square() -> None:
    gammas = euclidean_gamma_matrices_4()
    assert clifford_residual(gammas) < 1.0e-13
    assert clifford_square_residual(np.array([0.2, -0.4, 0.7, 1.3])) < 1.0e-13


def test_moduli_hodge_dirac_is_not_promoted_to_spacetime_dirac() -> None:
    payload = moduli_clifford_payload()
    assert payload["validation_passed"]
    assert payload["rank_obstruction"]["FR_line_complex_rank"] == 1
    assert "not by T*M4" in payload["canonical_moduli_square_root"]["why_not_spacetime_Dirac"]


def test_local_field_rescaling_ambiguity() -> None:
    assert abs(field_rescaling_kinetic_coefficient(9.0, 3.0) - 1.0) < 1.0e-13
    payload = normalization_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "OPEN_NOT_FIXED_BY_FR_HILBERT_NORM"


def test_self_adjoint_matcher_condition_is_stronger_than_unitarity() -> None:
    alpha = np.diag([1.0, 1.0, -1.0, -1.0]).astype(complex)
    good = np.diag([1.0, 1j, -1.0, -1j]).astype(complex)
    bad = np.array(
        [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, -1, 0],
            [0, 1, 0, -1],
        ],
        dtype=complex,
    ) / np.sqrt(2.0)
    assert unitarity_residual(good) < 1.0e-13
    assert unitarity_residual(bad) < 1.0e-13
    assert transmission_residual(alpha, alpha, good) < 1.0e-13
    assert transmission_residual(alpha, alpha, bad) > 1.0e-6
    assert matcher_payload()["validation_passed"]


def test_orbital_clebsch_factors_match_v12_1() -> None:
    factors = orbital_cg_factors()
    assert factors["up_heavy_middle_L3"]["exact"] == "1"
    assert factors["up_middle_light_L2"]["exact"] == "sqrt(10)/5"
    assert factors["down_heavy_middle_L3"]["exact"] == "1"
    assert factors["down_middle_light_L2"]["exact"] == "-sqrt(21)/7"


def test_spinor_lift_has_two_branches_for_nonzero_orbital_J() -> None:
    assert spinor_total_j_branches(0) == (Rational(1, 2),)
    assert spinor_total_j_branches(3) == (Rational(5, 2), Rational(7, 2))
    assert spinor_total_j_branches(5) == (Rational(9, 2), Rational(11, 2))


def test_exact_sixj_recoupling_factors() -> None:
    assert orbital_spin_recoupling_factor(
        target_orbital_j=3,
        target_total_j=Rational(5, 2),
        source_orbital_j=0,
        source_total_j=Rational(1, 2),
        tensor_rank=3,
    ) == -sqrt(42) / 7
    assert orbital_spin_recoupling_factor(
        target_orbital_j=5,
        target_total_j=Rational(11, 2),
        source_orbital_j=3,
        source_total_j=Rational(5, 2),
        tensor_rank=2,
    ) == 0


def test_spinor_recoupling_payload_keeps_full_matrix_open() -> None:
    payload = spinor_recoupling_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["one_up_L2_spinor_branch_vanishes"]
    assert payload["validation"]["full_spinorial_L2_L3_matrix_not_emitted"]


def test_round_s3_zeta_values_are_exact() -> None:
    assert round_s3_abs_dirac_zeta_zero() == Fraction(0, 1)
    assert round_s3_abs_dirac_zeta_minus_one_times_radius() == Fraction(-17, 480)
    assert round_s3_two_component_fermion_casimir_times_radius() == Fraction(17, 960)
    assert zeta_payload()["validation_passed"]


def test_completion_gate_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["gate_status"]["local_spacetime_Clifford_principal_symbol"] == "OPEN_NOT_DERIVED"
    assert payload["gate_status"]["renormalized_L2_L3_polarization"] == "OPEN"
    assert payload["gate_status"]["BHSM_complete"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
