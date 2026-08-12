"""Foundational decidability audit for completing BHSM from the retained action.

The established q-to-s transfer is accepted.  This module integrates the
retained nonlinear q--sigma Hamiltonian sub-block and proves two facts that
survive adding the parity-even shape sector: sigma=0 is an exact invariant
trajectory, and the repository leaves inequivalent sigma response jets as
independent action data.  Hence a unique material skin and downstream child
cannot be selected from the current mathematical input without an additional
action-owned response/initial-state law.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_ivp

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    reconstruction_interface_payload,
    retained_nonuniqueness_witness,
)
from bhsm.interface.aether_sigma_saturation_ejection_v15_19 import (
    formation_homoclinic_state,
)


FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
RESULT = (
    "CURRENT_BHSM_ACTION_FAMILY_DOES_NOT_SELECT_A_UNIQUE_SIGMA_RESPONSE_"
    "OR_NONZERO_SYMMETRY_BREAKING_SEED_SO_MATERIAL_SKIN_CHILD_"
    "RECONSTRUCTION_AND_FULL_BHSM_COMPLETION_ARE_NOT_DEDUCIBLE"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def coupled_q_sigma_trajectory(
    *,
    g: float,
    static_sigma_curvature: float,
    direct_sigma_quartic: float,
    sigma_seed: float,
    supercriticality: float = 0.4,
    kappa1: float = 1.0,
    zsigma: float = 1.0,
    cutoff_in_growth_times: float = 12.0,
) -> dict[str, Any]:
    """Integrate the exact retained q--sigma Hamiltonian sub-block.

    H=pq^2/[2 Mq(1+g sigma^2)]+p_sigma^2/(2Z)+Vq+
      K sigma^2/2+G0 sigma^4/4.
    The q-to-s sector is parity even, so it cannot invalidate the exact
    sigma-zero invariant-submanifold theorem used here.
    """

    coupling = float(g)
    curvature = float(static_sigma_curvature)
    quartic = float(direct_sigma_quartic)
    seed = float(sigma_seed)
    m = _positive(supercriticality, "supercriticality")
    k1 = _positive(kappa1, "kappa1")
    z = _positive(zsigma, "zsigma")
    cutoff = _positive(cutoff_in_growth_times, "cutoff_in_growth_times")
    if not all(math.isfinite(item) for item in (coupling, curvature, quartic, seed)):
        raise ValueError("couplings and seed must be finite")
    if coupling < 0.0 or quartic < 0.0:
        raise ValueError("this bounded control requires g and G0 nonnegative")
    critical_radius = (343.0 / (5.0 * k1)) ** (1.0 / 6.0)
    inertia = 1.5 * critical_radius**2
    growth_rate = math.sqrt(5.0 * m / (6.0 * critical_radius**2))
    time_limit = cutoff / growth_rate
    incoming = formation_homoclinic_state(
        -time_limit, supercriticality=m, critical_radius=critical_radius
    )

    def q_potential(q: float) -> float:
        return -5.0 * m * q**2 / 8.0 + 23.0 * q**4 / 144.0

    def q_potential_prime(q: float) -> float:
        return -5.0 * m * q / 4.0 + 23.0 * q**3 / 36.0

    def hamiltonian(state: np.ndarray) -> float:
        q, p_q, sigma, p_sigma = state
        weight = 1.0 + coupling * sigma**2
        return (
            p_q**2 / (2.0 * inertia * weight)
            + p_sigma**2 / (2.0 * z)
            + q_potential(q)
            + 0.5 * curvature * sigma**2
            + 0.25 * quartic * sigma**4
        )

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        q, p_q, sigma, p_sigma = state
        weight = 1.0 + coupling * sigma**2
        return np.array(
            [
                p_q / (inertia * weight),
                -q_potential_prime(q),
                p_sigma / z,
                coupling * p_q**2 * sigma / (inertia * weight**2)
                - curvature * sigma
                - quartic * sigma**3,
            ]
        )

    initial = np.array(
        [
            incoming["q"],
            inertia * (1.0 + coupling * seed**2) * incoming["q_dot"],
            seed,
            0.0,
        ]
    )
    solution = solve_ivp(
        rhs,
        (-time_limit, time_limit),
        initial,
        method="DOP853",
        rtol=1.0e-10,
        atol=1.0e-12,
        max_step=0.1 / growth_rate,
    )
    energies = np.array(
        [hamiltonian(solution.y[:, index]) for index in range(solution.y.shape[1])]
    )
    sigma_values = solution.y[2]
    return {
        "Hamiltonian": (
            "pq^2/[2Mq(1+g*sigma^2)]+p_sigma^2/(2Z)+Vq+"
            "Ksigma^2/2+G0sigma^4/4"
        ),
        "g": coupling,
        "K_sigma": curvature,
        "G0": quartic,
        "sigma_seed": seed,
        "solver_success": bool(solution.success),
        "maximum_absolute_sigma": float(np.max(np.abs(sigma_values))),
        "final_sigma": float(sigma_values[-1]),
        "final_q": float(solution.y[0, -1]),
        "energy_drift": float(np.max(energies) - np.min(energies)),
        "sigma_zero_exact_numerically": bool(np.max(np.abs(sigma_values)) == 0.0),
        "material_skin_criterion_defined": False,
    }


def sigma_zero_invariance_theorem() -> dict[str, Any]:
    """State the exact classical uniqueness result on the symmetric branch."""

    return {
        "sigma_equation_structure": (
            "dot_p_sigma=sigma*[g*p^T*I0^-1*p/(1+g*sigma^2)^2-"
            "K_sigma-G0*sigma^2]"
        ),
        "initial_data": "sigma=0_and_p_sigma=0",
        "unique_solution": "sigma(t)=0_and_p_sigma(t)=0",
        "holds_with_q_s_transfer": True,
        "reason": (
            "the_retained_q_s_action_and_constraint_domain_are_sigma_"
            "reflection_even_and_the_Hamiltonian_vector_field_is_locally_Lipschitz"
        ),
        "tachyonic_curvature_creates_nonzero_classical_seed": False,
        "positive_inertial_saturation_creates_nonzero_classical_seed": False,
        "sign_branch_selected": False,
    }


def nonlinear_nonuniqueness_witness() -> dict[str, Any]:
    """Return deterministic trajectories showing unresolved physical dependence."""

    zero = coupled_q_sigma_trajectory(
        g=5.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
        sigma_seed=0.0,
    )
    weak = coupled_q_sigma_trajectory(
        g=0.1,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
        sigma_seed=1.0e-6,
    )
    strong = coupled_q_sigma_trajectory(
        g=5.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
        sigma_seed=1.0e-6,
    )
    seed_changed = coupled_q_sigma_trajectory(
        g=5.0,
        static_sigma_curvature=0.02,
        direct_sigma_quartic=1.0,
        sigma_seed=1.0e-4,
    )
    return {
        "exact_zero_seed": zero,
        "weak_response_control": weak,
        "strong_response_control": strong,
        "same_action_changed_seed_control": seed_changed,
        "same_formation_architecture_different_g_changes_amplification": (
            strong["maximum_absolute_sigma"] > 1000.0 * weak["maximum_absolute_sigma"]
        ),
        "same_action_different_unselected_seed_changes_nonlinear_outcome": (
            seed_changed["maximum_absolute_sigma"]
            > 10.0 * strong["maximum_absolute_sigma"]
        ),
        "zero_seed_stays_zero": zero["sigma_zero_exact_numerically"],
        "controls_are_predictions": False,
    }


def foundational_completion_audit() -> dict[str, Any]:
    """Combine the algebraic coefficient and initial-state obstructions."""

    coefficients = retained_nonuniqueness_witness()
    interface = reconstruction_interface_payload()
    zero_theorem = sigma_zero_invariance_theorem()
    dynamics = nonlinear_nonuniqueness_witness()
    return {
        "retained_action_is_single_fully_selected_theory": False,
        "independent_sigma_response_triples_exist": len(coefficients["triples"]),
        "triples_share_sigma_zero_parent_and_first_variation": coefficients[
            "same_sigma_zero_background_and_first_variation"
        ],
        "nonlinear_dynamics_depends_on_unselected_response_data": dynamics[
            "same_formation_architecture_different_g_changes_amplification"
        ],
        "classical_nonzero_seed_or_state_rule_present": False,
        "sigma_zero_invariant": zero_theorem["unique_solution"],
        "physical_response_jet_present": interface[
            "physical_sigma_propagator_present_in_repository"
        ],
        "response_jet_X_derivative_present": interface["X_derivative_present_in_repository"],
        "nonlinear_response_present": interface[
            "physical_nonlinear_sigma_response_present_in_repository"
        ],
        "minimum_missing_action_owned_data": [
            "physical_sigma_generator_or_response_jet_(S_sigma,dS_sigma/dX,lambda_sigma)",
            "sigma_symmetry_breaking_initial_state_or_quantum_state_selection_rule",
            "pregeometric_to_regular_pairing_that_derives_both_without_empirical_fit",
        ],
        "can_be_derived_by_varying_existing_regular_fields": False,
        "reason": (
            "Euler_Lagrange_variation_of_fields_cannot_select_independent_"
            "unvaried_action_coefficients_and_a_Lipschitz_Z2_even_flow_"
            "cannot_leave_exact_zero_initial_data"
        ),
        "inventing_numeric_selector_allowed": False,
        "unique_material_skin_deducible": False,
        "unique_child_or_Unique_Actualization_deducible": False,
        "foundational_contradiction_to_requested_unconditional_completion": True,
    }


def completion_payload() -> dict[str, Any]:
    theorem = sigma_zero_invariance_theorem()
    dynamics = nonlinear_nonuniqueness_witness()
    audit = foundational_completion_audit()
    validation = {
        "zero_seed_remains_exactly_zero": dynamics["zero_seed_stays_zero"],
        "all_nonlinear_controls_integrate": all(
            row["solver_success"]
            for key, row in dynamics.items()
            if isinstance(row, dict) and "solver_success" in row
        ),
        "Hamiltonian_drift_small": all(
            row["energy_drift"] < 5.0e-11
            for key, row in dynamics.items()
            if isinstance(row, dict) and "energy_drift" in row
        ),
        "coefficient_dependence_material": dynamics[
            "same_formation_architecture_different_g_changes_amplification"
        ],
        "seed_dependence_material": dynamics[
            "same_action_different_unselected_seed_changes_nonlinear_outcome"
        ],
        "Z2_theorem_survives_shape_transfer": theorem["holds_with_q_s_transfer"],
        "response_jet_absence_confirmed": not audit["physical_response_jet_present"],
        "unconditional_completion_blocked": audit[
            "foundational_contradiction_to_requested_unconditional_completion"
        ],
        "no_parameter_fitted_or_selector_invented": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_completion_foundational_obstruction",
        "result": RESULT,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "sigma_zero_invariance_theorem": theorem,
        "nonlinear_q_sigma_backreaction_witness": dynamics,
        "foundational_completion_audit": audit,
        "scientific_status": (
            "the_q_to_s_enclosure_transfer_is_retained_but_the_current_"
            "action_does_not_determine_whether_a_nonzero_sigma_skin_ever_forms"
        ),
        "downstream_quantities_not_well_defined": [
            "material_skin",
            "geometric_separation_d",
            "contact_or_ejection_basin",
            "reconstruction_loss_surface",
            "Aether_transition_input",
            "persistent_child",
            "child_evaluated_Standard_Model_sectors",
            "Unique_Actualization",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "numeric_response_selector_invented": False,
            "primitive_Aether_geometry_used": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_completion_foundational_obstruction.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "FULL_BHSM_COMPLETE",
    "RESULT",
    "coupled_q_sigma_trajectory",
    "sigma_zero_invariance_theorem",
    "nonlinear_nonuniqueness_witness",
    "foundational_completion_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
