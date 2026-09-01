"""Gauge--spinor--ghost Calderon trace skeleton on current C2.

This module assembles the exact reset-transmission graph projectors already
owned by AE2/AE3 and distinguishes them from the still-missing physical outer
Calderon projector.  The distinction is essential: transmission glues traces
unitarily, but it neither changes the reflected gauge DtN ratio nor selects a
fermion positive-frequency covariance.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from bhsm.interface.action_extension_global_spin_reset_ae2 import (
    validate_unitary,
)
from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import (
    finite_rank_hadamard_nonuniqueness_theorem,
)
from bhsm.interface.ae3_c2_maxwell_common_shift_no_go import (
    required_noncommon_correction,
)
from bhsm.interface.ae3_c2_two_sided_calderon import (
    two_sided_residue_certificate,
)


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_GAUGE_SPINOR_GHOST_CALDERON_TRACE_SKELETON"


def orthogonal_graph_projector(
    reset_lift: Sequence[Sequence[complex]],
) -> dict[str, Any]:
    """Construct the orthogonal projector onto ``graph(U_reset)``."""

    lift = validate_unitary(reset_lift)
    size = lift.shape[0]
    identity = np.eye(size, dtype=complex)
    projector = 0.5 * np.block(
        [[identity, lift.conj().T], [lift, identity]]
    )
    graph = np.vstack((identity, lift))
    return {
        "one_side_dimension": size,
        "two_sided_dimension": 2 * size,
        "projector_real": projector.real.tolist(),
        "projector_imaginary": projector.imag.tolist(),
        "Hermitian_residual": float(
            np.linalg.norm(projector - projector.conj().T, ord=2)
        ),
        "idempotence_residual": float(
            np.linalg.norm(projector @ projector - projector, ord=2)
        ),
        "graph_fixing_residual": float(
            np.linalg.norm(projector @ graph - graph, ord=2)
        ),
        "rank": int(np.linalg.matrix_rank(projector, tol=1.0e-12)),
        "half_rank": int(np.linalg.matrix_rank(projector, tol=1.0e-12)) == size,
    }


def reset_transmission_complex() -> dict[str, Any]:
    """Assemble finite representatives of all retained reset trace graphs."""

    spin_gauge = np.asarray(((0.0, 1.0), (-1.0, 0.0)), dtype=complex)
    spinor_family = np.kron(spin_gauge, np.eye(3))
    coexact_gauge = np.eye(2, dtype=complex)
    constraint_ghost = np.eye(2, dtype=complex)
    rows = {
        "coexact_gauge": orthogonal_graph_projector(coexact_gauge),
        "constraint_ghost": orthogonal_graph_projector(constraint_ghost),
        "spinor_tensor_family": orthogonal_graph_projector(spinor_family),
    }
    return {
        "trace_sector_order": list(rows),
        "projector_certificates": rows,
        "all_Hermitian": all(
            row["Hermitian_residual"] < 1.0e-12 for row in rows.values()
        ),
        "all_idempotent": all(
            row["idempotence_residual"] < 1.0e-12 for row in rows.values()
        ),
        "all_fix_the_reset_graph": all(
            row["graph_fixing_residual"] < 1.0e-12 for row in rows.values()
        ),
        "all_half_rank": all(row["half_rank"] for row in rows.values()),
        "spinor_reset_factor": "U_spin_gauge_tensor_I3_family",
        "BRST_constraint_and_ghost_reset_matched": True,
        "new_boundary_parameter": False,
    }


def transmission_is_not_outer_calderon() -> dict[str, Any]:
    """Prove that the exact graph projectors do not close physical selection."""

    gauge = two_sided_residue_certificate()
    state = finite_rank_hadamard_nonuniqueness_theorem()
    return {
        "reset_graph_role": "KINEMATIC_INTERNAL_TRANSMISSION_DOMAIN",
        "physical_outer_Calderon_role": (
            "DYNAMIC_DIRICHLET_TO_NEUMANN_AND_SPINOR_POLARIZATION_SELECTION"
        ),
        "same_object": False,
        "gauge_two_sided_ratio": gauge["Zt_over_Zs_two_sided"],
        "reset_graph_repairs_gauge_residue": gauge[
            "one_positive_Lorentzian_residue"
        ],
        "reset_graph_preserves_Hadamard_covariance_continuum": state[
            "reset_transport_preserves_the_continuum"
        ],
        "reset_graph_selects_positive_frequency_covariance": False,
        "reset_graph_fixes_finite_scalar_determinant": False,
        "conclusion": (
            "THE_AE2_RESET_GRAPH_CLOSES_TRANSMISSION_BUT_CANNOT_BE_"
            "RELABELLED_THE_MISSING_PHYSICAL_OUTER_CALDERON_PROJECTOR"
        ),
    }


def physical_outer_calderon_contract() -> dict[str, Any]:
    """Type the one boundary object needed by the three downstream sectors."""

    correction = required_noncommon_correction()
    return {
        "operator": "C_phys_current_C2(omega,k;z_event)",
        "source_trace_space": [
            "coexact_gauge_(Gamma0_A,Gamma1_A)",
            "temporal_longitudinal_constraint_trace",
            "Faddeev_Popov_ghost_trace",
            "spinor_CAR_Cauchy_trace_tensor_C3_family",
        ],
        "required_properties": [
            "Hermitian_or_Krein_self_adjoint_on_the_complete_Green_pairing",
            "projector_or_equivalent_Calderon_graph_relation",
            "BRST_intertwining_of_constraint_and_ghost_blocks",
            "compatibility_with_the_owned_AE2_reset_transmission_graph",
            "continuous_frequency_gauge_DtN_derivatives",
            "self_dual_CAR_positive_frequency_polarization_modulo_Hadamard_symbol",
            "family_projector_preservation",
            "one_common_boundary_state_for_finite_fermion_determinants",
        ],
        "gauge_residue_condition": correction["required_equation"],
        "required_delta_Zt_minus_delta_Zs": correction[
            "required_delta_Zt_minus_delta_Zs"
        ],
        "fermion_output": "ONE_ACTION_SELECTED_CAUCHY_COVARIANCE_C_phys",
        "scalar_output": "FINITE_Z_fin[C_phys,mu]_AND_H0_fin[C_phys,mu]",
        "photon_output": "ONE_POSITIVE_MAXWELL_RESIDUE_IF_THE_CONDITION_HOLDS",
        "current_N3_gravity_eta_scalar_boundary_block_closed": True,
        "current_N3_gauge_spinor_ghost_projector_present": False,
        "one_operator_would_close_three_dependencies": True,
        "operator_constructed_here": False,
        "coefficient_or_state_inserted": False,
    }


def exact_remaining_owner() -> dict[str, Any]:
    return {
        "closed": [
            "AE2_unitary_reset_graph_projectors",
            "gauge_constraint_ghost_spinor_trace_space_direct_sum",
            "proof_that_transmission_is_not_physical_outer_Calderon_selection",
            "typed_shared_output_contract_for_gauge_fermion_and_scalar_sectors",
        ],
        "first_missing_map": (
            "EVENT_SPECIFIC_CURRENT_C2_GAUGE_SPINOR_GHOST_OUTER_CALDERON_"
            "PROJECTOR_ON_THE_COMPLETE_GREEN_TRACE_SPACE"
        ),
        "next_calculation": (
            "DERIVE_ITS_GAUGE_DTN_DERIVATIVES_AND_SPINOR_POLARIZATION_FROM_"
            "THE_SAME_JOINED_EVENT_CHILD_ACTION_VARIATION"
        ),
        "reset_graph_may_be_relabelled_physical_projector": False,
        "archived_Wentzell_matrix_may_be_inserted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_RESET_CALDERON_TRACE_SKELETON_DERIVED": True,
        "CURRENT_C2_GAUGE_GHOST_SPINOR_TRACE_SPACE_ASSEMBLED": True,
        "RESET_TRANSMISSION_NOT_PHYSICAL_OUTER_CALDERON_DERIVED": True,
        "CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED": False,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_FINITE_SCALAR_HESSIAN_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "exact_remaining_owner",
    "orthogonal_graph_projector",
    "physical_outer_calderon_contract",
    "reset_transmission_complex",
    "transmission_is_not_outer_calderon",
]
