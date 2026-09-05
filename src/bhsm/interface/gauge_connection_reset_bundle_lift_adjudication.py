"""Adjudicate gauge-connection transport across the AE2/AE4 reset seam.

The retained lineage owns more than a bundle-isomorphism class: AE2 selects
an abstract smooth spin--gauge boundary lift.  It does not, however, expose
the local one-jet of a principal-bundle lift.  Without the base Jacobian and
the vertical derivative of the local gauge transition, a connection one-form
cannot be pushed to the child trace.  This module records the exact ownership
levels and supplies only conditional differential-geometric identities.
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


ACTION_VERSION = "BHSM-AE-3.2.0-GAUGE-RESET-BUNDLE-LIFT-ADJUDICATION"
CLASSIFICATION = "AE4_GAUGE_CONNECTION_RESET_FROM_EVENT_CHILD_BUNDLE_LIFT"
STATUS = (
    "AE2_ABSTRACT_RESET_LIFT_EXISTS_BUT_AE4_CONNECTION_TRANSPORT_"
    "IS_NOT_EVALUABLE_WITHOUT_ITS_LOCAL_ONE_JET"
)
EXACT_MISSING_DATUM = (
    "ACTION_OWNED_EVALUABLE_LOCAL_ONE_JET_J1_FHAT_B_OF_THE_AE2_"
    "EVENT_CHILD_GAUGE_EQUIVARIANT_PRINCIPAL_BUNDLE_LIFT_ABSENT"
)


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
            "local_gauge_transition_g_B_evaluable": False,
            "vertical_first_derivative_dg_B_evaluable": False,
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
        "distinct_children_from_missing_vertical_one_jet": not np.allclose(
            child_zero, child_phase
        ),
        "same_base_incidence_point": True,
        "base_tangent_candidate_0": tangent_identity,
        "base_tangent_candidate_1": np.asarray([[2.0]]),
        "nonzero_event_child_candidate_0": child_identity_base,
        "nonzero_event_child_candidate_1": child_dilated_base,
        "distinct_children_from_missing_base_tangent": not np.allclose(
            child_identity_base, child_dilated_base
        ),
        "interpretation": (
            "THE_POINTWISE_VALUE_g_B(x0)=1_DOES_NOT_FIX_dg_B(x0),_AND_A_"
            "COMMON_INCIDENCE_POINT_DOES_NOT_FIX_DF_B(x0);_BOTH_ARE_PART_"
            "OF_j1_FHAT_B_AND_CHANGE_THE_CHILD_CONNECTION"
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
        "affine_transition_term": None,
        "U1_SU2_SU3_representation_preservation": (
            "CONDITIONAL_ON_g_B_VALUED_IN_RETAINED_G_SM_AND_dg_B_IN_ITS_LIE_ALGEBRA"
        ),
        "three_family_factor": "I3_UNCHANGED",
        "Maxwell_conormal_cotangent_lift": None,
        "functional_pairing_and_measure_used": None,
        "gauge_symplectic_reset": None,
        "ghost_reset": "BRST_INDUCED_BUT_NOT_INSTANTIABLE",
        "antighost_reset": "ADJOINT_INDUCED_BUT_NOT_INSTANTIABLE",
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


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "bundle_isomorphism_class_exists": True,
        "abstract_AE2_equivariant_boundary_lift_exists": True,
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
    "EXACT_MISSING_DATUM",
    "STATUS",
    "claim_boundary",
    "conditional_geometry_checks",
    "connection_pullback_residual",
    "connection_reset_linearization",
    "downstream_status",
    "induced_connection_transport",
    "local_one_jet_nonuniqueness_witness",
    "ownership_levels",
    "source_lineage_ledger",
    "weighted_cotangent_momentum_map",
]
