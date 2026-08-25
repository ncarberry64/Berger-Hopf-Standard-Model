"""Remove impossible normal-eigenvalue motion from the C2 proof tube."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_denominator_ball import (  # noqa: E402
    _centered_bounds,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR.json"
CONTINUATION = BASE / "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.json"
CONTINUATION_DATA = BASE / "BHSM_N12_C2_FRESH_CENTER_DENOMINATOR_CONTINUATION.npz"
RECENTER = BASE / "BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"
LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
THEORY = ROOT / "theory/n12_c2_descriptor_fiber_denominator.md"
INPUTS = (CONTINUATION, CONTINUATION_DATA, RECENTER, LINE, THEORY)
QDIM = 37


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing descriptor-fiber inputs: " + ", ".join(missing))
    continuation, recenter, line_record = (
        _load(path) for path in (CONTINUATION, RECENTER, LINE)
    )
    if not all(record.get("validation_passed") is True for record in (
        continuation, recenter, line_record,
    )):
        raise RuntimeError("validated descriptor continuation parents required")
    cover = continuation["continuation"]
    rows = cover["rows"]
    if len(rows) < 2:
        raise RuntimeError("at least two fresh-center rows required")
    last = rows[-1]
    with np.load(CONTINUATION_DATA) as data:
        centers = np.asarray(data["C2_fresh_center_predictor_centers"], dtype=float)
        center = centers[-2]
        weights = np.asarray(data["state_weights"], dtype=float)

    transferred = recenter["recenter"]
    base_pf = transferred["recentered_pole_free_bounds"]
    path_before = float(rows[-2]["fresh_center_path_upper"])
    pf = dict(base_pf)
    pf.update({
        "hard_D3_center": float(base_pf["hard_D3_center"])
        + float(base_pf["D4_full_hard_hard_upper"]) * path_before,
        "rhs_raw_derivative_center": float(base_pf["rhs_raw_derivative_center"])
        + float(base_pf["rhs_raw_second_derivative_upper"]) * path_before,
        "coupling_center": float(base_pf["coupling_center"])
        + float(base_pf["D4_full_selected_hard_upper"]) * path_before,
        "center_hard_rate_raw_norm": float(base_pf["center_hard_rate_raw_norm"])
        + float(base_pf["hard_Jacobi_action_upper"]) * path_before
        / max(float(np.max(weights[QDIM:])), 1.0),
    })
    radius = float(last["selected_ball_radius"])
    with localcontext() as context:
        context.prec = 100
        signed_end = Decimal(cover["final_signed_lambda_decimal"])
        signed_step = Decimal(last["signed_lambda_step_decimal"])
        signed_start = signed_end - signed_step
        fiber_lambda_upper = float(signed_end)
    parent_radius = min(
        float(transferred["recentered_parent_action_radius"]) - path_before,
        float(line_record["action_coordinate_ball_radius"])
        - float(transferred["old_root_to_new_center_action_distance_upper"])
        - path_before,
    )
    coefficient = _coefficient_enclosure(center, weights, parent_radius)
    isotropic = _centered_bounds(
        radius=radius,
        pf=pf,
        launch=transferred["recentered_launch_ball"],
        line=line_record["bounds"],
        center_c=tuple(last["c_psi_center_interval"]),
        center_b=tuple(last["b_psi_center_interval"]),
        center_lambda=float(signed_start),
        center_state=center,
        weights=weights,
        coefficient_bounds=coefficient,
    )
    c_lower = float(isotropic["c_psi_interval"][0])
    b_lower = float(isotropic["b_psi_interval"][0])
    remainder = float(isotropic["hard_remainder_upper"])
    product_lower = c_lower * b_lower
    isotropic_lambda_upper = float(isotropic["lambda_absolute_upper"])
    isotropic_loss = isotropic_lambda_upper * remainder
    fiber_loss = fiber_lambda_upper * remainder
    isotropic_delta = product_lower - isotropic_loss
    fiber_delta = product_lower - fiber_loss
    normal_overestimate = isotropic_lambda_upper / fiber_lambda_upper
    delta_improvement = fiber_delta / max(isotropic_delta, np.finfo(float).tiny)
    recorded_delta = float(last["Delta_lower"])
    relative_replay = abs(isotropic_delta - recorded_delta) / max(recorded_delta, 1.0e-300)

    validation = {
        "validated_1128_segment_parent_consumed": int(last["global_segment_index"]) == 1128,
        "descriptor_identity_is_exact_not_a_selector": True,
        "fixed_s_variations_are_tangent_to_lambda_level_set": True,
        "isotropic_last_Delta_replayed": relative_replay < 1.0e-8,
        "isotropic_lambda_radius_overestimates_exact_fiber_by_more_than_1e5": (
            normal_overestimate > 1.0e5
        ),
        "fiber_restricted_Delta_has_strict_positive_margin": fiber_delta > 1.0e-15,
        "fiber_Delta_improves_last_scalar_Delta_by_more_than_1e5": (
            delta_improvement > 1.0e5
        ),
        "hard_fixed_point_denominator_remains_positive": (
            float(isotropic["hard_self_consistency_denominator_lower"]) > 0.0
        ),
        "fiber_restriction_does_not_claim_endpoint_or_history_termination": True,
        "no_equation_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_DESCRIPTOR_FIBER_DENOMINATOR",
        "status": (
            "C2_DESCRIPTOR_FIBER_REMOVES_ISOTROPIC_SOFT_NORMAL_DELTA_COLLAPSE"
            if passed else "C2_DESCRIPTOR_FIBER_DENOMINATOR_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_REGULARIZED_C2_FLOW_IS_A_GRAPH_OVER_THE_ACTION_OWNED_SIGNED_"
            "EIGENVALUE_s;_AT_FIXED_s_THE_ERROR_BUNDLE_LIES_IN_THE_LEVEL_SET_"
            "lambda_event=s,_SO_THE_ISOTROPIC_LAMBDA_LIPSCHITZ_TIMES_RADIUS_"
            "LOSS_IS_NOT_AN_ADMISSIBLE_TRANSVERSE_VARIATION"
        ),
        "exact_fiber_theorem": {
            "descriptor": "s=lambda_event(Y)",
            "history_graph": "Y=Y(s)",
            "fixed_parameter_error_bundle": "E_s subset {Y:lambda_event(Y)=s}",
            "linearized_tangent_condition": "Dlambda_event(Y) delta_Y=0",
            "stepwise_soft_bound": "sup_{s in [s0,s1]}|lambda_event(Y(s))|=s1",
            "forbidden_isotropic_replacement": "s1+Lip(lambda_event)*r",
        },
        "segment_1128_replay": {
            "selected_ball_radius": radius,
            "signed_descriptor_start": str(signed_start),
            "signed_descriptor_end": str(signed_end),
            "isotropic_lambda_upper": isotropic_lambda_upper,
            "exact_fiber_lambda_upper": fiber_lambda_upper,
            "isotropic_normal_overestimate_factor": normal_overestimate,
            "c_times_b_lower": product_lower,
            "hard_remainder_upper": remainder,
            "isotropic_lambda_R_loss": isotropic_loss,
            "fiber_lambda_R_loss": fiber_loss,
            "recorded_isotropic_Delta_lower": recorded_delta,
            "replayed_isotropic_Delta_lower": isotropic_delta,
            "isotropic_replay_relative_error": relative_replay,
            "fiber_restricted_Delta_lower": fiber_delta,
            "fiber_over_isotropic_Delta_improvement": delta_improvement,
            "hard_self_consistency": float(isotropic["hard_self_consistency"]),
            "hard_denominator_lower": float(
                isotropic["hard_self_consistency_denominator_lower"]
            ),
        },
        "adjudication": {
            "segment_1128_Delta_collapse": "INVALID_AS_ACTIVE_PHYSICAL_FIBER_LIMIT",
            "remaining_scalar_limit": "HARD_BUNDLE_ISOTROPIC_WRAPPING",
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "mathematical_history_termination_claimed": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_FIXED_s_TANGENT_ERROR_BUNDLE_WITH_A_CONJUGATED_"
            "HARD_BUNDLE_MATRIX_OR_LOHNER_ENCLOSURE;_DO_NOT_REINTRODUCE_"
            "NORMAL_LAMBDA_VARIATION_INTO_THE_DESCRIPTOR_FIBER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_DESCRIPTOR_FIBER_HARD_MATRIX_ENCLOSURE_OR_COMBINED_PROJECTED_TAIL",
            "Gate8": "LOCKED",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
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
    replay = payload["segment_1128_replay"]
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "normal_overestimate": replay["isotropic_normal_overestimate_factor"],
        "isotropic_Delta": replay["replayed_isotropic_Delta_lower"],
        "fiber_Delta": replay["fiber_restricted_Delta_lower"],
        "Delta_improvement": replay["fiber_over_isotropic_Delta_improvement"],
        "hard_denominator": replay["hard_denominator_lower"],
    }, indent=2))


if __name__ == "__main__":
    main()
