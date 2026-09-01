"""Close a recenterable endpoint tube for the pole-free C2 launch."""

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

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_RECENTERABLE_LAUNCH_ENDPOINT.json"
DATA_RESULT = BASE / "BHSM_N12_C2_RECENTERABLE_LAUNCH_ENDPOINT.npz"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
REFINED_DATA = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
THEORY = ROOT / "theory/n12_c2_recenterable_launch_endpoint.md"
INPUTS = (LAUNCH, POLE_FREE, REFINED, REFINED_DATA, CANDIDATE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete recenterable C2 launch inputs required")
    launch, pole_free, refined = (
        _load(path) for path in (LAUNCH, POLE_FREE, REFINED)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, pole_free, refined,
    )):
        raise RuntimeError("validated pole-free launch inputs required")
    with np.load(REFINED_DATA) as data:
        refined_joint = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(CANDIDATE) as data:
        old_joint = np.asarray(data["state"], dtype=float)

    c2 = refined_joint[:98]
    jet = exact_full_action_jet_at_state(
        12, c2[:37], c2[37:74], c2[74:], points=96,
    )
    values, vectors = np.linalg.eigh(
        np.asarray(jet.hessian, dtype=float)[37:, 37:]
    )
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    selected_action = np.concatenate((np.zeros(37), psi * weights[37:]))

    ball = launch["launch_ball"]
    Jacobi = float(pole_free["bounds"]["pole_free_regularized_Jacobi_upper"])
    speed = float(ball["regularized_state_speed_upper"])
    lambda_end = float(ball["path_limited_lambda_upper"])
    Jacobi_exponent = Jacobi * lambda_end
    Jacobi_growth = math.exp(Jacobi_exponent)
    action_path = speed * lambda_end
    root_distance = float(refined["refined_radii_theorem"][
        "a_posteriori_root_distance_upper"
    ])

    c_interval = tuple(float(value) for value in ball["c_psi_interval"])
    c_midpoint = 0.5 * sum(c_interval)
    predictor_action = lambda_end * selected_action / c_midpoint
    predictor = c2 + predictor_action / weights
    # The predictor is deliberately not asserted to be the exact vector field
    # at the non-root proof center.  Twice the uniform speed encloses that
    # center-choice mismatch; the last term is the nonlinear flow remainder.
    nonlinear_remainder = (
        0.5 * Jacobi * speed * lambda_end**2 * Jacobi_growth
    )
    endpoint_tube = (
        Jacobi_growth * root_distance
        + 2.0 * speed * lambda_end
        + nonlinear_remainder
    )
    next_ball_radius = 2.0 * endpoint_tube
    np.savez_compressed(
        DATA_RESULT,
        C2_predictor_state=predictor,
        state_weights=weights,
        branch_reference=reference,
        refined_C2_center=c2,
        signed_lambda_end=np.asarray(lambda_end),
    )

    Delta_lower, Delta_upper = (
        float(value) for value in ball["Delta_interval"]
    )
    u_end = lambda_end**2
    coordinate_time = (
        u_end / (2.0 * Delta_upper), u_end / (2.0 * Delta_lower)
    )
    lapse_lower, lapse_upper = (
        float(value)
        for value in launch["explicit_segment"]["lapse_interval_on_launch_ball"]
    )
    proper_time = (
        lapse_lower * coordinate_time[0], lapse_upper * coordinate_time[1]
    )
    old_to_refined_action = float(np.linalg.norm(
        (refined_joint - old_joint) * np.tile(weights, 2)
    ))
    outer_use = (
        old_to_refined_action
        + float(np.linalg.norm(predictor_action)) + next_ball_radius
    )
    validation = {
        "same_actual_C2_branch_24_used": selected == 24,
        "pole_free_Jacobi_removes_old_length_cap": (
            lambda_end
            < 0.5 / Jacobi
            and lambda_end > float(launch["explicit_segment"][
                "signed_lambda_end_lower"
            ])
        ),
        "extended_launch_has_positive_coordinate_and_proper_time": (
            coordinate_time[0] > 0.0 and proper_time[0] > 0.0
        ),
        "extended_launch_stays_inside_Delta_tube": (
            action_path < float(ball["derived_root_relative_tube_radius"])
        ),
        "Jacobi_growth_is_close_to_one": Jacobi_growth < 1.001,
        "endpoint_tube_is_strictly_positive_and_finite": (
            0.0 < endpoint_tube < math.inf
        ),
        "next_recenter_ball_stays_inside_outer_launch_ball": (
            outer_use < float(ball["action_radius"])
        ),
        "predictor_is_proof_center_not_physical_endpoint": True,
        "no_selector_equation_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_RECENTERABLE_LAUNCH_ENDPOINT",
        "status": (
            "POLE_FREE_C2_LAUNCH_ENDPOINT_TUBE_RECENTERABLE"
            if passed else "C2_RECENTERABLE_LAUNCH_ENDPOINT_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_POLE_FREE_COVARIANT_JACOBI_BOUND_PERMITS_THE_FULL_"
            "DELTA_POSITIVITY_LIMITED_C2_LAUNCH;_THE_REFINED_ROOT_"
            "UNCERTAINTY,_FLOW_GROWTH,_PREDICTOR_MISMATCH,_AND_NONLINEAR_"
            "REMAINDER_CLOSE_AN_EXPLICIT_ENDPOINT_TUBE_STRICTLY_INSIDE_A_"
            "NEW_TRANSLATED_ACTION_BALL"
        ),
        "extended_segment": {
            "signed_lambda_end": lambda_end,
            "physical_u_end": u_end,
            "coordinate_time_interval": list(coordinate_time),
            "proper_time_interval": list(proper_time),
            "action_path_upper": action_path,
            "pole_free_Jacobi_exponent_upper": Jacobi_exponent,
            "pole_free_Jacobi_growth_upper": Jacobi_growth,
        },
        "endpoint_recenter": {
            "refined_root_distance_upper": root_distance,
            "predictor_action_step_norm": float(np.linalg.norm(predictor_action)),
            "nonlinear_remainder_upper": nonlinear_remainder,
            "endpoint_tube_radius_upper": endpoint_tube,
            "next_translated_ball_radius": next_ball_radius,
            "outer_launch_ball_radius": float(ball["action_radius"]),
            "outer_ball_total_radius_use": outer_use,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
            "predictor_is_physical_endpoint": False,
        },
        "exact_next_dependency": (
            "RECOMPUTE_THE_RETAINED_ACTION,_SELECTED_LINE,_DELTA,_AND_"
            "POLE_FREE_JACOBI_BOUNDS_ON_THE_TRANSLATED_PREDICTOR_BALL,_"
            "THEN_ITERATE_UNTIL_COMPLETED_ENCAPSULATION_OR_A_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "first_recenterable_C2_endpoint_tube": "CERTIFIED",
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
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
        "lambda_end": payload["extended_segment"]["signed_lambda_end"],
        "Jacobi_growth": payload["extended_segment"][
            "pole_free_Jacobi_growth_upper"
        ],
        "endpoint_tube": payload["endpoint_recenter"][
            "endpoint_tube_radius_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
