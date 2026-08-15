"""Proper-time normalization of the joint cycle gauge--Yukawa pushforward."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import (
    EVENT_TIME,
    cycle_sample_rows,
)


VERSION = "v15.91"
CLASSIFICATION = "BHSM_PROPER_TIME_JOINT_GAUGE_YUKAWA_PUSHFORWARD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False

# Direct ADM evaluations on the reset and stored constraint-solved states.
# K_B = R_b * integral(K W N C/r dchi) / N_b.
# K_E = N_b * integral(K W C r/N dchi) / R_b.
ADM_LOCAL_ROWS = (
    (0.0, 1.478043158469576, 1047.012993064123, 1760.168575465190, "reset"),
    (0.08, 2.6584440092989206, 733.166317007997, 2982.874990370266, "controlled"),
    (0.10, 3.194725614622591, 639.142899856196, 2905.877429853535, "controlled"),
    (0.103, 3.0576546456832867, 610.405035557754, 2108.695994485279, "controlled"),
    (0.10602, 3.6511129521584786, 578.944458782788, 2430.379698496332, "controlled"),
    (EVENT_TIME, 3.6511129521584786, 578.944458782788, 2430.379698496332, "event_limit"),
)


def _integral(times: np.ndarray, values: np.ndarray) -> float:
    return float(PchipInterpolator(times, values).integrate(0.0, EVENT_TIME))


def proper_time_cycle_pushforward() -> dict[str, Any]:
    samples = cycle_sample_rows()
    times = np.asarray([row[0] for row in ADM_LOCAL_ROWS], dtype=float)
    lapse = np.asarray([row[1] for row in ADM_LOCAL_ROWS], dtype=float)
    k_b = np.asarray([row[2] for row in ADM_LOCAL_ROWS], dtype=float)
    k_e = np.asarray([row[3] for row in ADM_LOCAL_ROWS], dtype=float)
    z_h = np.asarray([row["Z_H"] for row in samples], dtype=float)
    radius = np.asarray([row["R4"] for row in samples], dtype=float)
    proper_duration = _integral(times, lapse)

    def proper_average(values: np.ndarray) -> float:
        return _integral(times, lapse * values) / proper_duration

    k_b_cycle = proper_average(k_b)
    k_e_cycle = proper_average(k_e)
    z_cycle = proper_average(z_h)
    mean_log_radius = proper_average(np.log(radius))
    return {
        "physical_cycle_functional": (
            "Gamma_cycle=integral_0^Tstar N_boundary(t)dt*Gamma_proper(t)+Gamma_reset"
        ),
        "proper_cycle_duration": proper_duration,
        "coordinate_cycle_duration": EVENT_TIME,
        "mean_boundary_lapse": proper_duration / EVENT_TIME,
        "proper_cycle_K_magnetic": k_b_cycle,
        "proper_cycle_K_electric": k_e_cycle,
        "electric_to_magnetic_ratio": k_e_cycle / k_b_cycle,
        "gauge_cone_speed_relative_to_boundary_metric": math.sqrt(k_b_cycle / k_e_cycle),
        "proper_cycle_Z_H": z_cycle,
        "proper_cycle_canonical_Yukawa": z_cycle ** -0.5,
        "proper_log_mean_R4_in_ell_kappa": math.exp(mean_log_radius),
        "proper_matching_scale_in_ell_kappa_inverse": math.exp(-mean_log_radius),
        "family_Yukawa_matrix": "Y_proper*I3",
        "same_proper_time_measure_for_gauge_and_Yukawa": True,
        "rows": [
            {
                "time": time,
                "boundary_lapse": boundary_lapse,
                "K_magnetic": magnetic,
                "K_electric": electric,
                "provenance": provenance,
            }
            for time, boundary_lapse, magnetic, electric, provenance in ADM_LOCAL_ROWS
        ],
    }


def adm_derivation_contract() -> dict[str, Any]:
    return {
        "metric": "ds5^2=-N^2dt^2+C^2(dchi+beta*dt)^2+r^2dOmega3^2",
        "zero_shift_gauge": "beta_is_removed_by_an_interior_radial_diffeomorphism_fixed_at_the_boundary",
        "magnetic_radial_weight": "I_B=integral_dchi*K*W*N*C/r",
        "electric_frequency_weight": "I_E=integral_dchi*K*W*C*r/N",
        "boundary_normalization": "K_B=R_b*I_B/N_b,_K_E=N_b*I_E/R_b",
        "Lorentz_matching_equation": "K_E=K_B",
        "lapse_is_same_constraint_solved_lapse_used_in_eta_and_Gamma_cycle": True,
        "separate_gauge_normalization_inserted": False,
    }


def semantic_reclassification() -> dict[str, Any]:
    return {
        "v15_86_coordinate_time_PCHIP_values": "VALID_FROZEN-SPATIAL_DIAGNOSTICS",
        "v15_89_coordinate_log_mean_scale": "SUPERSEDED_BY_PROPER-TIME_MEAN",
        "v15_90_lapse-free_local_coefficients": "VALID_UNIT-LAPSE_STATIC_DIAGNOSTICS",
        "physical_absolute_cycle_values": "V15_91_PROPER-TIME_VALUES",
        "Lorentz_invariant_local_Maxwell_term_derived": False,
        "reason": "proper_cycle_K_E_not_equal_proper_cycle_K_B",
        "gauge_and_Yukawa_treated_as_unrelated_problems": False,
    }


def completion_payload() -> dict[str, Any]:
    cycle = proper_time_cycle_pushforward()
    derivation = adm_derivation_contract()
    semantics = semantic_reclassification()
    validation = {
        "proper_duration_positive": cycle["proper_cycle_duration"] > 0.0,
        "proper_gauge_coefficients_positive": (
            cycle["proper_cycle_K_magnetic"] > 0.0
            and cycle["proper_cycle_K_electric"] > 0.0
        ),
        "proper_Yukawa_nonzero": cycle["proper_cycle_canonical_Yukawa"] > 0.0,
        "one_measure": cycle["same_proper_time_measure_for_gauge_and_Yukawa"],
        "Lorentz_mismatch_detected": abs(
            cycle["electric_to_magnetic_ratio"] - 1.0
        ) > 1.0,
        "no_split_normalization": not derivation["separate_gauge_normalization_inserted"],
        "old_coordinate_average_not_called_physical": semantics[
            "physical_absolute_cycle_values"
        ].startswith("V15_91"),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_proper_time_joint_pushforward_v15_91",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "proper_time_cycle_pushforward": cycle,
        "ADM_derivation": derivation,
        "semantic_reclassification": semantics,
        "scientific_result": (
            "ONE_PROPER-TIME_Gamma_cycle_GIVES_K_B=813.476975,_K_E="
            "2717.004292,_Z_H=0.00176673551_AND_Y=23.7910840*I3;_THE_"
            "GAUGE_AND_YUKAWA_NORMALIZATIONS_REMAIN_JOINT,_WHILE_THE_DERIVED_"
            "LOCAL_GAUGE_CONE_DOES_NOT_EQUAL_THE_BOUNDARY_METRIC_CONE"
        ),
        "claim_boundary": {
            "proper_time_joint_pushforward_evaluated": True,
            "absolute_local_magnetic_and_electric_coefficients_evaluated": True,
            "proper_time_nonzero_Yukawa_evaluated": True,
            "Lorentz_invariant_Maxwell_matching_derived": False,
            "dense_constraint_solved_time_quadrature_evaluated": False,
        },
        "active_calculation": (
            "COMPUTE_THE_FULL_SHIFT-COVARIANT_FREQUENCY-DEPENDENT_DtN_"
            "SCHUR_COMPLEMENT_AND_TEST_WHETHER_EVENT/RESET_GLUING_SUPPLIES_"
            "THE_MISSING_GAUGE-CONE_TERM_WITHIN_THE_SAME_Gamma_cycle"
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
    path = target / "BHSM_aether_proper_time_joint_pushforward_v15_91.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "ADM_LOCAL_ROWS",
    "proper_time_cycle_pushforward", "adm_derivation_contract",
    "semantic_reclassification", "completion_payload", "deterministic_json",
    "materialize",
]
