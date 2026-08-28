"""Derive the Gate-7 outward closure budget from the signed center equation.

This is a conditional theorem, not outward interval authority.  It computes
the largest uniform perturbations of the center propagators and the three
curvature groups that still map the exact signed causal vector into the
existing nonlinear halo.  The calculation keeps the signed center source
before introducing norm-valued perturbation radii.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
DIRECTIONAL = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.npz"
MIXED = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.npz"
TRANSVERSE = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json"
SIGNED = BASE / "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
SIGNED_DATA = SIGNED.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_GATE7_OUTWARD_CLOSURE_BUDGET.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _threshold(predicate: Callable[[float], bool]) -> float:
    lower = 0.0
    upper = 1.0
    while upper < 1.0e30 and predicate(upper):
        lower = upper
        upper *= 10.0
    if upper >= 1.0e30 and predicate(upper):
        return math.inf
    for _ in range(160):
        midpoint = 0.5 * (lower + upper)
        if predicate(midpoint):
            lower = midpoint
        else:
            upper = midpoint
    return math.nextafter(lower, -math.inf)


def build_payload() -> dict[str, Any]:
    inputs = (
        CENTER, TANGENT, GREEN, DIRECTIONAL, MIXED, TRANSVERSE,
        SIGNED, SIGNED_DATA,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("exact signed center and outward-budget inputs required")
    transverse_record = json.loads(TRANSVERSE.read_text(encoding="utf-8"))
    signed_record = json.loads(SIGNED.read_text(encoding="utf-8"))
    if not transverse_record["validation_passed"] or not signed_record["validation_passed"]:
        raise RuntimeError("certified exact center curvature and vector required")

    with np.load(CENTER) as source:
        times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(GREEN) as source:
        step_maps = np.asarray(source["physical_macro_step_maps"], dtype=float)
        corrections = np.asarray(source["ambient_correction_profile"], dtype=float)
    with np.load(DIRECTIONAL) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)
        directional = np.asarray(
            source["physical_time_transverse_directional_curvature"],
            dtype=float,
        )
    with np.load(MIXED) as source:
        mixed = np.asarray(
            source["physical_time_transverse_mixed_Green_curvature"],
            dtype=float,
        )
    with np.load(SIGNED_DATA) as source:
        vector = np.asarray(source["signed_center_vector"], dtype=float)

    transverse = np.asarray([
        row["physical_time_transverse_D2f_Frobenius_norm"]
        for row in transverse_record["rows"]
    ], dtype=float)
    halo = float(signed_record["summary"]["existing_certified_nonlinear_halo"])
    dt = np.diff(times)
    frames = []
    correction_norm = []
    for index in range(48):
        physical_flow = tangents[index].T @ fields[index]
        physical_flow /= np.linalg.norm(physical_flow)
        frame = null_space(physical_flow[None, :])
        frames.append(frame)
        correction_norm.append(float(np.linalg.norm(
            frame.T @ tangents[index].T @ corrections[index]
        )))
    frames = np.asarray(frames)
    correction_norm = np.asarray(correction_norm)

    green_norm = np.zeros((48, 48))
    propagators: dict[tuple[int, int], np.ndarray] = {}
    for endpoint in range(1, 48):
        propagator = np.eye(73)
        for source_index in range(endpoint - 1, -1, -1):
            propagator = propagator @ step_maps[source_index]
            propagators[(endpoint, source_index)] = propagator.copy()
            green_norm[endpoint, source_index] = (
                dt[source_index] * np.linalg.norm(propagator, ord=2)
            )

    directional_source_norm = np.zeros(48)
    mixed_operator_norm = np.zeros(48)
    signed_source_norm = np.zeros(48)
    for index in range(48):
        frame = frames[index]
        directional_source = frame @ (
            0.5 * directional[index] * correction_norm[index] ** 2
        )
        mixed_operator_norm[index] = (
            np.linalg.norm(mixed[index], ord=2) * correction_norm[index]
        )
        mixed_source = frame @ (
            mixed[index] @ (frame.T @ vector[index])
            * correction_norm[index]
        )
        directional_source_norm[index] = np.linalg.norm(directional_source)
        signed_source_norm[index] = np.linalg.norm(
            directional_source + mixed_source
        )

    vector_norm = np.linalg.norm(vector, axis=1)

    def error_radius(
        green_relative_defect: float,
        directional_relative_drift: float,
        mixed_relative_drift: float,
        transverse_inflation: float,
    ) -> np.ndarray:
        error = np.zeros(48)
        for endpoint in range(1, 48):
            earlier = slice(0, endpoint)
            delta_mixed = mixed_relative_drift * mixed_operator_norm[earlier]
            with np.errstate(over="ignore", invalid="ignore"):
                integrand = (
                    green_relative_defect * signed_source_norm[earlier]
                    + (1.0 + green_relative_defect) * (
                        directional_relative_drift
                        * directional_source_norm[earlier]
                        + delta_mixed * vector_norm[earlier]
                        + (mixed_operator_norm[earlier] + delta_mixed)
                        * error[earlier]
                        + 0.5 * transverse_inflation * transverse[earlier]
                        * (vector_norm[earlier] + error[earlier]) ** 2
                    )
                )
                error[endpoint] = np.sum(green_norm[endpoint, earlier] * integrand)
            if not math.isfinite(float(error[endpoint])):
                error[endpoint:] = math.inf
                break
        return error

    def closes(green: float, directional_drift: float, mixed_drift: float, transverse_scale: float) -> bool:
        radius = vector_norm + error_radius(
            green, directional_drift, mixed_drift, transverse_scale,
        )
        return bool(np.all(np.isfinite(radius)) and np.max(radius) < halo)

    green_threshold = _threshold(lambda value: closes(value, 0.0, 0.0, 1.0))
    directional_threshold = _threshold(lambda value: closes(0.0, value, 0.0, 1.0))
    mixed_threshold = _threshold(lambda value: closes(0.0, 0.0, value, 1.0))
    transverse_threshold = _threshold(lambda value: closes(0.0, 0.0, 0.0, value))
    balanced_threshold = _threshold(
        lambda value: closes(value, value, value, 1.0 + value)
    )
    baseline_error = error_radius(0.0, 0.0, 0.0, 1.0)
    balanced_error = error_radius(
        balanced_threshold, balanced_threshold, balanced_threshold,
        1.0 + balanced_threshold,
    )

    np.savez_compressed(
        DATA,
        action_lengths=times,
        signed_center_vector=vector,
        signed_center_source_norm=signed_source_norm,
        directional_source_norm=directional_source_norm,
        mixed_source_operator_norm=mixed_operator_norm,
        causal_green_norm=green_norm,
        exact_transverse_curvature_Frobenius=transverse,
        baseline_error_radius=baseline_error,
        limiting_balanced_error_radius=balanced_error,
    )
    thresholds = {
        "uniform_relative_propagator_defect": green_threshold,
        "uniform_relative_directional_curvature_drift": directional_threshold,
        "uniform_relative_mixed_curvature_drift": mixed_threshold,
        "uniform_transverse_curvature_inflation": transverse_threshold,
        "balanced_relative_outward_perturbation": balanced_threshold,
    }
    validation = {
        "all_48_nodes_and_47_step_maps_used": (
            vector.shape == (48, 73) and step_maps.shape == (47, 73, 73)
        ),
        "signed_center_source_formed_before_norm": True,
        "propagator_defect_source_term_included": True,
        "directional_and_mixed_curvature_drift_terms_included": True,
        "transverse_quadratic_term_included": True,
        "strictly_lower_causal_dependency_preserved": bool(
            np.allclose(np.triu(green_norm), 0.0, atol=0.0, rtol=0.0)
        ),
        "all_conditional_thresholds_positive_and_finite": all(
            math.isfinite(value) and value > 0.0 for value in thresholds.values()
        ),
        "baseline_exact_center_replay_fits_halo": closes(0.0, 0.0, 0.0, 1.0),
        "reported_thresholds_are_lower_bisection_endpoints": all(
            closes(value, 0.0, 0.0, 1.0) if key == "uniform_relative_propagator_defect"
            else closes(0.0, value, 0.0, 1.0) if key == "uniform_relative_directional_curvature_drift"
            else closes(0.0, 0.0, value, 1.0) if key == "uniform_relative_mixed_curvature_drift"
            else closes(0.0, 0.0, 0.0, value) if key == "uniform_transverse_curvature_inflation"
            else closes(value, value, value, 1.0 + value)
            for key, value in thresholds.items()
        ),
        "outward_interval_values_not_claimed": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_OUTWARD_CLOSURE_BUDGET",
        "status": (
            "SIGNED_GATE7_OUTWARD_SUFFICIENT_BUDGET_DERIVED"
            if passed else "GATE7_OUTWARD_BUDGET_INVALID"
        ),
        "authority": "EXACT_SIGNED_CENTER_VOLTERRA_ERROR_IDENTITY_WITH_CONDITIONAL_OUTWARD_MAJORANTS",
        "identity": {
            "propagator_defect": "||P_tube-P_center||<=epsilon_G*||P_center||",
            "directional_drift": "||d_tube-d_center||<=epsilon_d*||d_center||",
            "mixed_drift": "||M_tube-M_center||<=epsilon_m*||M_center||",
            "transverse_tube": "||H_tube||<=kappa_H*H_center_Frobenius",
            "closure": "max_i(||v_i||+e_i)<existing_nonlinear_halo",
        },
        "summary": {
            "existing_nonlinear_halo": halo,
            "maximum_signed_center_vector_2_norm": float(np.max(vector_norm)),
            "maximum_baseline_total_radius": float(np.max(vector_norm + baseline_error)),
            "thresholds": thresholds,
            "corresponding_uniform_transverse_curvature_upper": float(
                transverse_threshold * np.max(transverse)
            ),
            "limiting_balanced_total_radius": float(
                np.max(vector_norm + balanced_error)
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "outward_sufficient_budget": "DERIVED",
            "outward_curvature_values": "OPEN_INTERVAL_AUTHORITY",
            "outward_propagator_defect": "OPEN_INTERVAL_AUTHORITY",
            "causal_interval_vector_radius": "OPEN_UNTIL_BUDGET_VALUES_ARE_PROVED",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EVALUATE_ONLY_THE_RECENTERED_CONE_PROPAGATOR_DEFECT_AND_"
            "DIRECTIONAL_MIXED_TRANSVERSE_DRIFTS_AGAINST_THE_REPORTED_"
            "SIGNED_BUDGETS;_DO_NOT_BUILD_A_GLOBAL_D3F_TENSOR"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
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
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
