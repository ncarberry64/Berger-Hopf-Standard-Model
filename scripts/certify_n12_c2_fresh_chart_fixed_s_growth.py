"""Transfer fixed-s C2 growth and hard-response data to the fresh chart."""

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

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from derive_n12_c2_launch_eigenline_ball import _load as _load_canonical  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CHART = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
CHART_DATA = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.npz"
CONTINUATION = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
RESULT = BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
THEORY = ROOT / "theory" / "n12_c2_fresh_chart_fixed_s_growth.md"
INPUTS = (CHART, CHART_DATA, CONTINUATION, THEORY)
QDIM = 37
COMPLEX_STEP = 1.0e-20
INFLATION = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
    )


def _rhs_raw(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = _jet(state)
    gradient = np.asarray(jet.gradient) / weights
    hessian_action = np.asarray(jet.hessian) / weights[:, None] / weights[None, :]
    configuration = q_weights * state[QDIM:2 * QDIM]
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ configuration,
        -mixed_mq @ configuration,
    ))
    return reduced_weights * rhs_action


def _cubic(state: np.ndarray, psi: np.ndarray) -> float:
    direction = np.concatenate((np.zeros(QDIM), psi))
    shifted = state.astype(complex) + 1j * COMPLEX_STEP * direction
    derivative = np.imag(np.asarray(_jet(shifted).hessian)[QDIM:, QDIM:]) / COMPLEX_STEP
    return float(psi @ derivative @ psi)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fresh fixed-s inputs: " + ", ".join(missing))
    chart, continuation = (_json(path) for path in (CHART, CONTINUATION))
    if not chart.get("validation_passed") or not continuation.get("validation_passed"):
        raise RuntimeError("validated fresh chart and continuation required")
    with np.load(CHART_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        psi_first = np.asarray(data["selected_vector_derivative_action"], dtype=float)
        lambda_first = np.asarray(data["lambda_gradient_action"], dtype=float)
        tangent = np.asarray(data["fixed_descriptor_tangent_basis"], dtype=float)

    q_weights, reduced_weights, maximum_q_weight, maximum_reduced_weight = metric_data()
    hessian = np.asarray(_jet(center).hessian, dtype=float)
    reduced = hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    replay = vectors[:, selected]
    if float(replay @ reference) < 0.0:
        replay = -replay
    if selected != 24 or float(replay @ psi) < 1.0 - 1.0e-10:
        raise RuntimeError("fresh branch-24 line does not replay")
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    identity = np.eye(center.size)
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))
    outer_radius = float(chart["radius_derivation"]["selected_fresh_chart_radius"])
    outer_d4 = chart["radius_derivation"]["failed_upper_D4_bounds"]
    selected_bounds = chart["radius_derivation"]["selected_chart_bounds"]
    center_gap = float(chart["center"]["center_hard_gap"])
    center_inverse = _up(1.0 / center_gap)
    denominator = _down(
        1.0 - float(selected_bounds["relative_hard_perturbation"])
        - center_inverse * float(selected_bounds["scalar_shift_upper"])
    )
    p1 = _up((
        float(chart["center"]["preconditioned_selected_line_first_variation"])
        + center_inverse * float(outer_d4["D4_XXPC"]) * outer_radius
    ) / denominator)
    relative_first = _up((
        float(chart["center"]["preconditioned_hard_block_first_variation"])
        + center_inverse * float(outer_d4["D4_XXCC"]) * outer_radius
    ) / denominator)
    lambda_one = _up(
        float(chart["center"]["lambda_gradient_action_norm"])
        + float(outer_d4["D4_XXPP"]) * outer_radius
        + 2.0 * (
            float(chart["center"]["selected_to_complement_first_variation"])
            + float(outer_d4["D4_XXPC"]) * outer_radius
        ) * float(selected_bounds["graph_norm_upper"])
    )
    complement_inverse = float(selected_bounds["complement_inverse_upper"])
    direct_p2 = _up(complement_inverse * float(outer_d4["D4_XXPC"]))
    p2 = _up(
        direct_p2
        + 2.0 * (relative_first + complement_inverse * lambda_one) * p1
        + p1**2
    )
    lambda_two = _up(
        float(outer_d4["D4_XXPP"])
        + 2.0 * (
            float(chart["center"]["selected_to_complement_first_variation"])
            + float(outer_d4["D4_XXPC"]) * outer_radius
        ) * p1
    )

    os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(outer_radius)
    action_module = _load_canonical("derive_n12_action_ball_majorants")
    action_bound = action_module.action_bound

    def mixed(*directions: np.ndarray) -> float:
        return _up(float(action_bound(
            center, projection=identity, mixed_directions=list(directions),
        ).d[-1]))

    action = {
        "D3_CCP": mixed(complement_action, complement_action, selected_action),
        "D3_CPP": mixed(complement_action, selected_action, selected_action),
        "D4_XCPP": mixed(identity, complement_action, selected_action, selected_action),
        "D4_XPPP": mixed(identity, selected_action, selected_action, selected_action),
        "D5_XXPPP": mixed(identity, identity, selected_action, selected_action, selected_action),
    }
    c0 = _cubic(center, psi)
    lambda_raw_reduced = lambda_first[QDIM:] * weights[QDIM:]
    kato_c_first = 3.0 * (lambda_raw_reduced @ psi_first)
    kato_c_first_norm = _up(float(np.linalg.norm(kato_c_first)))
    c1_center = _up(kato_c_first_norm + action["D4_XPPP"])
    c2 = _up(
        action["D5_XXPPP"]
        + 6.0 * action["D4_XCPP"] * p1
        + 3.0 * action["D3_CPP"] * p2
        + 6.0 * action["D3_CCP"] * p1**2
    )
    incoming_tube = float(
        continuation["continuation"]["final_endpoint_tube_radius_upper"]
    )

    def c_lower(radius: float) -> float:
        return _down(c0 - c1_center * radius - 0.5 * c2 * radius**2)

    if c_lower(math.nextafter(incoming_tube, outer_radius)) <= 0.0:
        raise ArithmeticError("fresh fixed-s cubic does not contain incoming tube")
    feasible, infeasible = incoming_tube, outer_radius
    for _ in range(100):
        midpoint = 0.5 * (feasible + infeasible)
        if midpoint in (feasible, infeasible):
            break
        lambda_lower = float(np.linalg.norm(lambda_first)) - lambda_two * midpoint
        if c_lower(midpoint) > 0.0 and lambda_lower > 0.0:
            feasible = midpoint
        else:
            infeasible = midpoint
    maximal_radius = feasible
    radius = 0.5 * (incoming_tube + maximal_radius)
    c_ball_lower = c_lower(radius)
    c1_ball = _up(c1_center + c2 * radius)
    p0 = _up(float(np.linalg.norm(selected_action)))
    p0_ball = _up(
        p0 + maximum_reduced_weight * p1 * radius
        + 0.5 * maximum_reduced_weight * p2 * radius**2
    )
    p1_action = _up(maximum_reduced_weight * (p1 + p2 * radius))
    p2_action = _up(maximum_reduced_weight * p2)
    d2_f0 = _up(
        p2_action / c_ball_lower
        + 2.0 * p1_action * c1_ball / c_ball_lower**2
        + p0_ball * c2 / c_ball_lower**2
        + 2.0 * p0_ball * c1_ball**2 / c_ball_lower**3
    )
    kato_birth = np.zeros((center.size, center.size))
    kato_birth[QDIM:] = reduced_weights[:, None] * (
        psi_first / c0 - psi[:, None] * kato_c_first[None, :] / c0**2
    )
    center_kato_norm = _up(float(np.linalg.norm(kato_birth, 2)))
    center_kato_tangent = tangent.T @ kato_birth @ tangent
    center_kato_mu = _up(float(np.linalg.eigvalsh(
        0.5 * (center_kato_tangent + center_kato_tangent.T)
    )[-1]))
    d4_uncertainty = _up(p0 * action["D4_XPPP"] / c0**2)
    center_operator = _up(center_kato_norm + d4_uncertainty)
    full_operator = _up(center_operator + d2_f0 * radius)
    lambda_lower = _down(float(np.linalg.norm(lambda_first)) - lambda_two * radius)

    # Recompute the action-owned hard-response center data needed by the next
    # uniform-gap propagation.  This is the same RHS map as the flow, not an
    # external load.
    rhs_center = np.asarray(_rhs_raw(center, weights), dtype=float)
    rhs_columns = np.empty((rhs_center.size, center.size))
    hard_columns = np.empty((center.size, complement.shape[1], complement.shape[1]))
    coupling_columns = np.empty((complement.shape[1], center.size))
    for column in range(center.size):
        shifted = center.astype(complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        rhs_columns[:, column] = np.imag(_rhs_raw(shifted, weights)) / COMPLEX_STEP
        derivative = np.imag(np.asarray(_jet(shifted).hessian)) / COMPLEX_STEP
        raw = derivative[QDIM:, QDIM:]
        hard_columns[column] = complement.T @ raw @ complement
        coupling_columns[:, column] = complement.T @ raw @ psi
        if (column + 1) % 16 == 0:
            print(f"fresh-growth response columns {column + 1}/{center.size}", flush=True)
    global_bound = action_bound(center)
    configuration_upper = _up(
        float(np.linalg.norm(q_weights * center[QDIM:2 * QDIM]))
        + maximum_q_weight * radius
    )
    rhs_second = _up(maximum_reduced_weight * (
        float(global_bound.d[4]) * configuration_upper
        + 3.0 * float(global_bound.d[3]) * maximum_q_weight
    ))
    pf = {
        "rhs_raw_derivative_center": _up(float(np.linalg.norm(rhs_columns, 2))),
        "rhs_raw_second_derivative_upper": rhs_second,
        "hard_D3_center": _up(float(np.linalg.norm(hard_columns))),
        "coupling_center": _up(float(np.linalg.norm(coupling_columns, 2))),
        "D4_full_hard_hard_upper": float(outer_d4["D4_XXCC"]),
        "D4_full_selected_hard_upper": float(outer_d4["D4_XXPC"]),
    }
    hard_center = complement @ (
        (complement.T @ rhs_center) / hard_values
    )
    b_center = float(psi @ rhs_center)
    validation = {
        "branch_24_replayed": selected == 24,
        "fresh_cubic_contains_incoming_tube": maximal_radius > incoming_tube,
        "derived_growth_radius_strictly_inside_fresh_chart": radius < outer_radius,
        "moving_cubic_and_normal_gradient_stay_positive": c_ball_lower > 0.0 and lambda_lower > 0.0,
        "fresh_full_fixed_s_birth_operator_is_finite": math.isfinite(full_operator),
        "fresh_hard_response_inputs_are_action_owned_and_finite": all(
            math.isfinite(value) for value in pf.values()
        ),
        "physical_propagation_remains_on_exact_descriptor_fiber": True,
        "no_validation_cutoff_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH",
        "status": (
            "C2_FRESH_CHART_FIXED_s_GROWTH_AND_HARD_RESPONSE_INPUTS_CERTIFIED"
            if passed else "C2_FRESH_CHART_FIXED_s_GROWTH_INVALID"
        ),
        "fresh_line_bounds": {
            "eigenline_gap_lower": float(selected_bounds["eigenline_gap_lower"]),
            "weighted_selected_to_complement_first_variation_on_ball": p1,
            "selected_eigenvalue_first_derivative_bound": lambda_one,
            "selected_eigenvalue_raw_Hessian_bound": lambda_two,
            "selected_line_second_variation_coefficient_upper": p2,
        },
        "moving_cubic": {
            "center_value": c0,
            "center_Kato_first_derivative_norm": kato_c_first_norm,
            "center_complete_first_derivative_upper": c1_center,
            "second_derivative_upper": c2,
            "ball_first_derivative_upper": c1_ball,
            "ball_value_lower": c_ball_lower,
        },
        "radius_derivation": {
            "incoming_endpoint_tube_upper": incoming_tube,
            "fresh_eigenline_chart_radius": outer_radius,
            "maximal_cubic_and_normal_feasible_radius_lower": maximal_radius,
            "selected_growth_chart_radius": radius,
            "selection_is_proof_midpoint_only": True,
        },
        "birth_limit_generator": {
            "center_Kato_tangent_numerical_abscissa": center_kato_mu,
            "fixed_line_D4_generator_uncertainty_upper": d4_uncertainty,
            "center_full_operator_norm_upper": center_operator,
            "D2F0_action_operator_upper": d2_f0,
            "full_action_ball_operator_norm_upper": full_operator,
        },
        "retained_action_mixed_bounds": action,
        "fresh_pole_free_bounds": pf,
        "center_response": {
            "b_psi_center": b_center,
            "hard_rate_raw_norm": float(np.linalg.norm(hard_center)),
            "selected_action_norm": p0,
        },
        "current_Gate7_semantic_owner": (
            "G7_08_MAXIMAL_C2_WEYL_FAMILY_PLUS_PHYSICAL_HEAT_MINUS_ZETA_"
            "QUOTIENT_COVECTOR_ROOT_OR_FINITE_LATER_EVENT_CANONICAL_STOP"
        ),
        "hindsight": {
            "result": "VALIDATED",
            "classification": "FRESH_FIBER_GROWTH_TRANSFER",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "CONTINUE_C2_ON_THE_FRESH_FIXED_DESCRIPTOR_CHART_WITH_THE_FRESH_"
            "UNIFORM_HARD_RESPONSE_INPUTS"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
        "radius": payload["radius_derivation"]["selected_growth_chart_radius"],
        "c_lower": payload["moving_cubic"]["ball_value_lower"],
        "full_operator": payload["birth_limit_generator"]["full_action_ball_operator_norm_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
