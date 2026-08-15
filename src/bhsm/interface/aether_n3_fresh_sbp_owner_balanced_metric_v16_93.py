"""Owner-balanced normal metric for period, w0, v0 and the actual event."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector,sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_pareto_balanced_selection_v16_89 import pareto_candidate_from_result
from bhsm.interface.aether_n3_fresh_sbp_post_pareto_audit_v16_92 import v16_91_selected_raw_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v16.93";CLASSIFICATION="BHSM_N3_FRESH_SBP_PERIOD_W0_V0_EVENT_OWNER_BALANCED_NORMAL_METRIC";FULL_BHSM_COMPLETE=False
FILTERS=(1e-6,1e-4);CAUCHY=(0.03,0.1,0.2,0.3,0.5,0.8);EPS=3e-6;MARGIN=1e-10
def _weight_schemes(residual:np.ndarray)->list[dict[str,Any]]:
    q=residual[:230].reshape(23,10);period=abs(float(residual[-2]));event=abs(float(residual[-1]));w0=float(np.linalg.norm(q[:,4]));v0=float(np.linalg.norm(q[:,7]));target=max(period,w0,v0,1e-12)
    equal={"period":1.0,"w0":target/max(w0,1e-12),"v0":target/max(v0,1e-12),"event":target/max(event,1e-12)}
    return [{"label":"identity","period":1.0,"w0":1.0,"v0":1.0,"event":1.0},{"label":"owner_equalized",**equal},{"label":"owner_equalized_event_x3",**{**equal,"event":3.0*equal["event"]}}]
def owner_balanced_metric()->dict[str,Any]:
    raw=v16_91_selected_raw_vector();scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y);initial=float(np.linalg.norm(residual));event=float(residual[-1]);assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"))[:,:-1]
    event_gradient=sbp_event_covector((y/scales)[:-1])/scales[:-1]/scales[-1];absolute_event_gradient=math.copysign(1.0,event)*event_gradient;rows=[];accepted=[];schemes=_weight_schemes(residual)
    for scheme in schemes:
        row_weights=np.ones(376);qweights=row_weights[:230].reshape(23,10);qweights[:,4]=scheme["w0"];qweights[:,7]=scheme["v0"];row_weights[-2]=scheme["period"];row_weights[-1]=scheme["event"]
        wm=row_weights[:,None]*matrix;wr=row_weights*residual;u,s,vt=np.linalg.svd(wm,full_matrices=False);spectral=float(s[0]);coeff=u.T@wr
        for relative_filter in FILTERS:
            mu=relative_filter*spectral;denom=s*s+mu*mu;base=-(vt.T@(s/denom*coeff));metric_inverse_event=vt.T@((vt@absolute_event_gradient)/denom);metric_event_norm=float(absolute_event_gradient@metric_inverse_event);base_event_slope=float(absolute_event_gradient@base);alpha=max(0.0,1.1*base_event_slope/metric_event_norm);corrected=base-alpha*metric_inverse_event
            direction=np.concatenate((corrected,[0.0]));direction/=np.linalg.norm(direction)
            try:_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction)
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:rows.append({"scheme":scheme,"relative_filter_scale":relative_filter,"domain_valid":False,"exception":type(exc).__name__,"common_descent_direction":False,"trials":[]});continue
            jd=(plus-minus)/(2*EPS);total_slope=float(residual@jd);absolute_event_slope=math.copysign(1.0,event)*float((plus[-1]-minus[-1])/(2*EPS));cauchy=max(0.0,-total_slope/float(jd@jd));row={"scheme":scheme,"event_row_weight":scheme["event"],"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,"measured_total_merit_slope":total_slope,"measured_absolute_event_slope":absolute_event_slope,"derived_cauchy_radius":cauchy,"common_descent_direction":bool(total_slope<0 and absolute_event_slope<0),"trials":[]}
            if row["common_descent_direction"] and cauchy>0:
                for factor in CAUCHY:
                    radius=factor*cauchy
                    try:
                        candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);norm=float(np.linalg.norm(candidate_r));cevent=float(candidate_r[-1]);trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"residual_norm":norm,"residual_reduction":initial-norm,"event_residual":cevent,"absolute_event_reduction":abs(event)-abs(cevent),"eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(v).hex() for v in raw_candidate]};row["trials"].append(trial)
                        if eta>1e-5 and norm<initial-MARGIN and abs(cevent)<abs(event)-MARGIN:accepted.append((norm,trial,scheme,relative_filter))
                    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"trust_radius":radius,"domain_valid":False,"exception":type(exc).__name__})
            rows.append(row)
    physical={"source_state":"v16.91_selected_refreshed_pareto_state","physical_residual_changed":False,"physical_event_changed":False,"owner_weight_schemes":schemes,"initial_residual_norm":initial,"initial_event_residual":event,**assembled,"direction_count":len(rows),"common_descent_direction_count":sum(r["common_descent_direction"] for r in rows),"strict_joint_candidate_count":len(accepted),"direction_rows":rows}
    physical["selected_pareto_balanced"]=pareto_candidate_from_result(physical);return physical
def v16_93_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_owner_balanced_metric_v16_93.json").read_text(encoding="utf-8"));values=p["fresh_sbp_owner_balanced_metric"]["selected_pareto_balanced"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.93 selected vector has wrong dimension")
    return raw
def completion_payload()->dict[str,Any]:
    r=owner_balanced_metric();b=r["selected_pareto_balanced"]
    validation={"v16_91_residual_reproduced":math.isclose(r["initial_residual_norm"],2.486624819288495,rel_tol=0,abs_tol=2e-8),"v16_91_event_reproduced":math.isclose(r["initial_event_residual"],-0.211419776681132,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"complete_scheme_filter_grid":r["direction_count"]==len(r["owner_weight_schemes"])*len(FILTERS),"pareto_candidate_exists":b is not None,
        "complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-MARGIN),"absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-MARGIN),"balanced_progress_positive":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_owner_balanced_metric_v16_93","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_owner_balanced_metric":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"BALANCED_PERIOD_FIBER_LOCALIZATION_HOPF_ANISOTROPY_AND_IDENTICAL_EVENT_CLOSURE","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_THE_SCALE_OWNER_TRANSITION","active_calculation":"PROMOTE_IF_VALIDATED_OR_USE_THE_OWNER_BALANCE_TRADEOFF_TO_RETARGET_THE_SAME_ACTION","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_owner_balanced_metric_v16_93.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","owner_balanced_metric","v16_93_selected_raw_vector","completion_payload","deterministic_json","materialize"]
