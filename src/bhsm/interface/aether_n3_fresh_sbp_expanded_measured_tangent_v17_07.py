"""Expanded measured tangent from all physical-normal damping scales."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.optimize import minimize
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_second_six_owner_measured_cone_v17_06 import v17_05_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import FILTERS,EPS,LABELS,MARGIN,_gradients,_metrics,_slopes
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.07";CLASSIFICATION="BHSM_N3_FRESH_SBP_EXPANDED_MULTI_FILTER_MEASURED_TANGENT";FULL_BHSM_COMPLETE=False
CAUCHY=(0.003,0.01,0.03,0.1,0.2,0.3,0.5,0.8,1.0,2.0)
def _measured_response(y:np.ndarray,r:np.ndarray,m:Mapping[str,float],basis:np.ndarray)->np.ndarray:
    columns=[]
    for i in range(basis.shape[1]):
        direction=np.concatenate((basis[:,i],[0.0]));_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction);columns.append(_slopes(r,(plus-minus)/(2*EPS),m))
    return np.column_stack(columns)
def _solve(response:np.ndarray)->tuple[np.ndarray,float,bool,np.ndarray,float]:
    # Convex dual of max_{||c||<=1} min_a(-M_a c): minimize
    # ||M^T lambda|| over the owner probability simplex.
    count=response.shape[0];gram=response@response.T;scale=max(float(np.linalg.norm(gram,2)),1e-300);scaled=gram/scale
    solved=minimize(lambda lam:0.5*float(lam@scaled@lam),np.ones(count)/count,jac=lambda lam:scaled@lam,bounds=[(0.0,None)]*count,constraints={"type":"eq","fun":lambda lam:float(np.sum(lam)-1.0),"jac":lambda lam:np.ones(count)},method="SLSQP",options={"ftol":1e-15,"maxiter":10000,"disp":False})
    lam=np.asarray(solved.x);dual_vector=response.T@lam;dual_norm=float(np.linalg.norm(dual_vector))
    if dual_norm==0:return np.zeros(response.shape[1]),0.0,False,lam,math.inf
    coeff=-dual_vector/dual_norm;rate=float(np.min(-response@coeff));gap=abs(dual_norm-rate)/max(dual_norm,1e-300)
    return coeff,rate,bool(solved.success and gap<1e-3),lam,gap
def expanded_measured_tangent()->dict[str,Any]:
    raw=v17_05_selected_raw_vector();scales=kkt_variable_scales();y=raw*scales;y,r=sbp_projected_residual_and_vector(y);initial=_metrics(r);assembled=sbp_physical_jacobian(y/scales);J=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(J,full_matrices=False);spectral=float(s[0]);G=_gradients(J,r,initial);columns=[];provenance=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;block=vt.T@((vt@G.T)/denom[:,None])
        for i,label in enumerate(LABELS):
            norm=float(np.linalg.norm(block[:,i]))
            if norm>0:columns.append(block[:,i]/norm);provenance.append({"relative_filter_scale":relative_filter,"owner":label,"pre_normalization_norm":norm})
    candidate_basis=np.column_stack(columns);ub,sb,vbt=np.linalg.svd(candidate_basis,full_matrices=False);keep=sb>max(1e-12,1e-10*float(sb[0]));basis=ub[:,keep];response=_measured_response(y,r,initial,basis);coeff,rate,solved,dual_weights,duality_gap=_solve(response);direction_reduced=basis@coeff;direction=np.concatenate((direction_reduced,[0.0]));_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction);jd=(plus-minus)/(2*EPS);verified=_slopes(r,jd,initial);cauchy=max(0.0,-float(r@jd)/float(jd@jd));common=bool(np.all(verified<0));trials=[];accepted=[]
    if common and cauchy>0:
        for factor in CAUCHY:
            radius=factor*cauchy
            try:
                candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(value).hex() for value in raw_candidate]};trials.append(trial)
                if eta>1e-5 and all(reductions[key]>MARGIN for key in initial):accepted.append((trial["minimum_fractional_progress"],sum(fractions.values()),trial))
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:trials.append({"cauchy_factor":factor,"domain_valid":False,"exception":type(exc).__name__})
    best=None
    if accepted:
        _,_,best=max(accepted,key=lambda item:(item[0],item[1]))
    return {"source_state":"v17.05_selected_six_owner_state","physical_residual_changed":False,"physical_event_changed":False,"owner_set":list(LABELS),"initial_metrics":initial,**assembled,"singular_value_scale":spectral,"candidate_column_count":candidate_basis.shape[1],"orthonormal_tangent_rank":int(np.sum(keep)),"candidate_column_provenance":provenance,"tangent_singular_values":sb.tolist(),"measured_response":response.tolist(),"maximin_solver":"CONVEX_OWNER_SIMPLEX_DUAL","maximin_solve_success":solved,"dual_owner_weights":dual_weights.tolist(),"relative_duality_gap":duality_gap,"predicted_equalized_fractional_rate":rate,"predicted_fractional_slopes":(response@coeff).tolist(),"verified_fractional_slopes":{LABELS[i]:float(verified[i]) for i in range(len(LABELS))},"direction_norm":float(np.linalg.norm(direction)),"derived_cauchy_radius":cauchy,"common_six_owner_descent":common,"trials":trials,"strict_six_owner_candidate_count":len(accepted),"selected_expanded_maximin":best}
def completion_payload()->dict[str,Any]:
    r=expanded_measured_tangent();b=r["selected_expanded_maximin"]
    validation={"v17_05_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.428689906333689,rel_tol=0,abs_tol=2e-8),"v17_05_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.122933895889858,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"multi_filter_span_used":r["candidate_column_count"]==18,"nontrivial_orthonormal_span":r["orthonormal_tangent_rank"]>=6,"dual_simplex_certificate":r["maximin_solver"]=="CONVEX_OWNER_SIMPLEX_DUAL" and math.isclose(sum(r["dual_owner_weights"]),1.0,rel_tol=0,abs_tol=1e-8) and min(r["dual_owner_weights"])>=-1e-10 and r["relative_duality_gap"]<1e-3,"maximin_solve_success":r["maximin_solve_success"],"common_direction_exists":r["common_six_owner_descent"],"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_expanded_measured_tangent_v17_07","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_expanded_measured_tangent":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"MULTI_SCALE_PHYSICAL_NORMAL_TANGENT_COMPATIBILITY_OF_COMPLETE_PERIOD_FIBER_HOPF_SCALE_AND_IDENTICAL_EVENT_DESCENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_THE_V17_06_LOCAL_SUBSPACE_OBSTRUCTION","active_calculation":"PROMOTE_IF_VALIDATED_OR_REDIRECT_TO_THE_MISSING_JACOBIAN_RANGE_COMPONENT","validation":validation,"validation_passed":all(validation.values())}
def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(item) for item in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {key:_canonical(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(item) for item in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_expanded_measured_tangent_v17_07.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","expanded_measured_tangent","completion_payload","deterministic_json","materialize"]
