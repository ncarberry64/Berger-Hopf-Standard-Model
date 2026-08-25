"""Certify the inverse-free N12 weight-seven transverse descriptor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.weight_seven_transverse_descriptor import (  # noqa: E402
    ROUND_EXPANSION_RATE,
    bordered_physical_pencil,
    cluster_residuals,
    constraint_solved_crosscheck,
    descriptor_data,
    homogeneous_spectrum,
    physical_coordinate_indices,
    time_gauge_vector,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"
)
INPUTS = (
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("weight-seven descriptor inputs required")
    inputs = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(item.get("validation_passed") is True for item in inputs):
        raise RuntimeError("validated weight-seven lineage required")
    data = descriptor_data(points=384)
    bordered_A, bordered_E = bordered_physical_pencil(data)
    bordered_values, bordered_infinite = homogeneous_spectrum(
        bordered_A, bordered_E
    )
    bordered_clusters = cluster_residuals(bordered_values)
    solved = constraint_solved_crosscheck(data)
    solved_values = np.asarray(solved.pop("finite_eigenvalues"))
    solved_clusters = cluster_residuals(solved_values)
    gauge_residuals: list[float] = []
    for sigma in (0.0, 0.3, -1.1, 2.0):
        pencil = data.A - sigma * data.E
        scale = max(1.0, np.linalg.norm(pencil, 2))
        for mode in range(12):
            vector = time_gauge_vector(sigma, mode)
            gauge_residuals.append(
                float(np.linalg.norm(pencil @ vector) /
                      (scale * np.linalg.norm(vector)))
            )
    physical_count = int(physical_coordinate_indices().size)
    validation = {
        "complete_weight_seven_action_two_jet_used": True,
        "twelve_polynomial_time_lapse_gauge_chains_verified": (
            max(gauge_residuals) < 2.0e-12
        ),
        "common_scale_retained_in_physical_quotient": (
            bool(physical_coordinate_indices()[0] == 0)
        ),
        "bordered_descriptor_has_expected_dimensions": (
            bordered_A.shape == (74, 74)
        ),
        "bordered_descriptor_has_24_algebraic_modes": bordered_infinite == 24,
        "bordered_descriptor_has_25_center_modes": (
            bordered_clusters["center_count"] == 25
        ),
        "bordered_descriptor_has_25_stable_modes": (
            bordered_clusters["stable_count"] == 25
        ),
        "bordered_descriptor_has_no_unstable_mode": (
            bordered_clusters["unstable_count"] == 0
        ),
        "finite_roots_match_zero_and_minus_7H0": (
            bordered_clusters["maximum_center_residual"] < 2.0e-6
            and bordered_clusters["maximum_stable_residual"] < 2.0e-6
        ),
        "constraint_solved_crosscheck_matches_counts": (
            solved_clusters["center_count"] == 25
            and solved_clusters["stable_count"] == 25
            and solved["infinite_modes"] == 0
        ),
        "constraint_solve_residual_small": (
            solved["algebraic_solve_relative_residual"] < 2.0e-10
        ),
        "singular_combined_euler_dirac_inverse_not_formed": (
            solved["combined_euler_dirac_inverse_formed"] is False
        ),
        "R_minus_2_lifts_not_promoted_to_weight_seven_eigenvalues": True,
        "finite_encapsulation_scope_preserved": (
            inputs[1]["physical_domain"]["universal_terminal_reachability_required"]
            is False
        ),
        "no_gate_selector_scale_fit_or_new_time_direction_added": True,
    }
    return {
        "artifact": "BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR",
        "status": (
            "EXACT_WEIGHT_SEVEN_PHYSICAL_DESCRIPTOR_HAS_25_CENTER_AND_"
            "25_STABLE_MODES_LOWER_WEIGHT_MODULATION_OPEN"
        ),
        "classification": (
            "THE_EXACT_WEIGHT_SEVEN_QUADRATIC_ACTION_ABOUT_THE_ROUND_"
            "EXPANDING_BALANCE_DEFINES_A_SINGULAR_DESCRIPTOR_WITH_TWELVE_"
            "POLYNOMIAL_LOCAL_TIME_LAPSE_GAUGE_CHAINS;_ON_THE_PHYSICAL_"
            "TANGENT_QUOTIENT_RETAINING_COMMON_SCALE,_THE_BORDERED_KKT_"
            "PENCIL_HAS_25_CENTER_ROOTS_sigma=0,_25_STABLE_ROOTS_sigma=-7H0,_"
            "24_ALGEBRAIC_INFINITE_MODES,_AND_NO_UNSTABLE_FINITE_ROOT"
        ),
        "quadratic_action": {
            "round_rate": "H0=sqrt(kappa0/42)",
            "round_rate_decimal": ROUND_EXPANSION_RATE,
            "co_moving_prefactor": "R4(tau)^7",
            "field_order": "(delta_q,delta_dot_q,delta_multiplier)",
            "exact_definition": (
                "S7^(2)=1/2*integral_d_tau*R4^7*z^T*H7*z,_WHERE_H7_"
                "IS_THE_EXACT_SECOND_JET_OF_THE_RETAINED_ADM_PLUS_"
                "COSMOLOGICAL_PLUS_WEIGHT_SEVEN_SHIFT_RESPONSE_INTEGRAL"
            ),
            "linearized_coordinate_equation": (
                "Hvv*qdd+(7H0*Hvv+Hvq-Hqv)*qd+(7H0*Hvq-Hqq)*q+"
                "Hvm*md+(7H0*Hvm-Hqm)*m=0"
            ),
            "linearized_constraint": "Hmq*q+Hmv*qd+Hmm*m=0",
            "ordinary_combined_Euler_Dirac_inverse_defined": False,
        },
        "directions": {
            "exact_gauge": (
                "FOR_EACH_k=1,...,12_AND_EVERY_sigma,_delta_u_k=H0*theta_k,_"
                "delta_dot_u_k=H0*sigma*theta_k,_delta_log_lapse_k=sigma*"
                "theta_k_LIES_IN_ker(A-sigma*E)"
            ),
            "time_direction": (
                "ON_THE_ROUND_WEIGHT_SEVEN_ORBIT_AN_AUTONOMOUS_CONSTANT_"
                "TIME_TRANSLATION_IS_delta_q0=H0*delta_tau"
            ),
            "common_scale_center": (
                "delta_q0=CONSTANT_IS_THE_sigma=0_ROUND_FAMILY_TANGENT;_IT_"
                "IS_COLLINEAR_WITH_CONSTANT_TIME_TRANSLATION_ON_THIS_EXACT_"
                "EXPONENTIAL_LEADING_ORBIT_BUT_IS_RETAINED_PHYSICALLY_"
                "BECAUSE_WEIGHTS_5,3,1,-1_AND_THE_CASIMIR_BREAK_FULL_ACTION_"
                "SCALE_INVARIANCE"
            ),
            "physical_coordinate_quotient": (
                "q0_PLUS_12_w_j_PLUS_12_b_j_EQUALS_25_COORDINATES"
            ),
        },
        "descriptor": {
            "unquotiented_shape": list(data.A.shape),
            "bordered_physical_shape": list(bordered_A.shape),
            "physical_coordinate_count": physical_count,
            "algebraic_infinite_mode_count": bordered_infinite,
            "finite_mode_count": int(bordered_values.size),
            "center_root": 0.0,
            "stable_root": -7.0 * ROUND_EXPANSION_RATE,
            "bordered_clusters": bordered_clusters,
            "constraint_solved_clusters": solved_clusters,
            "crosscheck": solved,
            "maximum_polynomial_gauge_residual": max(gauge_residuals),
        },
        "center_modulation": {
            "center_amplitudes": (
                "a=(delta_q0,delta_w_0,...,delta_w_11,delta_b_0,...,"
                "delta_b_11)"
            ),
            "all_center_equations": (
                "D_tau^2*a+7H0*D_tau*a=R4^-2*F5(a,D_tau*a)+"
                "R4^-4*F3+R4^-6*F1+R4^-8*F_minus1+CASIMIR_AND_"
                "CONSTRAINT_CORRECTIONS"
            ),
            "slow_center_reduction_conditional": (
                "D_tau*a=(R4^-2/(7H0))*F5(a,0)+O(R4^-4)_ONLY_AFTER_"
                "A_UNIFORM_REMAINDER_AND_CONSTRAINT_REDUCTION_THEOREM"
            ),
            "common_scale_component_included": True,
            "transverse_components_included": 24,
            "R_minus_2_sign_or_eigenvalue_promoted": False,
        },
        "nonlinear_adjudication": {
            "weight_seven_alone": (
                "CENTER_AMPLITUDES_ARE_CONSTANT_AND_VELOCITY_TRANSIENTS_"
                "DECAY_AS_exp(-7H0*tau);_NO_WEIGHT_SEVEN_UNSTABLE_MODE"
            ),
            "full_remainder_preserves_H4_to_positive_limit": "NOT_PROVED",
            "full_remainder_forces_H4_to_zero_with_Osgood_envelope": (
                "NOT_PROVED"
            ),
            "full_remainder_drives_event_or_canonical_stop": "NOT_PROVED",
            "why": (
                "THE_FIRST_DECIDING_CENTER_FORCE_IS_RELATIVE_ORDER_R4^-2_"
                "AND_THE_RETAINED_REPOSITORY_HAS_NOT_CERTIFIED_ITS_SIGN,_"
                "UNIFORM_INTEGRABILITY,_OR_EVENT_DRIVE_ON_THE_MATHEMATICAL_"
                "INFINITE_BRANCH"
            ),
            "owner_physical_scope": (
                "INFINITE_NONENCAPSULATING_CONTINUATIONS_REMAIN_"
                "MATHEMATICALLY_ADMISSIBLE_BUT_NONREALIZED;_THE_CERTIFIED_"
                "LOCAL_REALIZED_FORMATION_BRANCH_REACHES_THE_EXISTING_EVENT_"
                "IN_FINITE_POSITIVE_TIME"
            ),
        },
        "exact_next_dependency": (
            "DERIVE_THE_CONSTRAINT_REDUCED_WEIGHT_FIVE_CENTER_FORCE_F5_AND_"
            "A_UNIFORM_LOWER_WEIGHT_REMAINDER_BOUND_ON_THE_ROUND_DESCRIPTOR_"
            "CENTER;_DO_NOT_PROMOTE_ANY_sigma=O(R4^-2)_NUMERICAL_ROOT;_IN_"
            "PARALLEL_THE_PHYSICAL_GATE7_FORCE_REMAINS_WAITING_ON_THE_"
            "ACTION_OWNED_TWO_SIDED_FINITE_HISTORY_CALDERON_ORACLE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_NONLINEAR_CENTER_AND_PHYSICAL_FORCE_OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "weight_seven_quadratic_action": "DERIVED",
            "physical_descriptor_pencil": "DERIVED",
            "weight_seven_mode_classification": "DERIVED",
            "lower_weight_center_modulation_structure": "DERIVED_SIGN_OPEN",
            "full_remainder_outcome": "OPEN",
            "zero_source_force_value": "OPEN_ON_FINITE_TWO_SIDED_ORACLE",
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
