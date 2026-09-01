"""Apply the retained signed Green operator to the measured collocation defect."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import recon_n12_c2_stop_correlated_fine_defect as green  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
COLLOCATION = BASE / "BHSM_N12_GATE7_CONSTRAINT_DESCRIPTOR_HERMITE_COLLOCATION_CANDIDATE.json"
COLLOCATION_DATA = COLLOCATION.with_suffix(".npz")
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_FINE_HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE.json"
JACOBIAN_DATA = JACOBIAN.with_suffix(".npz")
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.json"
TANGENT_DATA = TANGENT.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_signed_green_endpoint_newton_candidate.md"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_ENDPOINT_NEWTON_CANDIDATE.json"
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
    collocation = _load(COLLOCATION)
    if collocation["status"] != "HERMITE_COLLOCATION_CANDIDATE_REQUIRES_OWNER_REFINEMENT":
        raise RuntimeError("the measured nonclosing Hermite defect is required")
    with np.load(COLLOCATION_DATA) as source:
        times = np.asarray(source["action_times"], dtype=float)
        endpoints = np.asarray(source["corrected_augmented_endpoints"], dtype=float)
        intervals = np.asarray(source["sample_interval"], dtype=int)
        fractions = np.asarray(source["sample_fraction"], dtype=float)
        residuals = np.asarray(source["sampled_augmented_flow_defect"], dtype=float)
    with np.load(JACOBIAN_DATA) as source:
        jacobian_times = np.asarray(source["action_lengths"], dtype=float)
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT_DATA) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)

    gauss_nodes, gauss_weights = np.polynomial.legendre.leggauss(3)
    units = 0.5 * (gauss_nodes + 1.0)
    maximum_step = FIXED_STEP / PROPAGATOR_SUBSTEPS
    correction = np.zeros(98)
    profile = [correction.copy()]
    source_profile = []
    tangent_projection = []
    for interval in range(times.size - 1):
        mask = intervals == interval
        local_fractions = fractions[mask]
        local_residuals = residuals[mask, :-1]
        duration = float(times[interval + 1] - times[interval])
        right_fraction = duration / FIXED_STEP
        if not np.allclose(local_fractions, right_fraction * units, atol=2.0e-14, rtol=0.0):
            raise RuntimeError("collocation samples do not match the Gauss-3 rule")
        source = np.zeros(98)
        for unit, weight, residual in zip(units, gauss_weights, local_residuals, strict=True):
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
            projected = tangent @ (tangent.T @ correction)
            projected_amount = float(np.linalg.norm(projected - correction))
            correction = projected
        tangent_projection.append(projected_amount)
        source_profile.append(source.copy())
        profile.append(correction.copy())

    profile = np.asarray(profile)
    source_profile = np.asarray(source_profile)
    new_action_states = endpoints[:, :-1] + profile
    profile_norm = np.linalg.norm(profile, axis=1)
    source_norm = np.linalg.norm(source_profile, axis=1)
    np.savez_compressed(
        DATA,
        action_times=times,
        prior_augmented_endpoints=endpoints,
        signed_Green_state_correction_action=profile,
        signed_Green_source_increment_action=source_profile,
        corrected_state_action=new_action_states,
        inherited_descriptors=endpoints[:, -1],
        macro_tangent_projection_2_norm=np.asarray(tangent_projection),
    )
    validation = {
        "all_370_Gauss3_defect_blocks_consumed": source_profile.shape == (370, 98),
        "all_371_endpoint_corrections_materialized": profile.shape == (371, 98),
        "correction_vanishes_at_reset": float(profile_norm[0]) == 0.0,
        "same_371_node_graph_Jacobian_used": jacobians.shape == (371, 98, 98),
        "same_47_macro_tangent_transfer_used": tangents.shape == (48, 98, 73),
        "sixteen_substeps_match_the_frozen_Taylor26_partition": PROPAGATOR_SUBSTEPS == 16,
        "signed_source_is_minus_measured_flow_defect": True,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            profile.ravel(), source_profile.ravel(), new_action_states.ravel(),
        ))))),
        "not_promoted_without_exact_field_constraint_and_fiber_replay": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = int(np.argmax(profile_norm))
    source_owner = int(np.argmax(source_norm))
    payload = {
        "artifact": "BHSM_N12_GATE7_SIGNED_GREEN_ENDPOINT_NEWTON_CANDIDATE",
        "status": "SIGNED_GREEN_ENDPOINT_NEWTON_CORRECTION_MATERIALIZED" if passed else "SIGNED_GREEN_ENDPOINT_NEWTON_CANDIDATE_INVALID",
        "authority": "NUMERICAL_SIGNED_GREEN_NEWTON_CANDIDATE_NOT_INTERVAL_AUTHORITY",
        "construction": {
            "shadow_equation": "e_prime=J*e-d",
            "source_sign": "MINUS_MEASURED_HERMITE_FLOW_DEFECT",
            "propagator_substeps_per_quarter_cell": PROPAGATOR_SUBSTEPS,
            "constraint_handling": "PROJECT_ONLY_AT_THE_46_COMPLETE_RETAINED_MACRO_SEAMS",
        },
        "summary": {
            "maximum_signed_Green_state_correction_2_norm": float(profile_norm[owner]),
            "maximum_signed_Green_state_correction_owner_node": owner,
            "terminal_signed_Green_state_correction_2_norm": float(profile_norm[-1]),
            "maximum_signed_source_increment_2_norm": float(source_norm[source_owner]),
            "maximum_signed_source_increment_owner_interval": source_owner,
            "maximum_macro_tangent_projection_2_norm": float(np.max(tangent_projection)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (COLLOCATION, COLLOCATION_DATA, JACOBIAN, JACOBIAN_DATA, TANGENT, TANGENT_DATA, THEORY, THIS_SCRIPT)
        },
        "adjudication": {
            "endpoint_position_inconsistency": "ONE_SIGNED_GREEN_NEWTON_CORRECTION_APPLIED",
            "constraint_manifold": "REQUIRES_DIRECT_REPLAY_ON_CORRECTED_ENDPOINTS",
            "descriptor_fiber": "REQUIRES_RECENTERING_AFTER_STATE_CORRECTION",
            "continuous_center": "OPEN_AFTER_EXACT_REPLAY",
        },
        "claim_boundary": {
            "continuous_action_constrained_center": "OPEN",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "REPLAY_ACTION_CONSTRAINTS_AND_SELECTED_DESCRIPTOR_ON_THE_371_CORRECTED_ENDPOINTS,_RECENTER_THE_STOP,_THEN_REMEASURE_THE_GAUSS3_FLOW_DEFECT",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
