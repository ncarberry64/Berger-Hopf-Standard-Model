"""Scale- and squashing-free quark response identities on current C2.

This reuses the frozen up/down Berger modes and the already-attached Hopf heat
semigroup.  It derives identities among response weights, not quark Yukawa
operators, quark masses, or physical poles.
"""

from __future__ import annotations

from math import exp, gcd, log, pi
from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    ACTION_VERSION,
    FROZEN_INTERNAL_BERGER_SHAPE,
    FROZEN_OVERLAP_WIDTH,
    frozen_internal_semigroup_attachment,
)
from bhsm.interface.ae3_family_harmonic_energy_pullback import MODE_ASSIGNMENTS


CLASSIFICATION = "CURRENT_C2_QUARK_SCALE_FREE_HOPF_RESPONSE_SUM_RULES"


def _mode_invariants(mode: tuple[int, int]) -> tuple[int, int]:
    k, j = mode
    return k * (k + 2), (k - 2 * j) ** 2


def _primitive_eliminant(sector: str) -> dict[str, Any]:
    modes = MODE_ASSIGNMENTS[sector]
    invariants = [_mode_invariants(mode) for mode in modes]
    (k_h, q2_h), (k_m, q2_m), (k_l, q2_l) = invariants
    delta_k_m = k_m - k_h
    delta_k_l = k_l - k_h
    delta_q2_m = q2_m - q2_h
    delta_q2_l = q2_l - q2_h
    common = gcd(abs(delta_q2_m), abs(delta_q2_l))
    if common == 0:
        raise ArithmeticError("at least one noncentral Berger charge is required")
    coefficient_middle = delta_q2_l // common
    coefficient_light = -delta_q2_m // common
    cost_constant = (
        coefficient_middle * delta_k_m + coefficient_light * delta_k_l
    )
    log_constant = -cost_constant / (4.0 * pi)
    return {
        "sector": sector,
        "roles": ["heavy", "middle", "light"],
        "modes": [list(mode) for mode in modes],
        "K_equals_k_times_k_plus_2": [row[0] for row in invariants],
        "q_squared_equals_k_minus_2j_squared": [row[1] for row in invariants],
        "primitive_log_coefficients_middle_light": [
            coefficient_middle,
            coefficient_light,
        ],
        "primitive_cost_constant": cost_constant,
        "primitive_log_constant": log_constant,
        "Berger_term_cancels_exactly": (
            coefficient_middle * delta_q2_m
            + coefficient_light * delta_q2_l
            == 0
        ),
    }


def quark_response_sum_rule_theorem() -> dict[str, Any]:
    """Derive the primitive within-sector eliminants from integer mode data."""

    up = _primitive_eliminant("up")
    down = _primitive_eliminant("down")
    if up["primitive_log_coefficients_middle_light"] != [16, -9]:
        raise ArithmeticError("unexpected up-sector primitive eliminant")
    if down["primitive_log_coefficients_middle_light"] != [1, 0]:
        raise ArithmeticError("unexpected down-sector primitive eliminant")
    return {
        "action_version": ACTION_VERSION,
        "operator": "T_f(a)=exp[-(K_f+(a^2-1)q_f^2)/(4*pi)]",
        "ratios": "r_f=T_f/T_heavy",
        "up": {
            **up,
            "exact_log_sum_rule": "9*log(r_light)-16*log(r_middle)=-78/pi",
            "exact_multiplicative_sum_rule": (
                "r_light^9=exp(-78/pi)*r_middle^16"
            ),
        },
        "down": {
            **down,
            "exact_log_sum_rule": "log(r_middle)=-12/pi",
            "exact_multiplicative_sum_rule": "r_middle=exp(-12/pi)",
        },
        "common_sector_prefactors_cancel": True,
        "Berger_squashing_cancels": True,
        "measured_quark_mass_used": False,
        "quark_Yukawa_operator_used": False,
        "relation_holds_for_every_positive_Berger_squashing": True,
    }


def quark_response_sum_rule_witness(*, squashing: float) -> dict[str, Any]:
    """Evaluate both exact identities at an arbitrary positive squashing."""

    a = float(squashing)
    if not np.isfinite(a) or a <= 0.0:
        raise ValueError("positive finite squashing required")
    rows: dict[str, Any] = {}
    for sector in ("up", "down"):
        costs = []
        for mode in MODE_ASSIGNMENTS[sector]:
            base, charge_squared = _mode_invariants(mode)
            costs.append(base + (a * a - 1.0) * charge_squared)
        weights = np.exp(-FROZEN_OVERLAP_WIDTH * np.asarray(costs))
        ratios = weights / weights[0]
        if sector == "up":
            log_residual = (
                9.0 * log(ratios[2])
                - 16.0 * log(ratios[1])
                + 78.0 / pi
            )
            multiplicative_residual = (
                ratios[2] ** 9 - exp(-78.0 / pi) * ratios[1] ** 16
            )
        else:
            log_residual = log(ratios[1]) + 12.0 / pi
            multiplicative_residual = ratios[1] - exp(-12.0 / pi)
        rows[sector] = {
            "costs": costs,
            "ratios_to_heavy": ratios.tolist(),
            "log_sum_rule_residual": float(log_residual),
            "multiplicative_sum_rule_residual": float(multiplicative_residual),
        }
    return {
        "squashing": a,
        "sectors": rows,
        "measured_quark_mass_used": False,
        "quark_Yukawa_operator_used": False,
    }


def attached_operator_witness() -> dict[str, Any]:
    """Verify the identities on the attached frozen internal operator."""

    attachment = frozen_internal_semigroup_attachment()
    a = float(attachment["frozen_internal_Berger_shape"])
    witness = quark_response_sum_rule_witness(squashing=a)
    comparison: dict[str, Any] = {}
    for sector in ("up", "down"):
        attached = np.asarray(
            attachment["sectors"][sector]["frozen_mass_ratio_screen"],
            dtype=float,
        )
        calculated = np.asarray(
            witness["sectors"][sector]["ratios_to_heavy"], dtype=float
        )
        comparison[sector] = {
            "attached_ratios_to_heavy": (attached / attached[0]).tolist(),
            "maximum_reconstruction_residual": float(
                np.max(np.abs(attached / attached[0] - calculated))
            ),
            "log_sum_rule_residual": witness["sectors"][sector][
                "log_sum_rule_residual"
            ],
        }
    return {
        "action_version": ACTION_VERSION,
        "frozen_internal_Berger_shape": a,
        "comparison": comparison,
        "all_attachment_commutators_zero": attachment[
            "all_attachment_commutators_zero"
        ],
        "response_weights_relabelled_as_quark_masses": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_UP_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED": True,
        "CURRENT_C2_DOWN_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED": True,
        "CURRENT_C2_QUARK_RESPONSE_IDENTITIES_HOLD_FOR_ALL_POSITIVE_SQUASHING": True,
        "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_DERIVED": False,
        "CURRENT_C2_UP_DOWN_ABSOLUTE_YUKAWA_PREFACTORS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_MASS_RATIOS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "ACTION_OWNED_INTRINSIC_M4_UP_DOWN_LR_HIGGS_OPERATORS_WITHOUT_"
            "INDEPENDENT_FAMILY_COEFFICIENTS__THEN_TEST_THE_RESPONSE_SUM_"
            "RULES_ON_THEIR_TREE_AND_DRESSED_POLES"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "attached_operator_witness",
    "claim_boundary",
    "quark_response_sum_rule_theorem",
    "quark_response_sum_rule_witness",
]
