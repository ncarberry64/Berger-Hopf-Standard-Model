"""Three-refresh covector-consistent N=3 continuation from v16.54."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_covector_consistent_curvature_v16_53 import covector_consistent_continuation_from

VERSION="v16.55"
CLASSIFICATION="BHSM_N3_COVECTOR_CONSISTENT_CURVATURE_MULTIREFRESH_CONTINUATION"
FULL_BHSM_COMPLETE=False
ITERATIONS=3

def v16_54_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_second_covector_consistent_curvature_v16_54.json").read_text(encoding="utf-8"))
    values=payload["second_covector_consistent_curvature_continuation"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.54 vector has wrong dimension")
    return raw

def multirefresh_continuation()->dict[str,Any]:
    raw=v16_54_raw_vector();rows=[];initial=None;termination="ITERATION_LIMIT"
    for iteration in range(1,ITERATIONS+1):
        result=covector_consistent_continuation_from(raw);best=result["best_accepted"]
        if initial is None:initial=result["initial_residual_norm"]
        row={"iteration":iteration,"initial_residual_norm":result["initial_residual_norm"],
             "curvature_norm":result["curvature_audit"]["raw_norm"],
             "curvature_asymmetry":result["curvature_audit"]["raw_asymmetry_relative_norm"],
             "merit_gradient_norm":result["merit_gradient_norm"],"measured_projected_slope":result["measured_projected_slope"],
             "derived_cauchy_radius":result["derived_cauchy_radius"],"residual_reducing_trial_count":result["residual_reducing_trial_count"],
             "accepted":best is not None}
        if best is None:
            rows.append(row);termination="NO_STRICT_PROJECTED_DESCENT";break
        row.update({"accepted_factor":best["cauchy_factor"],"accepted_residual_norm":best["residual_norm"],
                    "event_residual":best["event_residual"],"eta_minimum":best["eta_minimum"],
                    "accepted_step_norm":best["post_projection_step_norm"]})
        rows.append(row);raw=np.asarray([float.fromhex(v) for v in best["raw_vector_hex"]])
    return {"iterations_requested":ITERATIONS,"iterations_accepted":sum(row["accepted"] for row in rows),
            "termination":termination,"initial_residual_norm":initial,"final_residual_norm":rows[-1].get("accepted_residual_norm",rows[-1]["initial_residual_norm"]),
            "final_event_residual":rows[-1].get("event_residual"),"final_eta_minimum":rows[-1].get("eta_minimum"),
            "rows":rows,"final_raw_vector_hex":[float(v).hex() for v in raw]}

def completion_payload()->dict[str,Any]:
    result=multirefresh_continuation()
    validation={"accepted_v16_54_residual_reproduced":math.isclose(result["initial_residual_norm"],6.405723062607772,rel_tol=0,abs_tol=2e-9),
        "all_refreshes_accepted":result["iterations_accepted"]==ITERATIONS,
        "strict_monotone_descent":all(row["accepted_residual_norm"]<row["initial_residual_norm"]-1e-10 for row in result["rows"] if row["accepted"]),
        "complete_residual_reduced":result["final_residual_norm"]<result["initial_residual_norm"],
        "eta_domain_preserved":result["final_eta_minimum"] is not None and result["final_eta_minimum"]>1e-5,
        "full_precision_state_preserved":len(result["final_raw_vector_hex"])==376}
    return {"artifact":"BHSM_aether_n3_covector_curvature_continuation_v16_55","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"covector_curvature_multirefresh_continuation":result,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"PERSISTENT_JOINT_PARENT_EVENT_DESCENT_ON_THE_NORMALIZED_SOFT_BRANCH_CHART",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"AUDIT_THE_POST_CONTINUATION_BLOCK_RESIDUALS_AND_CONTINUE_OR_REDIRECT_TO_THEIR_UPSTREAM_OWNER",
        "validation":validation,"validation_passed":all(validation.values())}

def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(v) for v in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {k:_canonical(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(v) for v in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_covector_curvature_continuation_v16_55.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","ITERATIONS","v16_54_raw_vector","multirefresh_continuation","completion_payload","deterministic_json","materialize"]
