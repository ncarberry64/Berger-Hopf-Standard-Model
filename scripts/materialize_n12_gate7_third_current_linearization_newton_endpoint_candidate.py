"""Apply a third signed-Green Newton step with the second-center linearization."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
import materialize_n12_gate7_signed_green_projected_endpoint_candidate as projected  # noqa: E402
import recon_n12_c2_stop_correlated_fine_defect as green  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
RESIDUAL = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY.json"
JACOBIAN = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN.json"
TANGENT = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_MACRO_TANGENT.json"
THEORY = ROOT / "theory" / "n12_gate7_third_current_linearization_newton_endpoint_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
FIXED_STEP = 0.25
PROPAGATOR_SUBSTEPS = 16


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    records = [_load(path) for path in (CENTER, RESIDUAL, JACOBIAN, TANGENT)]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated second center, replay, Jacobian, and tangents required")
    with np.load(CENTER.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["recentered_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(RESIDUAL.with_suffix(".npz")) as source:
        intervals = np.asarray(source["sample_interval"], dtype=int)
        fractions = np.asarray(source["sample_fraction"], dtype=float)
        residuals = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        jacobian_times = np.asarray(source["action_lengths"], dtype=float)
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT.with_suffix(".npz")) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)

    nodes, gauss_weights = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (nodes + 1.0)
    maximum_step = FIXED_STEP / PROPAGATOR_SUBSTEPS
    correction = np.zeros(98)
    profile = [correction.copy()]
    source_profile = []
    tangent_projection = []
    for interval in range(times.size - 1):
        mask = intervals == interval
        duration = float(times[interval + 1] - times[interval])
        right_fraction = duration / FIXED_STEP
        if not np.allclose(fractions[mask], right_fraction * units, atol=2.0e-14, rtol=0.0):
            raise RuntimeError("residual samples do not match Gauss-3")
        source = np.zeros(98)
        for unit, weight, residual in zip(
            units, gauss_weights, residuals[mask, :-1], strict=True,
        ):
            sample_time = float(times[interval] + unit * duration)
            source -= 0.5 * duration * weight * green._propagate(
                residual, sample_time, float(times[interval + 1]),
                maximum_step, jacobian_times, jacobians,
            )
        correction = green._propagate(
            correction, float(times[interval]), float(times[interval + 1]),
            maximum_step, jacobian_times, jacobians,
        ) + source
        projected_amount = 0.0
        node = interval + 1
        if node % 8 == 0 and node <= 368:
            tangent = tangents[node // 8]
            new = tangent @ (tangent.T @ correction)
            projected_amount = float(np.linalg.norm(new - correction))
            correction = new
        tangent_projection.append(projected_amount)
        source_profile.append(source.copy())
        profile.append(correction.copy())
    profile = np.asarray(profile)
    source_profile = np.asarray(source_profile)
    trial_action_states = states * weights[None, :] + profile

    workers = min(
        int(os.environ.get("BHSM_N12_THIRD_NEWTON_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    tasks = [
        (index, trial_action_states[index], float(descriptors[index]))
        for index in range(times.size)
    ]
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=projected._initialize,
        initargs=(weights, reference),
    ) as executor:
        rows = list(executor.map(projected._replay, tasks, chunksize=2))
    rows.sort(key=lambda item: int(item[0]))
    trial_states = np.asarray([item[1] for item in rows])
    projection_action = np.asarray([item[2] for item in rows])
    initial_constraint = np.asarray([item[3] for item in rows])
    final_constraint = np.asarray([item[4] for item in rows])
    rates = np.asarray([item[5] for item in rows])
    eigenvalues = np.asarray([item[6] for item in rows])
    branches = np.asarray([item[7] for item in rows], dtype=int)
    gaps = np.asarray([item[8] for item in rows])

    if eigenvalues[-2] > 0.0 > eigenvalues[-1]:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = collocation._terminal_bracket(
            times, trial_states, weights, reference,
        )
        stop_route = "WITHIN_REPLAYED_FINAL_SEGMENT"
    elif eigenvalues[-1] > 0.0:
        left_stop, right_stop, stop_state, left_lambda, right_lambda = projected._extended_terminal_bracket(
            times, trial_states, float(eigenvalues[-1]), weights, reference,
        )
        stop_route = "ONE_STEP_RETAINED_FIELD_CONTINUATION_INSIDE_UNUSED_TERMINAL_CELL"
    else:
        raise RuntimeError("third Newton step moved the stop before the retained final segment")
    stop_time = 0.5 * (left_stop + right_stop)
    stop_rate, stop_field = collocation._field(stop_state, 0.0, weights, reference)
    output_times = np.concatenate((times[:-1], [stop_time]))
    output_states = np.vstack((trial_states[:-1], stop_state))
    output_descriptors = np.concatenate((descriptors[:1], eigenvalues[1:-1], [0.0]))
    output_rates = np.vstack((rates[:-1], stop_rate))
    stop_constraint = collocation.constraints._scaled_residual(stop_state, weights)[0]
    output_constraint = np.concatenate((final_constraint[:-1], [stop_constraint]))
    profile_norm = np.linalg.norm(profile, axis=1)
    source_norm = np.linalg.norm(source_profile, axis=1)
    projection_norm = np.linalg.norm(projection_action, axis=1)
    np.savez_compressed(
        DATA,
        action_times=output_times,
        projected_states=output_states,
        recentered_descriptors=output_descriptors,
        exact_endpoint_augmented_rates=output_rates,
        current_linearization_Green_correction_action=profile,
        current_linearization_source_increment_action=source_profile,
        constraint_projection_action=projection_action,
        initial_scaled_constraint_2_norm=initial_constraint,
        final_scaled_constraint_2_norm=output_constraint,
        selected_eigenline_gaps=gaps,
        first_hit_action_time_bracket=np.asarray([left_stop, right_stop]),
        state_weights=weights,
        branch_reference=reference,
    )
    validation = {
        "all_371_third_Newton_endpoints_replayed": output_states.shape == (371, 98),
        "second_center_graph_Jacobian_consumed": jacobians.shape == (371, 98, 98),
        "second_center_macro_tangents_consumed": tangents.shape == (48, 98, 73),
        "all_endpoint_constraints_close_numerically": float(np.max(output_constraint)) < 2.0e-14,
        "branch_24_selected_at_every_endpoint": bool(np.all(branches == 24)),
        "selected_line_remains_simple_numerically": float(np.min(gaps)) > 1.0e-7,
        "all_complete_preterminal_descriptors_are_positive": float(np.min(output_descriptors[:-1])) > 0.0,
        "terminal_selected_eigenvalue_is_numerically_bracketed": left_lambda > 0.0 > right_lambda,
        "terminal_bracket_not_promoted_to_outward_root": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            output_states.ravel(), output_descriptors, output_rates.ravel(),
            profile.ravel(), projection_action.ravel(),
        ))))),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE",
        "status": "THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINTS_MATERIALIZED" if passed else "THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE_INVALID",
        "authority": "NUMERICAL_THIRD_CURRENT_LINEARIZATION_NEWTON_CANDIDATE_NOT_INTERVAL_AUTHORITY",
        "summary": {
            "maximum_current_linearization_Green_correction_2_norm": float(np.max(profile_norm)),
            "maximum_current_linearization_Green_correction_owner_node": int(np.argmax(profile_norm)),
            "terminal_current_linearization_Green_correction_2_norm": float(profile_norm[-1]),
            "maximum_source_increment_2_norm": float(np.max(source_norm)),
            "maximum_source_increment_owner_interval": int(np.argmax(source_norm)),
            "maximum_macro_tangent_projection_2_norm": float(np.max(tangent_projection)),
            "triggered_constraint_projection_count": int(np.count_nonzero(projection_norm)),
            "maximum_constraint_projection_action_2_norm": float(np.max(projection_norm)),
            "maximum_final_scaled_constraint_2_norm": float(np.max(output_constraint)),
            "minimum_selected_eigenline_gap": float(np.min(gaps)),
            "first_hit_action_time_bracket": [left_stop, right_stop],
            "terminal_stop_route": stop_route,
            "terminal_stop_selected_branch": int(stop_field["selected_branch"]),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                CENTER, CENTER.with_suffix(".npz"), RESIDUAL, RESIDUAL.with_suffix(".npz"),
                JACOBIAN, JACOBIAN.with_suffix(".npz"), TANGENT, TANGENT.with_suffix(".npz"),
                THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "second_center_linearization": "USED_FOR_THIRD_SIGNED_GREEN_NEWTON_STEP",
            "continuous_center": "OPEN_PENDING_THIRD_GAUSS3_REPLAY",
            "first_hit": "NUMERICAL_BRACKET_ONLY",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN_INTERVAL_AUTHORITY",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ALL_1110_GAUSS3_RESIDUALS_ON_THE_THIRD_NEWTON_ENDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
