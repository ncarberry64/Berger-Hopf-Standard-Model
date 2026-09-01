"""Charged-lepton pole-dressing invariant induced by the AE3.1 sum rule.

The already-derived local-tree identity fixes the one logarithmic combination
of effective pole dressings that can change its physical readout.  This module
does not supply or fit those dressings; it isolates the exact target for a
future action-derived dressed two-point operator.
"""

from __future__ import annotations

from math import exp, log, pi
from typing import Any, Sequence

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae31_charged_lepton_scale_free_sum_rule import (
    composed_ae31_operator_witness,
)


CLASSIFICATION = "AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT"
DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT = np.asarray([8.0, -9.0, 1.0])


def _positive_triple(values: Sequence[float], *, label: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.shape != (3,):
        raise ValueError(f"{label} must contain heavy, middle, and light entries")
    if not np.all(np.isfinite(array)) or np.any(array <= 0.0):
        raise ValueError(f"{label} entries must be positive and finite")
    return array


def pole_dressing_invariant_theorem() -> dict[str, Any]:
    """Return the exact dressing identity without choosing a pole model."""

    coefficients = DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT
    return {
        "action_version": ACTION_VERSION,
        "roles": ["tau_slot", "mu_slot", "electron_slot"],
        "tree_identity": "R_tree=log(m_e/m_tau)-9*log(m_mu/m_tau)-54/pi=0",
        "effective_pole_map": "M_f=Z_f*m_f_with_Z_f>0",
        "physical_residual": (
            "R_pole=log(M_e/M_tau)-9*log(M_mu/M_tau)-54/pi"
        ),
        "exact_dressing_identity": (
            "R_pole=log(Z_e)-9*log(Z_mu)+8*log(Z_tau)"
        ),
        "multiplicative_invariant": "D=Z_e*Z_tau^8/Z_mu^9=exp(R_pole)",
        "log_dressing_coefficients_heavy_middle_light": coefficients.tolist(),
        "coefficient_sum": float(np.sum(coefficients)),
        "common_multiplicative_pole_rescaling_cancels": True,
        "common_wavefunction_or_unit_rescaling_can_repair_nonzero_residual": False,
        "one_family_resolved_log_combination_is_observable_by_this_sum_rule": True,
        "microscopic_self_energy_form_derived": False,
        "additive_or_nondiagonal_pole_corrections_excluded": False,
    }


def dressed_sum_rule_witness(
    *, tree_masses: Sequence[float], dressed_masses: Sequence[float]
) -> dict[str, Any]:
    """Verify the exact residual identity for any positive mass triples."""

    tree = _positive_triple(tree_masses, label="tree_masses")
    dressed = _positive_triple(dressed_masses, label="dressed_masses")
    dressing = dressed / tree
    tree_residual = (
        log(tree[2] / tree[0])
        - 9.0 * log(tree[1] / tree[0])
        - 54.0 / pi
    )
    pole_residual = (
        log(dressed[2] / dressed[0])
        - 9.0 * log(dressed[1] / dressed[0])
        - 54.0 / pi
    )
    dressing_log_invariant = float(
        DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT @ np.log(dressing)
    )
    return {
        "tree_masses_heavy_middle_light": tree.tolist(),
        "dressed_masses_heavy_middle_light": dressed.tolist(),
        "effective_dressings_heavy_middle_light": dressing.tolist(),
        "tree_sum_rule_residual": float(tree_residual),
        "dressed_sum_rule_residual": float(pole_residual),
        "dressing_log_invariant": dressing_log_invariant,
        "residual_difference_minus_dressing_invariant": float(
            pole_residual - tree_residual - dressing_log_invariant
        ),
    }


def common_rescaling_no_go(*, factor: float) -> dict[str, Any]:
    """Show that a common positive multiplicative correction cancels exactly."""

    common = float(factor)
    if not np.isfinite(common) or common <= 0.0:
        raise ValueError("positive finite common factor required")
    tree = np.asarray(
        composed_ae31_operator_witness()["eigenvalue_ratios_to_heavy"],
        dtype=float,
    )
    witness = dressed_sum_rule_witness(
        tree_masses=tree, dressed_masses=common * tree
    )
    return {
        "common_factor": common,
        "coefficient_sum": float(
            np.sum(DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT)
        ),
        "dressing_log_invariant": witness["dressing_log_invariant"],
        "tree_sum_rule_residual": witness["tree_sum_rule_residual"],
        "dressed_sum_rule_residual": witness["dressed_sum_rule_residual"],
        "nonzero_residual_repaired": False,
    }


def reference_pole_dressing_target(
    *, middle_over_heavy: float, light_over_heavy: float
) -> dict[str, Any]:
    """Evaluate the post-derivation pole-dressing target from reference ratios."""

    reference = _positive_triple(
        [1.0, middle_over_heavy, light_over_heavy], label="reference ratios"
    )
    tree = np.asarray(
        composed_ae31_operator_witness()["eigenvalue_ratios_to_heavy"],
        dtype=float,
    )
    effective = reference / tree
    residual = (
        log(reference[2]) - 9.0 * log(reference[1]) - 54.0 / pi
    )
    invariant = float(reference[2] / (exp(54.0 / pi) * reference[1] ** 9))
    coefficient_norm_squared = float(
        DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT
        @ DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT
    )
    minimum_log_vector = (
        residual
        * DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT
        / coefficient_norm_squared
    )
    return {
        "reference_ratios_heavy_middle_light": reference.tolist(),
        "tree_ratios_heavy_middle_light": tree.tolist(),
        "effective_dressing_ratios_with_Z_tau_gauge_one": effective.tolist(),
        "required_log_dressing_invariant": float(residual),
        "required_multiplicative_dressing_invariant": invariant,
        "effective_dressing_invariant_check": float(
            effective[2] * effective[0] ** 8 / effective[1] ** 9
        ),
        "coefficient_norm_squared": coefficient_norm_squared,
        "minimum_Euclidean_log_norm_representative": minimum_log_vector.tolist(),
        "minimum_Euclidean_multiplicative_representative": np.exp(
            minimum_log_vector
        ).tolist(),
        "representative_is_action_solution": False,
        "reference_data_used_only_after_derivation": True,
        "target_inserted_into_action": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT_DERIVED": True,
        "COMMON_MULTIPLICATIVE_POLE_RESCALING_NO_GO_DERIVED": True,
        "FAMILY_RESOLVED_DRESSING_TARGET_QUANTIFIED": True,
        "ACTION_DERIVED_DRESSED_TWO_POINT_OPERATOR_AVAILABLE": False,
        "MICROSCOPIC_SELF_ENERGY_OR_RG_FLOW_DERIVED": False,
        "ADDITIVE_OR_NONDIAGONAL_POLE_CORRECTIONS_EXCLUDED": False,
        "CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "ACTION_SELECTED_CHARGED_LEPTON_TWO_POINT_OPERATOR_WITH_"
            "FAMILY_RESOLVED_SELF_ENERGY__THEN_EVALUATE_"
            "LOG_Z_E_MINUS_9_LOG_Z_MU_PLUS_8_LOG_Z_TAU"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT",
    "claim_boundary",
    "common_rescaling_no_go",
    "dressed_sum_rule_witness",
    "pole_dressing_invariant_theorem",
    "reference_pole_dressing_target",
]
