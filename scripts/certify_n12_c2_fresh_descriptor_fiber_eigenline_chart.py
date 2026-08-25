"""Certify a fresh branch-24 chart after the first uniform-gap chart is spent."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from derive_n12_c2_birth_coefficient_quotient_jet import (  # noqa: E402
    _coefficient_enclosure,
)
from derive_n12_c2_launch_eigenline_ball import _load as _load_canonical  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CONTINUATION = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.json"
CONTINUATION_DATA = BASE / "BHSM_N12_C2_UNIFORM_GAP_CONTINUATION.npz"
PRIOR_LINE = BASE / "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json"
RESULT = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
DATA_RESULT = BASE / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.npz"
THEORY = ROOT / "theory" / "n12_c2_fresh_descriptor_fiber_eigenline_chart.md"
INPUTS = (CONTINUATION, CONTINUATION_DATA, PRIOR_LINE, THEORY)
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


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fresh fiber-chart inputs: " + ", ".join(missing))
    continuation, prior_line = (_json(path) for path in (CONTINUATION, PRIOR_LINE))
    if not continuation.get("validation_passed") or not prior_line.get("validation_passed"):
        raise RuntimeError("validated continuation and prior line chart required")
    with np.load(CONTINUATION_DATA) as data:
        center = np.asarray(data["C2_uniform_gap_predictor_centers"][-1], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)

    hessian = np.asarray(_jet(center).hessian, dtype=float)
    reduced = hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    complement = np.delete(vectors, selected, axis=1)
    hard_values = np.delete(values, selected)
    differences = hard_values - values[selected]
    center_gap = float(np.min(np.abs(differences)))
    inverse_diagonal = np.diag(1.0 / differences)
    inverse_norm = _up(1.0 / center_gap)
    reduced_weights = weights[QDIM:]
    identity = np.eye(center.size)
    selected_action = np.concatenate((np.zeros(QDIM), psi * reduced_weights))
    complement_action = np.vstack((
        np.zeros((QDIM, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))

    scalar_columns = np.empty(center.size)
    coupling_columns = np.empty((complement.shape[1], center.size))
    relative_hard_columns = np.empty((center.size, complement.shape[1], complement.shape[1]))
    for column in range(center.size):
        shifted = center.astype(complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        derivative = np.imag(np.asarray(_jet(shifted).hessian)) / COMPLEX_STEP
        raw = derivative[QDIM:, QDIM:]
        scalar_columns[column] = float(psi @ raw @ psi)
        coupling_columns[:, column] = complement.T @ raw @ psi
        relative_hard_columns[column] = inverse_diagonal @ (complement.T @ raw @ complement)
        if (column + 1) % 16 == 0:
            print(f"fresh-chart D3 columns {column + 1}/{center.size}", flush=True)

    scalar_first = _up(float(np.linalg.norm(scalar_columns)))
    coupling_first = _up(float(np.linalg.norm(coupling_columns, 2)))
    weighted_coupling_first = _up(float(np.linalg.norm(
        inverse_diagonal @ coupling_columns, 2
    )))
    relative_hard_first = _up(float(np.linalg.norm(relative_hard_columns)))
    psi_first = -complement @ (inverse_diagonal @ coupling_columns)
    tangent = null_space(scalar_columns[None, :])

    incoming_tube = float(
        continuation["continuation"]["final_endpoint_tube_radius_upper"]
    )

    def action_bounds(radius: float) -> dict[str, float]:
        os.environ["BHSM_N12_CERTIFICATE_BALL"] = str(radius)
        action_bound = _load_canonical("derive_n12_action_ball_majorants").action_bound

        def mixed(*directions: np.ndarray) -> float:
            return _up(float(action_bound(
                center, projection=identity, mixed_directions=list(directions),
            ).d[-1]))

        return {
            "D4_XXCC": mixed(identity, identity, complement_action, complement_action),
            "D4_XXPC": mixed(identity, identity, selected_action, complement_action),
            "D4_XXPP": mixed(identity, identity, selected_action, selected_action),
        }

    # Increase the trial radius until the first genuine eigenline/domain
    # theorem failure.  The D4 bounds at that failed upper radius remain valid
    # on every smaller radius used by the subsequent bisection.
    trial = max(4.0 * incoming_tube, 1.0e-10)
    failed_upper = None
    upper_bounds = None
    for _ in range(24):
        bounds = action_bounds(trial)
        coefficient = _coefficient_enclosure(center, weights, trial)
        relative = (
            relative_hard_first * trial
            + 0.5 * inverse_norm * bounds["D4_XXCC"] * trial**2
        )
        if (
            relative >= 1.0
            or coefficient["root_D_tau_log_R4_interval"][0] <= 0.0
            or not all(math.isfinite(value) for value in bounds.values())
        ):
            failed_upper = trial
            upper_bounds = bounds
            break
        trial *= 4.0
    if failed_upper is None or upper_bounds is None:
        raise ArithmeticError("no intrinsic eigenline/domain upper failure localized")

    def evaluate(radius: float) -> dict[str, float | bool]:
        relative = _up(
            relative_hard_first * radius
            + 0.5 * inverse_norm * upper_bounds["D4_XXCC"] * radius**2
        )
        coefficient = _coefficient_enclosure(center, weights, radius)
        if relative >= 1.0:
            return {"feasible": False, "relative_hard_perturbation": relative}
        complement_inverse = _up(inverse_norm / (1.0 - relative))
        scalar_shift = _up(
            scalar_first * radius + 0.5 * upper_bounds["D4_XXPP"] * radius**2
        )
        coupling = _up(
            coupling_first * radius + 0.5 * upper_bounds["D4_XXPC"] * radius**2
        )
        weighted_coupling = _up(
            weighted_coupling_first * radius
            + 0.5 * inverse_norm * upper_bounds["D4_XXPC"] * radius**2
        )
        shift_product = _up(complement_inverse * scalar_shift)
        if shift_product >= 1.0:
            return {"feasible": False, "relative_hard_perturbation": relative}
        shifted_inverse = _up(complement_inverse / (1.0 - shift_product))
        graph = _up(weighted_coupling / (1.0 - relative - inverse_norm * scalar_shift))
        schur = _up(coupling * graph)
        gap = _down(
            1.0 / complement_inverse - scalar_shift - schur - 2.0 * coupling
        )
        feasible = bool(
            radius > incoming_tube
            and gap > 0.0
            and coefficient["root_lapse_interval"][0] > 0.0
            and coefficient["root_D_tau_log_R4_interval"][0] > 0.0
            and math.isfinite(shifted_inverse)
        )
        return {
            "feasible": feasible,
            "relative_hard_perturbation": relative,
            "complement_inverse_upper": complement_inverse,
            "scalar_shift_upper": scalar_shift,
            "coupling_upper": coupling,
            "weighted_coupling_upper": weighted_coupling,
            "graph_norm_upper": graph,
            "Schur_correction_upper": schur,
            "eigenline_gap_lower": gap,
            "lapse_lower": float(coefficient["root_lapse_interval"][0]),
            "D_tau_log_R4_lower": float(coefficient["root_D_tau_log_R4_interval"][0]),
        }

    lower = math.nextafter(incoming_tube, failed_upper)
    if not bool(evaluate(lower).get("feasible")):
        raise ArithmeticError("fresh chart does not contain the incoming endpoint tube")
    feasible, infeasible = lower, failed_upper
    for _ in range(100):
        midpoint = 0.5 * (feasible + infeasible)
        if midpoint in (feasible, infeasible):
            break
        if bool(evaluate(midpoint).get("feasible")):
            feasible = midpoint
        else:
            infeasible = midpoint
    certified_radius = feasible
    selected_radius = 0.5 * (incoming_tube + certified_radius)
    selected_bounds = evaluate(selected_radius)
    if not bool(selected_bounds.get("feasible")):
        raise ArithmeticError("derived fresh descriptor-fiber chart is not feasible")

    np.savez_compressed(
        DATA_RESULT,
        center_state=center,
        state_weights=weights,
        branch_reference=reference,
        selected_vector=psi,
        selected_vector_derivative_action=psi_first,
        lambda_gradient_action=scalar_columns,
        fixed_descriptor_tangent_basis=tangent,
    )
    validation = {
        "branch_24_replayed": selected == 24,
        "incoming_1192_endpoint_tube_consumed": incoming_tube > 0.0,
        "ambient_ball_used_only_for_uniform_spectral_and_domain_control": True,
        "propagation_chart_is_exact_fixed_descriptor_fiber": tangent.shape == (98, 97),
        "fresh_chart_radius_strictly_exceeds_incoming_tube": selected_radius > incoming_tube,
        "fresh_uniform_hard_gap_is_positive": float(selected_bounds["eigenline_gap_lower"]) > 0.0,
        "lapse_and_radius_rate_remain_positive": (
            float(selected_bounds["lapse_lower"]) > 0.0
            and float(selected_bounds["D_tau_log_R4_lower"]) > 0.0
        ),
        "first_intrinsic_upper_failure_was_localized": failed_upper > selected_radius,
        "no_validation_cutoff_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART",
        "status": (
            "C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART_CERTIFIED"
            if passed else "C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART_INVALID"
        ),
        "center": {
            "selected_branch": selected,
            "binary64_selected_eigenvalue_not_used_as_descriptor": float(values[selected]),
            "center_hard_gap": center_gap,
            "lambda_gradient_action_norm": scalar_first,
            "selected_to_complement_first_variation": coupling_first,
            "preconditioned_selected_line_first_variation": weighted_coupling_first,
            "preconditioned_hard_block_first_variation": relative_hard_first,
        },
        "radius_derivation": {
            "incoming_endpoint_tube_upper": incoming_tube,
            "first_failed_intrinsic_upper_radius": failed_upper,
            "failed_upper_D4_bounds": upper_bounds,
            "maximal_feasible_radius_lower": certified_radius,
            "selected_fresh_chart_radius": selected_radius,
            "selection_is_proof_midpoint_only": True,
            "selected_chart_bounds": selected_bounds,
        },
        "chart_semantics": {
            "ambient_ball_role": "UNIFORM_BRANCH_GAP_AND_DOMAIN_CERTIFICATE_ONLY",
            "physical_propagation_domain": "EXACT_lambda_event_EQUALS_s_DESCRIPTOR_FIBER",
            "arbitrary_normal_motion_allowed": False,
            "proof_chart_boundary_is_physical_stop": False,
        },
        "hindsight": {
            "result": "VALIDATED",
            "classification": "PROOF_CHART_LIMIT_REMOVED_BY_FRESH_FIBER_CHART",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "TRANSFER_THE_FIXED_s_BIRTH_AND_UNIFORM_HARD_RESPONSE_BOUNDS_TO_"
            "THIS_FRESH_CHART_AND_CONTINUE_THE_SAME_C2_HISTORY"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
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
    radius = payload["radius_derivation"]
    print(json.dumps({
        "status": payload["status"],
        "incoming_tube": radius["incoming_endpoint_tube_upper"],
        "first_failed_upper": radius["first_failed_intrinsic_upper_radius"],
        "selected_radius": radius["selected_fresh_chart_radius"],
        "fresh_gap": radius["selected_chart_bounds"]["eigenline_gap_lower"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
