"""Prospectively test secant-transported event curvature at v20.99."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_continuation_v20_92 import v20_92_selected_raw_vector
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_95 import v20_95_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_99 import v20_99_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v21.00"
CLASSIFICATION = "BHSM_N3_ACTION_OWNED_CURVATURE_SECANT_TRANSPORT_PROPOSAL"
FULL_BHSM_COMPLETE = False


def v21_00_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00.json"
    ).read_text(encoding="utf-8"))["curvature_transport_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.00 has no physically promoted state")
    return np.asarray([
        float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]
    ])


def _audit(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))[
        "curvature_singular_subspace_refresh"
    ]


def completion_payload() -> dict[str, Any]:
    audit_92 = _audit("artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json")
    audit_95 = _audit("artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_97.json")
    support_92 = np.asarray(audit_92["event_curvature_support_indices"], dtype=int)
    support_95 = np.asarray(audit_95["event_curvature_support_indices"], dtype=int)
    if not np.array_equal(support_92, support_95):
        raise ValueError("event-curvature support changed; secant transport is undefined")
    block_92 = np.asarray(audit_92["event_curvature_symmetric_block"], dtype=float)
    block_95 = np.asarray(audit_95["event_curvature_symmetric_block"], dtype=float)
    scales = kkt_variable_scales()
    previous_secant = (v20_95_selected_raw_vector() - v20_92_selected_raw_vector()) * scales
    current_secant = (v20_99_selected_raw_vector() - v20_95_selected_raw_vector()) * scales
    ratio = float(np.linalg.norm(current_secant) / np.linalg.norm(previous_secant))
    cosine = float(
        previous_secant @ current_secant
        / (np.linalg.norm(previous_secant) * np.linalg.norm(current_secant))
    )
    transported = block_95 + ratio * (block_95 - block_92)
    transported_audit = dict(audit_95)
    transported_audit["event_curvature_symmetric_block"] = transported.tolist()
    result = dual_metric_range_space_proposal(
        v20_99_selected_raw_vector(),
        source_label="v20.99",
        curvature_key="secant_transported_curvature",
        curvature_override=transported_audit,
    )
    best = result["exact_search"]["best"]
    transport = {
        "previous_refresh_interval": ["v20.92", "v20.95"],
        "prospective_interval": ["v20.95", "v20.99"],
        "metric": "EXISTING_BHSM_H6_SCALED_KKT_COORDINATES",
        "physical_secant_arc_ratio": ratio,
        "secant_cosine": cosine,
        "previous_block_relative_change": float(
            np.linalg.norm(block_95 - block_92) / np.linalg.norm(block_92)
        ),
        "formula": "B_transport=B_v20.95+arc_ratio*(B_v20.95-B_v20.92)",
        "future_curvature_used_to_construct": False,
        "used_only_to_propose": True,
    }
    validation = {
        "source_v20_99_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782780987846174
        ) < 5.0e-12,
        "same_support": bool(np.array_equal(support_92, support_95)),
        "forward_secant": cosine > 0.0,
        "no_future_curvature": not transport["future_curvature_used_to_construct"],
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "curvature_transport": transport,
        "curvature_transport_proposal": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v21_00_selected_raw_vector",
    "completion_payload", "materialize",
]
