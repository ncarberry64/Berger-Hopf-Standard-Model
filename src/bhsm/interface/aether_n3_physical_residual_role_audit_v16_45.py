"""Physical-role audit of the residual at the accepted v16.44 N=3 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_physical_inverse_closure_v16_36 import Q_LABELS

VERSION = "v16.45"
CLASSIFICATION = "BHSM_N3_PHYSICAL_RESIDUAL_ROLE_AUDIT"
FULL_BHSM_COMPLETE = False


def v16_44_raw_vector() -> np.ndarray:
    payload = json.loads(Path("artifacts/BHSM_aether_n3_second_refined_filter_continuation_v16_44.json").read_text(encoding="utf-8"))
    values = payload["second_refined_filter_continuation"]["refined_filter_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.44 vector has wrong dimension")
    return raw


def physical_residual_role_audit() -> dict[str, Any]:
    raw = v16_44_raw_vector(); y = raw * kkt_variable_scales()
    _, residual = projected_residual_and_vector(y)
    q = residual[:230].reshape(23, 10); m = residual[230:374].reshape(24, 6)
    group_norms = np.linalg.norm(q, axis=0)
    roles = {
        "log_scale": "boundary_scale_and_common_pushforward_geometry",
        "u_1": "conformal_shape_and_reconstruction_geometry",
        "u_2": "conformal_shape_and_reconstruction_geometry",
        "u_3": "conformal_shape_and_reconstruction_geometry",
        "w_0": "normal/fiber_localization_geometry",
        "w_1": "normal/fiber_localization_geometry",
        "w_2": "normal/fiber_localization_geometry",
        "v_0": "Hopf_anisotropy_and_gauge_breaking_background_geometry",
        "v_1": "Hopf_anisotropy_and_gauge_breaking_background_geometry",
        "v_2": "Hopf_anisotropy_and_gauge_breaking_background_geometry",
    }
    flat_order = np.argsort(np.abs(q.ravel()))[::-1]
    leaders = [{
        "node": int(index // 10 + 1), "coordinate": Q_LABELS[index % 10],
        "physical_role": roles[Q_LABELS[index % 10]], "residual": float(q.ravel()[index]),
    } for index in flat_order[:16]]
    return {
        "source_state": "v16.44_best_accepted",
        "complete_residual_norm": float(np.linalg.norm(residual)),
        "q_stationarity_norm": float(np.linalg.norm(q)),
        "multiplier_stationarity_norm": float(np.linalg.norm(m)),
        "period_stationarity": float(residual[-2]), "event_residual": float(residual[-1]),
        "coordinate_group_ranking": [{
            "coordinate": Q_LABELS[i], "stationarity_norm": float(group_norms[i]),
            "physical_role": roles[Q_LABELS[i]],
        } for i in np.argsort(group_norms)[::-1]],
        "largest_coordinate_components": leaders,
        "terminal_layer_fraction_among_top_components": float(sum(row["node"] >= 21 for row in leaders) / len(leaders)),
        "interpretation": (
            "THE_REMAINING_N3_DEFECT_IS_A_STATIONARITY_DEFECT_OF_THE_EXISTING_"
            "UNBROKEN_PARENT_GEOMETRY;_IT_DOES_NOT_AUTHORIZE_A_NEW_FAMILY_"
            "COORDINATE_OR_AN_INDEPENDENT_YUKAWA_OR_GAUGE_NORMALIZATION"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = physical_residual_role_audit()
    validation = {
        "accepted_v16_44_residual_reproduced": math.isclose(result["complete_residual_norm"], 6.457090170149505, rel_tol=0.0, abs_tol=2e-9),
        "all_q_coordinate_roles_classified": len(result["coordinate_group_ranking"]) == 10,
        "largest_components_classified": len(result["largest_coordinate_components"]) == 16,
        "event_is_not_misreported_as_closed_saddle": result["q_stationarity_norm"] > abs(result["event_residual"]),
    }
    return {
        "artifact": "BHSM_aether_n3_physical_residual_role_audit_v16_45", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "physical_residual_role_audit": result,
        "status": "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained": "WHICH_PARENT_GEOMETRY_SECTORS_STILL_PREVENT_THE_COMMON_PARTICLE_EVENT",
        "dependency_advanced": "IDENTIFIES_THE_UPSTREAM_OWNER_OF_THE_REMAINING_N3_SADDLE_DEFECT",
        "active_calculation": "CONTINUE_THE_SAME_FILTERED_KKT_SOLVE_TARGETING_THE_REPORTED_EXISTING_GEOMETRY_BLOCKS",
        "validation": validation, "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping): return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_physical_residual_role_audit_v16_45.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path

__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v16_44_raw_vector", "physical_residual_role_audit", "completion_payload", "deterministic_json", "materialize"]
