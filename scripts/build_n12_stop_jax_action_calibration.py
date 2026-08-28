"""Build retained-minus-JAX action-jet corrections along a stop center.

The default remains the 48-node macro mesh.  ``BHSM_N12_CALIBRATION_GRID=fine``
selects the stored DOP853 grid through the stop; an integer
``BHSM_N12_CALIBRATION_STRIDE`` may thin that grid while always retaining the
last stop node.  This is predictor calibration, never interval authority.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_jax_full_local_action import (  # noqa: E402
    numpy_value_gradient_hessian,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_CALIBRATION_RESULT",
    str(BASE / "BHSM_N12_STOP_JAX_ACTION_CALIBRATION.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")
QDIM = 37


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _retained(task: tuple[int, np.ndarray]) -> tuple[int, float, np.ndarray, np.ndarray]:
    index, state = task
    jet = exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
    )
    return (
        index,
        float(jet.value),
        np.asarray(jet.gradient, dtype=float),
        np.asarray(jet.hessian, dtype=float),
    )


def main() -> None:
    with np.load(CENTER) as source:
        if os.environ.get("BHSM_N12_CALIBRATION_GRID", "macro") == "fine":
            weights = np.asarray(source["state_weights"], dtype=float)
            times_all = np.asarray(source["fine_grid_action_lengths"], dtype=float)
            augmented_all = np.asarray(
                source["fine_grid_augmented_action_values"], dtype=float,
            )
            bracket = int(source["stop_bracket_fine_grid_index"][0])
            stop_time = float(source["action_lengths"][-1])
            stop_state = np.asarray(source["centers"][-1], dtype=float)
            times_all = np.concatenate((times_all[:bracket + 1], [stop_time]))
            states_all = np.vstack((
                augmented_all[:bracket + 1, :-1] / weights,
                stop_state,
            ))
            stride = max(int(os.environ.get("BHSM_N12_CALIBRATION_STRIDE", "1")), 1)
            indices = list(range(0, times_all.size, stride))
            if indices[-1] != times_all.size - 1:
                indices.append(times_all.size - 1)
            action_lengths = times_all[indices]
            states = states_all[indices]
            grid_kind = "FINE_DOP853_GRID"
        else:
            states = np.asarray(source["centers"], dtype=float)
            action_lengths = np.asarray(source["action_lengths"], dtype=float)
            grid_kind = "RETAINED_MACRO_SEAMS"
    workers = min(12, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        retained = list(executor.map(
            _retained, list(enumerate(states)), chunksize=1,
        ))
    retained.sort(key=lambda item: item[0])
    value_correction = []
    gradient_correction = []
    hessian_correction = []
    rows = []
    for index, value, gradient, hessian in retained:
        jax_value, jax_gradient, jax_hessian = numpy_value_gradient_hessian(
            states[index]
        )
        jax_hessian = 0.5 * (jax_hessian + jax_hessian.T)
        dc0 = value - jax_value
        dc1 = gradient - jax_gradient
        dc2 = hessian - jax_hessian
        value_correction.append(dc0)
        gradient_correction.append(dc1)
        hessian_correction.append(dc2)
        rows.append({
            "node": index,
            "action_length": float(action_lengths[index]),
            "value_correction_absolute": abs(dc0),
            "gradient_correction_2_norm": float(np.linalg.norm(dc1)),
            "hessian_correction_operator_2_norm": float(np.linalg.norm(dc2, 2)),
            "hessian_correction_Frobenius_norm": float(np.linalg.norm(dc2)),
        })
    np.savez_compressed(
        DATA_RESULT,
        action_lengths=action_lengths,
        value_correction=np.asarray(value_correction),
        gradient_correction=np.asarray(gradient_correction),
        hessian_correction=np.asarray(hessian_correction),
    )
    validation = {
        "all_requested_calibration_nodes_evaluated": len(rows) == len(states),
        "all_corrections_finite": all(
            np.isfinite(value)
            for row in rows for value in row.values()
            if isinstance(value, float)
        ),
        "calibration_is_predictor_only": True,
        "retained_action_jet_remains_certificate_authority": True,
        "no_action_coefficient_equation_stop_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_STOP_JAX_ACTION_CALIBRATION",
        "status": "RETAINED_MINUS_JAX_ACTION_JET_MACRO_CALIBRATION_ASSEMBLED",
        "center": CENTER.relative_to(ROOT).as_posix(),
        "grid": {
            "kind": grid_kind,
            "nodes": len(rows),
            "maximum_step": float(np.max(np.diff(action_lengths))),
        },
        "summary": {
            "maximum_value_correction_absolute": max(row["value_correction_absolute"] for row in rows),
            "maximum_gradient_correction_2_norm": max(row["gradient_correction_2_norm"] for row in rows),
            "maximum_hessian_correction_operator_2_norm": max(row["hessian_correction_operator_2_norm"] for row in rows),
            "maximum_hessian_correction_Frobenius_norm": max(row["hessian_correction_Frobenius_norm"] for row in rows),
        },
        "rows": rows,
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "validation": validation,
        "structural_validation_passed": all(validation.values()),
        "validation_passed": False,
        "inputs": {
            CENTER.relative_to(ROOT).as_posix(): _sha256(CENTER),
            "src/bhsm/interface/aether_jax_full_local_action.py": _sha256(
                ROOT / "src/bhsm/interface/aether_jax_full_local_action.py"
            ),
            "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py": _sha256(
                ROOT / "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py"
            ),
        },
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
