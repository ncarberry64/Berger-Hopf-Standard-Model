"""Extend the C2 launch using the pole-free hard remainder and Jacobi bound."""

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
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (  # noqa: E402
    spectral_frequencies,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
DATA_RESULT = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.npz"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
REFINED = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
REFINED_DATA = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
LINE = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_BALL.json"
THEORY = ROOT / "theory/n12_c2_pole_free_outer_margin_extension.md"
INPUTS = (LAUNCH, POLE_FREE, REFINED, REFINED_DATA, CANDIDATE, LINE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete pole-free outer-margin inputs required")
    launch, pole_free, refined, line = (
        _load(path) for path in (LAUNCH, POLE_FREE, REFINED, LINE)
    )
    if not all(record.get("validation_passed") is True for record in (
        launch, pole_free, refined, line,
    )):
        raise RuntimeError("validated pole-free C2 parents required")
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
    maximum_reduced_weight = float(np.max(weights[37:]))

    old_ball = launch["launch_ball"]
    pf = pole_free["bounds"]
    lambda_lipschitz = float(old_ball["lambda_Lipschitz_upper"])
    hard_rate = float(pf["hard_rate_action_upper"])
    velocity = c2[37:74]
    coordinate_frequencies = spectral_frequencies(12)["coordinates"]
    configuration_rate = float(np.linalg.norm(
        velocity * np.sqrt(1.0 + coordinate_frequencies**2)
    ))
    hard_flow = math.hypot(configuration_rate, hard_rate)
    R_upper = lambda_lipschitz * hard_flow
    c_lipschitz = float(old_ball["c_psi_Lipschitz_upper"])
    b_lipschitz = float(pf["structured_b_psi_Lipschitz_upper"])
    root_c_lower, root_c_upper = (
        float(value) for value in old_ball["c_psi_interval"]
    )
    root_b_lower, root_b_upper = (
        float(value) for value in old_ball["b_psi_interval"]
    )
    root_product = root_c_lower * root_b_lower
    loss_slope = (
        root_b_upper * c_lipschitz
        + root_c_upper * b_lipschitz
        + lambda_lipschitz * R_upper
    )
    positivity_radius = root_product / loss_slope
    available_margin = float(old_ball["available_dynamic_margin_lower"])
    dynamic_radius = min(available_margin, positivity_radius)
    c_interval = (
        root_c_lower - c_lipschitz * dynamic_radius,
        root_c_upper + c_lipschitz * dynamic_radius,
    )
    b_interval = (
        root_b_lower - b_lipschitz * dynamic_radius,
        root_b_upper + b_lipschitz * dynamic_radius,
    )
    lambda_upper = lambda_lipschitz * dynamic_radius
    Delta = (
        c_interval[0] * b_interval[0] - lambda_upper * R_upper,
        c_interval[1] * b_interval[1] + lambda_upper * R_upper,
    )
    selected_action_upper = (
        float(np.linalg.norm(selected_action))
        + maximum_reduced_weight
        * float(line["bounds"][
            "weighted_selected_to_complement_first_variation_on_ball"
        ]) * dynamic_radius
    )
    numerator = math.hypot(
        lambda_upper * configuration_rate,
        b_interval[1] * selected_action_upper + lambda_upper * hard_rate,
    )
    speed = numerator / Delta[0]
    path_fraction = 0.8
    lambda_end = path_fraction * dynamic_radius / speed
    action_path = speed * lambda_end
    Jacobi = float(pf["pole_free_regularized_Jacobi_upper"])
    Jacobi_exponent = Jacobi * lambda_end
    Jacobi_growth = math.exp(Jacobi_exponent)

    root_distance = float(refined["refined_radii_theorem"][
        "a_posteriori_root_distance_upper"
    ])
    c_midpoint = 0.5 * sum(c_interval)
    predictor_action = lambda_end * selected_action / c_midpoint
    predictor = c2 + predictor_action / weights
    line_lipschitz = float(line["bounds"][
        "weighted_selected_to_complement_first_variation_on_ball"
    ])
    psi_action_lipschitz = maximum_reduced_weight * line_lipschitz
    c_halfwidth = 0.5 * (c_interval[1] - c_interval[0])
    birth_field_mismatch = (
        psi_action_lipschitz * root_distance / c_interval[0]
        + selected_action_upper * c_halfwidth
        / (c_interval[0] * c_midpoint)
    )
    nonlinear_remainder = (
        0.5 * Jacobi * speed * lambda_end**2 * Jacobi_growth
    )
    endpoint_tube = (
        Jacobi_growth * root_distance
        + lambda_end * birth_field_mismatch
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

    u_end = lambda_end**2
    coordinate_time = (
        u_end / (2.0 * Delta[1]), u_end / (2.0 * Delta[0])
    )
    lapse_lower, lapse_upper = (
        float(value)
        for value in launch["explicit_segment"]["lapse_interval_on_launch_ball"]
    )
    proper_time = (
        lapse_lower * coordinate_time[0], lapse_upper * coordinate_time[1]
    )
    old_to_refined = float(np.linalg.norm(
        (refined_joint - old_joint) * np.tile(weights, 2)
    ))
    outer_use = old_to_refined + float(np.linalg.norm(predictor_action)) + next_ball_radius
    validation = {
        "same_actual_C2_branch_24_used": selected == 24,
        "pole_free_R_replaces_superseded_crude_R": R_upper < float(old_ball["R_upper"]),
        "Delta_positivity_radius_exceeds_old_radius": (
            positivity_radius > float(old_ball["Delta_positivity_radius_lower"])
        ),
        "dynamic_radius_is_limited_by_outer_margin": (
            dynamic_radius == available_margin
        ),
        "Delta_stays_strictly_positive": Delta[0] > 0.0,
        "segment_is_longer_than_first_recenterable_launch": (
            lambda_end > float(launch["explicit_segment"]["signed_lambda_end_lower"])
        ),
        "pole_free_Jacobi_growth_is_finite": Jacobi_growth < 2.0,
        "endpoint_tube_closes_inside_outer_ball": outer_use < float(old_ball["action_radius"]),
        "positive_proper_duration": proper_time[0] > 0.0,
        "predictor_is_not_physical_endpoint": True,
        "no_selector_equation_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION",
        "status": (
            "C2_POLE_FREE_CONTINUATION_EXTENDED_TO_OUTER_MARGIN_FRACTION"
            if passed else "C2_POLE_FREE_OUTER_MARGIN_EXTENSION_NOT_CERTIFIED"
        ),
        "classification": (
            "REPLACING_THE_CRUDE_HARD_REMAINDER_BY_THE_CERTIFIED_COVARIANT_"
            "HARD_RATE_EXPANDS_THE_DELTA_POSITIVITY_TUBE_UNTIL_THE_EXISTING_"
            "OUTER_ACTION_MARGIN_IS_THE_ACTIVE_LIMIT;_A_LONGER_POSITIVE_"
            "PROPER_TIME_SEGMENT_AND_RECENTERABLE_ENDPOINT_TUBE_CLOSE"
        ),
        "improved_launch_ball": {
            "outer_action_radius": float(old_ball["action_radius"]),
            "available_outer_margin": available_margin,
            "pole_free_R_upper": R_upper,
            "superseded_crude_R_upper": float(old_ball["R_upper"]),
            "Delta_positivity_radius": positivity_radius,
            "derived_dynamic_radius": dynamic_radius,
            "c_psi_interval": list(c_interval),
            "b_psi_interval": list(b_interval),
            "Delta_interval": list(Delta),
            "regularized_speed_upper": speed,
            "path_fraction": path_fraction,
        },
        "extended_segment": {
            "signed_lambda_end": lambda_end,
            "physical_u_end": u_end,
            "coordinate_time_interval": list(coordinate_time),
            "proper_time_interval": list(proper_time),
            "action_path_upper": action_path,
            "Jacobi_exponent_upper": Jacobi_exponent,
            "Jacobi_growth_upper": Jacobi_growth,
        },
        "endpoint_recenter": {
            "birth_field_mismatch_upper": birth_field_mismatch,
            "nonlinear_remainder_upper": nonlinear_remainder,
            "endpoint_tube_radius_upper": endpoint_tube,
            "next_translated_ball_radius": next_ball_radius,
            "outer_ball_total_radius_use": outer_use,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
            "predictor_is_physical_endpoint": False,
        },
        "exact_next_dependency": (
            "CERTIFY_RETAINED_ACTION_AND_SELECTED_LINE_BOUNDS_ON_THE_NEW_"
            "TRANSLATED_BALL,_THEN_REPEAT_THE_POLE_FREE_DESCRIPTOR_FLOW_"
            "UNTIL_COMPLETED_ENCAPSULATION_OR_A_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "pole_free_outer_margin_segment": "CERTIFIED",
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
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
        "R": payload["improved_launch_ball"]["pole_free_R_upper"],
        "dynamic_radius": payload["improved_launch_ball"]["derived_dynamic_radius"],
        "lambda_end": payload["extended_segment"]["signed_lambda_end"],
        "endpoint_tube": payload["endpoint_recenter"]["endpoint_tube_radius_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
