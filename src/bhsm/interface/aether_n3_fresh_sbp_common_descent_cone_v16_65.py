"""Common total-merit/event descent cone at the v16.63 fresh SBP state."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector,sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v16.65";CLASSIFICATION="BHSM_N3_FRESH_SBP_COMMON_TOTAL_EVENT_DESCENT_CONE";FULL_BHSM_COMPLETE=False
CONE_FACTORS=(1.001,1.01,1.1,2.0,4.0,8.0);CAUCHY_FACTORS=(0.125,0.25,0.5,1.0,2.0);DIRECTIONAL_EPSILON=3e-6;MARGIN=1e-10

def v16_63_selected_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_joint_filter_v16_63.json").read_text(encoding="utf-8"))
    values=payload["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.63 selected vector has wrong dimension")
    return raw

def common_descent_cone_from(raw_vector:np.ndarray)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y)
    assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))
    total_gradient=matrix.T@residual;total_gradient[-1]=0
    event_gradient=np.zeros(376);event_gradient[:-1]=sbp_event_covector((y/scales)[:-1])/scales[:-1]/scales[-1]
    event=float(residual[-1]);absolute_event_gradient=math.copysign(1.0,event)*event_gradient
    threshold=max(0.0,-float(absolute_event_gradient@total_gradient)/float(absolute_event_gradient@absolute_event_gradient))
    initial=float(np.linalg.norm(residual));rows=[];accepted=[]
    for cone_factor in CONE_FACTORS:
        beta=cone_factor*threshold
        raw_direction=-total_gradient-beta*absolute_event_gradient;direction=raw_direction/np.linalg.norm(raw_direction)
        plus_y,plus_r=sbp_projected_residual_and_vector(y+DIRECTIONAL_EPSILON*direction)
        minus_y,minus_r=sbp_projected_residual_and_vector(y-DIRECTIONAL_EPSILON*direction)
        jd=(plus_r-minus_r)/(2*DIRECTIONAL_EPSILON);total_slope=float(residual@jd)
        event_slope=float((plus_r[-1]-minus_r[-1])/(2*DIRECTIONAL_EPSILON));absolute_event_slope=math.copysign(1.0,event)*event_slope
        jd_norm=float(np.linalg.norm(jd));cauchy=max(0.0,-total_slope/jd_norm**2)
        direction_row={"cone_factor":cone_factor,"beta":beta,"total_merit_slope":total_slope,
            "absolute_event_slope":absolute_event_slope,"derived_cauchy_radius":cauchy,"common_descent_direction":bool(total_slope<0 and absolute_event_slope<0),"trials":[]}
        if total_slope<0 and absolute_event_slope<0 and cauchy>0:
            for factor in CAUCHY_FACTORS:
                radius=factor*cauchy;candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales
                eta=_minimum_node_eta(raw_candidate);norm=float(np.linalg.norm(candidate_r));candidate_event=float(candidate_r[-1])
                trial={"cauchy_factor":factor,"trust_radius":radius,"residual_norm":norm,"residual_reduction":initial-norm,
                    "event_residual":candidate_event,"absolute_event_reduction":abs(event)-abs(candidate_event),"eta_minimum":eta,
                    "post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(v).hex() for v in raw_candidate]}
                direction_row["trials"].append(trial)
                if radius>0 and eta>1e-5 and norm<initial-MARGIN and abs(candidate_event)<abs(event)-MARGIN:accepted.append((norm,trial,cone_factor))
        rows.append(direction_row)
    best=None
    if accepted:
        norm,trial,cone=min(accepted,key=lambda item:item[0]);best={"cone_factor":cone,**trial,"residual_norm":norm}
    return {"source_state":"v16.63_selected_strict_joint_state","initial_residual_norm":initial,"initial_event_residual":event,
        "total_merit_gradient_norm":float(np.linalg.norm(total_gradient)),"absolute_event_gradient_norm":float(np.linalg.norm(absolute_event_gradient)),
        "minimum_event_constraint_beta":threshold,**assembled,"cone_direction_count":len(rows),
        "common_descent_direction_count":sum(row["common_descent_direction"] for row in rows),
        "strict_joint_candidate_count":len(accepted),"direction_rows":rows,"selected_best_accepted":best}

def common_descent_cone()->dict[str,Any]:return common_descent_cone_from(v16_63_selected_raw_vector())

def completion_payload()->dict[str,Any]:
    r=common_descent_cone();b=r["selected_best_accepted"]
    validation={"v16_63_state_reproduced":math.isclose(r["initial_residual_norm"],39.40229627868378,rel_tol=0,abs_tol=2e-8),
        "actual_event_reproduced":math.isclose(r["initial_event_residual"],0.370232077820356,rel_tol=0,abs_tol=2e-8),
        "event_constraint_beta_derived":r["minimum_event_constraint_beta"]>0,"common_descent_direction_exists":r["common_descent_direction_count"]>0,
        "strict_joint_candidate_exists":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-MARGIN),
        "absolute_actual_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-MARGIN),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_common_descent_cone_v16_65","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_common_descent_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"EXISTENCE_OF_A_LOCAL_DIRECTION_THAT_SIMULTANEOUSLY_DECREASES_PARENT_STATIONARITY_MERIT_AND_THE_ACTUAL_EVENT_MAGNITUDE",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_THE_COMMON_CONE_STATE_AND_REBUILD_THE_STRICT_JOINT_SOLVE","validation":validation,"validation_passed":all(validation.values())}
def _canonical(v:Any)->Any:
    if isinstance(v,np.ndarray):return [_canonical(x) for x in v.tolist()]
    if isinstance(v,np.bool_):return bool(v)
    if isinstance(v,np.integer):return int(v)
    if isinstance(v,np.floating):v=float(v)
    if isinstance(v,float):
        if not math.isfinite(v):raise ValueError("non-finite float")
        return round(v,15)
    if isinstance(v,Mapping):return {k:_canonical(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [_canonical(x) for x in v]
    return v
def deterministic_json(p:Mapping[str,Any])->str:return json.dumps(_canonical(p),indent=2,sort_keys=True)+"\n"
def materialize(d:str|Path)->Path:
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_common_descent_cone_v16_65.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","CONE_FACTORS","CAUCHY_FACTORS","v16_63_selected_raw_vector","common_descent_cone_from","common_descent_cone","completion_payload","deterministic_json","materialize"]
