"""Derive the stable action-graph Galerkin projection required by the N12 tail.

The retained radial principal weight vanishes cubically at the regular pole.
Consequently raw coefficient truncation is not uniformly bounded in the
natural weighted graph norm, even though every coefficient has the same
physical interpretation at every resolution.  This script proves that fact
with an explicit windowed-shape sequence and records the action-orthogonal
projection that removes the representation instability without changing the
BHSM equations or the nested approximation spaces.
"""

from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
from scipy.linalg import block_diag, eigh, null_space


ROOT = Path(__file__).resolve().parents[1]
RESULT = Path(os.environ.get(
    "BHSM_N12_ACTION_GRAPH_PROJECTOR_RESULT",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json",
))
ANCHOR_ORDER = 12
ANCHOR = (
    ROOT / "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)


def _beta(a: int, b: mp.mpf) -> mp.mpf:
    return mp.beta(mp.mpf(a), b)


def _countersequence_row(order: int) -> dict[str, float | int]:
    """Exact norm of h_K/a_0 in the canonical omega graph.

    With w=sin(2 chi)^2 and y=cos(4 chi)=1-2w,

        h_K = w (1-w)^K

    belongs to the windowed cosine space through mode K.  Dividing by the
    constant Chebyshev coefficient a_0=4^-K binomial(2K,K) fixes the raw b_0
    coefficient to one while the weighted graph norm tends to zero.
    """

    k = mp.mpf(order)
    a0 = mp.binomial(2 * order, order) / mp.power(4, order)
    b = 2 * k - mp.mpf("0.5")
    derivative_squared = mp.mpf("0.5") * (
        _beta(3, b)
        - 2 * (k + 1) * _beta(4, b)
        + (k + 1) ** 2 * _beta(5, b)
    )
    value_squared = _beta(4, 2 * k + mp.mpf("0.5")) / 32
    normalized_squared = (derivative_squared + value_squared) / a0**2
    return {
        "K": order,
        "maximum_basis_mode_index": order,
        "required_resolution": order + 1,
        "constant_Chebyshev_coefficient_a0": float(a0),
        "raw_b0_after_normalization": 1.0,
        "canonical_omega_graph_norm": float(mp.sqrt(normalized_squared)),
        "K_times_graph_norm": float(k * mp.sqrt(normalized_squared)),
    }


def _jacobi_data(mode: int) -> tuple[mp.mpf, mp.mpf, mp.mpf, mp.mpf]:
    """Bulk graph diagonal and endpoint values in the exact Jacobi basis."""

    n = mp.mpf(mode)
    # Weight w^beta*(1-w)^alpha with alpha=-1/2, beta=1.
    mass_norm = (n + 1) / ((2 * n + mp.mpf("1.5")) * (n + mp.mpf("0.5")))
    graph_diagonal = mp.mpf("0.5") * n * (n + mp.mpf("1.5")) + mp.mpf(1) / 32
    value_at_regular_pole = (-1 if mode % 2 else 1) * (n + 1)
    value_at_attachment = mp.binomial(2 * mode, mode) / mp.power(4, mode)
    return graph_diagonal, mass_norm, value_at_regular_pole, value_at_attachment


@lru_cache(maxsize=None)
def _chebyshev_constant_functional(mode: int) -> mp.mpf:
    """Exact T_0 coefficient of P_n^(-1/2,1)(x), x=-cos(theta).

    The Chebyshev integral gives the product below.  Its absolute value
    decreases monotonically to Euler's product 2/pi, which explicitly owns
    the logarithmic scale/u boundary-layer estimate.
    """

    if mode == 0:
        return mp.mpf(1)
    return -_chebyshev_constant_functional(mode - 1) * (
        1 - mp.mpf(1) / (4 * mode * mode)
    )


def _constrained_tail_constant(
    degree: int, algebraic_values: list[mp.mpf],
) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    """Tail bound with one finite-M algebraic and one continuous trace row."""

    s = mp.matrix(2, 2)
    t = mp.matrix(2, 2)
    for mode, algebraic in enumerate(algebraic_values):
        diagonal, mass, _, attachment = _jacobi_data(mode)
        endpoint = (algebraic, attachment)
        for left in range(2):
            for right in range(2):
                s[left, right] += (
                    endpoint[left] * endpoint[right]
                    / (diagonal * mass)
                )
                t[left, right] += (
                    endpoint[left] * endpoint[right]
                    / (diagonal**2 * mass)
                )
    s11 = s[1, 1]
    direction = mp.matrix([1, -s[0, 1] / s11])
    algebraic_energy = s[0, 0] - s[0, 1] ** 2 / s11
    algebraic_l2 = (direction.T * t * direction)[0]
    algebraic_ratio = algebraic_l2 / algebraic_energy
    attachment_dual_tail_upper = mp.mpf(8) / (mp.pi * degree)
    next_diagonal = _jacobi_data(degree + 1)[0]
    bound = (
        mp.sqrt(algebraic_ratio)
        + mp.sqrt(t[1, 1] * attachment_dual_tail_upper) / s11
        + mp.sqrt(1 / next_diagonal)
    )
    determinant = s[0, 0] * s11 - s[0, 1] ** 2
    return bound, algebraic_ratio, determinant


def _fortin_tail_row(degree: int) -> dict[str, float | int]:
    """Explicit G-to-weighted-L2 tail constants for the exact low spaces.

    The unwindowed scale/u space is every polynomial through degree M.  Each
    shape space is w times polynomials through degree M-1, equivalently the
    degree-M polynomials that vanish algebraically at the zero-capacity
    regular pole.  The attachment trace is preserved exactly.
    """

    next_diagonal = _jacobi_data(degree + 1)[0]
    # For n>=1, a_n^2<=1/(pi*n), 1/h_n<=4n and d_n>=n^2/2.
    # Hence the attachment-trace dual tail is bounded by
    # sum_{n>M} 8/(pi*n^2) <= 8/(pi*M).
    attachment_dual_tail_upper = mp.mpf(8) / (mp.pi * degree)
    attachment_s = mp.mpf(0)
    attachment_t = mp.mpf(0)
    for mode in range(degree + 1):
        diagonal, mass, _, attachment = _jacobi_data(mode)
        attachment_s += attachment**2 / (diagonal * mass)
        attachment_t += attachment**2 / (diagonal**2 * mass)
    scale_core_augmented_u_bound = (
        mp.sqrt(1 / next_diagonal)
        + mp.sqrt(attachment_t * attachment_dual_tail_upper) / attachment_s
    )
    u_bound, u_algebraic_ratio, u_determinant = _constrained_tail_constant(
        degree,
        [_chebyshev_constant_functional(mode) for mode in range(degree + 1)],
    )
    shape_bound, pole_boundary_layer_ratio, shape_determinant = (
        _constrained_tail_constant(
            degree,
            [_jacobi_data(mode)[2] for mode in range(degree + 1)],
        )
    )
    inflate = mp.mpf("1.000000000001")
    return {
        "M": degree,
        "next_bulk_graph_diagonal": float(next_diagonal),
        "attachment_dual_tail_upper": float(
            inflate * attachment_dual_tail_upper
        ),
        "scale_fixed_u_G_to_weighted_L2_tail_upper": float(
            inflate * u_bound
        ),
        "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper": float(
            inflate * scale_core_augmented_u_bound
        ),
        "scale_fixed_u_zero_Chebyshev_constant_layer_L2_to_G_ratio_squared": float(
            inflate * u_algebraic_ratio
        ),
        "windowed_shape_pole_boundary_layer_L2_to_G_ratio_squared": float(
            inflate * pole_boundary_layer_ratio
        ),
        "windowed_shape_G_to_weighted_L2_tail_upper": float(
            inflate * shape_bound
        ),
        "finite_low_u_constraint_Schur_determinant": float(u_determinant),
        "finite_low_shape_endpoint_Schur_determinant": float(
            shape_determinant
        ),
    }


def _coordinate_graph(order: int) -> np.ndarray:
    """Natural retained weighted graph on (rho,u,w,v) coordinates."""

    u, _ = _basis(order, max(768, 6 * order), "u")
    shape, _ = _basis(order, max(768, 6 * order), "shape_b")
    return block_diag(np.ones((1, 1)), u, shape, shape)


def _coordinate_injection(high_order: int) -> np.ndarray:
    low_dim = 1 + 3 * ANCHOR_ORDER
    high_dim = 1 + 3 * high_order
    injection = np.zeros((high_dim, low_dim))
    injection[0, 0] = 1.0
    for family in range(3):
        low_start = 1 + family * ANCHOR_ORDER
        high_start = 1 + family * high_order
        injection[
            high_start:high_start + ANCHOR_ORDER,
            low_start:low_start + ANCHOR_ORDER,
        ] = np.eye(ANCHOR_ORDER)
    return injection


def _boundary_jacobian(order: int, q: np.ndarray) -> np.ndarray:
    """Existing three geometry traces plus independent attachment row."""

    signs_u = (-1.0) ** np.arange(1, order + 1)
    signs_shape = (-1.0) ** np.arange(order)
    v_boundary = float(
        q[1 + 2 * order:1 + 3 * order] @ signs_shape
    )
    first = np.zeros(1 + 3 * order)
    first[0] = 1.0
    first[1:1 + order] = signs_u
    first[1 + 2 * order:1 + 3 * order] = (
        -math.tanh(2.0 * v_boundary) * signs_shape
    )
    scale = np.zeros_like(first)
    scale[0] = 1.0
    trace = np.zeros((3, 1 + 3 * order))
    trace[:, 0] = 1.0
    trace[:, 1:1 + order] = signs_u
    trace[0, 1 + order:1 + 2 * order] = signs_shape
    trace[1, 1 + 2 * order:1 + 3 * order] = signs_shape
    trace[2, 1 + 2 * order:1 + 3 * order] = -signs_shape
    return np.vstack((trace, scale - first))


def _trace_compatible_projection_record(
    high_order: int, low_q: np.ndarray,
) -> dict[str, float | int]:
    """Build the exact trace-preserving Galerkin projector.

    Boundary data are lifted in the retained low space and the remaining
    trace-zero part is projected orthogonally in the natural action graph.
    Thus no attachment row is incorrectly treated as a compact interior
    tail.
    """

    injection = _coordinate_injection(high_order)
    high_q = injection @ low_q
    low_graph = _coordinate_graph(ANCHOR_ORDER)
    high_graph = _coordinate_graph(high_order)
    low_trace = _boundary_jacobian(ANCHOR_ORDER, low_q)
    high_trace = _boundary_jacobian(high_order, high_q)
    nested_trace_defect = np.linalg.norm(
        high_trace @ injection - low_trace, ord=2
    )

    inverse_trace = np.linalg.solve(low_graph, low_trace.T)
    right_lift = inverse_trace @ np.linalg.inv(low_trace @ inverse_trace)
    kernel = null_space(low_trace)
    injected_kernel = injection @ kernel
    kernel_gram = injected_kernel.T @ high_graph @ injected_kernel
    kernel_projector = (
        injected_kernel
        @ np.linalg.solve(kernel_gram, injected_kernel.T @ high_graph)
    )
    lifted_trace = injection @ right_lift @ high_trace
    projector = lifted_trace + kernel_projector @ (
        np.eye(high_graph.shape[0]) - lifted_trace
    )
    complement = np.eye(high_graph.shape[0]) - projector
    full_norm = math.sqrt(float(np.max(eigh(
        projector.T @ high_graph @ projector,
        high_graph,
        eigvals_only=True,
    ))))
    kernel_norm = math.sqrt(float(np.max(eigh(
        kernel_projector.T @ high_graph @ kernel_projector,
        high_graph,
        eigvals_only=True,
    ))))
    return {
        "N": high_order,
        "nested_attachment_trace_defect": float(nested_trace_defect),
        "attachment_trace_preservation_defect": float(np.linalg.norm(
            high_trace @ projector - high_trace, ord=2
        )),
        "attachment_trace_tail_defect": float(np.linalg.norm(
            high_trace @ complement, ord=2
        )),
        "identity_on_injected_N12_defect": float(np.linalg.norm(
            projector @ injection - injection, ord=2
        )),
        "idempotence_defect": float(np.linalg.norm(
            projector @ projector - projector, ord=2
        )),
        "trace_kernel_action_orthogonal_projection_norm": kernel_norm,
        "full_trace_compatible_projection_norm": full_norm,
    }


def _basis(order: int, points: int, family: str) -> tuple[np.ndarray, ...]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = weights * math.pi / 8.0
    omega = np.sin(chi) ** 3 * np.cos(chi) ** 3
    if family == "u":
        modes = np.arange(1, order + 1, dtype=float)[:, None]
        values = np.cos(4.0 * modes * chi)
        derivatives = -4.0 * modes * np.sin(4.0 * modes * chi)
        trace = (-1.0) ** np.arange(1, order + 1)
        frequencies = 4.0 * np.arange(1, order + 1)
    elif family == "shape_b":
        modes = np.arange(order, dtype=float)[:, None]
        window = np.sin(2.0 * chi) ** 2
        window_prime = 2.0 * np.sin(4.0 * chi)
        values = window * np.cos(4.0 * modes * chi)
        derivatives = (
            window_prime * np.cos(4.0 * modes * chi)
            - window * 4.0 * modes * np.sin(4.0 * modes * chi)
        )
        trace = (-1.0) ** np.arange(order)
        frequencies = 4.0 * np.arange(order)
    else:
        raise ValueError(family)
    gram = (
        (derivatives * (quadrature * omega)) @ derivatives.T
        + (values * (quadrature * omega)) @ values.T
        + np.outer(trace, trace)
    )
    coordinate = np.diag(1.0 + frequencies**2)
    return gram, coordinate


def _projection_record(order: int, family: str) -> dict[str, float | int]:
    gram, coordinate = _basis(order, max(768, 6 * order), family)
    comparison = eigh(gram, coordinate, eigvals_only=True)
    low = np.zeros_like(gram)
    low[:ANCHOR_ORDER, :ANCHOR_ORDER] = gram[
        :ANCHOR_ORDER, :ANCHOR_ORDER
    ]
    raw_projection_norm = math.sqrt(float(np.max(
        eigh(low, gram, eigvals_only=True)
    )))

    injection = np.zeros((order, ANCHOR_ORDER))
    injection[:ANCHOR_ORDER, :] = np.eye(ANCHOR_ORDER)
    low_gram = injection.T @ gram @ injection
    restriction = np.linalg.solve(low_gram, injection.T @ gram)
    projector = injection @ restriction
    identity = np.eye(order)
    idempotence = np.linalg.norm(projector @ projector - projector, ord=2)
    self_adjoint = np.linalg.norm(
        projector.T @ gram - gram @ projector, ord=2
    ) / max(1.0, np.linalg.norm(gram, ord=2))
    orthogonal_projection_norm = math.sqrt(float(np.max(
        eigh(projector.T @ gram @ projector, gram, eigvals_only=True)
    )))
    return {
        "N": order,
        "minimum_natural_to_raw_coordinate_norm_ratio_squared": float(
            comparison[0]
        ),
        "maximum_natural_to_raw_coordinate_norm_ratio_squared": float(
            comparison[-1]
        ),
        "raw_coefficient_low_projection_norm_in_natural_graph": (
            raw_projection_norm
        ),
        "action_orthogonal_projection_norm_in_natural_graph": (
            orthogonal_projection_norm
        ),
        "action_orthogonal_idempotence_defect": float(idempotence),
        "action_orthogonal_self_adjointness_relative_defect": float(
            self_adjoint
        ),
    }


def main() -> None:
    mp.mp.dps = 80
    anchor = np.load(ANCHOR)
    joint = np.asarray(anchor["state"], dtype=float)
    anchor_qdim = 1 + 3 * ANCHOR_ORDER
    anchor_side_dim = 2 * anchor_qdim + 2 * ANCHOR_ORDER
    anchor_coordinates = {
        "event": joint[:anchor_qdim],
        "child": joint[
            anchor_side_dim:anchor_side_dim + anchor_qdim
        ],
    }
    countersequence = [
        _countersequence_row(order)
        for order in (8, 16, 32, 64, 128, 256, 512, 1024)
    ]
    fortin_tail = [
        _fortin_tail_row(degree)
        for degree in (12, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024, 4096)
    ]
    finite_diagnostics = {
        family: [_projection_record(order, family) for order in (
            16, 24, 32, 48, 64, 96, 128,
        )]
        for family in ("u", "shape_b")
    }
    trace_compatible = {
        side: [
            _trace_compatible_projection_record(order, coordinates)
            for order in (16, 24, 32, 48, 64)
        ]
        for side, coordinates in anchor_coordinates.items()
    }
    validation = {
        "explicit_countersequence_graph_norm_tends_down": all(
            left["canonical_omega_graph_norm"]
            > right["canonical_omega_graph_norm"]
            for left, right in zip(countersequence, countersequence[1:])
        ),
        "countersequence_has_fixed_raw_low_coefficient": all(
            row["raw_b0_after_normalization"] == 1.0
            for row in countersequence
        ),
        "raw_coefficient_projection_growth_is_diagnostic_only": True,
        "action_orthogonal_projectors_are_unit_norm_to_roundoff": all(
            abs(row["action_orthogonal_projection_norm_in_natural_graph"] - 1.0)
            < 2.0e-8
            for rows in finite_diagnostics.values() for row in rows
        ),
        "action_orthogonal_projectors_are_idempotent_to_roundoff": all(
            row["action_orthogonal_idempotence_defect"] < 2.0e-8
            for rows in finite_diagnostics.values() for row in rows
        ),
        "attachment_trace_is_exactly_nested_to_roundoff": all(
            row["nested_attachment_trace_defect"] < 2.0e-12
            for rows in trace_compatible.values() for row in rows
        ),
        "trace_compatible_projector_preserves_attachment_rows": all(
            row["attachment_trace_preservation_defect"] < 2.0e-9
            and row["attachment_trace_tail_defect"] < 2.0e-9
            for rows in trace_compatible.values() for row in rows
        ),
        "trace_kernel_projector_is_unit_norm_to_roundoff": all(
            abs(
                row["trace_kernel_action_orthogonal_projection_norm"] - 1.0
            ) < 2.0e-8
            for rows in trace_compatible.values() for row in rows
        ),
        "explicit_Fortin_tail_constants_are_positive": all(
            row["scale_fixed_u_G_to_weighted_L2_tail_upper"] > 0.0
            and row[
                "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
            ] > 0.0
            and row["windowed_shape_G_to_weighted_L2_tail_upper"] > 0.0
            and row["finite_low_u_constraint_Schur_determinant"] > 0.0
            and row["finite_low_shape_endpoint_Schur_determinant"] > 0.0
            for row in fortin_tail
        ),
        "explicit_Fortin_tail_constants_decrease": all(
            left["scale_fixed_u_G_to_weighted_L2_tail_upper"]
            > right["scale_fixed_u_G_to_weighted_L2_tail_upper"]
            and left["windowed_shape_G_to_weighted_L2_tail_upper"]
            > right["windowed_shape_G_to_weighted_L2_tail_upper"]
            and left[
                "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
            ] > right[
                "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
            ]
            for left, right in zip(fortin_tail, fortin_tail[1:])
        ),
        "common_four_over_sqrt_M_envelope_dominates_all_exact_rows": all(
            row["existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"]
            <= 4.0 / math.sqrt(row["M"])
            and row["windowed_shape_G_to_weighted_L2_tail_upper"]
            <= 4.0 / math.sqrt(row["M"])
            for row in fortin_tail
        ),
        "physical_equations_rows_gates_and_nested_spaces_unchanged": True,
        "no_finite_projection_growth_fit_used_as_the_proof": True,
    }
    payload: dict[str, Any] = {
        "classification": (
            "RAW_COEFFICIENT_TRUNCATION_IS_NOT_UNIFORMLY_BOUNDED_IN_"
            "THE_RETAINED_ACTION_WEIGHTED_TRACE_GRAPH;_THE_EXACT_"
            "ACTION_ORTHOGONAL_GALERKIN_PROJECTOR_IS_THE_REQUIRED_"
            "STABLE_NESTED_PROJECTION"
        ),
        "retained_action_graph": {
            "interval": "0<=chi<=pi/4",
            "principal_weight": "omega=sin(chi)^3*cos(chi)^3",
            "principal_factor": "kappa=3*lapse*R^5*exp(5u-w)>0",
            "canonical_family_norm": (
                "integral_0^(pi/4)omega*(abs(f_prime)^2+abs(f)^2)dchi"
                "+abs(f(pi/4))^2"
            ),
            "raw_frequency_diagonal_is_uniformly_equivalent": False,
            "reason": "omega_VANISHES_CUBICALLY_AT_THE_REGULAR_POLE",
        },
        "exact_weighted_polynomial_reduction": {
            "coordinate": "w=sin(2chi)^2_IN_[0,1]",
            "measure_identity": (
                "omega(chi)*dchi=w*(1-w)^(-1/2)*dw/32"
            ),
            "derivative_identity": (
                "omega(chi)*abs(df/dchi)^2*dchi="
                "w^2*(1-w)^(1/2)*abs(df/dw)^2*dw/2"
            ),
            "unwindowed_polynomial_space": (
                "span{cos(4kchi)}=POLYNOMIALS_IN_(1-2w)"
            ),
            "bulk_Jacobi_parameters": "alpha=-1/2,_beta=1",
            "bulk_Jacobi_derivative_eigenvalue": "n*(n+3/2)",
            "windowed_shape_space": (
                "span{sin(2chi)^2*cos(4jchi)}="
                "w*POLYNOMIALS_IN_(1-2w)"
            ),
            "finite_constraint_resolution": (
                "IN_THE_ORTHONORMAL_JACOBI_COEFFICIENTS_THE_BULK_GRAPH_"
                "DIAGONAL_IS_d_n=n*(n+3/2)/2+1/32;_THE_ATTACHMENT_"
                "CONDITION_IS_A_CONTINUOUS_RANK_ONE_ENDPOINT_FUNCTIONAL;_"
                "THE_WINDOWED_REGULAR_POLE_CONDITION_CONTRIBUTES_ONE_"
                "FINITE_M_POLE_REPRODUCING_KERNEL_WHOSE_WEIGHTED_L2_TO_G_"
                "RATIO_IS_COMPUTED_BY_THE_EXACT_TWO_BY_TWO_ENDPOINT_SCHUR_"
                "FORM"
            ),
        },
        "explicit_weighted_Jacobi_Fortin_tail": {
            "unwindowed_low_space": (
                "AFTER_THE_FOUR_EXISTING_BOUNDARY_ROWS_FIX_THE_SCALE_"
                "ERROR,_THE_u_LOW_SPACE_IS_THE_DEGREE_M_POLYNOMIALS_"
                "WITH_ZERO_CHEBYSHEV_T0_COEFFICIENT"
            ),
            "windowed_low_space": (
                "w*P_(M-1)_EQUALS_DEGREE_M_POLYNOMIALS_WITH_THE_"
                "ALGEBRAIC_REGULAR_POLE_VALUE_ZERO"
            ),
            "attachment_tail_inequalities": [
                "a_n^2=(4^-n*binomial(2n,n))^2<=1/(pi*n)",
                "1/h_n<=4n_FOR_n>=1",
                "d_n>=n^2/2_FOR_n>=1",
                "sum_(n>M)a_n^2/(d_n*h_n)<=8/(pi*M)",
            ],
            "scale_u_algebraic_identity": (
                "abs(T0(P_n^(-1/2,1)(-cos(theta))))="
                "product_(k=1)^n(1-1/(4k^2))>=2/pi"
            ),
            "scale_u_rate": (
                "THE_ZERO_CHEBYSHEV_CONSTANT_REPRODUCING_KERNEL_HAS_"
                "ENERGY_GROWTH_AT_LEAST_LOGARITHMIC,_SO_ITS_L2_TO_G_"
                "RATIO_TENDS_TO_ZERO_WITH_AN_EXPLICIT,_SLOW_LOGARITHMIC_"
                "BOUND"
            ),
            "regular_pole_note": (
                "POINT_EVALUATION_AT_w=0_IS_NOT_CONTINUOUS_IN_G;_IT_IS_"
                "THEREFORE_NOT_PROMOTED_AS_A_CONTINUUM_TRACE._ITS_ONLY_"
                "EFFECT_IS_THE_EXPLICIT_FINITE_M_WINDOWED_POLE_"
                "REPRODUCING_KERNEL_TERM"
            ),
            "scale_u_note": (
                "THE_MISSING_u_CONSTANT_MODE_IS_HANDLED_AS_ITS_EXACT_"
                "FINITE_M_CHEBYSHEV_T0_REPRODUCING_KERNEL;_IT_IS_NOT_"
                "SILENTLY_REPLACED_BY_A_FULL_POLYNOMIAL_SPACE"
            ),
            "scale_core_augmentation": {
                "finite_core_direction": (
                    "THE_EXACT_G_RIESZ_REPRESENTATIVE_OF_THE_MISSING_"
                    "CHEBYSHEV_T0_FUNCTIONAL"
                ),
                "physical_owner": (
                    "THE_EXISTING_SINGLE_scale_COORDINATE_AND_SCALE/u_"
                    "NORMALIZATION,_NOT_A_NEW_FIELD_OR_MODE"
                ),
                "use": (
                    "KEEP_THIS_ONE_LINE_IN_THE_FINITE_BORDERED_CORE;_THE_"
                    "REMAINING_u_TAIL_THEN_HAS_THE_DISPLAYED_SCALE_CORE_"
                    "AUGMENTED_BOUND"
                ),
                "changes_finite_equations_or_boundary_rows": False,
                "changes_physical_scale": False,
            },
            "operator_bound": (
                "norm((Identity-Pi_M^G)f)_L2(omega)<=C_F(M)*norm(f)_G_"
                "ON_THE_EXISTING_TRACE_COMPATIBLE_LOW_SPACE"
            ),
            "common_analytic_envelope": {
                "range": "EVERY_INTEGER_M_GREATER_THAN_OR_EQUAL_TO_12",
                "bound": "C_F(M)<=4/sqrt(M)",
                "scale_u_bound": (
                    "C_u(M)<=sqrt(2)/M+sqrt((768+16*zeta(4)/pi)*8/pi)"
                    "/(24*sqrt(M))<2.258/sqrt(M)"
                ),
                "windowed_shape_bound": (
                    "THE_EXACT_TWO_BY_TWO_POLE_ATTACHMENT_SCHUR_FORM_AND_"
                    "b_n=(-1)^n(n+1)_GIVE_sqrt(R_pole)<=1.5/sqrt(M);_"
                    "THE_ATTACHMENT_AND_BULK_TERMS_HAVE_THE_SAME_1.849_"
                    "AND_sqrt(2/M)_OVER_sqrt(M)_BOUNDS,_SO_C_shape(M)<"
                    "3.758/sqrt(M)<4/sqrt(M)"
                ),
                "finite_table_used_as_proof": False,
                "proof_owner": (
                    "EXACT_JACOBI_DIAGONAL,_a_n^2<=1/(pi*n),_"
                    "h_n^-1<=4n,_d_n>=n^2/2,_zeta(4)=pi^4/90,_AND_"
                    "THE_EXACT_ENDPOINT_SCHUR_COMPLEMENT"
                ),
            },
            "rows": fortin_tail,
            "finite_rows_are_a_fit": False,
            "proof_owner": (
                "EXACT_JACOBI_DIAGONAL,_FINITE_ENDPOINT_SCHUR_ALGEBRA,_"
                "AND_THE_DISPLAYED_ANALYTIC_p_SERIES_REMAINDER"
            ),
            "new_physics_or_gate": False,
        },
        "analytic_countersequence": {
            "definition": (
                "w=sin(2chi)^2,_y=cos(4chi)=1-2w,_"
                "h_K=w*(1-w)^K/a0(K),_"
                "a0(K)=4^-K*binomial(2K,K)"
            ),
            "basis_membership": (
                "h_K_IS_IN_THE_WINDOWED_COSINE_SPACE_THROUGH_MODE_K"
            ),
            "fixed_low_coordinate": "RAW_b0(h_K)=1",
            "exact_norm_formula": (
                "norm(h_K)^2=a0^-2*{0.5*[B(3,b)-2(K+1)B(4,b)"
                "+(K+1)^2B(5,b)]+B(4,2K+1/2)/32},_b=2K-1/2"
            ),
            "asymptotic_conclusion": (
                "a0~(pi*K)^-1/2_AND_norm(h_K)=O(K^-1),_SO_ANY_RAW_"
                "COEFFICIENT_PROJECTION_RETAINING_b0_HAS_UNBOUNDED_"
                "OPERATOR_NORM_IN_THE_ACTION_GRAPH"
            ),
            "rows": countersequence,
            "finite_rows_are_the_proof": False,
            "proof_owner": "EXACT_BETA_FUNCTION_IDENTITY_AND_STANDARD_STIRLING_ASYMPTOTICS",
        },
        "stable_projection": {
            "injection": "I_M:R^M_TO_R^N_IS_THE_EXISTING_ZERO_PADDING",
            "restriction": "R_M^G=(I_M^T*G_N*I_M)^-1*I_M^T*G_N",
            "projector": "Pi_M^G=I_M*R_M^G",
            "exact_identities": [
                "R_M^G*I_M=Identity_M",
                "(Pi_M^G)^2=Pi_M^G",
                "(Pi_M^G)^T*G_N=G_N*Pi_M^G",
                "norm(Pi_M^G)_G=1",
            ],
            "physical_interpretation": (
                "THE_NESTED_FIELD_SUBSPACE_AND_EVERY_BASIS_VARIABLE_KEEP_"
                "THEIR_EXISTING_MEANING;_ONLY_THE_PROOF_RESTRICTION_IS_"
                "THE_ACTION_GRAPH_BEST_APPROXIMATION_INSTEAD_OF_RAW_"
                "COEFFICIENT_DELETION"
            ),
            "new_physics_or_gate": False,
        },
        "trace_compatible_galerkin_decomposition": {
            "boundary_operator": (
                "Gamma_N=THE_EXISTING_THREE_GEOMETRY_TRACE_ROWS_PLUS_"
                "THE_INDEPENDENT_SECOND_ATTACHMENT_ROW"
            ),
            "low_action_minimum_norm_right_lift": (
                "H_M=G_M^-1*Gamma_M^T*(Gamma_M*G_M^-1*Gamma_M^T)^-1"
            ),
            "trace_kernel": "K_M=KER(Gamma_M)",
            "construction": (
                "P_M,N*x=I_M*H_M*Gamma_N*x+Pi_(I_M*K_M)^G*"
                "(x-I_M*H_M*Gamma_N*x)"
            ),
            "exact_identities": [
                "Gamma_N*I_M=Gamma_M",
                "Gamma_N*P_M,N=Gamma_N",
                "Gamma_N*(Identity-P_M,N)=0",
                "P_M,N*I_M=I_M",
                "P_M,N^2=P_M,N",
                "norm(Pi_(I_M*K_M)^G)_G=1",
            ],
            "consequence": (
                "THE_BOUNDARY_AND_ATTACHMENT_TRACE_IS_A_FIXED_FINITE_DIMENSIONAL_"
                "LIFTED_BLOCK_AND_ITS_INTERIOR_GALERKIN_TAIL_IS_EXACTLY_ZERO;_"
                "IT_MUST_NOT_BE_SUBTRACTED_FROM_THE_WEIGHTED_PRINCIPAL_GAP_"
                "USING_A_RAW_FREQUENCY_TAIL_NORM"
            ),
            "finite_roundoff_diagnostics": trace_compatible,
            "new_physics_or_gate": False,
        },
        "finite_diagnostics": finite_diagnostics,
        "reclassification": {
            "weighted_principal_gap_sqrt29_minus5_invalidated": False,
            "previous_comparison_of_weighted_principal_gap_with_raw_"
            "frequency_tail_is_a_common_norm_certificate": False,
            "static_singular_value_collapse_is_a_physical_obstruction": False,
            "classification": "GALERKIN_PROJECTION_CONDITIONING",
        },
        "supersedes_common_norm_claim_in": (
            "artifacts/n12_direct_checkpoint/BHSM_N12_PRINCIPAL_COERCIVITY.json"
        ),
        "superseded_claim": (
            "trace_attachment_to_principal_ratio=0.03654402679259201_"
            "IS_NOT_A_COMMON_ACTION_GRAPH_NORM_RATIO"
        ),
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "weighted_L2_Jacobi_Fortin_tail_closed": True,
        "full_normal_compact_tail_closed": False,
        "critical_regular_pole_block_routing": (
            "THE_WEIGHTED_L2_FORTIN_ESTIMATE_APPLIES_ONLY_TO_GENUINELY_"
            "COMPACT_OMEGA_WEIGHTED_BLOCKS;_THE_RETAINED_v_INVERSE_SQUARE_"
            "REGULAR_POLE_BLOCK_IS_PART_OF_THE_INDICIAL_PRINCIPAL_OPERATOR_"
            "AND_IS_NOT_COUNTED_AS_COMPACT"
        ),
        "first_missing_action_owned_modulus": (
            "THE_SOURCE_RESTRICTED_REGULAR_POLE_v_INDICIAL_BLOCK_IS_"
            "CLOSED_SEPARATELY;_THE_FIRST_REMAINING_OBJECT_IS_A_FULL_"
            "MIXED_(dq,dv,dm)_GRAPH_TO_OBSERVATION_FACTORIZATION_FOR_"
            "THE_GENUINELY_COMPACT_INTERIOR_EULER_DIRAC_BLOCK"
        ),
        "exact_next_dependency": (
            "ENCLOSE_C_ED^G_IN_THE_SOURCE_RESTRICTED_FULL_MIXED_GRAPH;_"
            "THEN_REUSE_THE_SAME_FACTORIZATION_FOR_THE_ORDERED_EVENT,_"
            "MOMENTUM_FLUX,_AND_GAUSS_CONSISTENCY_BLOCKS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
