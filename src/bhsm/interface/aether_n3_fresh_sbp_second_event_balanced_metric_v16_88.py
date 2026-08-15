"""Second event-balanced Gauss--Newton refresh from v16.87."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_event_balanced_metric_v16_87 import event_balanced_metric_from
VERSION="v16.88";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_EVENT_BALANCED_GAUSS_NEWTON_PRECONDITIONER";FULL_BHSM_COMPLETE=False
def v16_87_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_event_balanced_metric_v16_87.json").read_text(encoding="utf-8"));values=p["fresh_sbp_event_balanced_metric"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.87 selected vector has wrong dimension")
    return raw
def second_event_balanced_metric()->dict[str,Any]:return event_balanced_metric_from(v16_87_selected_raw_vector())
def completion_payload()->dict[str,Any]:
    r=second_event_balanced_metric();b=r["selected_best_accepted"]
    validation={"v16_87_residual_reproduced":math.isclose(r["initial_residual_norm"],2.655341904647002,rel_tol=0,abs_tol=2e-8),"v16_87_event_reproduced":math.isclose(r["initial_event_residual"],-0.233834619167092,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],
        "common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),"absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-1e-10),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_event_balanced_metric_v16_88","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_second_event_balanced_metric":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"PERSISTENCE_OF_BALANCED_PARENT_ORBIT_AND_IDENTICAL_ACTUAL_EVENT_CLOSURE_UNDER_A_FRESH_PHYSICAL_JACOBIAN","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_IF_STRICT_JOINT_THEN_REASSESS_THE_EVENT_STATIONARITY_BALANCE","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_second_event_balanced_metric_v16_88.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_87_selected_raw_vector","second_event_balanced_metric","completion_payload","deterministic_json","materialize"]
