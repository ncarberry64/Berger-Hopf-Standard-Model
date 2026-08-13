"""Refined small-radius damped common cone from v16.71."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_damped_newton_cone_v16_70 import damped_newton_common_cone_from
VERSION="v16.73";CLASSIFICATION="BHSM_N3_FRESH_SBP_REFINED_SMALL_RADIUS_DAMPED_COMMON_CONE";FULL_BHSM_COMPLETE=False
FILTER_RELATIVE_SCALES=(1e-6,1e-4);CONE_FACTORS=(1.1,2.0);CAUCHY_FACTORS=(1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1)
def v16_71_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_damped_newton_cone_v16_71.json").read_text(encoding="utf-8"));values=p["fresh_sbp_second_damped_newton_common_cone"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values]);
    if raw.shape!=(376,):raise ValueError("v16.71 selected vector has wrong dimension")
    return raw
def refined_damped_cone()->dict[str,Any]:return damped_newton_common_cone_from(v16_71_selected_raw_vector(),filter_relative_scales=FILTER_RELATIVE_SCALES,cone_factors=CONE_FACTORS,cauchy_factors=CAUCHY_FACTORS)
def completion_payload()->dict[str,Any]:
    r=refined_damped_cone();b=r["selected_best_accepted"]
    validation={"v16_71_residual_reproduced":math.isclose(r["initial_residual_norm"],15.380754137909294,rel_tol=0,abs_tol=2e-8),
        "v16_71_event_reproduced":math.isclose(r["initial_event_residual"],-0.31430136337983,rel_tol=0,abs_tol=2e-8),
        "refined_grid_probed":r["direction_count"]==len(FILTER_RELATIVE_SCALES)*len(CONE_FACTORS),
        "common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,
        "complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),
        "absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-1e-10),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_refined_damped_cone_v16_73","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_refined_damped_common_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"SMALL_RADIUS_COMMON_DESCENT_OF_PARENT_STATIONARITY_AND_THE_ACTUAL_EVENT_IN_THE_NEW_HIGH_ETA_BASIN",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"PROMOTE_THE_REFINED_COMMON_STEP_OR_REDIRECT_TO_THE_NEXT_MEASURED_UPSTREAM_DEFECT",
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_refined_damped_cone_v16_73.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","FILTER_RELATIVE_SCALES","CONE_FACTORS","CAUCHY_FACTORS","v16_71_selected_raw_vector","refined_damped_cone","completion_payload","deterministic_json","materialize"]
