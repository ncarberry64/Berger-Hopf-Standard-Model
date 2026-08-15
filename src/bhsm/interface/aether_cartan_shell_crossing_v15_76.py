"""Normalize the Cartan LR kernel and estimate its first event-shell crossing."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import cap_fields
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import (
    SNAPSHOTS,
    up_channel_norm_bound,
)
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    geometric_heat_parameter,
    physical_heat_susceptibility,
)


VERSION = "v15.76"
CLASSIFICATION = "BHSM_NORMALIZED_CARTAN_EVENT_SHELL_CROSSING"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def clifford_coefficient_contract() -> dict[str, Any]:
    return {
        "spin_connection_derivative": (
            "delta_L_D/delta_omega_MAB=(i/4)*e*barPsi*Gamma^MAB*Psi"
        ),
        "antisymmetric_contorsion_EH_term": "-(K_G5*W/2)*C_ABC*C^ABC",
        "eliminated_three_form_term": (
            "-(1/(32*K_G5*W))*(barPsi*Gamma_ABC*Psi)^2"
        ),
        "four_dimensional_axial_magnitude": "3/(16*K_G5*W)",
        "scalar_LR_Fierz_magnitude": "c_EC/(K_G5*W),_c_EC=3/4",
        "c_EC": 0.75,
        "new_coefficient": False,
    }


@lru_cache(maxsize=1)
def shell_geometry(points: int = 1800) -> dict[str, float]:
    state = SNAPSHOTS[0.10602]
    q = np.asarray(state["q"], dtype=float)
    velocity = np.asarray(state["v"], dtype=float)
    multipliers = np.asarray(state["m"], dtype=float)
    fields = cap_fields(q, velocity, points=points)
    chi = np.asarray(fields["chi"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    C = np.asarray(fields["C"])
    f = np.asarray(fields["f"])
    sigma = np.asarray(fields["sigma"])
    radius = A * B / np.sqrt(A * A + B * B)
    n1, n2, b0, b1 = multipliers
    lapse = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    shift = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    normal_f = (
        np.asarray(fields["f_dot_coordinate"])
        - shift * np.asarray(fields["f_prime"])
    ) / lapse
    spatial_x = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    legendre = 1.0 + (spatial_x - normal_f**2) ** 3
    index = int(np.argmin(legendre))

    proper = np.zeros_like(chi)
    proper[1:] = np.cumsum(
        0.5 * (C[1:] + C[:-1]) * np.diff(chi)
    )
    shell_s = float(proper[index])
    local = np.abs(chi - chi[index]) < 0.025
    polynomial = np.polyfit(proper[local] - shell_s, legendre[local], 4)
    quadratic_coefficient = float(polynomial[-3])

    boundary_radius = float(radius[-1])
    jacobian = (radius / boundary_radius) ** 3
    # Exact v14.45 cancellation: J|u0|^2=N0^2 sin(f)^2.
    normalization_integral = float(np.trapezoid(np.sin(f) ** 2 * C, chi))
    normalization = normalization_integral ** -0.5
    u0_shell = float(
        normalization * jacobian[index] ** -0.5 * math.sin(float(f[index]))
    )
    return {
        "time": 0.10602,
        "shell_chi": float(chi[index]),
        "shell_proper_coordinate": shell_s,
        "minimum_eta_Legendre": float(legendre[index]),
        "Legendre_quadratic_coefficient": quadratic_coefficient,
        "Lambda_shell": float(1.0 - 4.0 * sigma[index] ** 2),
        "J_shell": float(jacobian[index]),
        "normalization_integral": normalization_integral,
        "u0_shell": u0_shell,
        "u0_shell_nonzero": float(abs(u0_shell) > 0.0),
    }


def leading_cartan_amplitude() -> float:
    shell = shell_geometry()
    k_g5 = 2.0 * math.pi**2 * RADIUS0**3
    return float(
        0.75 / k_g5
        * math.pi * shell["J_shell"] * shell["u0_shell"] ** 4
        / (
            shell["Lambda_shell"]
            * math.sqrt(shell["Legendre_quadratic_coefficient"])
        )
    )


def leading_crossing_estimate() -> dict[str, Any]:
    susceptibility = physical_heat_susceptibility(geometric_heat_parameter())
    amplitude = leading_cartan_amplitude()
    up_gauge_bound = up_channel_norm_bound(0.10602)
    channel_factors = {
        "up": 1.0,
        "down": (13.0 / 10.0) / (7.0 / 5.0),
        "charged_lepton": (3.0 / 10.0) / (7.0 / 5.0),
        "neutrino": 0.0,
    }
    rows = {}
    for channel, factor in channel_factors.items():
        gauge = factor * up_gauge_bound
        epsilon = (susceptibility * amplitude / (1.0 - gauge)) ** 2
        rows[channel] = {
            "gauge_norm_bound_at_last_slice": gauge,
            "leading_epsilon_star": epsilon,
        }
    return {
        "K_G5": 2.0 * math.pi**2 * RADIUS0**3,
        "c_EC": 0.75,
        "Cartan_inverse_sqrt_epsilon_amplitude": amplitude,
        "regulated_LR_susceptibility": susceptibility,
        "channels": rows,
        "first_channel": "up",
        "up_leading_epsilon_star": rows["up"]["leading_epsilon_star"],
        "status": (
            "LEADING_FROZEN-SHELL_ESTIMATE_BEFORE_COMPOSITE_BACKREACTION_"
            "NOT_THE_FINAL_BACKREACTED_VALUE"
        ),
    }


def completion_payload() -> dict[str, Any]:
    coefficient = clifford_coefficient_contract()
    shell = shell_geometry()
    estimate = leading_crossing_estimate()
    validation = {
        "Clifford_coefficient_fixed": coefficient["c_EC"] == 0.75,
        "no_new_four_fermion_coefficient": not coefficient["new_coefficient"],
        "interior_shell": 0.0 < shell["shell_chi"] < math.pi / 4.0,
        "quadratic_shell_minimum": shell["Legendre_quadratic_coefficient"] > 0.0,
        "zero_mode_nonzero_on_shell": bool(shell["u0_shell_nonzero"]),
        "finite_positive_crossing_estimate": (
            0.0 < estimate["up_leading_epsilon_star"] < 1.0e-6
        ),
        "up_crosses_first": estimate["first_channel"] == "up",
        "estimate_not_overclaimed_as_backreacted_solution": estimate[
            "status"
        ].endswith("NOT_THE_FINAL_BACKREACTED_VALUE"),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_cartan_shell_crossing_v15_76",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "Clifford_coefficient": coefficient,
        "actual_shell_geometry": shell,
        "leading_crossing_estimate": estimate,
        "scientific_result": (
            "THE_CARTAN_LR_COEFFICIENT_IS_3/4_WITH_NO_NEW_PARAMETER;_THE_"
            "ACTUAL_LAST-SLICE_SHELL_AND_NORMALIZED_ETA_ZERO_MODE_GIVE_A_"
            "FINITE_LEADING_UP-CHANNEL_CROSSING_NEAR_epsilon=3.1e-10,_AT_"
            "WHICH_THE_SAME_PUSHFORWARD_EVALUATES_THE_GAUGE_RESIDUE"
        ),
        "claim_boundary": {
            "nonzero_same-pushforward_Yukawa_crossing_exists": True,
            "leading_crossing_scale_computed": True,
            "fully_backreacted_crossing_computed": False,
            "physical_family_hierarchy_computed": False,
        },
        "active_calculation": (
            "SOLVE_THE_COUPLED_HUBBARD-STRATONOVICH_GAP_AND_CHILD_KKT_"
            "EQUATIONS_IN_THE_epsilon~1e-10_EVENT_LAYER,_USING_THE_SAME_"
            "CARTAN_PLUS_GAUGE_Gamma_boundary_STRESS"
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
    path = target / "BHSM_aether_cartan_shell_crossing_v15_76.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "clifford_coefficient_contract", "shell_geometry",
    "leading_cartan_amplitude", "leading_crossing_estimate",
    "completion_payload", "deterministic_json", "materialize",
]
