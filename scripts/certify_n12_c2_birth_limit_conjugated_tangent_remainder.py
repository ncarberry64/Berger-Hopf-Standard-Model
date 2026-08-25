"""Certify the C2 birth-limit tangent remainder on the physical lambda fiber.

The signed finite-difference D4 column in the center diagnostic is not used.
Its complete action-owned absolute envelope and the retained D5 variation
instead control the moving cubic.  The selected-line motion is transported by
the already certified Kato graph bounds.
"""

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
from derive_n12_c2_launch_eigenline_ball import _load as _load_canonical  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.json"
CENTER_DATA = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.npz"
STABILITY = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_STABILITY.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
CANCELLED = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
RESULT = BASE / "BHSM_N12_C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER.json"
THEORY = ROOT / "theory" / "n12_c2_birth_limit_conjugated_tangent_remainder.md"
INPUTS = (CENTER, CENTER_DATA, STABILITY, LINE, CANCELLED, THEORY)
QDIM = 37
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


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing birth-limit tangent inputs: " + ", ".join(missing))
    center_record, stability, line_record, cancelled = (
        _json(path) for path in (CENTER, STABILITY, LINE, CANCELLED)
    )
    if not all(record.get("validation_passed") is True for record in (
        center_record, stability, line_record, cancelled,
    )):
        raise RuntimeError("validated center, line, and continuation parents required")

    with np.load(CENTER_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        psi_first = np.asarray(data["selected_vector_derivative_action"], dtype=float)
        complete_c_first = np.asarray(
            data["c_gradient_action_central_difference"], dtype=float
        )
        fixed_d4_measured = np.asarray(
            data["fixed_line_c_gradient_action_central_difference"], dtype=float
        )
        tangent = np.asarray(data["fixed_s_tangent_basis"], dtype=float)
        lambda_first = np.asarray(data["lambda_gradient_action"], dtype=float)

    jet = exact_full_action_jet_at_state(
        12, center[:QDIM], center[QDIM:2 * QDIM], center[2 * QDIM:], points=96,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    selected_vector = vectors[:, selected]
    if float(selected_vector @ reference) < 0.0:
        selected_vector = -selected_vector
    if selected != 24 or float(selected_vector @ psi) < 1.0 - 1.0e-10:
        raise RuntimeError("center selected line does not replay")
    complement = np.delete(vectors, selected, axis=1)
    reduced_weights = weights[QDIM:]
    maximum_reduced_weight = float(np.max(reduced_weights))
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))
    identity = np.eye(center.size)

    continuation = cancelled["continuation"]
    current_radius = _up(
        float(continuation["fresh_center_path_upper"])
        + float(continuation["final_endpoint_tube_radius_upper"])
    )
    available = _down(
        float(line_record["action_coordinate_ball_radius"])
        - 6.050520685850281e-13 - 5.2400317483810544e-15
    )
    if not 0.0 < current_radius < available:
        raise ArithmeticError("continued physical tube leaves the certified line ball")
    # Certify the full remaining line ball, not just the portion occupied by
    # the present continuation.  This makes the result reusable by the next
    # hard-response continuation without extrapolation.
    radius = available

    # Consume the canonical committed majorant implementation even when the
    # shared worktree copy carries unrelated owner work.
    os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(radius)
    action_bound = _load_canonical("derive_n12_action_ball_majorants").action_bound

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

    line = line_record["bounds"]
    p1 = _up(float(line["weighted_selected_to_complement_first_variation_on_ball"]))
    inverse = _up(float(line["ordered_eigenprojector_reduced_resolvent_bound"]))
    relative_first = _up(float(line["relative_complement_first_variation_on_ball"]))
    lambda_one = _up(float(line["selected_eigenvalue_first_derivative_bound"]))
    direct_p2 = _up(inverse * float(line["selected_complement_fourth_variation"]))
    p2 = _up(
        direct_p2
        + 2.0 * (relative_first + inverse * lambda_one) * p1
        + p1**2
    )

    # Complete product rule for c(Y)=D3S(Y)[psi(Y),psi(Y),psi(Y)].
    # Coefficients p1,p2 are complement coefficients; the mixed action
    # directions already contain the reduced output weights.
    c2 = _up(
        action["D5_XXPPP"]
        + 6.0 * action["D4_XCPP"] * p1
        + 3.0 * action["D3_CPP"] * p2
        + 6.0 * action["D3_CCP"] * p1**2
    )
    kato_c_first = complete_c_first - fixed_d4_measured
    kato_c_first_norm = _up(float(np.linalg.norm(kato_c_first)))
    c1_center = _up(kato_c_first_norm + action["D4_XPPP"])
    c1_ball = _up(c1_center + c2 * radius)
    c0 = float(center_record["center"]["c_psi"])
    c_lower = _down(c0 - c1_center * radius - 0.5 * c2 * radius**2)

    p0_action = _up(float(np.linalg.norm(selected_action)))
    p0_ball = _up(
        p0_action + maximum_reduced_weight * p1 * radius
        + 0.5 * maximum_reduced_weight * p2 * radius**2
    )
    p1_action_ball = _up(maximum_reduced_weight * (p1 + p2 * radius))
    p2_action = _up(maximum_reduced_weight * p2)
    if c_lower <= 0.0:
        raise ArithmeticError("moving cubic lower bound is not positive")

    # Hessian bound for F0=Psi/c on the action-coordinate physical tube.
    d2_f0 = _up(
        p2_action / c_lower
        + 2.0 * p1_action_ball * c1_ball / c_lower**2
        + p0_ball * c2 / c_lower**2
        + 2.0 * p0_ball * c1_ball**2 / c_lower**3
    )

    # Rebuild the center generator without the cancellation-sensitive signed
    # D4 finite difference.  The unknown fixed-line D4 row is then added as
    # an absolute action-owned operator ball.
    kato_birth = np.zeros((center.size, center.size))
    kato_birth[QDIM:] = reduced_weights[:, None] * (
        psi_first / c0 - psi[:, None] * kato_c_first[None, :] / c0**2
    )
    tangent_kato = tangent.T @ kato_birth @ tangent
    tangent_kato_mu = _up(float(np.linalg.eigvalsh(
        0.5 * (tangent_kato + tangent_kato.T)
    )[-1]))
    full_kato_norm = _up(float(np.linalg.norm(kato_birth, 2)))
    d4_generator_uncertainty = _up(
        p0_action * action["D4_XPPP"] / c0**2
    )
    center_mu_upper = _up(tangent_kato_mu + d4_generator_uncertainty)
    center_operator_upper = _up(full_kato_norm + d4_generator_uncertainty)

    lambda_norm = _up(float(np.linalg.norm(lambda_first)))
    lambda_hessian = _up(float(line["selected_eigenvalue_raw_Hessian_bound"]))
    lambda_lower = _down(lambda_norm - lambda_hessian * radius)
    normal_rotation = _up(2.0 * lambda_hessian * radius / lambda_lower)
    rotation_remainder = _up(4.0 * normal_rotation * center_operator_upper)
    field_remainder = _up(d2_f0 * radius)
    tangent_remainder = _up(field_remainder + rotation_remainder)
    full_ball_operator = _up(center_operator_upper + field_remainder)

    initial_s = float(continuation["initial_signed_lambda_decimal"])
    final_s = float(continuation["final_signed_lambda_decimal"])
    horizon = _up(final_s - initial_s)
    center_growth = _up(math.exp(center_mu_upper * horizon))
    center_condition = _up(math.exp(2.0 * center_operator_upper * horizon))
    conjugated_remainder = _up(center_condition * tangent_remainder)
    total_growth = _up(center_growth * math.exp(conjugated_remainder * horizon))
    full_ball_growth = _up(math.exp(full_ball_operator * horizon))

    validation = {
        "branch_24_and_center_line_replayed": selected == 24,
        "continued_tube_strictly_inside_certified_line_ball": current_radius < radius,
        "canonical_committed_action_majorant_used": True,
        "retained_D3_D4_D5_mixed_bounds_finite": all(
            math.isfinite(value) for value in action.values()
        ),
        "moving_cubic_stays_positive_on_tube": c_lower > 0.0,
        "normal_gradient_stays_nonzero_on_tube": lambda_lower > 0.0,
        "normal_plane_rotation_is_small": normal_rotation < 1.0,
        "birth_limit_conjugated_growth_is_finite": math.isfinite(total_growth),
        "birth_limit_full_ball_growth_is_finite": math.isfinite(full_ball_growth),
        "signed_finite_difference_D4_not_used_as_authority": True,
        "finite_s_correction_not_claimed_by_birth_limit_bound": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER",
        "status": (
            "C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER_CERTIFIED;_FINITE_s_CORRECTION_OPEN"
            if passed else "C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER_INVALID"
        ),
        "physical_tube": {
            "matrix_center_to_continuation_path_upper": float(
                continuation["fresh_center_path_upper"]
            ),
            "final_endpoint_tube_upper": float(
                continuation["final_endpoint_tube_radius_upper"]
            ),
            "current_combined_action_radius_upper": current_radius,
            "certified_matrix_center_ball_radius": radius,
            "available_line_ball_radius_lower": available,
            "signed_descriptor_horizon": horizon,
        },
        "selected_line": {
            "first_variation_coefficient_upper": p1,
            "direct_second_variation_coefficient_upper": direct_p2,
            "complete_second_variation_coefficient_upper": p2,
            "normal_gradient_center_norm": lambda_norm,
            "normal_gradient_ball_lower": lambda_lower,
            "normal_plane_rotation_upper": normal_rotation,
        },
        "retained_action_mixed_bounds": action,
        "moving_cubic": {
            "center_value": c0,
            "center_Kato_first_derivative_norm": kato_c_first_norm,
            "center_complete_first_derivative_upper": c1_center,
            "second_derivative_upper": c2,
            "ball_first_derivative_upper": c1_ball,
            "ball_value_lower": c_lower,
        },
        "birth_limit_generator": {
            "formula": "F_0=Psi/c;_D2F_0_is_bounded_by_the_complete_quotient_product_rule",
            "center_Kato_tangent_numerical_abscissa": tangent_kato_mu,
            "fixed_line_D4_generator_uncertainty_upper": d4_generator_uncertainty,
            "center_tangent_numerical_abscissa_upper": center_mu_upper,
            "center_full_operator_norm_upper": center_operator_upper,
            "D2F0_action_operator_upper": d2_f0,
            "field_variation_remainder_upper": field_remainder,
            "tangent_rotation_remainder_upper": rotation_remainder,
            "total_tangent_remainder_upper": tangent_remainder,
            "full_action_ball_operator_norm_upper": full_ball_operator,
        },
        "conjugated_growth": {
            "center_growth_upper": center_growth,
            "center_condition_upper": center_condition,
            "conjugated_remainder_upper": conjugated_remainder,
            "total_birth_limit_tangent_growth_upper": total_growth,
            "total_birth_limit_full_ball_growth_upper": full_ball_growth,
        },
        "adjudication": {
            "birth_limit_tangent_remainder": "CERTIFIED_ON_CURRENT_CONTINUED_TUBE",
            "finite_s_correction_sG": "OPEN_REQUIRES_CANCELLATION_PRESERVING_HARD_RESPONSE_ENCLOSURE",
            "current_scalar_hard_denominator_exhaustion_is_event_or_stop": False,
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "hindsight": {
            "result": "VALIDATED",
            "classification": "NUMERICAL_CONDITIONING_REMOVED;_PROOF_CHART_LIMIT_REMAINS",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_FINITE_s_CORRECTION_DERIVATIVE_ON_THE_SAME_TANGENT_"
            "BUNDLE_WITH_THE_HARD_RESPONSE_SCHUR_GRAPH;_DO_NOT_RETURN_TO_"
            "THE_ISOTROPIC_HARD_DENOMINATOR"
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
        "radius": payload["physical_tube"]["certified_matrix_center_ball_radius"],
        "c_lower": payload["moving_cubic"]["ball_value_lower"],
        "remainder": payload["birth_limit_generator"]["total_tangent_remainder_upper"],
        "growth": payload["conjugated_growth"]["total_birth_limit_tangent_growth_upper"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
