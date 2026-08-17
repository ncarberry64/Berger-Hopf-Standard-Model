"""Exact explicit-event-multiplier continuation from the promoted v20.81 geometry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_project_event_multiplier, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import v20_81_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v20.82"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_EXPLICIT_MULTIPLIER_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v20_82_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_82.json"
    ).read_text(encoding="utf-8"))["rayleigh_multiplier_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.82 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["candidate"]["raw_vector_hex"]])


def rayleigh_multiplier_continuation(
    source_raw_override: np.ndarray | None = None, *, source_label: str = "v20.81",
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    source = v20_81_selected_raw_vector() if source_raw_override is None else np.asarray(source_raw_override, dtype=float)
    candidate = rayleigh_project_event_multiplier(source)
    source_norm = float(np.linalg.norm(rayleigh_square_physical_residual(source * scales)))
    candidate_norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate * scales)))
    eta = float(_minimum_node_eta(candidate)); child = _fresh_child_gate(candidate)
    promoted = bool(candidate_norm < source_norm and eta > 1.0e-5 and child["all_pass"])
    return {
        "source": {"version": source_label, "exact_rayleigh_f376_l2": source_norm,
                   "raw_event_multiplier": float(source[-1])},
        "candidate": {"exact_rayleigh_f376_l2": candidate_norm,
                      "exact_reduction": source_norm - candidate_norm,
                      "eta_minimum": eta, "raw_event_multiplier": float(candidate[-1]),
                      "raw_vector_hex": [float(value).hex() for value in candidate]},
        "proposal_method": "EXACT_LEAST_SQUARES_UPDATE_OF_THE_EXPLICIT_EVENT_MULTIPLIER_ONLY",
        "event_multiplier_remains_explicit_376TH_UNKNOWN": True,
        "promotion": {"promoted": promoted, "child": child},
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "componentwise_monotonicity_added": False,
        "next_action": "CONTINUE_CORRECTED_SQUARE_KKT_FROM_V20_82" if promoted else "AUDIT_MULTIPLIER_PROJECTION_FAILURE",
    }


def completion_payload() -> dict[str, Any]:
    result = rayleigh_multiplier_continuation()
    validation = {
        "source_v20_81_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.794237505175150) < 5.0e-12,
        "exact_merit_reduced": result["candidate"]["exact_reduction"] > 0.0,
        "explicit_multiplier_preserved": result["event_multiplier_remains_explicit_376TH_UNKNOWN"],
        "fresh_child_passes": result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values()) and result["promotion"]["promoted"]
    return {
        "artifact": "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_82", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_multiplier_continuation": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_82.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_82_selected_raw_vector", "rayleigh_multiplier_continuation", "completion_payload", "materialize"]
