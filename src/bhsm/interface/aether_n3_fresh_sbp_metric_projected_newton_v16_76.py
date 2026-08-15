"""Gauss--Newton-metric projection into the actual-event descent half-space."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector,sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_refined_damped_cone_v16_73 import FILTER_RELATIVE_SCALES,CONE_FACTORS,CAUCHY_FACTORS
from bhsm.interface.aether_n3_fresh_sbp_post_refined_block_audit_v16_75 import v16_74_selected_raw_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v16.76";CLASSIFICATION="BHSM_N3_FRESH_SBP_GAUSS_NEWTON_METRIC_ACTUAL_EVENT_PROJECTION";FULL_BHSM_COMPLETE=False
DIRECTIONAL_EPSILON=3e-6;MARGIN=1e-10

def metric_projected_newton_from(
    raw_vector:np.ndarray, *,
    filter_relative_scales:tuple[float,...]=FILTER_RELATIVE_SCALES,
    cone_factors:tuple[float,...]=CONE_FACTORS,
    cauchy_factors:tuple[float,...]=CAUCHY_FACTORS,
)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,residual=sbp_projected_residual_and_vector(y)
    assembled=sbp_physical_jacobian(y/scales);matrix=np.asarray(assembled.pop("matrix"));reduced_matrix=matrix[:,:-1]
    u,s,vt=np.linalg.svd(reduced_matrix,full_matrices=False);spectral_scale=float(s[0]);coefficients=u.T@residual
    event_gradient=sbp_event_covector((y/scales)[:-1])/scales[:-1]/scales[-1]
    event=float(residual[-1]);absolute_event_gradient=math.copysign(1.0,event)*event_gradient
    initial=float(np.linalg.norm(residual));directions=[];accepted=[]
    for relative_filter in filter_relative_scales:
        mu=relative_filter*spectral_scale;denominator=s*s+mu*mu
        base_reduced=-(vt.T@(s/denominator*coefficients))
        metric_inverse_event=vt.T@((vt@absolute_event_gradient)/denominator)
        metric_event_norm=float(absolute_event_gradient@metric_inverse_event)
        base_event_slope=float(absolute_event_gradient@base_reduced)
        boundary_alpha=max(0.0,base_event_slope/metric_event_norm)
        for cone_factor in cone_factors:
            alpha=cone_factor*boundary_alpha
            corrected_reduced=base_reduced-alpha*metric_inverse_event
            corrected=np.concatenate((corrected_reduced,[0.0]));norm=float(np.linalg.norm(corrected))
            if norm==0.0:continue
            direction=corrected/norm
            try:
                _,plus_r=sbp_projected_residual_and_vector(y+DIRECTIONAL_EPSILON*direction)
                _,minus_r=sbp_projected_residual_and_vector(y-DIRECTIONAL_EPSILON*direction)
            except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:
                directions.append({"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","cone_factor":cone_factor,
                    "direction_domain_valid":False,"exception":type(exc).__name__,"common_descent_direction":False,"trials":[]});continue
            jd=(plus_r-minus_r)/(2*DIRECTIONAL_EPSILON);total_slope=float(residual@jd)
            event_slope=float((plus_r[-1]-minus_r[-1])/(2*DIRECTIONAL_EPSILON));absolute_event_slope=math.copysign(1.0,event)*event_slope
            jd_norm=float(np.linalg.norm(jd));cauchy=max(0.0,-total_slope/jd_norm**2)
            row={"relative_filter_scale":relative_filter,"relative_filter_scale_label":f"{relative_filter:.0e}","absolute_filter_scale":mu,
                "unrestricted_reduced_direction_norm":float(np.linalg.norm(base_reduced)),"base_absolute_event_linear_slope":base_event_slope,
                "metric_event_covector_norm_squared":metric_event_norm,"cone_factor":cone_factor,"metric_halfspace_alpha":alpha,
                "corrected_direction_norm":norm,"measured_total_merit_slope":total_slope,"measured_absolute_event_slope":absolute_event_slope,
                "derived_cauchy_radius":cauchy,"common_descent_direction":bool(total_slope<0 and absolute_event_slope<0),"trials":[]}
            if row["common_descent_direction"] and cauchy>0:
                for factor in cauchy_factors:
                    radius=factor*cauchy
                    try:
                        candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales
                        eta=_minimum_node_eta(raw_candidate);candidate_norm=float(np.linalg.norm(candidate_r));candidate_event=float(candidate_r[-1])
                        trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"residual_norm":candidate_norm,
                            "residual_reduction":initial-candidate_norm,"event_residual":candidate_event,"absolute_event_reduction":abs(event)-abs(candidate_event),
                            "eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(v).hex() for v in raw_candidate]}
                        row["trials"].append(trial)
                        if eta>1e-5 and candidate_norm<initial-MARGIN and abs(candidate_event)<abs(event)-MARGIN:accepted.append((candidate_norm,trial,relative_filter,cone_factor))
                    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:
                        row["trials"].append({"cauchy_factor":factor,"trust_radius":radius,"domain_valid":False,"exception":type(exc).__name__})
            directions.append(row)
    best=None
    if accepted:
        candidate_norm,trial,relative_filter,cone_factor=min(accepted,key=lambda item:item[0]);best={"relative_filter_scale":relative_filter,
            "relative_filter_scale_label":f"{relative_filter:.0e}","cone_factor":cone_factor,**trial,"residual_norm":candidate_norm}
    ranks={f"relative_{cutoff:.0e}":int(np.sum(s>cutoff*spectral_scale)) for cutoff in (1e-8,1e-10,1e-12,1e-14)}
    return {"source_state":"v16.74_selected_refined_common_cone_state","projection_metric":"DAMPED_GAUSS_NEWTON_NORMAL_METRIC_ON_375_PHYSICAL_BASE_VARIABLES",
        "event_multiplier_input_direction_fixed":True,"initial_residual_norm":initial,"initial_event_residual":event,**assembled,
        "singular_value_scale":spectral_scale,"smallest_singular_value":float(s[-1]),"numerical_ranks":ranks,"direction_count":len(directions),
        "common_descent_direction_count":sum(row["common_descent_direction"] for row in directions),"strict_joint_candidate_count":len(accepted),
        "direction_rows":directions,"selected_best_accepted":best}

def metric_projected_newton()->dict[str,Any]:return metric_projected_newton_from(v16_74_selected_raw_vector())
def completion_payload()->dict[str,Any]:
    r=metric_projected_newton();b=r["selected_best_accepted"]
    validation={"v16_74_residual_reproduced":math.isclose(r["initial_residual_norm"],14.803880474835667,rel_tol=0,abs_tol=2e-8),
        "v16_74_event_reproduced":math.isclose(r["initial_event_residual"],-0.31374183936204,rel_tol=0,abs_tol=2e-8),
        "all_metric_directions_probed":r["direction_count"]==len(FILTER_RELATIVE_SCALES)*len(CONE_FACTORS),
        "common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,
        "complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-MARGIN),
        "absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-MARGIN),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_metric_projected_newton_v16_76","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"fresh_sbp_metric_projected_newton":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"NORMAL_METRIC_CLOSEST_KKT_CORRECTION_COMPATIBLE_WITH_DESCENT_OF_THE_IDENTICAL_ACTUAL_SOFT_EVENT",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_THE_METRIC_PROJECTED_STATE_IF_VALIDATED_OR_USE_ITS_MEASURED_DEFECT_TO_REDIRECT_WITHIN_THE_SAME_ORBIT",
        "validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_metric_projected_newton_v16_76.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","metric_projected_newton_from","metric_projected_newton","completion_payload","deterministic_json","materialize"]
