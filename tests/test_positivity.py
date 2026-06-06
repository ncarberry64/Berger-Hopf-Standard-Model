import numpy as np
import pytest

from positivity import (
    compensated_barrier,
    complement_projector,
    diagonal_proxy_operator,
    finite_berger_modes,
    gap_condition_with_operator,
    is_psd,
    is_symmetric,
    min_eigenvalue,
    orthogonal_projector,
    psd_barrier_from_q,
    restrict_to_complement,
    zero_mode_basis_from_modes,
)
from spectral_gap import MU_H, natural_lambda2


def _finite_basis_case(n_max=4):
    modes = finite_berger_modes(n_max)
    zero_basis = zero_mode_basis_from_modes(modes)
    base = diagonal_proxy_operator(modes)
    return modes, zero_basis, base


def test_q_dagger_q_is_positive_semidefinite():
    q = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0]])
    barrier = psd_barrier_from_q(q)

    assert is_symmetric(barrier)
    assert is_psd(barrier)
    assert min_eigenvalue(barrier) >= -1e-10


def test_projectors_and_restriction_remove_zero_mode():
    modes, zero_basis, base = _finite_basis_case()
    p0 = orthogonal_projector(zero_basis)
    p_perp = complement_projector(zero_basis)
    restricted = restrict_to_complement(base, zero_basis)

    assert np.allclose(p0 @ p0, p0)
    assert np.allclose(p_perp @ p_perp, p_perp)
    assert np.allclose(p0 @ p_perp, np.zeros_like(p0))
    assert restricted.shape == (len(modes) - zero_basis.shape[1], len(modes) - zero_basis.shape[1])


def test_psd_profile_term_never_reduces_complement_gap():
    _, zero_basis, base = _finite_basis_case()
    profile = psd_barrier_from_q(np.diag([0.0] + [2.0] * (base.shape[0] - 1)))

    base_result = gap_condition_with_operator(base, np.zeros_like(base), zero_basis, MU_H)
    psd_result = gap_condition_with_operator(base, profile, zero_basis, MU_H)

    assert psd_result["restricted_profile_min_eigenvalue"] >= 0.0
    assert psd_result["restricted_min_eigenvalue"] >= base_result["restricted_min_eigenvalue"]
    assert psd_result["passes"] is True


def test_negative_well_can_break_proxy_gap():
    _, zero_basis, base = _finite_basis_case()
    negative_well = np.diag([0.0] + [-0.01 * MU_H] * (base.shape[0] - 1))

    result = gap_condition_with_operator(base, negative_well, zero_basis, MU_H)

    assert result["restricted_profile_min_eigenvalue"] < 0.0
    assert result["passes"] is False


def test_compensated_barrier_restores_gap_only_when_complement_profile_is_nonnegative():
    _, zero_basis, base = _finite_basis_case()
    dimension = base.shape[0]
    negative_well = np.diag([0.0] + [-0.01 * MU_H] * (dimension - 1))
    under = negative_well + psd_barrier_from_q(np.diag([0.0] + [1.0] * (dimension - 1)))
    restored = negative_well + psd_barrier_from_q(
        np.diag([0.0] + [np.sqrt(0.01 * MU_H)] * (dimension - 1))
    )

    under_result = gap_condition_with_operator(base, under, zero_basis, MU_H)
    restored_result = gap_condition_with_operator(base, restored, zero_basis, MU_H)

    assert under_result["restricted_profile_min_eigenvalue"] < 0.0
    assert under_result["passes"] is False
    assert restored_result["restricted_profile_min_eigenvalue"] >= -1e-10
    assert restored_result["passes"] is True


def test_compensated_q_barrier_subtracts_only_protected_zero_subspace():
    _, zero_basis, base = _finite_basis_case()
    q = np.diag([0.0] + [3.0] * (base.shape[0] - 1))
    barrier = compensated_barrier(q, zero_basis, zero_mode_shift=5.0)
    zero_vector = zero_basis[:, 0]
    restricted_barrier = restrict_to_complement(barrier, zero_basis)

    assert np.allclose(complement_projector(zero_basis) @ zero_vector, np.zeros_like(zero_vector))
    assert np.allclose(barrier @ zero_vector, -5.0 * zero_vector)
    assert is_psd(restricted_barrier)


def test_complement_only_barrier_leaves_zero_mode_subspace_unchanged():
    _, zero_basis, base = _finite_basis_case()
    q = np.diag([0.0] + [2.0] * (base.shape[0] - 1))
    barrier = psd_barrier_from_q(q)
    zero_vector = zero_basis[:, 0]

    assert np.allclose(barrier @ zero_vector, np.zeros_like(zero_vector))


def test_no_function_silently_adjusts_lambda2():
    modes = finite_berger_modes(3)
    default_operator = diagonal_proxy_operator(modes)
    explicit_natural = diagonal_proxy_operator(modes, lambda2=natural_lambda2())
    explicit_wide = diagonal_proxy_operator(modes, lambda2=10.0)

    assert np.allclose(default_operator, explicit_natural)
    assert not np.allclose(default_operator, explicit_wide)
    with pytest.raises(ValueError):
        diagonal_proxy_operator(modes, lambda2=0.0)


def test_gap_condition_reports_explicit_pass_fail():
    _, zero_basis, base = _finite_basis_case()
    passing = gap_condition_with_operator(base, np.zeros_like(base), zero_basis, MU_H)
    failing = gap_condition_with_operator(base, -0.01 * MU_H * np.eye(base.shape[0]), zero_basis, MU_H)

    assert type(passing["passes"]) is bool
    assert type(failing["passes"]) is bool
    assert passing["passes"] is True
    assert failing["passes"] is False
