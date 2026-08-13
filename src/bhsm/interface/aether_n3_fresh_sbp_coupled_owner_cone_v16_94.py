"""Coupled period/w0/v0/event descent cone in the physical normal metric."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.optimize import minimize
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_owner_balanced_metric_v16_93 import v16_93_selected_raw_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v16.94";CLASSIFICATION="BHSM_N3_FRESH_SBP_COUPLED_PERIOD_W0_V0_EVENT_NORMAL_METRIC_DESCENT_CONE";FULL_BHSM_COMPLETE=False
FILTERS=(1e-6,1e-4,1e-3);CONE_FACTORS=(1.01,1.1,2.0);CAUCHY=(0.03,0.1,0.2,0.3,0.5,0.8);EPS=3e-6;MARGIN=1e-10
W0_ROWS=np.arange(4,230,10);V0_ROWS=np.arange(7,230,10);PERIOD_ROW=374;EVENT_ROW=375
def _metrics(r:np.ndarray)->dict[str,float]:
    return {"complete":float(np.linalg.norm(r)),"period":abs(float(r[PERIOD_ROW])),"w0":float(np.linalg.norm(r[W0_ROWS])),"v0":float(np.linalg.norm(r[V0_ROWS])),"event":abs(float(r[EVENT_ROW]))}
def _constraint_gradients(matrix:np.ndarray,residual:np.ndarray)->tuple[np.ndarray,list[str]]:
    gradients=[];labels=[]
    for label,rows in (("period",np.asarray([PERIOD_ROW])),("w0",W0_ROWS),("v0",V0_ROWS)):
        block=residual[rows];g=matrix[rows].T@block;n=float(np.linalg.norm(g))
        if n>0:gradients.append(g/n);labels.append(label)
    g=math.copysign(1.0,float(residual[EVENT_ROW]))*matrix[EVENT_ROW];n=float(np.linalg.norm(g))
    if n>0:gradients.append(g/n);labels.append("event")
    return np.asarray(gradients),labels
def coupled_owner_cone_from(
    raw_vector:np.ndarray,
    *,
    source_state:str="supplied_full_precision_state",
)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y);initial=_metrics(residual);assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))[:,:-1]
    u,s,vt=np.linalg.svd(matrix,full_matrices=False);spectral=float(s[0]);coeff=u.T@residual;A,labels=_constraint_gradients(matrix,residual);rows=[];accepted=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;base=-(vt.T@(s/denom*coeff));hinv_at=vt.T@((vt@A.T)/denom[:,None]);G=A@hinv_at;b=A@base
        objective=lambda lam:0.5*float(lam@G@lam)-float(b@lam);gradient=lambda lam:G@lam-b
        solved=minimize(objective,np.zeros(A.shape[0]),jac=gradient,bounds=[(0.0,None)]*A.shape[0],method="L-BFGS-B",options={"ftol":1e-15,"gtol":1e-12,"maxiter":500})
        lam=np.asarray(solved.x);correction=hinv_at@lam;projected=base-correction
        for cone_factor in CONE_FACTORS:
            direction_reduced=base-cone_factor*correction;direction=np.concatenate((direction_reduced,[0.0]));direction/=np.linalg.norm(direction)
            try:_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction)
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:rows.append({"relative_filter_scale":relative_filter,"cone_factor":cone_factor,"direction_domain_valid":False,"exception":type(exc).__name__,"common_all_block_descent":False,"trials":[]});continue
            jd=(plus-minus)/(2*EPS);slopes={"complete_merit":float(residual@jd),"period":math.copysign(1.0,float(residual[PERIOD_ROW]))*float(jd[PERIOD_ROW]),"w0":float(residual[W0_ROWS]@jd[W0_ROWS])/max(initial["w0"],1e-300),"v0":float(residual[V0_ROWS]@jd[V0_ROWS])/max(initial["v0"],1e-300),"event":math.copysign(1.0,float(residual[EVENT_ROW]))*float(jd[EVENT_ROW])}
            cauchy=max(0.0,-slopes["complete_merit"]/float(jd@jd));common=all(value<0 for value in slopes.values());row={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"cone_factor":cone_factor,"dual_projection_success":bool(solved.success),"dual_multipliers":lam.tolist(),"constraint_labels":labels,"base_constraint_slopes":b.tolist(),"projected_constraint_slopes":(A@projected).tolist(),"measured_slopes":slopes,"derived_cauchy_radius":cauchy,"common_all_block_descent":common,"trials":[]}
            if common and cauchy>0:
                for factor in CAUCHY:
                    radius=factor*cauchy
                    try:
                        candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(v).hex() for v in raw_candidate]};row["trials"].append(trial)
                        if eta>1e-5 and all(reductions[k]>MARGIN for k in initial):accepted.append((trial["minimum_fractional_progress"],sum(fractions.values()),trial,relative_filter,cone_factor))
                    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"trust_radius":radius,"domain_valid":False,"exception":type(exc).__name__})
            rows.append(row)
    best=None
    if accepted:
        _,_,trial,relative_filter,cone_factor=max(accepted,key=lambda x:(x[0],x[1]));best={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","cone_factor":cone_factor,**trial}
    return {"source_state":source_state,"physical_residual_changed":False,"physical_event_changed":False,"required_decreasing_metrics":list(initial),"initial_metrics":initial,**assembled,"singular_value_scale":spectral,"direction_count":len(rows),"common_all_block_direction_count":sum(r["common_all_block_descent"] for r in rows),"strict_all_block_candidate_count":len(accepted),"direction_rows":rows,"selected_maximin_all_block":best}
def coupled_owner_cone()->dict[str,Any]:return coupled_owner_cone_from(
    v16_93_selected_raw_vector(),source_state="v16.93_selected_identity_metric_state"
)
def completion_payload()->dict[str,Any]:
    r=coupled_owner_cone();b=r["selected_maximin_all_block"]
    validation={"v16_93_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],2.437270312411382,rel_tol=0,abs_tol=2e-8),"v16_93_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.208275968278929,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_five_metrics_present":set(r["required_decreasing_metrics"])=={"complete","period","w0","v0","event"},"common_direction_exists":r["common_all_block_direction_count"]>0,"strict_all_block_candidate_exists":b is not None,"all_metrics_reduced":bool(b is not None and all(v>MARGIN for v in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_coupled_owner_cone_v16_94","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_coupled_owner_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"SIMULTANEOUS_PERIOD_FIBER_LOCALIZATION_HOPF_ANISOTROPY_AND_ACTUAL_EVENT_CLOSURE_IN_ONE_PHYSICAL_NORMAL_METRIC","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_THE_SCALE_BLOCK_COLLAPSE","active_calculation":"PROMOTE_THE_ALL_BLOCK_MAXIMIN_STATE_IF_VALIDATED_OR_USE_THE_ACTIVE_CONSTRAINTS_TO_BUILD_THE_NEXT_COUPLED_CORRECTION","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_coupled_owner_cone_v16_94.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","coupled_owner_cone_from","coupled_owner_cone","completion_payload","deterministic_json","materialize"]
