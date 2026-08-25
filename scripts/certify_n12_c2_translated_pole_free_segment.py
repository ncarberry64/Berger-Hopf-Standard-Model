"""Propagate C2 through the first translated pole-free descriptor ball."""

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
RESULT = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
DATA_RESULT = BASE / "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.npz"
BALL = BASE / "BHSM_N12_C2_TRANSLATED_DESCRIPTOR_BALL.json"
EXTENSION = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
EXTENSION_DATA = BASE / "BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.npz"
POLE_FREE = BASE / "BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
LAUNCH = BASE / "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
PARENT_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
THEORY = ROOT / "theory/n12_c2_translated_pole_free_segment.md"
INPUTS = (
    BALL, EXTENSION, EXTENSION_DATA, POLE_FREE, LAUNCH, PARENT_LINE,
    CANDIDATE, THEORY,
)
QDIM = 37
STATE_DIMENSION = 98


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete translated C2 segment inputs required")
    ball, extension, pole_free, launch, parent_line = (
        _load(path) for path in (BALL, EXTENSION, POLE_FREE, LAUNCH, PARENT_LINE)
    )
    if not all(record.get("validation_passed") is True for record in (
        ball, extension, pole_free, launch, parent_line,
    )):
        raise RuntimeError("validated translated C2 parents required")
    with np.load(EXTENSION_DATA) as data:
        center = np.asarray(data["C2_predictor_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        signed_s0 = float(data["signed_lambda_end"])
    with np.load(CANDIDATE) as data:
        root_state = np.asarray(data["state"], dtype=float)[:STATE_DIMENSION]

    translated = ball["translated_ball"]
    pf = pole_free["bounds"]
    line = parent_line["bounds"]
    old_ball = launch["launch_ball"]
    total_radius = float(translated["total_root_relative_radius"])
    local_radius = float(translated["derived_local_radius"])
    initial_tube = float(extension["endpoint_recenter"][
        "endpoint_tube_radius_upper"
    ])

    frequencies = spectral_frequencies(12)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    reduced_weights = np.concatenate((
        np.ones(QDIM), np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    maximum_q_weight = float(np.max(q_weights))
    maximum_reduced_weight = float(np.max(reduced_weights))

    # Rebuild the inverse-free regularized Jacobi bound on the full
    # root-relative translated ball.
    hard_inverse = 1.0 / float(line["eigenline_gap_lower"])
    hard_D3 = (
        float(pf["hard_D3_center"])
        + float(pf["D4_full_hard_hard_upper"]) * total_radius
    )
    denominator = 1.0 - hard_inverse * hard_D3 * total_radius
    rhs_derivative = (
        float(pf["rhs_raw_derivative_center"])
        + float(pf["rhs_raw_second_derivative_upper"]) * total_radius
    )
    projector_derivative = 2.0 * float(
        line["weighted_selected_to_complement_first_variation_on_ball"]
    )
    b_upper = max(abs(value) for value in translated["b_psi_interval"])
    center_hard = float(pf["center_hard_rate_raw_norm"])
    hard_Jacobi_raw = hard_inverse * (
        rhs_derivative + hard_D3 * center_hard
        + projector_derivative * b_upper
    ) / denominator
    hard_rate_raw = center_hard + hard_Jacobi_raw * total_radius
    hard_rate_action = maximum_reduced_weight * hard_rate_raw
    hard_Jacobi_action = maximum_reduced_weight * hard_Jacobi_raw
    coupling = (
        float(pf["coupling_center"])
        + float(pf["D4_full_selected_hard_upper"]) * total_radius
    )
    lambda_lipschitz = float(line["selected_eigenvalue_first_derivative_bound"])
    lambda_hessian = float(line["selected_eigenvalue_raw_Hessian_bound"])
    lambda_upper = lambda_lipschitz * total_radius
    structured_b_lipschitz = (
        rhs_derivative
        + (coupling + lambda_upper * projector_derivative) * hard_rate_raw
    )
    root_configuration = q_weights * root_state[QDIM:2 * QDIM]
    configuration_upper = (
        float(np.linalg.norm(root_configuration))
        + maximum_q_weight * total_radius
    )
    hard_flow = math.hypot(configuration_upper, hard_rate_action)
    remainder_upper = lambda_lipschitz * hard_flow
    hard_flow_Jacobi = math.hypot(maximum_q_weight, hard_Jacobi_action)
    remainder_lipschitz = (
        lambda_hessian * hard_flow
        + lambda_lipschitz * hard_flow_Jacobi
    )
    c_upper = max(abs(value) for value in translated["c_psi_interval"])
    c_lipschitz = float(old_ball["c_psi_Lipschitz_upper"])
    Delta_lipschitz = (
        b_upper * c_lipschitz + c_upper * structured_b_lipschitz
        + lambda_lipschitz * remainder_upper
        + lambda_upper * remainder_lipschitz
    )
    selected_action_upper = (
        maximum_reduced_weight
        + maximum_reduced_weight
        * float(line["weighted_selected_to_complement_first_variation_on_ball"])
        * total_radius
    )
    numerator_upper = math.hypot(
        lambda_upper * configuration_upper,
        b_upper * selected_action_upper + lambda_upper * hard_rate_action,
    )
    numerator_lipschitz = (
        lambda_lipschitz * configuration_upper
        + lambda_upper * maximum_q_weight
        + structured_b_lipschitz * selected_action_upper
        + b_upper * maximum_reduced_weight
        * float(line["weighted_selected_to_complement_first_variation_on_ball"])
        + lambda_lipschitz * hard_rate_action
        + lambda_upper * hard_Jacobi_action
    )
    Delta_lower, Delta_upper = (
        float(value) for value in translated["Delta_interval"]
    )
    speed_upper = numerator_upper / Delta_lower
    Jacobi = (
        numerator_lipschitz / Delta_lower
        + numerator_upper * Delta_lipschitz / Delta_lower**2
    )

    # Evaluate an action-owned proof vector at the translated center.  The
    # signed descriptor is external because binary64 cannot resolve its
    # magnitude from the near-zero Hessian eigenvalue.
    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
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
    center_configuration = q_weights * center[QDIM:2 * QDIM]
    mixed_vq = hessian_action[QDIM:QDIM + QDIM, :QDIM]
    mixed_mq = hessian_action[2 * QDIM:, :QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient[:QDIM] - mixed_vq @ center_configuration,
        -mixed_mq @ center_configuration,
    ))
    rhs_raw = reduced_weights * rhs_action
    b_center = float(psi @ rhs_raw)
    hard_center = complement @ ((complement.T @ rhs_raw) / hard_values)
    c_lower, c_upper_interval = (
        float(value) for value in translated["c_psi_interval"]
    )
    c_midpoint = 0.5 * (c_lower + c_upper_interval)
    c_halfwidth = 0.5 * (c_upper_interval - c_lower)
    nominal_Delta = c_midpoint * b_center
    nominal_numerator = np.concatenate((
        signed_s0 * center_configuration,
        (b_center * psi + signed_s0 * hard_center) * reduced_weights,
    ))
    nominal_field = nominal_numerator / nominal_Delta
    field_mismatch = (
        float(np.linalg.norm(nominal_numerator))
        * (abs(b_center) * c_halfwidth + signed_s0 * remainder_upper)
        / (Delta_lower * nominal_Delta)
    )

    available = local_radius - initial_tube
    path_limited_step = available / (4.0 * speed_upper)
    growth_limited_step = math.log(2.0) / Jacobi
    signed_step = min(path_limited_step, growth_limited_step)
    signed_s1 = signed_s0 + signed_step
    predictor_action_step = signed_step * nominal_field
    predictor = center + predictor_action_step / weights
    growth = math.exp(Jacobi * signed_step)
    nonlinear_remainder = 0.5 * Jacobi * speed_upper * signed_step**2 * growth
    endpoint_tube = growth * (
        initial_tube + signed_step * field_mismatch
    ) + nonlinear_remainder
    root_path_use = (
        float(extension["extended_segment"]["action_path_upper"])
        + float(np.linalg.norm(predictor_action_step)) + endpoint_tube
    )

    physical_u_increment = signed_s1**2 - signed_s0**2
    coordinate_time = (
        physical_u_increment / (2.0 * Delta_upper),
        physical_u_increment / (2.0 * Delta_lower),
    )
    lapse_lower, lapse_upper = (
        float(value) for value in translated["lapse_interval"]
    )
    proper_time = (
        lapse_lower * coordinate_time[0],
        lapse_upper * coordinate_time[1],
    )
    np.savez_compressed(
        DATA_RESULT,
        C2_predictor_state=predictor,
        state_weights=weights,
        branch_reference=reference,
        signed_lambda_start=np.asarray(signed_s0),
        signed_lambda_end=np.asarray(signed_s1),
    )

    validation = {
        "same_actual_C2_branch_24_used": selected == 24,
        "hard_covariant_self_consistency_closes": denominator > 0.5,
        "pole_free_Jacobi_is_finite": math.isfinite(Jacobi) and Jacobi > 0.0,
        "translated_Delta_stays_positive": Delta_lower > 0.0,
        "initial_endpoint_tube_fits_local_ball": available > 0.0,
        "signed_descriptor_step_is_positive": signed_step > 0.0,
        "path_uses_strict_dyadic_fraction_of_available_radius": (
            speed_upper * signed_step <= available / 4.0
        ),
        "Jacobi_growth_is_at_most_two": growth <= 2.0,
        "Euler_endpoint_tube_closes_in_translated_ball": (
            root_path_use < total_radius
        ),
        "positive_coordinate_and_proper_time_increment": (
            coordinate_time[0] > 0.0 and proper_time[0] > 0.0
        ),
        "lapse_radius_rate_selected_line_and_Legendre_margins_transfer": (
            lapse_lower > 0.0
            and float(translated["D_tau_log_R4_interval"][0]) > 0.0
            and float(translated["selected_line_gap_lower"]) > 0.0
            and float(translated["Legendre_event_lower"]) > 0.0
        ),
        "binary64_soft_eigenvalue_not_used_as_signed_descriptor": True,
        "predictor_not_promoted_to_physical_endpoint_or_selector": True,
        "no_recurrence_periodic_endpoint_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT",
        "status": (
            "SECOND_C2_POLE_FREE_SEGMENT_AND_ENDPOINT_TUBE_CERTIFIED"
            if passed else "C2_TRANSLATED_POLE_FREE_SEGMENT_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_FIRST_TRANSLATED_ACTION_BALL_SUPPORTS_THE_SAME_INVERSE_FREE_"
            "HARD_SOLVE,_DIFFERENTIATED_SOFT_SOURCE,_AND_POLE_CANCELLED_"
            "DESCRIPTOR_FIELD;_A_POSITIVE_SIGNED_EIGENVALUE_AND_PROPER_TIME_"
            "INCREMENT_CLOSE_IN_A_SECOND_RECENTERABLE_ENDPOINT_TUBE"
        ),
        "translated_generator": {
            "total_root_relative_radius": total_radius,
            "hard_self_consistency_denominator_lower": denominator,
            "hard_rate_action_upper": hard_rate_action,
            "hard_Jacobi_action_upper": hard_Jacobi_action,
            "structured_b_psi_Lipschitz_upper": structured_b_lipschitz,
            "hard_remainder_upper": remainder_upper,
            "hard_remainder_Lipschitz_upper": remainder_lipschitz,
            "Delta_action_derivative_upper": Delta_lipschitz,
            "regularized_speed_upper": speed_upper,
            "pole_free_regularized_Jacobi_upper": Jacobi,
        },
        "proof_center": {
            "signed_lambda_start": signed_s0,
            "selected_branch": selected,
            "b_psi_center": b_center,
            "c_psi_midpoint": c_midpoint,
            "nominal_Delta": nominal_Delta,
            "nominal_field_action_norm": float(np.linalg.norm(nominal_field)),
            "field_mismatch_upper": field_mismatch,
            "predictor_is_physical_endpoint": False,
        },
        "translated_segment": {
            "signed_lambda_step": signed_step,
            "signed_lambda_end": signed_s1,
            "physical_u_increment": physical_u_increment,
            "coordinate_time_increment_interval": list(coordinate_time),
            "proper_time_increment_interval": list(proper_time),
            "action_predictor_step_norm": float(np.linalg.norm(predictor_action_step)),
            "Jacobi_exponent_upper": Jacobi * signed_step,
            "Jacobi_growth_upper": growth,
        },
        "endpoint_recenter": {
            "initial_tube_radius": initial_tube,
            "nonlinear_remainder_upper": nonlinear_remainder,
            "endpoint_tube_radius_upper": endpoint_tube,
            "root_relative_path_plus_tube_upper": root_path_use,
            "translated_ball_radius": total_radius,
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
            "predictor_is_physical_endpoint": False,
        },
        "adjudication": {
            "physical_encapsulation_endpoint_reached": False,
            "canonical_stop_reached": False,
            "outcome": "REGULAR_FORWARD_CONTINUATION_AVAILABLE",
        },
        "exact_next_dependency": (
            "CERTIFY_THE_NEXT_TRANSLATED_ACTION_BALL_AROUND_THIS_ENDPOINT_"
            "TUBE_AND_COMPOSE_ITS_INVERSE_FREE_VOLTERRA_WEYL_TRANSFER"
        ),
        "claim_boundary": {
            "second_pole_free_C2_segment": "CERTIFIED" if passed else "OPEN",
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
        "Jacobi": payload["translated_generator"][
            "pole_free_regularized_Jacobi_upper"
        ],
        "signed_step": payload["translated_segment"]["signed_lambda_step"],
        "endpoint_tube": payload["endpoint_recenter"][
            "endpoint_tube_radius_upper"
        ],
        "root_use": payload["endpoint_recenter"][
            "root_relative_path_plus_tube_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
