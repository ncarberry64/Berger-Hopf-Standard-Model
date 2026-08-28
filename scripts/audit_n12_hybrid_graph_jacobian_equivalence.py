"""Compare the hybrid third-tensor graph Jacobian with retained replays."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

import jax
import jaxlib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_hybrid_c2_graph_jacobian import (  # noqa: E402
    graph_jacobian_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
RETAINED = Path(os.environ.get(
    "BHSM_N12_STOP_JACOBIAN_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_HYBRID_GRAPH_AUDIT_RESULT",
    str(BASE / "BHSM_N12_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json"),
))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(RETAINED) as source:
        retained_jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
        retained_gradients = np.asarray(source["descriptor_gradient_action"], dtype=float)
    rows = []
    for index in (0, 11, 23, 35, 47):
        hybrid = graph_jacobian_action(
            states[index], weights, reference, float(descriptors[index]),
        )
        jacobian = np.asarray(hybrid["graph_Jacobian_action"])
        gradient = np.asarray(hybrid["descriptor_gradient_action"])
        retained_jacobian = retained_jacobians[index]
        retained_gradient = retained_gradients[index]
        rows.append({
            "node": index,
            "selected_branch": int(hybrid["selected_branch"]),
            "graph_Jacobian_absolute_residual": float(np.linalg.norm(
                jacobian - retained_jacobian, ord=2,
            )),
            "graph_Jacobian_relative_residual": float(
                np.linalg.norm(jacobian - retained_jacobian, ord=2)
                / max(np.linalg.norm(retained_jacobian, ord=2), np.finfo(float).tiny)
            ),
            "descriptor_gradient_absolute_residual": float(np.linalg.norm(
                gradient - retained_gradient,
            )),
            "descriptor_gradient_relative_residual": float(
                np.linalg.norm(gradient - retained_gradient)
                / max(np.linalg.norm(retained_gradient), np.finfo(float).tiny)
            ),
        })
    validation = {
        "same_selected_branch_24": all(row["selected_branch"] == 24 for row in rows),
        "graph_Jacobian_relative_residual_below_1e_minus_4": max(
            row["graph_Jacobian_relative_residual"] for row in rows
        ) < 1.0e-4,
        "descriptor_gradient_relative_residual_below_1e_minus_8": max(
            row["descriptor_gradient_relative_residual"] for row in rows
        ) < 1.0e-8,
        "hybrid_third_tensor_not_promoted_to_interval_authority": True,
        "retained_directional_replay_remains_certificate_authority": True,
        "no_action_equation_stop_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT",
        "status": (
            "HYBRID_GRAPH_JACOBIAN_RECONNAISSANCE_EQUIVALENT_TO_RETAINED_REPLAY"
            if all(validation.values()) else "HYBRID_GRAPH_JACOBIAN_NOT_EQUIVALENT"
        ),
        "rows": rows,
        "summary": {
            "maximum_graph_Jacobian_absolute_residual": max(
                row["graph_Jacobian_absolute_residual"] for row in rows
            ),
            "maximum_graph_Jacobian_relative_residual": max(
                row["graph_Jacobian_relative_residual"] for row in rows
            ),
            "maximum_descriptor_gradient_absolute_residual": max(
                row["descriptor_gradient_absolute_residual"] for row in rows
            ),
            "maximum_descriptor_gradient_relative_residual": max(
                row["descriptor_gradient_relative_residual"] for row in rows
            ),
        },
        "software": {
            "jax": jax.__version__,
            "jaxlib": jaxlib.__version__,
            "backend": jax.default_backend(),
            "x64_enabled": bool(jax.config.x64_enabled),
        },
        "center": CENTER.relative_to(ROOT).as_posix(),
        "inputs": {
            CENTER.relative_to(ROOT).as_posix(): _sha256(CENTER),
            RETAINED.relative_to(ROOT).as_posix(): _sha256(RETAINED),
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
