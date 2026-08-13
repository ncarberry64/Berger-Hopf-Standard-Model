"""Fourth common total-merit/event descent cone from v16.67."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_common_descent_cone_v16_65 import common_descent_cone_from
VERSION="v16.68";CLASSIFICATION="BHSM_N3_FRESH_SBP_FOURTH_COMMON_TOTAL_EVENT_DESCENT_CONE";FULL_BHSM_COMPLETE=False
def v16_67_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_third_common_cone_v16_67.json").read_text(encoding="utf-8"));values=p["fresh_sbp_third_common_descent_cone"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values]);
    if raw.shape!=(376,):raise ValueError("v16.67 selected vector has wrong dimension")
    return raw
def fourth_common_cone()->dict[str,Any]:return common_descent_cone_from(v16_67_selected_raw_vector())
def completion_payload()->dict[str,Any]:
    r=fourth_common_cone();b=r["selected_best_accepted"]
    validation={"v16_67_residual_reproduced":math.isclose(r["initial_residual_norm"],32.84923863946645,rel_tol=0,abs_tol=2e-8),
        "v16_67_event_reproduced":math.isclose(r["initial_event_residual"],0.352855690367092,rel_tol=0,abs_tol=2e-8),
        "common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,
        "complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),
        "absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-1e-10),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_fourth_common_cone_v16_68","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_fourth_common_descent_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"FOURTH_FRESH_TEST_OF_THE_COMMON_PARENT_STATIONARITY_AND_ACTUAL_EVENT_DESCENT_CONE",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"AUDIT_THE_POST_CONE_SBP_BLOCKS_AND_CONTINUE_OR_REDIRECT_TO_THEIR_UPSTREAM_OWNER",
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_fourth_common_cone_v16_68.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_67_selected_raw_vector","fourth_common_cone","completion_payload","deterministic_json","materialize"]
