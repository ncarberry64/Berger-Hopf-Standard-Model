"""Scale-free charged-lepton mode sum rule from the AE3.1 action.

The common Higgs scale, trace-normalized Yukawa prefactor, and Berger
squashing cancel from one exact relation among the three frozen charged-
lepton slots.  The result is a conditional local-tree pole relation; it does
not promote the three global physical lepton poles.
"""

from __future__ import annotations

from math import exp, log, pi
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    charged_lepton_yukawa_operator,
)
from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    FROZEN_INTERNAL_BERGER_SHAPE,
    FROZEN_OVERLAP_WIDTH,
)
from bhsm.interface.ae3_family_harmonic_energy_pullback import MODE_ASSIGNMENTS


CLASSIFICATION = "AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE"


def _mode_invariants(mode: tuple[int, int]) -> tuple[int, int]:
    k, j = mode
    return k * (k + 2), (k - 2 * j) ** 2


def charged_lepton_sum_rule_theorem() -> dict[str, Any]:
    """Derive the exact parameter-eliminated relation from integer modes."""

    modes = MODE_ASSIGNMENTS["charged_lepton"]
    invariants = [_mode_invariants(mode) for mode in modes]
    (k_heavy, q2_heavy), (k_middle, q2_middle), (k_light, q2_light) = invariants
    if q2_middle == q2_heavy:
        raise ArithmeticError("middle mode must carry a distinct Berger charge")
    elimination_multiplier = (q2_light - q2_heavy) // (
        q2_middle - q2_heavy
    )
    if (q2_light - q2_heavy) != elimination_multiplier * (
        q2_middle - q2_heavy
    ):
        raise ArithmeticError("Berger-charge squares do not eliminate exactly")
    constant_cost = (
        elimination_multiplier * (k_middle - k_heavy)
        - (k_light - k_heavy)
    )
    return {
        "action_version": ACTION_VERSION,
        "sector": "charged_lepton",
        "roles": ["tau_slot", "mu_slot", "electron_slot"],
        "modes": [list(mode) for mode in modes],
        "K_equals_k_times_k_plus_2": [row[0] for row in invariants],
        "q_squared_equals_k_minus_2j_squared": [row[1] for row in invariants],
        "semigroup_width": FROZEN_OVERLAP_WIDTH,
        "semigroup_width_exact": "1/(4*pi)",
        "cost_formula": "L_f=K_f+(a^2-1)*q_f^2",
        "ratio_formula": "log(m_f/m_tau)=-L_f/(4*pi)",
        "Berger_elimination_multiplier": elimination_multiplier,
        "constant_cost_numerator": constant_cost,
        "exact_log_sum_rule": (
            "log(m_e/m_tau)=9*log(m_mu/m_tau)+54/pi"
        ),
        "exact_multiplicative_sum_rule": (
            "m_e/m_tau=exp(54/pi)*(m_mu/m_tau)^9"
        ),
        "absolute_energy_scale_cancels": True,
        "Higgs_saddle_scale_cancels": True,
        "trace_normalized_Yukawa_prefactor_cancels": True,
        "Berger_squashing_cancels": True,
        "measured_fine_structure_anchor_cancels_with_squashing": True,
        "measured_lepton_mass_used_to_derive_relation": False,
        "relation_holds_for_every_positive_Berger_squashing": True,
    }


def sum_rule_witness(*, squashing: float) -> dict[str, Any]:
    """Evaluate the identity at any positive squashing without mass inputs."""

    a = float(squashing)
    if not np.isfinite(a) or a <= 0.0:
        raise ValueError("positive finite squashing required")
    modes = MODE_ASSIGNMENTS["charged_lepton"]
    costs = []
    for mode in modes:
        base, charge_squared = _mode_invariants(mode)
        costs.append(base + (a * a - 1.0) * charge_squared)
    weights = [exp(-FROZEN_OVERLAP_WIDTH * cost) for cost in costs]
    ratios = [weight / weights[0] for weight in weights]
    log_residual = log(ratios[2]) - 9.0 * log(ratios[1]) - 54.0 / pi
    multiplicative_rhs = exp(54.0 / pi) * ratios[1] ** 9
    return {
        "squashing": a,
        "costs": costs,
        "ratios_to_heavy": ratios,
        "log_sum_rule_residual": log_residual,
        "multiplicative_sum_rule_residual": ratios[2] - multiplicative_rhs,
        "measured_lepton_mass_used": False,
    }


def frozen_reference_diagnostic(
    *, middle_over_heavy: float, light_over_heavy: float
) -> dict[str, Any]:
    """Compare frozen on-shell ratios only after deriving the identity."""

    middle = float(middle_over_heavy)
    light = float(light_over_heavy)
    if not np.isfinite(middle) or not np.isfinite(light):
        raise ValueError("finite reference ratios required")
    if middle <= 0.0 or light <= 0.0:
        raise ValueError("positive reference ratios required")
    sum_rule_light = exp(54.0 / pi) * middle**9
    log_residual = log(light) - 9.0 * log(middle) - 54.0 / pi
    return {
        "reference_middle_over_heavy": middle,
        "reference_light_over_heavy": light,
        "sum_rule_light_over_heavy_from_reference_middle": sum_rule_light,
        "log_residual": log_residual,
        "required_multiplicative_dressing": light / sum_rule_light,
        "tree_relation_fractional_residual": sum_rule_light / light - 1.0,
        "reference_data_used_only_after_derivation": True,
        "comparison_is_parameter_fit": False,
        "dressing_factor_inserted_into_action": False,
    }


def composed_ae31_operator_witness() -> dict[str, Any]:
    """Verify the sum rule on the already composed AE3.1 Yukawa operator."""

    yukawa = charged_lepton_yukawa_operator()
    eigenvalues = np.asarray(
        yukawa["eigenvalues_heavy_middle_light"], dtype=float
    )
    ratios = eigenvalues / eigenvalues[0]
    log_residual = float(
        log(ratios[2]) - 9.0 * log(ratios[1]) - 54.0 / pi
    )
    return {
        "action_version": ACTION_VERSION,
        "operator": "Y_l=(16*sqrt(2*pi)/3969)*exp[-L_a,l/(4*pi)]",
        "eigenvalue_ratios_to_heavy": ratios.tolist(),
        "log_sum_rule_residual": log_residual,
        "frozen_squashing_used_for_witness": FROZEN_INTERNAL_BERGER_SHAPE,
        "squashing_value_used_to_derive_identity": False,
        "absolute_energy_calibration_used": False,
        "measured_lepton_mass_used": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE_DERIVED": True,
        "ABSOLUTE_UNIT_DEPENDENCE_ELIMINATED_FROM_SUM_RULE": True,
        "BERGER_SQUASHING_DEPENDENCE_ELIMINATED_FROM_SUM_RULE": True,
        "MEASURED_LEPTON_MASS_USED_TO_DERIVE_SUM_RULE": False,
        "CURRENT_C2_LOCAL_TREE_LEPTON_RELATION_DERIVED_CONDITIONALLY": True,
        "CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "ACTION_SELECTED_GLOBAL_CHARGED_LEPTON_POLES_OR_MATCHED_PARENT_"
            "RELATIVE_ENERGIES__THEN_TEST_THE_SCALE_FREE_MODE_SUM_RULE_ON_"
            "THE_PHYSICAL_READOUT"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "charged_lepton_sum_rule_theorem",
    "claim_boundary",
    "composed_ae31_operator_witness",
    "frozen_reference_diagnostic",
    "sum_rule_witness",
]
