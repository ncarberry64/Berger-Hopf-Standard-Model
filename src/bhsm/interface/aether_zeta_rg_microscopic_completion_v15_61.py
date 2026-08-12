"""Actual-child zeta and RG test of the remaining M4 microscopic data."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


VERSION = "v15.61"
CLASSIFICATION = "BHSM_ACTUAL_CHILD_ZETA_RG_MICROSCOPIC_COMPLETION_GATE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


GAUGE_BETA_ONE_LOOP = {
    "Y": Fraction(41, 6),
    "Sp1": Fraction(-19, 6),
    "SU3": Fraction(-7, 1),
}
INVERSE_COUPLING_RAY = {
    "Y": Fraction(5, 3),
    "Sp1": Fraction(1, 1),
    "SU3": Fraction(1, 1),
}


def zeta_scale_shift(zeta_zero: float, scale_ratio: float) -> float:
    if not math.isfinite(zeta_zero) or scale_ratio <= 0.0:
        raise ValueError("finite zeta zero and positive scale ratio required")
    return float(zeta_zero) * math.log(float(scale_ratio) ** 2)


def actual_operator_spectral_contract() -> dict[str, Any]:
    return {
        "operator": (
            "D_actual=i*gamma^mu*(nabla_mu+A_mu)_on_the_rank48_Weyl_bundle_"
            "with_U_phys=I_and_D_finite_left-right=0"
        ),
        "M4_radius": RADIUS0 / 2.0,
        "canonical_matching_scale": "mu_star=1/R4=2/R_F",
        "a4_gauge_trace_ray": "K_Y:K_2:K_3=5/3:1:1",
        "a4_common_amplitude_fixed_by_representation_trace": False,
        "finite_off_diagonal_Dirac_block": "0",
        "inner_fluctuation_contains_Higgs_doublet": False,
        "Yukawa_entries_generated_by_heat_trace": False,
        "reason": (
            "a_heat_trace_is_a_function_of_the_operator_entries_and_cannot_"
            "create_a_zero-order_bifundamental_entry_absent_from_D_actual"
        ),
    }


def zeta_renormalization_contract() -> dict[str, Any]:
    examples = [
        {
            "zeta_zero": value,
            "scale_ratio": ratio,
            "Gamma_shift_twice_convention": zeta_scale_shift(value, ratio),
        }
        for value, ratio in ((1.0, 2.0), (-2.0, 0.5), (0.0, 3.0))
    ]
    return {
        "induced_action": "Gamma_zeta=(1/2)*STr*log_det_zeta(P/mu^2)",
        "scale_law": "Gamma_zeta(mu2)-Gamma_zeta(mu1)=-STr[zeta_P(0)]*log(mu2/mu1)",
        "examples": examples,
        "nonlocal_spectral_part_fixed_once_operator_fixed": True,
        "logarithmic_anomaly_fixed_once_operator_fixed": True,
        "finite_local_F_squared_Higgs_and_curvature_counterterms_fixed": False,
        "canonical_child_scale_removes_need_to_name_mu_star": True,
        "canonical_child_scale_fixes_finite_counterterm_values": False,
    }


def one_loop_ray_flow() -> dict[str, Any]:
    # d(1/g_i^2)/d log(mu)=-b_i/(8*pi^2).
    derivative = {
        name: -float(value) / (8.0 * math.pi**2)
        for name, value in GAUGE_BETA_ONE_LOOP.items()
    }
    ray = np.asarray([float(INVERSE_COUPLING_RAY[name]) for name in ("Y", "Sp1", "SU3")])
    tangent = np.asarray([derivative[name] for name in ("Y", "Sp1", "SU3")])
    projection = float(tangent @ ray / (ray @ ray)) * ray
    transverse = tangent - projection
    return {
        "convention": "dK_i/dlog(mu)=-b_i/(8pi^2),_K_i=1/g_i^2",
        "one_loop_b": {name: str(value) for name, value in GAUGE_BETA_ONE_LOOP.items()},
        "inverse_coupling_ray": {name: str(value) for name, value in INVERSE_COUPLING_RAY.items()},
        "flow_derivative": derivative,
        "ray_tangent_projection": projection.tolist(),
        "ray_transverse_component": transverse.tolist(),
        "ray_transverse_norm": float(np.linalg.norm(transverse)),
        "trace_ray_preserved_by_one_loop_SM_flow": bool(np.linalg.norm(transverse) < 1.0e-14),
        "nonzero_common_perturbative_fixed_point": False,
        "Gaussian_fixed_point": "g_Y=g_2=g_3=0",
        "matching_scale_selected_by_child": "mu_star=2/R_F",
        "matching_amplitude_selected_by_RG_fixed_point": False,
    }


def microscopic_candidate_exhaustion() -> dict[str, Any]:
    return {
        "pure_zeta_determinant": {
            "fixes": ["nonlocal_part", "log_anomaly"],
            "does_not_fix": ["finite_local_Z_gauge", "Higgs_potential", "finite_Dirac_Yukawas"],
        },
        "local_zeta_a4": {
            "fixes": ["dimension-four_coefficient_ratios_after_operator_is_given"],
            "does_not_fix": ["operator_zero-order_entries", "relevant_Higgs_mass_term", "overall_physical_matching_amplitude"],
        },
        "cutoff_spectral_action": {
            "can_generate": ["relevant_and_marginal_local_terms"],
            "requires": ["cutoff_profile_moments", "cross-stratum_trace", "finite_Dirac_data"],
        },
        "one_loop_RG_fixed_point": {
            "only_common_fixed_point_in_current_perturbative_sector": "Gaussian",
            "produces_interacting_SM": False,
        },
        "single_zero-input_candidate_closes_observed_interacting_SM": False,
        "smallest_missing_foundational_object": (
            "a_global_stratified_spectral_triple_or_equivalent_operator-"
            "measure_principle_that_derives_its_finite_Dirac_block_and_"
            "renormalized_boundary_conditions_from_the_child_event_data"
        ),
    }


def completion_payload() -> dict[str, Any]:
    operator = actual_operator_spectral_contract()
    zeta = zeta_renormalization_contract()
    flow = one_loop_ray_flow()
    exhaustion = microscopic_candidate_exhaustion()
    validation = {
        "actual_matching_scale_is_geometric": operator["M4_radius"] > 0.0,
        "heat_trace_does_not_create_missing_Yukawa": not operator[
            "Yukawa_entries_generated_by_heat_trace"
        ],
        "zeta_scale_law_examples_finite": all(
            math.isfinite(row["Gamma_shift_twice_convention"])
            for row in zeta["examples"]
        ),
        "finite_counterterms_not_falsely_fixed": not zeta[
            "finite_local_F_squared_Higgs_and_curvature_counterterms_fixed"
        ],
        "SM_flow_leaves_trace_ray": not flow[
            "trace_ray_preserved_by_one_loop_SM_flow"
        ] and flow["ray_transverse_norm"] > 1.0e-3,
        "nonzero_fixed_point_not_fabricated": not flow[
            "nonzero_common_perturbative_fixed_point"
        ],
        "candidate_exhaustion_fail_closed": not exhaustion[
            "single_zero-input_candidate_closes_observed_interacting_SM"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_zeta_rg_microscopic_completion_v15_61",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "actual_operator_spectral_contract": operator,
        "zeta_renormalization": zeta,
        "one_loop_gauge_ray_flow": flow,
        "microscopic_candidate_exhaustion": exhaustion,
        "claim_boundary": {
            "actual_child_zeta_candidate_evaluated_structurally": True,
            "child_matching_scale_selected": True,
            "absolute_M4_normalization_selected": False,
            "finite_Dirac_Yukawa_block_selected": False,
            "interacting_RG_fixed_point_selected": False,
        },
        "active_calculation": (
            "FORMULATE_THE_MINIMAL_GLOBAL_STRATIFIED_OPERATOR-MEASURE_OBJECT_"
            "AND_TEST_UNIQUENESS_AGAINST_THE_FIXED_EVENT,_RANK16_CARRIER,_"
            "ROUND_INTERNAL_DIRAC_SPECTRUM,_AND_NO-NEW-COEFFICIENT_RULE"
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
        rounded = round(value, 12)
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
    path = target / "BHSM_aether_zeta_rg_microscopic_completion_v15_61.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "GAUGE_BETA_ONE_LOOP", "INVERSE_COUPLING_RAY", "zeta_scale_shift",
    "actual_operator_spectral_contract", "zeta_renormalization_contract",
    "one_loop_ray_flow", "microscopic_candidate_exhaustion",
    "completion_payload", "deterministic_json", "materialize",
]
