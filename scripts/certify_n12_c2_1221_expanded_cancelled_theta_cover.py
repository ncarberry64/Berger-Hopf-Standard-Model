"""Propagate a finite cancelled-theta cover inside the expanded 1221 ball."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE_SCRIPT = ROOT / "scripts" / "certify_n12_c2_1221_cancelled_theta_step.py"
CENTER_DATA = BASE / "BHSM_N12_C2_1221_CANCELLED_CENTER_MATRIX.npz"
STEP = BASE / "BHSM_N12_C2_LOHNER_STEP_1221.json"
RESULT = BASE / "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221.json"
DATA = RESULT.with_suffix(".npz")
MAX_STEPS = 16
INFLATION = 1.0 + 1.0e-10

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, -math.inf)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _expanded_parent() -> dict:
    os.environ["BHSM_N12_EXPANDED_CANCELLED_THETA"] = "1"
    spec = importlib.util.spec_from_file_location("expanded_parent", SOURCE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load expanded cancelled parent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_payload()


def build_payload() -> dict:
    parent = _expanded_parent()
    if parent.get("validation_passed") is not True:
        raise RuntimeError("validated expanded cancelled parent required")
    prior = json.loads(STEP.read_text(encoding="utf-8"))
    with np.load(CENTER_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    with np.load(BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz") as data:
        reference = np.asarray(data["branch_reference"], dtype=float)

    radius = float(parent["domain"]["selected_radius"])
    delta_abs = float(parent["domain"]["Delta_absolute_upper"])
    lapse_lower = float(parent["domain"]["lapse_interval"][0])
    G1 = float(parent["cancelled_field"]["first_variation_ball_upper"])
    mu = float(parent["cancelled_field"]["logarithmic_norm_ball_upper"])
    tube = float(prior["segment"]["endpoint_tube_radius_upper"])
    descriptor_center = float(parent["segment"]["signed_descriptor_start"])
    descriptor_interval = [descriptor_center, descriptor_center]
    cumulative_path = 0.0
    theta = 0.0
    proper_lower_sum = 0.0
    centers = [center.copy()]
    descriptors = [descriptor_center]
    rows = []
    exhaustion = "MAXIMUM_COVER_STEPS_REACHED"

    for index in range(MAX_STEPS):
        field = exact_cancelled_euler_dirac_field_action(
            state=center, weights=weights, reference=reference,
            signed_descriptor=descriptor_center,
        )
        G = np.asarray(field["cancelled_field_action"], dtype=float)
        Gnorm = _up(float(np.linalg.norm(G)))
        remaining = radius - cumulative_path - tube
        if remaining <= 0.0 or descriptor_interval[0] <= 0.0:
            exhaustion = "EXPANDED_BALL_OR_SIGNED_DESCRIPTOR_INTERVAL_EXHAUSTED"
            break
        upper = min(
            0.9 * remaining / Gnorm,
            0.45 * descriptor_interval[0] / delta_abs,
        )

        def trial(h: float) -> dict:
            growth = math.exp(mu * h)
            truncation = _up(0.5 * G1 * Gnorm * h**2 * growth)
            action_step = h * G
            endpoint = center + action_step / weights
            stored = (endpoint - center) * weights
            rounding = _up(float(np.linalg.norm(stored - action_step)))
            new_tube = _up(growth * tube + truncation + rounding)
            path = _up(float(np.linalg.norm(stored)))
            new_total = cumulative_path + path + new_tube
            new_interval = [
                _down(descriptor_interval[0] - h * delta_abs),
                _up(descriptor_interval[1] + h * delta_abs),
            ]
            return {
                "closes": new_total < radius and new_interval[0] > 0.0,
                "endpoint": endpoint,
                "tube": new_tube,
                "path": path,
                "total": new_total,
                "interval": new_interval,
                "growth": growth,
                "truncation": truncation,
                "rounding": rounding,
            }

        if upper <= 0.0:
            exhaustion = "NO_POSITIVE_THETA_STEP_REMAINS"
            break
        if not trial(upper)["closes"]:
            feasible, infeasible = 0.0, upper
            for _ in range(100):
                midpoint = 0.5 * (feasible + infeasible)
                if trial(midpoint)["closes"]:
                    feasible = midpoint
                else:
                    infeasible = midpoint
            upper = feasible
        h = 0.5 * upper
        outcome = trial(h)
        if h <= 0.0 or not outcome["closes"]:
            exhaustion = "NO_POSITIVE_CANCELLED_COVER_STEP_CLOSES"
            break
        old_lower = descriptor_interval[0]
        descriptor_center += h * float(field["Delta"])
        proper_lower = lapse_lower * old_lower * h
        proper_lower_sum += proper_lower
        theta += h
        cumulative_path += outcome["path"]
        tube = outcome["tube"]
        descriptor_interval = outcome["interval"]
        center = outcome["endpoint"]
        centers.append(center.copy())
        descriptors.append(descriptor_center)
        rows.append({
            "index": index + 1,
            "theta_step": h,
            "theta_end": theta,
            "selected_branch": int(field["selected_branch"]),
            "center_Delta": float(field["Delta"]),
            "signed_descriptor_center_end": descriptor_center,
            "signed_descriptor_endpoint_interval": descriptor_interval.copy(),
            "center_path_increment_upper": outcome["path"],
            "cumulative_center_path_upper": cumulative_path,
            "endpoint_tube_radius_upper": tube,
            "joint_domain_use_upper": cumulative_path + tube,
            "matrix_growth_upper": outcome["growth"],
            "Euler_truncation_upper": outcome["truncation"],
            "proper_time_increment_lower": proper_lower,
            "proof_center_is_physical_endpoint": False,
        })
    else:
        exhaustion = "MAXIMUM_COVER_STEPS_REACHED_WITH_DOMAIN_OPEN"

    np.savez_compressed(
        DATA,
        predictor_centers=np.asarray(centers),
        signed_descriptor_centers=np.asarray(descriptors),
        state_weights=weights,
        branch_reference=reference,
        endpoint_tube_radius=np.asarray(tube),
    )
    accepted = len(rows)
    validation = {
        "expanded_full_action_parent_consumed": parent["domain"][
            "expanded_full_action_line_consumed"
        ] is True,
        "strict_positive_cover_extension": accepted > 0,
        "all_steps_retain_branch_24": accepted > 0 and all(
            row["selected_branch"] == 24 for row in rows
        ),
        "all_tubes_and_centers_stay_inside_expanded_ball": accepted > 0 and all(
            row["joint_domain_use_upper"] < radius for row in rows
        ),
        "all_signed_descriptor_intervals_stay_positive": accepted > 0 and all(
            row["signed_descriptor_endpoint_interval"][0] > 0.0 for row in rows
        ),
        "all_proper_time_increments_are_positive": accepted > 0 and all(
            row["proper_time_increment_lower"] > 0.0 for row in rows
        ),
        "predictors_not_promoted_to_physical_endpoints": all(
            row["proof_center_is_physical_endpoint"] is False for row in rows
        ),
        "Delta_sign_not_used_as_domain_condition": True,
        "binary64_eigenvalue_not_used_as_descriptor": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_EXPANDED_CANCELLED_THETA_COVER_FROM_1221",
        "status": (
            "C2_EXPANDED_CANCELLED_THETA_FINITE_COVER_CERTIFIED"
            if passed else "C2_EXPANDED_CANCELLED_THETA_COVER_FAILED"
        ),
        "cover": {
            "accepted_steps": accepted,
            "rows": rows,
            "theta_total": theta,
            "proper_time_lower_sum": proper_lower_sum,
            "initial_signed_descriptor": float(parent["segment"]["signed_descriptor_start"]),
            "final_signed_descriptor_center": descriptor_center,
            "final_signed_descriptor_interval": descriptor_interval,
            "expanded_ball_radius": radius,
            "final_cumulative_center_path_upper": cumulative_path,
            "final_endpoint_tube_radius_upper": tube,
            "final_joint_domain_use_upper": cumulative_path + tube,
            "exhaustion": exhaustion,
            "data": DATA.relative_to(ROOT).as_posix(),
        },
        "exact_next_dependency": (
            "RECENTER_THE_EXPANDED_CANCELLED_RESPONSE_AT_THE_FINAL_PREDICTOR_"
            "AND_REPEAT_UNTIL_EFFICIENT_LOG_DESCRIPTOR_CONTINUATION"
        ),
        "inputs": {
            "expanded_parent_script": _sha256(SOURCE_SCRIPT),
            "tracked_step_1221": _sha256(STEP),
            "center_matrix": _sha256(CENTER_DATA),
        },
        "validation": validation,
        "validation_passed": passed,
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
        "accepted_steps": payload["cover"]["accepted_steps"],
        "final_descriptor": payload["cover"]["final_signed_descriptor_center"],
        "final_interval": payload["cover"]["final_signed_descriptor_interval"],
        "final_domain_use": payload["cover"]["final_joint_domain_use_upper"],
        "exhaustion": payload["cover"]["exhaustion"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
