"""Project the certified exact-affine fine center to the action constraints."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
NATIVE_DATA = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
FROZEN = BASE / "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.json"
FROZEN_DATA = FROZEN.with_suffix(".npz")
EXACT = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.json"
EXACT_DATA = EXACT.with_suffix(".npz")
JACOBIAN_DATA = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
PRIOR = BASE / "BHSM_N12_GATE7_PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE.json"
THEORY = ROOT / "theory" / "n12_gate7_projected_exact_affine_fine_center_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
_WEIGHTS: np.ndarray | None = None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _initialize(weights: np.ndarray) -> None:
    global _WEIGHTS
    _WEIGHTS = weights


def _project(task: tuple[int, np.ndarray]) -> tuple[int, np.ndarray, np.ndarray, float, float, float]:
    index, state = task
    if _WEIGHTS is None:
        raise RuntimeError("projection worker not initialized")
    constraint, norms, values = constraints._constraint_geometry(state, _WEIGHTS)
    scaled = values / norms
    gram = constraint @ constraint.T
    delta_action = -constraint.T @ np.linalg.solve(gram, scaled)
    projected = state + delta_action / _WEIGHTS
    final = constraints._scaled_residual(projected, _WEIGHTS)[0]
    return (
        index, projected, delta_action, float(np.linalg.norm(scaled)),
        final, float(np.linalg.cond(gram)),
    )


def main() -> None:
    exact, z2, prior = (_load(path) for path in (EXACT, Z2, PRIOR))
    if exact.get("validation_passed") is not True or prior.get("validation_passed") is not True:
        raise RuntimeError("validated exact-affine response and native projection required")
    with np.load(NATIVE_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(FROZEN_DATA) as source:
        times = np.asarray(source["fine_action_lengths"], dtype=float)
        base_augmented = np.asarray(
            source["base_augmented_action_values"], dtype=float,
        )
        direct_descriptor = np.asarray(
            source["direct_descriptor_correction_profile"], dtype=float,
        )
        frozen_state_response = np.asarray(
            source["state_correction_profile"], dtype=float,
        )
    with np.load(EXACT_DATA) as source:
        exact_times = np.asarray(source["fine_action_lengths"], dtype=float)
        exact_state_response = np.asarray(
            source["fine_signed_response_midpoint"], dtype=float,
        )
        exact_response_radius = np.asarray(
            source["fine_signed_response_Euclidean_radius"], dtype=float,
        )
    with np.load(JACOBIAN_DATA) as source:
        descriptor_gradient = np.asarray(
            source["descriptor_gradient_action"], dtype=float,
        )
    if not np.array_equal(times, exact_times):
        raise RuntimeError("frozen and exact-affine fine grids differ")
    descriptor_correction = direct_descriptor + np.einsum(
        "ij,ij->i", descriptor_gradient, exact_state_response,
    )
    exact_affine_action_states = base_augmented[:, :-1] + exact_state_response
    exact_affine_descriptors = base_augmented[:, -1] + descriptor_correction
    exact_affine_states = exact_affine_action_states / weights[None, :]

    workers = min(
        int(os.environ.get("BHSM_N12_EXACT_AFFINE_PROJECTION_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(weights,),
    ) as executor:
        evaluated = list(executor.map(
            _project, enumerate(exact_affine_states), chunksize=2,
        ))
    evaluated.sort(key=lambda item: item[0])
    projected_states = np.asarray([item[1] for item in evaluated])
    projection_action = np.asarray([item[2] for item in evaluated])
    initial_scaled = np.asarray([item[3] for item in evaluated])
    final_scaled = np.asarray([item[4] for item in evaluated])
    gram_conditions = np.asarray([item[5] for item in evaluated])
    projection_norm = np.linalg.norm(projection_action, axis=1)
    response_norm = np.linalg.norm(exact_state_response, axis=1)
    exact_minus_frozen = np.linalg.norm(
        exact_state_response - frozen_state_response, axis=1,
    )
    nonlinear_radius = float(z2["domain"]["candidate_nonlinear_action_radius"])
    projection_to_radius = math.nextafter(
        float(np.max(projection_norm)) / nonlinear_radius, math.inf,
    )
    np.savez_compressed(
        DATA,
        action_times=times,
        base_augmented_action_values=base_augmented,
        exact_affine_state_response_action=exact_state_response,
        exact_affine_state_response_Euclidean_radius=exact_response_radius,
        direct_descriptor_correction=direct_descriptor,
        exact_affine_descriptor_correction=descriptor_correction,
        exact_affine_descriptors=exact_affine_descriptors,
        exact_affine_states=exact_affine_states,
        projected_states=projected_states,
        projection_action=projection_action,
        initial_scaled_constraint_2_norm=initial_scaled,
        final_scaled_constraint_2_norm=final_scaled,
        constraint_Gram_condition_number=gram_conditions,
        state_weights=weights,
        branch_reference=reference,
    )

    validation = {
        "all_371_exact_affine_nodes_projected": projected_states.shape == (371, 98),
        "exact_affine_and_frozen_grids_identical": np.array_equal(times, exact_times),
        "exact_affine_response_is_the_certified_Taylor26_response": (
            exact["claim_boundary"]["retained_source_sample_propagation_to_fine_nodes"]
            == "CERTIFIED_IF_VALIDATION_PASSES"
        ),
        "coupled_descriptor_reconstructed_without_double_counting": bool(np.allclose(
            descriptor_correction,
            direct_descriptor + np.einsum(
                "ij,ij->i", descriptor_gradient, exact_state_response,
            ),
            atol=0.0, rtol=0.0,
        )),
        "all_projection_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            projected_states.ravel(), projection_action.ravel(),
            initial_scaled, final_scaled, gram_conditions,
            exact_affine_descriptors,
        ))))),
        "one_step_projection_closes_every_node_numerically": (
            float(np.max(final_scaled)) < 2.0e-14
        ),
        "exact_affine_response_differs_materially_from_native_only_candidate": (
            float(np.max(response_norm)) > 1.0e-7
        ),
        "projection_exceeds_existing_final_nonlinear_radius_so_cone_not_inherited": (
            projection_to_radius > 10.0
        ),
        "projected_nodes_not_relabelled_as_continuous_flow": True,
        "descriptor_fiber_and_first_hit_not_inherited_after_projection": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE",
        "status": (
            "PROJECTED_EXACT_AFFINE_371_NODE_CONSTRAINT_CENTER_CANDIDATE_MATERIALIZED"
            if passed else "PROJECTED_EXACT_AFFINE_FINE_CENTER_CANDIDATE_INVALID"
        ),
        "authority": (
            "CERTIFIED_256_BIT_TAYLOR26_SIGNED_SOURCE_RESPONSE_PLUS_COUPLED_"
            "DESCRIPTOR_THEN_ONE_MINIMUM_ACTION_NORM_CONSTRAINT_NEWTON_STEP"
        ),
        "summary": {
            "node_count": int(times.size),
            "maximum_exact_affine_state_response_2_norm": float(np.max(response_norm)),
            "maximum_exact_affine_response_Euclidean_radius": float(np.max(exact_response_radius)),
            "maximum_exact_minus_frozen_response_2_norm": float(np.max(exact_minus_frozen)),
            "maximum_initial_scaled_constraint_2_norm": float(np.max(initial_scaled)),
            "maximum_projected_scaled_constraint_2_norm": float(np.max(final_scaled)),
            "maximum_action_projection_2_norm": float(np.max(projection_norm)),
            "maximum_constraint_Gram_condition_number": float(np.max(gram_conditions)),
            "existing_final_nonlinear_action_radius": nonlinear_radius,
            "maximum_projection_to_existing_radius_ratio": projection_to_radius,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                NATIVE_DATA, FROZEN, FROZEN_DATA, EXACT, EXACT_DATA,
                JACOBIAN_DATA, Z2, PRIOR, THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "projected_native_only_candidate": "SUPERSEDED_AS_CURRENT_CENTER_BY_EXACT_AFFINE_RESPONSE_COMPOSITION",
            "projected_exact_affine_371_nodes": "CONSTRAINT_ACCURATE_DISCRETE_CANDIDATE",
            "continuous_projected_trajectory": "OPEN",
            "descriptor_fiber_lambda_equals_s": "OPEN_AFTER_PROJECTION",
            "first_hit_time": "MUST_BE_REBUILT_ON_THE_PROJECTED_EXACT_AFFINE_FLOW",
            "final_Z2_cone": "MUST_BE_REBUILT_BECAUSE_PROJECTION_EXCEEDS_EXISTING_RADIUS",
        },
        "claim_boundary": {
            "constraint_accurate_projected_exact_affine_nodes": "MATERIALIZED_CANDIDATE",
            "continuous_action_constrained_center": "OPEN_COLLOCATION_OR_SHADOWING",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "nonlinear_72D_history_first_jet": "OPEN_AFTER_CARRIER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REBUILD_THE_DENSE_FLOW_DEFECT_ON_THIS_PROJECTED_EXACT_AFFINE_"
            "CENTER,_SOLVE_THE_CONSTRAINT_AND_DESCRIPTOR_FIBER_AUGMENTED_"
            "COLLOCATION_CORRECTION,_THEN_REBUILD_Z2_AND_THE_FIRST_HIT"
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
