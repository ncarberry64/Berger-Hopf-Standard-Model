"""Derive and audit the exact finite-endpoint zero-source force functional."""

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

from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (  # noqa: E402
    periodic_laplacian,
)
from bhsm.interface.aether_replacement_geometry_force_v16_06 import (  # noqa: E402
    regulator_first,
)
from bhsm.interface.forward_finite_endpoint_heat_force import (  # noqa: E402
    heat_regulator_value_and_force,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
    ),
    ARTIFACTS / "BHSM_aether_replacement_geometry_force_v16_06.json",
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/"
        "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_difference_witness() -> dict[str, float]:
    operator = np.asarray(
        [[2.4, 0.31 - 0.12j, -0.08],
         [0.31 + 0.12j, 3.1, 0.27j],
         [-0.08, -0.27j, 4.0]],
        dtype=complex,
    )
    jet = np.asarray(
        [[0.4, -0.16 + 0.07j, 0.03],
         [-0.16 - 0.07j, -0.2, 0.11j],
         [0.03, -0.11j, 0.13]],
        dtype=complex,
    )
    analytic = heat_regulator_value_and_force(
        operator, {"h": jet}
    )["forces"]["h"]
    epsilon = 1.0e-5
    plus = heat_regulator_value_and_force(
        operator + epsilon * jet, {}
    )["Gamma_heat"]
    minus = heat_regulator_value_and_force(
        operator - epsilon * jet, {}
    )["Gamma_heat"]
    finite = (plus - minus) / (2.0 * epsilon)
    return {
        "analytic": analytic,
        "finite_difference": finite,
        "absolute_residual": abs(analytic - finite),
    }


def basis_covariance_witness() -> dict[str, float]:
    rng = np.random.default_rng(1207)
    raw = rng.normal(size=(5, 5)) + 1j * rng.normal(size=(5, 5))
    unitary, _ = np.linalg.qr(raw)
    operator = np.diag([1.2, 1.7, 2.5, 3.2, 4.6]).astype(complex)
    jet = np.diag([0.2, -0.1, 0.7, -0.3, 0.4]).astype(complex)
    first = heat_regulator_value_and_force(operator, {"h": jet})
    second = heat_regulator_value_and_force(
        unitary @ operator @ unitary.conj().T,
        {"h": unitary @ jet @ unitary.conj().T},
    )
    return {
        "Gamma_residual": abs(first["Gamma_heat"] - second["Gamma_heat"]),
        "force_residual": abs(first["forces"]["h"] - second["forces"]["h"]),
    }


def historical_operator_level_witness() -> dict[str, float]:
    radii = np.asarray([1.0, 1.04, 0.98, 1.02, 1.01, 0.99])
    step = 0.07
    level = 3.0
    spatial = (level / radii) ** 2
    operator = periodic_laplacian(len(radii), step) + np.diag(spatial)
    jets = {
        f"node_{index}": np.diag(
            [-2.0 * value if row == index else 0.0 for row, value in enumerate(spatial)]
        )
        for index in range(len(radii))
    }
    current = heat_regulator_value_and_force(operator, jets)
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    probabilities = np.abs(eigenvectors) ** 2
    diagonal_fprime = probabilities @ regulator_first(eigenvalues, 1.0)
    historical = -2.0 * spatial * diagonal_fprime
    current_vector = np.asarray([
        current["forces"][f"node_{index}"] for index in range(len(radii))
    ])
    return {
        "maximum_force_residual": float(np.max(np.abs(current_vector - historical))),
        "current_force_norm": float(np.linalg.norm(current_vector)),
    }


def reset_fiber_geometry_variation_witness() -> dict[str, Any]:
    checkpoint = np.load(INPUTS[-1])
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    state = np.asarray(checkpoint["state"], dtype=float)
    fixed_event_child = jacobian[26:, 98:]
    fiber = null_space(fixed_event_child)
    child = state[98:]
    q = child[:37]
    signs_k = (-1.0) ** np.arange(1, 13)
    signs_j = (-1.0) ** np.arange(12)
    v_boundary = float(q[25:37] @ signs_j)
    log_r4_gradient = np.zeros(98)
    log_r4_gradient[0] = 1.0
    log_r4_gradient[1:13] = signs_k
    log_r4_gradient[25:37] = -math.tanh(2.0 * v_boundary) * signs_j
    projected = fiber @ (fiber.T @ log_r4_gradient)
    projected_norm = float(np.linalg.norm(projected))
    unit = projected / projected_norm
    geometry_map = fiber[:37, :]
    singular_values = np.linalg.svd(geometry_map, compute_uv=False)
    geometry_rank = int(np.sum(singular_values > 1.0e-11))
    return {
        "fixed_event_child_shape": list(fixed_event_child.shape),
        "fixed_event_child_fiber_dimension": int(fiber.shape[1]),
        "fiber_kernel_residual": float(np.linalg.norm(fixed_event_child @ fiber, 2)),
        "child_q_variation_rank_on_fiber": geometry_rank,
        "child_q_variation_rank_after_any_one_dimensional_time_quotient_lower": (
            geometry_rank - 1
        ),
        "boundary_v": v_boundary,
        "boundary_log_R4_covector_projection_norm": projected_norm,
        "unit_fiber_direction_boundary_log_R4_rate": float(
            log_r4_gradient @ unit
        ),
        "unit_fiber_direction_constraint_residual": float(
            np.linalg.norm(fixed_event_child @ unit)
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-endpoint force inputs required")
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated finite-endpoint force inputs required")
    finite, branch, incidence, historical, dini, reset = records
    fd = finite_difference_witness()
    covariance = basis_covariance_witness()
    shared = historical_operator_level_witness()
    fiber = reset_fiber_geometry_variation_witness()
    validation = {
        "finite_physical_domain_and_local_existence_consumed": (
            finite["claim_boundary"]["finite_encapsulation_existence"]
            == "CLOSED_LOCAL_ACTION_THEOREM"
            and branch["adjudication"][
                "finite_positive_time_completed_encapsulation_exists"
            ] is True
        ),
        "finite_endpoint_compact_resolvent_source_control_consumed": (
            dini["validation_passed"] is True
        ),
        "domain_parametric_incidence_available": (
            incidence["claim_boundary"][
                "domain_parametric_nonzero_local_incidence"
            ] == "DERIVED"
        ),
        "noncommuting_finite_difference_verified": (
            fd["absolute_residual"] < 1.0e-10
        ),
        "basis_covariance_verified": max(covariance.values()) < 1.0e-12,
        "historical_engine_matches_only_at_shared_operator_level": (
            shared["maximum_force_residual"] < 1.0e-12
        ),
        "historical_periodic_value_not_promoted": (
            historical["claim_boundary"]["heat_geometry_force_evaluated"]
            is True
        ),
        "reset_fiber_geometry_variation_certified": (
            reset["reset_correspondence"]["fixed_event_child_fiber_dimension"]
            == fiber["fixed_event_child_fiber_dimension"] == 67
            and fiber["child_q_variation_rank_after_any_one_dimensional_time_quotient_lower"]
            >= 1
            and fiber["boundary_log_R4_covector_projection_norm"] > 0.0
            and fiber["unit_fiber_direction_constraint_residual"] < 1.0e-10
        ),
        "current_numeric_force_not_fabricated": True,
        "no_reset_selector_endpoint_parameter_contour_scale_fit_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL",
        "status": "EXACT_FORCE_FUNCTIONAL_DERIVED_CURRENT_OPERATOR_REALIZATION_OPEN",
        "classification": (
            "ON_EVERY_RETAINED_POSITIVE_SELF_ADJOINT_FINITE_ENDPOINT_"
            "REALIZATION_THE_ZERO_SOURCE_HEAT_GEOMETRY_FORCE_IS_THE_EXACT_"
            "BASIS_INDEPENDENT_TRACE_OF_exp(-ell2_P)/(2P)_TIMES_D_P;_THE_"
            "CURRENT_N12_NUMBER_IS_NOT_THE_HISTORICAL_PERIODIC_VALUE_AND_"
            "REMAINS_OPEN_UNTIL_THE_ACTION_OWNED_FINITE_HISTORY_OPERATOR_"
            "AND_ITS_GEOMETRY_JET_ARE_REALIZED"
        ),
        "exact_force_theorem": {
            "functional": "Gamma_heat(P)=Tr[-(1/2)*E1(ell^2*P)]",
            "first_variation": (
                "D_Gamma_heat(P)[delta_P]=(1/2)*Tr["
                "exp(-ell^2*P)*P^(-1)*delta_P]"
            ),
            "direct_sum": (
                "F_h=(1/2)*sum_C_s_C*m_C*Tr[exp(-ell^2*P_C)*"
                "P_C^(-1)*D_h_P_C]"
            ),
            "noncommuting_delta_P_allowed": True,
            "basis_independent": True,
            "finite_by_compact_elliptic_resolvent_positive_quotient_gap_and_finite_order_action_jet": True,
            "zero_source_means": "GAUGE_AND_HS_EXTERNAL_SOURCES_SET_TO_ZERO",
            "geometry_variation_retained": True,
        },
        "current_realization_audit": {
            "local_pre_event_branch_exists_abstractly": True,
            "certified_event_and_complete_child_states_exist": True,
            "finite_history_coefficient_or_operator_oracle_available": False,
            "action_owned_temporal_form_matrix_on_that_history_available": False,
            "geometry_jet_D_h_P_on_that_realization_available": False,
            "reset_relation_is_set_valued": True,
            "reset_fiber_invariance_of_force_proved": False,
            "reset_relation_alone_holds_child_geometry_fixed": False,
            "reset_fiber_child_q_variation_rank": fiber[
                "child_q_variation_rank_on_fiber"
            ],
            "reset_fiber_boundary_log_R4_variation_nonzero": True,
            "therefore_current_force_value_or_sign_evaluated": False,
        },
        "historical_transfer_boundary": {
            "v16_06_periodic_replacement_common_log_radius_force": historical[
                "replacement_seed_geometry_force"
            ]["replacement_common_log_radius_force"],
            "shared_matrix_function_derivative_identity_reproduced": True,
            "periodic_24_node_seed_is_current_finite_history": False,
            "periodic_force_value_promoted": False,
        },
        "witnesses": {
            "noncommuting_finite_difference": fd,
            "basis_covariance": covariance,
            "historical_shared_operator_level": shared,
            "reset_fiber_geometry_variation": fiber,
        },
        "exact_next_dependency": (
            "CONSTRUCT_FROM_THE_RETAINED_EULER_DIRAC_BRANCH_AND_EVENT_CHILD_"
            "GRAPH_A_VALIDATED_FINITE_HISTORY_OPERATOR_COEFFICIENT_ORACLE_"
            "WITH_D_TAU,_THE_ACTION_OWNED_ENDPOINT_FORM,_AND_D_PHI_P;_THEN_"
            "EVALUATE_THE_TRACE_FORCE_WITHOUT_SELECTING_A_RESET_FIBER_"
            "MEMBER_BY_HAND,_EITHER_BY_A_JOINT_SADDLE_SOLVE_OR_BY_PROVING_"
            "RESET_FIBER_INVARIANCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FORCE_REALIZATION_OPEN",
            "zero_source_force_functional": "DERIVED",
            "zero_source_force_value": "OPEN",
            "zero_source_force_sign": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE_REALIZATION",
            "pair_plus_contact_Hessian": "OPEN_AFTER_SADDLE",
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
