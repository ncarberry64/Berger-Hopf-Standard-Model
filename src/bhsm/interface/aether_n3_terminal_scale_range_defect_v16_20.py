"""Localize the v16.19 endpoint-scale KKT defect and project rho exactly."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    event_covector,
    replacement_action_covector,
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    _minimum_node_eta,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.20"
CLASSIFICATION = "BHSM_N3_ENDPOINT_SCALE_PERIOD_KKT_RANGE_DEFECT"
FULL_BHSM_COMPLETE = False


def v16_19_final_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_kkt_projected_refresh_v16_19.json"
    ).read_text(encoding="utf-8"))
    values = payload["projected_state_refresh"]["final_raw_vector_hex"]
    return np.asarray([float.fromhex(value) for value in values])


def range_defect_and_projection() -> dict[str, Any]:
    raw = v16_19_final_raw_vector()
    scales = kkt_variable_scales()
    base = raw[:-1]
    before = scaled_analytic_kkt_residual(raw * scales)
    action = np.asarray(
        replacement_action_covector(base)["covector"]
    ) / scales[:-1]
    event = event_covector(base) / scales[:-1] / scales[-1]
    y_rho = -float(action @ event) / float(event @ event)
    projected = raw.copy()
    projected[-1] = y_rho / scales[-1]
    after = scaled_analytic_kkt_residual(projected * scales)
    q_count = 230
    m_count = 144
    largest_q_index = int(np.argmax(np.abs(after[:q_count])))
    ordered = np.argsort(np.abs(after[:q_count]))[-12:][::-1]
    endpoint_scale_indices = {0, 10, 200, 210, 220}
    return {
        "rho_before": float(raw[-1]),
        "rho_projected": float(projected[-1]),
        "residual_norm_before": float(np.linalg.norm(before)),
        "residual_norm_after_projection": float(np.linalg.norm(after)),
        "q_stationarity_norm_after": float(np.linalg.norm(after[:q_count])),
        "multiplier_stationarity_norm_after": float(np.linalg.norm(
            after[q_count:q_count + m_count]
        )),
        "period_stationarity_after": float(after[-2]),
        "event_residual_after": float(after[-1]),
        "largest_q_residual_index": largest_q_index,
        "largest_q_residual_component": float(after[largest_q_index]),
        "largest_q_residual_is_endpoint_scale": (
            largest_q_index in endpoint_scale_indices
        ),
        "largest_coordinate_components": [
            {
                "reduced_index": int(index),
                "node": int(index // 10 + 1),
                "coordinate": int(index % 10),
                "value": float(after[index]),
            }
            for index in ordered
        ],
        "eta_minimum": _minimum_node_eta(projected),
        "projected_raw_vector_hex": [
            float(value).hex() for value in projected
        ],
    }


def completion_payload() -> dict[str, Any]:
    result = range_defect_and_projection()
    validation = {
        "exact_rho_projection_reduces_residual": (
            result["residual_norm_after_projection"]
            < result["residual_norm_before"]
        ),
        "multiplier_block_nearly_closed": (
            result["multiplier_stationarity_norm_after"] < 2.0e-2
        ),
        "defect_localized_to_endpoint_scale": (
            result["largest_q_residual_is_endpoint_scale"]
        ),
        "eta_domain_preserved": result["eta_minimum"] > 1.0e-5,
    }
    return {
        "artifact": "BHSM_aether_n3_terminal_scale_range_defect_v16_20",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "range_defect": result,
        "dependency_advanced": (
            "THE_REMAINING_REFRESHED_KKT_DEFECT_IS_LOCALIZED_TO_THE_"
            "ANCHORED_ENDPOINT-SCALE_AND_PERIOD_BLOCK_AFTER_EXACT_RHO_PROJECTION"
        ),
        "active_calculation": (
            "RESOLVE_THE_ENDPOINT-SCALE/PERIOD_RANGE_DEFECT_IN_THE_SAME_"
            "ANCHORED_COMMON-PUSHFORWARD_KKT_SYSTEM"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_terminal_scale_range_defect_v16_20.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_19_final_raw_vector", "range_defect_and_projection",
    "completion_payload", "deterministic_json", "materialize",
]
