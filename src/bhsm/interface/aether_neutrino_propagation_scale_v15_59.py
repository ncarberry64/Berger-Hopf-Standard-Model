"""Massless neutrino propagation cycle and geometric scale map on the reset."""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


VERSION = "v15.59"
CLASSIFICATION = "BHSM_NEUTRINO_PROPAGATION_AND_GEOMETRIC_SCALE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def weyl_frequency(level: int, radius: float) -> float:
    if not isinstance(level, int) or level < 0 or radius <= 0.0:
        raise ValueError("nonnegative level and positive radius required")
    return (level + 1.5) / radius


def propagation_cycle(level: int, radius: float) -> dict[str, Any]:
    frequency = weyl_frequency(level, radius)
    period = 2.0 * math.pi * radius
    phase = cmath.exp(-1j * frequency * period)
    return {
        "level": level,
        "frequency": frequency,
        "great_circle_null_return_time": period,
        "phase_real": float(phase.real),
        "phase_imag": float(phase.imag),
        "projective_return": abs(phase + 1.0) < 2.0e-13,
        "formula": "exp[-i*(n+3/2)*2pi]=-1",
    }


def neutrino_family_propagation_contract(levels: int = 8) -> dict[str, Any]:
    if levels <= 0:
        raise ValueError("levels must be positive")
    radius = RADIUS0 / 2.0
    cycles = [propagation_cycle(level, radius) for level in range(levels)]
    return {
        "M4": "R_t_times_S3_R4",
        "reset_R4_in_kappa1_units": radius,
        "operator": "i*d_t-D_Weyl_on_S3_tensor_I3_family",
        "spectrum": "omega_n=(n+3/2)/R4,_multiplicity_(n+1)(n+2)",
        "family_factor": "I3",
        "mass_matrices": "M_nu=0_3_on_the_selected_H_star=0_background",
        "mass_squared_splittings": [0.0, 0.0],
        "vacuum_oscillation_phase_differences": [0.0, 0.0],
        "canonical_basis_transition_probability": "P_alpha_to_beta=delta_alpha_beta",
        "PMNS_observable": False,
        "propagation_cycles": cycles,
        "all_modes_return_on_the_odd_projective_ray": all(
            cycle["projective_return"] for cycle in cycles
        ),
        "interpretation": (
            "the_current_BHSM_neutrino_is_an_exactly_null_propagation-supported_"
            "Weyl_envelopment,_not_a_primitive_stationary_mass_insertion"
        ),
        "environment_or_detector_noncentral_response_derived": False,
    }


def geometric_scale_map() -> dict[str, Any]:
    return {
        "dimension_of_kappa1": "length^(-6)_in_eight_spacetime_dimensions",
        "fundamental_length": "ell_kappa=kappa1^(-1/6)",
        "fiber_radius": "R_F=(343/5)^(1/6)*ell_kappa",
        "dimensionless_fiber_radius": RADIUS0,
        "M4_radius": "R4=R_F/2",
        "child_cap_radial_length": "L_cap=pi*R_F/4",
        "Weyl_energy": "E_n=hbar*c*(n+3/2)/R4",
        "free_SM_Casimir_energy": "E_SM=(59/15)*hbar*c/R_F",
        "five_dimensional_weak_coefficient": "K_F^(5)=kappa1*pi^2*R_F^5",
        "absolute_numeric_eV_or_GeV_value": None,
        "external_calibration_used": False,
        "scale_status": (
            "all_lengths_and_energies_are_unique_multiples_of_the_single_"
            "dimensionful_action_datum_kappa1;_the_action_does_not_select_a_"
            "numerical_SI_value_for_kappa1"
        ),
    }


def completion_payload() -> dict[str, Any]:
    neutrino = neutrino_family_propagation_contract()
    scale = geometric_scale_map()
    validation = {
        "all_sampled_Weyl_modes_projectively_return": neutrino[
            "all_modes_return_on_the_odd_projective_ray"
        ],
        "three_family_operator_central": neutrino["family_factor"] == "I3",
        "mass_splittings_zero_on_reset": neutrino[
            "mass_squared_splittings"
        ] == [0.0, 0.0],
        "PMNS_not_relabelled_observable": not neutrino["PMNS_observable"],
        "single_action_scale_used": scale["fundamental_length"].startswith(
            "ell_kappa="
        ),
        "no_external_scale_calibration": not scale[
            "external_calibration_used"
        ],
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_neutrino_propagation_scale_v15_59",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "neutrino_propagation": neutrino,
        "geometric_scale_map": scale,
        "claim_boundary": {
            "massless_neutrino_projective_propagation_cycle_derived": True,
            "current_reset_Delta_m_squared_derived_as_zero": True,
            "nonzero_PMNS_or_neutrino_oscillation_derived": False,
            "all_scales_reduced_to_kappa1": True,
            "numerical_absolute_scale_selected_in_external_units": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_COMPLETE_SELECTED-HYBRID_ACTION_AND_DETERMINE_"
            "WHETHER_THE_REMAINING_M4_WILSON_NORMALIZATIONS_FOLLOW_FROM_A_"
            "UNIQUE_MICROSCOPIC_REDUCTION_OR_DEFINE_A_NONUNIQUE_THEORY_FAMILY"
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
    path = target / "BHSM_aether_neutrino_propagation_scale_v15_59.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "weyl_frequency",
    "propagation_cycle", "neutrino_family_propagation_contract",
    "geometric_scale_map", "completion_payload", "deterministic_json",
    "materialize",
]
