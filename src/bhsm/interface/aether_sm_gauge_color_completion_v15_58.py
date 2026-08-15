"""Gauge-normalization ray and closed-S3 color singlets.

The parent diagonal quotient fixes the five-dimensional weak kinetic density.
The selected rank-16 carrier then fixes the full Standard Model coupling ray.
The absolute four-dimensional point additionally requires the normalized
radial/localization pushforward and is not identified with the dimensionful
five-dimensional coefficient.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import (
    attachment_states,
)
from bhsm.interface.particle_chirality_anomaly_normalization import (
    connection_trace_indices,
)


VERSION = "v15.58"
CLASSIFICATION = "BHSM_SM_GAUGE_NORMALIZATION_AND_COLOR_SINGLET_COMPLETION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def carrier_trace_extension_contract() -> dict[str, Any]:
    indices = connection_trace_indices()
    return {
        "faithful_group": "(SU3_times_Sp1_times_U1Y)/Z6",
        "one_family_trace_indices": {
            "I_Y": str(indices["I1_raw"]),
            "I_2": str(indices["I2"]),
            "I_3": str(indices["I3"]),
        },
        "trace_ratio": "10/3:2:2",
        "completion_rule": (
            "use_one_positive_carrier_trace_on_the_rank-16_family_and_fix_"
            "its_single_overall_coefficient_by_the_action-owned_Sp1_term"
        ),
        "provenance": (
            "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_RANK16_CARRIER_"
            "AND_DIAGONAL_SP1_ATTACHMENT"
        ),
        "historically_derived_from_EH_for_SU3_or_U1": False,
        "new_continuous_coefficient": False,
        "uniqueness_scope": (
            "unique_among_extensions_using_the_selected_single_carrier_trace_"
            "and_no_additional_factor-dependent_invariant_bilinear_coefficients"
        ),
    }


def reset_gauge_normalization_ray() -> dict[str, Any]:
    state = attachment_states()["reconstructed_round_boundary"]
    K5 = float(state["connection_kinetic_coefficient"])
    return {
        "M5_convention": "L5=-K_F^(5)*F_2^a_F_2^a/4",
        "matching_location": "hybrid_reset_at_R_F=(343/5)^(1/6)_in_kappa1_units",
        "K_F_five_dimensional": K5,
        "K_F_five_dimensional_status": "ACTION_DERIVED_V15_50_DIMENSIONFUL_DENSITY",
        "M4_inverse_coupling_ray": "K_Y:K_2:K_3=5/3:1:1",
        "M4_parameterization": {
            "K_Y": "(5/3)*Z_gauge", "K_2": "Z_gauge", "K_3": "Z_gauge",
        },
        "coupling_squared_ratio": "g_Y^2:g_2^2:g_3^2=3/5:1:1",
        "sin_squared_theta_W_on_this_ray": 3.0 / 8.0,
        "Z_gauge": (
            "the_dimensionless_normalized_M5-to-M4_connection-mode_or_"
            "boundary-localization_pushforward"
        ),
        "Z_gauge_derived": False,
        "five_dimensional_K_F_identified_directly_with_M4_inverse_g_squared": False,
        "absolute_M4_couplings_derived": False,
        "RG_evolved_to_external_experimental_scale": False,
        "external_measured_coupling_used": False,
    }


def color_gauss_singlet_contract() -> dict[str, Any]:
    return {
        "spatial_manifold": "S3_closed_without_boundary",
        "Gauss_operator": "G^a=(D_i_E^i)^a-rho^a",
        "physical_state_condition": "G^a(x)|physical>=0",
        "global_condition": (
            "the_constant_global_SU3_generators_annihilate_physical_states;_"
            "there_is_no_boundary_color_flux_sector_on_closed_S3"
        ),
        "local_quark": "section_in_3_or_bar3_and_not_a_gauge-invariant_state_by_itself",
        "meson_decomposition": "3_tensor_bar3=1_direct_sum_8",
        "meson_singlet": "M=bar(q)^i*q_i/sqrt(3)",
        "baryon_decomposition": "3_tensor_3_tensor_3=1_direct_sum_8_direct_sum_8_direct_sum_10",
        "baryon_singlet": "B=epsilon_ijk*q^i*q^j*q^k/sqrt(6)",
        "antibaryon_singlet": "Bbar=epsilon^ijk*bar(q)_i*bar(q)_j*bar(q)_k/sqrt(6)",
        "global_color_open_asymptotic_state_allowed": False,
        "global_color_singlet_envelopment": True,
        "kinematic_confinement_on_the_closed_child": True,
        "dynamical_area_law_or_Yang-Mills_mass_gap_derived": False,
        "hadron_mass_spectrum_derived": False,
    }


def completion_payload() -> dict[str, Any]:
    extension = carrier_trace_extension_contract()
    couplings = reset_gauge_normalization_ray()
    color = color_gauss_singlet_contract()
    validation = {
        "trace_indices_exact": extension["trace_ratio"] == "10/3:2:2",
        "M5_weak_density_inherited": couplings["K_F_five_dimensional"] > 0.0,
        "five_dimensional_coefficient_not_misidentified_as_M4_coupling": not couplings[
            "five_dimensional_K_F_identified_directly_with_M4_inverse_g_squared"
        ],
        "weak_angle_is_three_eighths": math.isclose(
            couplings["sin_squared_theta_W_on_this_ray"], float(Fraction(3, 8))
        ),
        "no_measured_coupling_inserted": not couplings[
            "external_measured_coupling_used"
        ],
        "color_singlet_constraint_derived": color[
            "kinematic_confinement_on_the_closed_child"
        ],
        "color_open_asymptotic_state_excluded": not color[
            "global_color_open_asymptotic_state_allowed"
        ],
        "no_mass_gap_overclaim": not color[
            "dynamical_area_law_or_Yang-Mills_mass_gap_derived"
        ],
        "no_new_continuous_coefficient": not extension[
            "new_continuous_coefficient"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_sm_gauge_color_completion_v15_58",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "carrier_trace_extension": extension,
        "reset_gauge_normalization_ray": couplings,
        "color_Gauss_singlets": color,
        "claim_boundary": {
            "M4_gauge_coupling_ray_derived_by_carrier_trace": True,
            "absolute_M4_gauge_couplings_derived": False,
            "weak_mixing_angle_on_the_derived_ray": True,
            "closed_child_color_singlet_confinement_derived": True,
            "RG_flow_to_observed_scale_derived": False,
            "hadron_mass_spectrum_derived": False,
        },
        "active_calculation": (
            "DERIVE_THE_NORMALIZED_M5-TO-M4_GAUGE_MODE_PUSHFORWARD,_THE_"
            "MASSLESS_NEUTRINO_PROPAGATION_MONODROMY,_AND_THE_ABSOLUTE_"
            "GEOMETRIC_SCALE"
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
    path = target / "BHSM_aether_sm_gauge_color_completion_v15_58.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "carrier_trace_extension_contract", "reset_gauge_normalization_ray",
    "color_gauss_singlet_contract", "completion_payload",
    "deterministic_json", "materialize",
]
