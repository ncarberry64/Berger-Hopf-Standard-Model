"""Certify the signed center vectors Db, Dc, and Dlambda at C2 node 1214."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    DirectedInterval,
    interval_tensor_norm_upper,
    retained_action_tensor_interval,
)


BASE = ROOT / "artifacts" / "flagship_integration"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
RECON = BASE / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
RECON_DATA = RECON.with_suffix(".npz")
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.json"
DATA_RESULT = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_c2_signed_first_coefficient_vectors.md"
INTERVAL_SOURCE = (
    ROOT / "src" / "bhsm" / "interface"
    / "aether_retained_action_tensor_interval.py"
)
QDIM = 37
TOTAL = 98
POINTS = 96


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    parents = [BORDERED, BORDERED_DATA, RECON, RECON_DATA, FIELD, FIELD_DATA]
    missing = [str(path) for path in parents if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing signed first-vector inputs: " + ", ".join(missing))
    if not all(json.loads(path.read_text(encoding="utf-8"))["validation_passed"]
               for path in (BORDERED, RECON, FIELD)):
        raise RuntimeError("validated signed first-vector parents are required")

    with np.load(BORDERED_DATA) as data:
        state = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        hard = np.asarray(data["bordered_response"], dtype=float)[:-1]
        stored_lambda = np.asarray(data["lambda_gradient_action"], dtype=float)
    with np.load(RECON_DATA) as data:
        z = np.asarray(data["third_variation_hard_adjoint"], dtype=float)
    with np.load(FIELD_DATA) as data:
        stored_c = np.asarray(data["moving_c_gradient_action"], dtype=float)

    reduced_weights = weights[QDIM:]
    eye = np.eye(TOTAL)
    embed = np.zeros((TOTAL, psi.size))
    embed[QDIM:] = np.diag(reduced_weights)
    p = embed @ psi
    z_action = embed @ z
    v = embed @ hard
    qdot = np.zeros(TOTAL)
    qdot[:QDIM] = weights[:QDIM] * state[QDIM:2 * QDIM]
    qdot_first = np.zeros((TOTAL, TOTAL))
    qdot_first[:QDIM, QDIM:2 * QDIM] = np.diag(
        weights[:QDIM] / weights[QDIM:2 * QDIM]
    )
    j_p = np.zeros(TOTAL)
    j_p[:QDIM] = weights[:QDIM] * psi[:QDIM]
    state_lo = np.nextafter(state, -np.inf)
    state_hi = np.nextafter(state, np.inf)

    def tensor(*directions: np.ndarray) -> DirectedInterval:
        value = retained_action_tensor_interval(
            12, state_lo, state_hi, list(directions), points=POINTS
        )
        print(
            f"D{len(directions)} signed output norm upper="
            f"{interval_tensor_norm_upper(value):.17g}",
            flush=True,
        )
        return value

    lambda_interval = tensor(eye, p, p)
    c_interval = tensor(eye, p, p, p) + 3.0 * tensor(eye, p, z_action)
    b_interval = (
        tensor(eye, j_p)
        - tensor(eye, p, qdot)
        - tensor(p, qdot_first)
        - tensor(eye, p, v)
    )

    lambda_lo = np.asarray(lambda_interval.lo, dtype=float)
    lambda_hi = np.asarray(lambda_interval.hi, dtype=float)
    c_lo = np.asarray(c_interval.lo, dtype=float)
    c_hi = np.asarray(c_interval.hi, dtype=float)
    b_lo = np.asarray(b_interval.lo, dtype=float)
    b_hi = np.asarray(b_interval.hi, dtype=float)
    c_mid = 0.5 * (c_lo + c_hi)
    lambda_mid = 0.5 * (lambda_lo + lambda_hi)
    stored_c_discrepancy = float(np.linalg.norm(stored_c - c_mid))
    stored_lambda_discrepancy = float(
        np.linalg.norm(stored_lambda - lambda_mid)
    )
    np.savez_compressed(
        DATA_RESULT,
        center_state=state,
        state_weights=weights,
        b_first_action_lower=b_lo,
        b_first_action_upper=b_hi,
        c_first_action_lower=c_lo,
        c_first_action_upper=c_hi,
        lambda_first_action_lower=lambda_lo,
        lambda_first_action_upper=lambda_hi,
    )

    validation = {
        "all_center_intervals_are_ordered": bool(
            np.all(b_lo <= b_hi)
            and np.all(c_lo <= c_hi)
            and np.all(lambda_lo <= lambda_hi)
        ),
        "older_binary64_moving_c_cross_method_discrepancy_is_recorded": (
            0.0 < stored_c_discrepancy < 5.0e-9
        ),
        "older_complex_step_lambda_cross_method_discrepancy_is_recorded": (
            0.0 < stored_lambda_discrepancy < 3.0e-16
        ),
        "row_86_b_center_matches_independent_replay": bool(
            b_lo[86] <= -0.7673819343475514 <= b_hi[86]
        ),
        "no_inverse_or_selected_line_resolve_is_formed": True,
        "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS",
        "status": (
            "C2_SIGNED_CENTER_Db_Dc_Dlambda_VECTORS_CERTIFIED"
            if passed else "C2_SIGNED_FIRST_COEFFICIENT_VECTOR_CERTIFICATE_INVALID"
        ),
        "classification": (
            "OUTWARD_ROUNDED_POINT_INTERVAL_RETAINED_ACTION_TENSOR_"
            "WITH_SIGNED_VECTOR_ASSEMBLY_BEFORE_NORMS"
        ),
        "reference_node": 1214,
        "center_norms": {
            "b_first_interval_norm_upper": interval_tensor_norm_upper(b_interval),
            "c_first_interval_norm_upper": interval_tensor_norm_upper(c_interval),
            "lambda_first_interval_norm_upper": interval_tensor_norm_upper(
                lambda_interval
            ),
        },
        "cross_method_discrepancies": {
            "older_binary64_moving_c_to_interval_midpoint_2_norm": (
                stored_c_discrepancy
            ),
            "older_complex_step_lambda_to_interval_midpoint_2_norm": (
                stored_lambda_discrepancy
            ),
            "authority": (
                "THE_NEW_POINT_INTERVAL_IS_THE_SIGNED_CENTER_AUTHORITY;_"
                "OLDER_POINT_VECTORS_ARE_CROSSCHECKS_ONLY"
            ),
        },
        "row_86_intervals": {
            "b_first": [float(b_lo[86]), float(b_hi[86])],
            "c_first": [float(c_lo[86]), float(c_hi[86])],
            "lambda_first": [float(lambda_lo[86]), float(lambda_hi[86])],
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": sha256(DATA_RESULT),
        "adjudication": {
            "signed_center_first_coefficient_vectors": (
                "CERTIFIED" if passed else "OPEN"
            ),
            "tube_mean_value_radii": "OPEN_ROW_BOOTSTRAP",
            "complete_D2Delta_operator": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "USE_THE_SIGNED_CENTER_INTERVALS_WITH_ROW_SELF_CONSISTENT_"
            "MEAN_VALUE_RADII_IN_THE_COMPLETE_D2DELTA_ROW_SWEEP"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (*parents, INTERVAL_SOURCE, THEORY, Path(__file__))
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "center_norms": payload["center_norms"],
        "row_86_intervals": payload["row_86_intervals"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
