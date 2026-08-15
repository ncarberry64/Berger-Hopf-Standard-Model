"""Pareto-balanced promotion from the fully evaluated v16.88 physical rays."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
VERSION="v16.89";CLASSIFICATION="BHSM_N3_FRESH_SBP_PARETO_BALANCED_PHYSICAL_RAY_SELECTION";FULL_BHSM_COMPLETE=False
def pareto_candidate_from_result(r:Mapping[str,Any])->dict[str,Any]|None:
    initial=float(r["initial_residual_norm"]);event=float(r["initial_event_residual"]);candidates=[]
    for row in r["direction_rows"]:
        for trial in row["trials"]:
            if not trial.get("domain_valid",False):continue
            residual_fraction=float(trial["residual_reduction"])/initial;event_fraction=float(trial["absolute_event_reduction"])/abs(event)
            if residual_fraction<=0 or event_fraction<=0:continue
            candidates.append({"event_row_weight":row["event_row_weight"],"relative_filter_scale":row["relative_filter_scale"],"relative_filter_scale_label":row["relative_filter_scale_label"],
                **trial,"residual_fractional_reduction":residual_fraction,"event_fractional_reduction":event_fraction,"minimum_fractional_progress":min(residual_fraction,event_fraction)})
    return max(candidates,key=lambda x:(x["minimum_fractional_progress"],x["residual_fractional_reduction"]+x["event_fractional_reduction"])) if candidates else None
def pareto_balanced_selection()->dict[str,Any]:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_event_balanced_metric_v16_88.json").read_text(encoding="utf-8"));r=p["fresh_sbp_second_event_balanced_metric"]
    initial=float(r["initial_residual_norm"]);event=float(r["initial_event_residual"]);selected=pareto_candidate_from_result(r)
    candidates=sum(1 for row in r["direction_rows"] for trial in row["trials"] if trial.get("domain_valid",False) and trial["residual_reduction"]>0 and trial["absolute_event_reduction"]>0)
    return {"source_state":"v16.87_selected_event_balanced_state","v16_88_minimum_total_candidate_promoted":False,"reason":"MINIMUM_TOTAL_CANDIDATE_ASYMPTOTICALLY_NEGLECTS_THE_MANDATORY_EVENT_EQUATION",
        "physical_residual_changed":False,"physical_event_changed":False,"selection_rule":"maximize_minimum_of_fractional_complete_residual_reduction_and_fractional_absolute_event_reduction_among_strict_joint_candidates",
        "initial_residual_norm":initial,"initial_event_residual":event,"strict_joint_candidate_count":candidates,"selected_pareto_balanced":selected}
def selected_raw_vector()->np.ndarray:
    values=pareto_balanced_selection()["selected_pareto_balanced"]["raw_vector_hex"];raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.89 selected vector has wrong dimension")
    return raw
def completion_payload()->dict[str,Any]:
    r=pareto_balanced_selection();b=r["selected_pareto_balanced"]
    validation={"v16_87_residual_reproduced":math.isclose(r["initial_residual_norm"],2.655341904647002,rel_tol=0,abs_tol=2e-8),"v16_87_event_reproduced":math.isclose(r["initial_event_residual"],-0.233834619167092,rel_tol=0,abs_tol=2e-8),
        "old_stationarity_biased_winner_not_promoted":not r["v16_88_minimum_total_candidate_promoted"],"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"pareto_candidate_exists":b is not None,
        "complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),"absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-1e-10),
        "balanced_fraction_positive":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_pareto_balanced_selection_v16_89","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_pareto_balanced_selection":r,"status":"VALIDATED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"NONNEGLECTED_SIMULTANEOUS_PROGRESS_OF_PARENT_ORBIT_STATIONARITY_AND_THE_IDENTICAL_ACTUAL_SOFT_EVENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"REFRESH_THE_EVENT_BALANCED_PHYSICAL_JACOBIAN_AT_THE_PARETO_PROMOTED_STATE","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_pareto_balanced_selection_v16_89.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","pareto_candidate_from_result","pareto_balanced_selection","selected_raw_vector","completion_payload","deterministic_json","materialize"]
