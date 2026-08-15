"""Second covector-consistent curvature continuation from v16.53."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_covector_consistent_curvature_v16_53 import covector_consistent_continuation_from

VERSION="v16.54"
CLASSIFICATION="BHSM_N3_SECOND_COVECTOR_CONSISTENT_EVENT_CURVATURE_CONTINUATION"
FULL_BHSM_COMPLETE=False

def v16_53_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_covector_consistent_curvature_v16_53.json").read_text(encoding="utf-8"))
    values=payload["covector_consistent_curvature_continuation"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.53 vector has wrong dimension")
    return raw

def second_covector_consistent_continuation()->dict[str,Any]:return covector_consistent_continuation_from(v16_53_raw_vector())

def completion_payload()->dict[str,Any]:
    result=second_covector_consistent_continuation();best=result["best_accepted"]
    validation={"accepted_v16_53_residual_reproduced":math.isclose(result["initial_residual_norm"],6.409165623953296,rel_tol=0,abs_tol=2e-9),
        "local_chart_preserved":result["curvature_relative_step"]<1e-4,
        "measured_direction_is_descent":result["measured_projected_slope"]<0,
        "positive_cauchy_radius":result["derived_cauchy_radius"]>0,
        "strict_step_accepted":best is not None,
        "complete_residual_reduced":bool(best is not None and best["residual_norm"]<result["initial_residual_norm"]-1e-10),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_second_covector_consistent_curvature_v16_54","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"second_covector_consistent_curvature_continuation":result,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"PERSISTENCE_OF_THE_SMOOTH_NORMALIZED_EULER_DIRAC_SOFT_BRANCH_CURVATURE_CHART",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"CONTINUE_THE_COVECTOR_CONSISTENT_PROJECTED_SOLVE_OR_REDIRECT_TO_THE_NEXT_MEASURED_DEFECT",
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_second_covector_consistent_curvature_v16_54.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_53_raw_vector","second_covector_consistent_continuation","completion_payload","deterministic_json","materialize"]
