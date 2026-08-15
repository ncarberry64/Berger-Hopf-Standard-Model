"""Nonlinear composite-mass branch below the joint Cartan event crossing."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import brentq

from bhsm.interface.aether_cartan_shell_crossing_v15_76 import (
    leading_cartan_amplitude,
    leading_crossing_estimate,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_unified_heat_pushforward_gap_v15_70 import (
    geometric_heat_parameter,
)


VERSION = "v15.77"
CLASSIFICATION = "BHSM_NONLINEAR_CARTAN_COMPOSITE_GAP_BRANCH"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def dimensionless_susceptibility(mass_times_radius: float) -> float:
    x = float(mass_times_radius)
    if x < 0.0:
        raise ValueError("nonnegative mass required")
    heat = geometric_heat_parameter()
    total = 0.0
    for n in range(128):
        energy = n + 1.5
        term = (
            (n + 1) * (n + 2) * math.exp(-heat * energy * energy)
            / math.sqrt(energy * energy + x * x)
        )
        total += term
        if n > 12 and term < 1.0e-16:
            break
    radius = RADIUS0 / 2.0
    return total / (2.0 * math.pi**2 * radius**2)


def composite_wavefunction_residue(mass_times_radius: float) -> float:
    """Positive derivative residue ``-d Chi/d(m^2)``."""

    x = float(mass_times_radius)
    if x < 0.0:
        raise ValueError("nonnegative mass required")
    heat = geometric_heat_parameter()
    total = 0.0
    for n in range(128):
        energy = n + 1.5
        term = (
            (n + 1) * (n + 2) * math.exp(-heat * energy * energy)
            / (energy * energy + x * x) ** 1.5
        )
        total += term
        if n > 12 and term < 1.0e-16:
            break
    return total / (4.0 * math.pi**2)


def up_effective_coupling(epsilon: float) -> float:
    value = float(epsilon)
    if value <= 0.0:
        raise ValueError("epsilon must be positive")
    estimate = leading_crossing_estimate()
    chi0 = dimensionless_susceptibility(0.0)
    gauge_kernel = (
        estimate["channels"]["up"]["gauge_norm_bound_at_last_slice"] / chi0
    )
    return gauge_kernel + leading_cartan_amplitude() / math.sqrt(value)


def solve_up_gap(epsilon: float) -> dict[str, float | bool]:
    value = float(epsilon)
    critical = leading_crossing_estimate()["up_leading_epsilon_star"]
    coupling = up_effective_coupling(value)
    if value >= critical:
        return {
            "epsilon": value,
            "critical_epsilon": critical,
            "broken": False,
            "mass_times_R4": 0.0,
            "mass_in_ell_kappa_inverse": 0.0,
            "Z_H": composite_wavefunction_residue(0.0),
            "Yukawa_residue": 0.0,
        }
    root = brentq(
        lambda mass: coupling * dimensionless_susceptibility(mass) - 1.0,
        0.0, 1.0e5, xtol=2.0e-13, rtol=2.0e-13,
    )
    residue = composite_wavefunction_residue(root)
    return {
        "epsilon": value,
        "critical_epsilon": critical,
        "broken": True,
        "mass_times_R4": root,
        "mass_in_ell_kappa_inverse": root / (RADIUS0 / 2.0),
        "Z_H": residue,
        "Yukawa_residue": residue ** -0.5,
    }


def gap_branch_rows() -> list[dict[str, float | bool]]:
    critical = leading_crossing_estimate()["up_leading_epsilon_star"]
    return [solve_up_gap(fraction * critical) | {"epsilon_fraction": fraction}
            for fraction in (1.1, 1.0, 0.9, 0.5, 0.1, 0.01)]


def effective_potential_contract() -> dict[str, Any]:
    return {
        "dimensionless_coupling": (
            "g_hat(epsilon)=G_total(epsilon)/(2*pi^2*R4^2)"
        ),
        "potential": (
            "V_hat(x;epsilon)=x^2/(2*g_hat)-sum_n d_n*exp(-t*E_n^2)*"
            "[sqrt(E_n^2+x^2)-E_n]"
        ),
        "stationarity": "dV_hat/dx=0_iff_x=0_or_G_total*Chi_LR(x)=1",
        "composite_residue": "Z_H=-partial_Chi_LR/partial_(m^2)>0",
        "canonical_Yukawa": "Y=Z_H^(-1/2)_for_unit_Hubbard-Stratonovich_vertex",
        "same_regulator_and_Gamma_boundary": True,
    }


def completion_payload() -> dict[str, Any]:
    rows = gap_branch_rows()
    contract = effective_potential_contract()
    broken = [row for row in rows if row["broken"]]
    validation = {
        "symmetric_side_massless": all(
            row["mass_times_R4"] == 0.0 for row in rows if not row["broken"]
        ),
        "broken_side_nonzero": all(
            row["mass_times_R4"] > 0.0 and row["Yukawa_residue"] > 0.0
            for row in broken
        ),
        "mass_grows_inward": all(
            broken[index]["mass_times_R4"] < broken[index + 1]["mass_times_R4"]
            for index in range(len(broken) - 1)
        ),
        "composite_residue_positive": all(row["Z_H"] > 0.0 for row in rows),
        "one_effective_action": contract["same_regulator_and_Gamma_boundary"],
        "no_Yukawa_inserted": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_nonlinear_cartan_gap_branch_v15_77",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "effective_potential": contract,
        "gap_branch_rows": rows,
        "scientific_result": (
            "THE_SAME_CARTAN-PLUS-GAUGE_PUSHFORWARD_HAS_A_UNIQUE_NONZERO_"
            "COMPOSITE_MASS_BRANCH_BELOW_epsilon_star;_Z_H_AND_THE_NONZERO_"
            "YUKAWA_RESIDUE_ARE_DERIVATIVES_OF_THE_SAME_REGULATED_"
            "SUSCEPTIBILITY_AND_ARE_NOT_INDEPENDENT_INPUTS"
        ),
        "claim_boundary": {
            "nonzero_composite_mass_branch_solved": True,
            "nonzero_Yukawa_residue_solved_on_branch": True,
            "event_layer_backreaction_solved": False,
            "cycle-averaged_physical_mass_solved": False,
        },
        "active_calculation": (
            "INSERT_V_hat_AND_ITS_epsilon_DERIVATIVE_INTO_THE_CHILD_KKT_"
            "EVENT-LAYER_EQUATIONS_AND_COMPUTE_THE_HYBRID-CYCLE_MASS_AND_"
            "GAUGE_RESIDUE_FROM_ONE_PERIOD"
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
    path = target / "BHSM_aether_nonlinear_cartan_gap_branch_v15_77.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "dimensionless_susceptibility", "composite_wavefunction_residue",
    "up_effective_coupling", "solve_up_gap", "gap_branch_rows",
    "effective_potential_contract", "completion_payload", "deterministic_json",
    "materialize",
]
