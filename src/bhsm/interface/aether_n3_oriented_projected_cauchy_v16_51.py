"""Derivative-oriented projected Cauchy continuation from v16.49."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_projected_cauchy_continuation_v16_49 import CAUCHY_FACTORS, DERIVATIVE_EPSILON
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system

VERSION="v16.51"
CLASSIFICATION="BHSM_N3_DERIVATIVE_ORIENTED_PROJECTED_CAUCHY_CONTINUATION"
FULL_BHSM_COMPLETE=False
REDUCTION_MARGIN=1e-10


def v16_49_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_projected_cauchy_continuation_v16_49.json").read_text(encoding="utf-8"))
    values=payload["projected_cauchy_continuation"]["projected_cauchy_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v16.49 vector has wrong dimension")
    return raw


def oriented_projected_cauchy_bank(matrix:np.ndarray,residual:np.ndarray,raw:np.ndarray)->dict[str,Any]:
    scales=kkt_variable_scales();y=raw*scales
    gradient=matrix.T@residual;gradient[-1]=0.0
    base_direction=-gradient/np.linalg.norm(gradient)

    def directional_data(direction:np.ndarray)->tuple[np.ndarray,float,float,float,float]:
        plus_y,plus_r=projected_residual_and_vector(y+DERIVATIVE_EPSILON*direction)
        minus_y,minus_r=projected_residual_and_vector(y-DERIVATIVE_EPSILON*direction)
        jd=(plus_r-minus_r)/(2*DERIVATIVE_EPSILON)
        return jd,float(residual@jd),float(np.linalg.norm(jd)),float(np.linalg.norm(plus_y-y)),float(np.linalg.norm(minus_y-y))

    forward=directional_data(base_direction)
    reverse=directional_data(-base_direction)
    if forward[1] < reverse[1]:
        direction=base_direction;chosen=forward;orientation="assembled_negative_gradient"
    else:
        direction=-base_direction;chosen=reverse;orientation="reversed_by_measured_projected_derivative"
    jd,slope,jd_norm,plus_response,minus_response=chosen
    cauchy=max(0.0,-slope/jd_norm**2)
    initial=float(np.linalg.norm(residual));trials=[];accepted=[]
    for factor in CAUCHY_FACTORS:
        radius=factor*cauchy
        candidate,candidate_residual=projected_residual_and_vector(y+radius*direction)
        raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate)
        norm=float(np.linalg.norm(candidate_residual))
        row={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),
             "eta_minimum":eta,"residual_norm":norm,"residual_reduction":initial-norm,
             "event_residual":float(candidate_residual[-1]),
             "post_projection_step_norm":float(np.linalg.norm(candidate-y)),
             "quadratic_predicted_residual_norm":float(np.linalg.norm(residual+radius*jd))}
        trials.append(row)
        if radius>0 and eta>1e-5 and norm<initial-REDUCTION_MARGIN:accepted.append((norm,candidate,row))
    best=None
    if accepted:
        norm,vector,row=min(accepted,key=lambda item:item[0])
        best={**row,"residual_norm":norm,"raw_vector_hex":[float(v).hex() for v in vector/scales]}
    return {"method":"measured_derivative_oriented_Cauchy_step_on_event_multiplier_eliminated_manifold",
            "orientation":orientation,"forward_projected_slope":forward[1],"reverse_projected_slope":reverse[1],
            "chosen_projected_slope":slope,"projected_J_direction_norm":jd_norm,"derived_cauchy_radius":cauchy,
            "projection_response_plus_norm":plus_response,"projection_response_minus_norm":minus_response,
            "reduction_margin":REDUCTION_MARGIN,"initial_residual_norm":initial,"trial_count":len(trials),
            "residual_reducing_trial_count":len(accepted),"trials":trials,"best_accepted":best}


def oriented_projected_cauchy()->dict[str,Any]:
    matrix,residual,raw=refreshed_system_at(v16_49_raw_vector())
    return {"fresh_physical_audit":spectral_and_block_audit_from_system(matrix,residual,raw),
            "oriented_projected_cauchy_trial_bank":oriented_projected_cauchy_bank(matrix,residual,raw)}


def completion_payload()->dict[str,Any]:
    result=oriented_projected_cauchy();audit=result["fresh_physical_audit"]
    bank=result["oriented_projected_cauchy_trial_bank"];best=bank["best_accepted"]
    validation={"accepted_v16_49_residual_reproduced":math.isclose(audit["residual_norm"],6.412284998138246,rel_tol=0,abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric":audit["symmetric_relative_residual"]<1e-14,
        "chosen_direction_is_measured_descent":bank["chosen_projected_slope"]<0,
        "positive_cauchy_radius_derived":bank["derived_cauchy_radius"]>0,
        "at_least_one_strict_step_accepted":best is not None,
        "complete_residual_reduced_beyond_margin":bool(best is not None and best["residual_norm"]<audit["residual_norm"]-REDUCTION_MARGIN),
        "positive_step_accepted":bool(best is not None and best["trust_radius"]>0),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_oriented_projected_cauchy_v16_51","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"oriented_projected_cauchy_continuation":result,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"JOINT_PARENT_EVENT_STATIONARITY_ON_THE_MEASURED_DESCENT_ORIENTATION_OF_THE_PROJECTED_MANIFOLD",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"PROMOTE_ONLY_A_STRICT_POSITIVE_PROJECTED_DESCENT_AND_REFRESH_THE_SAME_SYSTEM",
        "validation":validation,"validation_passed":all(validation.values())}


def _canonical(value:Any)->Any:
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_oriented_projected_cauchy_v16_51.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path

__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","REDUCTION_MARGIN","v16_49_raw_vector","oriented_projected_cauchy_bank","oriented_projected_cauchy","completion_payload","deterministic_json","materialize"]
