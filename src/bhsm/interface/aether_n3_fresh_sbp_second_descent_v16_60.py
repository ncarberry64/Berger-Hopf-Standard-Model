"""Second exact physical descent of the fresh SBP N=3 event KKT."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_descent_from
VERSION="v16.60";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_COVECTOR_CONSISTENT_PHYSICAL_DESCENT";FULL_BHSM_COMPLETE=False
def v16_59_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_first_descent_v16_59.json").read_text(encoding="utf-8"));values=p["fresh_sbp_first_descent"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values]);
    if raw.shape!=(376,):raise ValueError("v16.59 vector has wrong dimension")
    return raw
def second_sbp_descent()->dict[str,Any]:return sbp_descent_from(v16_59_raw_vector())
def completion_payload()->dict[str,Any]:
    r=second_sbp_descent();b=r["best_accepted"]
    validation={"accepted_v16_59_residual_reproduced":math.isclose(r["initial_residual_norm"],43.17476935389932,rel_tol=0,abs_tol=2e-8),
        "measured_direction_is_descent":r["measured_projected_slope"]<0,"positive_cauchy_radius":r["derived_cauchy_radius"]>0,
        "strict_step_accepted":b is not None,"complete_residual_reduced":bool(b is not None and b["residual_norm"]<r["initial_residual_norm"]-1e-10),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_descent_v16_60","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_second_descent":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"SECOND_JOINT_STATIONARITY_DESCENT_OF_THE_VARIATIONALLY_CONSISTENT_FRESH_N3_PARENT_EVENT_ORBIT",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"REFRESH_AND_CONTINUE_THE_SAME_FRESH_SBP_JOINT_SOLVE","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_second_descent_v16_60.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_59_raw_vector","second_sbp_descent","completion_payload","deterministic_json","materialize"]
