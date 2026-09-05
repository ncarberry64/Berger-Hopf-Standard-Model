"""Adjudicate spatial attachment equivalence across the AE2/AE4 reset seam.

The retained lineage owns more than a bundle-isomorphism class: AE2 selects
an abstract smooth spin--gauge boundary lift and its common reset frame closes
the gauge-vertical one-jet as ``(G_R,dG_R)=(I,0)``.  The local spatial base map
``F_B`` and its differential remain absent.  The current audit asks the
logically prior physical question: whether a representative is required at
all, or whether the action owns a relative spatial-diffeomorphism quotient.
It proves the natural tensorial identities that are available, but does not
promote levelwise covariance to an unowned event--child quotient.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from bhsm.interface.action_extension_global_spin_reset_ae2 import action_definition
from bhsm.interface.ae2_covariant_seam_response import (
    transition_covariant_derivative,
)
from bhsm.interface.ae31_c2_reset_hadamard_transport import (
    reset_hadamard_transport_theorem,
)
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import (
    hybrid_bundle_gluing,
)
from bhsm.interface.aether_boundary_identity_ejection_v15_13 import (
    ejection_gate_payload,
)
from bhsm.interface.aether_hybrid_actualization_persistence_v15_52 import (
    actualization_invariant_tuple,
    hybrid_cycle_contract,
)
from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import (
    boundary_identity_chain_complex,
    oriented_cut_and_event_data,
    reconstruction_seed,
)
from bhsm.interface.master_action.symmetries import rows as master_symmetry_rows


ACTION_VERSION = "BHSM-AE-3.2.3-ATTACHMENT-DIFFEO-QUOTIENT-AUDIT"
CLASSIFICATION = "AE4_EVENT_CHILD_ATTACHMENT_DIFFEO_EQUIVALENCE_AUTHORITY"
STATUS = (
    "ATTACHMENT_REPRESENTATIVE_PHYSICAL_EQUIVALENCE_UNDECIDED_BECAUSE_THE_"
    "RELATIVE_EVENT_CHILD_DIFFEO_QUOTIENT_IS_NOT_ACTION_OWNED"
)
EXACT_MISSING_BASE_DATUM = (
    "ACTION_OWNED_CROSS_COPY_SPATIAL_ATTACHMENT_MORPHISM_"
    "SIGMA_EVENT_TO_SIGMA_CHILD_ABSENT"
)
EXACT_CLOSED_VERTICAL_DATUM = (
    "ACTION_OWNED_COMMON_RESET_FRAME_GAUGE_VERTICAL_ONE_JET_"
    "G_R_EQUALS_I_AND_dG_R_EQUALS_ZERO"
)
EXACT_ATTACHMENT_QUOTIENT_DATUM = (
    "ACTION_OWNED_EVENT_CHILD_RELATIVE_SPATIAL_DIFFEOMORPHISM_"
    "EQUIVALENCE_CONTRACT_ABSENT"
)
# A representative base map remains absent, but this smaller prior datum now
# decides whether such a representative is physical input or gauge choice.
EXACT_MISSING_DATUM = EXACT_ATTACHMENT_QUOTIENT_DATUM


def _square(value: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    return matrix


def _connection(value: Sequence[Sequence[Sequence[complex]]], name: str) -> np.ndarray:
    connection = np.asarray(value, dtype=complex)
    if (
        connection.ndim != 3
        or connection.shape[1] != connection.shape[2]
        or not np.all(np.isfinite(connection))
    ):
        raise ValueError(f"{name} must have finite shape (base, fiber, fiber)")
    return connection


def induced_connection_transport(
    event_connection: Sequence[Sequence[Sequence[complex]]],
    base_tangent: Sequence[Sequence[float]],
    gauge_lift: Sequence[Sequence[complex]],
    gauge_lift_derivative: Sequence[Sequence[Sequence[complex]]],
) -> np.ndarray:
    """Evaluate the conditional repository-convention connection law.

    ``base_tangent[mu,i]=dF_B^mu/dx_event^i``.  The repository convention

    ``dU + (F_B^* A_child) U - U A_event = 0``

    gives ``F_B^* A_child=U A_event U^dagger-dU U^dagger``.  This function is
    a theorem-class evaluator for supplied local one-jet data; it does not
    manufacture the missing retained ``j^1 Fhat_B``.
    """

    event = _connection(event_connection, "event_connection")
    tangent = np.asarray(base_tangent, dtype=float)
    lift = _square(gauge_lift, "gauge_lift")
    derivative = _connection(gauge_lift_derivative, "gauge_lift_derivative")
    dimension, fiber, _ = event.shape
    if tangent.shape != (dimension, dimension):
        raise ValueError("base_tangent must be square with the base dimension")
    if derivative.shape != event.shape or lift.shape != (fiber, fiber):
        raise ValueError("connection, lift, and lift derivative dimensions must match")
    if not np.all(np.isfinite(tangent)):
        raise ValueError("base_tangent must be finite")
    if not np.allclose(lift.conj().T @ lift, np.eye(fiber), atol=1.0e-12, rtol=0.0):
        raise ValueError("gauge_lift must be unitary")
    if np.linalg.matrix_rank(tangent) != dimension:
        raise ValueError("base_tangent must be invertible")

    pullback = np.asarray(
        [lift @ component @ lift.conj().T - d_lift @ lift.conj().T
         for component, d_lift in zip(event, derivative)],
        dtype=complex,
    )
    flattened = pullback.reshape(dimension, fiber * fiber)
    child = np.linalg.solve(tangent.T, flattened)
    return child.reshape(dimension, fiber, fiber)


def connection_pullback_residual(
    event_connection: Sequence[Sequence[Sequence[complex]]],
    child_connection: Sequence[Sequence[Sequence[complex]]],
    base_tangent: Sequence[Sequence[float]],
    gauge_lift: Sequence[Sequence[complex]],
    gauge_lift_derivative: Sequence[Sequence[Sequence[complex]]],
) -> float:
    """Return the norm of the local connection-preserving equation."""

    event = _connection(event_connection, "event_connection")
    child = _connection(child_connection, "child_connection")
    tangent = np.asarray(base_tangent, dtype=float)
    lift = _square(gauge_lift, "gauge_lift")
    derivative = _connection(gauge_lift_derivative, "gauge_lift_derivative")
    if child.shape != event.shape or derivative.shape != event.shape:
        raise ValueError("all connection data must have one shape")
    if tangent.shape != (event.shape[0], event.shape[0]):
        raise ValueError("base_tangent dimension mismatch")
    pulled_child = np.einsum("mi,mab->iab", tangent, child)
    residuals = [
        transition_covariant_derivative(lift, d_lift, a_event, a_child)
        for d_lift, a_event, a_child in zip(derivative, event, pulled_child)
    ]
    return float(np.linalg.norm(np.asarray(residuals)))


def connection_reset_linearization(
    base_tangent: Sequence[Sequence[float]],
    gauge_lift: Sequence[Sequence[complex]],
) -> np.ndarray:
    """Return the conditional derivative with respect to ``A_event``.

    The affine ``-dU U^dagger`` term does not enter this fixed-background
    derivative.  The returned matrix acts on base-major vectorized matrices.
    """

    tangent = np.asarray(base_tangent, dtype=float)
    lift = _square(gauge_lift, "gauge_lift")
    if tangent.ndim != 2 or tangent.shape[0] != tangent.shape[1]:
        raise ValueError("base_tangent must be square")
    if not np.all(np.isfinite(tangent)) or np.linalg.matrix_rank(tangent) != tangent.shape[0]:
        raise ValueError("base_tangent must be finite and invertible")
    if not np.allclose(lift.conj().T @ lift, np.eye(lift.shape[0]), atol=1.0e-12, rtol=0.0):
        raise ValueError("gauge_lift must be unitary")
    base_inverse = np.linalg.inv(tangent.T)
    # NumPy uses row-major flattening.  For that convention
    # vec_row(U A U^dagger)=(U tensor conjugate(U)) vec_row(A).
    adjoint_matrix = np.kron(lift, lift.conj())
    return np.kron(base_inverse, adjoint_matrix)


def weighted_cotangent_momentum_map(
    event_momentum: Sequence[complex],
    reset_derivative: Sequence[Sequence[complex]],
    event_pairing_weight: Sequence[Sequence[complex]],
    child_pairing_weight: Sequence[Sequence[complex]],
) -> np.ndarray:
    """Return the conditional inverse-adjoint momentum transport.

    For ``q_child=L q_event`` and pairings ``p^dagger W dq``, exact canonical
    transport requires ``p_child=W_child^-1 L^-dagger W_event p_event``.
    """

    momentum = np.asarray(event_momentum, dtype=complex)
    derivative = _square(reset_derivative, "reset_derivative")
    event_weight = _square(event_pairing_weight, "event_pairing_weight")
    child_weight = _square(child_pairing_weight, "child_pairing_weight")
    size = derivative.shape[0]
    if (
        momentum.shape != (size,)
        or event_weight.shape != derivative.shape
        or child_weight.shape != derivative.shape
    ):
        raise ValueError("momentum, derivative, and weights must agree")
    inverse_adjoint = np.linalg.inv(derivative).conj().T
    return np.linalg.solve(child_weight, inverse_adjoint @ event_weight @ momentum)


def common_reset_gauge_vertical_one_jet(
    base_dimension: int, fiber_dimension: int
) -> dict[str, Any]:
    """Return the AE2-owned gauge vertical one-jet in its common frame.

    This closes only the gauge-vertical half; it neither supplies ``F_B`` nor
    asserts that the spin lift is constant.
    """

    if not isinstance(base_dimension, int) or base_dimension <= 0:
        raise ValueError("base_dimension must be a positive integer")
    if not isinstance(fiber_dimension, int) or fiber_dimension <= 0:
        raise ValueError("fiber_dimension must be a positive integer")
    ae2 = action_definition()
    if ae2["common_reset_frame"] != (
        "U_R=I_UP_TO_GLOBAL_SPIN_SIGN_AND_GAUGE_FRAME"
    ):
        raise ValueError("AE2 common reset frame is not available")
    return {
        "status": "CLOSED_IN_THE_ACTION_OWNED_AE2_COMMON_RESET_GAUGE_FRAME",
        "object": EXACT_CLOSED_VERTICAL_DATUM,
        "G_R": np.eye(fiber_dimension, dtype=complex),
        "dG_R": np.zeros(
            (base_dimension, fiber_dimension, fiber_dimension), dtype=complex
        ),
        "full_spin_lift_derivative_claimed_zero": False,
        "independent_relative_gauge_parameter": False,
        "frame_covariance": (
            "A_SIMULTANEOUS_COMMON_GAUGE_FRAME_CHANGE_IS_REDUNDANCY_AND_DOES_"
            "NOT_REOPEN_A_RELATIVE_EVENT_CHILD_TRANSITION"
        ),
    }


def one_jet_component_status() -> dict[str, Any]:
    """Classify the base and gauge-vertical halves independently."""

    vertical = common_reset_gauge_vertical_one_jet(3, 2)
    return {
        "A_base_attachment": {
            "status": "OPEN",
            "abstract_trace_identification": "EXISTS_AS_A_BOUNDARY_RELATION",
            "local_spatial_map_F_B": None,
            "local_spatial_differential_DF_B": None,
            "N12_first_hit_map": "F12:R^196_TO_R^57_ON_CAUCHY_STATE_VARIABLES",
            "N12_moving_endpoint_jet": (
                "JACOBI_FIELD_OF_THE_RETAINED_EULER_DIRAC_STATE_FLOW"
            ),
            "implicit_differentiation_for_DF_B": (
                "INAPPLICABLE_BECAUSE_THE_RETAINED_JACOBIAN_HAS_NO_SPATIAL_"
                "BOUNDARY_MAP_AS_ITS_DOMAIN_OR_CODOMAIN"
            ),
            "earliest_missing_primitive": EXACT_MISSING_BASE_DATUM,
            "blocked_by": EXACT_MISSING_BASE_DATUM,
        },
        "B_vertical_gauge_lift": {
            "status": "CLOSED",
            "abstract_AE2_lift": "EXISTS",
            "common_reset_gauge_representative": "G_R=I",
            "common_reset_gauge_derivative": "dG_R=0",
            "full_spin_lift_derivative_claimed_zero": vertical[
                "full_spin_lift_derivative_claimed_zero"
            ],
            "object": EXACT_CLOSED_VERTICAL_DATUM,
        },
    }


def spatial_base_route_audit() -> list[dict[str, Any]]:
    """Test the four permitted constructions in the requested order."""

    return [
        {
            "route": "A_COMMON_AMBIENT_EMBEDDINGS",
            "status": "DOES_NOT_CLOSE",
            "found": (
                "V15_45_NAMES_AN_ORIENTED_TOPOLOGICAL_CUT_ALONG_A_COMMON_"
                "FULL_PREIMAGE_SEAM_INTO_SEPARATE_SIGMA_C_AND_SIGMA_P_COPIES"
            ),
            "missing": (
                "NO_LOCAL_EVENT_AND_CHILD_EMBEDDINGS_INTO_ONE_RETAINED_POST_"
                "EVENT_GEOMETRY_AND_NO_ACTION_OWNED_CROSS_COPY_BLOWDOWN_MAP"
            ),
        },
        {
            "route": "B_RETAINED_FLOW_MAP",
            "status": "DOES_NOT_CLOSE",
            "found": (
                "EULER_DIRAC_FLOW_ON_CAUCHY_STATE_SPACE_BEFORE_THE_EVENT_AND_"
                "POSITIVE_DURATION_CHILD_FLOW_AFTER_RECONSTRUCTION"
            ),
            "missing": (
                "NO_SPATIAL_VECTOR_FIELD_OR_FLOW_CARRYING_SIGMA_EVENT_TO_"
                "SIGMA_CHILD_ACROSS_THE_METRIC_ERASING_RESET"
            ),
        },
        {
            "route": "C_COLLAR_OR_NORMAL_EXPONENTIAL",
            "status": "DOES_NOT_CLOSE",
            "found": (
                "V15_13_DEFINES_A_SCALAR_CLOSEST_POINT_NORMAL_SEPARATION_IN_"
                "A_COMMON_RECONSTRUCTED_CLOCK_SLICE_BEFORE_THE_CUT_LOCUS"
            ),
            "missing": (
                "NO_EVENT_WIDE_NORMAL_EXPONENTIAL_ATTACHMENT_AND_NO_RETAINED_"
                "FIREWALL_METRIC_OR_PROPER_DISTANCE_THROUGH_THE_RESET"
            ),
        },
        {
            "route": "D_IMPLICIT_EVENT_CHILD_CONSTRUCTION",
            "status": "DOES_NOT_CLOSE",
            "found": (
                "N3_AND_N12_IMPLICIT_SYSTEMS_FOR_EVENT_STATE,_CHILD_CAUCHY_"
                "DATA,_BOUNDARY_ROWS,_AND_DISCRETE_INCIDENCE"
            ),
            "missing": (
                "NO_OWNED_SPATIAL_POINT_VARIABLES_x_y_OR_ATTACHMENT_EQUATION_"
                "C(B,x,y)=0_FROM_WHICH_y=F_B(x)_COULD_BE_SOLVED"
            ),
        },
    ]


def spatial_correspondence_nonuniqueness_witness() -> dict[str, Any]:
    """Exhibit two indistinguishable degree-one maps on ``S3 x S3``.

    At the identity, ``id x id`` and ``Ad_a x id`` fix the same point and
    preserve orientation, the product tangent metric, and volume.  Their
    tangent maps differ, so the retained topology and incidence cannot select
    the one-form pullback.
    """

    angle = 0.7
    rotation = np.asarray(
        (
            (np.cos(angle), -np.sin(angle), 0.0),
            (np.sin(angle), np.cos(angle), 0.0),
            (0.0, 0.0, 1.0),
        )
    )
    first = np.eye(6)
    second = np.block(
        [[rotation, np.zeros((3, 3))], [np.zeros((3, 3)), np.eye(3)]]
    )
    metric = np.eye(6)
    return {
        "boundary_model": "SIGMA_EVENT_AND_SIGMA_CHILD_ARE_EACH_S3_TIMES_S3",
        "candidate_0": "IDENTITY_TIMES_IDENTITY",
        "candidate_1": "INNER_AUTOMORPHISM_Ad_a_TIMES_IDENTITY",
        "same_marked_group_identity_point": True,
        "same_degree": 1,
        "same_orientation": bool(
            np.linalg.det(first) > 0.0 and np.linalg.det(second) > 0.0
        ),
        "same_volume_jacobian": bool(
            np.isclose(np.linalg.det(first), np.linalg.det(second))
        ),
        "both_preserve_product_tangent_metric": bool(
            np.allclose(first.T @ metric @ first, metric)
            and np.allclose(second.T @ metric @ second, metric)
        ),
        "D_candidate_0": first,
        "D_candidate_1": second,
        "tangent_maps_distinct": not np.allclose(first, second),
        "connection_components_can_differ": not np.allclose(
            np.linalg.solve(first.T, np.arange(1.0, 7.0)),
            np.linalg.solve(second.T, np.arange(1.0, 7.0)),
        ),
        "interpretation": (
            "TOPOLOGY,_DEGREE,_ORIENTATION,_A_COMMON_MARKED_POINT,_METRIC,_"
            "AND_VOLUME_DO_NOT_SELECT_THE_CROSS_COPY_SPATIAL_CORRESPONDENCE"
        ),
    }


def attachment_symmetry_group() -> dict[str, Any]:
    """Return the maximal *proved* attachment symmetry, not a wished-for one.

    The master action is diffeomorphism covariant level by level, but its own
    ledger marks cross-level covariance unproved.  Changing an attachment is
    a relative event/child relabelling, rather than a common coordinate change
    of a fixed glued domain.  No retained source declares that relative action
    to be gauge or supplies its action on the AE2 trace graph.
    """

    diffeomorphism = next(
        row for row in master_symmetry_rows() if row["symmetry"] == "diffeomorphism"
    )
    return {
        "boundary": "SIGMA_EVENT_AND_SIGMA_CHILD_ARE_EACH_S3_TIMES_S3",
        "levelwise_action_covariance": diffeomorphism,
        "full_Diff_Sigma_admissible": False,
        "why_not_full_Diff": (
            "THE_CURRENT_C2_GERM_USES_A_FIXED_BACKGROUND,_RADIAL_GALERKIN_"
            "DOMAIN,_BERGER_HOPF_STRUCTURE,_AND_FIXED_PROJECTORS;_NO_SOURCE_"
            "PROVES_THAT_ARBITRARY_DIFF_SIGMA_PRESERVES_THESE_DATA"
        ),
        "levelwise_tensorial_candidate": (
            "ORIENTATION_AND_SPIN_STRUCTURE_PRESERVING_DIFFS_ACTING_BY_"
            "SIMULTANEOUS_PULLBACK_ON_METRIC,_CONNECTION,_SPINORS,_GHOSTS,_"
            "HS_FIELDS,_MEASURE,_AND_DOMAIN"
        ),
        "fixed_background_candidate": (
            "THE_STABILIZER_OF_THE_BERGER_HOPF_BACKGROUND,_ORIENTATION,_"
            "MARKED_DATA,_FAMILY_MODE_PROJECTORS,_INCIDENCE,_AND_BOUNDARY_DOMAIN"
        ),
        "product_preserving_candidate": "DIFF(S3)_HOPF_TIMES_DIFF(S3)_HOPF",
        "proved_common_reparametrization_rule": (
            "FOR_A_SUPPLIED_F_B,_PAIRS_(phi_event,phi_child)_WITH_"
            "phi_child_COMPOSE_F_B_EQUALS_F_B_COMPOSE_phi_event_PRESERVE_"
            "THE_SAME_GLUE_BY_COORDINATE_CHANGE"
        ),
        "proved_nontrivial_relative_attachment_group": None,
        "relative_group_action_on_AE2_domain": None,
        "relative_group_action_on_current_C2_Galerkin_domain": None,
        "maximal_proved_attachment_symmetry_group": (
            "ONLY_COMMON_REPARAMETRIZATIONS_OF_AN_ALREADY_SUPPLIED_GLUE;_"
            "NO_GROUP_CURRENTLY_RELATES_DISTINCT_F_B_REPRESENTATIVES"
        ),
        "candidate_Ad_family": (
            "Ad_exp(theta*tau3)_TIMES_ID_PRESERVES_THE_BERGER_HOPF_AXIS,_"
            "ORIENTATION,_PRODUCT_STRUCTURE,_MARKED_IDENTITY,_AND_HAAR_MEASURE"
        ),
        "candidate_Ad_family_is_action_owned_relative_gauge": False,
        "blocked_by": EXACT_ATTACHMENT_QUOTIENT_DATUM,
    }


def attachment_representative_naturality_witness() -> dict[str, Any]:
    """Check the tensorial ``id``/``Ad`` comparison at one local tangent model.

    The calculation transforms fields, metric, and momenta together.  Equal
    scalar values therefore certify standard naturality identities.  They do
    not certify that BHSM quotients the relative event/child transformation.
    """

    angle = 0.7
    rotation = np.asarray(
        (
            (np.cos(angle), -np.sin(angle), 0.0),
            (np.sin(angle), np.cos(angle), 0.0),
            (0.0, 0.0, 1.0),
        )
    )
    tangent = np.block(
        [[rotation, np.zeros((3, 3))], [np.zeros((3, 3)), np.eye(3)]]
    )
    metric = np.diag((1.0, 1.0, 1.7**2, 1.0, 1.0, 0.8**2))
    event_connection = np.asarray((0.3, -0.7, 0.2, 0.5, -0.1, 0.9))
    child_connection = np.linalg.solve(tangent.T, event_connection)

    event_curvature = np.asarray(
        (
            (0.0, 0.2, -0.1, 0.0, 0.3, 0.0),
            (-0.2, 0.0, 0.4, -0.2, 0.0, 0.1),
            (0.1, -0.4, 0.0, 0.25, 0.0, -0.3),
            (0.0, 0.2, -0.25, 0.0, 0.35, 0.0),
            (-0.3, 0.0, 0.0, -0.35, 0.0, 0.15),
            (0.0, -0.1, 0.3, 0.0, -0.15, 0.0),
        )
    )
    child_curvature = tangent @ event_curvature @ tangent.T
    inverse_metric = np.linalg.inv(metric)

    def maxwell_form(curvature: np.ndarray) -> float:
        return float(
            0.5
            * np.einsum(
                "ij,kl,ik,jl->",
                curvature,
                curvature,
                inverse_metric,
                inverse_metric,
            )
        )

    identity_maxwell = maxwell_form(event_curvature)
    adjoint_maxwell = maxwell_form(child_curvature)

    zero = np.zeros_like(tangent)
    configuration_map = tangent
    momentum_map = np.linalg.inv(configuration_map).T
    cotangent_lift = np.block(
        [[configuration_map, zero], [zero, momentum_map]]
    )
    alpha = np.block(
        [[zero, zero], [np.eye(6), zero]]
    )
    omega = alpha - alpha.T

    pauli = (
        np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex),
        np.asarray(((0.0, -1.0j), (1.0j, 0.0)), dtype=complex),
        np.asarray(((1.0, 0.0), (0.0, -1.0)), dtype=complex),
    )
    spin_lift = np.diag(
        (np.exp(-0.5j * angle), np.exp(0.5j * angle))
    )
    covector = np.asarray((0.4, -0.2, 0.7))
    dirac_0 = sum(value * matrix for value, matrix in zip(covector, pauli))
    dirac_a = spin_lift @ dirac_0 @ spin_lift.conj().T

    brst_0 = np.zeros((4, 4), dtype=complex)
    brst_0[0, 1] = 1.0
    brst_0[2, 3] = 2.0
    brst_unitary = np.asarray(
        (
            (np.cos(angle), -np.sin(angle), 0.0, 0.0),
            (np.sin(angle), np.cos(angle), 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        dtype=complex,
    )
    brst_a = brst_unitary @ brst_0 @ brst_unitary.conj().T

    reset_internal = np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex)
    spatial_spin = np.kron(spin_lift, np.eye(6, dtype=complex))
    frozen_reset = np.kron(
        np.eye(2, dtype=complex), np.kron(reset_internal, np.eye(3))
    )

    probe = np.asarray((1.0, -0.5, 0.25, 0.75), dtype=complex)
    transformed_probe = brst_unitary @ probe
    ghost_bilinear_0 = np.vdot(probe, brst_0 @ probe)
    ghost_bilinear_a = np.vdot(transformed_probe, brst_a @ transformed_probe)
    hs_kernel = np.diag((9.0, 9.0, 3.0, 3.0))
    hs_probe = np.asarray((0.2, -0.1, 0.4, 0.3))
    hs_value = float(hs_probe @ hs_kernel @ hs_probe)
    gfhs_0 = identity_maxwell + ghost_bilinear_0.real + hs_value
    gfhs_a = adjoint_maxwell + ghost_bilinear_a.real + hs_value

    return {
        "representatives": ["F_0=id_times_id", "F_a=Ad_a_times_id"],
        "a_family": "a=exp(theta*tau3),_theta=0.7",
        "metric_invariance_residual": float(
            np.linalg.norm(tangent.T @ metric @ tangent - metric)
        ),
        "measure_jacobian_residual": float(abs(np.linalg.det(tangent) - 1.0)),
        "orientation_preserved": bool(np.linalg.det(tangent) > 0.0),
        "connection_pullback_residual": float(
            np.linalg.norm(tangent.T @ child_connection - event_connection)
        ),
        "curvature_pullback_residual": float(
            np.linalg.norm(
                tangent.T @ child_curvature @ tangent - event_curvature
            )
        ),
        "Maxwell_quadratic_values": [identity_maxwell, adjoint_maxwell],
        "Maxwell_quadratic_residual": float(abs(identity_maxwell - adjoint_maxwell)),
        "Maxwell_canonical_alpha_residual": float(
            np.linalg.norm(cotangent_lift.T @ alpha @ cotangent_lift - alpha)
        ),
        "Maxwell_canonical_omega_residual": float(
            np.linalg.norm(cotangent_lift.T @ omega @ cotangent_lift - omega)
        ),
        "fermion_Dirac_unitary_residual": float(
            np.linalg.norm(dirac_a - spin_lift @ dirac_0 @ spin_lift.conj().T)
        ),
        "fermion_Dirac_eigenvalue_residual": float(
            np.linalg.norm(
                np.linalg.eigvalsh(dirac_a) - np.linalg.eigvalsh(dirac_0)
            )
        ),
        "fermion_Dirac_singular_value_residual": float(
            np.linalg.norm(
                np.linalg.svd(dirac_a, compute_uv=False)
                - np.linalg.svd(dirac_0, compute_uv=False)
            )
        ),
        "spatial_spin_lift_commutes_with_U_R_tensor_I3_residual": float(
            np.linalg.norm(spatial_spin @ frozen_reset - frozen_reset @ spatial_spin)
        ),
        "BRST_nilpotency_residuals": [
            float(np.linalg.norm(brst_0 @ brst_0)),
            float(np.linalg.norm(brst_a @ brst_a)),
        ],
        "BRST_rank_invariant": bool(
            np.linalg.matrix_rank(brst_0) == np.linalg.matrix_rank(brst_a)
        ),
        "ghost_bilinear_residual": float(abs(ghost_bilinear_0 - ghost_bilinear_a)),
        "HS_algebraic_value_residual": 0.0,
        "representation_projector_ranks_unchanged": True,
        "combined_tensorial_GFHS_value_residual": float(abs(gfhs_0 - gfhs_a)),
        "event_algebraic_balance_under_relative_attachment": None,
        "Noether_charge_representative_independence": None,
        "scope": (
            "LOCAL_TENSORIAL_NATURALITY_UNDER_SIMULTANEOUS_PULLBACK;_NOT_AN_"
            "ACTION_OWNED_RELATIVE_ATTACHMENT_QUOTIENT"
        ),
    }


def gfhs_naturality() -> dict[str, Any]:
    """Classify levelwise naturality separately from reset equivalence."""

    common = (
        "NATURAL_UNDER_ORIENTATION_SPIN_PRESERVING_DIFFEO_WITH_METRIC,_"
        "MEASURE,_FIELDS,_AND_DOMAIN_TRANSFORMED_TOGETHER"
    )
    return {
        "Maxwell": {
            "tensorial_law": "F(phi^*A)=phi^*F(A)",
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "ghost": {
            "tensorial_law": "M_FP[phi^*B,phi^*A]phi^*c=phi^*(M_FP[B,A]c)",
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "fermion": {
            "tensorial_law": (
                "D_(phi^*B,phi^*A)Lift_phi^spin=Lift_phi^spin D_(B,A)"
            ),
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "HS": {
            "tensorial_law": "K_HS[phi^*B]phi^*H=phi^*(K_HS[B]H)",
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "gauge_fermion": {
            "tensorial_law": "NATURAL_BY_CONNECTION_AND_SPINOR_PULLBACK",
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "fermion_HS": {
            "tensorial_law": "NATURAL_FOR_HS_SCALAR_PULLBACK_AND_SPIN_LIFT",
            "action_density": common,
            "current_C2_relative_reset_test": "NOT_EVALUABLE",
        },
        "combined_germ": {
            "formal_levelwise_identity": (
                "Gamma_GFHS[phi^*B;phi^*Phi]=Gamma_GFHS[B;Phi]"
            ),
            "proved_scope": "COVARIANT_LOCAL_DENSITIES_AND_THE_FINITE_WITNESS",
            "not_proved_scope": (
                "THE_RESET_GLUED_CURRENT_C2_GALERKIN_DOMAIN,_BOUNDARY_"
                "CONDITIONS,_RELATIVE_GRAPH,_AND_INTEGRATED_CROSS_COPY_ACTION"
            ),
            "full_BHSM_reset_natural": None,
        },
    }


def canonical_attachment_quotient() -> dict[str, Any]:
    """State the exact symplectic-reduction condition and missing owner."""

    return {
        "unreduced_phase_space": "TSTAR_Q_BOUNDARY",
        "candidate_group": (
            "G_ATTACHMENT_SUBSET_DIFF(Sigma_event)_TIMES_DIFF(Sigma_child)"
        ),
        "candidate_group_action_owned": False,
        "alpha_invariant_under_cotangent_lift": True,
        "alpha_horizontal_on_full_phase_space": False,
        "horizontality_identity": "i_(xi_TSTAR_Q)alpha=<J,xi>",
        "alpha_basic_on_full_phase_space": False,
        "omega_invariant_under_cotangent_lift": True,
        "omega_descends_conditionally": (
            "ON_J_INVERSE_0_MOD_G_ATTACHMENT_IF_THE_GROUP_ACTION,_MOMENT_"
            "MAP,_CONSTRAINT_SURFACE,_FREE_PROPERNESS,_AND_DOMAIN_PRESERVATION_"
            "ARE_ACTION_OWNED"
        ),
        "BRST_descent_conditionally": (
            "REQUIRES_THE_ATTACHMENT_DIFFEO_GHOST_COMPLEX_AND_ITS_"
            "INTERTWINING_WITH_THE_EXISTING_INTERNAL_GAUGE_BRST_COMPLEX"
        ),
        "constraints_descend": None,
        "quotient_phase_space": None,
        "reduced_reset_map": None,
        "reduced_reset_canonical": None,
        "beta_representative_invariant": None,
        "beta_basic": None,
        "local_reset_generating_germ": None,
        "blocked_by": EXACT_ATTACHMENT_QUOTIENT_DATUM,
    }


def attachment_equivalence_adjudication() -> dict[str, Any]:
    """Answer whether the existing map ambiguity has been proved gauge."""

    return {
        "outcome_A_pure_redundancy": {
            "proved": False,
            "reason": (
                "NO_ACTION_OWNED_RELATIVE_EVENT_CHILD_DIFFEO_GROUP_ACTS_ON_"
                "THE_RESET_DOMAIN_AND_CURRENT_C2_GALERKIN_GERM"
            ),
        },
        "outcome_B_partial_redundancy": {
            "proved": False,
            "candidate_residuals_not_promoted": [
                "RELATIVE_HOPF_HORIZONTAL_FRAME_ANGLE_OR_CONJUGACY_CLASS",
                "MAPPING_CLASS_OR_DISCRETE_ATTACHMENT_SECTOR",
                "SEAM_HOLONOMY_CLASS",
            ],
            "reason": (
                "THE_QUOTIENT_GROUP_MUST_BE_FIXED_BEFORE_ITS_ORBIT_INVARIANTS_"
                "OR_RESIDUAL_MODULI_CAN_BE_COMPUTED"
            ),
        },
        "outcome_C_physical_nonuniqueness": {
            "proved": False,
            "reason": (
                "NO_TWO_ACTION_OWNED_REPRESENTATIVES_HAVE_BEEN_PROPAGATED_"
                "THROUGH_A_COMPLETE_COMMON_RESET_ACTION_AND_DOMAIN"
            ),
        },
        "classification": "A_B_AND_C_REMAIN_UNDECIDED_AT_THE_ACTION_DOMAIN_LEVEL",
        "formal_id_Ad_witness_equivalent_after_simultaneous_pullback": True,
        "formal_witness_sufficient_to_close_physical_equivalence": False,
        "connection_class_unique": None,
        "curvature_class_unique": None,
        "physical_observable_invariance": {
            "local_tensorial_action_value": "VERIFIED_FOR_THE_WITNESS",
            "intrinsic_operator_spectrum": "VERIFIED_UNDER_UNITARY_PULLBACK",
            "gauge_curvature_quadratic_invariant": "VERIFIED_FOR_THE_WITNESS",
            "trace_determinant_invariants": "UNITARY_SIMILARITY_IDENTITY",
            "BRST_complex_rank_and_nilpotency": "VERIFIED_FOR_THE_WITNESS",
            "BRST_cohomology_on_actual_reset_domain": None,
            "fermion_singular_and_eigenvalue_data": "VERIFIED_FOR_THE_WITNESS",
            "projector_ranks": "UNCHANGED_ON_THE_SEPARATE_INTERNAL_FACTOR",
            "Noether_charges": None,
            "integrated_reset_action": None,
            "event_algebraic_balance": None,
        },
        "representative_independence": None,
        "identity_representative_allowed": False,
        "identity_semantics": (
            "NOT_YET_AN_ADMISSIBLE_GAUGE_FIXING_AND_NOT_A_DERIVED_PHYSICAL_MAP"
        ),
        "residual_physical_attachment_datum": None,
        "reset_generator_status": "BLOCKED_BEFORE_REDUCED_BETA_CAN_BE_FORMED",
        "graph_jet_status": "DTHETA_THROUGH_D3THETA_NOT_AVAILABLE",
        "global_S1_S4_status": {
            "S1": "REFERENCE_SLICE_ONLY",
            "S2": "BLOCKED",
            "S3": "BLOCKED",
            "S4": "BLOCKED",
        },
        "full_field_reset_can_proceed_without_new_physical_law": False,
        "exact_next_object": EXACT_ATTACHMENT_QUOTIENT_DATUM,
    }


def spatial_base_attachment_authority() -> dict[str, Any]:
    """State the child ontology and every downstream authority field."""

    event = oriented_cut_and_event_data()
    identities = boundary_identity_chain_complex()
    seed = reconstruction_seed()
    invariants = actualization_invariant_tuple()
    cycle = hybrid_cycle_contract()
    ejection = ejection_gate_payload()
    return {
        "Sigma_event_definition": (
            "AE2_LAST_REGULAR_EVENT_TRACE;_V15_45_SUPPLIES_SEPARATE_S3_"
            "TIMES_S3_BOUNDARY_COPIES_BUT_NO_LOCAL_EVENT_EMBEDDING"
        ),
        "Sigma_child_definition": seed["child_boundary"],
        "child_ontology": (
            "CASE_4_ABSTRACT_POST_CUT_COPY_WITH_STATE_FIELD_INHERITANCE_AND_"
            "DISCRETE_INCIDENCE_BUT_NO_SPATIAL_POINT_CORRESPONDENCE"
        ),
        "event_embedding": None,
        "child_embedding": None,
        "common_ambient_geometry": None,
        "topological_pre_cut_seam": event["common_full_preimage_seam"],
        "oriented_cut": event["oriented_cut"],
        "separate_boundary_identities": seed["boundary_identities"],
        "discrete_incidence": invariants["incidence"],
        "cross_copy_boundary_exchange_selected": identities[
            "boundary_identity_exchange"
        ],
        "flow_if_any": {
            "state_flow": cycle["flow"],
            "spatial_event_child_flow": None,
        },
        "collar_if_any": {
            "available_scalar_coordinate": ejection["coordinate"],
            "domain": ejection["coordinate_domain"],
            "event_wide_attachment_map": None,
        },
        "metric_transport_through_firewall": (
            "metric" not in event["not_transported_as_pregeometric_primitives"]
        ),
        "retained_child_boundary_solvability_relation": (
            "V17_98_STORED_AUTHORITY_ARTIFACT_CLASSIFIES_THE_FIELD_STATE_"
            "BOUNDARY_MAP_AS_CLOSED"
        ),
        "F_B": None,
        "D_F_B": None,
        "LOCAL_EVENT_CHILD_BASE_MAP_DERIVED": False,
        "GLOBAL_EVENT_CHILD_BASE_MAP_DERIVED": False,
        "authority_scope_required": (
            "A_LOCAL_DIFFEOMORPHISM_ON_THE_EVENTUAL_GATE7_RESET_NEIGHBORHOOD_"
            "WOULD_SUFFICE_FOR_LOCAL_CONNECTION_MAXWELL_AND_ACTION_JETS"
        ),
        "global_boundary_diffeomorphism_required_now": False,
        "inverse_D_F_B": None,
        "cotangent_pullback": None,
        "conormal_map": None,
        "induced_boundary_metric_relation": None,
        "volume_area_density_transformation": None,
        "orientation_sign": (
            "CHILD_SIDE_IS_NEGATIVE_x_BUT_RELATIVE_MAP_ORIENTATION_IS_NOT_"
            "EVALUABLE_WITHOUT_F_B"
        ),
        "higher_F_B_jets_required": (
            "AT_LEAST_j1_FOR_CONNECTION_AND_MAXWELL_TRANSPORT;_j2_AND_j3_"
            "DEPEND_ON_THE_EVENTUAL_GEOMETRIC_CONSTRUCTION_AND_RESET_GENERATOR"
        ),
        "connection_reset": None,
        "curvature_naturality": None,
        "Maxwell_cotangent_lift": None,
        "symplecticity": None,
        "BRST_reset": "GAUGE_VERTICAL_IDENTITY_ONLY_BASE_PULLBACK_OPEN",
        "reset_generator": None,
        "global_S1": "REFERENCE_SLICE_ONLY",
        "global_S2": "BLOCKED",
        "global_S3": "BLOCKED",
        "global_S4": "BLOCKED",
        "conceptual_interpretation": (
            "BHSM_SPECIFIES_WHAT_DISCRETE_DATA_AND_RECONSTRUCTED_STATE_THE_"
            "CHILD_INHERITS_BUT_NOT_WHERE_EACH_EVENT_BOUNDARY_POINT_ATTACHES_"
            "TO_THE_CHILD_BOUNDARY"
        ),
        "exact_next_object": EXACT_MISSING_BASE_DATUM,
    }


def ownership_levels() -> dict[str, Any]:
    """Distinguish the three objects requested by the adjudication."""

    bundle = hybrid_bundle_gluing()
    ae2 = action_definition()
    hadamard = reset_hadamard_transport_theorem()
    return {
        "bundle_isomorphism_class": {
            "status": "EXISTS",
            "owner": "V15_53_RETURNED_SM_BUNDLE_CLASS",
            "same_class_returns": bundle["hybrid_bundle_returns_to_same_isomorphism_class"],
            "connection_one_forms_transported": bundle[
                "connection_one_forms_transported_as_pregeometric_primitives"
            ],
        },
        "actual_equivariant_bundle_morphism": {
            "status": "EXISTS_ABSTRACTLY_ON_THE_AE2_BOUNDARY_BUNDLE",
            "owner": "BHSM_AE2_OWNER_AUTHORIZED_ACTION_DOMAIN_EXTENSION",
            "object": ae2["reset_lift"],
            "smooth": "SMOOTH_SPIN_GAUGE_BUNDLE_ISOMORPHISM" in hadamard[
                "why_Hadamard_is_preserved"
            ],
            "principal_bundle_local_representative_evaluable": False,
            "local_gauge_transition_g_B_evaluable_in_common_reset_frame": True,
            "local_gauge_transition_g_B": "I",
            "vertical_first_derivative_dg_B_evaluable_in_common_reset_frame": True,
            "vertical_first_derivative_dg_B": "0",
            "base_map_F_B_evaluable": False,
            "base_tangent_DF_B_evaluable": False,
        },
        "induced_connection_transport": {
            "status": "CONDITIONAL_FORMULA_ONLY_NOT_ACTION_OWNED_EVALUABLE_MAP",
            "repository_convention": "dU+(F_B^*A_child)U-UA_event=0",
            "configuration_map": None,
            "derivative_at_zero": None,
            "two_background_evaluations": [],
            "blocked_by": EXACT_MISSING_DATUM,
        },
    }


def source_lineage_ledger() -> list[dict[str, Any]]:
    """Record the focused lift/transition/base-map search without overclaiming."""

    return [
        {
            "source": "V15_53_HYBRID_STANDARD_MODEL_BUNDLE",
            "found": "BUNDLE_ISOMORPHISM_CLASS_AND_DISCRETE_REPRESENTATION_DATA",
            "not_found": "CONNECTION_ONE_FORM_TRANSPORT",
        },
        {
            "source": "BHSM_AE2_GLOBAL_SPIN_RESET_ACTION",
            "found": "ABSTRACT_ACTUAL_SMOOTH_SPIN_TIMES_G_SM_BOUNDARY_LIFT_U_R",
            "not_found": "LOCAL_F_B_DF_B_g_B_dg_B",
        },
        {
            "source": "AE31_RESET_HADAMARD_TRANSPORT",
            "found": "ASSOCIATED_FERMION_CAR_AND_PRINCIPAL_SYMBOL_TRANSPORT",
            "not_found": "PRINCIPAL_GAUGE_LIFT_REPRESENTATIVE_OR_CONNECTION_PULLBACK",
        },
        {
            "source": "AE2_COVARIANT_SEAM_RESPONSE",
            "found": "GENERIC_EQUATION_dU_PLUS_A_CHILD_U_MINUS_U_A_EVENT",
            "not_found": "RETAINED_EVENT_CHILD_TRANSITION_INPUTS",
        },
        {
            "source": "N12_AE2_COVARIANT_SEAM_ENCLOSURE",
            "found": "PARAMETER_SPACE_RANDOM_FRAME_WITNESS_WITH_NABLA_PHI_U_R_ZERO",
            "not_found": "PHYSICAL_SPACETIME_GAUGE_CONNECTION_RESET",
        },
        {
            "source": "N12_INTRINSIC_FIRST_HIT_AND_MOVING_ENDPOINT_JETS",
            "found": "STATE_SPACE_MAP_F12_R196_TO_R57_AND_EULER_DIRAC_JACOBI_FIELDS",
            "not_found": "SPATIAL_BOUNDARY_MAP_F_B_OR_ITS_TANGENT_MAP_DF_B",
        },
        {
            "source": "V15_15_MATERIAL_SKIN_TRACE",
            "found": "COMMON_PARENT_FRAME_AND_CONTINUOUS_PULLBACK_CONNECTION_FOR_A_MATERIAL_INTERFACE",
            "not_found": "GATE7_FIREWALL_BIRTH_SPATIAL_BASE_ATTACHMENT_MAP",
        },
        {
            "source": "V15_45_RECONSTRUCTION_FIREWALL_ORIENTED_CUT",
            "found": "COMMON_TOPOLOGICAL_SEAM_AND_SEPARATE_SIGMA_C_SIGMA_P_BOUNDARY_COPIES",
            "not_found": "LOCAL_CROSS_COPY_SPATIAL_CORRESPONDENCE_OR_EMBEDDING_JETS",
        },
        {
            "source": "V15_52_HYBRID_ACTUALIZATION",
            "found": "METRIC_ERASING_EVENT_FUNCTOR_AND_DISCRETE_TUPLE_TO_CAUCHY_STATE_RECONSTRUCTION",
            "not_found": "SPATIAL_POINT_TRANSPORT_THROUGH_THE_RESET",
        },
        {
            "source": "V15_13_BOUNDARY_IDENTITY_AND_EJECTION",
            "found": "SCALAR_CLOSEST_POINT_NORMAL_SEPARATION_ON_A_RECONSTRUCTED_CLOCK_SLICE",
            "not_found": "EVENT_WIDE_NORMAL_EXPONENTIAL_MAP_ACROSS_THE_FIREWALL",
        },
        {
            "source": "V17_98_FIREWALL_CORE_CHILD_OWNERSHIP",
            "found": "FIELD_STATE_BOUNDARY_SOLVABILITY_AND_DISCRETE_INCIDENCE",
            "not_found": "SPATIAL_ATTACHMENT_OF_EVENT_POINTS_TO_CHILD_POINTS",
        },
        {
            "source": "V17_84_EVENT_COMPLETE_CHILD_CORRESPONDENCE",
            "found": "BOUNDARY_CANONICAL_RELATION_THEOREM_CLASS",
            "not_found": "NONZERO_GFHS_CONNECTION_TRACE_MAP",
        },
        {
            "source": "V17_85_TERMINAL_CHILD_BOUNDARY_MAP",
            "found": "GEOMETRY_TRACE_AND_GAUGE_CARRIER_ISOMORPHISM_CLASS",
            "not_found": "GAUGE_CONNECTION_ONE_FORM_OR_SEAM_BASE_DIFFERENTIAL",
        },
        {
            "source": "V17_89_EVENT_ATTACHMENT_STATE_INCIDENCE",
            "found": "RANK_TWO_GEOMETRY_ATTACHMENT_COORDINATE_JACOBIAN",
            "not_found": "SPACETIME_BOUNDARY_MAP_DF_B_OR_GAUGE_TRANSITION_dg_B",
        },
        {
            "source": "V15_57_FULL_SOBOLEV_ACTUALIZATION",
            "found": "CONSTANT_ZERO_BACKGROUND_RECONSTRUCTION",
            "not_found": "NONZERO_CONNECTION_TRANSPORT",
        },
        {
            "source": "V17_97_ZERO_BACKGROUND_CALDERON_CLOSURE",
            "found": "ZERO_GFHS_TRACE_MATCH_AT_THE_ORIGIN",
            "not_found": "FULL_NONZERO_FLUCTUATION_GRAPH",
        },
        {
            "source": "AE4_DOMAIN_AND_STRATIFIED_FLUX_ASSEMBLER",
            "found": "DOMAIN_CLASS_AND_BLOCK_CONSUMER",
            "not_found": "RESET_MAP_GENERATOR_OR_BUNDLE_LIFT_ONE_JET",
        },
    ]


def local_one_jet_nonuniqueness_witness() -> dict[str, Any]:
    """Show why a pointwise lift value and incidence do not transport a one-form."""

    event = np.asarray([[[0.0j]]])
    lift = np.asarray([[1.0 + 0.0j]])
    tangent_identity = np.asarray([[1.0]])
    derivative_zero = np.asarray([[[0.0j]]])
    derivative_phase = np.asarray([[[1.0j]]])
    child_zero = induced_connection_transport(
        event, tangent_identity, lift, derivative_zero
    )
    child_phase = induced_connection_transport(
        event, tangent_identity, lift, derivative_phase
    )

    nonzero_event = np.asarray([[[1.0j]]])
    child_identity_base = induced_connection_transport(
        nonzero_event, tangent_identity, lift, derivative_zero
    )
    child_dilated_base = induced_connection_transport(
        nonzero_event, np.asarray([[2.0]]), lift, derivative_zero
    )
    return {
        "same_pointwise_gauge_lift": True,
        "same_bundle_isomorphism_class": True,
        "vertical_derivative_candidate_0": derivative_zero,
        "vertical_derivative_candidate_1": derivative_phase,
        "zero_event_child_candidate_0": child_zero,
        "zero_event_child_candidate_1": child_phase,
        "distinct_children_without_AE2_common_frame_selection": not np.allclose(
            child_zero, child_phase
        ),
        "vertical_ambiguity_applies_without_AE2_common_frame_selection": True,
        "AE2_common_frame_removes_vertical_ambiguity": True,
        "AE2_selected_gauge_lift": np.eye(1, dtype=complex),
        "AE2_selected_gauge_lift_derivative": np.zeros((1, 1, 1), dtype=complex),
        "same_base_incidence_point": True,
        "base_tangent_candidate_0": tangent_identity,
        "base_tangent_candidate_1": np.asarray([[2.0]]),
        "nonzero_event_child_candidate_0": child_identity_base,
        "nonzero_event_child_candidate_1": child_dilated_base,
        "distinct_children_from_missing_base_tangent": not np.allclose(
            child_identity_base, child_dilated_base
        ),
        "interpretation": (
            "THE_AE2_COMMON_FRAME_CLOSES_THE_GAUGE_VERTICAL_HALF,_BUT_A_"
            "COMMON_INCIDENCE_POINT_STILL_DOES_NOT_FIX_DF_B(x0)_AND_THUS_"
            "DOES_NOT_FIX_THE_CHILD_CONNECTION_COMPONENTS"
        ),
    }


def conditional_geometry_checks() -> dict[str, Any]:
    """Verify the conditional law without promoting the witness to BHSM data."""

    root = 1.0 / np.sqrt(2.0)
    lift = root * np.asarray(((1.0, 1.0j), (1.0j, 1.0)), dtype=complex)
    tangent = np.asarray(((2.0, 0.0), (0.0, 0.5)))
    event = np.asarray(
        (
            ((0.0j, 1.0j), (1.0j, 0.0j)),
            ((1.0j, 0.0j), (0.0j, -1.0j)),
        ),
        dtype=complex,
    )
    derivative = np.asarray(
        (
            0.25j * lift,
            -0.5j * lift,
        ),
        dtype=complex,
    )
    child = induced_connection_transport(event, tangent, lift, derivative)
    linearization = connection_reset_linearization(tangent, lift)
    zero_child = induced_connection_transport(
        np.zeros_like(event), np.eye(2), np.eye(2), np.zeros_like(event)
    )
    return {
        "scope": "CONDITIONAL_THEOREM_CLASS_NOT_RETAINED_RESET_DATA",
        "connection_pullback_residual": connection_pullback_residual(
            event, child, tangent, lift, derivative
        ),
        "nonzero_trace_transported": float(np.linalg.norm(child)) > 0.0,
        "affine_term_nonzero": float(np.linalg.norm(derivative)) > 0.0,
        "fixed_background_linearization_shape": list(linearization.shape),
        "reference_identity_zero_field_recovery_residual": float(
            np.linalg.norm(zero_child)
        ),
        "not_an_admissible_BHSM_background_evaluation": True,
    }


def downstream_status() -> dict[str, Any]:
    """Fail closed on every structure depending on the missing one-jet."""

    return {
        "R_A": None,
        "D_R_A_at_zero": None,
        "D_R_A_at_two_admissible_backgrounds": None,
        "affine_transition_term": "ZERO_IN_THE_AE2_COMMON_RESET_GAUGE_FRAME",
        "U1_SU2_SU3_representation_preservation": "CLOSED_FOR_G_R_EQUALS_I",
        "three_family_factor": "I3_UNCHANGED",
        "Maxwell_conormal_cotangent_lift": None,
        "functional_pairing_and_measure_used": None,
        "gauge_symplectic_reset": None,
        "ghost_reset": "GAUGE_VERTICAL_FACTOR_IS_IDENTITY_BUT_BASE_PULLBACK_IS_OPEN",
        "antighost_reset": "GAUGE_VERTICAL_FACTOR_IS_IDENTITY_BUT_BASE_PULLBACK_IS_OPEN",
        "fermion_covariant_derivative_intertwining": (
            "EQUIVALENT_CONDITIONALLY_TO_THE_CONNECTION_PRESERVING_EQUATION;_"
            "NOT_EVALUABLE_FOR_THE_RETAINED_SEAM"
        ),
        "curvature_transport": "CONDITIONAL_FUNCTORIALITY_ONLY",
        "holonomy_transport": "NO_RETAINED_MAPPED_LOOP_AND_LIFT_REPRESENTATIVE",
        "full_boundary_reset_R_B": None,
        "Delta_omega": None,
        "beta": None,
        "S_RESET_GFHS": None,
        "Theta": None,
        "D_Theta": None,
        "D2_Theta": None,
        "D3_Theta": None,
        "S1_global": "REFERENCE_SLICE_ONLY",
        "S2_global": "BLOCKED",
        "S3_global": "BLOCKED",
        "S4_global": "BLOCKED",
        "event_Noether_Hamiltonian_balance": None,
        "HS_normal_Legendre_rank": 0,
        "pi_H": 0.0,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def requested_object_classification() -> dict[str, Any]:
    """Give the per-object authority boundary after the quotient audit."""

    return {
        "F_B": (
            "REPRESENTATIVE_ABSENT_AND_NOT_YET_PROVED_TO_BE_PHYSICAL_DATA_"
            "OR_PURE_GAUGE"
        ),
        "F_B_equivalence_class": "NOT_DEFINED_WITHOUT_G_ATTACHMENT",
        "D_F_B": (
            "REPRESENTATIVE_DIFFERENTIAL_ABSENT;_REDUCED_NEED_UNDECIDED"
        ),
        "U_R": (
            "ABSTRACT_FULL_SPIN_GAUGE_LIFT_EXISTS;_GAUGE_FACTOR_IS_I_IN_"
            "THE_AE2_COMMON_RESET_FRAME"
        ),
        "d_U_R": (
            "GAUGE_FACTOR_dG_R_EQUALS_ZERO_IS_DERIVED;_FULL_SPIN_LIFT_"
            "DIFFERENTIAL_IS_NOT_CLAIMED_OR_NEEDED_FOR_GFHS_CONNECTION_TRANSPORT"
        ),
        "R_A": (
            "CONDITIONAL_FOR_A_REPRESENTATIVE;_CONNECTION_CLASS_NOT_DEFINED_"
            "WITHOUT_THE_ATTACHMENT_QUOTIENT"
        ),
        "cotangent_lift": (
            "FORMALLY_NATURAL_FOR_EACH_REPRESENTATIVE;_REDUCED_LIFT_OPEN"
        ),
        "symplectic_reset": "REDUCED_PHASE_SPACE_AND_RESET_MAP_OPEN",
        "S_RESET_GFHS": "OPEN_BEFORE_REDUCED_BETA_CAN_BE_FORMED",
        "graph_jets": (
            "OPEN_DTheta_THROUGH_D3Theta_NOT_REACHED;_HIGHER_BUNDLE_JET_"
            "DEPENDENCY_CANNOT_BE_FIXED_BEFORE_THE_F_B_CONSTRUCTION_EXISTS"
        ),
        "global_S1_S4": {
            "S1": "REFERENCE_SLICE_ONLY",
            "S2": "BLOCKED",
            "S3": "BLOCKED",
            "S4": "BLOCKED",
        },
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "bundle_isomorphism_class_exists": True,
        "abstract_AE2_equivariant_boundary_lift_exists": True,
        "common_reset_frame_gauge_vertical_one_jet_derived": True,
        "common_reset_frame_G_R_is_identity": True,
        "common_reset_frame_dG_R_is_zero": True,
        "action_owned_local_spatial_base_map_F_B_exists": False,
        "action_owned_local_spatial_base_differential_DF_B_exists": False,
        "levelwise_diffeomorphism_covariance_exists": True,
        "cross_level_diffeomorphism_intertwiner_proved": False,
        "action_owned_relative_event_child_diffeomorphism_group_exists": False,
        "attachment_representative_independence_proved": False,
        "attachment_representative_dependence_proved": False,
        "identity_representative_is_admissible_gauge_fixing": False,
        "connection_class_transport_derived": False,
        "quotient_boundary_phase_space_derived": False,
        "child_spatial_boundary_ontology": (
            "CASE_4_ABSTRACT_COPY_WITH_STATE_INHERITANCE_AND_DISCRETE_INCIDENCE"
        ),
        "common_ambient_embedding_route_closed": False,
        "retained_spatial_flow_route_closed": False,
        "normal_exponential_route_closed": False,
        "implicit_spatial_attachment_route_closed": False,
        "evaluable_principal_bundle_lift_local_one_jet_exists": False,
        "connection_transport_derived": False,
        "cotangent_lift_derived": False,
        "symplectic_reset_derived": False,
        "exact_reset_generating_functional_derived": False,
        "constant_v15_57_reused": False,
        "family_spectrum_rebuilt": False,
        "empirical_coefficients_used": False,
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "FULL_BHSM_COMPLETE": False,
        "exact_missing_datum": EXACT_MISSING_DATUM,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "EXACT_CLOSED_VERTICAL_DATUM",
    "EXACT_ATTACHMENT_QUOTIENT_DATUM",
    "EXACT_MISSING_BASE_DATUM",
    "EXACT_MISSING_DATUM",
    "STATUS",
    "claim_boundary",
    "attachment_equivalence_adjudication",
    "attachment_representative_naturality_witness",
    "attachment_symmetry_group",
    "canonical_attachment_quotient",
    "common_reset_gauge_vertical_one_jet",
    "conditional_geometry_checks",
    "connection_pullback_residual",
    "connection_reset_linearization",
    "downstream_status",
    "gfhs_naturality",
    "induced_connection_transport",
    "local_one_jet_nonuniqueness_witness",
    "one_jet_component_status",
    "ownership_levels",
    "requested_object_classification",
    "spatial_base_attachment_authority",
    "spatial_base_route_audit",
    "spatial_correspondence_nonuniqueness_witness",
    "source_lineage_ledger",
    "weighted_cotangent_momentum_map",
]
