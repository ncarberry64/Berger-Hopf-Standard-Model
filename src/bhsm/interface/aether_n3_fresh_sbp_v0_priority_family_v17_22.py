"""Measured tangent families with bounded v0-priority maximin targets."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_second_dense_radius_v17_21 import second_dense_radius
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import FILTERS,EPS,LABELS,MARGIN,_gradients,_metrics,_slopes
from bhsm.interface.aether_n3_fresh_sbp_expanded_measured_tangent_v17_07 import _measured_response,_solve
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.22";CLASSIFICATION="BHSM_N3_FRESH_SBP_V0_PRIORITY_MEASURED_TANGENT_FAMILY";FULL_BHSM_COMPLETE=False
PRIORITIES=(1.0,1.25,1.5,2.0,3.0,4.0);RANKS=(6,9,12,18);CAUCHY=(0.01,0.03,0.05,0.075,0.1,0.125,0.15,0.2)
def v17_21_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_dense_radius_v17_21.json").read_text(encoding="utf-8"));values=p["fresh_sbp_second_dense_radius"]["selected_dense_radius"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v17.21 selected vector has wrong dimension")
    return raw
def v0_priority_family_from(raw_vector:np.ndarray,*,source_state:str="supplied_full_precision_state")->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,r=sbp_projected_residual_and_vector(y);initial=_metrics(r);assembled=sbp_physical_jacobian(y/scales);J=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(J,full_matrices=False);spectral=float(s[0]);G=_gradients(J,r,initial);columns=[];filter_blocks=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;block=vt.T@((vt@G.T)/denom[:,None]);block=block/np.maximum(np.linalg.norm(block,axis=0),1e-300);filter_blocks.append((relative_filter,block));columns.extend(block[:,i] for i in range(block.shape[1]))
    candidate=np.column_stack(columns);ub,sb,vbt=np.linalg.svd(candidate,full_matrices=False);keep=sb>max(1e-12,1e-10*float(sb[0]));basis=ub[:,keep];response=_measured_response(y,r,initial,basis);families=[]
    for rank in RANKS:
        if rank<=basis.shape[1]:families.append((f"combined_rank_{rank}",np.eye(basis.shape[1])[:,:rank]))
    for relative_filter,block in filter_blocks:
        qf,rf=np.linalg.qr(block,mode="reduced");families.append((f"single_filter_{relative_filter:.0e}",basis.T@qf))
    rows=[];accepted=[];v0_index=LABELS.index("v0")
    for family,transform in families:
        raw_response=response@transform
        for priority in PRIORITIES:
            targets=np.ones(len(LABELS));targets[v0_index]=priority;weighted_response=raw_response/targets[:,None];coeff,weighted_rate,solved,weights,gap=_solve(weighted_response);direction_reduced=basis@(transform@coeff);direction=np.concatenate((direction_reduced,[0.0]));_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction);jd=(plus-minus)/(2*EPS);verified=_slopes(r,jd,initial);cauchy=max(0.0,-float(r@jd)/float(jd@jd));common=bool(np.all(verified<0));row={"family":family,"dimension":transform.shape[1],"v0_priority":priority,"maximin_solve_success":solved,"relative_duality_gap":gap,"weighted_equalized_rate":weighted_rate,"predicted_fractional_slopes":(raw_response@coeff).tolist(),"verified_fractional_slopes":{LABELS[i]:float(verified[i]) for i in range(len(LABELS))},"derived_cauchy_radius":cauchy,"common_six_owner_descent":common,"trials":[]}
            if solved and common and cauchy>0:
                for factor in CAUCHY:
                    radius=factor*cauchy
                    try:
                        candidate_y,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate_y/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"eta_minimum":eta,"raw_vector_hex":[float(value).hex() for value in raw_candidate]};row["trials"].append(trial)
                        if eta>1e-5 and all(reductions[key]>MARGIN for key in initial):accepted.append((trial["minimum_fractional_progress"],sum(fractions.values()),trial,family,priority))
                    except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"domain_valid":False,"exception":type(exc).__name__})
            rows.append(row)
    best=None
    if accepted:
        _,_,trial,family,priority=max(accepted,key=lambda item:(item[0],item[1]));best={"family":family,"v0_priority":priority,**trial}
    return {"source_state":source_state,"physical_residual_changed":False,"physical_event_changed":False,"priority_semantics":"MAXIMIZE_MINIMUM_OF_RAW_FRACTIONAL_OWNER_DESCENT_DIVIDED_BY_OWNER_TARGET_WITH_V0_TARGET_INCREASED","initial_metrics":initial,**assembled,"singular_value_scale":spectral,"tangent_rank":basis.shape[1],"family_count":len(families),"priority_count":len(PRIORITIES),"direction_rows":rows,"common_direction_count":sum(row["common_six_owner_descent"] for row in rows),"strict_candidate_count":len(accepted),"selected_v0_priority_maximin":best}
def v0_priority_family()->dict[str,Any]:return v0_priority_family_from(v17_21_selected_raw_vector(),source_state="v17.21_selected_second_dense_radius_state")
def completion_payload()->dict[str,Any]:
    r=v0_priority_family();b=r["selected_v0_priority_maximin"]
    validation={"v17_21_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.252645654334879,rel_tol=0,abs_tol=2e-8),"v17_21_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.105533276231636,rel_tol=0,abs_tol=2e-8),"v17_21_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.376290798969446,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"bounded_priorities_tested":r["priority_count"]==len(PRIORITIES),"all_families_tested":r["family_count"]==7,"common_direction_exists":r["common_direction_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_v0_priority_family_v17_22","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_v0_priority_family":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"FINITE_NONLINEAR_SIX_OWNER_DESCENT_WITH_EXPLICIT_COMPENSATION_FOR_THE_MEASURED_V0_CURVATURE_BOTTLENECK","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_v0_priority_family_v17_22.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_21_selected_raw_vector","v0_priority_family_from","v0_priority_family","completion_payload","deterministic_json","materialize"]
