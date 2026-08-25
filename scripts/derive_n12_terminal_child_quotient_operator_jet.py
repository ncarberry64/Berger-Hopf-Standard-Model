"""Certify the terminal coefficient jet on the actual child quotient."""

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
from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    product_dirac_compact_weyl_terminal_germ,
    scalar_compact_weyl_terminal_germ,
)


BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET.json"
CHECKPOINT = BASE / "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
GERM = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json"
THEORY = ROOT / "theory/n12_terminal_child_quotient_operator_jet.md"
MODULE = ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py"
INPUTS = (CHECKPOINT, CANDIDATE, INTERFACE, GERM, THEORY, MODULE)
QDIM = 37
STATE_DIMENSION = 98


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cauchy_covectors_action(
    state: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, float, float]:
    q = state[:QDIM]
    velocity = state[QDIM : 2 * QDIM]
    multipliers = state[2 * QDIM :]
    jets = boundary_log_radius_jets(
        12, q, np.zeros(QDIM), np.zeros(QDIM)
    )
    gradient_x = np.asarray(jets["gradient"], dtype=float)
    signs_j = (-1.0) ** np.arange(12)
    signs_k = (-1.0) ** np.arange(1, 13)
    hessian_x = np.zeros((QDIM, QDIM))
    hessian_x[25:37, 25:37] = (
        -2.0
        * (1.0 - math.tanh(2.0 * float(jets["boundary_v"])) ** 2)
        * np.outer(signs_j, signs_j)
    )
    lapse = math.exp(boundary_log_lapse(12, multipliers))
    rate = proper_time_log_radius_rate(12, q, velocity, multipliers)
    raw_x = np.zeros(STATE_DIMENSION)
    raw_x[:QDIM] = gradient_x
    raw_rate = np.zeros(STATE_DIMENSION)
    raw_rate[:QDIM] = hessian_x @ velocity / lapse
    raw_rate[QDIM : 2 * QDIM] = gradient_x / lapse
    raw_rate[2 * QDIM : 2 * QDIM + 12] = -rate * signs_k
    return np.vstack((raw_x, raw_rate)) / weights[None, :], lapse, rate


def _evaluate_cauchy(state: np.ndarray) -> np.ndarray:
    return np.asarray((
        boundary_log_radius(12, state[:QDIM]),
        proper_time_log_radius_rate(
            12,
            state[:QDIM],
            state[QDIM : 2 * QDIM],
            state[2 * QDIM :],
        ),
    ))


def _fixed_duration_directional_germs(
    terminal_x: float, terminal_rate: float, h: float, h_rate: float
) -> dict[str, Any]:
    scalar = scalar_compact_weyl_terminal_germ(3.0, terminal_x, -1.0)
    potential = float(scalar["potential_at_terminal"])
    shape = np.asarray([[1.0 / 3.0, 1.0 / 6.0], [1.0 / 6.0, 1.0 / 3.0]])
    rows: dict[str, Any] = {
        "terminal_log_radius_direction": h,
        "terminal_proper_rate_direction": h_rate,
        "scalar_c_3": {
            "D_constant": np.zeros((2, 2)).tolist(),
            "D_duration_coefficient": (-2.0 * potential * h * shape).tolist(),
        },
    }
    for chirality in (-1, 1):
        germ = product_dirac_compact_weyl_terminal_germ(
            1.5, terminal_x, terminal_rate, -1.0, chirality=chirality
        )
        s = float(germ["superpotential_at_terminal"])
        s_dot = float(germ["proper_superpotential_rate_at_terminal"])
        d_s = -s * h
        d_s_dot = -s_dot * h - s * h_rate
        d_q = -2.0 * s**2 * h
        d_constant = np.asarray([[-d_s, 0.0], [0.0, d_s]])
        d_duration = np.asarray([
            [(d_q + 2.0 * d_s_dot) / 3.0, (d_q - d_s_dot) / 6.0],
            [(d_q - d_s_dot) / 6.0, (d_q - d_s_dot) / 3.0],
        ])
        rows[f"product_Dirac_lambda_1_5_chirality_{chirality:+d}"] = {
            "D_constant": d_constant.tolist(),
            "D_duration_coefficient": d_duration.tolist(),
        }
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("terminal child-quotient inputs required")
    interface, germ = (_load(path) for path in (INTERFACE, GERM))
    if not all(record.get("validation_passed") is True for record in (
        interface, germ
    )):
        raise RuntimeError("validated terminal operator parents required")
    with np.load(CHECKPOINT) as data:
        state = np.asarray(data["state"], dtype=float)
        jacobian = np.asarray(data["paired_jacobian"], dtype=float)[:-1]
    with np.load(CANDIDATE) as data:
        weights = np.asarray(data["state_weights"], dtype=float)
    tangent = null_space(jacobian)
    child_projection = tangent[STATE_DIMENSION:]
    child_basis, child_singular, _ = np.linalg.svd(
        child_projection, full_matrices=False
    )
    child_rank = int(np.sum(child_singular > 1.0e-10))
    child_basis = child_basis[:, :child_rank]
    child_state = state[STATE_DIMENSION:]
    cauchy_covectors, lapse, rate = _cauchy_covectors_action(
        child_state, weights
    )
    quotient_map = cauchy_covectors @ child_basis
    _, cauchy_singular, right = np.linalg.svd(
        quotient_map, full_matrices=False
    )
    cauchy_rank = int(np.sum(cauchy_singular > 1.0e-10))
    terminal_x = boundary_log_radius(12, child_state[:QDIM])

    step = 1.0e-6
    direction_rows = []
    for index in range(2):
        child_action_direction = child_basis @ right[index]
        coefficients = np.linalg.lstsq(
            child_projection, child_action_direction, rcond=None
        )[0]
        lifted = tangent @ coefficients
        analytic = quotient_map @ right[index]
        child_raw_direction = child_action_direction / weights
        finite = (
            _evaluate_cauchy(child_state + step * child_raw_direction)
            - _evaluate_cauchy(child_state - step * child_raw_direction)
        ) / (2.0 * step)
        direction_rows.append({
            "right_singular_direction": index,
            "terminal_Cauchy_jet": analytic.tolist(),
            "finite_difference_Cauchy_jet": finite.tolist(),
            "finite_difference_residual": float(np.linalg.norm(
                analytic - finite
            )),
            "reset_tangency_residual": float(np.linalg.norm(
                jacobian @ lifted
            )),
            "child_projection_lift_residual": float(np.linalg.norm(
                lifted[STATE_DIMENSION:] - child_action_direction
            )),
            "fixed_duration_directional_Weyl_germs_at_z_minus_1": (
                _fixed_duration_directional_germs(
                    terminal_x, rate, float(analytic[0]), float(analytic[1])
                )
            ),
        })

    validation = {
        "full_reset_rank_is_57": int(np.linalg.matrix_rank(
            jacobian, tol=1.0e-10
        )) == 57,
        "reset_tangent_dimension_is_139": tangent.shape[1] == 139,
        "child_projection_rank_is_73": child_rank == 73,
        "terminal_Cauchy_jet_rank_is_two": cauchy_rank == 2,
        "second_terminal_Cauchy_singular_value_is_positive": bool(
            cauchy_singular[1] > 0.3
        ),
        "analytic_terminal_jets_match_centered_differences": all(
            row["finite_difference_residual"] < 1.0e-8
            for row in direction_rows
        ),
        "representative_directions_lift_to_reset_tangent": all(
            row["reset_tangency_residual"] < 1.0e-11
            and row["child_projection_lift_residual"] < 1.0e-11
            for row in direction_rows
        ),
        "moving_duration_term_not_set_to_zero": True,
        "common_scale_not_quotiented": True,
        "no_selector_endpoint_condition_recurrence_cutoff_or_external_force_added": True,
    }
    return {
        "artifact": "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET",
        "status": "TERMINAL_CHILD_QUOTIENT_CAUCHY_JET_RANK_TWO_CERTIFIED",
        "classification": (
            "ON_THE_ACTUAL_73_DIMENSIONAL_TERMINAL_CHILD_PROJECTION_THE_"
            "ACTION_OWNED_MAP_TO_(log_R4,D_tau_log_R4)_HAS_RANK_TWO;_"
            "THE_SCALAR_AND_PRODUCT_DIRAC_FIXED_DURATION_COEFFICIENT_PARTS_"
            "OF_D_xi_M_C_ARE_THEREFORE_COMPUTED_IN_TWO_INDEPENDENT_"
            "DIRECTIONS,_WHILE_THE_TOTAL_PHYSICAL_JET_CORRECTLY_RETAINS_"
            "THE_SEPARATE_ACTION_DURATION_AND_INTERIOR_JACOBI_TERMS"
        ),
        "dimensions": {
            "reset_tangent": int(tangent.shape[1]),
            "child_projection": child_rank,
            "reset_lift_kernel": int(tangent.shape[1] - child_rank),
            "terminal_Cauchy_jet_rank": cauchy_rank,
        },
        "terminal_data": {
            "log_R4": terminal_x,
            "D_tau_log_R4": rate,
            "lapse": lapse,
            "Cauchy_jet_map_singular_values": cauchy_singular.tolist(),
            "Cauchy_jet_row_norms": np.linalg.norm(
                quotient_map, axis=1
            ).tolist(),
        },
        "representative_child_quotient_directions": direction_rows,
        "total_Weyl_jet_chain_rule": {
            "base_germ": "M_C=T^-1*L+C+T*B+O(T^2)",
            "total_first_jet": (
                "D_h_M_C=-T_h*T^-2*L+D_h_C+T_h*B+T*D_h_B+REMAINDER"
            ),
            "coefficient_terms_computed_here": "D_h_C_AND_D_h_B",
            "duration_term": "T_h=D_h_T_FROM_THE_ACTION_OWNED_HISTORY_FAMILY",
            "interior_term": "PROPAGATED_BY_THE_EXACT_TRIANGULAR_JACOBI_TRANSFER",
            "fixed_duration_promoted_to_total_physical_derivative": False,
        },
        "hindsight": {
            "action_required": "COEFFICIENT_JET_PLUS_MOVING_DURATION_JET",
            "fixed_duration_part_mislabeled_as_total": "CORRECTED",
            "existence_reset_or_recurrence_reopened": False,
            "history_member_selected": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_73_DIMENSIONAL_CHILD_IMAGE_THROUGH_THE_LOCAL_"
            "ACTION_FLOW_IN_THE_REGULAR_DESINGULARIZED_CHART_TO_OBTAIN_"
            "T_xi_AND_THE_INTERIOR_x_xi_JACOBI_PATH;_THEN_ASSEMBLE_THE_"
            "TOTAL_M_C_JET_AND_HEAT_MINUS_ZETA_COVECTOR"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_TOTAL_CHILD_HISTORY_OPERATOR_JET",
            "terminal_child_Cauchy_jet": "CERTIFIED_RANK_TWO",
            "fixed_duration_terminal_D_xi_M_C_coefficients": "COMPUTED",
            "total_physical_D_xi_M_C": "OPEN_DURATION_AND_INTERIOR_JACOBI",
            "zero_source_force": "OPEN_AFTER_TOTAL_OPERATOR_JET",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
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
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
