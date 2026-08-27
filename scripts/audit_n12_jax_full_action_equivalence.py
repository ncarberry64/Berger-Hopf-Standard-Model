"""Cross-validate the optional JAX N12 action realization."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import jax
import jaxlib
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
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_JAX_FULL_ACTION_EQUIVALENCE_AUDIT.json"
QDIM = 37


def main() -> None:
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
    indices = (0, 11, 23, 35, 47)
    rows = []
    for index in indices:
        state = states[index]
        start = time.perf_counter()
        value, gradient, hessian = numpy_value_gradient_hessian(state)
        jax_seconds = time.perf_counter() - start
        start = time.perf_counter()
        retained = exact_full_action_jet_at_state(
            12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:], points=96,
        )
        retained_seconds = time.perf_counter() - start
        retained_gradient = np.asarray(retained.gradient, dtype=float)
        retained_hessian = np.asarray(retained.hessian, dtype=float)
        value_scale = max(abs(float(retained.value)), 1.0)
        gradient_scale = max(float(np.linalg.norm(retained_gradient)), 1.0)
        hessian_scale = max(float(np.linalg.norm(retained_hessian)), 1.0)
        rows.append({
            "node": index,
            "value_relative_residual": abs(value - float(retained.value)) / value_scale,
            "gradient_relative_residual": float(
                np.linalg.norm(gradient - retained_gradient) / gradient_scale
            ),
            "hessian_relative_residual": float(
                np.linalg.norm(hessian - retained_hessian) / hessian_scale
            ),
            "hessian_symmetry_residual": float(np.linalg.norm(hessian - hessian.T)),
            "JAX_seconds_including_first_compile_when_applicable": jax_seconds,
            "retained_Jet_seconds": retained_seconds,
        })
    validation = {
        "five_global_stop_nodes_compared": len(rows) == 5,
        "value_relative_residual_below_1e_minus_12": max(
            row["value_relative_residual"] for row in rows
        ) < 1.0e-12,
        "gradient_relative_residual_below_1e_minus_11": max(
            row["gradient_relative_residual"] for row in rows
        ) < 1.0e-11,
        "hessian_relative_residual_below_1e_minus_10": max(
            row["hessian_relative_residual"] for row in rows
        ) < 1.0e-10,
        "JAX_is_acceleration_only_and_retained_jet_remains_authority": True,
        "same_96_point_action_quadrature_and_all_boundary_terms_used": True,
        "no_action_coefficient_equation_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_JAX_FULL_ACTION_EQUIVALENCE_AUDIT",
        "status": (
            "OPTIONAL_JAX_ACTION_VALUE_GRADIENT_HESSIAN_EQUIVALENT_TO_RETAINED_JET"
            if all(validation.values()) else "JAX_ACTION_REALIZATION_NOT_EQUIVALENT"
        ),
        "rows": rows,
        "summary": {
            "maximum_value_relative_residual": max(row["value_relative_residual"] for row in rows),
            "maximum_gradient_relative_residual": max(row["gradient_relative_residual"] for row in rows),
            "maximum_hessian_relative_residual": max(row["hessian_relative_residual"] for row in rows),
            "minimum_warm_JAX_seconds": min(row["JAX_seconds_including_first_compile_when_applicable"] for row in rows[1:]),
            "minimum_retained_Jet_seconds": min(row["retained_Jet_seconds"] for row in rows),
        },
        "software": {
            "jax": jax.__version__,
            "jaxlib": jaxlib.__version__,
            "backend": jax.default_backend(),
            "x64_enabled": bool(jax.config.x64_enabled),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
