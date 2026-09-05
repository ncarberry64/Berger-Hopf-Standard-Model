"""Adjudicate the nonfermion reset graph from retained GFHS variation.

The retained Maxwell and FP actions determine boundary Green pairings, but a
Green pairing does not choose one of its maximal-isotropic graphs.  The
coefficient-free EC/HS action is algebraic and has no boundary pairing at all.
This module makes that distinction executable and identifies the first
missing variational datum without promoting a response operator to an action.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np

from bhsm.interface.ae31_c2_gauge_composite_hs_action import (
    intrinsic_higgs_mixing_boundary,
)
from bhsm.interface.ae32_c2_einstein_cartan_lr_action import (
    algebraic_hubbard_stratonovich_block,
)
from bhsm.interface.background_covariant_gfhs_operator_family import (
    radial_maxwell_boundary_coefficient,
)


ACTION_VERSION = "BHSM-AE-3.2.0-NONFERMION-BOUNDARY-VARIATION"
CLASSIFICATION = "RETAINED_GFHS_BULK_BOUNDARY_VARIATION_ADJUDICATION"
STATUS = (
    "RETAINED_GFHS_BULK_VARIATION_DOES_NOT_UNIQUELY_SELECT_"
    "NONFERMION_RELATIVE_BOUNDARY_GRAPH_FIRST_FIELD_JET"
)
EXACT_MISSING_DATUM = (
    "ACTION_OWNED_BRST_COMPATIBLE_MIXED_RESET_BOUNDARY_VARIATION_"
    "D_PhiSM_D_GAMMA0_SQUARED_S_RESET_GFHS[B;0,0]"
)


def _vector(value: Sequence[complex], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 1 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector")
    return result


def _square(value: Sequence[Sequence[complex]], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if (
        result.ndim != 2
        or result.shape[0] != result.shape[1]
        or not np.all(np.isfinite(result))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    return result


def gauge_green_form(
    q_left: Sequence[complex],
    pi_left: Sequence[complex],
    q_right: Sequence[complex],
    pi_right: Sequence[complex],
) -> complex:
    """Maxwell radial Green form on ``(Gamma0 A, Gamma1^A A)``.

    ``Gamma1^A`` is the outward weighted radial Maxwell conormal.  The
    normalization is inherited from the parent radial energy; no DtN table is
    used here.
    """

    ql = _vector(q_left, "q_left")
    pl = _vector(pi_left, "pi_left")
    qr = _vector(q_right, "q_right")
    pr = _vector(pi_right, "pi_right")
    if not (ql.shape == pl.shape == qr.shape == pr.shape):
        raise ValueError("gauge boundary vectors must have equal dimensions")
    return complex(np.vdot(ql, pr) - np.vdot(pl, qr))


def ghost_green_form(
    q_antighost: Sequence[complex],
    pi_antighost: Sequence[complex],
    q_ghost: Sequence[complex],
    pi_ghost: Sequence[complex],
) -> complex:
    """FP cross-Green form for independent ``cbar`` and ``c`` traces."""

    qb = _vector(q_antighost, "q_antighost")
    pb = _vector(pi_antighost, "pi_antighost")
    q = _vector(q_ghost, "q_ghost")
    p = _vector(pi_ghost, "pi_ghost")
    if not (qb.shape == pb.shape == q.shape == p.shape):
        raise ValueError("ghost boundary vectors must have equal dimensions")
    return complex(np.vdot(qb, p) - np.vdot(pb, q))


def hs_green_form(
    q_left: Sequence[complex], q_right: Sequence[complex]
) -> complex:
    """Return the EC/HS boundary form, identically zero at bare level."""

    left = _vector(q_left, "q_left")
    right = _vector(q_right, "q_right")
    if left.shape != right.shape:
        raise ValueError("HS traces must have equal dimensions")
    return 0.0 + 0.0j


def canonical_boundary_variables() -> dict[str, Any]:
    """Record only canonical variables present in the retained actions."""

    ec = algebraic_hubbard_stratonovich_block()
    composite = intrinsic_higgs_mixing_boundary()
    return {
        "gauge": {
            "configuration_trace": "q_A=Gamma0(A_coexact,A_constraint)",
            "canonical_momentum": (
                "pi_A=Gamma1^A(A)=OUTWARD_WEIGHTED_RADIAL_MAXWELL_CONORMAL"
            ),
            "relative_momentum": "Pi_A=pi_A,event+U_A^dagger*pi_A,child",
            "green_form": "<q_A,pi_A'>-<pi_A,q_A'>",
            "source": (
                "src/bhsm/interface/ae3_c2_lorentzian_gauge_ghost_hessian.py"
            ),
        },
        "ghost": {
            "configuration_traces": "q_c=Gamma0(c),q_cbar=Gamma0(cbar)",
            "canonical_momenta": "pi_c=Gamma1_FP(c),pi_cbar=Gamma1_FP^dagger(cbar)",
            "green_form": "<q_cbar,pi_c>-<pi_cbar,q_c>",
            "antighost_independent_value": False,
            "antighost_relation": "Theta_cbar=Theta_c^dagger",
            "source": (
                "constraint_ghost_frequency_block__FP_SYMBOL_IS_DERIVATIVE_"
                "OF_THE_SAME_BRST_GAUGE_FUNCTIONAL"
            ),
        },
        "HS": {
            "configuration_trace": "q_H=Gamma0(H_HS_up,H_HS_down,H_HS_e,H_HS_nu)",
            "canonical_momentum": "pi_H=partial_L_EC_HS/partial(normal_derivative_H)=0",
            "green_form": "0",
            "HS_derivative_kinetic_term_present": ec[
                "HS_derivative_kinetic_term_present"
            ],
            "composite_derivative_kinetic_term_present": composite[
                "auxiliary_derivative_kinetic_term_at_bare_level"
            ],
            "source": (
                "src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py"
            ),
        },
    }


def _retained_radial_matrix(level: int = 2, nodes: int = 9) -> np.ndarray:
    """Assemble the same weighted radial Maxwell form used by the local germ."""

    if level < 2 or nodes < 5:
        raise ValueError("transverse level >=2 and at least five nodes required")
    rho = np.linspace(1.0e-3, math.pi / 2.0, nodes)
    matrix = np.zeros((nodes, nodes), dtype=float)
    for index in range(nodes - 1):
        left, right = rho[index : index + 2]
        width = right - left
        midpoint = 0.5 * (left + right)
        sigma = -0.5 + midpoint / math.pi - math.sin(2.0 * midpoint) / (
            2.0 * math.pi
        )
        weight = 1.0 - 4.0 * sigma**2
        gradient = weight * math.sin(midpoint) / width
        potential = width * weight * level**2 / math.sin(midpoint)
        local = gradient * np.asarray(((1.0, -1.0), (-1.0, 1.0)))
        local += potential * np.asarray(((2.0, 1.0), (1.0, 2.0))) / 6.0
        matrix[index : index + 2, index : index + 2] += local
    return matrix


def radial_maxwell_green_identity_witness() -> dict[str, Any]:
    """Verify discrete integration by parts before radial elimination."""

    matrix = _retained_radial_matrix()
    u = np.asarray((0.2, -0.1, 0.4, 0.3, -0.2, 0.1, 0.5, -0.3, 0.6), dtype=complex)
    v = np.asarray((-0.4, 0.2, 0.1, -0.5, 0.3, 0.7, -0.2, 0.4, 0.1), dtype=complex)
    ku = matrix @ u
    kv = matrix @ v
    interior = slice(1, -1)
    bulk = np.vdot(ku[interior], v[interior]) - np.vdot(
        u[interior], kv[interior]
    )
    q_u = u[[0, -1]]
    q_v = v[[0, -1]]
    pi_u = ku[[0, -1]]
    pi_v = kv[[0, -1]]
    boundary = gauge_green_form(q_u, pi_u, q_v, pi_v)
    return {
        "radial_form_assembled_before_DtN_elimination": True,
        "bulk_green_difference": bulk,
        "boundary_green_form": boundary,
        "green_identity_residual": float(abs(bulk - boundary)),
        "stored_response_table_used": False,
    }


def cayley_lift(theta: Sequence[Sequence[complex]]) -> np.ndarray:
    """Map a Hermitian graph coordinate to its unitary transmission lift."""

    operator = _square(theta, "theta")
    if not np.allclose(operator, operator.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError("theta must be Hermitian")
    identity = np.eye(operator.shape[0], dtype=complex)
    return np.linalg.solve(identity - 1.0j * operator, identity + 1.0j * operator)


def relative_first_variation_residual(
    q_event: Sequence[complex],
    pi_event: Sequence[complex],
    delta_q_event: Sequence[complex],
    theta: Sequence[Sequence[complex]],
) -> float:
    """Cancel the vertical two-sided boundary variation on a supplied graph.

    This verifies a candidate graph; it does not derive that graph.  The child
    trace is transported by the Cayley lift and its momentum by the opposite
    cotangent lift.
    """

    q = _vector(q_event, "q_event")
    pi = _vector(pi_event, "pi_event")
    variation = _vector(delta_q_event, "delta_q_event")
    lift = cayley_lift(theta)
    if not (q.shape == pi.shape == variation.shape == (lift.shape[0],)):
        raise ValueError("relative boundary dimensions must match")
    child_variation = lift @ variation
    child_momentum = -lift @ pi
    value = np.vdot(pi, variation) + np.vdot(child_momentum, child_variation)
    return float(abs(value))


def graph_green_isotropy_residual(
    theta: Sequence[Sequence[complex]],
    q_left: Sequence[complex],
    q_right: Sequence[complex],
) -> float:
    """Green residual on the Robin-coordinate graph ``pi=theta q``."""

    operator = _square(theta, "theta")
    left = _vector(q_left, "q_left")
    right = _vector(q_right, "q_right")
    if left.shape != right.shape or left.size != operator.shape[0]:
        raise ValueError("graph dimensions must match")
    return float(
        abs(gauge_green_form(left, operator @ left, right, operator @ right))
    )


def brst_graph_compatibility_witness() -> dict[str, Any]:
    """Show BRST relates gauge/ghost jets but leaves their common value free."""

    projector = np.diag((1.0, 1.0, 0.0, 0.0))
    gauge_generator = 1.0j * np.diag((1.0, 1.0, 2.0, 2.0))
    trace = np.asarray((0.4, -0.2, 0.3, 0.1), dtype=complex)
    results = []
    for coefficient in (0.0, 1.0):
        jet_a = coefficient * projector
        jet_c = coefficient * projector
        jet_cbar = jet_c.conj().T
        gauge_residual = np.linalg.norm(jet_a @ gauge_generator - gauge_generator @ jet_a)
        graph_residual = np.linalg.norm(jet_c @ trace - jet_a @ trace)
        adjoint_residual = np.linalg.norm(jet_cbar - jet_c.conj().T)
        results.append(
            {
                "coefficient": coefficient,
                "gauge_covariance_residual": float(gauge_residual),
                "BRST_graph_residual": float(graph_residual),
                "antighost_adjoint_residual": float(adjoint_residual),
            }
        )
    return {
        "relation": "D_Theta_c=D_Theta_A_ON_LONGITUDINAL_BRST_IMAGE",
        "antighost_relation": "D_Theta_cbar=(D_Theta_c)^dagger",
        "independent_antighost_jet_required": False,
        "both_nonuniqueness_witnesses_BRST_compatible": all(
            max(
                row["gauge_covariance_residual"],
                row["BRST_graph_residual"],
                row["antighost_adjoint_residual"],
            )
            < 1.0e-12
            for row in results
        ),
        "candidate_results": results,
        "BRST_selects_common_jet_value": False,
        "spurious_physical_gauge_mode_introduced": False,
    }


def hs_boundary_variation_witness() -> dict[str, Any]:
    """Expose the rank-zero HS Legendre map of the retained local action."""

    variables = canonical_boundary_variables()["HS"]
    left = np.asarray((1.0, -0.2, 0.3, 0.4))
    right = np.asarray((-0.1, 0.5, 0.2, -0.3))
    return {
        **variables,
        "boundary_green_form_value": hs_green_form(left, right),
        "normal_Legendre_rank": 0,
        "all_HS_graph_jets_invisible_to_retained_bulk_boundary_variation": True,
        "heat_derived_HS_kinetic_response_used_as_action": False,
        "physical_HS_direction_derived": False,
    }


def variational_selection_witness() -> dict[str, Any]:
    """Test the two old graph jets against every retained boundary criterion."""

    projector = np.diag((1.0, 1.0, 0.0, 0.0))
    generator = 1.0j * np.diag((1.0, 1.0, 2.0, 2.0))
    q = np.asarray((1.0, -0.25, 0.0, 0.0), dtype=complex)
    r = np.asarray((0.2, 0.4, -0.1, 0.3), dtype=complex)
    pi = np.asarray((0.3, -0.1, 0.2, 0.4), dtype=complex)
    dq = np.asarray((-0.2, 0.5, 0.1, -0.3), dtype=complex)
    probe = 0.35
    candidates = []
    for name, jet in (("Theta_0", np.zeros((4, 4))), ("Theta_1", projector)):
        theta_reference = np.zeros((4, 4))
        theta_probe = probe * jet
        hypothetical_potential = float(0.5 * np.real(np.vdot(q, theta_probe @ q)))
        candidates.append(
            {
                "name": name,
                "Theta_at_zero": theta_reference,
                "D_Phi_Theta_at_zero": jet,
                "Hermiticity_residual": float(
                    np.linalg.norm(theta_probe - theta_probe.conj().T)
                ),
                "gauge_centrality_residual": float(
                    np.linalg.norm(theta_probe @ generator - generator @ theta_probe)
                ),
                "projector_preservation_residual": float(
                    np.linalg.norm(theta_probe @ projector - projector @ theta_probe)
                ),
                "graph_green_residual": graph_green_isotropy_residual(
                    theta_probe, q, r
                ),
                "relative_first_variation_residual": relative_first_variation_residual(
                    q, pi, dq, theta_probe
                ),
                "hypothetical_boundary_potential": hypothetical_potential,
            }
        )
    return {
        "candidate_results": candidates,
        "same_zero_field_graph": np.array_equal(
            candidates[0]["Theta_at_zero"], candidates[1]["Theta_at_zero"]
        ),
        "different_first_field_jets": not np.array_equal(
            candidates[0]["D_Phi_Theta_at_zero"],
            candidates[1]["D_Phi_Theta_at_zero"],
        ),
        "all_fixed_field_vertical_variations_cancel": all(
            row["relative_first_variation_residual"] < 1.0e-12
            for row in candidates
        ),
        "both_graphs_maximal_isotropic": all(
            row["graph_green_residual"] < 1.0e-12 for row in candidates
        ),
        "hypothetical_completions_differ": (
            candidates[0]["hypothetical_boundary_potential"]
            != candidates[1]["hypothetical_boundary_potential"]
        ),
        "retained_bulk_variation_selects_unique_jet": False,
        "competing_nonuniqueness_witness_rejected": False,
        "why": (
            "THE_BULK_GREEN_FORM_TESTS_A_SUPPLIED_MAXIMAL_ISOTROPIC_GRAPH_BUT_"
            "DOES_NOT_GENERATE_ITS_HORIZONTAL_FIELD_DERIVATIVE"
        ),
        "exact_missing_variational_datum": EXACT_MISSING_DATUM,
    }


def moving_domain_hessian_witness() -> dict[str, Any]:
    """Show the missing graph jet changes an otherwise consistent Hessian.

    ``S_reset^lambda(phi,q)=lambda*phi*<q,Pq>/2`` is used only as a pair of
    hypothetical completions.  Its trace Hessian is ``Theta_lambda`` and
    direct differentiation gives ``D_phi Theta_lambda=lambda P``.  Both
    completions are internally consistent; neither occurs in the retained
    action.
    """

    projector = np.diag((1.0, 1.0, 0.0, 0.0))
    step = 1.0e-6
    rows = []
    for coefficient in (0.0, 1.0):
        def trace_hessian(field: float) -> np.ndarray:
            return coefficient * field * projector

        direct = (trace_hessian(step) - trace_hessian(-step)) / (2.0 * step)
        analytic = coefficient * projector
        rows.append(
            {
                "coefficient": coefficient,
                "analytic_D_Phi_trace_Hessian": analytic,
                "direct_D_Phi_trace_Hessian": direct,
                "consistency_residual": float(np.linalg.norm(direct - analytic)),
            }
        )
    return {
        "hypothetical_completion_rows": rows,
        "both_moving_domain_Hessians_internally_consistent": all(
            row["consistency_residual"] < 1.0e-12 for row in rows
        ),
        "Hessians_distinct": not np.array_equal(
            rows[0]["analytic_D_Phi_trace_Hessian"],
            rows[1]["analytic_D_Phi_trace_Hessian"],
        ),
        "geometry_nonfermion_boundary_mixed_block": None,
        "nonfermion_nonfermion_boundary_mixed_block": None,
        "retained_action_contains_either_hypothetical_completion": False,
        "second_variation_selects_unique_jet": False,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def two_background_boundary_witness() -> dict[str, Any]:
    """Show genuine bulk background dependence does not select the graph jet."""

    coefficients = [
        float(radial_maxwell_boundary_coefficient(-0.12, 0.08)),
        float(radial_maxwell_boundary_coefficient(0.17, 0.08)),
    ]
    selection = variational_selection_witness()
    return {
        "background_coordinates": [
            {"log_radius": -0.12, "omega": 0.08},
            {"log_radius": 0.17, "omega": 0.08},
        ],
        "radial_Maxwell_boundary_coefficients": coefficients,
        "bulk_background_dependence_nontrivial": coefficients[0] != coefficients[1],
        "both_graph_candidates_admissible_at_both_backgrounds": all(
            row["graph_green_residual"] < 1.0e-12
            for row in selection["candidate_results"]
        ),
        "background_dependence_selects_graph_jet": False,
    }


def higher_graph_jet_dependency() -> dict[str, Any]:
    """Derive the moving-domain jet order needed by global S1--S4."""

    return {
        "rule": (
            "THE_kTH_ACTION_VARIATION_DIFFERENTIATES_THE_BOUNDARY_"
            "ADMISSIBILITY_CONDITION_k_MINUS_1_TIMES"
        ),
        "S1_global": {"required_graph_data": "Theta[B;0]", "available": True},
        "S2_global": {
            "required_graph_data": "D_PhiSM_Theta[B;0]",
            "available": False,
        },
        "S3_global": {
            "required_graph_data": "D_PhiSM_SQUARED_Theta[B;0]",
            "available": False,
        },
        "S4_global": {
            "required_graph_data": "D_PhiSM_CUBED_Theta[B;0]",
            "available": False,
        },
        "first_jet_alone_completes_global_S1_through_S4": False,
        "affine_graph_truncation_action_derived": False,
        "same_missing_owner_generates_all_required_jets": (
            "S_RESET_GFHS_REPEATED_MIXED_BOUNDARY_VARIATIONS"
        ),
    }


def ae4_reset_gluing_status() -> dict[str, Any]:
    return {
        "zero_field_trace_match_reused": True,
        "fermion_AE2_transport_changed": False,
        "nine_frozen_family_mode_fibers_rebuilt": False,
        "retarded_direct_sum_assembler_available": True,
        "nonfermion_first_order_reset_gluing": False,
        "global_stratified_GFHS_family_derived": False,
        "why_not": EXACT_MISSING_DATUM,
    }


def full_field_child_inheritance_status() -> dict[str, Any]:
    return {
        "geometry_child_relation_reused": True,
        "fermion_child_relation_reused": True,
        "family_projectors_reused": True,
        "gauge_child_inheritance_at_zero_field": True,
        "ghost_child_inheritance_at_zero_field": True,
        "HS_child_inheritance_at_zero_field": True,
        "nonzero_first_order_nonfermion_inheritance_unique": False,
        "action_owned_data_only": True,
        "blocked_by": EXACT_MISSING_DATUM,
    }


def event_balance_decomposition() -> dict[str, Any]:
    return {
        "bulk": {
            "residual": 0.0,
            "scope": "LOCAL_GFHS_EULER_LAGRANGE_AND_AE4_ALGEBRAIC_IDENTITY",
        },
        "boundary_reset": {
            "residual": None,
            "scope": "D_PhiSM_THETA_CONTRIBUTION_NOT_ACTION_OWNED",
        },
        "history_seam": {
            "residual": 0.0,
            "scope": "RETAINED_FERMION_SEAM_DENSITY_ZERO_ON_OWNED_AE2_GRAPH",
        },
        "event_child": {
            "residual": None,
            "scope": "NONFERMION_FIRST_ORDER_CHILD_DOMAIN_NOT_UNIQUE",
        },
        "total": None,
        "physical_event_balance_evaluable": False,
        "empirical_counterterm_inserted": False,
        "exact_owning_term": EXACT_MISSING_DATUM,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "retained_bulk_variation_uniquely_determines_D_PhiSM_Theta": False,
        "gauge_boundary_green_form_derived": True,
        "ghost_boundary_green_form_derived": True,
        "HS_boundary_green_form_identically_zero": True,
        "BRST_relations_between_graph_jets_derived": True,
        "BRST_selects_common_graph_jet_value": False,
        "global_stratified_GFHS_operator_family_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_BHSM_COMPLETE": False,
        "empirical_inputs_used": False,
        "exact_missing_variational_datum": EXACT_MISSING_DATUM,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "EXACT_MISSING_DATUM",
    "STATUS",
    "ae4_reset_gluing_status",
    "brst_graph_compatibility_witness",
    "canonical_boundary_variables",
    "cayley_lift",
    "claim_boundary",
    "event_balance_decomposition",
    "full_field_child_inheritance_status",
    "gauge_green_form",
    "ghost_green_form",
    "graph_green_isotropy_residual",
    "higher_graph_jet_dependency",
    "hs_boundary_variation_witness",
    "hs_green_form",
    "moving_domain_hessian_witness",
    "radial_maxwell_green_identity_witness",
    "relative_first_variation_residual",
    "two_background_boundary_witness",
    "variational_selection_witness",
]
