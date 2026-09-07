"""Test whether the retained AE4 reset induces a GFHS generating function.

The test is deliberately ordered.  A canonical generating function can be
recovered from ``R^* alpha-alpha`` only after the reset map ``R`` is defined
on the action-owned boundary phase space.  The retained sources define the
fermion lift and the zero-background nonfermion match, but do not define the
nonzero gauge-connection trace component of ``R``.  This module records the
maximal reference-slice canonical result and stops at that first missing map.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from bhsm.interface.action_extension_global_spin_reset_ae2 import (
    action_definition,
)
from bhsm.interface.ae31_c2_reset_hadamard_transport import (
    reset_hadamard_transport_theorem,
)
from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    assembly_contract,
)
from bhsm.interface.ae4_future_collapse_relative_boundary_domain import (
    future_collapse_domain_contract,
)
from bhsm.interface.aether_full_sobolev_hybrid_actualization_v15_57 import (
    full_reconstruction_operator,
)
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import (
    hybrid_bundle_gluing,
)
from bhsm.interface.nonfermion_relative_boundary_variation import (
    canonical_boundary_variables,
)


ACTION_VERSION = "BHSM-AE-3.2.0-RESET-GENERATOR-ADJUDICATION"
CLASSIFICATION = "GFHS_AE4_RESET_CANONICAL_GENERATOR_ADJUDICATION"
STATUS = "RESET_MAP_INSUFFICIENTLY_DEFINED_ON_NONZERO_GAUGE_CONNECTION_TRACE"
EXACT_MISSING_DATUM = (
    "ACTION_OWNED_NONZERO_GAUGE_CONNECTION_TRACE_AE4_RESET_MAP_"
    "R_A[B;GAMMA0_A_EVENT]_TO_GAMMA0_A_CHILD"
)


def _square(value: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if (
        result.ndim != 2
        or result.shape[0] != result.shape[1]
        or not np.all(np.isfinite(result))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    return result


def canonical_one_form_matrix(dimension: int) -> np.ndarray:
    """Return ``A`` with ``alpha_z(delta z)=z^dagger A delta z=p^dagger dq``."""

    size = int(dimension)
    if size <= 0:
        raise ValueError("positive canonical dimension required")
    zero = np.zeros((size, size), dtype=complex)
    identity = np.eye(size, dtype=complex)
    return np.block([[zero, zero], [identity, zero]])


def canonical_symplectic_matrix(dimension: int) -> np.ndarray:
    """Return ``omega=A-A^dagger`` in ``(q,p)`` order."""

    alpha = canonical_one_form_matrix(dimension)
    return alpha - alpha.conj().T


def unitary_cotangent_lift(
    trace_lift: Sequence[Sequence[complex]],
) -> np.ndarray:
    """Lift a unitary trace map to ``(q,p) -> (Uq,Up)``."""

    lift = _square(trace_lift, "trace_lift")
    if not np.allclose(
        lift.conj().T @ lift,
        np.eye(lift.shape[0]),
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError("trace_lift must be unitary")
    zero = np.zeros_like(lift)
    return np.block([[lift, zero], [zero, lift]])


def symplectic_pullback_residual(
    reset_derivative: Sequence[Sequence[complex]],
    symplectic_form: Sequence[Sequence[complex]],
) -> float:
    """Return ``||R^dagger omega R-omega||`` for a supplied derivative."""

    reset = _square(reset_derivative, "reset_derivative")
    omega = _square(symplectic_form, "symplectic_form")
    if reset.shape != omega.shape:
        raise ValueError("reset derivative and symplectic form must agree")
    return float(np.linalg.norm(reset.conj().T @ omega @ reset - omega))


def canonical_one_form_pullback_residual(
    reset_derivative: Sequence[Sequence[complex]],
    one_form_matrix: Sequence[Sequence[complex]],
) -> float:
    """Test exact preservation of the canonical one-form by a linear lift."""

    reset = _square(reset_derivative, "reset_derivative")
    alpha = _square(one_form_matrix, "one_form_matrix")
    if reset.shape != alpha.shape:
        raise ValueError("reset derivative and one-form matrix must agree")
    return float(np.linalg.norm(reset.conj().T @ alpha @ reset - alpha))


def boundary_phase_space_contract() -> dict[str, Any]:
    """Separate canonical, BRST, algebraic, and constraint directions."""

    variables = canonical_boundary_variables()
    gauge_omega = canonical_symplectic_matrix(2)
    fermion_normal = 1.0j * np.diag((1.0, -1.0))
    hs_zero = np.zeros((4, 4))
    return {
        "gauge": {
            "kind": "TRUE_CANONICAL_BOUNDARY_PAIR_AFTER_GAUGE_REDUCTION",
            "variables": variables["gauge"],
            "finite_witness_form": gauge_omega,
            "finite_witness_rank": int(np.linalg.matrix_rank(gauge_omega)),
            "must_be_present_in_symplecticity_test": True,
        },
        "ghost_antighost": {
            "kind": "GRADED_FP_CROSS_PAIR_BRST_RELATED_TO_LONGITUDINAL_GAUGE",
            "variables": variables["ghost"],
            "independent_reset_coefficient": False,
            "quotient_rule": (
                "REMOVE_GLOBAL_GAUGE_ZERO_MODES_AND_DESCEND_THE_MATCHED_"
                "LONGITUDINAL_GAUGE_GHOST_COMPLEX"
            ),
        },
        "fermion": {
            "kind": "NONDEGENERATE_DIRAC_GREEN_TRACE_SPACE",
            "finite_witness_form": fermion_normal,
            "finite_witness_rank": int(np.linalg.matrix_rank(fermion_normal)),
            "reset_graph_owner": "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION",
        },
        "HS": {
            "kind": "ALGEBRAIC_PRESYMPLECTIC_NULL_DIRECTION",
            "variables": variables["HS"],
            "finite_witness_form": hs_zero,
            "finite_witness_rank": int(np.linalg.matrix_rank(hs_zero)),
            "forced_canonical_partner_added": False,
        },
        "constraints": {
            "kind": "PRESYMPLECTIC_NULL_UNTIL_CONSTRAINT_BRST_REDUCTION",
            "independent_boundary_phase_coordinates": False,
        },
        "reduced_phase_space": {
            "operation": (
                "QUOTIENT_CONSTRAINT_AND_BRST_NULL_DIRECTIONS;_OMIT_HS_FROM_"
                "THE_SYMPLECTIC_TEST_BUT_RETAIN_HS_AS_AN_ALGEBRAIC_TRACE"
            ),
            "nondegenerate_sectors": ["gauge_transverse", "fermion"],
            "graded_induced_sector": "longitudinal_gauge_ghost",
            "algebraic_trace_outside_symplectic_quotient": "HS",
        },
    }


def source_search_ledger() -> list[dict[str, Any]]:
    """Classify every plausible retained reset-generator source."""

    ae2 = action_definition()
    hadamard = reset_hadamard_transport_theorem()
    old_reset = full_reconstruction_operator()
    bundle = hybrid_bundle_gluing()
    ae4 = future_collapse_domain_contract()
    assembly = assembly_contract()
    return [
        {
            "source": "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION",
            "scope": "FERMION_TRACE_AND_SQUARED_FLUX_PLUS_REFERENCE_BRST_RULE",
            "usable": True,
            "nonzero_gauge_connection_trace_map": False,
            "evidence": ae2["trace_graph"],
        },
        {
            "source": "AE31_RESET_HADAMARD_TRANSPORT",
            "scope": "FERMION_CAR_STATE_CLASS",
            "usable": True,
            "nonzero_gauge_connection_trace_map": False,
            "evidence": hadamard["covariance_map"],
        },
        {
            "source": "V15_57_FULL_SOBOLEV_HYBRID_ACTUALIZATION",
            "scope": "CONSTANT_RECONSTRUCTION_TO_ZERO_SM_BACKGROUND",
            "usable": False,
            "reason": (
                "D_R=0_AND_A_CONSTANT_MAP_CANNOT_PRESERVE_THE_NONZERO_"
                "MAXWELL_BOUNDARY_SYMPLECTIC_FORM"
            ),
            "evidence": old_reset["Frechet_derivative"],
        },
        {
            "source": "V15_53_RETURNED_SM_BUNDLE_CLASS",
            "scope": "DISCRETE_BUNDLE_ISOMORPHISM_CLASS_ONLY",
            "usable": False,
            "reason": "CONNECTION_ONE_FORMS_ARE_EXPLICITLY_NOT_TRANSPORTED",
            "evidence": bundle[
                "connection_one_forms_transported_as_pregeometric_primitives"
            ],
        },
        {
            "source": "V17_97_ZERO_BACKGROUND_CALDERON_CLOSURE",
            "scope": "ORIGIN_OF_GAUGE_FERMION_GHOST_HS_GRAPH_ONLY",
            "usable": False,
            "reason": "FULL_NONZERO_FLUCTUATION_CALDERON_MATRICES_FALSE",
            "evidence": False,
            "evaluation_rule": (
                "REUSE_THE_STATIC_SCOPE_CONTRACT_WITHOUT_RERUNNING_THE_"
                "HISTORICAL_SCALAR_CHILD_SOLVER"
            ),
        },
        {
            "source": "N12_FULL_RESET_ACTION_JACOBIAN",
            "scope": "GEOMETRY_CONSTRAINT_ATTACHMENT_TRACE_AND_MOMENTUM_ROWS",
            "usable": False,
            "reason": (
                "ITS_EVENT_CHILD_STATE_COORDINATES_CONTAIN_NO_GFHS_"
                "CONNECTION_TRACE_OR_MAXWELL_CONORMAL_ARGUMENT"
            ),
            "nonzero_gauge_connection_trace_map": False,
        },
        {
            "source": "AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN",
            "scope": "CAUSAL_DOMAIN_CLASS_AND_RETARDED_CHILD_REDUCTION",
            "usable": False,
            "reason": "DOMAIN_CLASS_DOES_NOT_DEFINE_NONZERO_CONNECTION_TRACE_INCIDENCE",
            "evidence": ae4["reset_graph_role"],
        },
        {
            "source": "AE4_STRATIFIED_EVENT_FLUX_ASSEMBLY",
            "scope": "ASSEMBLER_GIVEN_SECTOR_BLOCKS",
            "usable": False,
            "reason": "CONSUMES_THE_MAP_BLOCKS_AND_DOES_NOT_GENERATE_THEM",
            "evidence": assembly["event_balance"],
        },
        {
            "source": "RETAINED_SEAM_JUNCTION_CORNER_AND_TRANSGRESSION_TERMS",
            "scope": "GEOMETRY_OR_ZERO_INDEPENDENT_FERMION_SEAM_DENSITY",
            "usable": False,
            "reason": "NO_NONFERMION_CONNECTION_TRACE_RESET_FUNCTIONAL_FOUND",
        },
    ]


def actual_reset_map_ledger() -> dict[str, Any]:
    """Report the actual definition status on every GFHS boundary sector."""

    return {
        "geometry_background": {
            "status": "DEFINED",
            "map": "N12_EVENT_CHILD_RESET_RELATION_AND_CURRENT_C2_STATE_BRIDGE",
        },
        "gauge": {
            "status": "MISSING",
            "reference_value": "ZERO_TRACE_TO_ZERO_TRACE",
            "missing_component": EXACT_MISSING_DATUM,
        },
        "ghost": {
            "status": "BRST_INDUCED",
            "dependency": "NONZERO_GAUGE_CONNECTION_TRACE_MAP",
            "instantiable_now": False,
        },
        "antighost": {
            "status": "ADJOINT_INDUCED",
            "dependency": "GHOST_RESET_MAP",
            "instantiable_now": False,
        },
        "fermion": {
            "status": "DEFINED",
            "map": "Gamma0_child=U_R*Gamma0_event",
            "flux_map": "Gamma1_child=-U_R*Gamma1_event",
            "family_factor": "I3",
        },
        "HS": {
            "status": "STRUCTURAL_ZERO",
            "symplectic_momentum": "pi_H=0",
            "nonzero_algebraic_trace_map": "MISSING",
            "reference_value": "ZERO_TRACE_TO_ZERO_TRACE",
        },
        "constraints": {
            "status": "DEFINED",
            "scope": "GEOMETRY_KKT_AND_FORMAL_AE4_RESPONSE_ROWS_GIVEN_BLOCKS",
            "nonzero_GFHS_blocks_available": False,
        },
        "mixed_GFHS": {
            "status": "MISSING",
            "reason": "NO_NONZERO_GAUGE_MAP_FROM_WHICH_TO_DIFFERENTIATE_MIXED_RESET_TERMS",
        },
        "complete_on_reduced_GFHS_boundary_phase_space": False,
        "first_missing_component": EXACT_MISSING_DATUM,
    }


def reference_canonicality_witness() -> dict[str, Any]:
    """Test the maps that are actually defined and reject the constant reset."""

    identity = np.eye(2, dtype=complex)
    gauge_reset = unitary_cotangent_lift(identity)
    gauge_alpha = canonical_one_form_matrix(2)
    gauge_omega = canonical_symplectic_matrix(2)

    fermion_trace_lift = np.asarray(
        ((0.0, 1.0), (1.0, 0.0)), dtype=complex
    )
    fermion_reset = unitary_cotangent_lift(fermion_trace_lift)
    fermion_alpha = canonical_one_form_matrix(2)
    fermion_omega = canonical_symplectic_matrix(2)

    constant_derivative = np.zeros_like(gauge_reset)
    return {
        "zero_field_gauge_identity": {
            "symplectic_residual": symplectic_pullback_residual(
                gauge_reset, gauge_omega
            ),
            "canonical_one_form_residual": canonical_one_form_pullback_residual(
                gauge_reset, gauge_alpha
            ),
            "S_reset_normalized": 0.0,
            "scope": "REFERENCE_SLICE_ONLY",
        },
        "AE2_fermion_cotangent_lift": {
            "symplectic_residual": symplectic_pullback_residual(
                fermion_reset, fermion_omega
            ),
            "canonical_one_form_residual": canonical_one_form_pullback_residual(
                fermion_reset, fermion_alpha
            ),
            "common_orientation_momentum_rule": (
                "p_child_common=-Gamma1_child=U_R*Gamma1_event"
            ),
            "independent_seam_action": 0.0,
        },
        "v15_57_constant_reconstruction": {
            "symplectic_residual": symplectic_pullback_residual(
                constant_derivative, gauge_omega
            ),
            "expected_residual": float(np.linalg.norm(gauge_omega)),
            "may_be_used_as_nonzero_GFHS_reset": False,
        },
    }


def canonicality_adjudication() -> dict[str, Any]:
    """Adjudicate ``R_B^* omega-omega`` without filling missing map entries."""

    witness = reference_canonicality_witness()
    ledger = actual_reset_map_ledger()
    return {
        "sector_residuals": {
            "gauge_zero_field": witness["zero_field_gauge_identity"][
                "symplectic_residual"
            ],
            "gauge_nonzero": None,
            "ghost_nonzero": None,
            "fermion": witness["AE2_fermion_cotangent_lift"][
                "symplectic_residual"
            ],
            "HS": "NOT_IN_REDUCED_SYMPLECTIC_SPACE__RANK_ZERO",
            "mixed": None,
            "history_seam_reset": 0.0,
        },
        "Delta_omega_full": None,
        "full_canonicality_testable": False,
        "reset_is_exact_symplectic": False,
        "reset_is_symplectic_but_nonexact": False,
        "reset_is_proven_nonsymplectic": False,
        "reset_is_incompletely_defined": True,
        "classification": STATUS,
        "first_undefined_map_component": ledger["first_missing_component"],
        "constant_zero_background_map_rejected_as_extension": True,
    }


def exactness_adjudication() -> dict[str, Any]:
    """Test ``beta=R^*alpha-alpha`` only where the retained map exists."""

    witness = reference_canonicality_witness()
    return {
        "beta_zero_field_gauge": 0.0,
        "d_beta_zero_field_gauge": 0.0,
        "S_RESET_GFHS_zero_field_normalization": 0.0,
        "fermion_beta": 0.0,
        "fermion_independent_seam_action": 0.0,
        "beta_nonzero_GFHS": None,
        "d_beta_nonzero_GFHS": None,
        "cohomology_class_nonzero_GFHS": None,
        "domain_simple_connectivity_assumed": False,
        "reference_one_form_residuals": {
            "gauge": witness["zero_field_gauge_identity"][
                "canonical_one_form_residual"
            ],
            "fermion": witness["AE2_fermion_cotangent_lift"][
                "canonical_one_form_residual"
            ],
        },
        "S_RESET_GFHS_derived": False,
        "blocked_before_closedness_test_by": EXACT_MISSING_DATUM,
    }


def brst_reset_compatibility() -> dict[str, Any]:
    return {
        "reference_common_frame_BRST_intertwining_residual": 0.0,
        "ghost_rule": "R_c=BRST_INDUCED_FROM_R_A_ON_LONGITUDINAL_IMAGE",
        "antighost_rule": "R_cbar=ADJOINT_INDUCED_FROM_R_c",
        "independent_ghost_coefficient_added": False,
        "independent_antighost_coefficient_added": False,
        "nonzero_BRST_reset_instantiable": False,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def hs_reset_adjudication() -> dict[str, Any]:
    """Keep the algebraic HS trace without manufacturing a canonical pair."""

    return {
        "normal_Legendre_rank": 0,
        "pi_H": 0.0,
        "independent_HS_symplectic_coordinate": False,
        "bare_HS_boundary_kinetic_term_added": False,
        "action_owned_reset_seam_HS_interaction_found": False,
        "action_owned_canonical_HS_mixed_boundary_coupling_found": False,
        "nonzero_event_child_HS_trace_map_found": False,
        "independent_HS_term_in_S_RESET_GFHS": 0.0,
        "mixed_HS_dependence_of_S_RESET_GFHS": None,
        "HS_graph_derivatives_may_be_declared_structural_zero": False,
        "why_not": (
            "PRESYMPLECTIC_NULLITY_REMOVES_H_FROM_THE_SYMPLECTICITY_TEST_BUT_"
            "DOES_NOT_DEFINE_ITS_NONZERO_ALGEBRAIC_CHILD_TRACE_OR_EXCLUDE_A_"
            "MIXED_RESET_INTERACTION"
        ),
    }


def graph_and_global_derivative_status() -> dict[str, Any]:
    return {
        "generating_equations": None,
        "Theta_GFHS": None,
        "Theta_at_zero": "ZERO_RELATIVE_GRAPH_REFERENCE_ONLY",
        "D_Theta_at_zero": None,
        "D2_Theta_at_zero": None,
        "D3_Theta_at_zero": None,
        "old_Theta0_Theta1_witnesses_uniquely_discriminated": False,
        "S1_global": "REFERENCE_SLICE_ONLY",
        "S2_global": "BLOCKED",
        "S3_global": "BLOCKED",
        "S4_global": "BLOCKED",
        "bulk_GFHS_derivatives_double_counted": False,
        "reset_derivatives_added_without_generator": False,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def event_balance_status() -> dict[str, Any]:
    return {
        "bulk": 0.0,
        "canonical_reset": None,
        "history_seam": 0.0,
        "event_child": None,
        "constraint_BRST": None,
        "total": None,
        "global_residual_evaluable": False,
        "nonclosing_contribution": EXACT_MISSING_DATUM,
        "empirical_repair_added": False,
    }


def child_inheritance_status() -> dict[str, Any]:
    return {
        "geometry": "DEFINED",
        "gauge": "MISSING_NONZERO_TRACE_MAP",
        "ghost": "BRST_INDUCED_BUT_BLOCKED",
        "antighost": "ADJOINT_INDUCED_BUT_BLOCKED",
        "fermion": "DEFINED_AE2_U_R_TENSOR_I3",
        "HS": "ZERO_REFERENCE_ONLY__NONZERO_ALGEBRAIC_TRACE_MAP_MISSING",
        "nine_frozen_family_mode_fibers_rebuilt": False,
        "full_field_child_inheritance_promoted": False,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "reset_classification": "INCOMPLETELY_DEFINED",
        "reference_gauge_and_fermion_maps_exact_symplectic": True,
        "full_GFHS_reset_symplecticity_proved": False,
        "full_GFHS_reset_nonsymplecticity_proved": False,
        "S_RESET_GFHS_derived": False,
        "BACKGROUND_COVARIANT_STRATIFIED_GFHS_OPERATOR_FAMILY_DERIVED": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_BHSM_COMPLETE": False,
        "empirical_inputs_used": False,
        "exact_missing_datum": EXACT_MISSING_DATUM,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "EXACT_MISSING_DATUM",
    "STATUS",
    "actual_reset_map_ledger",
    "boundary_phase_space_contract",
    "brst_reset_compatibility",
    "canonical_one_form_matrix",
    "canonical_one_form_pullback_residual",
    "canonical_symplectic_matrix",
    "canonicality_adjudication",
    "child_inheritance_status",
    "claim_boundary",
    "event_balance_status",
    "exactness_adjudication",
    "graph_and_global_derivative_status",
    "hs_reset_adjudication",
    "reference_canonicality_witness",
    "source_search_ledger",
    "symplectic_pullback_residual",
    "unitary_cotangent_lift",
]
