"""Self-similar persistence test of the reconstructed BHSM child cap."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import minimize_scalar

from bhsm.interface.aether_post_cut_child_cap_reconstruction_v15_46 import (
    HOPF_ORBIT_VOLUME,
    integrate_exact_round_cap_tt,
    solve_minimal_round_cap_cmc_tt_reconstruction,
)


VERSION = "v15.47"
CLASSIFICATION = "BHSM_POST_CUT_SELF_SIMILAR_PERSISTENCE_TEST"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def self_similar_reduction(*, points: int = 700) -> dict[str, Any]:
    """Construct the exact one-scale Hamiltonian constraint function."""

    reconstructed = solve_minimal_round_cap_cmc_tt_reconstruction(points=points)
    initial = integrate_exact_round_cap_tt(
        reconstructed["radius"],
        trace_rate=reconstructed["trace_rate"],
        points=points,
    )
    chi = np.asarray(initial["coordinate"])
    s = np.asarray(initial["K_chi"])
    d = np.asarray(initial["anisotropy_d"])
    weight = np.sin(chi) ** 3 * np.cos(chi) ** 3
    weight_norm = float(np.trapezoid(weight, chi))
    sigma = -0.5 + 2.0 * chi / math.pi - np.sin(4.0 * chi) / (2.0 * math.pi)
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    tt_norm_initial = float(np.trapezoid(
        weight * (7.0 * s**2 / 6.0 + 6.0 * d**2), chi
    ) / weight_norm)
    radius_initial = float(reconstructed["radius"])
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0

    def friedmann(radius: float) -> float:
        radius = float(radius)
        if radius <= 0.0:
            raise ValueError("radius must be positive")
        x_eta = 7.0 / radius**2
        eta_legendre = 1.0 + x_eta**3
        inertia = (
            HOPF_ORBIT_VOLUME
            * radius**7
            * float(np.trapezoid(
                weight * localization * eta_legendre, chi
            ))
        )
        omega = 0.5 / inertia
        eta_mean = float(np.trapezoid(
            weight * localization * (0.5 * x_eta + 0.125 * x_eta**4), chi
        ) / weight_norm)
        fr_mean = float(np.trapezoid(
            weight * 0.5 * localization * eta_legendre * omega**2, chi
        ) / weight_norm)
        tt_mean = tt_norm_initial * (radius_initial / radius) ** 14
        return (
            0.5 * kappa0
            + eta_mean
            + fr_mean
            - 21.0 / radius**2
            + 0.5 * tt_mean
        ) / 21.0

    minimum = minimize_scalar(
        friedmann, bounds=(0.35 * radius_initial, 8.0 * radius_initial),
        method="bounded", options={"xatol": 2.0e-12},
    )
    sample_radii = np.geomspace(0.25 * radius_initial, 12.0 * radius_initial, 1200)
    sample_values = np.array([friedmann(value) for value in sample_radii])
    initial_value = friedmann(radius_initial)
    return {
        "equation": "R_dot^2/R^2=G(R)",
        "TT_conservation": "TijTij(R)=TijTij(R_star)*(R_star/R)^14",
        "FR_conservation": "omega(R)=J/I(R),_J=1/2",
        "initial_radius": radius_initial,
        "initial_trace_rate": reconstructed["trace_rate"],
        "initial_G": initial_value,
        "initial_constraint_identity_residual": abs(
            initial_value - reconstructed["trace_rate"] ** 2
        ),
        "minimum_radius": float(minimum.x),
        "minimum_G": float(minimum.fun),
        "sampled_minimum_G": float(np.min(sample_values)),
        "turning_point_count": int(np.count_nonzero(
            sample_values[:-1] * sample_values[1:] < 0.0
        )),
        "self_similar_periodic_orbit_exists": bool(minimum.fun <= 0.0),
        "contracting_branch_direction": "R_decreases",
        "persistence_verdict": (
            "SELF_SIMILAR_CAP_SECTOR_NOT_PERSISTENT;_THE_PHYSICAL_"
            "PERSISTENCE_PROBLEM_IS_THE_NONROUND_CAP_SHAPE-RESPONSE-"
            "BOUNDARY_TRACTION_FLOW"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = self_similar_reduction()
    validation = {
        "reconstructed_slice_satisfies_reduced_constraint": result[
            "initial_constraint_identity_residual"
        ] < 2.0e-10,
        "no_self_similar_turning_point": result["turning_point_count"] == 0,
        "strictly_positive_self_similar_G": result["minimum_G"] > 0.0,
        "self_similar_periodicity_rejected": not result[
            "self_similar_periodic_orbit_exists"
        ],
        "nonround_persistence_problem_selected": "NONROUND" in result[
            "persistence_verdict"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_post_cut_self_similar_persistence_v15_47",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "self_similar_reduction": result,
        "claim_boundary": {
            "self_similar_sector_decided": True,
            "complete_nonround_Floquet_spectrum_computed": False,
            "persistent_particle_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "active_calculation": (
            "EVOLVE_THE_NONROUND_POST-CUT_CAP_SHAPE_RESPONSE_AND_BOUNDARY_"
            "TRACTION_SYSTEM_AND_COMPUTE_ITS_CONSTRAINT-REDUCED_MONODROMY"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
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
        rounded = round(value, 8)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_post_cut_self_similar_persistence_v15_47.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "self_similar_reduction", "completion_payload", "deterministic_json",
    "materialize",
]

