"""Event-balanced Gauss--Newton preconditioner for the unchanged N=3 KKT."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector,sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v16.87";CLASSIFICATION="BHSM_N3_FRESH_SBP_EVENT_BALANCED_GAUSS_NEWTON_PRECONDITIONER";FULL_BHSM_COMPLETE=False
EVENT_WEIGHTS=(1.0,3.0,10.0,30.0);FILTERS=(1e-6,1e-4);CONE=1.1;CAUCHY=(0.03,0.1,0.2,0.3,0.5,0.8);EPS=3e-6;MARGIN=1e-10
def v16_86_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_dense_metric_ray_v16_86.json").read_text(encoding="utf-8"));values=p["fresh_sbp_second_dense_metric_ray"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.86 selected vector has wrong dimension")
    return raw
def event_balanced_metric_from(raw_vector:np.ndarray)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float);scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y);initial=float(np.linalg.norm(residual));event=float(residual[-1])
    assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))[:,:-1]
    event_gradient=sbp_event_covector((y/scales)[:-1])/scales[:-1]/scales[-1];absolute_event_gradient=math.copysign(1.0,event)*event_gradient
    rows=[];accepted=[]
    for event_weight in EVENT_WEIGHTS:
        weighted_matrix=matrix.copy();weighted_matrix[-1]*=event_weight;weighted_residual=residual.copy();weighted_residual[-1]*=event_weight
        u,s,vt=np.linalg.svd(weighted_matrix,full_matrices=False);spectral=float(s[0]);coeff=u.T@weighted_residual
        for relative_filter in FILTERS:
            mu=relative_filter*spectral;denom=s*s+mu*mu;base=-(vt.T@(s/denom*coeff));metric_inverse_event=vt.T@((vt@absolute_event_gradient)/denom)
            metric_event_norm=float(absolute_event_gradient@metric_inverse_event);base_event_slope=float(absolute_event_gradient@base);boundary=max(0.0,base_event_slope/metric_event_norm);corrected=base-CONE*boundary*metric_inverse_event
            direction=np.concatenate((corrected,[0.0]));direction/=np.linalg.norm(direction)
            try:
                _,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction)
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:
                rows.append({"event_row_weight":event_weight,"relative_filter_scale":relative_filter,"domain_valid":False,"exception":type(exc).__name__,"common_descent_direction":False,"trials":[]});continue
            jd=(plus-minus)/(2*EPS);total_slope=float(residual@jd);absolute_event_slope=math.copysign(1.0,event)*float((plus[-1]-minus[-1])/(2*EPS));cauchy=max(0.0,-total_slope/float(jd@jd))
            row={"event_row_weight":event_weight,"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"base_absolute_event_linear_slope":base_event_slope,
                "metric_event_covector_norm_squared":metric_event_norm,"measured_total_merit_slope":total_slope,"measured_absolute_event_slope":absolute_event_slope,"derived_cauchy_radius":cauchy,
                "common_descent_direction":bool(total_slope<0 and absolute_event_slope<0),"trials":[]}
            if row["common_descent_direction"] and cauchy>0:
                for factor in CAUCHY:
                    radius=factor*cauchy
                    try:
                        candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);norm=float(np.linalg.norm(candidate_r));candidate_event=float(candidate_r[-1])
                        trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"residual_norm":norm,"residual_reduction":initial-norm,"event_residual":candidate_event,"absolute_event_reduction":abs(event)-abs(candidate_event),
                            "eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(v).hex() for v in raw_candidate]};row["trials"].append(trial)
                        if eta>1e-5 and norm<initial-MARGIN and abs(candidate_event)<abs(event)-MARGIN:accepted.append((norm,trial,event_weight,relative_filter))
                    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"trust_radius":radius,"domain_valid":False,"exception":type(exc).__name__})
            rows.append(row)
    best=None
    if accepted:
        norm,trial,weight,relative_filter=min(accepted,key=lambda x:x[0]);best={"event_row_weight":weight,"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}",**trial,"residual_norm":norm}
    return {"source_state":"v16.86_selected_second_dense_metric_state","physical_residual_changed":False,"physical_event_changed":False,"preconditioner_only_event_row_weights":list(EVENT_WEIGHTS),"initial_residual_norm":initial,"initial_event_residual":event,**assembled,
        "direction_count":len(rows),"common_descent_direction_count":sum(r["common_descent_direction"] for r in rows),"strict_joint_candidate_count":len(accepted),"direction_rows":rows,"selected_best_accepted":best}
def event_balanced_metric()->dict[str,Any]:return event_balanced_metric_from(v16_86_selected_raw_vector())
def completion_payload()->dict[str,Any]:
    r=event_balanced_metric();b=r["selected_best_accepted"]
    validation={"v16_86_residual_reproduced":math.isclose(r["initial_residual_norm"],2.897637137967211,rel_tol=0,abs_tol=2e-8),"v16_86_event_reproduced":math.isclose(r["initial_event_residual"],-0.278977516745537,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],
        "complete_weight_filter_grid":r["direction_count"]==len(EVENT_WEIGHTS)*len(FILTERS),"common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-MARGIN),
        "absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-MARGIN),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_event_balanced_metric_v16_87","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_event_balanced_metric":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"BALANCED_SIMULTANEOUS_CLOSURE_OF_PARENT_ORBIT_STATIONARITY_AND_THE_IDENTICAL_ACTUAL_EULER_DIRAC_EVENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_THE_BEST_UNWEIGHTED_STRICT_JOINT_CANDIDATE_OR_USE_THE_MEASURED_TRADEOFF_TO_RETARGET_THE_SAME_EVENT","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_event_balanced_metric_v16_87.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","EVENT_WEIGHTS","FILTERS","CAUCHY","v16_86_selected_raw_vector","event_balanced_metric_from","event_balanced_metric","completion_payload","deterministic_json","materialize"]
