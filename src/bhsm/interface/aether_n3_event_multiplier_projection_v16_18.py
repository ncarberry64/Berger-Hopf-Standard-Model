"""Exact one-dimensional event-multiplier projection at the v16.17 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    event_covector,
    event_value_from_base,
    replacement_action_covector,
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    _minimum_node_eta,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.18"
CLASSIFICATION = "BHSM_N3_EXACT_EVENT_MULTIPLIER_PROJECTION"
FULL_BHSM_COMPLETE = False


def v16_17_final_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_kkt_second_refresh_v16_17.json"
    ).read_text(encoding="utf-8"))
    values = payload["second_refreshed_continuation"]["final_raw_vector_hex"]
    return np.asarray([float.fromhex(value) for value in values])


def projected_event_multiplier_state() -> dict[str, Any]:
    raw = v16_17_final_raw_vector()
    scales = kkt_variable_scales()
    base = raw[:-1]
    action_gradient = np.asarray(
        replacement_action_covector(base)["covector"]
    ) / scales[:-1]
    event_gradient = event_covector(base) / scales[:-1] / scales[-1]
    y_rho = -float(action_gradient @ event_gradient) / float(
        event_gradient @ event_gradient
    )
    projected = raw.copy()
    projected[-1] = y_rho / scales[-1]
    before = scaled_analytic_kkt_residual(raw * scales)
    after = scaled_analytic_kkt_residual(projected * scales)
    q_count = 23 * 10
    m_count = 24 * 6
    return {
        "rho_before": float(raw[-1]),
        "rho_after": float(projected[-1]),
        "residual_norm_before": float(np.linalg.norm(before)),
        "residual_norm_after": float(np.linalg.norm(after)),
        "q_stationarity_norm_after": float(np.linalg.norm(after[:q_count])),
        "multiplier_stationarity_norm_after": float(np.linalg.norm(
            after[q_count:q_count + m_count]
        )),
        "period_stationarity_after": float(after[-2]),
        "event_residual_unchanged": float(after[-1]),
        "eta_minimum_unchanged": _minimum_node_eta(projected),
        "projected_raw_vector_hex": [
            float(value).hex() for value in projected
        ],
    }


def completion_payload() -> dict[str, Any]:
    result = projected_event_multiplier_state()
    validation = {
        "event_equation_unchanged": math.isclose(
            result["event_residual_unchanged"], -0.2666222223498367,
            rel_tol=0.0, abs_tol=1.0e-9,
        ),
        "complete_residual_reduced": (
            result["residual_norm_after"] < result["residual_norm_before"]
        ),
        "eta_domain_preserved": result["eta_minimum_unchanged"] > 1.0e-5,
        "full_precision_state_preserved": len(
            result["projected_raw_vector_hex"]
        ) == 376,
    }
    return {
        "artifact": "BHSM_aether_n3_event_multiplier_projection_v16_18",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_multiplier_projection": result,
        "dependency_advanced": (
            "THE_ONE-DIMENSIONAL_EVENT-MULTIPLIER_BLOCK_IS_EXACTLY_"
            "PROJECTED_BEFORE_THE_NEXT_PHYSICAL_JACOBIAN_REFRESH"
        ),
        "active_calculation": (
            "REFRESH_THE_COMMON_EVENT-KKT_JACOBIAN_AT_THE_PROJECTED_STATE"
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
    path = target / "BHSM_aether_n3_event_multiplier_projection_v16_18.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_17_final_raw_vector", "projected_event_multiplier_state",
    "completion_payload", "deterministic_json", "materialize",
]
