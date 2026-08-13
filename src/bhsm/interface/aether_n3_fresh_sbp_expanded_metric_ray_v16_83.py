"""Expanded exact nonlinear ray from the v16.81 metric-projected state."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_metric_projected_newton_v16_76 import metric_projected_newton_from
from bhsm.interface.aether_n3_fresh_sbp_post_metric_block_audit_v16_82 import v16_81_selected_raw_vector
VERSION="v16.83";CLASSIFICATION="BHSM_N3_FRESH_SBP_EXPANDED_GAUSS_NEWTON_METRIC_RAY";FULL_BHSM_COMPLETE=False
FILTERS=(1e-6,1e-4);CONES=(1.1,2.0);CAUCHY=(0.03,0.1,0.3,1.0,3.0)
def expanded_metric_ray()->dict[str,Any]:return metric_projected_newton_from(v16_81_selected_raw_vector(),filter_relative_scales=FILTERS,cone_factors=CONES,cauchy_factors=CAUCHY)
def completion_payload()->dict[str,Any]:
    r=expanded_metric_ray();b=r["selected_best_accepted"]
    validation={"v16_81_residual_reproduced":math.isclose(r["initial_residual_norm"],10.539813695735257,rel_tol=0,abs_tol=2e-8),"v16_81_event_reproduced":math.isclose(r["initial_event_residual"],-0.295377155257419,rel_tol=0,abs_tol=2e-8),
        "expanded_beyond_old_edge":max(CAUCHY)>0.1,"common_direction_exists":r["common_descent_direction_count"]>0,"strict_joint_candidate_exists":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),
        "absolute_event_reduced":bool(b is not None and abs(b["event_residual"])<abs(r["initial_event_residual"])-1e-10),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_expanded_metric_ray_v16_83","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_expanded_metric_ray":r,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"NONLINEAR_TRUST_EXTENT_OF_THE_SAME_NORMAL_METRIC_CORRECTION_FOR_OPEN_ORBIT_AND_ACTUAL_EVENT_STATIONARITY",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION","active_calculation":"PROMOTE_THE_BEST_STRICT_JOINT_EXPANDED_RAY_OR_TARGET_THE_MEASURED_LATE_ORBIT_BLOCK","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_expanded_metric_ray_v16_83.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","FILTERS","CONES","CAUCHY","expanded_metric_ray","completion_payload","deterministic_json","materialize"]
