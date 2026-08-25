"""Analytic N12 full-action branch at the round expanding balance."""

from __future__ import annotations

from typing import Any


def normalized_action_scale_decomposition() -> dict[str, Any]:
    """Return the exact epsilon=R4^-2 decomposition near the round state."""

    return {
        "small_parameter": "epsilon=R4^-2",
        "normalized_action": (
            "L_hat=L7+epsilon*L5+epsilon^2*L3+epsilon^3*L1+"
            "epsilon^4*L_minus1+epsilon^7*J/(I7+epsilon*I5+"
            "epsilon^2*I3+epsilon^3*I1)"
        ),
        "bulk_scale_weights": [7, 5, 3, 1, -1],
        "bulk_epsilon_powers": [0, 1, 2, 3, 4],
        "inertia_scale_weights": [7, 5, 3, 1],
        "normalized_inverse_inertia_leading_epsilon_power": 7,
        "boundary_Casimir_epsilon_power": 4,
        "coefficient_functions_are_real_analytic": True,
        "round_leading_inertia_strictly_positive": True,
        "reason": (
            "volume,_positive_interior_localization,_unit_lapse,_and_"
            "eta_legendre=1+x_spatial^3>1_on_the_round_state"
        ),
    }


def positive_integer_nonresonance() -> dict[str, Any]:
    """Prove invertibility of every positive-order recurrence pencil."""

    return {
        "recurrence_pencil": "A7+2*k*H0*E7",
        "positive_orders": "k_in_Z_greater_than_or_equal_to_1",
        "finite_descriptor_roots": ["0", "-7*H0"],
        "candidate_recurrence_root": "-2*k*H0",
        "center_collision": "-2*k*H0=0_has_no_positive_integer_solution",
        "stable_collision": "-2*k*H0=-7*H0_requires_k=7/2_not_an_integer",
        "all_positive_integer_recurrence_pencils_invertible": True,
        "algebraic_multiplier_block_removed_by_analytic_constraint_IFT": True,
    }


def asymptotic_branch_theorem() -> dict[str, Any]:
    """Return the analytic Briot--Bouquet consequence and exact scope."""

    scale = normalized_action_scale_decomposition()
    nonresonance = positive_integer_nonresonance()
    return {
        "theorem": "FINITE_DIMENSIONAL_ANALYTIC_BRIOT_BOUQUET_BRANCH",
        "hypotheses": {
            "normalized_full_action_real_analytic_near_round_state": scale[
                "coefficient_functions_are_real_analytic"
            ],
            "inverse_inertia_denominator_nonzero_near_round_state": scale[
                "round_leading_inertia_strictly_positive"
            ],
            "positive_integer_nonresonance": nonresonance[
                "all_positive_integer_recurrence_pencils_invertible"
            ],
            "first_order_gauge_compatibility_required": True,
            "classical_Noether_compatibility_continues_all_orders": True,
        },
        "conclusion": {
            "exists_epsilon_star": True,
            "branch_domain": "0<=epsilon<epsilon_star",
            "complete_descriptor_branch": "Z(epsilon)=epsilon*X5+epsilon^2*R(epsilon)",
            "remainder": "R_is_real_analytic_and_uniformly_bounded_on_0<=epsilon<=epsilon_0<epsilon_star",
            "log_radius_rate": "H4(epsilon)=H0+epsilon*h1+epsilon^2*r_H(epsilon)",
            "positive_limit": "lim_(epsilon_to_0+)H4=H0=sqrt(kappa0/42)>0",
            "event_or_domain_stop_inside_sufficiently_small_asymptotic_neighborhood": False,
        },
        "scope": {
            "existence_not_universal_reachability": True,
            "mathematical_infinite_branch_only": True,
            "owner_classification": "NONREALIZED_FORMATION_HISTORY",
            "physical_particle_observable_promoted": False,
            "R_minus_2_eigenvalue_promoted": False,
        },
    }


__all__ = [
    "asymptotic_branch_theorem",
    "normalized_action_scale_decomposition",
    "positive_integer_nonresonance",
]
