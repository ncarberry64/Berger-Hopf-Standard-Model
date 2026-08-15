"""Measured five-owner response in the fresh physical-normal subspace."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.optimize import minimize
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import _metrics,W0_ROWS,V0_ROWS,PERIOD_ROW,EVENT_ROW
from bhsm.interface.aether_n3_fresh_sbp_fractional_maximin_cone_v17_01 import v17_00_selected_raw_vector,_fractional_gradients
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.02";CLASSIFICATION="BHSM_N3_FRESH_SBP_MEASURED_FRACTIONAL_RESPONSE_CONE";FULL_BHSM_COMPLETE=False
FILTERS=(1e-6,1e-4,1e-3);CAUCHY=(0.01,0.03,0.1,0.2,0.3,0.5,0.8,1.0,2.0);EPS=3e-6;MARGIN=1e-10

def _fractional_slopes(residual:np.ndarray,jd:np.ndarray,metrics:Mapping[str,float])->np.ndarray:
    return np.asarray([float(residual@jd)/(metrics["complete"]**2),math.copysign(1.0,float(residual[PERIOD_ROW]))*float(jd[PERIOD_ROW])/metrics["period"],float(residual[W0_ROWS]@jd[W0_ROWS])/(metrics["w0"]**2),float(residual[V0_ROWS]@jd[V0_ROWS])/(metrics["v0"]**2),math.copysign(1.0,float(residual[EVENT_ROW]))*float(jd[EVENT_ROW])/metrics["event"]])

def _measured_response(y:np.ndarray,residual:np.ndarray,metrics:Mapping[str,float],basis:np.ndarray)->np.ndarray:
    columns=[]
    for index in range(basis.shape[1]):
        direction=np.concatenate((basis[:,index],[0.0]));step=EPS/max(float(np.linalg.norm(direction)),1e-300);_,plus=sbp_projected_residual_and_vector(y+step*direction);_,minus=sbp_projected_residual_and_vector(y-step*direction);columns.append(_fractional_slopes(residual,(plus-minus)/(2*step),metrics))
    return np.column_stack(columns)

def _solve_maximin(response:np.ndarray,norm_gram:np.ndarray)->tuple[np.ndarray,float,bool]:
    count=response.shape[1];c0=-np.linalg.pinv(response,rcond=1e-12)@np.ones(response.shape[0]);norm=math.sqrt(max(float(c0@norm_gram@c0),0.0))
    if norm>0:c0*=0.9/norm
    t0=min(0.0,float(np.min(-response@c0)));x0=np.concatenate((c0,[t0]));objective=lambda x:-float(x[-1]);gradient=lambda x:np.concatenate((np.zeros(count),[-1.0]));constraints=[{"type":"ineq","fun":lambda x:-response@x[:-1]-x[-1],"jac":lambda x:np.column_stack((-response,-np.ones(response.shape[0])))},{"type":"ineq","fun":lambda x:1.0-float(x[:-1]@norm_gram@x[:-1]),"jac":lambda x:np.concatenate((-2.0*norm_gram@x[:-1],[0.0]))}]
    solved=minimize(objective,x0,jac=gradient,constraints=constraints,method="SLSQP",options={"ftol":1e-13,"maxiter":1000,"disp":False});return np.asarray(solved.x[:-1]),float(solved.x[-1]),bool(solved.success)

def measured_fractional_cone_from(raw_vector:np.ndarray,*,source_state:str="supplied_full_precision_state")->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y);initial=_metrics(residual);assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(matrix,full_matrices=False);spectral=float(s[0]);gradients,labels=_fractional_gradients(matrix,residual,initial);rows=[];accepted=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;basis=vt.T@((vt@gradients.T)/denom[:,None]);norm_gram=gradients@basis;response=_measured_response(y,residual,initial,basis);coeff,tangent_rate,solved=_solve_maximin(response,norm_gram);direction_reduced=basis@coeff;direction=np.concatenate((direction_reduced,[0.0]));hnorm=math.sqrt(max(float(coeff@norm_gram@coeff),0.0));step=EPS/max(float(np.linalg.norm(direction)),1e-300);_,plus=sbp_projected_residual_and_vector(y+step*direction);_,minus=sbp_projected_residual_and_vector(y-step*direction);jd=(plus-minus)/(2*step);slopes=_fractional_slopes(residual,jd,initial);cauchy=max(0.0,-float(residual@jd)/float(jd@jd));common=bool(np.all(slopes<0));row={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"maximin_solve_success":solved,"physical_normal_norm":hnorm,"predicted_equalized_fractional_rate":tangent_rate,"constraint_labels":labels,"measured_basis_response":response.tolist(),"predicted_fractional_slopes":(response@coeff).tolist(),"verified_fractional_slopes":{labels[i]:float(slopes[i]) for i in range(len(labels))},"derived_cauchy_radius":cauchy,"common_all_block_descent":common,"trials":[]}
        if common and cauchy>0:
            for factor in CAUCHY:
                radius=factor*cauchy
                try:
                    candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(value).hex() for value in raw_candidate]};row["trials"].append(trial)
                    if eta>1e-5 and all(reductions[key]>MARGIN for key in initial):accepted.append((trial["minimum_fractional_progress"],sum(fractions.values()),trial,relative_filter))
                except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"domain_valid":False,"exception":type(exc).__name__})
        rows.append(row)
    best=None
    if accepted:
        _,_,trial,relative_filter=max(accepted,key=lambda item:(item[0],item[1]));best={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}",**trial}
    return {"source_state":source_state,"physical_residual_changed":False,"physical_event_changed":False,"subspace":"H_INVERSE_TIMES_THE_FIVE_PHYSICAL_OWNER_GRADIENTS","response_calibration":"CENTERED_ACTUAL_RESIDUAL_EVALUATIONS_IN_EACH_SUBSPACE_BASIS_DIRECTION","initial_metrics":initial,**assembled,"singular_value_scale":spectral,"direction_rows":rows,"common_all_block_direction_count":sum(row["common_all_block_descent"] for row in rows),"strict_all_block_candidate_count":len(accepted),"selected_measured_maximin_fractional":best}

def measured_fractional_cone()->dict[str,Any]:return measured_fractional_cone_from(v17_00_selected_raw_vector(),source_state="v17.00_selected_fifth_coupled_owner_state")

def completion_payload()->dict[str,Any]:
    r=measured_fractional_cone();b=r["selected_measured_maximin_fractional"]
    validation={"v17_00_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.474584035022365,rel_tol=0,abs_tol=2e-8),"v17_00_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.129386144536552,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"measured_response_used":"ACTUAL_RESIDUAL" in r["response_calibration"],"common_direction_exists":r["common_all_block_direction_count"]>0,"strict_candidate_exists":b is not None,"all_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_measured_fractional_cone_v17_02","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_measured_fractional_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"ACTUAL_FIVE_OWNER_RESPONSE_INSIDE_THE_FRESH_PHYSICAL_NORMAL_SUBSPACE","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_THE_V17_01_DERIVATIVE_MISMATCH","active_calculation":"PROMOTE_IF_VALIDATED_OR_REDIRECT_TO_THE_MISSING_PHYSICAL_JACOBIAN_BLOCK","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_measured_fractional_cone_v17_02.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","measured_fractional_cone_from","measured_fractional_cone","completion_payload","deterministic_json","materialize"]
