"""Audit whether the stored within-seam center is action-constraint admissible."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact  # noqa: E402
import certify_n12_gate7_exact_affine_terminal_selected_eigenvalue_bracket as bracket  # noqa: E402
import materialize_n12_gate7_exact_center_physical_field_jacobian as direct  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
FIELD = BASE / "BHSM_N12_GATE7_EXACT_CENTER_PHYSICAL_FIELD_JACOBIAN.json"
FIELD_DATA = FIELD.with_suffix(".npz")
FIRST_HIT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
FIRST_HIT_DATA = FIRST_HIT.with_suffix(".npz")
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
THEORY = ROOT / "theory" / "n12_gate7_within_seam_constraint_center_obstruction.md"
RESULT = BASE / "BHSM_N12_GATE7_WITHIN_SEAM_CONSTRAINT_CENTER_OBSTRUCTION.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
QDIM = 37
NEWTON_STEPS = 4


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _constraint_geometry(
    state: np.ndarray, weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    jet = direct._jet(state)
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    velocity = state[QDIM:2 * QDIM]
    energy_row = np.concatenate((
        hessian[QDIM:2 * QDIM, :QDIM].T @ velocity - gradient[:QDIM],
        hessian[QDIM:2 * QDIM, QDIM:2 * QDIM].T @ velocity,
        hessian[QDIM:2 * QDIM, 2 * QDIM:].T @ velocity
        - gradient[2 * QDIM:],
    ))
    raw = np.vstack((hessian[2 * QDIM:, :], energy_row))
    action = raw / weights[None, :]
    norms = np.linalg.norm(action, axis=1)
    normalized = action / norms[:, None]
    values = np.concatenate((
        gradient[2 * QDIM:],
        [velocity @ gradient[QDIM:2 * QDIM] - float(jet.value)],
    ))
    return normalized, norms, values


def _scaled_residual(state: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    _, norms, values = _constraint_geometry(state, weights)
    scaled = values / norms
    return float(np.linalg.norm(scaled)), float(np.max(np.abs(scaled)))


def _linearized_correction(
    state: np.ndarray, weights: np.ndarray,
) -> tuple[float, float, float]:
    constraint, norms, values = _constraint_geometry(state, weights)
    scaled = values / norms
    gram = constraint @ constraint.T
    delta_action = -constraint.T @ np.linalg.solve(gram, scaled)
    return (
        float(np.linalg.norm(scaled)),
        float(np.linalg.norm(delta_action)),
        float(np.linalg.cond(gram)),
    )


def _newton_project(
    initial: np.ndarray, weights: np.ndarray,
) -> tuple[np.ndarray, list[float], float]:
    state = np.array(initial, copy=True)
    history = []
    maximum_gram_condition = 0.0
    for _ in range(NEWTON_STEPS):
        constraint, norms, values = _constraint_geometry(state, weights)
        scaled = values / norms
        history.append(float(np.linalg.norm(scaled)))
        gram = constraint @ constraint.T
        maximum_gram_condition = max(
            maximum_gram_condition, float(np.linalg.cond(gram)),
        )
        delta_action = -constraint.T @ np.linalg.solve(gram, scaled)
        state += delta_action / weights
    history.append(_scaled_residual(state, weights)[0])
    return state, history, maximum_gram_condition


def main() -> None:
    field, first_hit, causal = (
        _load(path) for path in (FIELD, FIRST_HIT, CAUSAL)
    )
    if not all(record.get("validation_passed") is True for record in (
        field, first_hit, causal,
    )):
        raise RuntimeError("validated direct-field, first-hit, and causal parents required")
    (
        states, rates, times, weights, _reference,
        fine_times, fine_correction, _nonlinear_radius,
    ) = exact._inputs()
    with np.load(FIELD_DATA) as source:
        node_times = np.asarray(source["action_lengths"], dtype=float)
        node_states = np.asarray(source["exact_center_states"], dtype=float)
    with np.load(FIRST_HIT_DATA) as source:
        first_hit_midpoint = float(source["first_hit_action_time_midpoint"])

    node_diagnostics = np.asarray([
        _linearized_correction(state, weights) for state in node_states
    ])
    node_scaled = node_diagnostics[:, 0]
    node_linearized_correction = node_diagnostics[:, 1]
    node_gram_condition = node_diagnostics[:, 2]
    midpoint_times = []
    midpoint_initial_scaled = []
    midpoint_initial_max = []
    midpoint_correction = []
    midpoint_final_scaled = []
    midpoint_gram_condition = []
    rows = []
    for seam in range(47):
        right = first_hit_midpoint if seam == 46 else float(times[seam + 1])
        midpoint = 0.5 * (float(times[seam]) + right)
        initial = bracket._state_at(
            midpoint, states, rates, times, weights, fine_times, fine_correction,
        )
        initial_scaled, initial_max = _scaled_residual(initial, weights)
        projected, history, gram_condition = _newton_project(initial, weights)
        correction = float(np.linalg.norm((projected - initial) * weights))
        final_scaled = float(history[-1])
        midpoint_times.append(midpoint)
        midpoint_initial_scaled.append(initial_scaled)
        midpoint_initial_max.append(initial_max)
        midpoint_correction.append(correction)
        midpoint_final_scaled.append(final_scaled)
        midpoint_gram_condition.append(gram_condition)
        rows.append({
            "seam": seam,
            "midpoint_action_time": midpoint,
            "initial_scaled_constraint_2_norm": initial_scaled,
            "initial_scaled_constraint_maximum": initial_max,
            "four_step_Newton_action_correction_2_norm": correction,
            "four_step_Newton_final_scaled_constraint_2_norm": final_scaled,
            "Newton_scaled_residual_history": history,
            "maximum_constraint_Gram_condition_number": gram_condition,
        })

    midpoint_times = np.asarray(midpoint_times)
    midpoint_initial_scaled = np.asarray(midpoint_initial_scaled)
    midpoint_initial_max = np.asarray(midpoint_initial_max)
    midpoint_correction = np.asarray(midpoint_correction)
    midpoint_final_scaled = np.asarray(midpoint_final_scaled)
    midpoint_gram_condition = np.asarray(midpoint_gram_condition)
    maximum_macro_radius = float(causal["summary"][
        "maximum_exact_total_center_radius"
    ])
    correction_to_macro_radius = math.nextafter(
        float(np.max(midpoint_correction)) / maximum_macro_radius, math.inf,
    )
    node_correction_to_macro_radius = math.nextafter(
        float(np.max(node_linearized_correction)) / maximum_macro_radius,
        math.inf,
    )
    np.savez_compressed(
        DATA,
        macro_node_action_times=node_times,
        macro_node_scaled_constraint_2_norm=node_scaled,
        macro_node_linearized_action_correction_2_norm=node_linearized_correction,
        macro_node_constraint_Gram_condition_number=node_gram_condition,
        seam_midpoint_action_times=midpoint_times,
        seam_midpoint_initial_scaled_constraint_2_norm=midpoint_initial_scaled,
        seam_midpoint_initial_scaled_constraint_maximum=midpoint_initial_max,
        seam_midpoint_four_step_Newton_action_correction_2_norm=midpoint_correction,
        seam_midpoint_four_step_Newton_final_scaled_constraint_2_norm=midpoint_final_scaled,
        seam_midpoint_maximum_constraint_Gram_condition_number=midpoint_gram_condition,
    )

    validation = {
        "all_48_materialized_macro_nodes_audited": node_scaled.shape == (48,),
        "all_47_retained_seam_midpoints_audited": midpoint_times.shape == (47,),
        "all_quantities_are_finite": bool(np.all(np.isfinite(np.concatenate((
            node_scaled, node_linearized_correction, node_gram_condition,
            midpoint_initial_scaled, midpoint_correction, midpoint_final_scaled,
            midpoint_gram_condition,
        ))))),
        "birth_macro_node_is_constraint_accurate": (
            float(node_scaled[0]) < 2.0e-12
        ),
        "exact_affine_corrected_macro_path_has_constraint_drift": (
            float(np.max(node_scaled[1:])) > 1.0e-11
        ),
        "macro_node_constraint_correction_exceeds_center_radius": (
            node_correction_to_macro_radius > 10.0
        ),
        "stored_within_seam_interpolant_is_not_constraint_accurate": (
            float(np.max(midpoint_initial_scaled)) > 1.0e-5
        ),
        "Newton_projection_closes_each_midpoint_numerically": (
            float(np.max(midpoint_final_scaled)) < 2.0e-14
        ),
        "projection_correction_cannot_be_hidden_in_macro_center_radius": (
            correction_to_macro_radius > 1.0e6
        ),
        "projection_not_relabelled_as_flow_connection": True,
        "continuous_variational_carrier_not_promoted": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_WITHIN_SEAM_CONSTRAINT_CENTER_OBSTRUCTION",
        "status": (
            "DIRECT_CONTINUOUS_ACTION_CONSTRAINED_CENTER_REQUIRED_BEFORE_VARIATIONAL_CARRIER"
            if passed else "WITHIN_SEAM_CONSTRAINT_CENTER_AUDIT_INVALID"
        ),
        "authority": (
            "DIRECT_RETAINED_FULL_ACTION_GRADIENT_HESSIAN_CONSTRAINT_ROWS_ON_"
            "ALL_MACRO_NODES_AND_SEAM_MIDPOINTS"
        ),
        "summary": {
            "birth_macro_node_scaled_constraint_2_norm": float(node_scaled[0]),
            "maximum_corrected_macro_node_scaled_constraint_2_norm": float(np.max(node_scaled[1:])),
            "first_hit_midpoint_scaled_constraint_2_norm": float(node_scaled[-1]),
            "maximum_macro_node_linearized_action_correction_2_norm": float(np.max(node_linearized_correction)),
            "maximum_macro_node_linearized_correction_to_center_radius_ratio": node_correction_to_macro_radius,
            "maximum_seam_midpoint_scaled_constraint_2_norm": float(np.max(midpoint_initial_scaled)),
            "maximum_four_step_Newton_action_correction_2_norm": float(np.max(midpoint_correction)),
            "maximum_four_step_Newton_final_scaled_constraint_2_norm": float(np.max(midpoint_final_scaled)),
            "maximum_constraint_Gram_condition_number": float(np.max(midpoint_gram_condition)),
            "maximum_exact_macro_center_radius": maximum_macro_radius,
            "maximum_projection_correction_to_macro_radius_ratio": correction_to_macro_radius,
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                FIELD, FIELD_DATA, FIRST_HIT, FIRST_HIT_DATA, CAUSAL,
                THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "discrete_stored_center_field_Jacobians": "NUMERICAL_FORMULA_EVALUATIONS_NOT_CONSTRAINT_CENTER_AUTHORITY",
            "first_hit_midpoint_field_Jacobian": "REPRESENTATIVE_ONLY_NOT_CONSTRAINT_CENTER_AUTHORITY",
            "stored_Hermite_plus_fine_correction_within_seam_path": (
                "REJECTED_AS_DIRECT_ACTION_CONSTRAINED_CENTER"
            ),
            "Newton_projected_midpoints": "DIAGNOSTIC_ONLY_NOT_A_FLOW_CONNECTION",
            "continuous_center_owner": (
                "DIRECT_NORMALIZED_ACTION_FLOW_WITH_CONSTRAINT_PRESERVATION_"
                "AND_FIRST_HIT_TERMINAL_ENCLOSURE"
            ),
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN",
            "continuous_outward_variational_carrier": "BLOCKED_ON_CENTER",
            "nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "INTEGRATE_AND_OUTWARD_CERTIFY_THE_DIRECT_NORMALIZED_ACTION_FIELD_"
            "FROM_THE_RESET_SEED_TO_THE_FIRST_HIT_WHILE_PRESERVING_THE_25_"
            "ACTION_CONSTRAINTS;_THEN_EVALUATE_DF_ALONG_THAT_CENTER"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
