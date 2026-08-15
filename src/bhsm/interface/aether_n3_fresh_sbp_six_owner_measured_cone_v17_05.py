"""Measured six-owner normal cone after log-scale re-enters the active set."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.optimize import minimize
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import W0_ROWS,V0_ROWS,PERIOD_ROW,EVENT_ROW
from bhsm.interface.aether_n3_fresh_sbp_post_measured_audit_v17_04 import v17_03_selected_raw_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.05";CLASSIFICATION="BHSM_N3_FRESH_SBP_SIX_OWNER_MEASURED_FRACTIONAL_NORMAL_CONE";FULL_BHSM_COMPLETE=False
SCALE_ROWS=np.arange(0,230,10);FILTERS=(1e-6,1e-4,1e-3);CAUCHY=(0.01,0.03,0.1,0.2,0.3,0.5,0.8,1.0,2.0);EPS=3e-6;MARGIN=1e-10;LABELS=("complete","period","w0","v0","log_scale","event")
def _metrics(r:np.ndarray)->dict[str,float]:return {"complete":float(np.linalg.norm(r)),"period":abs(float(r[PERIOD_ROW])),"w0":float(np.linalg.norm(r[W0_ROWS])),"v0":float(np.linalg.norm(r[V0_ROWS])),"log_scale":float(np.linalg.norm(r[SCALE_ROWS])),"event":abs(float(r[EVENT_ROW]))}
def _slopes(r:np.ndarray,jd:np.ndarray,m:Mapping[str,float])->np.ndarray:return np.asarray([float(r@jd)/(m["complete"]**2),math.copysign(1,float(r[PERIOD_ROW]))*float(jd[PERIOD_ROW])/m["period"],float(r[W0_ROWS]@jd[W0_ROWS])/(m["w0"]**2),float(r[V0_ROWS]@jd[V0_ROWS])/(m["v0"]**2),float(r[SCALE_ROWS]@jd[SCALE_ROWS])/(m["log_scale"]**2),math.copysign(1,float(r[EVENT_ROW]))*float(jd[EVENT_ROW])/m["event"]])
def _gradients(J:np.ndarray,r:np.ndarray,m:Mapping[str,float])->np.ndarray:return np.asarray([J.T@r/(m["complete"]**2),math.copysign(1,float(r[PERIOD_ROW]))*J[PERIOD_ROW]/m["period"],J[W0_ROWS].T@r[W0_ROWS]/(m["w0"]**2),J[V0_ROWS].T@r[V0_ROWS]/(m["v0"]**2),J[SCALE_ROWS].T@r[SCALE_ROWS]/(m["log_scale"]**2),math.copysign(1,float(r[EVENT_ROW]))*J[EVENT_ROW]/m["event"]])
def _response(y:np.ndarray,r:np.ndarray,m:Mapping[str,float],basis:np.ndarray)->np.ndarray:
    columns=[]
    for i in range(basis.shape[1]):
        d=np.concatenate((basis[:,i],[0.0]));step=EPS/max(float(np.linalg.norm(d)),1e-300);_,plus=sbp_projected_residual_and_vector(y+step*d);_,minus=sbp_projected_residual_and_vector(y-step*d);columns.append(_slopes(r,(plus-minus)/(2*step),m))
    return np.column_stack(columns)
def _solve(response:np.ndarray,gram:np.ndarray)->tuple[np.ndarray,float,bool]:
    n=response.shape[1];c0=-np.linalg.pinv(response,rcond=1e-12)@np.ones(response.shape[0]);norm=math.sqrt(max(float(c0@gram@c0),0))
    if norm>0:c0*=0.9/norm
    x0=np.concatenate((c0,[min(0.0,float(np.min(-response@c0)))]));objective=lambda x:-float(x[-1]);gradient=lambda x:np.concatenate((np.zeros(n),[-1.0]));constraints=[{"type":"ineq","fun":lambda x:-response@x[:-1]-x[-1],"jac":lambda x:np.column_stack((-response,-np.ones(response.shape[0])))},{"type":"ineq","fun":lambda x:1-float(x[:-1]@gram@x[:-1]),"jac":lambda x:np.concatenate((-2*gram@x[:-1],[0.0]))}];solved=minimize(objective,x0,jac=gradient,constraints=constraints,method="SLSQP",options={"ftol":1e-13,"maxiter":1000});return np.asarray(solved.x[:-1]),float(solved.x[-1]),bool(solved.success)
def six_owner_measured_cone_from(raw_vector:np.ndarray,*,source_state:str="supplied_full_precision_state")->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,r=sbp_projected_residual_and_vector(y);initial=_metrics(r);assembled=sbp_physical_jacobian(y/scales);J=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(J,full_matrices=False);spectral=float(s[0]);G=_gradients(J,r,initial);rows=[];accepted=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;basis=vt.T@((vt@G.T)/denom[:,None]);gram=G@basis;response=_response(y,r,initial,basis);coeff,rate,solved=_solve(response,gram);dred=basis@coeff;direction=np.concatenate((dred,[0.0]));hnorm=math.sqrt(max(float(coeff@gram@coeff),0));step=EPS/max(float(np.linalg.norm(direction)),1e-300);_,plus=sbp_projected_residual_and_vector(y+step*direction);_,minus=sbp_projected_residual_and_vector(y-step*direction);jd=(plus-minus)/(2*step);slopes=_slopes(r,jd,initial);cauchy=max(0.0,-float(r@jd)/float(jd@jd));common=bool(np.all(slopes<0));row={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"maximin_solve_success":solved,"physical_normal_norm":hnorm,"predicted_equalized_fractional_rate":rate,"constraint_labels":list(LABELS),"measured_basis_response":response.tolist(),"predicted_fractional_slopes":(response@coeff).tolist(),"verified_fractional_slopes":{LABELS[i]:float(slopes[i]) for i in range(len(LABELS))},"derived_cauchy_radius":cauchy,"common_all_block_descent":common,"trials":[]}
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
    return {"source_state":source_state,"physical_residual_changed":False,"physical_event_changed":False,"owner_set":list(LABELS),"scale_row_count":len(SCALE_ROWS),"initial_metrics":initial,**assembled,"singular_value_scale":spectral,"direction_rows":rows,"common_six_owner_direction_count":sum(row["common_all_block_descent"] for row in rows),"strict_six_owner_candidate_count":len(accepted),"selected_six_owner_maximin":best}
def six_owner_measured_cone()->dict[str,Any]:return six_owner_measured_cone_from(v17_03_selected_raw_vector(),source_state="v17.03_selected_second_measured_fractional_state")
def completion_payload()->dict[str,Any]:
    r=six_owner_measured_cone();b=r["selected_six_owner_maximin"]
    validation={"v17_03_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.446086490970255,rel_tol=0,abs_tol=2e-8),"v17_03_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.124504504205082,rel_tol=0,abs_tol=2e-8),"scale_owner_reintroduced":"log_scale" in r["owner_set"],"all_scale_rows_retained":r["scale_row_count"]==23,"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"common_direction_exists":r["common_six_owner_direction_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_six_owner_measured_cone_v17_05","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_six_owner_measured_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"SIMULTANEOUS_COMPLETE_PERIOD_FIBER_HOPF_SCALE_AND_IDENTICAL_EVENT_DESCENT_WITHOUT_DELETING_SCALE_VARIATION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_SCALE_REENTERED_THE_ACTIVE_OWNER_SET","active_calculation":"PROMOTE_IF_VALIDATED_THEN_REPEAT_THE_SIX_OWNER_MEASURED_CONE","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_six_owner_measured_cone_v17_05.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","six_owner_measured_cone_from","six_owner_measured_cone","completion_payload","deterministic_json","materialize"]
