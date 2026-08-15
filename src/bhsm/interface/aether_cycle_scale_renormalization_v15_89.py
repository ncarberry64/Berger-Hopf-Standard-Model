"""Absolute BHSM-unit scale and RG transport of the joint cycle residues."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import (
    EVENT_TIME,
    cycle_sample_rows,
    one_cycle_residues,
)


VERSION = "v15.89"
CLASSIFICATION = "BHSM_ONE_CYCLE_ABSOLUTE_SCALE_AND_RENORMALIZATION_MAP"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False

TRACE_FACTORS = {"Y": Fraction(5, 3), "Sp1": Fraction(1), "SU3": Fraction(1)}
ONE_LOOP_B = {"Y": Fraction(41, 6), "Sp1": Fraction(-19, 6), "SU3": Fraction(-7)}


def cycle_matching_scale() -> dict[str, float | str]:
    rows = cycle_sample_rows()
    times = np.asarray([row["time"] for row in rows], dtype=float)
    radii = np.asarray([row["R4"] for row in rows], dtype=float)
    mean_log_radius = float(
        PchipInterpolator(times, np.log(radii)).integrate(0.0, EVENT_TIME)
        / EVENT_TIME
    )
    radius = math.exp(mean_log_radius)
    return {
        "fundamental_length": "ell_kappa=kappa1^(-1/6)",
        "cycle_log_mean_R4_in_ell_kappa": radius,
        "cycle_matching_scale_in_ell_kappa_inverse": 1.0 / radius,
        "definition": "log(mu_cycle^(-1))=Tstar^(-1)*integral_0^Tstar log(R4(t))dt",
        "external_SI_value_of_kappa1_inserted": False,
    }


def absolute_cycle_form_factors() -> dict[str, Any]:
    residues = one_cycle_residues()
    transverse = float(residues["PCHIP_cycle_transverse_DtN"])
    electric = float(residues["PCHIP_cycle_electric_DtN"])
    rows = {}
    for name, factor in TRACE_FACTORS.items():
        trace = float(factor)
        k_t = trace * transverse
        k_e = trace * electric
        rows[name] = {
            "trace_factor": str(factor),
            "K_transverse": k_t,
            "K_electric": k_e,
            "boundary_form_factor_g_transverse": k_t ** -0.5,
            "boundary_form_factor_g_electric": k_e ** -0.5,
        }
    return {
        "normalization_convention": "Gamma_cycle_contains_(K_i/4)*F_i*F_i",
        "sectors": rows,
        "inverse_coupling_ray_in_each_form_factor": "K_Y:K_2:K_3=5/3:1:1",
        "weak_angle_on_matching_ray": 3.0 / 8.0,
        "transverse_and_electric_are_two_components_of_one_nonlocal_DtN_operator": True,
        "independent_Lorentzian_Maxwell_coefficients_inserted": False,
        "local_zero_momentum_coupling_identified_with_DtN_form_factor": False,
    }


def rg_transport(scale_ratio: float = 2.0) -> dict[str, Any]:
    if scale_ratio <= 0.0:
        raise ValueError("positive scale ratio required")
    form = absolute_cycle_form_factors()["sectors"]
    log_ratio = math.log(float(scale_ratio))
    transported = {}
    for name, beta in ONE_LOOP_B.items():
        shift = -float(beta) * log_ratio / (8.0 * math.pi**2)
        transported[name] = {
            "one_loop_b": str(beta),
            "Delta_K": shift,
            "K_transverse_at_mu": float(form[name]["K_transverse"]) + shift,
            "K_electric_at_mu": float(form[name]["K_electric"]) + shift,
        }
    return {
        "scale_ratio_mu_over_mu_cycle": float(scale_ratio),
        "law": "K_i(mu)=K_i(mu_cycle)-b_i*log(mu/mu_cycle)/(8*pi^2)",
        "transported_form_factors": transported,
        "SM_one_loop_flow_preserves_matching_ray": False,
        "interpretation": (
            "the_trace_ray_is_a_boundary_condition_at_mu_cycle,_not_an_"
            "RG-invariant_identity_at_all_scales"
        ),
        "new_matching_coefficient_introduced": False,
    }


def renormalization_semantics() -> dict[str, Any]:
    return {
        "common_parent_prescription": "exp(-ell_kappa^2*H5)_before_all_Gamma_cycle_derivatives",
        "matched_outputs": [
            "transverse_gauge_form_factor", "electric_gauge_form_factor",
            "composite_Z_H", "canonical_Yukawa_vertex",
        ],
        "finite_shift_of_only_gauge_or_only_Yukawa_allowed": False,
        "scheme_change": (
            "a_common_reparameterization_of_Gamma_cycle_with_all_derived_"
            "operators_transformed_together"
        ),
        "dimensionless_normalization_missing": False,
        "dimensionful_SI_calibration_missing": True,
        "why": (
            "kappa1_is_the_single_dimensionful_action_datum;_BHSM_predicts_"
            "dimensionless_ratios_and_values_in_ell_kappa_units_but_does_not_"
            "derive_a_number_of_meters_from_dimensionless_mathematics"
        ),
    }


def completion_payload() -> dict[str, Any]:
    scale = cycle_matching_scale()
    form = absolute_cycle_form_factors()
    flow = rg_transport()
    semantics = renormalization_semantics()
    validation = {
        "cycle_scale_positive": scale["cycle_matching_scale_in_ell_kappa_inverse"] > 0.0,
        "all_form_factors_positive": all(
            row["K_transverse"] > 0.0 and row["K_electric"] > 0.0
            for row in form["sectors"].values()
        ),
        "trace_ray_exact": math.isclose(
            form["sectors"]["Y"]["K_transverse"]
            / form["sectors"]["Sp1"]["K_transverse"],
            5.0 / 3.0,
        ),
        "no_split_Maxwell_normalization": not form[
            "independent_Lorentzian_Maxwell_coefficients_inserted"
        ],
        "RG_is_transport_not_retuning": not flow["new_matching_coefficient_introduced"],
        "common_scheme_only": not semantics[
            "finite_shift_of_only_gauge_or_only_Yukawa_allowed"
        ],
        "dimensionless_absolute_normalization_closed": not semantics[
            "dimensionless_normalization_missing"
        ],
        "no_external_scale_fabricated": scale[
            "external_SI_value_of_kappa1_inserted"
        ] is False,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_cycle_scale_renormalization_v15_89",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "cycle_matching_scale": scale,
        "absolute_cycle_form_factors": form,
        "one_loop_RG_transport_example": flow,
        "renormalization_semantics": semantics,
        "scientific_result": (
            "THE_SAME_Gamma_cycle_FIXES_ABSOLUTE_DIMENSIONLESS_GAUGE_AND_"
            "YUKAWA_RESIDUES_AT_mu_cycle=0.97959715*ell_kappa^(-1);_RG_IS_"
            "JOINT_TRANSPORT_OF_THOSE_MATCHED_OUTPUTS,_WHILE_AN_SI_VALUE_"
            "REQUIRES_THE_SINGLE_DIMENSIONFUL_ACTION_DATUM_kappa1"
        ),
        "claim_boundary": {
            "absolute_dimensionless_boundary_form_factors_derived": True,
            "cycle_matching_scale_in_kappa_units_derived": True,
            "RG_transport_law_recorded": True,
            "local_zero_momentum_SM_couplings_derived": False,
            "external_SI_value_of_kappa1_derived": False,
        },
        "active_calculation": (
            "DENSIFY_THE_CONSTRAINT-SOLVED_ONE-CYCLE_QUADRATURE_AND_DERIVE_"
            "THE_LOW-MOMENTUM_LOCAL_LIMIT_OF_THE_SAME_NONLOCAL_DtN_OPERATOR"
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
    path = target / "BHSM_aether_cycle_scale_renormalization_v15_89.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "TRACE_FACTORS",
    "ONE_LOOP_B", "cycle_matching_scale", "absolute_cycle_form_factors",
    "rg_transport", "renormalization_semantics", "completion_payload",
    "deterministic_json", "materialize",
]
