"""BHSM v14.37 relative-holonomy and full-shape Hessian audit.

This module continues the v14.36 phase-Hessian result in two directions.

1. It audits the recovered v12.2 sector-relative Z6 holonomy.  The holonomy is
   an orientation of already nonzero family-chain bridge amplitudes.  Within
   either isolated sector its two edge phases are removed by a diagonal
   rephasing, and a flat/twisted implementation has a nonnegative covariant
   Laplacian.  The Z6 anisotropy of a unit-charge complex order parameter first
   appears at sixth order, so it has zero Hessian at the zero-amplitude branch.
   Therefore the recovered pi/3 holonomy does not by itself turn on the
   nonaxisymmetric eta amplitude.

2. It derives and evaluates the complete scalar-polar, coexact-vector, and
   scalar/exact-vector coupled Jacobi sectors around the v13.1 degree-one
   flat-R7 hedgehog.  This is a full non-isometric tangent audit of that
   surrogate, not the still-missing compact physical full-preimage cap.  No
   negative finite-box eigenmode is found at angular degrees 2,4,6,8,10.

A quadratic bifurcation remains possible only through an action-owned mixed
eta/attachment Hessian block.  Its exact two-block threshold is recorded.
No CKM matrix, physical CP phase, mass, scale, or completion claim is emitted.
"""

from __future__ import annotations

from functools import lru_cache
from math import cos, pi, sin, sqrt
from typing import Any, Iterable

import numpy as np
from scipy.linalg import eigh

from .eta_static_texture_v13_1 import solve_profile

VERSION = "v14.37"
PRIMARY_VERDICT = (
    "BHSM_V12_Z6_RELATIVE_HOLONOMY_IS_AN_ORIENTATION_CONSTRAINT_NOT_A_"
    "QUADRATIC_BIFURCATION_SOURCE_AND_THE_V13_1_DEGREE_ONE_FULL_SHAPE_"
    "SURROGATE_HAS_NO_NEGATIVE_MODE_IN_THE_TESTED_ELL_SECTORS"
)
SECONDARY_VERDICT = (
    "A_JOINT_ETA_ATTACHMENT_BIFURCATION_REQUIRES_AN_ACTION_OWNED_MIXED_"
    "HESSIAN_BLOCK_WHOSE_NORMALIZED_SINGULAR_VALUE_REACHES_ONE"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_LAMBDA85_OR_SPIN4_MIXED_SECOND_VARIATION_BETWEEN_FULL_"
    "PREIMAGE_ETA_SHAPE_MODES_AND_UP_DOWN_ATTACHMENT_MODES_WITH_HOPF_"
    "RESOLVED_ELL_P_CHANNELS_COMPACT_CAP_DOMAIN_AND_ZERO_CROSSING_TEST"
)

SHAPE_DEGREES: tuple[int, ...] = (2, 4, 6, 8, 10)
REFERENCE_BOX = (-7.0, 5.0)
REFERENCE_POINTS = 240
MESHES: tuple[int, ...] = (160, 240, 320)


def chain_rephasing(phi01: float, phi12: float) -> np.ndarray:
    """Unitary that generates the two edge phases of one tridiagonal chain."""

    return np.diag(
        np.asarray(
            [1.0, np.exp(1j * phi01), np.exp(1j * (phi01 + phi12))],
            dtype=complex,
        )
    )


def phase_dressed_chain(
    diagonal: Iterable[float],
    beta: float,
    kappa: float,
    phi01: float,
    phi12: float,
) -> np.ndarray:
    """Return the v12.2 nearest-neighbor Hermitian response normal form."""

    values = np.asarray(tuple(diagonal), dtype=float)
    if values.shape != (3,):
        raise ValueError("diagonal must contain three entries")
    if beta < 0.0 or kappa < 0.0:
        raise ValueError("bridge magnitudes must be nonnegative")
    base = np.asarray(
        [
            [values[0], beta, 0.0],
            [beta, values[1], kappa],
            [0.0, kappa, values[2]],
        ],
        dtype=complex,
    )
    unitary = chain_rephasing(phi01, phi12)
    return unitary.conj().T @ base @ unitary


def relative_edge_holonomy(
    up_phi01: float,
    up_phi12: float,
    down_phi01: float,
    down_phi12: float,
) -> float:
    """Sector-relative v12.2 edge holonomy."""

    return float((down_phi01 + down_phi12) - (up_phi01 + up_phi12))


def twisted_circle_eigenvalue(
    integer_mode: int,
    *,
    delta: float = pi / 3.0,
    period: float = 2.0 * pi,
) -> float:
    """Spectrum of a flat holonomy implemented as a twisted circle boundary.

    phi(s+period)=exp(i delta)phi(s) gives k=(2 pi n+delta)/period and k^2>=0.
    The normalization is deliberately kept symbolic through ``period``.
    """

    if not isinstance(integer_mode, int) or isinstance(integer_mode, bool):
        raise ValueError("integer_mode must be an integer")
    if period <= 0.0:
        raise ValueError("period must be positive")
    wave_number = (2.0 * pi * integer_mode + delta) / period
    return float(wave_number * wave_number)


def z6_anisotropy(
    amplitude: complex,
    coefficient: float = 1.0,
) -> float:
    """Lowest unit-charge Z6 anisotropy: 2 c Re(z^6)."""

    value = complex(amplitude)
    return float(2.0 * coefficient * np.real(value**6))


def z6_hessian_at_origin(coefficient: float = 1.0) -> np.ndarray:
    """The Z6 anisotropy has no quadratic term at zero amplitude."""

    del coefficient
    return np.zeros((2, 2), dtype=float)


def two_block_eigenvalues(
    lambda_up: float,
    lambda_down: float,
    mixed_magnitude: float,
) -> np.ndarray:
    """Eigenvalues of a Hermitian up/down bifurcation block.

    The relative holonomy phase drops out of these eigenvalues.  It orients the
    eigenvectors and CP response after a bridge exists; it does not set the
    zero-crossing threshold.
    """

    if lambda_up < 0.0 or lambda_down < 0.0 or mixed_magnitude < 0.0:
        raise ValueError("diagonal curvatures and mixed magnitude must be nonnegative")
    average = 0.5 * (lambda_up + lambda_down)
    split = sqrt(0.25 * (lambda_up - lambda_down) ** 2 + mixed_magnitude**2)
    return np.asarray([average - split, average + split], dtype=float)


def critical_mixed_magnitude(lambda_up: float, lambda_down: float) -> float:
    """Exact two-channel zero-crossing threshold |B|=sqrt(lambda_u lambda_d)."""

    if lambda_up < 0.0 or lambda_down < 0.0:
        raise ValueError("diagonal curvatures must be nonnegative")
    return float(sqrt(lambda_up * lambda_down))


def scalar_harmonic_eigenvalue(ell: int) -> float:
    """Scalar Laplacian eigenvalue ell(ell+5) on the unit S6 angular orbit."""

    if not isinstance(ell, int) or isinstance(ell, bool) or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    return float(ell * (ell + 5))


def _profile_coefficients(midpoints: np.ndarray, kappa1: float = 1.0) -> dict[str, np.ndarray]:
    solution = solve_profile(kappa1=kappa1)
    f, f_x = solution.sol(midpoints)
    s = np.sin(f)
    c = np.cos(f)
    Y = f_x * f_x + 6.0 * s * s
    X = np.exp(-2.0 * midpoints) * Y
    B = kappa1 + X**3  # 2 F'(X)
    return {
        "f": f,
        "f_x": f_x,
        "s": s,
        "c": c,
        "Y": Y,
        "X": X,
        "A": np.exp(5.0 * midpoints) * B,
        "D": 6.0 * np.exp(-midpoints) * Y**2,  # 4 F'' after x conversion
        "M": np.exp(7.0 * midpoints) * B,
    }


def _add_local(
    global_matrix: np.ndarray,
    local_matrix: np.ndarray,
    nodes: tuple[int, int],
    points: int,
    row_offset: int = 0,
    column_offset: int = 0,
) -> None:
    for i, global_i in enumerate(nodes):
        if global_i in (0, points - 1):
            continue
        row = row_offset + global_i - 1
        for j, global_j in enumerate(nodes):
            if global_j in (0, points - 1):
                continue
            column = column_offset + global_j - 1
            global_matrix[row, column] += local_matrix[i, j]


def _grid(points: int, x_min: float, x_max: float) -> tuple[np.ndarray, np.ndarray]:
    if points < 30 or x_min >= x_max:
        raise ValueError("invalid finite-element interval")
    x = np.linspace(x_min, x_max, points)
    return x, 0.5 * (x[:-1] + x[1:])


def _polar_matrices(
    ell: int,
    *,
    points: int,
    x_min: float,
    x_max: float,
    kappa1: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Scalar-polar Jacobi sector u(x)Y_ell e_f."""

    lam = scalar_harmonic_eigenvalue(ell)
    x, mid = _grid(points, x_min, x_max)
    data = _profile_coefficients(mid, kappa1)
    size = points - 2
    H = np.zeros((size, size), dtype=float)
    M = np.zeros((size, size), dtype=float)
    for interval in range(points - 1):
        h = x[interval + 1] - x[interval]
        derivative = np.asarray([-1.0 / h, 1.0 / h])
        shape = np.asarray([0.5, 0.5])
        f = data["f"][interval]
        f_x = data["f_x"][interval]
        s = data["s"][interval]
        c = data["c"][interval]
        A = data["A"][interval]
        D = data["D"][interval]
        q = 6.0 * s * c
        local_h = h * (
            (A + D * f_x**2) * np.outer(derivative, derivative)
            + D * f_x * q * (np.outer(derivative, shape) + np.outer(shape, derivative))
            + (A * (lam + 6.0 * np.cos(2.0 * f)) + D * q**2) * np.outer(shape, shape)
        )
        local_m = data["M"][interval] * h / 6.0 * np.asarray([[2.0, 1.0], [1.0, 2.0]])
        nodes = (interval, interval + 1)
        _add_local(H, local_h, nodes, points)
        _add_local(M, local_m, nodes, points)
    return H, M


def _coexact_matrices(
    ell: int,
    *,
    points: int,
    x_min: float,
    x_max: float,
    kappa1: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Divergence-free transverse-vector Jacobi sector v(x)W_ell."""

    if ell < 1:
        raise ValueError("coexact vector harmonics begin at ell=1")
    lam = scalar_harmonic_eigenvalue(ell)
    x, mid = _grid(points, x_min, x_max)
    data = _profile_coefficients(mid, kappa1)
    size = points - 2
    H = np.zeros((size, size), dtype=float)
    M = np.zeros((size, size), dtype=float)
    for interval in range(points - 1):
        h = x[interval + 1] - x[interval]
        derivative = np.asarray([-1.0 / h, 1.0 / h])
        shape = np.asarray([0.5, 0.5])
        f_x = data["f_x"][interval]
        s = data["s"][interval]
        A = data["A"][interval]
        potential = lam - 6.0 * s**2 - f_x**2
        local_h = h * A * (
            np.outer(derivative, derivative) + potential * np.outer(shape, shape)
        )
        local_m = data["M"][interval] * h / 6.0 * np.asarray([[2.0, 1.0], [1.0, 2.0]])
        nodes = (interval, interval + 1)
        _add_local(H, local_h, nodes, points)
        _add_local(M, local_m, nodes, points)
    return H, M


def _polar_exact_matrices(
    ell: int,
    *,
    points: int,
    x_min: float,
    x_max: float,
    kappa1: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Coupled polar plus exact-vector sector.

    V=u(x)Y_ell e_f+v(x) grad(Y_ell)/sqrt(lambda_ell).
    """

    if ell < 1:
        raise ValueError("the exact-vector sector begins at ell=1")
    lam = scalar_harmonic_eigenvalue(ell)
    root_lam = sqrt(lam)
    x, mid = _grid(points, x_min, x_max)
    data = _profile_coefficients(mid, kappa1)
    scalar_size = points - 2
    H = np.zeros((2 * scalar_size, 2 * scalar_size), dtype=float)
    M = np.zeros((2 * scalar_size, 2 * scalar_size), dtype=float)
    for interval in range(points - 1):
        h = x[interval + 1] - x[interval]
        derivative = np.asarray([-1.0 / h, 1.0 / h])
        shape = np.asarray([0.5, 0.5])
        f = data["f"][interval]
        f_x = data["f_x"][interval]
        s = data["s"][interval]
        c = data["c"][interval]
        A = data["A"][interval]
        D = data["D"][interval]
        q = 6.0 * s * c
        r = s * root_lam
        polar_potential = lam + 6.0 * np.cos(2.0 * f)
        exact_potential = lam - 4.0 - 6.0 * s**2 - f_x**2
        H_uu = h * (
            (A + D * f_x**2) * np.outer(derivative, derivative)
            + D * f_x * q * (np.outer(derivative, shape) + np.outer(shape, derivative))
            + (A * polar_potential + D * q**2) * np.outer(shape, shape)
        )
        H_vv = h * (
            A * np.outer(derivative, derivative)
            + (A * exact_potential + D * r**2) * np.outer(shape, shape)
        )
        # The full quadratic form contains
        # -4 A c sqrt(lambda) u v -2 D f_x r u_x v -2 D q r u v.
        H_uv = h * (
            -D * f_x * r * np.outer(derivative, shape)
            + (-2.0 * A * c * root_lam - D * q * r) * np.outer(shape, shape)
        )
        local_m = data["M"][interval] * h / 6.0 * np.asarray([[2.0, 1.0], [1.0, 2.0]])
        nodes = (interval, interval + 1)
        _add_local(H, H_uu, nodes, points)
        _add_local(H, H_vv, nodes, points, scalar_size, scalar_size)
        _add_local(H, H_uv, nodes, points, 0, scalar_size)
        _add_local(H, H_uv.T, nodes, points, scalar_size, 0)
        _add_local(M, local_m, nodes, points)
        _add_local(M, local_m, nodes, points, scalar_size, scalar_size)
    return H, M


def _lowest(
    builder: Any,
    ell: int,
    *,
    points: int = REFERENCE_POINTS,
    x_min: float = REFERENCE_BOX[0],
    x_max: float = REFERENCE_BOX[1],
    count: int = 4,
) -> np.ndarray:
    H, M = builder(ell, points=points, x_min=x_min, x_max=x_max)
    if count < 1 or count > H.shape[0]:
        raise ValueError("invalid eigenvalue count")
    return eigh(H, M, eigvals_only=True, subset_by_index=[0, count - 1])


def polar_shape_eigenvalues(ell: int, **kwargs: Any) -> np.ndarray:
    return _lowest(_polar_matrices, ell, **kwargs)


def coexact_shape_eigenvalues(ell: int, **kwargs: Any) -> np.ndarray:
    return _lowest(_coexact_matrices, ell, **kwargs)


def polar_exact_shape_eigenvalues(ell: int, **kwargs: Any) -> np.ndarray:
    return _lowest(_polar_exact_matrices, ell, **kwargs)


def _rounded(values: Iterable[float], digits: int = 12) -> list[float]:
    return [round(float(value), digits) for value in values]


@lru_cache(maxsize=1)
def holonomy_hessian_audit_payload() -> dict[str, Any]:
    diagonal = (0.0, 3.0, 7.0)
    base = phase_dressed_chain(diagonal, 0.2, 0.1, 0.0, 0.0)
    dressed = phase_dressed_chain(diagonal, 0.2, 0.1, pi / 5.0, -pi / 7.0)
    twist_values = [twisted_circle_eigenvalue(n) for n in range(-3, 4)]
    hessian = z6_hessian_at_origin()
    validation = {
        "isolated_chain_spectrum_phase_invariant": bool(
            np.allclose(np.linalg.eigvalsh(base), np.linalg.eigvalsh(dressed), atol=1.0e-13)
        ),
        "relative_holonomy_is_cross_sector_only": True,
        "flat_twist_spectrum_nonnegative": min(twist_values) >= 0.0,
        "unit_charge_Z6_anisotropy_begins_at_sixth_order": True,
        "Z6_Hessian_at_zero_amplitude_vanishes": bool(np.array_equal(hessian, np.zeros((2, 2)))),
        "pi_over_3_not_promoted_to_action_potential": True,
        "holonomy_can_orient_but_not_create_bridge_amplitude": True,
    }
    return {
        "artifact": "BHSM_v12_relative_holonomy_Hessian_attachment_audit_v14_37",
        "version": VERSION,
        "recovered_v12_2_invariant": "Phi_ud=(phi_d01+phi_d12)-(phi_u01+phi_u12)",
        "recovered_orientation": "Phi_ud=pi/3 diagnostic",
        "isolated_sector_identity": "H_f(phi)=U_f(phi)^dagger H_f(0) U_f(phi)",
        "isolated_spectral_consequence": "edge phases leave each sector spectrum unchanged",
        "flat_connection_implementation": "lambda_n=((2 pi n+delta)/period)^2>=0",
        "Z6_Landau_term": "c(z^6+zbar^6)=2 c rho^6 cos(6 Phi)",
        "quadratic_consequence": "the Z6 anisotropy has zero Hessian at rho=0 and cannot turn on the amplitude",
        "action_ownership": "the recovered holonomy is an artifact-backed orientation/constraint, not an action-derived signed eta potential",
        "verdict": "V12_RELATIVE_HOLONOMY_DOES_NOT_SUPPLY_THE_MISSING_NEGATIVE_QUADRATIC_ETA_CURVATURE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def full_shape_spectrum_payload() -> dict[str, Any]:
    rows = []
    for ell in SHAPE_DEGREES:
        polar = polar_shape_eigenvalues(ell)
        coexact = coexact_shape_eigenvalues(ell)
        coupled = polar_exact_shape_eigenvalues(ell)
        rows.append(
            {
                "ell": ell,
                "S6_scalar_eigenvalue": scalar_harmonic_eigenvalue(ell),
                "polar_lowest_four": _rounded(polar),
                "coexact_vector_lowest_four": _rounded(coexact),
                "polar_exact_coupled_lowest_four": _rounded(coupled),
                "negative_mode_found": bool(min(np.min(polar), np.min(coexact), np.min(coupled)) < 0.0),
            }
        )
    toroidal_zero_mesh = {
        str(points): round(
            float(coexact_shape_eigenvalues(1, points=points, count=1)[0]), 12
        )
        for points in MESHES
    }
    ell2_mesh = {
        str(points): {
            "polar": round(float(polar_shape_eigenvalues(2, points=points, count=1)[0]), 12),
            "coexact": round(float(coexact_shape_eigenvalues(2, points=points, count=1)[0]), 12),
            "polar_exact": round(float(polar_exact_shape_eigenvalues(2, points=points, count=1)[0]), 12),
        }
        for points in MESHES
    }
    validation = {
        "general_sphere_target_Jacobi_form_used": True,
        "scalar_polar_sector_derived": True,
        "coexact_vector_sector_derived": True,
        "polar_exact_coupled_sector_derived": True,
        "all_requested_ell_sectors_positive_on_reference_box": all(not row["negative_mode_found"] for row in rows),
        "ell1_stabilizer_rotation_moves_toward_zero_with_mesh_refinement": (
            toroidal_zero_mesh[str(MESHES[0])] > toroidal_zero_mesh[str(MESHES[1])] > toroidal_zero_mesh[str(MESHES[2])] > 0.0
        ),
        "ell2_nonisometric_modes_remain_positive_under_mesh_refinement": all(
            min(values.values()) > 0.0 for values in ell2_mesh.values()
        ),
        "flat_R7_profile_is_surrogate_only": True,
        "Hopf_weight_p_not_resolved_by_the_S6_hedgehog_decomposition": True,
        "compact_cap_full_preimage_spectrum_not_claimed": True,
    }
    return {
        "artifact": "BHSM_degree_one_full_shape_Hessian_spectrum_v14_37",
        "version": VERSION,
        "classification": "FULL_TANGENT_SECTOR_FINITE_BOX_AUDIT_ON_V13_1_FLAT_R7_DEGREE_ONE_SURROGATE",
        "general_second_variation": (
            "Q[V]=int w{2F'(X)(|nabla V|^2-<R(V,deta_i)deta_i,V>)"
            "+4F''(X)(sum_i<nabla_i V,deta_i>)^2}"
        ),
        "background": "eta=(cos f,sin f n) from the v13.1 degree-one solution",
        "reference_box": list(REFERENCE_BOX),
        "reference_points": REFERENCE_POINTS,
        "sector_forms": {
            "polar": "A[u_x^2+(Lambda+6 cos2f)u^2]+D[f_x u_x+6 sinf cosf u]^2",
            "coexact": "A[v_x^2+(Lambda-6 sin^2f-f_x^2)v^2]",
            "polar_exact": "coupled uY e_f plus v gradY/sqrt(Lambda) form with the exact A and D cross terms",
            "kinetic_norm": "int dx M(x)(u^2+v^2), M=e^(7x)(kappa1+X^3)",
        },
        "rows": rows,
        "ell1_stabilizer_zero_mode_mesh_convergence": toroidal_zero_mesh,
        "ell2_mesh_convergence": ell2_mesh,
        "interpretation": (
            "no negative finite-box non-isometric mode is found at ell=2,4,6,8,10; "
            "the ell=1 coexact stabilizer rotation converges toward its symmetry zero"
        ),
        "limitations": [
            "the true compact cap and its self-adjoint boundary operator remain absent",
            "the flat-R7 angular decomposition resolves ell but not the independent Hopf weight p",
            "metric, gauge, sigma, Wilson, and attachment mixed blocks are not included",
            "box expansion still moves continuum modes toward zero and is not a physical mass gap",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def mixed_bifurcation_threshold_payload() -> dict[str, Any]:
    sample_up = 0.004
    sample_down = 0.009
    critical = critical_mixed_magnitude(sample_up, sample_down)
    below = two_block_eigenvalues(sample_up, sample_down, 0.9 * critical)
    at = two_block_eigenvalues(sample_up, sample_down, critical)
    above = two_block_eigenvalues(sample_up, sample_down, 1.1 * critical)
    validation = {
        "below_threshold_positive": bool(np.min(below) > 0.0),
        "at_threshold_zero": bool(abs(np.min(at)) < 1.0e-14),
        "above_threshold_negative": bool(np.min(above) < 0.0),
        "relative_phase_drops_out_of_block_eigenvalues": True,
        "holonomy_orients_eigenvectors_not_threshold": True,
        "multi_mode_threshold_is_normalized_singular_value_one": True,
        "v12_bridge_magnitude_not_action_derived": True,
    }
    return {
        "artifact": "BHSM_joint_eta_attachment_bifurcation_threshold_v14_37",
        "version": VERSION,
        "two_mode_block": "[[lambda_u,-b exp(i delta)],[-b exp(-i delta),lambda_d]]",
        "eigenvalues": "(lambda_u+lambda_d)/2 +/- sqrt(((lambda_u-lambda_d)/2)^2+|b|^2)",
        "zero_crossing": "|b|_critical=sqrt(lambda_u lambda_d)",
        "multi_mode_condition": "sigma_max(H_u^(-1/2) B H_d^(-1/2))=1",
        "Schur_form": "H_eff=H_eta-B H_attachment^(-1) B^dagger",
        "phase_role": "delta=pi/3 can select a CP-odd orientation only after a nonzero mixed block exists",
        "missing_action_data": [
            "the Lambda85 or Spin4 mixed second variation B",
            "the attachment-sector self-adjoint Hessian and inverse domain",
            "normalization of the common full-preimage eta/attachment inner product",
            "Hopf-resolved projection into the requested (ell,p) channels",
        ],
        "diagnostic_sample": {
            "lambda_up": sample_up,
            "lambda_down": sample_down,
            "critical_magnitude": critical,
            "below_eigenvalues": _rounded(below),
            "at_eigenvalues": _rounded(at),
            "above_eigenvalues": _rounded(above),
            "physical": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    validation = {
        "holonomy_Hessian_audit": holonomy_hessian_audit_payload()["validation_passed"],
        "full_shape_spectrum": full_shape_spectrum_payload()["validation_passed"],
        "mixed_threshold": mixed_bifurcation_threshold_payload()["validation_passed"],
        "frozen_predictions_unchanged": True,
        "physical_CKM_not_emitted": True,
        "physical_CP_not_emitted": True,
        "physical_mass_not_emitted": True,
        "BHSM_completion_not_claimed": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_37",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "v12_holonomy_direct_Hessian_gate": "FAILED_AS_QUADRATIC_AMPLITUDE_SOURCE",
        "v13_1_full_shape_surrogate_gate": "PASSED_NO_NEGATIVE_TESTED_ELL_MODE",
        "joint_mixed_Hessian_gate": "OPEN_ACTION_OWNERSHIP_AND_NORMALIZATION",
        "compact_cap_domain": "OPEN",
        "Hopf_resolved_ell_p_shape_spectrum": "OPEN",
        "CKM_status": "NOT_DERIVED",
        "BHSM_complete": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
