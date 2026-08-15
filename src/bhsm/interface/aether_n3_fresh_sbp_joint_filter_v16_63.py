"""Fresh SBP continuation requiring complete-residual and actual-event descent."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_descent_from
VERSION="v16.63";CLASSIFICATION="BHSM_N3_FRESH_SBP_STRICT_JOINT_EVENT_FILTER_CONTINUATION";FULL_BHSM_COMPLETE=False
def v16_62_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_fourth_descent_v16_62.json").read_text(encoding="utf-8"));values=p["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values]);
    if raw.shape!=(376,):raise ValueError("v16.62 selected vector has wrong dimension")
    return raw
def joint_filter_continuation()->dict[str,Any]:return sbp_descent_from(v16_62_selected_raw_vector(),retain_trial_vectors=True,joint_filter=True)
def completion_payload()->dict[str,Any]:
    r=joint_filter_continuation();minimum=r["best_accepted"];selected=r["best_joint_filter_accepted"]
    validation={"selected_v16_62_residual_reproduced":math.isclose(r["initial_residual_norm"],39.777540884049806,rel_tol=0,abs_tol=2e-8),
        "selected_v16_62_event_reproduced":math.isclose(r["initial_event_residual"],-0.592193260921461,rel_tol=0,abs_tol=2e-8),
        "measured_direction_is_descent":r["measured_projected_slope"]<0,"positive_cauchy_radius":r["derived_cauchy_radius"]>0,
        "strict_joint_step_accepted":selected is not None,
        "complete_residual_reduced":bool(selected is not None and selected["residual_norm"]<r["initial_residual_norm"]-1e-10),
        "actual_event_magnitude_reduced":bool(selected is not None and abs(selected["event_residual"])<abs(r["initial_event_residual"])-1e-10),
        "eta_domain_preserved":bool(selected is not None and selected["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(selected is not None and len(selected["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_joint_filter_v16_63","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_joint_filter_continuation":r,"minimum_total_candidate":minimum,"selected_best_accepted":selected,
        "selection_rule":"MINIMUM_COMPLETE_RESIDUAL_AMONG_STRICT_STEPS_THAT_ALSO_REDUCE_THE_ABSOLUTE_ACTUAL_EVENT_RESIDUAL",
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"SIMULTANEOUS_PARENT_STATIONARITY_AND_ACTUAL_EULER_DIRAC_EVENT_DESCENT_ON_THE_FRESH_SBP_ORBIT",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"REFRESH_AND_REPEAT_THE_STRICT_JOINT_FILTER_OR_REDIRECT_IF_NO_COMMON_DESCENT_EXISTS",
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_joint_filter_v16_63.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_62_selected_raw_vector","joint_filter_continuation","completion_payload","deterministic_json","materialize"]
