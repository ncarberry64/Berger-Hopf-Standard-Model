"""Projected-manifold Cauchy continuation from v16.47."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system

VERSION = "v16.49"
CLASSIFICATION = "BHSM_N3_EVENT_MULTIPLIER_ELIMINATED_CAUCHY_CONTINUATION"
FULL_BHSM_COMPLETE = False
CAUCHY_FACTORS = (0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
DERIVATIVE_EPSILON = 1e-8


def v16_47_raw_vector() -> np.ndarray:
    payload = json.loads(Path("artifacts/BHSM_aether_n3_strong_damping_continuation_v16_47.json").read_text(encoding="utf-8"))
    values = payload["strong_damping_continuation"]["strong_damping_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.47 vector has wrong dimension")
    return raw


def projected_cauchy_trial_bank(matrix: np.ndarray, residual: np.ndarray, raw: np.ndarray) -> dict[str, Any]:
    scales = kkt_variable_scales(); y = raw * scales
    gradient = matrix.T @ residual
    # rho is already the exact least-squares projection; its merit derivative
    # vanishes. Move only on the 375-dimensional base manifold.
    gradient[-1] = 0.0
    gradient_norm = float(np.linalg.norm(gradient))
    direction = -gradient / gradient_norm
    plus_y, plus_r = projected_residual_and_vector(y + DERIVATIVE_EPSILON * direction)
    minus_y, minus_r = projected_residual_and_vector(y - DERIVATIVE_EPSILON * direction)
    projected_j_direction = (plus_r - minus_r) / (2.0 * DERIVATIVE_EPSILON)
    projected_j_direction_norm = float(np.linalg.norm(projected_j_direction))
    directional_slope = float(residual @ projected_j_direction)
    cauchy_radius = max(0.0, -directional_slope / projected_j_direction_norm**2)
    initial_norm = float(np.linalg.norm(residual))
    trials=[]; accepted=[]
    for factor in CAUCHY_FACTORS:
        radius = factor * cauchy_radius
        candidate, candidate_residual = projected_residual_and_vector(y + radius * direction)
        raw_candidate = candidate / scales
        eta = _minimum_node_eta(raw_candidate)
        norm = float(np.linalg.norm(candidate_residual))
        row = {
            "cauchy_factor": factor, "trust_radius": radius,
            "domain_valid": bool(eta > 1e-5), "eta_minimum": eta,
            "residual_norm": norm, "residual_reduction": initial_norm - norm,
            "event_residual": float(candidate_residual[-1]),
            "post_projection_step_norm": float(np.linalg.norm(candidate-y)),
            "quadratic_predicted_residual_norm": float(np.linalg.norm(residual + radius * projected_j_direction)),
        }
        trials.append(row)
        if eta > 1e-5 and norm < initial_norm: accepted.append((norm,candidate,row))
    best=None
    if accepted:
        norm,vector,row=min(accepted,key=lambda item:item[0])
        best={**row,"residual_norm":norm,"raw_vector_hex":[float(v).hex() for v in vector/scales]}
    return {
        "method":"Cauchy_step_on_exact_event_multiplier_eliminated_merit_manifold",
        "derivative_epsilon":DERIVATIVE_EPSILON,
        "merit_gradient_norm":gradient_norm,
        "projected_directional_slope":directional_slope,
        "projected_J_direction_norm":projected_j_direction_norm,
        "derived_cauchy_radius":cauchy_radius,
        "projection_response_plus_norm":float(np.linalg.norm(plus_y-y)),
        "projection_response_minus_norm":float(np.linalg.norm(minus_y-y)),
        "initial_residual_norm":initial_norm,"trial_count":len(trials),
        "residual_reducing_trial_count":len(accepted),"trials":trials,"best_accepted":best,
    }


def projected_cauchy_continuation() -> dict[str, Any]:
    matrix,residual,raw=refreshed_system_at(v16_47_raw_vector())
    return {"fresh_physical_audit":spectral_and_block_audit_from_system(matrix,residual,raw),
            "projected_cauchy_trial_bank":projected_cauchy_trial_bank(matrix,residual,raw)}


def completion_payload() -> dict[str, Any]:
    result=projected_cauchy_continuation(); audit=result["fresh_physical_audit"]
    bank=result["projected_cauchy_trial_bank"]; best=bank["best_accepted"]
    validation={
        "accepted_v16_47_residual_reproduced":math.isclose(audit["residual_norm"],6.442521870987222,rel_tol=0.0,abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric":audit["symmetric_relative_residual"]<1e-14,
        "projected_direction_is_descent":bank["projected_directional_slope"]<0.0,
        "positive_cauchy_radius_derived":bank["derived_cauchy_radius"]>0.0,
        "cauchy_factor_grid_probed":bank["trial_count"]==len(CAUCHY_FACTORS),
        "at_least_one_joint_step_accepted":best is not None,
        "complete_residual_reduced":bool(best is not None and best["residual_norm"]<audit["residual_norm"]),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376),
    }
    return {"artifact":"BHSM_aether_n3_projected_cauchy_continuation_v16_49","version":VERSION,
            "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":FULL_BHSM_COMPLETE,
            "projected_cauchy_continuation":result,
            "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
            "real_physical_property_explained":"JOINT_PARENT_EVENT_STATIONARITY_AFTER_EXACT_ELIMINATION_OF_THE_EVENT_MULTIPLIER",
            "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
            "active_calculation":"PROMOTE_THE_PROJECTED_CAUCHY_STATE_IF_VALIDATED_OR_RETURN_TO_THE_STRONGLY_DAMPED_FILTER",
            "validation":validation,"validation_passed":all(validation.values())}


def _canonical(value: Any) -> Any:
    if isinstance(value,np.ndarray):return [_canonical(v) for v in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {k:_canonical(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(v) for v in value]
    return value


def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True)
    path=target/"BHSM_aether_n3_projected_cauchy_continuation_v16_49.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path

__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","CAUCHY_FACTORS","DERIVATIVE_EPSILON","v16_47_raw_vector","projected_cauchy_trial_bank","projected_cauchy_continuation","completion_payload","deterministic_json","materialize"]
