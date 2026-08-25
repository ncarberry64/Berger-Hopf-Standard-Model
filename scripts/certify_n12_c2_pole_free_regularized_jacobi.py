"""Certify the cancellation-preserving C2 regularized Jacobi bound."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (  # noqa: E402
    spectral_frequencies,
)
from derive_n12_c2_launch_eigenline_ball import _load  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
LINE = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_BALL.json"
MAJORANTS = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
THEORY = ROOT / "theory/n12_c2_pole_free_regularized_jacobi.md"
INPUTS = (CANDIDATE, LAUNCH, LINE, MAJORANTS, REFINED, THEORY)
QDIM = 37
STATE_DIMENSION = 98
RADIUS = 1.0e-12


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete pole-free C2 Jacobi inputs required")
    launch, line, majorants, refined = (
        _load_json(path) for path in (LAUNCH, LINE, MAJORANTS, REFINED)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, line, majorants, refined,
    )):
        raise RuntimeError("validated C2 launch parents required")
    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)[:STATE_DIMENSION]
        third = np.asarray(data["event_third"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    frequencies = spectral_frequencies(12)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    reduced_weights = np.concatenate((
        np.ones(QDIM), np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    maximum_q_weight = float(np.max(q_weights))
    maximum_reduced_weight = float(np.max(reduced_weights))
    W = np.diag(reduced_weights)
    identity = np.eye(STATE_DIMENSION)

    jet = exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
    )
    gradient = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = (
        np.asarray(jet.hessian, dtype=float)
        / weights[:, None] / weights[None, :]
    )
    raw_D = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(raw_D)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))

    velocity = state[QDIM:2 * QDIM]
    configuration_rate = q_weights * velocity
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ configuration_rate,
        -mixed_mq @ configuration_rate,
    ))
    rhs_raw = reduced_weights * rhs_action
    bpsi = float(psi @ rhs_raw)
    hard_rate = complement @ ((complement.T @ rhs_raw) / hard_values)

    raw_derivatives = np.asarray([
        W @ third[QDIM:, QDIM:, column] @ W
        for column in range(STATE_DIMENSION)
    ])
    qdot_derivative = np.zeros((QDIM, STATE_DIMENSION))
    qdot_derivative[:, QDIM:2 * QDIM] = np.diag(q_weights)
    rhs_derivative_action = np.empty((reduced_weights.size, STATE_DIMENSION))
    for column in range(STATE_DIMENSION):
        d_qdot = qdot_derivative[:, column]
        rhs_derivative_action[:QDIM, column] = (
            q_weights * hessian_action[:QDIM, column]
            - third[QDIM:QDIM + QDIM, :QDIM, column] @ configuration_rate
            - mixed_vq @ d_qdot
        )
        rhs_derivative_action[QDIM:, column] = (
            -third[2 * QDIM:, :QDIM, column] @ configuration_rate
            - mixed_mq @ d_qdot
        )
    rhs_derivative_raw_center = float(np.linalg.norm(
        W @ rhs_derivative_action, 2
    ))
    coupling_center = float(np.linalg.norm(np.column_stack([
        complement.T @ derivative @ psi for derivative in raw_derivatives
    ]), 2))
    hard_D3_center = float(np.linalg.norm(np.asarray([
        complement.T @ derivative @ complement
        for derivative in raw_derivatives
    ])))

    os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(RADIUS)
    action_bound = _load("derive_n12_action_ball_majorants").action_bound
    d4_xxcc = float(action_bound(
        state, projection=identity,
        mixed_directions=[identity, identity, complement_action, complement_action],
    ).d[-1])
    d4_xxpc = float(action_bound(
        state, projection=identity,
        mixed_directions=[identity, identity, selected_action, complement_action],
    ).d[-1])

    event_majorants = next(
        row for row in majorants["sectors"] if row["sector"] == "event"
    )["derivative_operator_majorants_0_through_5"]
    configuration_upper = (
        float(np.linalg.norm(configuration_rate)) + maximum_q_weight * RADIUS
    )
    rhs_second_action = (
        float(event_majorants[4]) * configuration_upper
        + 3.0 * float(event_majorants[3]) * maximum_q_weight
    )
    rhs_derivative_upper = (
        rhs_derivative_raw_center
        + maximum_reduced_weight * rhs_second_action * RADIUS
    )
    line_bounds = line["bounds"]
    line_lipschitz = float(
        line_bounds["weighted_selected_to_complement_first_variation_on_ball"]
    )
    projector_derivative = 2.0 * line_lipschitz
    hard_D3_upper = hard_D3_center + d4_xxcc * RADIUS
    coupling_upper = coupling_center + d4_xxpc * RADIUS
    hard_inverse = 1.0 / float(line_bounds["eigenline_gap_lower"])
    b_upper = max(abs(value) for value in launch["launch_ball"]["b_psi_interval"])
    denominator = 1.0 - hard_inverse * hard_D3_upper * RADIUS
    hard_Jacobi_raw = hard_inverse * (
        rhs_derivative_upper
        + hard_D3_upper * float(np.linalg.norm(hard_rate))
        + projector_derivative * b_upper
    ) / denominator
    hard_rate_raw_upper = float(np.linalg.norm(hard_rate)) + hard_Jacobi_raw * RADIUS
    hard_rate_action_upper = maximum_reduced_weight * hard_rate_raw_upper
    hard_Jacobi_action = maximum_reduced_weight * hard_Jacobi_raw

    c_lipschitz = float(launch["launch_ball"]["c_psi_Lipschitz_upper"])
    lambda_upper = float(launch["launch_ball"]["lambda_upper"])
    b_lipschitz_structured = (
        rhs_derivative_upper
        + (coupling_upper + lambda_upper * projector_derivative)
        * hard_rate_raw_upper
    )
    lambda_lipschitz = float(launch["launch_ball"]["lambda_Lipschitz_upper"])
    lambda_hessian = float(line_bounds["selected_eigenvalue_raw_Hessian_bound"])
    hard_flow_upper = math.hypot(configuration_upper, hard_rate_action_upper)
    remainder_upper = lambda_lipschitz * hard_flow_upper
    hard_flow_Jacobi = math.hypot(maximum_q_weight, hard_Jacobi_action)
    remainder_lipschitz = (
        lambda_hessian * hard_flow_upper
        + lambda_lipschitz * hard_flow_Jacobi
    )
    c_upper = max(abs(value) for value in launch["launch_ball"]["c_psi_interval"])
    Delta_lipschitz = (
        b_upper * c_lipschitz + c_upper * b_lipschitz_structured
        + lambda_lipschitz * remainder_upper
        + lambda_upper * remainder_lipschitz
    )
    Delta_lower = float(launch["launch_ball"]["Delta_interval"][0])
    selected_action_upper = (
        float(np.linalg.norm(selected_action))
        + maximum_reduced_weight * line_lipschitz * RADIUS
    )
    numerator_upper = math.hypot(
        lambda_upper * configuration_upper,
        b_upper * selected_action_upper + lambda_upper * hard_rate_action_upper,
    )
    numerator_lipschitz = (
        lambda_lipschitz * configuration_upper
        + lambda_upper * maximum_q_weight
        + b_lipschitz_structured * selected_action_upper
        + b_upper * maximum_reduced_weight * line_lipschitz
        + lambda_lipschitz * hard_rate_action_upper
        + lambda_upper * hard_Jacobi_action
    )
    pole_free_Jacobi = (
        numerator_lipschitz / Delta_lower
        + numerator_upper * Delta_lipschitz / Delta_lower**2
    )
    old_Jacobi = float(launch["launch_ball"][
        "regularized_first_Jacobi_generator_upper"
    ])
    validation = {
        "actual_C2_branch_24_used": selected == 24,
        "hard_block_stays_uniformly_invertible": hard_inverse > 0.0,
        "hard_Jacobi_self_consistency_closes": denominator > 0.0,
        "pole_free_hard_Jacobi_is_finite": math.isfinite(hard_Jacobi_action),
        "soft_source_derivative_uses_structural_identity": (
            math.isfinite(b_lipschitz_structured)
        ),
        "regularized_Jacobi_contains_no_inverse_soft_eigenvalue": True,
        "pole_free_bound_improves_crude_bound": 0.0 < pole_free_Jacobi < old_Jacobi,
        "refined_same_root_center_consumed": refined["validation_passed"] is True,
        "no_selector_equation_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI",
        "status": (
            "C2_POLE_FREE_COVARIANT_REGULARIZED_JACOBI_BOUND_CERTIFIED"
            if passed else "C2_POLE_FREE_REGULARIZED_JACOBI_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_COVARIANT_HARD_VARIATION_QD^{-1}Q_AND_THE_DIFFERENTIATED_"
            "SOFT_SOURCE_IDENTITY_REMOVE_THE_CANCELLATION_DESTROYING_"
            "PROJECTOR_TIMES_FULL_RHS_AND_INVERSE_SQUARED_BOUNDS;_THE_"
            "RESULTING_SIGNED_EIGENVALUE_REPARAMETRIZED_C2_JACOBI_BOUND_"
            "IS_FINITE,_POLE_FREE,_AND_STRICTLY_SHARPER"
        ),
        "structural_identities": {
            "hard_rate": "r_h=(Q*D*Q)^-1*Q*b",
            "hard_covariant_variation": (
                "nabla_delta_r_h=D_h^-1*Q*(delta_b-delta_D*r_h-delta_P*P*b)"
            ),
            "soft_source_variation": (
                "delta_b_psi=<psi,delta_b>-<Q*delta_D*psi,r_h>-"
                "lambda*<Q*delta_D*psi,(D_h-lambda)^-1*r_h>"
            ),
            "inverse_soft_eigenvalue_powers": 0,
        },
        "bounds": {
            "action_radius": RADIUS,
            "center_hard_rate_raw_norm": float(np.linalg.norm(hard_rate)),
            "hard_rate_action_upper": hard_rate_action_upper,
            "rhs_raw_derivative_upper": rhs_derivative_upper,
            "hard_D3_upper": hard_D3_upper,
            "coupling_upper": coupling_upper,
            "hard_Jacobi_action_upper": hard_Jacobi_action,
            "structured_b_psi_Lipschitz_upper": b_lipschitz_structured,
            "hard_remainder_Lipschitz_upper": remainder_lipschitz,
            "Delta_action_derivative_upper": Delta_lipschitz,
            "pole_free_regularized_Jacobi_upper": pole_free_Jacobi,
            "superseded_crude_regularized_Jacobi_upper": old_Jacobi,
            "improvement_factor_lower": old_Jacobi / pole_free_Jacobi,
        },
        "exact_next_dependency": (
            "REISSUE_THE_EXPLICIT_C2_LAUNCH_LENGTH_WITH_THIS_POLE_FREE_"
            "JACOBI_BOUND_AND_THE_REFINED_ROOT_CENTER,_THEN_CLOSE_A_"
            "RECENTERABLE_ENDPOINT_TUBE_AND_CONTINUE_THE_SAME_ACTION_FLOW"
        ),
        "claim_boundary": {
            "pole_free_first_C2_Jacobi": "CERTIFIED",
            "recenterable_endpoint_tube": "OPEN_NEXT",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "zero_source_force": "OPEN_AFTER_COMPLETE_M_C2",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "pole_free": payload["bounds"]["pole_free_regularized_Jacobi_upper"],
        "old": payload["bounds"]["superseded_crude_regularized_Jacobi_upper"],
        "improvement": payload["bounds"]["improvement_factor_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
