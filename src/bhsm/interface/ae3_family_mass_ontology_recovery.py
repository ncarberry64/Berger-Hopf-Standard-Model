"""Recover the BHSM harmonic/scale/relative-energy mass ontology into AE3.

The audit distinguishes a definition, a conditional spectral-semigroup mass
construction, and a current action-derived observable.  It does not promote
the historical conditional numbers or identify a raw internal eigenvalue with
physical mass.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, pi
from typing import Any


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "AE3_FAMILY_MASS_ONTOLOGY_AND_HOPF_SCALE_RECOVERY_AUDIT"


@dataclass(frozen=True)
class LineageRow:
    object_id: str
    preserved_result: str
    downgraded_or_missing: str
    same_current_AE3_action: bool
    same_current_C2_domain: bool
    physical_mass_evaluable: bool


def lineage_ledger() -> dict[str, Any]:
    """Trace the two mass lineages through the current AE3 boundary."""

    rows = (
        LineageRow(
            "V14_54_CYCLE_INVARIANT_MASS_CONTRACT",
            "MASS_IS_STABLE_REST_FRAME_COMPOSITE_MINUS_PARENT_RELATIVE_CHARGE_OR_FLOQUET_QUASI_ENERGY_WITH_E_REL=m*c^2",
            "DEFINITION_ONLY__NO_MATCHED_PARENT_Q_XI_STABLE_CYCLE_OR_EVALUATED_RELATIVE_CHARGE",
            False,
            False,
            False,
        ),
        LineageRow(
            "V15_54_ACTION_NORMALIZED_BERGER_SCALAR_SEEDS",
            "FROZEN_MODE_LABELS_AND_SCALAR_EIGENVALUES_ON_THE_RECONSTRUCTED_RADIUS",
            "SCALAR_SEED_NOT_A_SPINOR_POLE_OR_PARENT_RELATIVE_ENERGY",
            False,
            False,
            False,
        ),
        LineageRow(
            "V15_56_HYBRID_YUKAWA_MASS_SEMANTICS",
            "RAW_VERTICAL_LEVEL_IS_NOT_MASS_AND_FIBER_INVARIANT_OVERLAP_IS_I3",
            "LOCAL_OVERLAP_REDUCTION_DID_NOT_EVALUATE_MODE_DEPENDENT_TOTAL_PARENT_RELATIVE_ENERGY",
            False,
            False,
            False,
        ),
        LineageRow(
            "HISTORICAL_HOPF_BASE_HEAT_SEMIGROUP_DIMENSIONFUL_LEPTON_CANDIDATE",
            "EXP_MINUS_L_OVER_4PI_GIVES_NONFITTED_DECREASING_FAMILY_WEIGHTS_AND_A_CONDITIONAL_DIMENSIONFUL_TRIPLET",
            "UNIT_RESPONSE_TIME_PROFILE_RADIUS_PLANCK_TO_EW_LIFT_AND_TRACE_NORMALIZED_MASS_INSERTION_REMAIN_CONDITIONAL_AND_NOT_AE3_ATTACHED",
            False,
            False,
            False,
        ),
        LineageRow(
            "CURRENT_AE3_C2_FAMILY_MODE_TRANSPORT_AND_PRODUCT_DIRAC_BLOCK",
            "ALL_FROZEN_FIBERS_REACH_THE_ENCLOSURE_AND_THE_LOCAL_DYNAMIC_BLOCK_IS_I3_CENTRAL",
            "NO_MODE_RESOLVED_FULL_ACTION_ENERGY_Q_XI_MATCHED_PARENT_OR_FERMION_POLE",
            True,
            True,
            False,
        ),
    )
    return {
        "rows": [asdict(row) for row in rows],
        "mass_ontology_preserved": True,
        "raw_mode_eigenvalue_equals_mass_rejected": True,
        "local_I3_overlap_no_go_scope": "LOCAL_FIBER_INVARIANT_YUKAWA_REDUCTION_ONLY",
        "local_I3_overlap_proves_equal_total_parent_relative_energies": False,
        "historical_semigroup_candidate_present_in_corpus": True,
        "historical_semigroup_candidate_present_in_active_AE3_dependency_graph": False,
    }


def recovered_hopf_semigroup_candidate(
    *, squashing: float = 1.1570541357334329
) -> dict[str, Any]:
    """Reproduce the historical no-lepton-input semigroup weights.

    This is recovery of a stored conditional candidate, not a new prediction.
    """

    if squashing <= 0.0:
        raise ValueError("positive Berger squashing required")
    modes = ((0, 0), (5, 2), (9, 3))
    lambdas = []
    weights = []
    for k, j in modes:
        q = k - 2 * j
        value = k * (k + 2) + (squashing**2 - 1.0) * q**2
        lambdas.append(value)
        weights.append(exp(-value / (4.0 * pi)))
    return {
        "sector": "charged_lepton",
        "roles": ["heavy", "middle", "light"],
        "modes": [list(mode) for mode in modes],
        "squashing": squashing,
        "Berger_costs": lambdas,
        "heat_semigroup_weights": weights,
        "weight_order": "heavy>middle>light",
        "three_distinct_weights": len(set(weights)) == 3,
        "middle_over_heavy": weights[1] / weights[0],
        "light_over_heavy": weights[2] / weights[0],
        "measured_lepton_mass_used": False,
        "classification": "RECOVERED_HISTORICAL_CONDITIONAL_CANDIDATE",
        "is_positive_local_harmonic_energy": False,
        "is_contraction_response_weight": True,
        "equals_evaluated_parent_relative_energy": False,
    }


def missing_bridge_decomposition() -> dict[str, Any]:
    """State the exact current links without collapsing two routes into one."""

    relative_energy_route = [
        "CURRENT_C2_NORMALIZED_MODE_REALIZATION_PHI_f_IN_THE_COMPLETE_FIELD_DOMAIN",
        "ACTION_OWNED_PARENT_ONLY_DOMAIN_AND_MATCHED_PARENT_SECTION_AT_COMMON_DATA",
        "COMPLETE_COVARIANT_THETA_Q_XI_BOUNDARY_ENSEMBLE_AND_COUNTERTERMS",
        "MODE_RESOLVED_COMPOSITE_MINUS_PARENT_DELTA_H_XI_OR_STABLE_FLOQUET_CYCLE",
        "REST_FRAME_OR_SIMPLE_POLE_EQUIVALENCE_AND_ABSOLUTE_UNIT_MAP",
    ]
    semigroup_route = [
        "CURRENT_C2_DERIVATION_OF_THE_HOPF_BASE_RESPONSE_GENERATOR_AND_UNIT_RESPONSE_TIME",
        "ACTION_OWNERSHIP_OF_THE_PROFILE_RADIUS_AND_TRACE_NORMALIZED_CHARGED_SOURCE",
        "ACTION_OWNERSHIP_OF_THE_DIMENSIONFUL_HOPF_LIFT_ON_THE_CURRENT_BACKGROUND",
        "CURRENT_C2_BROKEN_SECTOR_INSERTION_AND_FERMION_SIMPLE_POLES",
        "PROOF_OF_EQUIVALENCE_TO_THE_V14_54_PARENT_RELATIVE_MASS_CONTRACT",
    ]
    return {
        "relative_energy_route": relative_energy_route,
        "semigroup_insertion_route": semigroup_route,
        "single_missing_numeric_radius_only": False,
        "why": (
            "A_RADIUS_SUPPLIES_DIMENSION_BUT_NOT_THE_MATCHED_REFERENCE_CHARGE_"
            "MODE_REALIZATION_BOUNDARY_GENERATOR_OR_POLE_EQUIVALENCE"
        ),
        "shared_bottleneck": (
            "CURRENT_C2_MODE_RESOLVED_ACTION_ENERGY_MAP_WITH_ITS_OWNED_"
            "DIMENSIONFUL_SCALE_AND_PHYSICAL_POLE_OR_RELATIVE_CHARGE_READOUT"
        ),
        "shortest_nonfabricated_next_unit": (
            "RECOVER_AND_TYPE_THE_HISTORICAL_HOPF_BASE_SEMIGROUP_SOURCE_"
            "RADIUS_AND_LIFT_IN_THE_AE3_C2_ACTION_INVENTORY;_IF_ANY_INPUT_"
            "FAILS_OWNERSHIP_STOP_THERE;_OTHERWISE_DERIVE_ITS_FERMION_POLE_"
            "AND_COMPARE_WITH_DELTA_H_XI"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "v14_54_mass_ontology_recovered": True,
        "historical_Hopf_semigroup_candidate_recovered": True,
        "historical_conditional_numbers_promoted": False,
        "current_AE3_family_mass_hierarchy_derived": False,
        "current_C2_parent_relative_energy_evaluated": False,
        "current_C2_physical_scale_link_complete": False,
        "raw_harmonic_level_relabelled_as_mass": False,
        "local_I3_overlap_misapplied_to_total_energy": False,
        "measured_mass_used": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "LineageRow",
    "claim_boundary",
    "lineage_ledger",
    "missing_bridge_decomposition",
    "recovered_hopf_semigroup_candidate",
]
