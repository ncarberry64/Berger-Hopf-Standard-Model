"""Second direct fresh-Jacobian Pareto-balanced refresh from v16.90."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_event_balanced_metric_v16_87 import event_balanced_metric_from
from bhsm.interface.aether_n3_fresh_sbp_pareto_balanced_selection_v16_89 import pareto_candidate_from_result
from bhsm.interface.aether_n3_fresh_sbp_refreshed_pareto_balance_v16_90 import selected_raw_vector_v16_90
VERSION="v16.91";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_REFRESHED_EVENT_BALANCED_PARETO_PROMOTION";FULL_BHSM_COMPLETE=False
def second_refreshed_pareto()->dict[str,Any]:
    physical=event_balanced_metric_from(selected_raw_vector_v16_90());selected=pareto_candidate_from_result(physical)
    return {"source_state":"v16.90_refreshed_pareto_state","physical_event_balanced_rays":physical,"selection_rule":"maximize_minimum_fractional_progress_of_original_complete_residual_and_original_absolute_event","selected_pareto_balanced":selected}
def completion_payload()->dict[str,Any]:
    r=second_refreshed_pareto();p=r["physical_event_balanced_rays"];b=r["selected_pareto_balanced"]
    validation={"v16_90_residual_reproduced":math.isclose(p["initial_residual_norm"],2.537677943552421,rel_tol=0,abs_tol=2e-8),"v16_90_event_reproduced":math.isclose(p["initial_event_residual"],-0.213770703575521,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not p["physical_residual_changed"] and not p["physical_event_changed"],
        "pareto_candidate_exists":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<p["initial_residual_norm"]-1e-10),"absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(p["initial_event_residual"])-1e-10),
        "balanced_progress_positive":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_refreshed_pareto_v16_91","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_second_refreshed_pareto":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"CONTINUED_FRESH_JACOBIAN_NONNEGLECTED_PROGRESS_OF_PARENT_STATIONARITY_AND_THE_IDENTICAL_ACTUAL_EVENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_NEW_PHYSICAL_BLOCKS_AND_SOFT_SPECTRUM","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_second_refreshed_pareto_v16_91.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","second_refreshed_pareto","completion_payload","deterministic_json","materialize"]
