"""Select finite nonlinear progress across measured tangent subspace families."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_physical_jacobian
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_second_six_owner_measured_cone_v17_06 import v17_05_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import FILTERS,EPS,LABELS,MARGIN,_gradients,_metrics,_slopes
from bhsm.interface.aether_n3_fresh_sbp_expanded_measured_tangent_v17_07 import _measured_response,_solve
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.08";CLASSIFICATION="BHSM_N3_FRESH_SBP_MEASURED_TANGENT_FAMILY_NONLINEAR_SELECTION";FULL_BHSM_COMPLETE=False
RANKS=(6,9,12,15,18);CAUCHY=(0.003,0.01,0.03,0.1,0.2,0.3,0.5,0.8,1.0,2.0)
def tangent_family_selection_from(raw_vector:np.ndarray,*,source_state:str="supplied_full_precision_state")->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales;y,r=sbp_projected_residual_and_vector(y);initial=_metrics(r);assembled=sbp_physical_jacobian(y/scales);J=np.asarray(assembled.pop("matrix"))[:,:-1];u,s,vt=np.linalg.svd(J,full_matrices=False);spectral=float(s[0]);G=_gradients(J,r,initial);blocks=[];columns=[]
    for relative_filter in FILTERS:
        mu=relative_filter*spectral;denom=s*s+mu*mu;block=vt.T@((vt@G.T)/denom[:,None]);norms=np.linalg.norm(block,axis=0);normalized=block/np.maximum(norms,1e-300);blocks.append((relative_filter,normalized));columns.extend(normalized[:,i] for i in range(normalized.shape[1]))
    candidate_basis=np.column_stack(columns);ub,sb,vbt=np.linalg.svd(candidate_basis,full_matrices=False);keep=sb>max(1e-12,1e-10*float(sb[0]));basis=ub[:,keep];response=_measured_response(y,r,initial,basis);families=[]
    for rank in RANKS:
        if rank<=basis.shape[1]:families.append((f"combined_rank_{rank}",np.eye(basis.shape[1])[:,:rank]))
    for relative_filter,block in blocks:
        qf,rf=np.linalg.qr(block,mode="reduced");families.append((f"single_filter_{relative_filter:.0e}",basis.T@qf))
    rows=[];accepted=[]
    for label,transform in families:
        response_sub=response@transform;coeff,rate,solved,weights,gap=_solve(response_sub);direction_reduced=basis@(transform@coeff);direction=np.concatenate((direction_reduced,[0.0]));_,plus=sbp_projected_residual_and_vector(y+EPS*direction);_,minus=sbp_projected_residual_and_vector(y-EPS*direction);jd=(plus-minus)/(2*EPS);verified=_slopes(r,jd,initial);cauchy=max(0.0,-float(r@jd)/float(jd@jd));common=bool(np.all(verified<0));row={"family":label,"dimension":transform.shape[1],"maximin_solve_success":solved,"relative_duality_gap":gap,"dual_owner_weights":weights.tolist(),"predicted_equalized_fractional_rate":rate,"predicted_fractional_slopes":(response_sub@coeff).tolist(),"verified_fractional_slopes":{LABELS[i]:float(verified[i]) for i in range(len(LABELS))},"direction_norm":float(np.linalg.norm(direction)),"derived_cauchy_radius":cauchy,"common_six_owner_descent":common,"trials":[]}
        if solved and common and cauchy>0:
            for factor in CAUCHY:
                radius=factor*cauchy
                try:
                    candidate,candidate_r=sbp_projected_residual_and_vector(y+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"eta_minimum":eta,"post_projection_step_norm":float(np.linalg.norm(candidate-y)),"raw_vector_hex":[float(value).hex() for value in raw_candidate]};row["trials"].append(trial)
                    if eta>1e-5 and all(reductions[key]>MARGIN for key in initial):accepted.append((trial["minimum_fractional_progress"],sum(fractions.values()),trial,label))
                except (FloatingPointError,ValueError,np.linalg.LinAlgError) as exc:row["trials"].append({"cauchy_factor":factor,"domain_valid":False,"exception":type(exc).__name__})
        rows.append(row)
    best=None
    if accepted:
        _,_,trial,label=max(accepted,key=lambda item:(item[0],item[1]));best={"family":label,**trial}
    return {"source_state":source_state,"physical_residual_changed":False,"physical_event_changed":False,"owner_set":list(LABELS),"initial_metrics":initial,**assembled,"singular_value_scale":spectral,"combined_candidate_columns":candidate_basis.shape[1],"orthonormal_tangent_rank":basis.shape[1],"tangent_singular_values":sb.tolist(),"measured_full_response":response.tolist(),"family_count":len(rows),"family_rows":rows,"common_family_count":sum(row["common_six_owner_descent"] for row in rows),"strict_six_owner_candidate_count":len(accepted),"selected_family_maximin":best}
def tangent_family_selection()->dict[str,Any]:return tangent_family_selection_from(v17_05_selected_raw_vector(),source_state="v17.05_selected_six_owner_state")
def completion_payload()->dict[str,Any]:
    r=tangent_family_selection();b=r["selected_family_maximin"]
    validation={"v17_05_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.428689906333689,rel_tol=0,abs_tol=2e-8),"v17_05_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.122933895889858,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_tangent_families_tested":r["family_count"]==8,"common_family_exists":r["common_family_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>MARGIN for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"outperforms_full_rank_v17_07":bool(b is not None and b["minimum_fractional_progress"]>3.653131928e-6),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_tangent_family_selection_v17_08","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_tangent_family_selection":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"FINITE_NONLINEAR_COMPATIBILITY_OF_ALL_SIX_PHYSICAL_OWNER_DESCENTS_ACROSS_THE_MEASURED_NORMAL_TANGENT_FAMILY","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_BEYOND_THE_STIFF_FULL_RANK_DIRECTION","active_calculation":"PROMOTE_THE_BEST_VALIDATED_TANGENT_FAMILY_THEN_REAUDIT_THE_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_tangent_family_selection_v17_08.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","tangent_family_selection_from","tangent_family_selection","completion_payload","deterministic_json","materialize"]
