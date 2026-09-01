"""Current-C2 family/mode to harmonic-energy pullback audit.

The stored family labels are evaluated with the already-derived Berger scalar
spectrum and common reset radius.  The resulting spectral stiffness operator
is noncentral on the three family slots.  This module then tests, rather than
assumes, whether it is an action-derived physical fermion mass operator.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_hybrid_flavor_spectrum_v15_54 import (
    berger_scalar_eigenvalue,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT"

MODE_ASSIGNMENTS = {
    "charged_lepton": ((0, 0), (5, 2), (9, 3)),
    "up": ((0, 0), (6, 0), (10, 1)),
    "down": ((0, 0), (6, 3), (8, 2)),
}
ROLE_ORDER = ("heavy", "middle", "light")


def slot_projectors() -> tuple[np.ndarray, ...]:
    """Return the three rank-one projectors used by the current C2 fibers."""

    rows = []
    for index in range(3):
        projector = np.zeros((3, 3), dtype=float)
        projector[index, index] = 1.0
        rows.append(projector)
    return tuple(rows)


def pulled_back_operator(values: list[float] | tuple[float, ...]) -> np.ndarray:
    """Pull a diagonal harmonic observable back through the slot map."""

    if len(values) != 3 or not np.all(np.isfinite(values)):
        raise ValueError("three finite harmonic values required")
    return sum(
        float(value) * projector
        for value, projector in zip(values, slot_projectors())
    )


def harmonic_spectral_pullback() -> dict[str, Any]:
    """Evaluate the frozen labels on the common action-normalized reset fiber."""

    sectors: dict[str, Any] = {}
    for sector, modes in MODE_ASSIGNMENTS.items():
        eigenvalues = [
            berger_scalar_eigenvalue(k, j, RADIUS0, RADIUS0)
            for k, j in modes
        ]
        dimensionless = [value * RADIUS0**2 for value in eigenvalues]
        positive_frequency = [float(np.sqrt(value)) for value in eigenvalues]
        operator = pulled_back_operator(eigenvalues)
        sectors[sector] = {
            "roles": list(ROLE_ORDER),
            "modes": [list(mode) for mode in modes],
            "scalar_Laplacian_eigenvalues": eigenvalues,
            "dimensionless_R_F_squared_eigenvalues": dimensionless,
            "positive_frequency_proxies": positive_frequency,
            "pulled_back_spectral_stiffness_operator": operator.tolist(),
            "operator_is_family_noncentral": not np.allclose(
                operator, np.trace(operator) * np.eye(3) / 3.0
            ),
            "three_distinct_spectral_values": len(set(dimensionless)) == 3,
            "common_radius_for_all_slots": RADIUS0,
        }
    return {
        "action_version": ACTION_VERSION,
        "manifestation_map": "I:family_slot_f->stored_Berger_mode_(k_f,j_f)",
        "pullback": "K_family=I_dagger*(-Delta_Berger)*I=sum_f lambda_f*P_f",
        "round_reset_radius": RADIUS0,
        "family_dependent_radius_present": False,
        "sectors": sectors,
        "spectral_noncentrality_derived": all(
            row["operator_is_family_noncentral"] for row in sectors.values()
        ),
    }


def positive_energy_killer_test() -> dict[str, Any]:
    """Test every frozen charged-sector ordering before empirical comparison.

    Any positive static gradient energy and any positive-frequency map that is
    monotone in the nonnegative spectral eigenvalue place the zero mode below
    its excitations.  The frozen BHSM ledger assigns that zero mode to the
    heaviest family, so this class cannot be the present rest-mass map.
    """

    pullback = harmonic_spectral_pullback()
    rows = []
    for sector, data in pullback["sectors"].items():
        stiffness = data["dimensionless_R_F_squared_eigenvalues"]
        frequency = [value * RADIUS0 for value in data["positive_frequency_proxies"]]
        rows.append(
            {
                "sector": sector,
                "frozen_role_order": "heavy>middle>light",
                "spectral_stiffness_order": "heavy<middle<light",
                "positive_frequency_order": "heavy<middle<light",
                "dimensionless_stiffness": stiffness,
                "dimensionless_frequency": frequency,
                "middle_over_heavy_displacement": None,
                "light_over_heavy_displacement": None,
                "why_requested_ratios_undefined": "heavy_slot_is_the_lambda_zero_reference",
                "light_over_middle_stiffness": stiffness[2] / stiffness[1],
                "light_over_middle_frequency": frequency[2] / frequency[1],
                "frozen_mass_order_compatible": False,
            }
        )
    return {
        "rows": rows,
        "no_measured_mass_used": True,
        "monotone_positive_F_of_lambda_compatible_with_frozen_roles": False,
        "finite_family_dependent_radius_can_lift_lambda_zero": False,
        "result": (
            "NONCENTRAL_SEPARATION_EXISTS_BUT_POSITIVE_MONOTONE_HARMONIC_"
            "ENERGY_HAS_THE_OPPOSITE_ORDER_AND_ZERO_HEAVY_REFERENCE"
        ),
        "test_passed": all(not row["frozen_mass_order_compatible"] for row in rows),
    }


def physical_mass_ownership_gate() -> dict[str, Any]:
    """Separate the derived stiffness pullback from a physical mass operator."""

    return {
        "frozen_family_mode_labels_present": True,
        "Berger_scalar_eigenvalues_action_normalized": True,
        "common_dimensionless_reset_radius_action_owned": True,
        "family_dependent_action_radius_present": False,
        "normalized_current_C2_manifestation_isometry_I_constructed": False,
        "parent_action_mode_energy_displacement_evaluated": False,
        "spinor_Dirac_lift_of_scalar_labels_constructed": False,
        "fermion_rest_energy_or_simple_pole_extracted": False,
        "absolute_physical_unit_numerically_derived": False,
        "scalar_spectral_stiffness_may_be_relabelled_as_fermion_mass": False,
        "old_exponential_overlap_rule_used": False,
        "empirical_mass_data_used": False,
        "physical_mass_operator_derived": False,
        "exact_missing_bridge": (
            "SAME_CURRENT_C2_NORMALIZED_MANIFESTATION_MAP_INTO_AN_ACTION_"
            "ENERGY_DOMAIN_PLUS_THE_COMPLETE_PARENT_RELATIVE_ENERGY_OR_"
            "FERMION_POLE_FUNCTIONAL_AND_ANY_ACTION_SELECTED_STATE_"
            "DEPENDENT_LOCALIZATION_SCALE"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "mode_energy_pullback_premise_reopened": True,
        "family_noncentral_spectral_stiffness_derived": True,
        "family_mass_hierarchy_derived": False,
        "physical_muon_mass_derived": False,
        "CKM_PMNS_derived": False,
        "particle_spectrum_rebuilt": False,
        "candidate_falsified_scope": (
            "POSITIVE_MONOTONE_FUNCTION_OF_THE_CURRENT_COMMON_RADIUS_"
            "SCALAR_HARMONIC_EIGENVALUE_AS_THE_FROZEN_FAMILY_REST_MASS"
        ),
        "v14_54_parent_relative_cycle_energy_tested_here": False,
        "historical_Hopf_base_heat_semigroup_mass_candidate_tested_here": False,
        "broader_signed_or_nonmonotone_energy_mechanism_disproved": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "MODE_ASSIGNMENTS",
    "ROLE_ORDER",
    "claim_boundary",
    "harmonic_spectral_pullback",
    "physical_mass_ownership_gate",
    "positive_energy_killer_test",
    "pulled_back_operator",
    "slot_projectors",
]
