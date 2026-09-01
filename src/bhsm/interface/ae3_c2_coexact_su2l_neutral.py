"""Current-C2 lowest-Weyl neutral SU(2)_L source attachment."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_coexact_hypercharge import (
    lowest_weyl_coexact_hypercharge_source_jet,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_LOWEST_WEYL_COEXACT_SU2L_NEUTRAL_SOURCE_JET"


def weak_neutral_representation_ledger() -> dict[str, Any]:
    rows = {
        "Q_L": {"multiplicity_each": 3, "T3_eigenvalues": (0.5, -0.5), "Y": 1 / 6},
        "L_L": {"multiplicity_each": 1, "T3_eigenvalues": (0.5, -0.5), "Y": -0.5},
        "u_c": {"multiplicity_each": 3, "T3_eigenvalues": (0.0,), "Y": -2 / 3},
        "d_c": {"multiplicity_each": 3, "T3_eigenvalues": (0.0,), "Y": 1 / 3},
        "e_c": {"multiplicity_each": 1, "T3_eigenvalues": (0.0,), "Y": 1.0},
        "nu_c": {"multiplicity_each": 1, "T3_eigenvalues": (0.0,), "Y": 0.0},
    }
    trace_t3 = sum(
        row["multiplicity_each"] * sum(row["T3_eigenvalues"]) for row in rows.values()
    )
    trace_t3_squared = sum(
        row["multiplicity_each"] * sum(value * value for value in row["T3_eigenvalues"])
        for row in rows.values()
    )
    trace_y_t3 = sum(
        row["multiplicity_each"] * row["Y"] * sum(row["T3_eigenvalues"])
        for row in rows.values()
    )
    return {
        "one_family_rows": rows,
        "one_family_T3_trace": trace_t3,
        "one_family_T3_square_trace": trace_t3_squared,
        "three_family_T3_square_trace": 3.0 * trace_t3_squared,
        "one_family_Y_T3_trace": trace_y_t3,
        "family_factor": "I3",
        "right_singlets_are_T3_neutral": True,
        "structural_electromagnetic_generator": "Q_em=T3+Y_BH",
    }


def lowest_weyl_coexact_su2l_neutral_source_jet(
    *, proper_durations: np.ndarray, inverse_radii: np.ndarray,
    source_profile: np.ndarray, chirality: int,
) -> dict[str, Any]:
    jet = lowest_weyl_coexact_hypercharge_source_jet(
        proper_durations=proper_durations,
        inverse_radii=inverse_radii,
        source_profile=source_profile,
        chirality=chirality,
    )
    jet.update({
        "classification": CLASSIFICATION,
        "source_kind": "SPATIAL_COEXACT_SU2L_NEUTRAL_T3",
        "internal_generator": "T3=diag(1/2,-1/2)_on_Q_L_and_L_L;_zero_on_singlets",
        "physical_photon_identified": False,
    })
    return jet


def neutral_source_pair_ledger() -> dict[str, Any]:
    return {
        "current_C2_JY_source_attached": True,
        "current_C2_J3_source_attached": True,
        "both_sources_share_lowest_Weyl_coexact_C2_domain": True,
        "Q_em_structural_generator_available": True,
        "neutral_Hessian_null_direction_derived": False,
        "fields_and_currents_rotated_to_A_Z": False,
        "physical_photon_vertex_derived": False,
        "prediction_emitted": False,
    }


__all__ = [
    "ACTION_VERSION", "CLASSIFICATION",
    "lowest_weyl_coexact_su2l_neutral_source_jet",
    "neutral_source_pair_ledger", "weak_neutral_representation_ledger",
]
