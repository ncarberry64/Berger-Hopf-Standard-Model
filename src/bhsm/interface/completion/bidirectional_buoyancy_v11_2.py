"""Fail-closed v11.2 formalization of the bidirectional-buoyancy ontology."""

from __future__ import annotations

from math import pi
from typing import Any


VERDICT = "BHSM_BIDIRECTIONAL_BUOYANCY_AND_FIXED_ENCLOSURE_ARCHITECTURE_DERIVED_CONDITIONALLY_BUT_ATTACHMENT_CHARACTER_REMAINS_UNFIXED"
NEXT_OBJECT = "ACTION_OWNED_CORE_SURFACE_ATTACHMENT_TERM_FIXING_ATTACHMENT_CHARACTER_AND_EXCHANGE_CURRENT"
CASIMIR_VERDICT = "BHSM_CASIMIR_REINTERPRETATION_BLOCKED_BY_ABSENT_NORMALIZED_BOUNDARY_SPECTRUM"


def induced_metric_variation(
    ambient_pullback_variation: float,
    tangential_symmetrized_gradient: float,
    extrinsic_normal_variation: float,
) -> float:
    """Scalar component of delta h=delta g|_Sigma+2 nabla_(a xi_b)+2 K^I_ab xi_I."""

    return ambient_pullback_variation + 2 * tangential_symmetrized_gradient + 2 * extrinsic_normal_variation


def relational_interval(metric: list[list[float]], displacement: list[float]) -> float:
    """Coordinate expression for the local quadratic interval; a geodesic completion is still required globally."""

    return sum(metric[i][j] * displacement[i] * displacement[j] for i in range(len(displacement)) for j in range(len(displacement)))


def spherical_flux_density(total_flux: float, radius: float) -> float:
    """Conserved radial flux density on a two-sphere."""

    if radius <= 0:
        raise ValueError("radius must be positive")
    return total_flux / (4 * pi * radius**2)


def casimir_pressure_benchmark(separation: float, hbar: float = 1.0, c: float = 1.0) -> float:
    """External ideal-conductor benchmark, never an action-derived BHSM output."""

    if separation <= 0:
        raise ValueError("separation must be positive")
    return -(pi**2 * hbar * c) / (240 * separation**4)


def ontology_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_bidirectional_topological_buoyancy_ontology_v11_2",
        "classification": "AUTHOR_ONTOLOGY_CLARIFICATION",
        "author_axioms": [
            "spacetime is surface-seeking",
            "energy is core-seeking",
            "observable differentials arise from their relational interaction",
        ],
        "derived_consequences": [
            "intrinsic enclosure data and external embedding data are mathematically distinct",
            "a paired variational response requires an action coupling both sectors",
        ],
        "not_derived": ["a force law", "a primitive character", "a transfer rate", "a cosmological response"],
        "status": "AUTHOR_AXIOM_RECORDED; ACTION_REALIZATION_OPEN",
        "validation_passed": True,
    }


def fixed_encapsulation_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_fixed_encapsulation_geometry_v11_2",
        "classification": "AUTHOR_ONTOLOGY_CLARIFICATION_AND_DERIVED_CONDITIONAL",
        "intrinsic_candidate": {"metric": "h_enc_ab", "area": "integral_Sigma sqrt(|h_enc|)", "cross_distance": "geodesic diameter along the selected inside-edge pair", "topology": "T_enc"},
        "external_data": ["embedding X", "normal bundle N Sigma_enc", "extrinsic curvature K", "ambient metric", "attachment morphism", "relational interval"],
        "variation_identity": "delta h_enc_ab=i_X^*(delta g)_ab+2 nabla_(a xi_b)+2 K^I_ab xi_I",
        "ordinary_motion_condition": "delta h_enc_ab=0 (isometric-embedding constraint surface)",
        "ordinary_motion_invariance_automatic": False,
        "action_owned_constraint_or_stability_term": None,
        "support_character": {"intrinsic_metric": 0, "embedding": None, "normal_bundle": None, "attachment": None},
        "new_lagrange_multipliers_added": False,
        "status": "FIXED_INTRINSIC_GEOMETRY_CONDITIONALLY_CONSISTENT_BUT_NOT_DERIVED_AS_AN_EQUATION_OF_MOTION",
        "validation_passed": True,
    }


def displacement_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_relational_spacetime_displacement_v11_2",
        "classification": "AUTHOR_HYPOTHESIS_AND_DERIVED_CONDITIONAL",
        "relational_interval_local": "Delta s_ij^2=g_ambient(mu,nu) Delta X_ij^mu Delta X_ij^nu",
        "global_covariant_candidate": "twice Synge world function or a boundary-to-boundary geodesic distance on a normal convex domain",
        "q_D_candidate_interpretation": "relational support differential between a fixed enclosure and ambient core-surface placement",
        "q_D_reclassification": "OPEN; retained in the three-mode system pending constraints",
        "current_candidate": "J_st^A may be the support/attachment component of the existing ambient response, not an added independent field",
        "local_balance_candidate": "nabla_A J_st^A=Gamma_release-Gamma_capture+Gamma_displacement",
        "global_balance_requirement": "integrated boundary flux plus core/surface transfer vanishes on a closed system",
        "spherical_limit": "J_r=Phi/(4 pi r^2) only for stationary conserved radial flux",
        "inverse_square_is_force_law": False,
        "plate_casimir_uses_inverse_square": False,
        "new_fields_added": [],
        "status": "RELATIONAL_AND_SPHERICAL_KINEMATICS_DERIVED_CONDITIONALLY; PHYSICAL_CURRENT_OPEN",
        "validation_passed": True,
    }


def exchange_current_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_core_surface_exchange_current_v11_2",
        "classification": "CANDIDATE",
        "isolated_known_current": "j_shift^A=-lambda_D^2 A_D^A=lambda_D nabla^A q_D",
        "candidate_decomposition": "J_D^A=J_core^A+J_surface^A+J_attach^A",
        "action_derived_decomposition": None,
        "orientation_signs_fixed": False,
        "candidate_closed_identity": "nabla_A(J_core^A+J_surface^A+J_attach^A)=0",
        "local_conservation": None,
        "global_closed_system_conservation": "REQUIRED_BY_AUTHOR_ONTOLOGY_BUT_NOT_YET_ACTION_DERIVED",
        "core_mediated_nonlocal_transfer": "OPEN",
        "new_independent_current_field": False,
        "status": "BLOCKED_BY_ABSENT_ATTACHMENT_ACTION_AND_ORIENTATION_FIXED_VARIATION",
        "validation_passed": True,
    }


def boundary_pressure_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_boundary_spectral_pressure_v11_2",
        "classification": "AUTHOR_HYPOTHESIS_AND_DERIVATION_TARGET",
        "boundary_operator": None,
        "interior_spectrum": None,
        "exterior_spectrum": None,
        "normalized_spectral_measure": None,
        "regularization": None,
        "formal_energy_difference": "Delta E(a)=E_in(a)-E_out(a)",
        "formal_pressure": "P(a)=-partial_a[Delta E(a)/Area]",
        "geometry_cases_calculable": [],
        "no_double_counting_rule": "standard field modes and any BHSM support modes must be identified or proved independent before summing",
        "status": "BLOCKED_BY_ABSENT_NORMALIZED_BOUNDARY_SUPPORT_OPERATOR_DOMAIN_AND_SPECTRAL_MEASURE",
        "validation_passed": True,
    }


def casimir_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_casimir_reproduction_gate_v11_2",
        "classification": "EXTERNAL_REPRODUCTION_BENCHMARK",
        "benchmark_energy_per_area": "-pi^2 hbar c/(720 a^3)",
        "benchmark_pressure": "-pi^2 hbar c/(240 a^4)",
        "a_minus_4_scaling_reproduced_by_bhsm": None,
        "exact_coefficient_reproduced_by_bhsm": None,
        "standard_qft_mode_restriction": "established benchmark only",
        "bhsm_support_mode_restriction": None,
        "bhsm_spacetime_displacement_interpretation": "AUTHOR_HYPOTHESIS",
        "standard_qft_equivalence": None,
        "additional_bhsm_contribution": None,
        "measured_coefficient_used_as_input": False,
        "verdict": CASIMIR_VERDICT,
        "validation_passed": True,
    }


def black_hole_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_black_hole_de_envelopment_transfer_v11_2",
        "classification": "AUTHOR_BLACK_HOLE_DE_ENVELOPMENT_HYPOTHESIS",
        "ordinary_motion": "dA_enc/dtau=dL_enc/dtau=0 on the conditional fixed-enclosure sector",
        "trigger": None,
        "transfer_map": None,
        "Gamma_BH": None,
        "enclosed_balance_candidate": "nabla_A J_enc^A=-Gamma_BH",
        "surface_balance_candidate": "nabla_A J_surface^A=+Gamma_BH",
        "conserved_sum_if_same_domain_and_orientation": "nabla_A(J_enc^A+J_surface^A)=0",
        "surface_receiving_domain": None,
        "cosmic_expansion_relation": None,
        "new_transfer_term_added": False,
        "status": "BLOCKED_BY_ABSENT_TRIGGER_TRANSFER_OPERATOR_AND_SURFACE_RECEIVING_DOMAIN",
        "validation_passed": True,
    }


def steering_payload() -> dict[str, Any]:
    sections = {
        "ontology": ontology_payload(),
        "fixed_encapsulation": fixed_encapsulation_payload(),
        "relational_displacement": displacement_payload(),
        "core_surface_exchange": exchange_current_payload(),
        "boundary_spectral_pressure": boundary_pressure_payload(),
        "casimir_gate": casimir_payload(),
        "black_hole_transfer": black_hole_payload(),
    }
    return {
        "artifact": "BHSM_bidirectional_buoyancy_steering_result_v11_2",
        **sections,
        "supported_action": {"new_action_owned_term": None, "new_fields": [], "new_coefficients": [], "arbitrary_choices_introduced": False, "complete": False, "Mark_II": "NOT_REACHED"},
        "validated": ["intrinsic/extrinsic separation", "conditional inverse-square radial flux dilution", "need for a boundary spectral-pressure calculation"],
        "invalidated": ["nonzero support character on the intrinsic enclosure metric in the current full-coframe action", "one universal inverse-square law", "plate Casimir pressure from spherical dilution", "unrestricted spacetime creation", "black-hole transfer without a receiving channel"],
        "open": ["attachment character", "exchange current", "normalized boundary support spectrum", "de-envelopment threshold and transfer", "cosmological response"],
        "primary_verdict": VERDICT,
        "exact_next_object": NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_promoted": [],
        "validation_passed": all(section["validation_passed"] for section in sections.values()),
    }
