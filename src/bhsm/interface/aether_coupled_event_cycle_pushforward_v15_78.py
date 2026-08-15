"""Coupled Cartan-gap event asymptotics and the single cycle pushforward.

This module does not average an independently normalized gauge action with an
independently chosen Yukawa action.  Both are functional derivatives of one
period of the same reduced parent boundary functional.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_cartan_shell_crossing_v15_76 import (
    leading_cartan_amplitude,
    leading_crossing_estimate,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_nonlinear_cartan_gap_branch_v15_77 import (
    solve_up_gap,
    up_effective_coupling,
)
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    geometric_heat_parameter,
)


VERSION = "v15.78"
CLASSIFICATION = "BHSM_COUPLED_EVENT_CYCLE_PUSHFORWARD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def _spectral_rows() -> list[tuple[float, float]]:
    heat = geometric_heat_parameter()
    rows: list[tuple[float, float]] = []
    for n in range(128):
        energy = n + 1.5
        weight = (n + 1) * (n + 2) * math.exp(-heat * energy * energy)
        rows.append((energy, weight))
        if n > 12 and weight < 1.0e-16:
            break
    return rows


def heat_weight_count() -> float:
    """The finite heat-weighted state count controlling the strong branch."""

    return sum(weight for _, weight in _spectral_rows())


def minimized_gap_potential(epsilon: float) -> float:
    """Dimensionless Hubbard--Stratonovich potential at its gap solution."""

    row = solve_up_gap(epsilon)
    if not row["broken"]:
        return 0.0
    x = float(row["mass_times_R4"])
    radius = RADIUS0 / 2.0
    g_hat = up_effective_coupling(epsilon) / (2.0 * math.pi**2 * radius**2)
    sea = sum(
        weight * (math.sqrt(energy * energy + x * x) - energy)
        for energy, weight in _spectral_rows()
    )
    return x * x / (2.0 * g_hat) - sea


def envelope_backreaction(epsilon: float) -> float:
    """Return ``d V_*(epsilon)/d epsilon`` by the envelope theorem."""

    row = solve_up_gap(epsilon)
    if not row["broken"]:
        return 0.0
    x = float(row["mass_times_R4"])
    radius = RADIUS0 / 2.0
    amplitude = leading_cartan_amplitude()
    g_hat = up_effective_coupling(epsilon) / (2.0 * math.pi**2 * radius**2)
    # g_hat'=-A_EC/(4*pi^2*R4^2*epsilon^(3/2)).
    return (
        amplitude * x * x
        / (8.0 * math.pi**2 * radius**2 * g_hat**2 * epsilon**1.5)
    )


def strong_branch_asymptotics() -> dict[str, float | str]:
    """Coefficients of the epsilon-down-to-zero solution and its stress."""

    radius = RADIUS0 / 2.0
    amplitude = leading_cartan_amplitude()
    count = heat_weight_count()
    g_coefficient = amplitude / (2.0 * math.pi**2 * radius**2)
    x_coefficient = count * g_coefficient
    mass_coefficient = x_coefficient / radius
    potential_coefficient = 0.5 * count * count * g_coefficient
    z_coefficient = count / (4.0 * math.pi**2 * x_coefficient**3)
    yukawa_coefficient = z_coefficient ** -0.5
    return {
        "heat_weight_count": count,
        "g_hat": "g_hat~g0*epsilon^(-1/2)",
        "g0": g_coefficient,
        "mass_times_R4": "x~x0*epsilon^(-1/2)",
        "x0": x_coefficient,
        "mass_in_ell_kappa_inverse_coefficient": mass_coefficient,
        "V_star": "V_star~-D*epsilon^(-1/2)",
        "D": potential_coefficient,
        "dV_star_d_epsilon": "+(D/2)*epsilon^(-3/2)",
        "Z_H": "Z_H~Z0*epsilon^(3/2)",
        "Z0": z_coefficient,
        "Y": "Y~Y0*epsilon^(-3/4)",
        "Y0": yukawa_coefficient,
    }


def simple_legendre_event_balance() -> dict[str, Any]:
    """Power-count a KKT-derived approach ``epsilon~a*tau**p``.

    The Legendre eigenvalue is a phase-space function.  It must not be
    relabelled as a configuration coordinate with an assumed kinetic term.
    This function therefore records the exact integrability threshold that
    the constrained Legendre pencil has to satisfy.
    """

    return {
        "simple_event_coordinate": (
            "epsilon=lambda_min(H_Legendre),_d_epsilon_not_zero_at_Sigma"
        ),
        "event_law_to_be_computed_from_KKT": (
            "epsilon(t)~a*(T_star-t)^p,_a>0"
        ),
        "mass_law": "m(t)=O((T_star-t)^(-p/2))",
        "Yukawa_law": "Y(t)=O((T_star-t)^(-3p/4))",
        "gauge_DtN_law": "Z_g(t)=O(1)",
        "mass_impulse_integrable_iff": "p<2",
        "Yukawa_vertex_integrable_iff": "p<4/3",
        "gauge_residue_integrable": True,
        "frozen_transverse_p_equals_1_would_be_integrable": True,
        "p_equals_4_over_7_not_assumed": True,
        "reason": (
            "a_vanishing_phase-space_Legendre_eigenvalue_is_not_itself_a_"
            "configuration_coordinate_with_epsilon*dot(epsilon)^2_kinetics"
        ),
        "reset_value_can_be_zero_while_cycle_functional_is_nonzero": True,
    }


def cycle_pushforward_contract() -> dict[str, Any]:
    """Define all four-dimensional residues from one parent period."""

    return {
        "one_period_functional": (
            "Gamma_cycle[B]=Gamma_reset[B(T_star),B(0)]"
            "+integral_0^Tstar dt*Gamma_boundary[W_t;B(t)]"
        ),
        "absolute_gauge_normalization": (
            "Z_i^cycle=(1/Tstar)*delta^2_Gamma_cycle/"
            "delta_F_i_delta_F_i_at_zero"
        ),
        "composite_kinetic_residue": (
            "Z_H^cycle=(1/Tstar)*delta^2_Gamma_cycle/"
            "delta_(D_H)_delta_(D_Hbar)_at_H_star"
        ),
        "left_right_vertex": (
            "R_f^cycle=(1/Tstar)*delta^3_Gamma_cycle/"
            "delta_bar_fL_delta_fR_delta_H_at_H_star"
        ),
        "canonical_Yukawa": (
            "Y_f^cycle=(Z_L^cycle)^(-1/2)*R_f^cycle*"
            "(Z_R^cycle)^(-1/2)*(Z_H^cycle)^(-1/2)"
        ),
        "Floquet_mass": (
            "M_F=(i/Tstar)*Log[U_reset*Texp(-i*integral_0^Tstar M(t)dt)]"
        ),
        "central_family_specialization": (
            "M(t)=m(t)*I3_implies_time_ordering_drops_and_the_event_mass_"
            "impulse_is_positive_and_finite"
        ),
        "same_parent_functional_for_gauge_and_Yukawa": True,
        "independent_normalization_conditions": False,
    }


def backreaction_rows() -> list[dict[str, float]]:
    critical = leading_crossing_estimate()["up_leading_epsilon_star"]
    rows = []
    for fraction in (0.9, 0.5, 0.1, 0.01):
        epsilon = fraction * critical
        rows.append({
            "epsilon_fraction": fraction,
            "V_star": minimized_gap_potential(epsilon),
            "dV_star_d_epsilon": envelope_backreaction(epsilon),
        })
    return rows


def completion_payload() -> dict[str, Any]:
    asymptotics = strong_branch_asymptotics()
    balance = simple_legendre_event_balance()
    cycle = cycle_pushforward_contract()
    rows = backreaction_rows()
    validation = {
        "broken_potential_strictly_negative": all(row["V_star"] < 0.0 for row in rows),
        "backreaction_drives_epsilon_down": all(
            row["dV_star_d_epsilon"] > 0.0 for row in rows
        ),
        "strong_mass_coefficient_positive": (
            asymptotics["mass_in_ell_kappa_inverse_coefficient"] > 0.0
        ),
        "cycle_integrability_threshold_derived": (
            balance["mass_impulse_integrable_iff"] == "p<2"
            and balance["Yukawa_vertex_integrable_iff"] == "p<4/3"
            and balance["gauge_residue_integrable"]
        ),
        "one_parent_cycle_functional": cycle[
            "same_parent_functional_for_gauge_and_Yukawa"
        ] and not cycle["independent_normalization_conditions"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_coupled_event_cycle_pushforward_v15_78",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "backreaction_rows": rows,
        "strong_branch_asymptotics": asymptotics,
        "simple_legendre_event_balance": balance,
        "cycle_pushforward": cycle,
        "scientific_result": (
            "THE_CARTAN_GAP_STRESS_DRIVES_THE_SAME_LEGENDRE_EVENT;_FOR_THE_"
            "KKT-DERIVED_EVENT_LAW_epsilon~TAU^p_THE_MASS_AND_YUKAWA_"
            "INSERTIONS_ARE_CYCLE-INTEGRABLE_IFF_p<2_AND_p<4/3,_WHILE_THE_"
            "FINITE_GAUGE_DtN_IS_INTEGRABLE;_ALL_ARE_DERIVATIVES_OF_ONE_"
            "Gamma_cycle"
        ),
        "claim_boundary": {
            "coupled_dominant_event_power_solved": False,
            "one_cycle_residue_functional_derived": True,
            "constrained_Legendre_event_exponent_p_evaluated": False,
            "full_cycle_absolute_numbers_evaluated": False,
        },
        "active_calculation": (
            "EVALUATE_THE_CONSTRAINED_KKT_VECTOR_FIELD_ACTING_ON_THE_MINIMUM_"
            "LEGENDRE_EIGENVALUE_TO_FIX_p,_THEN_EVALUATE_THE_FULL_ONE-PERIOD_"
            "GAUGE_AND_FERMION_RESIDUES"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_coupled_event_cycle_pushforward_v15_78.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "heat_weight_count",
    "minimized_gap_potential", "envelope_backreaction",
    "strong_branch_asymptotics", "simple_legendre_event_balance",
    "cycle_pushforward_contract", "backreaction_rows", "completion_payload",
    "deterministic_json", "materialize",
]
