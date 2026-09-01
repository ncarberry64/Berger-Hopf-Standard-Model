"""Current-C2 coexact gauge form shape with fail-closed normalization."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.aether_forward_c2_finite_core_descriptor import (
    assemble_finite_core_descriptor,
)
from bhsm.interface.aether_nonabelian_coexact_vertex_v16_03 import (
    coexact_curl_basis,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_COEXACT_GAUGE_FORM_SHAPE_OPEN_LORENTZIAN_RESIDUE"


def lowest_coexact_gauge_form_shape(
    *, log_radii: np.ndarray, proper_durations: np.ndarray
) -> dict[str, Any]:
    """Assemble the n=0 coexact one-form pencil on the current C2 geometry.

    The exact S3 curl spectrum at level zero is ``(+2,+2,+2)``.  Each
    component therefore has form ``|a'|^2+4 R4^-2 |a|^2``.  The returned
    object fixes this differential form and its BRST/coexact multiplicity but
    deliberately leaves the one Lorentzian Maxwell residue unevaluated.
    """

    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    decomposition = coexact_curl_basis(0)
    curl_values = np.asarray(decomposition["coexact_eigenvalues"], dtype=float)
    if curl_values.shape != (3,) or not np.allclose(curl_values, 2.0, atol=1.0e-13):
        raise ValueError("unexpected n=0 coexact curl spectrum")
    unit = assemble_finite_core_descriptor(
        log_radii=x,
        proper_durations=h,
        channel="scalar",
        unit_channel_value=2.0,
    )
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "angular_level": 0,
        "coexact_dimension": int(decomposition["coexact_dimension"]),
        "longitudinal_dimension": int(decomposition["longitudinal_dimension"]),
        "curl_eigenvalues": curl_values,
        "form": "integral_dt_(|partial_t_a_T|^2+4*R4^-2*|a_T|^2)",
        "component_pencil": unit,
        "K_diagonal_blocks": unit["K_diagonal"][:, None, None]
        * np.eye(3)[None, :, :],
        "K_off_diagonal_blocks": unit["K_off_diagonal"][:, None, None]
        * np.eye(3)[None, :, :],
        "M_diagonal_blocks": unit["M_diagonal"][:, None, None]
        * np.eye(3)[None, :, :],
        "M_off_diagonal_blocks": unit["M_off_diagonal"][:, None, None]
        * np.eye(3)[None, :, :],
        "BRST_longitudinal_sector_removed_by_coexact_projection": True,
        "overall_Lorentzian_Maxwell_residue_attached": False,
        "physical_propagator_normalized": False,
        "explicit_inverse_formed": False,
    }


def gauge_normalization_interface() -> dict[str, Any]:
    """State the exact distinction between form shape and physical residue."""

    return {
        "parent_Maxwell_action_owned": True,
        "parent_coefficient_relation": "K_F5/K_G5=R_F^2/2",
        "independent_gauge_normalization_allowed": False,
        "historical_spatial_coexact_response_available": True,
        "historical_Gauss_response_available": True,
        "historical_proper_time_response_available": True,
        "historical_responses_define_one_Lorentzian_coefficient": False,
        "current_C2_dynamic_frequency_response_available": True,
        "current_C2_dynamic_frequency_response_outcome": (
            "GAUGE_GHOST_HESSIAN_DERIVED__TEMPORAL_SPATIAL_RESIDUE_MISMATCH"
        ),
        "current_C2_broken_electroweak_saddle_available": False,
        "current_C2_physical_photon_residue_available": False,
        "exact_missing_object": (
            "ONE_ACTION_DERIVED_NONSINGULAR_BOUNDARY_OR_WENTZELL_TERM_OR_"
            "OTHER_EXISTING_PARENT_DOMAIN_MECHANISM_THAT_REMOVES_THE_CURRENT_"
            "TRANSVERSE_LORENTZ_RESIDUE_MISMATCH_WITHOUT_A_FREE_COEFFICIENT"
        ),
        "form_shape_may_be_used_for_finite_core_domain_and_gap_analysis": True,
        "form_shape_may_be_used_as_normalized_photon_propagator": False,
    }


def coexact_gauge_puzzle_ledger() -> dict[str, Any]:
    return {
        "advanced_sections": {
            "full_field_action": [
                "current_C2_n0_coexact_gauge_field_coordinate_form_shape",
                "exact_coexact_BRST_quotient_and_threefold_curl_plus2_multiplicity",
                "positive_inverse_free_finite_core_gauge_pencil",
                "current_C2_continuous_frequency_gauge_ghost_Hessian",
                "strict_temporal_spatial_residue_mismatch_certificate",
            ],
            "muon_magnetic_moment": [
                "current_C2_hypercharge_source_and_gauge_form_share_one_domain"
            ],
            "collisions_and_decays": [
                "current_C2_transverse_gauge_form_domain_precursor"
            ],
        },
        "open_join": (
            "action_derived_resolution_of_the_smooth_trace_residue_mismatch_"
            "then_broken_electroweak_neutral_mixing_and_maximal_exterior"
        ),
        "coexact_gauge_form_shape_derived": True,
        "normalized_photon_propagator_derived": False,
        "muon_magnetic_moment_derived": False,
        "prediction_emitted": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "coexact_gauge_puzzle_ledger",
    "gauge_normalization_interface",
    "lowest_coexact_gauge_form_shape",
]
