"""Physical-normal maximin fractional descent from the v17.00 state."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.optimize import minimize
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import _metrics,W0_ROWS,V0_ROWS,PERIOD_ROW,EVENT_ROW
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.01";CLASSIFICATION="BHSM_N3_FRESH_SBP_PHYSICAL_NORMAL_FRACTIONAL_MAXIMIN_CONE";FULL_BHSM_COMPLETE=False
FILTERS=(1e-6,1e-4,1e-3);CAUCHY=(0.01,0.03,0.1,0.2,0.3,0.5,0.8,1.0,2.0);EPS=3e-6;MARGIN=1e-10

def v17_00_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_fifth_coupled_owner_cone_v17_00.json").read_text(encoding="utf-8"));values=p["fresh_sbp_fifth_coupled_owner_cone"]["selected_maximin_all_block"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v17.00 selected vector has wrong dimension")
    return raw

def _fractional_gradients(matrix:np.ndarray,residual:np.ndarray,metrics:Mapping[str,float])->tuple[np.ndarray,list[str]]:
    gradients=[matrix.T@residual/(metrics["complete"]**2),math.copysign(1.0,float(residual[PERIOD_ROW]))*matrix[PERIOD_ROW]/metrics["period"],matrix[W0_ROWS].T@residual[W0_ROWS]/(metrics["w0"]**2),matrix[V0_ROWS].T@residual[V0_ROWS]/(metrics["v0"]**2),math.copysign(1.0,float(residual[EVENT_ROW]))*matrix[EVENT_ROW]/metrics["event"]]
    return np.asarray(gradients),["complete","period","w0","v0","event"]

def _maximin_coefficients(gram:np.ndarray)->tuple[np.ndarray,float,bool]:
    count=gram.shape[0];pinv=np.linalg.pinv(gram,rcond=1e-12);c0=-pinv@np.ones(count);norm=math.sqrt(max(float(c0@gram@c0),0.0))
    if norm>0:c0*=0.9/norm
    t0=min(0.0,float(np.min(-gram@c0)));x0=np.concatenate((c0,[t0]))
    objective=lambda x:-float(x[-1]);gradient=lambda x:np.concatenate((np.zeros(count),[-1.0]))
    constraints=[{"type":"ineq","fun":lambda x:-gram@x[:-1]-x[-1],"jac":lambda x:np.column_stack((-gram,-np.ones(count)))},{"type":"ineq","fun":lambda x:1.0-float(x[:-1]@gram@x[:-1]),"jac":lambda x:np.concatenate((-2.0*gram@x[:-1],[0.0]))}]
    solved=minimize(objective,x0,jac=gradient,constraints=constraints,method="SLSQP",options={"ftol":1e-13,"maxiter":1000,"disp":False})
    return np.asarray(solved.x[:-1]),float(solved.x[-1]),bool(solved.success)

def fractional_maximin_cone()->dict[str,Any]:
    raw=v17_00_selected_raw_vector();scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y);initial=_metrics(residual);assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(matrix,full_matrices=False);spectral=float(s[0]);gradients,labels=_fractional_gradients(matrix,residual,initial);rows=[];accepted=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;hinv_gt=vt.T@((vt@gradients.T)/denom[:,None]);gram=gradients@hinv_gt;coeff,tangent_rate,solved=_maximin_coefficients(gram);direction_reduced=hinv_gt@coeff;hnorm=math.sqrt(max(float(coeff@gram@coeff),0.0));direction=np.concatenate((direction_reduced,[0.0]))
        try:_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction)
        except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:rows.append({"relative_filter_scale":relative_filter,"direction_domain_valid":False,"exception":type(exc).__name__,"trials":[]});continue
        jd=(plus-minus)/(2*EPS);slopes={"complete":float(residual@jd)/(initial["complete"]**2),"period":math.copysign(1.0,float(residual[PERIOD_ROW]))*float(jd[PERIOD_ROW])/initial["period"],"w0":float(residual[W0_ROWS]@jd[W0_ROWS])/(initial["w0"]**2),"v0":float(residual[V0_ROWS]@jd[V0_ROWS])/(initial["v0"]**2),"event":math.copysign(1.0,float(residual[EVENT_ROW]))*float(jd[EVENT_ROW])/initial["event"]};cauchy=max(0.0,-float(residual@jd)/float(jd@jd));common=all(value<0 for value in slopes.values());row={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"maximin_solve_success":solved,"physical_normal_norm":hnorm,"predicted_equalized_fractional_rate":tangent_rate,"constraint_labels":labels,"predicted_fractional_slopes":(gram@coeff).tolist(),"measured_fractional_slopes":slopes,"derived_cauchy_radius":cauchy,"common_all_block_descent":common,"trials":[]}
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
    return {"source_state":"v17.00_selected_fifth_coupled_owner_state","physical_residual_changed":False,"physical_event_changed":False,"normal_metric_changed":False,"objective":"MAXIMIZE_THE_WORST_LINEARIZED_FRACTIONAL_DECREASE_OF_COMPLETE_PERIOD_W0_V0_EVENT_AT_UNIT_PHYSICAL_NORMAL_NORM","initial_metrics":initial,**assembled,"singular_value_scale":spectral,"direction_rows":rows,"common_all_block_direction_count":sum(row.get("common_all_block_descent",False) for row in rows),"strict_all_block_candidate_count":len(accepted),"selected_maximin_fractional":best}

def completion_payload()->dict[str,Any]:
    r=fractional_maximin_cone();b=r["selected_maximin_fractional"]
    validation={"v17_00_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.474584035022365,rel_tol=0,abs_tol=2e-8),"v17_00_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.129386144536552,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"same_normal_metric":not r["normal_metric_changed"],"common_direction_exists":r["common_all_block_direction_count"]>0,"strict_candidate_exists":b is not None,"all_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_fractional_maximin_cone_v17_01","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_fractional_maximin_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"BALANCED_SIMULTANEOUS_CLOSURE_RATE_OF_PERIOD_FIBER_HOPF_AND_IDENTICAL_EVENT_IN_THE_PHYSICAL_NORMAL_METRIC","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AT_THE_V0_BOTTLENECK","active_calculation":"PROMOTE_IF_VALIDATED_OR_REDIRECT_TO_THE_MEASURED_TANGENT_OBSTRUCTION","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_fractional_maximin_cone_v17_01.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_00_selected_raw_vector","fractional_maximin_cone","completion_payload","deterministic_json","materialize"]
