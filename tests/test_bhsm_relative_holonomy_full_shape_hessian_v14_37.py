from __future__ import annotations

from math import pi

import numpy as np

from bhsm.interface.completion.relative_holonomy_full_shape_hessian_completion_gate_v14_37 import (
    all_payloads,
    materialization_hashes,
)
from bhsm.interface.completion.relative_holonomy_full_shape_hessian_v14_37 import (
    MESHES,
    SHAPE_DEGREES,
    chain_rephasing,
    completion_payload,
    coexact_shape_eigenvalues,
    critical_mixed_magnitude,
    full_shape_spectrum_payload,
    holonomy_hessian_audit_payload,
    mixed_bifurcation_threshold_payload,
    phase_dressed_chain,
    polar_exact_shape_eigenvalues,
    polar_shape_eigenvalues,
    relative_edge_holonomy,
    twisted_circle_eigenvalue,
    two_block_eigenvalues,
    z6_anisotropy,
    z6_hessian_at_origin,
)


def test_isolated_v12_chain_phases_are_unitary_rephasings() -> None:
    diagonal = (0.0, 3.0, 7.0)
    base = phase_dressed_chain(diagonal, 0.2, 0.1, 0.0, 0.0)
    dressed = phase_dressed_chain(diagonal, 0.2, 0.1, pi / 5.0, -pi / 7.0)
    assert np.allclose(np.linalg.eigvalsh(base), np.linalg.eigvalsh(dressed), atol=1.0e-13)
    unitary = chain_rephasing(pi / 5.0, -pi / 7.0)
    assert np.allclose(unitary.conj().T @ unitary, np.eye(3), atol=1.0e-13)
    assert abs(relative_edge_holonomy(0.0, 0.0, pi / 3.0, 0.0) - pi / 3.0) < 1.0e-15


def test_flat_holonomy_and_z6_anisotropy_do_not_supply_negative_quadratic_curvature() -> None:
    assert min(twisted_circle_eigenvalue(n) for n in range(-6, 7)) >= 0.0
    assert np.array_equal(z6_hessian_at_origin(), np.zeros((2, 2)))
    epsilon = 1.0e-3 * np.exp(1j * 0.37)
    assert abs(z6_anisotropy(epsilon)) < 3.0e-18


def test_two_block_bifurcation_threshold_is_exact_and_phase_independent() -> None:
    lambda_u, lambda_d = 0.004, 0.009
    critical = critical_mixed_magnitude(lambda_u, lambda_d)
    assert abs(critical - 0.006) < 1.0e-15
    assert np.min(two_block_eigenvalues(lambda_u, lambda_d, 0.99 * critical)) > 0.0
    assert abs(np.min(two_block_eigenvalues(lambda_u, lambda_d, critical))) < 1.0e-14
    assert np.min(two_block_eigenvalues(lambda_u, lambda_d, 1.01 * critical)) < 0.0


def test_full_nonisometric_shape_surrogate_has_no_negative_requested_mode() -> None:
    for ell in SHAPE_DEGREES:
        assert np.min(polar_shape_eigenvalues(ell, points=160, count=2)) > 0.0
        assert np.min(coexact_shape_eigenvalues(ell, points=160, count=2)) > 0.0
        assert np.min(polar_exact_shape_eigenvalues(ell, points=160, count=2)) > 0.0


def test_coexact_ell1_stabilizer_mode_converges_toward_zero() -> None:
    values = [float(coexact_shape_eigenvalues(1, points=points, count=1)[0]) for points in MESHES]
    assert values[0] > values[1] > values[2] > 0.0


def test_ell2_shape_modes_remain_positive_under_mesh_refinement() -> None:
    for points in MESHES:
        assert polar_shape_eigenvalues(2, points=points, count=1)[0] > 0.0
        assert coexact_shape_eigenvalues(2, points=points, count=1)[0] > 0.0
        assert polar_exact_shape_eigenvalues(2, points=points, count=1)[0] > 0.0


def test_scientific_payloads_validate_and_fail_closed() -> None:
    for payload in (
        holonomy_hessian_audit_payload(),
        full_shape_spectrum_payload(),
        mixed_bifurcation_threshold_payload(),
        completion_payload(),
    ):
        assert payload["validation_passed"]
    gate = completion_payload()
    assert gate["v12_holonomy_direct_Hessian_gate"] == "FAILED_AS_QUADRATIC_AMPLITUDE_SOURCE"
    assert gate["v13_1_full_shape_surrogate_gate"] == "PASSED_NO_NEGATIVE_TESTED_ELL_MODE"
    assert gate["joint_mixed_Hessian_gate"] == "OPEN_ACTION_OWNERSHIP_AND_NORMALIZATION"
    assert gate["BHSM_complete"] is False


def test_deterministic_materialization(tmp_path) -> None:
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert len(first) == len(all_payloads()) == 4
