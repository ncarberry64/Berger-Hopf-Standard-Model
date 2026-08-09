from fractions import Fraction

import pytest

from bhsm.interface.completion.zeta_spectral_ray_v14_49 import (
    SpectralRay,
    cap_ray_vector,
    cutoff_spectral_moment_rank,
    determinant_2x2,
    generic_counterterm_matrix,
    q_level,
    solve_berger_spectral_amplitude,
    status_payload,
    zeta_local_branch_contract,
)


def test_q_levels() -> None:
    assert q_level(1) == 0
    assert q_level(2) == 5
    assert q_level(3) == 12


def test_generic_counterterm_rank_is_two() -> None:
    matrix = generic_counterterm_matrix()
    assert matrix == ((5, 25), (12, 144))
    assert determinant_2x2(matrix) == 420


def test_pure_dirac_weyl_ray_constraint() -> None:
    ray = SpectralRay()
    assert ray.c_r2 == Fraction(-2, 3)
    assert ray.c_ricci2 == Fraction(2, 1)
    assert ray.linear_constraint == 0


def test_spectral_cap_vectors_are_rank_one_in_amplitude() -> None:
    first = cap_ray_vector(amplitude=1.0, a_r2=3.0, b_ricci2=2.0, c_ricci2=4.0)
    second = cap_ray_vector(amplitude=7.0, a_r2=3.0, b_ricci2=2.0, c_ricci2=4.0)
    matrix = ((first[0], second[0]), (first[1], second[1]))
    assert determinant_2x2(matrix) == pytest.approx(0.0)


def test_berger_amplitude_solver() -> None:
    assert solve_berger_spectral_amplitude(pi_prime=6.0, local_ray_derivative=-3.0) == 2.0


def test_berger_amplitude_solver_fails_closed() -> None:
    with pytest.raises(ZeroDivisionError):
        solve_berger_spectral_amplitude(pi_prime=1.0, local_ray_derivative=0.0)


def test_generic_cutoff_has_three_moments() -> None:
    payload = cutoff_spectral_moment_rank()
    assert payload["independent_cutoff_moments"] == 3
    assert payload["dimension_four_local_terms_share_f0"] is True


def test_zeta_branch_is_explicitly_foundational() -> None:
    contract = zeta_local_branch_contract()
    assert contract["branch_type"] == "FOUNDATIONAL_CONDITIONAL_ZETA_LOCAL_ACTION"
    assert "the choice of zeta-local action itself" in contract["not_derived"]
    assert contract["input_compression"]["canonical_zeta_local_declaration"] == [
        "physical scale/matching prescription"
    ]


def test_status_fails_closed() -> None:
    payload = status_payload()
    assert payload["generic_counterterm_determinant"] == 420
    assert payload["claim_boundary"]["zero_input_BHSM_completed"] is False
    assert payload["claim_boundary"]["zeta_local_branch_adopted_officially"] is False
    assert payload["claim_boundary"]["frozen_predictions_changed"] is False
