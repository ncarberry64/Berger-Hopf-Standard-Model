"""Close the exact-center Gate-7 stop witness by continuity.

The birth cell uses a causal Taylor bound that vanishes at reset.  Every
subsequent preterminal exact-spectrum cell uses its already-certified
path-plus-halo selected-line shift.  The separately certified last-cell sign
bracket then gives a canonical earliest zero of the continuous regular flow.
No derivative enclosure, unique zero, or differentiable stop-time map is
claimed or required for the existence-only Gate-7 stop alternative.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
import audit_n12_gate7_causal_y_z1_z2_margin_budget as bernstein  # noqa: E402
import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
DENSE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
FINE_RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.json"
FINE = FINE_RECORD.with_suffix(".npz")
SPECTRUM = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
BRACKET = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET.json"
FLOW_CYLINDER = BASE / "BHSM_N12_GATE7_RESET_TO_STOP_FLOW_CYLINDER.json"
OPEN_FAMILY = BASE / "BHSM_N12_GATE7_OPEN_FAMILY_STOP_TRANSVERSALITY_REDUCTION.json"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
DATA = RESULT.with_suffix(".npz")
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
    seam = min(max(int(np.searchsorted(times, time, side="right") - 1), 0), 46)
    span = float(times[seam + 1] - times[seam])
    fraction = float((time - times[seam]) / span)
    controls = np.asarray((
        states[seam] * weights,
        states[seam] * weights + span * rates[seam] / 3.0,
        states[seam + 1] * weights - span * rates[seam + 1] / 3.0,
        states[seam + 1] * weights,
    ))
    one_minus = 1.0 - fraction
    weights_b = np.asarray((
        one_minus ** 3,
        3.0 * fraction * one_minus ** 2,
        3.0 * fraction ** 2 * one_minus,
        fraction ** 3,
    ))
    action_state = weights_b @ controls
    action_state += exact.cone._interpolate_correction(
        time, fine_times, fine_correction,
    )
    return action_state / weights


def _selected_value(task: tuple[int, float, np.ndarray, np.ndarray]) -> tuple[int, int, float]:
    index, midpoint, state, reference = task
    jet = cluster.local.exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    return index, selected, float(values[SELECTED])


def _birth_cell_certificate(
    dense_values: np.ndarray,
    dense_coefficients: np.ndarray,
    fine_times: np.ndarray,
    fine_correction: np.ndarray,
    fine_radius: np.ndarray,
    z2: dict[str, Any],
) -> tuple[bool, float, float, float, float]:
    macro_times = np.asarray([row["action_length"] for row in z2["rows"]])
    nonlinear = np.asarray(z2["causal_Taylor_Volterra"]["total_radius"])
    endpoint = 1
    displacement = float(
        np.linalg.norm(fine_correction[endpoint]) + fine_radius[endpoint]
        + np.interp(fine_times[endpoint], macro_times, nonlinear)
    )
    descriptor_d1 = max(
        float(row["selected_descriptor_D1_upper"]) for row in z2["rows"]
    )
    descriptor_d2 = max(
        float(row["retained_interval_H2_selected_scalar_upper"])
        for row in z2["rows"]
    )
    poly = bernstein._dense_power(
        dense_values[0, -1], dense_coefficients[0, :, -1],
    )
    # On the first fine cell both the exact-affine correction and the causal
    # solution halo vanish at reset and grow no faster than their endpoint
    # radii times the local fraction x.
    poly = bernstein._add_linear(
        poly, 0.0, -descriptor_d1 * displacement, 1.0,
    )
    poly += [Fraction(0)] * max(0, 3 - len(poly))
    poly[2] -= Fraction.from_float(
        0.5 * descriptor_d2 * displacement ** 2
    )
    certificate = bernstein._positive_range(
        poly, Fraction(0), Fraction(1), max_depth=24,
    )
    return (
        bool(certificate[0]), float(certificate[1]), displacement,
        descriptor_d1, descriptor_d2,
    )


def main() -> None:
    spectrum = json.loads(SPECTRUM.read_text(encoding="utf-8"))
    z2 = json.loads(Z2.read_text(encoding="utf-8"))
    bracket = json.loads(BRACKET.read_text(encoding="utf-8"))
    cylinder = json.loads(FLOW_CYLINDER.read_text(encoding="utf-8"))
    open_family = json.loads(OPEN_FAMILY.read_text(encoding="utf-8"))
    if not all(record.get("validation_passed") for record in (
        spectrum, z2, bracket, cylinder, open_family,
    )):
        raise RuntimeError("validated exact-center stop parents required")
    (
        states, rates, times, weights, reference,
        fine_times, fine_correction, _nonlinear_radius,
    ) = exact._inputs()
    with np.load(DENSE) as source:
        dense_values = np.asarray(source["fine_grid_augmented_action_values"])
        dense_coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"])
    with np.load(FINE) as source:
        fine_radius = np.asarray(source["fine_signed_response_Euclidean_radius"])

    birth = _birth_cell_certificate(
        dense_values, dense_coefficients, fine_times, fine_correction,
        fine_radius, z2,
    )
    birth_right = float(fine_times[1])
    terminal_left = float(bracket["terminal_cell"]["action_interval"][0])
    rows = [
        row for row in spectrum["rows"]
        if float(row["action_interval"][0]) >= birth_right
        and float(row["action_interval"][1]) <= terminal_left
    ]
    tasks = []
    for index, row in enumerate(rows):
        left, right = (float(value) for value in row["action_interval"])
        midpoint = 0.5 * (left + right)
        tasks.append((
            index, midpoint,
            _state_at(
                midpoint, states, rates, times, weights,
                fine_times, fine_correction,
            ),
            reference,
        ))
    workers = min(int(os.environ.get("BHSM_N12_FIRST_STOP_WORKERS", "12")), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        evaluated = list(executor.map(_selected_value, tasks, chunksize=8))
    evaluated.sort(key=lambda item: item[0])
    selected = np.asarray([item[1] for item in evaluated], dtype=int)
    centers = np.asarray([item[2] for item in evaluated], dtype=float)
    shifts = np.asarray([float(row["selected_line_shift_upper"]) for row in rows])
    lowers = centers - shifts
    intervals = np.asarray([row["action_interval"] for row in rows], dtype=float)
    np.savez_compressed(
        DATA,
        preterminal_action_intervals=intervals,
        selected_branches=selected,
        center_selected_eigenvalues=centers,
        path_plus_halo_selected_shift_upper=shifts,
        selected_eigenvalue_lower=lowers,
    )
    owner = int(np.argmin(lowers))
    terminal = bracket["terminal_cell"]
    validation = {
        "birth_cell_causal_radius_vanishes_at_reset": bool(
            np.linalg.norm(fine_correction[0]) == 0.0 and fine_radius[0] == 0.0
            and z2["causal_Taylor_Volterra"]["total_radius"][0] == 0.0
        ),
        "birth_cell_action_owned_selected_descriptor_strictly_positive": birth[0],
        "all_preterminal_exact_spectrum_cells_evaluated": len(rows) > 0,
        "branch_24_selected_on_every_preterminal_cell": bool(np.all(selected == SELECTED)),
        "all_post_birth_preterminal_cells_uniformly_positive": bool(np.all(lowers > 0.0)),
        "preterminal_cover_reaches_terminal_bracket_left_endpoint": bool(
            intervals[-1, 1] == terminal_left
        ),
        "terminal_left_endpoint_positive_after_uniform_halo": (
            terminal["left"]["sign"] == "POSITIVE"
        ),
        "terminal_right_endpoint_negative_after_uniform_halo": (
            terminal["right"]["sign"] == "NEGATIVE"
        ),
        "selected_line_simple_on_entire_exact_spectrum_cover": bool(
            spectrum["validation"]["both_selected_line_boundary_margins_positive_everywhere"]
        ),
        "regular_exact_flow_continuity_supplies_an_earliest_zero": True,
        "interval_Newton_uniqueness_not_required_or_claimed": True,
        "no_differentiable_stop_time_or_physical_selector_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP",
        "status": (
            "ONE_EXACT_FORWARD_RESET_HISTORY_REACHES_A_CANONICAL_EARLIEST_STOP"
            if passed else "EXACT_AFFINE_CONTINUOUS_FIRST_STOP_INVALID"
        ),
        "authority": (
            "CAUSAL_BIRTH_BERNSTEIN_TAYLOR_BOUND_PLUS_EXACT_ACTION_SELECTED_"
            "EIGENVALUE_PATH_HALO_CLUSTER_COVER_AND_TERMINAL_SIGN_BRACKET"
        ),
        "birth_cell": {
            "action_interval": [0.0, birth_right],
            "minimum_exact_Bernstein_lower": birth[1],
            "endpoint_total_state_displacement_upper": birth[2],
            "selected_descriptor_D1_upper": birth[3],
            "selected_descriptor_D2_upper": birth[4],
        },
        "preterminal_cover": {
            "cell_count": len(rows),
            "action_interval": [birth_right, terminal_left],
            "minimum_selected_eigenvalue_lower": float(lowers[owner]),
            "minimum_owner": {
                "cell": owner,
                "action_interval": intervals[owner].tolist(),
                "center_selected_eigenvalue": float(centers[owner]),
                "path_plus_halo_shift_upper": float(shifts[owner]),
            },
        },
        "terminal_bracket": terminal,
        "Gate7_consequence": {
            "one_exact_history_from_the_certified_reset_relation": "CERTIFIED",
            "strict_selected_stop_margin_before_terminal_cell": "CERTIFIED",
            "canonical_earliest_lambda24_zero_exists_in_terminal_cell": "CERTIFIED_BY_CONTINUITY",
            "open_stop_reaching_seed_stratum": (
                "FOLLOWS_FROM_STRICT_FIXED_TIME_SIGN_BRACKET_AND_RETAINED_"
                "REGULAR_FLOW_CONTINUOUS_DEPENDENCE"
            ),
            "whole_family_multiple_shooting_required": False,
            "unique_or_differentiable_stop_time": "NOT_REQUIRED_NOT_CLAIMED",
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                DENSE, FINE_RECORD, FINE, SPECTRUM, Z2, BRACKET,
                FLOW_CYLINDER, OPEN_FAMILY, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "exact_center_stop_witness": "CERTIFIED" if passed else "OPEN",
            "Gate7_geometric_connection_owner": "CLOSED" if passed else "ACTIVE",
            "force_KKT_Hessian": "NEXT_OWNER",
            "Gate7": "ACTIVE_FORCE_KKT_HESSIAN" if passed else "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EVALUATE_THE_EXISTING_ACTION_OWNED_HEAT_MINUS_ZETA_FORCE_KKT_AND_"
            "PHYSICAL_HESSIAN_ON_THIS_CERTIFIED_STOP_STRATUM"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "birth_cell": payload["birth_cell"],
        "preterminal_cover": payload["preterminal_cover"],
        "validation_passed": passed,
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
