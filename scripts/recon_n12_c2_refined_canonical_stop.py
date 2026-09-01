"""Refine the finite C2 Euler--Dirac stop candidate.

The authoritative claim remains reconnaissance.  Starting from the final
positive node of the global denominator-free path, this script integrates
the same action-arclength system with an event function ``s=0``.  One- and
two-substep RK4/secant refinements are compared so that the resulting state is a
useful center for a later interval flow-cylinder or multiple-shooting proof.
No reverse physical history and no new stopping rule are introduced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
PATH_RECORD = BASE / "BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json"
PATH_DATA = PATH_RECORD.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _rhs(
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, float]:
    field = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=max(descriptor, 0.0),
    )
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    return cancelled / weights / norm, float(field["Delta"]) / norm


def _rk4_step(
    state: np.ndarray,
    descriptor: float,
    step: float,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, float]:
    k1y, k1s = _rhs(state, descriptor, weights, reference)
    k2y, k2s = _rhs(
        state + 0.5 * step * k1y,
        descriptor + 0.5 * step * k1s,
        weights,
        reference,
    )
    k3y, k3s = _rhs(
        state + 0.5 * step * k2y,
        descriptor + 0.5 * step * k2s,
        weights,
        reference,
    )
    k4y, k4s = _rhs(
        state + step * k3y,
        descriptor + step * k3s,
        weights,
        reference,
    )
    return (
        state + step * (k1y + 2.0 * k2y + 2.0 * k3y + k4y) / 6.0,
        descriptor + step * (k1s + 2.0 * k2s + 2.0 * k3s + k4s) / 6.0,
    )


def _integrate_n(
    state: np.ndarray,
    descriptor: float,
    action_length: float,
    subdivisions: int,
    weights: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, float]:
    current_state = state.copy()
    current_descriptor = descriptor
    step = action_length / subdivisions
    for _ in range(subdivisions):
        current_state, current_descriptor = _rk4_step(
            current_state, current_descriptor, step, weights, reference
        )
    return current_state, current_descriptor


def _secant_hit(
    state: np.ndarray,
    descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
    *,
    subdivisions: int,
    iterations: int = 4,
) -> tuple[np.ndarray, float, float, dict[str, Any]]:
    left_h, left_s = 0.0, descriptor
    right_h = 0.35
    right_state, right_s = _integrate_n(
        state, descriptor, right_h, subdivisions, weights, reference
    )
    if not right_s < 0.0:
        raise ArithmeticError("initial refinement interval must cross s=0")
    evaluations = 4 * subdivisions
    current_state = right_state
    for _ in range(iterations):
        hit = left_h - left_s * (right_h - left_h) / (right_s - left_s)
        current_state, current_s = _integrate_n(
            state, descriptor, hit, subdivisions, weights, reference
        )
        evaluations += 4 * subdivisions
        if current_s > 0.0:
            left_h, left_s = hit, current_s
        else:
            right_h, right_s = hit, current_s
    hit = left_h - left_s * (right_h - left_h) / (right_s - left_s)
    current_state, current_s = _integrate_n(
        state, descriptor, hit, subdivisions, weights, reference
    )
    evaluations += 4 * subdivisions
    return current_state, hit, current_s, {
        "subdivisions": subdivisions,
        "secant_iterations": iterations,
        "field_evaluations": evaluations,
        "final_bracket": [left_h, right_h],
    }


def build_payload() -> dict[str, Any]:
    record = json.loads(PATH_RECORD.read_text(encoding="utf-8"))
    if record.get("status") != "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY":
        raise RuntimeError("global canonical-stop reconnaissance required")
    with np.load(PATH_DATA) as source:
        state = np.asarray(source["left_positive_state"], dtype=float)
        descriptor = float(source["left_positive_descriptor"])
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    coarse_state, coarse_hit, coarse_s, coarse_stats = _secant_hit(
        state, descriptor, weights, reference, subdivisions=1
    )
    fine_state, fine_hit, fine_s, fine_stats = _secant_hit(
        state, descriptor, weights, reference, subdivisions=2
    )
    field = exact_cancelled_euler_dirac_field_action(
        state=fine_state,
        weights=weights,
        reference=reference,
        signed_descriptor=0.0,
    )
    geometry = boundary_geometry_action_covectors(state=fine_state, weights=weights)
    cancelled = np.asarray(field["cancelled_field_action"], dtype=float)
    field_norm = float(np.linalg.norm(cancelled))
    descriptor_rate = float(field["Delta"]) / field_norm
    state_discrepancy = float(np.linalg.norm((fine_state - coarse_state) * weights))
    hit_discrepancy = abs(fine_hit - coarse_hit)

    np.savez_compressed(
        DATA,
        stop_center=fine_state,
        coarse_stop_center=coarse_state,
        state_weights=weights,
        branch_reference=reference,
        action_tangent=cancelled / field_norm,
        action_length_from_left=np.asarray(fine_hit),
        total_action_length=np.asarray(92.0 + fine_hit),
    )
    return {
        "artifact": "BHSM_N12_C2_REFINED_CANONICAL_STOP_RECONNAISSANCE",
        "status": "TRANSVERSE_FINITE_s_ZERO_STOP_CENTER_REFINED;_INTERVAL_FLOW_CYLINDER_OPEN",
        "stop_owner": "RETAINED_EULER_DIRAC_RANK_LOSS_s_EQUALS_ZERO",
        "action_length": {
            "certified_core_to_last_positive_center": 92.0,
            "last_positive_center_to_candidate_stop": fine_hit,
            "certified_core_to_candidate_stop": 92.0 + fine_hit,
            "coarse_fine_hit_discrepancy": hit_discrepancy,
        },
        "candidate_stop": {
            "signed_descriptor": 0.0,
            "fine_integrated_descriptor_residual": fine_s,
            "coarse_integrated_descriptor_residual": coarse_s,
            "Delta": float(field["Delta"]),
            "ds_da": descriptor_rate,
            "transverse_to_stop_face": descriptor_rate < 0.0,
            "selected_branch": int(field["selected_branch"]),
            "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
            "cancelled_field_action_norm": field_norm,
            "boundary_lapse": float(np.exp(float(geometry["log_lapse"]))),
            "boundary_radius": float(np.exp(float(geometry["log_R4"]))),
            "coarse_fine_weighted_state_discrepancy": state_discrepancy,
        },
        "integrators": {"coarse": coarse_stats, "fine": fine_stats},
        "interpretation": (
            "THIS_IS_A_NUMERICAL_CENTER_FOR_ONE_FINITE_FORWARD_RESET_TO_STOP_"
            "FLOW_CYLINDER_CERTIFICATE,_NOT_AN_INTERVAL_STOP_PROOF"
        ),
        "claim_boundary": {
            "center_event_located": True,
            "stop_face_regular_at_center": descriptor_rate < 0.0,
            "between_core_and_stop_interval_shadowing": False,
            "reset_family_to_stop_cylinder_degree": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ENCLOSE_ONE_FINITE_CORRELATED_FORWARD_WITNESS_FROM_THE_CERTIFIED_"
            "1222_CORE_TO_THE_REGULAR_s_ZERO_STOP_FACE,_WITH_STRICT_EARLIER_"
            "DOMAIN_MARGINS_AND_A_SCALAR_INTERVAL_FIRST_HIT"
        ),
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            PATH_RECORD.relative_to(ROOT).as_posix(): _sha256(PATH_RECORD),
            PATH_DATA.relative_to(ROOT).as_posix(): _sha256(PATH_DATA),
        },
        "validation_passed": False,
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
    print(json.dumps({
        "status": payload["status"],
        "action_length": payload["action_length"],
        "candidate_stop": payload["candidate_stop"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2))


if __name__ == "__main__":
    main()
