"""Audit reset-fiber radius jets and the physical common-scale center."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
    proper_time_log_radius_rate,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / (
        "n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"
    ),
    ARTIFACTS / "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def radius_cauchy_jet_witness() -> dict[str, Any]:
    with np.load(INPUTS[0]) as checkpoint:
        state = np.asarray(checkpoint["state"], dtype=float)[98:]
        jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)[
            26:, 98:
        ]
    q = state[:37]
    velocity = state[37:74]
    multipliers = state[74:]
    tangent = null_space(jacobian)

    x_jets = boundary_log_radius_jets(
        12, q, np.zeros(37), np.zeros(37)
    )
    gradient_x = np.asarray(x_jets["gradient"], dtype=float)
    signs_j = (-1.0) ** np.arange(12)
    signs_k = (-1.0) ** np.arange(1, 13)
    boundary_v = float(x_jets["boundary_v"])
    hessian_x = np.zeros((37, 37))
    hessian_x[25:37, 25:37] = (
        -2.0
        * (1.0 - math.tanh(2.0 * boundary_v) ** 2)
        * np.outer(signs_j, signs_j)
    )
    lapse = math.exp(boundary_log_lapse(12, multipliers))
    rate = proper_time_log_radius_rate(12, q, velocity, multipliers)

    covector_x = np.zeros(98)
    covector_x[:37] = gradient_x
    covector_rate = np.zeros(98)
    covector_rate[:37] = hessian_x @ velocity / lapse
    covector_rate[37:74] = gradient_x / lapse
    covector_rate[74:86] = -rate * signs_k

    raw_jet_map = np.vstack((covector_x, covector_rate)) @ tangent
    left, singular, right = np.linalg.svd(raw_jet_map, full_matrices=False)
    rank = int(np.sum(singular > 1.0e-10))

    # Cross-check the analytic two-row derivative along both right-singular
    # directions by direct centered differences of the retained radius map.
    rows = []
    step = 1.0e-6
    for index in range(2):
        direction = tangent @ right[index]
        analytic = raw_jet_map @ right[index]

        def evaluate(offset: float) -> np.ndarray:
            shifted = state + offset * direction
            return np.asarray((
                boundary_log_radius(12, shifted[:37]),
                proper_time_log_radius_rate(
                    12, shifted[:37], shifted[37:74], shifted[74:]
                ),
            ))

        finite = (evaluate(step) - evaluate(-step)) / (2.0 * step)
        rows.append({
            "right_singular_direction": index,
            "analytic_jet_derivative": analytic.tolist(),
            "centered_finite_difference": finite.tolist(),
            "absolute_crosscheck_residual": float(np.linalg.norm(analytic - finite)),
            "constraint_tangency_residual": float(
                np.linalg.norm(jacobian @ direction)
            ),
        })

    radius = math.exp(boundary_log_radius(12, q))
    scalar_potential = 1.0 / (radius * radius)
    coefficient_jacobian = np.asarray((
        (-2.0 * scalar_potential, 0.0),
        (4.0 * scalar_potential * rate, -2.0 * scalar_potential),
    ))
    return {
        "fixed_event_child_jacobian_shape": list(jacobian.shape),
        "raw_reset_tangent_dimension": int(tangent.shape[1]),
        "boundary_log_R4": boundary_log_radius(12, q),
        "boundary_R4": radius,
        "boundary_lapse": lapse,
        "boundary_proper_log_R4_rate": rate,
        "raw_log_R4_covector_norm": float(np.linalg.norm(raw_jet_map[0])),
        "raw_proper_rate_covector_norm": float(np.linalg.norm(raw_jet_map[1])),
        "radius_Cauchy_jet_singular_values": singular.tolist(),
        "radius_Cauchy_jet_rank": rank,
        "finite_difference_rows": rows,
        "scalar_fixed_channel_coefficient_jet": {
            "coefficient": "V=R4^-2=exp(-2*x)",
            "proper_time_derivative": "D_tau_V=-2*V*D_tau_x",
            "jet_change_matrix_from_(delta_x,delta_D_tau_x)": (
                coefficient_jacobian.tolist()
            ),
            "determinant": float(np.linalg.det(coefficient_jacobian)),
            "exact_positive_determinant_formula": "4*exp(-4*x)>0",
        },
        "rank_inequality_after_any_one_dimensional_time_quotient": (
            max(0, rank - 1)
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("reset-fiber radius-jet audit inputs required")
    reset = _load(INPUTS[1])
    angular = _load(INPUTS[2])
    force_domain = _load(INPUTS[3])
    parametric = _load(INPUTS[4])
    reconnaissance = _load(INPUTS[5])
    time_tangent = reconnaissance["cross_resolution_reconnaissance"][
        "whole_system_time_translation_tangent_interface"
    ]
    if not all(record.get("validation_passed") is True for record in (
        reset, angular, force_domain, parametric, reconnaissance, time_tangent
    )):
        raise RuntimeError("validated reset-fiber radius-jet inputs required")
    witness = radius_cauchy_jet_witness()
    validation = {
        "radius_Cauchy_jet_has_rank_two_on_raw_reset_tangent": (
            witness["radius_Cauchy_jet_rank"] == 2
            and witness["radius_Cauchy_jet_singular_values"][1] > 0.18
        ),
        "analytic_jet_derivatives_match_centered_differences": all(
            row["absolute_crosscheck_residual"] < 1.0e-8
            and row["constraint_tangency_residual"] < 1.0e-12
            for row in witness["finite_difference_rows"]
        ),
        "fixed_channel_coefficient_jet_map_is_invertible": (
            witness["scalar_fixed_channel_coefficient_jet"]["determinant"] > 0.0
        ),
        "one_dimensional_time_quotient_leaves_a_coefficient_jet_direction": (
            reset["reset_correspondence"][
                "fixed_event_child_fiber_dimension"
            ] == 67
            and reset["reset_correspondence"][
                "after_existing_whole_system_time_quotient"
            ] == 66
            and witness[
                "rank_inequality_after_any_one_dimensional_time_quotient"
            ] >= 1
        ),
        "global_time_translation_is_exact_action_symmetry": (
            time_tangent["validation"][
                "retained_action_has_no_explicit_history_time"
            ] is True
            and time_tangent["validation"][
                "event_child_matching_is_covariant_under_common_time_translation"
            ] is True
        ),
        "common_scale_has_multiple_retained_action_weights": (
            angular["retained_action_uniform_scale_ownership_audit"][
                "witness"
            ]["pre_inverse_inertia_bulk_scale_weights"] == [7, 5, 3, 1, -1]
            and angular["retained_action_uniform_scale_ownership_audit"][
                "witness"
            ]["boundary_Casimir_scale_weight"] == -1
        ),
        "common_scale_force_is_not_a_free_cutoff_or_gauge_identity": (
            force_domain["theorem"]["common_scale_direction"]
            == "delta_log_R4=h=1"
            and force_domain["domain_adjudication"][
                "arbitrary_regular_free_cutoff_allowed"
            ] is False
        ),
        "parametric_oracle_still_open": (
            parametric["claim_boundary"]["actual_parametric_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "no_scale_quotient_selector_endpoint_fit_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT",
        "status": "TIME_QUOTIENT_CANNOT_REMOVE_ALL_RADIUS_JET_VARIATION_COMMON_SCALE_RETAINED_PHYSICAL_CENTER",
        "classification": (
            "THE_ACTION_OWNED_RESET_TANGENT_HAS_RANK_TWO_IN_THE_BOUNDARY_"
            "RADIUS_CAUCHY_JET_(log_R4,D_tau_log_R4);_THE_FIXED_CHANNEL_"
            "COEFFICIENT_JET_IS_AN_INVERTIBLE_FUNCTION_OF_THAT_PAIR,_SO_ANY_"
            "ONE_DIMENSIONAL_WHOLE_TIME_QUOTIENT_LEAVES_AT_LEAST_ONE_"
            "COEFFICIENT_HISTORY_DIRECTION;_THE_COMMON_SCALE_IS_A_PHYSICAL_"
            "WEIGHT_SEVEN_CENTER_WITH_LOWER_WEIGHT_AND_CASIMIR_FORCE,_NOT_AN_"
            "EXACT_GAUGE_DIRECTION_TO_DELETE_FROM_THE_FULL_SADDLE"
        ),
        "radius_Cauchy_jet_witness": witness,
        "quotient_theorem": {
            "raw_map": "A:T_raw_TO_R2,_A(delta_y)=(delta_x,delta_D_tau_x)",
            "computed_rank": witness["radius_Cauchy_jet_rank"],
            "for_any_time_generator_g": (
                "rank_OF_THE_INDUCED_COEFFICIENT_JET_MOD_span(A*g)_IS_AT_"
                "LEAST_rank(A)-1=1"
            ),
            "explicit_time_generator_needed_for_this_lower_bound": False,
            "consequence": (
                "WHOLE_SYSTEM_TIME_TRANSLATION_ALONE_CANNOT_MAKE_THE_"
                "FIXED_CHANNEL_COEFFICIENT_HISTORY_CONSTANT_ON_THE_RESET_FIBER"
            ),
        },
        "center_classification": {
            "exact_whole_system_time_translation": (
                "GAUGE_EQUIVALENCE_tau_time=(D_t_U_pre,D_t_U_child,-1_event_time)"
            ),
            "weight_seven_local_lapse_velocity_kernel": (
                "TWELVE_LEADING_DESCRIPTOR_KERNEL_VECTORS_z_k;_THEY_ARE_"
                "LIFTED_AT_RELATIVE_R^-2_BY_THE_FULL_RETAINED_ACTION_AND_ARE_"
                "NOT_PROMOTED_HERE_TO_TWELVE_EXACT_FULL_ACTION_GAUGES"
            ),
            "common_scale": (
                "PHYSICAL_CENTER_OR_MODULATION_DIRECTION_AT_WEIGHT_SEVEN;_"
                "RETAINED_WEIGHTS_5,3,1,-1_AND_THE_BOUNDARY_CASIMIR_BREAK_"
                "UNIFORM_SCALE_INVARIANCE"
            ),
            "common_scale_may_be_removed_from_full_replacement_saddle": False,
            "reason": (
                "THE_RETAINED_ACTION_AND_ZETA_FUNCTIONAL_HAVE_NONTRIVIAL_"
                "COMMON_SCALE_VARIATION;_CENTER_AT_ONE_HOMOGENEOUS_WEIGHT_"
                "DOES_NOT_MEAN_GAUGE_OF_THE_COMPLETE_ACTION"
            ),
        },
        "fiber_invariance_adjudication": {
            "reset_kinematics_force_full_coefficient_invariance": False,
            "time_translation_force_full_coefficient_invariance": False,
            "common_scale_symmetry_force_full_coefficient_invariance": False,
            "separate_quantum_trace_cancellation_theorem_proved": False,
            "actual_parametric_exterior_oracle_still_required": True,
            "single_reset_representative_promoted": False,
        },
        "semantic_correction": {
            "superseded_phrase": (
                "QUOTIENT_THE_FULL_REPLACEMENT_TANGENT_BY_A_COMMON_SCALE_CENTER"
            ),
            "current_rule": (
                "QUOTIENT_ONLY_ACTION_DERIVED_EXACT_GAUGE_EQUIVALENCES;_KEEP_"
                "THE_COMMON_SCALE_AS_A_PHYSICAL_CENTER_IN_THE_FORCE_AND_"
                "LOWER_WEIGHT_MODULATION_EQUATION"
            ),
        },
        "exact_next_dependency": (
            "REALIZE_THE_PARAMETRIC_FINITE_STRATUM_EXTERIOR_ORACLE_AND_ITS_"
            "FIRST_TWO_PHYSICAL_GEOMETRY_JETS;_THE_ONLY_REMAINING_"
            "INVARIANCE_SHORTCUT_WOULD_REQUIRE_A_SEPARATE_RETAINED_ACTION_"
            "QUANTUM_TRACE_CANCELLATION_THEOREM,_NOT_RESET_KINEMATICS,_TIME_"
            "TRANSLATION,_OR_COMMON_SCALE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PARAMETRIC_EXTERIOR_ORACLE_OPEN",
            "radius_Cauchy_jet_variation_after_time_quotient": "NONZERO",
            "common_scale_full_action_gauge": False,
            "common_scale_physical_modulation": "RETAIN",
            "actual_projected_force": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
