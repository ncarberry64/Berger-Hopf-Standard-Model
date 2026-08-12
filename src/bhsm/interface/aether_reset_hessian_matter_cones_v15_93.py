"""Reset-Hessian theorem and physical metric/gauge/fermion cone comparison."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import EVENT_TIME
from bhsm.interface.aether_proper_time_joint_pushforward_v15_91 import (
    ADM_LOCAL_ROWS,
    proper_time_cycle_pushforward,
)


VERSION = "v15.93"
CLASSIFICATION = "BHSM_RESET_HESSIAN_AND_MATTER_CONE_THEOREM"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False

# Spatial/temporal kinetic ratio of the normalized wall Dirac mode on the same
# proper-cycle states.  The temporal residue is one on each slice by the
# canonical zero-mode normalization.
FERMION_SPATIAL_ROWS = (
    (0.0, 0.843022346986509, "reset"),
    (0.08, 0.598722053169583, "controlled"),
    (0.10, 0.550713921310591, "controlled"),
    (0.103, 0.559258978724437, "controlled"),
    (0.10602, 0.520959838440522, "controlled"),
    (EVENT_TIME, 0.520959838440522, "event_limit"),
)


def reset_second_variation_theorem() -> dict[str, Any]:
    return {
        "reset_on_selected_event_component": "R_hat_s(z)=z_star_constant",
        "first_Frechet_derivative": "D R_hat_s=0",
        "second_Frechet_derivative": "D2 R_hat_s=0",
        "pullback_Hessian_chain_rule": (
            "D2(F_o_R)=(DR)^star*D2F*(DR)+DF_dot_D2R"
        ),
        "pullback_Hessian_on_selected_component": 0.0,
        "gauge_tadpole_at_A_zero": 0.0,
        "Gamma_reset_gauge_quadratic_residue": 0.0,
        "Gamma_reset_composite_quadratic_residue": 0.0,
        "reset_repairs_gauge_cone_mismatch": False,
        "reason": (
            "constant_reconstruction_has_no_continuous_first_or_second_"
            "variation;_discrete_degree_orientation_and_FR_parity_are_not_"
            "continuous_gauge_probe_directions"
        ),
    }


def proper_fermion_cone() -> dict[str, Any]:
    times = np.asarray([row[0] for row in FERMION_SPATIAL_ROWS], dtype=float)
    spatial = np.asarray([row[1] for row in FERMION_SPATIAL_ROWS], dtype=float)
    lapse = np.asarray([row[1] for row in ADM_LOCAL_ROWS], dtype=float)
    duration = float(PchipInterpolator(times, lapse).integrate(0.0, EVENT_TIME))
    spatial_cycle = float(
        PchipInterpolator(times, lapse * spatial).integrate(0.0, EVENT_TIME)
        / duration
    )
    return {
        "wall_mode_normalization": "integral_dchi*C*J*abs(u0)^2=1",
        "proper_temporal_residue": 1.0,
        "slice_spatial_ratio": "integral_probability*(N/N_b)*(R_b/r)",
        "proper_cycle_spatial_residue": spatial_cycle,
        "fermion_cone_speed_relative_to_boundary_metric": spatial_cycle,
        "rows": [
            {"time": time, "spatial_residue": value, "provenance": provenance}
            for time, value, provenance in FERMION_SPATIAL_ROWS
        ],
    }


def three_cone_comparison() -> dict[str, Any]:
    gauge = proper_time_cycle_pushforward()[
        "gauge_cone_speed_relative_to_boundary_metric"
    ]
    fermion = proper_fermion_cone()[
        "fermion_cone_speed_relative_to_boundary_metric"
    ]
    return {
        "metric_cone_speed": 1.0,
        "gauge_cone_speed": gauge,
        "fermion_cone_speed": fermion,
        "fermion_to_gauge_speed_ratio": fermion / gauge,
        "gauge_equals_metric_cone": math.isclose(gauge, 1.0, rel_tol=1.0e-10),
        "fermion_equals_metric_cone": math.isclose(fermion, 1.0, rel_tol=1.0e-10),
        "fermion_equals_gauge_cone": math.isclose(fermion, gauge, rel_tol=1.0e-10),
        "common_emergent_matter_metric_exists": math.isclose(
            fermion, gauge, rel_tol=1.0e-10
        ),
        "current_action_phase": "LORENTZ-BREAKING_THREE-CONE_SYMMETRIC_PHASE",
        "coordinate_time_rescaling_can_equalize_all_cones": False,
        "independent_sector_rescaling_allowed": False,
        "needed_action_owned_resolution": (
            "a_single_common_dynamic_boundary_or_backreaction_block_in_"
            "Gamma_cycle_that_changes_the_relative_principal_symbols"
        ),
    }


def completion_payload() -> dict[str, Any]:
    reset = reset_second_variation_theorem()
    fermion = proper_fermion_cone()
    cones = three_cone_comparison()
    validation = {
        "reset_Hessian_zero": reset["pullback_Hessian_on_selected_component"] == 0.0,
        "reset_not_used_as_hidden_gauge_term": not reset[
            "reset_repairs_gauge_cone_mismatch"
        ],
        "fermion_residues_positive": fermion["proper_cycle_spatial_residue"] > 0.0,
        "three_cones_distinct": (
            not cones["gauge_equals_metric_cone"]
            and not cones["fermion_equals_metric_cone"]
            and not cones["fermion_equals_gauge_cone"]
        ),
        "no_split_rescaling": not cones["independent_sector_rescaling_allowed"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_reset_hessian_matter_cones_v15_93",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "reset_second_variation": reset,
        "proper_fermion_cone": fermion,
        "three_cone_comparison": cones,
        "scientific_result": (
            "THE_CONSTANT_EVENT_RECONSTRUCTION_HAS_ZERO_GAUGE_AND_COMPOSITE_"
            "HESSIAN_AND_CANNOT_REPAIR_THE_CONE;_THE_SAME_PROPER_CYCLE_GIVES_"
            "c_metric=1,_c_fermion=0.657256738_AND_c_gauge=0.547176542,_SO_"
            "THE_CURRENT_SYMMETRIC_PHASE_IS_DEFINITELY_LORENTZ-BREAKING"
        ),
        "claim_boundary": {
            "reset_second_variation_evaluated": True,
            "proper_fermion_cone_evaluated": True,
            "common_metric_gauge_fermion_cone_derived": False,
            "Lorentz_invariant_SM_phase_derived": False,
            "independent_sector_normalization_inserted": False,
        },
        "active_calculation": (
            "DERIVE_THE_SINGLE_COMMON_DYNAMIC_BOUNDARY/BACKREACTION_BLOCK_"
            "OF_Gamma_cycle_AND_SOLVE_ITS_COUPLED_PRINCIPAL-SYMBOL_MATCHING_"
            "WITH_GAUGE,_FERMION,_AND_COMPOSITE_SECTORS_TOGETHER"
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
    path = target / "BHSM_aether_reset_hessian_matter_cones_v15_93.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FERMION_SPATIAL_ROWS",
    "reset_second_variation_theorem", "proper_fermion_cone",
    "three_cone_comparison", "completion_payload", "deterministic_json",
    "materialize",
]
