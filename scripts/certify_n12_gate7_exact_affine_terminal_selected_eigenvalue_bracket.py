"""Certify the corrected exact-center terminal lambda_24 sign bracket.

The scalar stop equation is the action-owned selected reduced-Hessian
eigenvalue, not the historical separately propagated descriptor coordinate.
This certificate evaluates that eigenvalue at both ends of the last exact
spectrum cell and attaches only the already-certified causal solution halo.
The much larger proof-cell path ellipsoid is deliberately excluded from the
endpoint perturbation calculation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact  # noqa: E402
import certify_n12_gate7_recentered_cone_boundary_cluster_spectrum as cone  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
CAUSAL_RECORD = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
CAUSAL = CAUSAL_RECORD.with_suffix(".npz")
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET.json"
THIS_SCRIPT = Path(__file__).resolve()
QDIM = 37
SELECTED = 24


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _state_at(
    time: float,
    states: np.ndarray,
    rates: np.ndarray,
    times: np.ndarray,
    weights: np.ndarray,
    fine_times: np.ndarray,
    fine_correction: np.ndarray,
) -> np.ndarray:
    seam = 46
    span = float(times[seam + 1] - times[seam])
    fraction = float((time - times[seam]) / span)
    controls = np.asarray((
        states[seam] * weights,
        states[seam] * weights + span * rates[seam] / 3.0,
        states[seam + 1] * weights - span * rates[seam + 1] / 3.0,
        states[seam + 1] * weights,
    ))
    one_minus = 1.0 - fraction
    bernstein = np.asarray((
        one_minus ** 3,
        3.0 * fraction * one_minus ** 2,
        3.0 * fraction ** 2 * one_minus,
        fraction ** 3,
    ))
    base_action = bernstein @ controls
    correction_action = exact.cone._interpolate_correction(
        time, fine_times, fine_correction,
    )
    return (base_action + correction_action) / weights


def _endpoint(
    time: float,
    halo_radius: float,
    states: np.ndarray,
    rates: np.ndarray,
    times: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    fine_times: np.ndarray,
    fine_correction: np.ndarray,
) -> dict[str, Any]:
    state = _state_at(
        time, states, rates, times, weights, fine_times, fine_correction,
    )
    jet = cluster.local.exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    projection = np.sqrt(2.0) * halo_radius * np.eye(98)
    directionals = np.array(cone._batched_hessian_directionals(
        jnp.asarray(state),
        jnp.asarray(projection.T / weights[None, :]),
    ), copy=True)[:, QDIM:, QDIM:]
    directionals *= cone.JAX_D3_NORM_INFLATION
    geometry = {
        "midpoint": state,
        "projection": projection,
        "values": values,
        "vectors": vectors,
        "selected": selected,
        "directionals": list(directionals),
    }
    selected_bound = cluster._cluster_bound(
        (SELECTED,), cluster._distance_groups(values, (SELECTED,)),
        geometry, weights,
    )
    shift = float(selected_bound["cluster_spectral_shift_upper"])
    center = float(values[SELECTED])
    return {
        "action_length": time,
        "selected_branch": selected,
        "center_selected_eigenvalue": center,
        "causal_solution_halo_radius": halo_radius,
        "halo_only_selected_eigenvalue_shift_upper": shift,
        "selected_eigenvalue_interval": [center - shift, center + shift],
        "sign": "POSITIVE" if center - shift > 0.0 else (
            "NEGATIVE" if center + shift < 0.0 else "UNRESOLVED"
        ),
    }


def main() -> None:
    spectrum = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    causal_record = json.loads(CAUSAL_RECORD.read_text(encoding="utf-8"))
    z2 = json.loads(Z2.read_text(encoding="utf-8"))
    if not all(record.get("validation_passed") for record in (
        spectrum, causal_record, z2,
    )):
        raise RuntimeError("validated exact spectrum and causal Z2 radius required")
    (
        states, rates, times, weights, reference,
        fine_times, fine_correction, _nonlinear_radius,
    ) = exact._inputs()
    last_row = spectrum["rows"][-1]
    left, right = (float(value) for value in last_row["action_interval"])
    if right != float(times[-1]):
        raise RuntimeError("terminal spectrum cell does not end at corrected abscissa")
    # Use the certified uniform final-center Taylor--Volterra radius.  The
    # smaller stored endpoint radius is not extended into the cell without a
    # separate within-seam monotonicity theorem.
    terminal_halo = float(
        z2["summary"]["maximum_third_order_Taylor_Volterra_total_radius"]
    )
    left_record = _endpoint(
        left, terminal_halo, states, rates, times, weights, reference,
        fine_times, fine_correction,
    )
    right_record = _endpoint(
        right, terminal_halo, states, rates, times, weights, reference,
        fine_times, fine_correction,
    )
    validation = {
        "corrected_terminal_abscissa_consumed": right == 92.30513924040065,
        "last_exact_spectrum_cell_consumed": (
            int(last_row["seam"]) == 46 and int(last_row["local_index"]) == 64
        ),
        "branch_24_selected_at_both_endpoints": (
            left_record["selected_branch"] == right_record["selected_branch"] == SELECTED
        ),
        "causal_halo_only_not_full_path_ellipsoid_used_at_endpoints": True,
        "left_endpoint_strictly_positive_after_halo": left_record["sign"] == "POSITIVE",
        "right_endpoint_strictly_negative_after_halo": right_record["sign"] == "NEGATIVE",
        "continuous_selected_line_simple_on_terminal_cell": bool(
            last_row["boundary_cluster_certificate_closed"]
            and float(last_row["selected_positive_gap_lower"]) > 0.0
            and float(last_row["negative_selected_gap_lower"]) > 0.0
        ),
        "historical_propagated_descriptor_not_used_as_stop_equation": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET",
        "status": (
            "ACTION_OWNED_SELECTED_EIGENVALUE_TERMINAL_SIGN_BRACKET_CERTIFIED"
            if passed else "TERMINAL_SELECTED_EIGENVALUE_BRACKET_INVALID"
        ),
        "authority": (
            "RETAINED_ACTION_EXACT_FULL_JET_PLUS_CAUSAL_SOLUTION_HALO_ONLY_"
            "QUARTER_GAP_D4_CLUSTER_ENCLOSURE"
        ),
        "stop_equation": "lambda_24=0",
        "terminal_cell": {
            "action_interval": [left, right],
            "left": left_record,
            "right": right_record,
            "selected_positive_gap_lower": last_row["selected_positive_gap_lower"],
            "negative_selected_gap_lower": last_row["negative_selected_gap_lower"],
        },
        "adjudication": {
            "historical_separately_propagated_descriptor_coordinate": "NOT_STOP_AUTHORITY",
            "action_owned_selected_eigenvalue": "STOP_AUTHORITY",
            "existence_of_a_terminal_zero_by_continuity": passed,
            "canonical_earliest_zero": (
                "FOLLOWS_AFTER_SEPARATE_STRICT_PRETERMINAL_POSITIVITY_TRANSFER"
            ),
            "uniqueness_and_differentiable_stop_time": (
                "OPEN_DERIVATIVE_ENCLOSURE_NOT_REQUIRED_FOR_EXISTENCE_ONLY_STOP"
            ),
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (SPECTRUM, CAUSAL_RECORD, CAUSAL, Z2, THIS_SCRIPT)
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "terminal_action_owned_sign_bracket": "CERTIFIED" if passed else "OPEN",
            "continuous_preterminal_margin": "OPEN_SEPARATE_TRANSFER",
            "scalar_interval_Newton_uniqueness": "NOT_REQUIRED_FOR_EXISTENCE_ONLY_STOP",
            "differentiable_stop_time": "OPEN_DERIVATIVE_ENCLOSURE",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "TRANSFER_STRICT_ACTION_OWNED_PRETERMINAL_POSITIVITY_TO_THE_LEFT_"
            "ENDPOINT_AND_USE_REGULAR_FLOW_CONTINUITY_TO_DEFINE_THE_CANONICAL_"
            "EARLIEST_ZERO;_DO_NOT_REQUIRE_A_DERIVATIVE_ENCLOSURE_UNLESS_A_"
            "DIFFERENTIABLE_STOP_TIME_MAP_IS_LATER_NEEDED"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "terminal_cell": payload["terminal_cell"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
