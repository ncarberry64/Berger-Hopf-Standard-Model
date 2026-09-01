"""Transport the frozen BHSM overlap semigroup to the current C2 birth fiber.

The finite family operator is evaluated on the already reconstructed round
reset geometry.  This derives a current-C2 response *shape*.  It does not add
the missing intrinsic LR--Higgs coupling, choose a broken saddle, or relabel
the response eigenvalues as physical masses.
"""

from __future__ import annotations

from math import exp, isfinite, pi
from typing import Any

import numpy as np

from bhsm.interface.ae3_family_harmonic_energy_pullback import (
    MODE_ASSIGNMENTS,
    ROLE_ORDER,
    harmonic_spectral_pullback,
    pulled_back_operator,
    slot_projectors,
)
from bhsm.interface.master_action.topographic_profile_component_selection import (
    A_SQUASH,
)


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_BIRTH_HOPF_SEMIGROUP_SHAPE_TRANSPORT_THEOREM"
FROZEN_OVERLAP_WIDTH = 1.0 / (4.0 * pi)
FROZEN_INTERNAL_BERGER_SHAPE = A_SQUASH


def family_heat_semigroup(*, sector: str, response_time: float) -> dict[str, Any]:
    """Evaluate ``exp(-response_time*K_family)`` on one frozen family fiber."""

    if sector not in MODE_ASSIGNMENTS:
        raise ValueError(f"unknown charged sector: {sector}")
    time = float(response_time)
    if not isfinite(time) or time < 0.0:
        raise ValueError("finite nonnegative response time required")

    pullback = harmonic_spectral_pullback()["sectors"][sector]
    raw_costs = np.asarray(
        pullback["dimensionless_R_F_squared_eigenvalues"], dtype=float
    )
    integral_costs = np.rint(raw_costs)
    if not np.allclose(raw_costs, integral_costs, atol=2.0e-13, rtol=0.0):
        raise ArithmeticError("round-reset Berger costs did not recover integers")

    generator = pulled_back_operator(integral_costs.tolist())
    weights = np.exp(-time * integral_costs)
    operator = pulled_back_operator(weights.tolist())
    projectors = slot_projectors()
    commutators = [
        float(np.linalg.norm(operator @ projector - projector @ operator))
        for projector in projectors
    ]
    return {
        "action_version": ACTION_VERSION,
        "sector": sector,
        "roles": list(ROLE_ORDER),
        "modes": [list(mode) for mode in MODE_ASSIGNMENTS[sector]],
        "response_time": time,
        "round_reset_dimensionless_generator_costs": integral_costs.tolist(),
        "family_generator": generator.tolist(),
        "semigroup_weights": weights.tolist(),
        "semigroup_operator": operator.tolist(),
        "self_adjoint": bool(np.allclose(operator, operator.T, atol=0.0, rtol=0.0)),
        "positive_definite": bool(np.all(weights > 0.0)),
        "contraction": bool(np.max(weights) <= 1.0),
        "operator_norm": float(np.max(weights)),
        "commutator_norms_with_family_projectors": commutators,
        "commutes_with_all_family_projectors": max(commutators) == 0.0,
        "family_noncentral_for_positive_time": bool(
            time > 0.0 and len(set(weights.tolist())) == 3
        ),
        "frozen_role_order_recovered": bool(
            weights[0] > weights[1] > weights[2]
        ),
        "measured_mass_used": False,
    }


def current_c2_birth_overlap_operator() -> dict[str, Any]:
    """Derive the coefficient-free family response shape at the AE3 reset."""

    sectors = {
        sector: family_heat_semigroup(
            sector=sector, response_time=FROZEN_OVERLAP_WIDTH
        )
        for sector in MODE_ASSIGNMENTS
    }
    semigroup_checks: dict[str, Any] = {}
    for sector in MODE_ASSIGNMENTS:
        first = family_heat_semigroup(
            sector=sector, response_time=0.25 * FROZEN_OVERLAP_WIDTH
        )
        second = family_heat_semigroup(
            sector=sector, response_time=0.75 * FROZEN_OVERLAP_WIDTH
        )
        combined = np.asarray(sectors[sector]["semigroup_operator"])
        product = np.asarray(first["semigroup_operator"]) @ np.asarray(
            second["semigroup_operator"]
        )
        semigroup_checks[sector] = {
            "composition_residual": float(np.linalg.norm(combined - product)),
            "composition_holds": bool(
                np.allclose(combined, product, atol=2.0e-16, rtol=2.0e-15)
            ),
            "generator_identity": "dT/dt|_0=-K_family",
        }
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "background": "ACTUAL_RESET_GENERATED_ROUND_C2_BIRTH_FIBER",
        "frozen_overlap_width": FROZEN_OVERLAP_WIDTH,
        "frozen_overlap_width_formula": "1/(4*pi)",
        "operator_formula": "T_C2_birth=exp[-K_family/(4*pi)]",
        "sectors": sectors,
        "semigroup_checks": semigroup_checks,
        "all_sector_shapes_noncentral": all(
            row["family_noncentral_for_positive_time"] for row in sectors.values()
        ),
        "all_frozen_role_orders_recovered": all(
            row["frozen_role_order_recovered"] for row in sectors.values()
        ),
        "historical_squashing_reused": False,
        "current_round_geometry_used": True,
        "historical_dimensionful_mass_triplet_transported": False,
        "result": "CURRENT_C2_FINITE_FAMILY_HOPF_RESPONSE_SHAPE_DERIVED",
    }


def frozen_internal_semigroup_attachment() -> dict[str, Any]:
    """Attach the unchanged frozen internal Berger operator over current C2.

    The current C2 history is the carrier/base factor.  The Berger shape and
    family projectors live on the independent internal finite fiber, so the
    round birth geometry does not set ``a=1`` in this operator.
    """

    sectors: dict[str, Any] = {}
    for sector, modes in MODE_ASSIGNMENTS.items():
        costs = []
        for k, j in modes:
            q = k - 2 * j
            costs.append(
                k * (k + 2)
                + (FROZEN_INTERNAL_BERGER_SHAPE**2 - 1.0) * q**2
            )
        weights = np.exp(-FROZEN_OVERLAP_WIDTH * np.asarray(costs))
        operator = pulled_back_operator(weights.tolist())
        sectors[sector] = {
            "roles": list(ROLE_ORDER),
            "modes": [list(mode) for mode in modes],
            "frozen_internal_Berger_costs": costs,
            "frozen_mass_ratio_screen": weights.tolist(),
            "family_operator": operator.tolist(),
            "family_noncentral": len(set(weights.tolist())) == 3,
            "frozen_role_order_recovered": bool(
                weights[0] > weights[1] > weights[2]
            ),
        }

    spatial_dimension = 9
    spin_dimension = 2
    spatial_identity = np.eye(spatial_dimension)
    spin_identity = np.eye(spin_dimension)
    family_identity = np.eye(3)
    reset_lift = np.asarray(((0.0, 1.0), (1.0, 0.0)))
    reset = np.kron(spatial_identity, np.kron(reset_lift, family_identity))
    restriction = np.kron(
        np.diag([1.0] * 4 + [0.0] * 5),
        np.kron(spin_identity, family_identity),
    )
    carrier = np.kron(
        np.diag(np.linspace(0.0, 1.0, spatial_dimension)),
        np.kron(spin_identity, family_identity),
    )
    commutators: dict[str, Any] = {}
    for sector, row in sectors.items():
        family_operator = np.asarray(row["family_operator"])
        lifted = np.kron(
            spatial_identity, np.kron(spin_identity, family_operator)
        )
        commutators[sector] = {
            "with_reset": float(np.linalg.norm(lifted @ reset - reset @ lifted)),
            "with_enclosure_restriction": float(
                np.linalg.norm(lifted @ restriction - restriction @ lifted)
            ),
            "with_localization_carrier": float(
                np.linalg.norm(lifted @ carrier - carrier @ lifted)
            ),
        }

    return {
        "action_version": ACTION_VERSION,
        "base_factor": "ACTUAL_RESET_SELECTED_MAXIMAL_C2_HISTORY",
        "internal_factor": "FROZEN_BERGER_MODE_AND_FAMILY_FIBER",
        "factorization": "L2(C2)_carrier tensor (Spin x G_SM) tensor F_family",
        "frozen_internal_Berger_shape": FROZEN_INTERNAL_BERGER_SHAPE,
        "frozen_overlap_width": FROZEN_OVERLAP_WIDTH,
        "current_C2_round_reset_sets_internal_Berger_shape_to_one": False,
        "sectors": sectors,
        "commutator_certificate": commutators,
        "all_attachment_commutators_zero": all(
            max(row.values()) == 0.0 for row in commutators.values()
        ),
        "all_frozen_ratios_attached_unchanged": True,
        "measured_mass_used": False,
        "result": "FROZEN_INTERNAL_HOPF_RESPONSE_OPERATOR_ATTACHED_OVER_CURRENT_C2",
    }


def action_transport_ledger() -> dict[str, Any]:
    """Order the variational owners and stop at the first missing AE3 term."""

    rows = [
        {
            "order": 1,
            "object": "FROZEN_CHARGED_FAMILY_PROJECTORS_AND_MODE_LABELS",
            "current_C2_present": True,
            "current_AE3_action_owned": True,
            "status": "ATTACHED_AND_REUSED",
        },
        {
            "order": 2,
            "object": "FROZEN_INTERNAL_BERGER_GENERATOR_ON_FAMILY_FIBER",
            "current_C2_present": True,
            "current_AE3_action_owned": False,
            "status": "UPSTREAM_FROZEN_BHSM_OPERATOR_ATTACHED_BY_TENSOR_FACTORIZATION",
        },
        {
            "order": 3,
            "object": "FROZEN_BHSM_OVERLAP_WIDTH_S_EQUALS_1_OVER_4PI",
            "current_C2_present": True,
            "current_AE3_action_owned": False,
            "status": "REUSABLE_FROZEN_FRAMEWORK_RULE_NOT_AN_AE3_VARIATIONAL_TERM",
        },
        {
            "order": 4,
            "object": "INTRINSIC_M4_LR_HIGGS_COUPLING_WITH_T_C2",
            "current_C2_present": False,
            "current_AE3_action_owned": False,
            "status": "FIRST_VARIATIONAL_FAILURE",
        },
        {
            "order": 5,
            "object": "TRACE_NORMALIZED_CHARGED_SOURCE_AND_PROFILE_LIFT",
            "current_C2_present": False,
            "current_AE3_action_owned": False,
            "status": "HISTORICAL_CONDITIONAL_PACKAGE_NOT_AE3_TRANSPORTED",
        },
        {
            "order": 6,
            "object": "NONZERO_ACTION_SELECTED_HIGGS_OR_HS_SADDLE",
            "current_C2_present": False,
            "current_AE3_action_owned": False,
            "status": "DOWNSTREAM_BROKEN_SECTOR_FAILURE",
        },
        {
            "order": 7,
            "object": "MODE_RESOLVED_FERMION_SIMPLE_POLES",
            "current_C2_present": False,
            "current_AE3_action_owned": False,
            "status": "DOWNSTREAM_POLE_FAILURE",
        },
        {
            "order": 8,
            "object": "MATCHED_PARENT_DELTA_H_XI_EQUIVALENCE",
            "current_C2_present": False,
            "current_AE3_action_owned": False,
            "status": "DOWNSTREAM_RELATIVE_ENERGY_FAILURE",
        },
    ]
    return {
        "rows": rows,
        "kinematic_transport_closed_through": (
            "UNCHANGED_FROZEN_INTERNAL_MASS_RATIO_OPERATOR_ON_CURRENT_C2_FIBER"
        ),
        "first_missing_variational_owner": (
            "CURRENT_AE3_INTRINSIC_M4_LR_HIGGS_COUPLING_WITH_T_C2"
        ),
        "first_failure_is_only_a_numeric_scale": False,
        "historical_v11_3_term_can_be_silently_relabelled_AE3": False,
        "successor_action_required_for_full_transport": True,
        "minimal_successor_term_shape": (
            "S_4_lH_superset_-integral(bar(L_L)*y0*T_C2*H*e_R+h.c.)"
        ),
        "y0_currently_derived": False,
        "no_independent_family_coefficient_allowed": True,
    }


def symmetric_slice_mass_test() -> dict[str, Any]:
    """Test the transported shape on the only currently evaluated HS slice."""

    birth = current_c2_birth_overlap_operator()
    zero_masses = {
        sector: (np.zeros((3, 3), dtype=float)).tolist() for sector in MODE_ASSIGNMENTS
    }
    return {
        "evaluated_current_HS_slice": "SYMMETRIC_ZERO_HS_PROBE",
        "nonzero_action_selected_H_star_present": False,
        "formal_mass_relation": "M_f=(H_star/sqrt(2))*y0*T_f",
        "formal_mass_operators_at_H_star_zero": zero_masses,
        "all_formal_mass_operators_zero": True,
        "response_shapes_remain_noncentral": birth["all_sector_shapes_noncentral"],
        "zero_formal_mass_is_a_physical_pole_theorem": False,
        "why_not": (
            "AE3_HAS_NO_DYNAMICAL_HS_KERNEL_NONZERO_BROKEN_SADDLE_OR_"
            "FAMILY_RESOLVED_FERMION_POLE_ON_CURRENT_C2"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "current_C2_finite_family_Hopf_response_shape_derived": True,
        "charged_lepton_up_down_response_orderings_derived": True,
        "frozen_internal_Hopf_response_operator_attached_to_current_C2": True,
        "frozen_mass_ratio_screens_transported_unchanged": True,
        "current_AE3_Yukawa_operator_derived": False,
        "current_AE3_family_mass_hierarchy_derived": False,
        "current_C2_physical_fermion_poles_derived": False,
        "current_C2_parent_relative_energies_derived": False,
        "historical_dimensionful_numbers_promoted": False,
        "current_round_geometry_substituted_for_internal_squashing": False,
        "measured_mass_used": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_derivation": (
            "VERSION_AND_VARY_THE_RETAINED_INTRINSIC_M4_LR_HIGGS_"
            "SEMIGROUP_COUPLING_ON_CURRENT_C2_WITHOUT_AN_INDEPENDENT_"
            "FAMILY_COEFFICIENT;_THEN_DERIVE_ITS_BROKEN_SADDLE_AND_POLES"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "FROZEN_OVERLAP_WIDTH",
    "FROZEN_INTERNAL_BERGER_SHAPE",
    "action_transport_ledger",
    "claim_boundary",
    "current_c2_birth_overlap_operator",
    "family_heat_semigroup",
    "frozen_internal_semigroup_attachment",
    "symmetric_slice_mass_test",
]
