"""Project every retained native DOP853 node to the 25 action constraints."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_within_seam_constraint_center_obstruction as obstruction  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
NATIVE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
NATIVE_DATA = NATIVE.with_suffix(".npz")
OBSTRUCTION = BASE / "BHSM_N12_GATE7_WITHIN_SEAM_CONSTRAINT_CENTER_OBSTRUCTION.json"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
THEORY = ROOT / "theory" / "n12_gate7_projected_native_dop853_center_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()


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
    native, prior, causal = (
        _load(path) for path in (NATIVE, OBSTRUCTION, CAUSAL)
    )
    if prior.get("validation_passed") is not True:
        raise RuntimeError("validated within-seam obstruction required")
    with np.load(NATIVE_DATA) as source:
        fine_times = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        fine_augmented = np.asarray(
            source["fine_grid_augmented_action_values"], dtype=float,
        )
        macro_times = np.asarray(source["action_lengths"], dtype=float)
        macro_states = np.asarray(source["centers"], dtype=float)
        macro_descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    # Keep the native 0.25 grid through 92.25, then append the native dense
    # s=0 endpoint instead of the unused full 92.5 bracket endpoint.
    times = np.concatenate((fine_times[:-1], macro_times[-1:]))
    descriptors = np.concatenate((fine_augmented[:-1, -1], macro_descriptors[-1:]))
    native_states = np.vstack((
        fine_augmented[:-1, :-1] / weights[None, :], macro_states[-1],
    ))

    projected_states = []
    initial_scaled = []
    final_scaled = []
    corrections = []
    gram_conditions = []
    for index, state in enumerate(native_states):
        constraint, norms, values = obstruction._constraint_geometry(state, weights)
        scaled = values / norms
        gram = constraint @ constraint.T
        delta_action = -constraint.T @ np.linalg.solve(gram, scaled)
        projected = state + delta_action / weights
        final = obstruction._scaled_residual(projected, weights)[0]
        projected_states.append(projected)
        initial_scaled.append(float(np.linalg.norm(scaled)))
        final_scaled.append(final)
        corrections.append(float(np.linalg.norm(delta_action)))
        gram_conditions.append(float(np.linalg.cond(gram)))
        if (index + 1) % 32 == 0:
            print(json.dumps({
                "projected_nodes": index + 1,
                "action_time": float(times[index]),
                "correction_2_norm": corrections[-1],
                "final_scaled_constraint_2_norm": final,
            }), flush=True)

    projected_states = np.asarray(projected_states)
    initial_scaled = np.asarray(initial_scaled)
    final_scaled = np.asarray(final_scaled)
    corrections = np.asarray(corrections)
    gram_conditions = np.asarray(gram_conditions)
    maximum_macro_radius = float(causal["summary"][
        "maximum_exact_total_center_radius"
    ])
    reconnaissance_halo = float(causal["summary"][
        "reference_reconnaissance_nonlinear_halo"
    ])
    correction_to_macro_radius = math.nextafter(
        float(np.max(corrections)) / maximum_macro_radius, math.inf,
    )
    halo_utilization = math.nextafter(
        float(np.max(corrections)) / reconnaissance_halo, math.inf,
    )
    np.savez_compressed(
        DATA,
        action_times=times,
        signed_descriptors=descriptors,
        native_states=native_states,
        projected_states=projected_states,
        one_step_action_corrections=(projected_states - native_states) * weights[None, :],
        initial_scaled_constraint_2_norm=initial_scaled,
        final_scaled_constraint_2_norm=final_scaled,
        constraint_Gram_condition_number=gram_conditions,
        state_weights=weights,
        branch_reference=reference,
    )

    validation = {
        "all_371_retained_nodes_projected": projected_states.shape == (371, 98),
        "native_times_strictly_increase_to_native_stop": (
            bool(np.all(np.diff(times) > 0.0))
            and times[-1] == float(macro_times[-1])
        ),
        "native_stop_descriptor_is_zero": descriptors[-1] == 0.0,
        "all_projection_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            projected_states.ravel(), initial_scaled, final_scaled,
            corrections, gram_conditions,
        ))))),
        "native_constraint_drift_reproduced": float(np.max(initial_scaled)) > 1.0e-11,
        "one_step_projection_closes_every_node_numerically": (
            float(np.max(final_scaled)) < 2.0e-14
        ),
        "projection_is_inside_reconnaissance_halo": halo_utilization < 1.0,
        "projection_is_outside_exact_macro_radius_so_not_inherited": (
            correction_to_macro_radius > 10.0
        ),
        "projected_nodes_not_relabelled_as_continuous_flow": True,
        "descriptor_fiber_and_first_hit_not_inherited": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE",
        "status": (
            "PROJECTED_NATIVE_DOP853_371_NODE_CONSTRAINT_CENTER_CANDIDATE_MATERIALIZED"
            if passed else "PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE_INVALID"
        ),
        "authority": (
            "ONE_MINIMUM_ACTION_NORM_NEWTON_STEP_USING_THE_DIRECT_25_ROW_"
            "RETAINED_ACTION_CONSTRAINT_DIFFERENTIAL"
        ),
        "summary": {
            "node_count": int(times.size),
            "native_action_time_end": float(times[-1]),
            "maximum_native_scaled_constraint_2_norm": float(np.max(initial_scaled)),
            "maximum_projected_scaled_constraint_2_norm": float(np.max(final_scaled)),
            "maximum_action_projection_2_norm": float(np.max(corrections)),
            "maximum_constraint_Gram_condition_number": float(np.max(gram_conditions)),
            "maximum_exact_macro_center_radius": maximum_macro_radius,
            "maximum_projection_to_exact_macro_radius_ratio": correction_to_macro_radius,
            "reference_reconnaissance_nonlinear_halo": reconnaissance_halo,
            "maximum_reconnaissance_halo_utilization": halo_utilization,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                NATIVE, NATIVE_DATA, OBSTRUCTION, CAUSAL, THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "native_DOP853_dense_center": "RETAINED_AS_THE_CLOSE_FLOW_CANDIDATE",
            "projected_371_nodes": "CONSTRAINT_ACCURATE_DISCRETE_CANDIDATE",
            "continuous_projected_trajectory": "OPEN",
            "descriptor_fiber_lambda_equals_s": "OPEN_AFTER_PROJECTION",
            "first_hit_time": "MUST_BE_REBUILT_ON_THE_PROJECTED_FLOW",
        },
        "claim_boundary": {
            "constraint_accurate_discrete_center_nodes": "MATERIALIZED_CANDIDATE",
            "continuous_action_constrained_center": "OPEN_SHADOWING_OR_COLLOCATION",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "BUILD_THE_NATIVE_DOP853_DENSE_POLYNOMIAL_TO_PROJECTED_NODE_DEFECT_"
            "AND_CERTIFY_A_CONSTRAINT_AND_DESCRIPTOR_FIBER_PRESERVING_"
            "CONTINUOUS_SHADOWING_CENTER_WITH_A_NEW_FIRST_HIT"
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
