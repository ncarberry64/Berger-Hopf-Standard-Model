"""First exact physical descent of the fresh SBP N=3 event KKT."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector,sbp_projected_residual_and_vector,sbp_replacement_action_covector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices,kkt_variable_scales

VERSION="v16.59"
CLASSIFICATION="BHSM_N3_FRESH_SBP_FIRST_COVECTOR_CONSISTENT_PHYSICAL_DESCENT"
FULL_BHSM_COMPLETE=False
ACTION_HESSIAN_RELATIVE_STEP=1e-4
EVENT_CURVATURE_RELATIVE_STEP=1e-5
DIRECTIONAL_EPSILON=3e-6
CAUCHY_FACTORS=(0.125,0.25,0.5,1.0,2.0,4.0)
REDUCTION_MARGIN=1e-10

def v16_58_projected_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_kkt_v16_58.json").read_text(encoding="utf-8"))
    values=payload["fresh_sbp_kkt"]["projected_raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.58 vector has wrong dimension")
    return raw

def sbp_physical_jacobian(raw:np.ndarray)->dict[str,Any]:
    scales=kkt_variable_scales();y=raw*scales;ybase=y[:-1];dimension=375
    def action_gradient(value:np.ndarray)->np.ndarray:
        return np.asarray(sbp_replacement_action_covector(value/scales[:-1])["covector"])/scales[:-1]
    action_hessian=np.empty((dimension,dimension))
    for column in range(dimension):
        step=ACTION_HESSIAN_RELATIVE_STEP*max(1.0,abs(float(ybase[column])));delta=np.zeros(dimension);delta[column]=step
        action_hessian[:,column]=(action_gradient(ybase+delta)-action_gradient(ybase-delta))/(2*step)
    action_asym=float(np.linalg.norm(action_hessian-action_hessian.T)/max(1.0,np.linalg.norm(action_hessian)))
    action_hessian=0.5*(action_hessian+action_hessian.T)
    event_gradient=sbp_event_covector(raw[:-1])/scales[:-1]/scales[-1]
    event_hessian=np.zeros((dimension,dimension));support=event_gradient_indices()
    def event_gradient_at(value:np.ndarray)->np.ndarray:
        return sbp_event_covector(value/scales[:-1])/scales[:-1]/scales[-1]
    for index in support:
        step=EVENT_CURVATURE_RELATIVE_STEP*max(1.0,abs(float(ybase[index])));delta=np.zeros(dimension);delta[index]=step
        event_hessian[:,index]=(event_gradient_at(ybase+delta)-event_gradient_at(ybase-delta))/(2*step)
    event_asym=float(np.linalg.norm(event_hessian-event_hessian.T)/max(1.0,np.linalg.norm(event_hessian)))
    matrix=np.zeros((376,376));matrix[:-1,:-1]=action_hessian+y[-1]*event_hessian
    matrix[:-1,-1]=event_gradient;matrix[-1,:-1]=event_gradient
    return {"matrix":matrix,"action_hessian_norm":float(np.linalg.norm(action_hessian)),
        "action_hessian_raw_asymmetry":action_asym,"event_hessian_norm":float(np.linalg.norm(event_hessian)),
        "event_hessian_raw_asymmetry":event_asym,"event_curvature_contribution_norm":float(abs(y[-1])*np.linalg.norm(event_hessian))}

def sbp_descent_from(
    raw_vector:np.ndarray, *, retain_trial_vectors:bool=False,
    joint_filter:bool=False,
)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y)
    assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"));gradient=matrix.T@residual;gradient[-1]=0
    direction=-gradient/np.linalg.norm(gradient)
    plus_y,plus_r=sbp_projected_residual_and_vector(y+DIRECTIONAL_EPSILON*direction)
    minus_y,minus_r=sbp_projected_residual_and_vector(y-DIRECTIONAL_EPSILON*direction)
    jd=(plus_r-minus_r)/(2*DIRECTIONAL_EPSILON);slope=float(residual@jd);orientation="physical_negative_merit_gradient"
    if slope>=0:direction=-direction;jd=-jd;slope=-slope;orientation="reversed_by_measured_projected_derivative"
    jd_norm=float(np.linalg.norm(jd));cauchy=-slope/jd_norm**2;initial=float(np.linalg.norm(residual));initial_event=float(residual[-1]);trials=[];accepted=[];joint_accepted=[]
    for factor in CAUCHY_FACTORS:
        radius=factor*cauchy;candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales
        eta=_minimum_node_eta(raw_candidate);norm=float(np.linalg.norm(candidate_r))
        row={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"eta_minimum":eta,
            "residual_norm":norm,"residual_reduction":initial-norm,"event_residual":float(candidate_r[-1]),
            "post_projection_step_norm":float(np.linalg.norm(candidate-y)),"linear_predicted_residual_norm":float(np.linalg.norm(residual+radius*jd))}
        if retain_trial_vectors:row["raw_vector_hex"]=[float(v).hex() for v in raw_candidate]
        trials.append(row)
        if radius>0 and eta>1e-5 and norm<initial-REDUCTION_MARGIN:
            accepted.append((norm,candidate,row))
            if joint_filter and abs(float(candidate_r[-1]))<abs(initial_event)-REDUCTION_MARGIN:joint_accepted.append((norm,candidate,row))
    best=None
    if accepted:
        norm,vector,row=min(accepted,key=lambda item:item[0]);best={**row,"residual_norm":norm,"raw_vector_hex":[float(v).hex() for v in vector/scales]}
    best_joint=None
    if joint_accepted:
        norm,vector,row=min(joint_accepted,key=lambda item:item[0]);best_joint={**row,"residual_norm":norm,"raw_vector_hex":[float(v).hex() for v in vector/scales]}
    result={"source_state":"v16.58_fresh_canonical_SBP_projected_seed","old_non_SBP_state_transplanted":False,
        **assembled,"initial_residual_norm":initial,"merit_gradient_norm":float(np.linalg.norm(gradient)),"orientation":orientation,
        "measured_projected_slope":slope,"projected_J_direction_norm":jd_norm,"derived_cauchy_radius":cauchy,
        "trial_count":len(trials),"residual_reducing_trial_count":len(accepted),"trials":trials,"best_accepted":best}
    if joint_filter:
        result.update({"initial_event_residual":initial_event,"joint_filter_reducing_trial_count":len(joint_accepted),
            "best_joint_filter_accepted":best_joint})
    return result

def first_sbp_descent()->dict[str,Any]:return sbp_descent_from(v16_58_projected_raw_vector())

def completion_payload()->dict[str,Any]:
    result=first_sbp_descent();best=result["best_accepted"]
    validation={"fresh_SBP_residual_reproduced":math.isclose(result["initial_residual_norm"],48.25314420125869,rel_tol=0,abs_tol=2e-8),
        "no_old_state_transplant":not result["old_non_SBP_state_transplanted"],"measured_direction_is_descent":result["measured_projected_slope"]<0,
        "positive_cauchy_radius":result["derived_cauchy_radius"]>0,"strict_step_accepted":best is not None,
        "complete_residual_reduced":bool(best is not None and best["residual_norm"]<result["initial_residual_norm"]-REDUCTION_MARGIN),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_first_descent_v16_59","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"fresh_sbp_first_descent":result,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"FIRST_JOINT_STATIONARITY_DESCENT_OF_THE_VARIATIONALLY_CONSISTENT_FRESH_N3_PARENT_EVENT_ORBIT",
        "dependency_advanced":"BEGINS_SIMULTANEOUS_N3_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"REFRESH_THE_SBP_PHYSICAL_JACOBIAN_AT_THE_ACCEPTED_STATE_AND_CONTINUE_JOINT_CLOSURE",
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_first_descent_v16_59.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_58_projected_raw_vector","sbp_physical_jacobian","sbp_descent_from","first_sbp_descent","completion_payload","deterministic_json","materialize"]
