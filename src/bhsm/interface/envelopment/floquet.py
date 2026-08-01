"""Relative-periodic, Floquet, family, and downstream fail-closed gates."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from ..master_action.automatic_geometric_lens_theorem import (
    physical_current_from_action_forms,
)
from .foundation import FAMILY_LEDGERS


def monodromy_audit(
    monodromy: np.ndarray,
    *,
    removed_modes: Iterable[int] = (),
    tolerance: float = 1.0e-10,
) -> dict[str, Any]:
    """Classify a supplied finite-dimensional monodromy diagnostic."""

    matrix = np.asarray(monodromy, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("monodromy must be square")
    removed = sorted(set(int(index) for index in removed_modes))
    eigenvalues = np.linalg.eigvals(matrix)
    physical = np.delete(eigenvalues, removed) if removed else eigenvalues
    radii = np.abs(physical)
    if radii.size == 0:
        classification = "NUMERICALLY_UNRESOLVED"
    elif np.any(radii > 1 + tolerance):
        classification = "UNSTABLE"
    elif np.any(np.abs(radii - 1) <= tolerance):
        classification = "MARGINAL"
    else:
        classification = "STABLE"
    return {
        "multipliers": [[float(value.real), float(value.imag)] for value in eigenvalues],
        "removed_mode_indices": removed,
        "physical_multiplier_radii": [float(value) for value in radii],
        "classification": classification,
        "physical_orbit_claimed": False,
    }


def relative_periodic_orbit_gate() -> dict[str, Any]:
    return {
        "target": "Phi(tau+T)=h.Phi(tau)",
        "charged_lepton_target": "electron-like timelike self-envelopment",
        "ansatz_candidates": [
            "spherical/cohomogeneity-one degree-one texture prototype",
            "Berger-Hopf equivariant texture",
            "internal phase rotation",
            "breathing radius",
            "coupled eta-sigma-metric-gauge dressing",
        ],
        "ansatz_audit": [
            {
                "class": "spherical/cohomogeneity-one",
                "retains": ["degree", "breathing scale", "sigma formation"],
                "loses_or_unproved": ["Hopf-weighted current", "C3 family immersion", "charged gauge dressing"],
                "physical_target_eligible": False,
                "use": "normalized coefficient proxy only",
            },
            {
                "class": "Berger-Hopf equivariant",
                "retains": ["Hopf anisotropy", "internal triality orientation", "breathing scale"],
                "loses_or_unproved": ["action-selected localized domain", "local M4 chiral transgression", "gauge boundary data"],
                "physical_target_eligible": None,
                "use": "next ansatz theorem target",
            },
            {
                "class": "fully coupled eta-sigma-metric-gauge relative-periodic",
                "retains": ["complete target field content", "gauge dressing", "moving boundary"],
                "loses_or_unproved": ["tractable gauge-fixed reduction", "elliptic-hyperbolic domain", "connection ownership"],
                "physical_target_eligible": None,
                "use": "required physical boundary-value problem",
            },
        ],
        "least_restrictive_selected_ansatz": None,
        "complete_reduced_equations": None,
        "gauge_fixed_boundary_conditions": None,
        "action_selected_orbit": None,
        "period": None,
        "physical_energy": None,
        "Floquet_operator": None,
        "Floquet_classification": "NOT_EVALUABLE_NO_PHYSICAL_ORBIT",
        "numerical_search_executed": False,
        "numerical_search_block_reason": (
            "the coupled gauge-fixed operator, admissible boundary domain, and local "
            "chiral/gauge attachment are not defined, so shooting or collocation would solve a chosen proxy theory"
        ),
        "numerical_evidence": {
            "discretization": None,
            "domain": None,
            "boundary_conditions": None,
            "residual_norm": None,
            "constraint_residual": None,
            "convergence_order": None,
            "independent_method_agreement": None,
            "conserved_quantities": None,
        },
        "collective_radius_proxy_available": True,
        "collective_radius_proxy_is_particle": False,
        "status": "BLOCKED_EXACT_OBJECT_PROVED",
        "exact_missing_object": (
            "GAUGE_FIXED_COUPLED_ETA_SIGMA_METRIC_CONNECTION_RELATIVE_PERIODIC_"
            "BOUNDARY_VALUE_PROBLEM_WITH_ACTION_OWNED_BOUNDARY_DATA"
        ),
    }


def cycle_form_definitions() -> dict[str, Any]:
    return {
        "A_f": None,
        "G_f": "T^-1 int_0^T A_f^dagger K8 A_f dtau",
        "Q_f": "T^-1 int_0^T A_f^dagger H8 A_f dtau",
        "K_ud": "T^-1 int_0^T A_u^dagger J_CG A_d dtau",
        "L_f": "G_f^-1/2 Q_f G_f^-1/2",
        "V_BHSM": "W_u^dagger Pol(G_u^-1/2 K_ud G_d^-1/2) W_d",
        "physical_G_u": None,
        "physical_Q_u": None,
        "physical_G_d": None,
        "physical_Q_d": None,
        "physical_K_ud": None,
        "physical_V_BHSM": None,
        "matrix_printed": False,
        "reason": "no stable action-selected orbit or family immersion A_f exists",
    }


def static_cycle_reduction(
    G_u: np.ndarray,
    Q_u: np.ndarray,
    K_ud: np.ndarray,
    G_d: np.ndarray,
    Q_d: np.ndarray,
) -> dict[str, Any]:
    """Evaluate the stationary limit of the v10 cycle averages.

    Constant cycle data integrate to the existing v8.9 static Gram, Hessian,
    and current forms.  This utility tests only that mathematical limit.
    """

    result = physical_current_from_action_forms(G_u, Q_u, K_ud, G_d, Q_d)
    return {
        "cycle_average_G_u": np.asarray(G_u, dtype=complex),
        "cycle_average_Q_u": np.asarray(Q_u, dtype=complex),
        "cycle_average_K_ud": np.asarray(K_ud, dtype=complex),
        "cycle_average_G_d": np.asarray(G_d, dtype=complex),
        "cycle_average_Q_d": np.asarray(Q_d, dtype=complex),
        "static_v8_9_result": result,
        "identity_exact": True,
        "physical_promotion": False,
    }


def static_limit_theorem() -> dict[str, Any]:
    return {
        "hypothesis": "A_f,K8,H8,J_CG are stationary along the cycle",
        "conclusion": (
            "cycle averages equal the static pullback Gram, Hessian, and current "
            "forms used by the v8.9 automatic geometric lens theorem"
        ),
        "new_normalization": False,
        "classification": "DERIVED_CONDITIONAL",
    }


def downstream_sector_gates() -> dict[str, Any]:
    return {
        "charged_lepton": {
            "orbit": None,
            "mass": None,
            "status": "BLOCKED_BY_NO_GAUGE_DRESSED_STABLE_RELATIVE_PERIODIC_ORBIT",
        },
        "quark": {
            "isolated_branch_sought": False,
            "color_neutral_parent": None,
            "nested_sub_envelopments": None,
            "separation_energy_curve": None,
            "status": "BHSM_QUARK_SUB_ENVELOPMENT_REQUIRES_A_COMPLETE_COLOR_NEUTRAL_PARENT_SOLUTION",
        },
        "neutrino": {
            "static_rest_mass_assigned": False,
            "propagating_orbit": None,
            "monodromy_sectors": None,
            "PMNS": None,
            "adiabatic_L_over_E_limit": None,
            "status": "BHSM_NEUTRINO_THREE_SECTOR_MONODROMY_NOT_GENERATED_BY_CURRENT_ORBIT",
        },
        "measurement": {
            "coupled_system_definition_registered": True,
            "normalized_probabilities": None,
            "scattering_amplitudes": None,
            "status": "OPEN_COUPLED_BASIN_TRANSITION_AMPLITUDE_THEOREM",
        },
        "four_dimensional": {
            "field_dictionary": None,
            "canonical_normalization": None,
            "Lorentz_and_gauge_assignments": None,
            "mass_width_scheme": None,
            "renormalization_scheme": None,
            "runtime": None,
            "status": "OPEN_AFTER_PHYSICAL_ORBIT_AND_UNIT_BRIDGE",
        },
    }


def family_and_floquet_payload() -> dict[str, Any]:
    forms = cycle_form_definitions()
    gates = downstream_sector_gates()
    return {
        "family_ledgers": {key: [list(slot) for slot in value] for key, value in FAMILY_LEDGERS.items()},
        "relative_periodic_orbit": relative_periodic_orbit_gate(),
        "cycle_forms": forms,
        "static_limit": static_limit_theorem(),
        "sectors": gates,
        "physical_CKM": None,
        "physical_PMNS": None,
        "matrices_printed": False,
        "measured_flavor_inputs_used": False,
        "classification": "DERIVED_CONDITIONAL",
    }
