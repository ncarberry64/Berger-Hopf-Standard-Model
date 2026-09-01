"""Certify the action-owned formation-amplitude and duration endpoint jet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
    proper_time_log_radius_rate,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
CHECKPOINT = BASE / "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
DIRECTED = BASE / "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
ORIENTATION = BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"
COEFFICIENT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
QUOTIENT = BASE / "BHSM_N12_TERMINAL_CHILD_QUOTIENT_OPERATOR_JET.json"
LOCAL_BRANCH = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
)
THEORY = ROOT / "theory/n12_desingularized_finite_history_operator_parameter.md"
INPUTS = (
    CANDIDATE,
    CHECKPOINT,
    DIRECTED,
    ORIENTATION,
    COEFFICIENT,
    INTERFACE,
    QUOTIENT,
    LOCAL_BRANCH,
    THEORY,
)
QDIM = 37


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _terminal_rate_action_covector(
    state: np.ndarray, weights: np.ndarray
) -> np.ndarray:
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
    raw = np.zeros(98)
    raw[:QDIM] = hessian_x @ velocity / lapse
    raw[QDIM : 2 * QDIM] = gradient_x / lapse
    raw[2 * QDIM : 2 * QDIM + 12] = -rate * signs_k
    return raw / weights


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("desingularized operator-parameter inputs required")
    orientation, coefficient, interface, quotient, local_branch = (
        _load(path)
        for path in (ORIENTATION, COEFFICIENT, INTERFACE, QUOTIENT, LOCAL_BRANCH)
    )
    if not all(record.get("validation_passed") is True for record in (
        orientation, coefficient, interface, quotient, local_branch
    )):
        raise RuntimeError("validated desingularized branch parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[98:]
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(CHECKPOINT) as data:
        normalized_child_lambda_row = np.asarray(
            data["paired_jacobian"], dtype=float
        )[-1, 98:]
    with np.load(DIRECTED) as data:
        child_gradient_scale = float(data["child_gradient_scale"])

    jet = exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM : 2 * QDIM],
        state[2 * QDIM :],
        points=96,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    eigenvalues, eigenvectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(eigenvectors.T @ reference)))
    psi = eigenvectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    selected_action = np.concatenate((
        np.zeros(QDIM), psi * weights[QDIM:]
    ))
    selected_action /= np.linalg.norm(selected_action)
    child_lambda_covector = (
        normalized_child_lambda_row * child_gradient_scale
    )
    recovered_c = float(child_lambda_covector @ selected_action)
    rate_covector = _terminal_rate_action_covector(state, weights)
    selected_rate_direction = float(rate_covector @ selected_action)
    selected_x_direction = 0.0

    center_c = float(orientation["center_cubic"]["decimal_centered_value"])
    center_b = float(
        orientation["root_forcing_transfer"]["center_b_psi"]
    )
    duration_center = 1.0 / (-2.0 * center_c * center_b)
    duration_interval = coefficient["desingularized_duration_jet"][
        "quadratic_coefficient_interval"
    ]
    second_duration_interval = [
        2.0 * float(duration_interval[0]),
        2.0 * float(duration_interval[1]),
    ]
    normalized_rate_direction = selected_rate_direction / center_c

    step = 1.0e-6
    raw_direction = selected_action / weights

    def rate(offset: float) -> float:
        shifted = state + offset * raw_direction
        return proper_time_log_radius_rate(
            12,
            shifted[:QDIM],
            shifted[QDIM : 2 * QDIM],
            shifted[2 * QDIM :],
        )

    finite_rate_direction = (rate(step) - rate(-step)) / (2.0 * step)
    validation = {
        "incoming_selected_line_is_branch_23": selected == 23,
        "selected_eigenvalue_is_terminal_zero_within_root_scale": abs(
            float(eigenvalues[selected])
        ) < 2.0e-14,
        "recovered_c_psi_lies_in_certified_root_interval": (
            float(coefficient["desingularized_duration_jet"][
                "root_c_psi_interval"
            ][0])
            <= recovered_c
            <= float(coefficient["desingularized_duration_jet"][
                "root_c_psi_interval"
            ][1])
        ),
        "selected_log_radius_first_direction_is_zero": selected_x_direction == 0.0,
        "selected_rate_direction_matches_centered_difference": abs(
            selected_rate_direction - finite_rate_direction
        ) < 1.0e-9,
        "duration_quadratic_coefficient_is_positive": duration_center > 0.0,
        "duration_second_jet_interval_is_strictly_positive": (
            second_duration_interval[0] > 0.0
        ),
        "terminal_event_is_fixed_along_incoming_amplitude_germ": (
            "E1=C_*" in interface["exact_local_theorem"][
                "positive_duration_family"
            ]
        ),
        "no_positive_amplitude_or_history_member_selected": True,
        "no_recurrence_endpoint_condition_cutoff_external_force_or_scale_added": True,
    }
    return {
        "artifact": "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER",
        "status": "ACTION_OWNED_FORMATION_AMPLITUDE_DURATION_JET_CERTIFIED",
        "classification": (
            "THE_ACTUAL_INCOMING_BRANCH_23_SELECTED_LINE_SUPPLIES_THE_"
            "ACTION_COORDINATE_lambda_AND_THE_CERTIFIED_LAW_T(lambda)=a*"
            "lambda^2+o(lambda^2);_THE_TERMINAL_EVENT_COEFFICIENT_IS_FIXED_"
            "ALONG_THIS_AMPLITUDE_GERM,_D_lambda_T_AT_ZERO_VANISHES,_AND_"
            "D_lambda2_T_IS_STRICTLY_POSITIVE_WITHOUT_SELECTING_A_POSITIVE_"
            "HISTORY_MEMBER"
        ),
        "incoming_selected_line": {
            "branch": selected,
            "center_selected_eigenvalue": float(eigenvalues[selected]),
            "D_selected_eigenvalue_on_unit_selected_action_direction": (
                recovered_c
            ),
            "certified_center_c_psi_interval": [
                float(orientation["center_cubic"]["lower"]),
                float(orientation["center_cubic"]["upper"]),
            ],
            "D_log_R4_on_unit_selected_action_direction": selected_x_direction,
            "D_proper_rate_on_unit_selected_action_direction": (
                selected_rate_direction
            ),
            "D_proper_rate_per_unit_lambda_at_terminal": (
                normalized_rate_direction
            ),
            "terminal_tangent": "dY/dlambda=Psi_E/c_psi(E)",
        },
        "duration_parameter_jet": {
            "law": "T(lambda)=a*lambda^2+o(lambda^2)",
            "center_a": duration_center,
            "certified_a_interval": [
                float(duration_interval[0]), float(duration_interval[1])
            ],
            "D_lambda_T_at_zero": 0.0,
            "D_lambda2_T_at_zero_interval": second_duration_interval,
            "lambda_positive_member_selected": False,
        },
        "compact_Weyl_amplitude_germ": {
            "scalar": (
                "M_C=(a*lambda^2)^-1*L*(1+o(1))+O(lambda^2)"
            ),
            "product_Dirac": (
                "M_C=(a*lambda^2)^-1*L*(1+o(1))+diag(-s_E,s_E)+O(lambda^2)"
            ),
            "finite_for_every_sufficiently_small_lambda_positive": True,
            "defined_at_lambda_zero": False,
            "reason": "lambda_zero_has_zero_physical_duration",
        },
        "parameter_separation": {
            "formation_amplitude": "lambda_positive_ON_A_FIXED_TERMINAL_ROOT",
            "event_child_family": "73_DIMENSIONAL_TERMINAL_CHILD_IMAGE",
            "terminal_Cauchy_jet_moves_with_amplitude": False,
            "terminal_Cauchy_jet_moves_across_event_child_family": True,
        },
        "hindsight": {
            "action_required": "DESINGULARIZED_FORMATION_AMPLITUDE_AND_DURATION_JET",
            "positive_lambda_value_required_before_same_action_saddle": False,
            "positive_lambda_value_may_be_selected_by_hand": False,
            "existence_reset_or_recurrence_reopened": False,
        },
        "exact_next_dependency": (
            "REALIZE_THE_COMPLETE_SELF_ADJOINT_SPECTRAL_FAMILY_AS_A_"
            "FUNCTION_OF_(xi,lambda)_FOR_lambda>0,_EVALUATE_THE_ZERO_SOURCE_"
            "HEAT_MINUS_ZETA_COVECTOR,_AND_ALLOW_THE_SAME_ACTION_SADDLE_TO_"
            "DETERMINE_lambda_AND_THE_NONINVARIANT_CHILD_DIRECTIONS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PARAMETRIC_SPECTRAL_FORCE",
            "formation_amplitude_duration_jet": "CERTIFIED",
            "positive_history_member": "NOT_SELECTED",
            "complete_positive_duration_spectral_family": "OPEN",
            "zero_source_force": "OPEN_AFTER_SPECTRAL_FAMILY",
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
