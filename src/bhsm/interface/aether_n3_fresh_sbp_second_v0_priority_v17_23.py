"""Second bounded v0-priority measured tangent family from v17.22."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_v0_priority_family_v17_22 import v0_priority_family_from
VERSION="v17.23";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_V0_PRIORITY_MEASURED_TANGENT_FAMILY";FULL_BHSM_COMPLETE=False
def v17_22_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_v0_priority_family_v17_22.json").read_text(encoding="utf-8"));values=p["fresh_sbp_v0_priority_family"]["selected_v0_priority_maximin"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v17.22 selected vector has wrong dimension")
    return raw
def second_v0_priority()->dict[str,Any]:return v0_priority_family_from(v17_22_selected_raw_vector(),source_state="v17.22_selected_v0_priority_state")
def completion_payload()->dict[str,Any]:
    r=second_v0_priority();b=r["selected_v0_priority_maximin"]
    validation={"v17_22_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.192046120259039,rel_tol=0,abs_tol=2e-8),"v17_22_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.099693053008901,rel_tol=0,abs_tol=2e-8),"v17_22_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.35954947220889,rel_tol=0,abs_tol=2e-8),"source_state_owned":r["source_state"]=="v17.22_selected_v0_priority_state","physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"bounded_priorities_tested":r["priority_count"]==6,"all_families_tested":r["family_count"]==7,"common_direction_exists":r["common_direction_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_v0_priority_v17_23","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_second_v0_priority":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"PERSISTENCE_OF_SIX_OWNER_DESCENT_WITH_V0_CURVATURE_COMPENSATION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_SOFT_MODE_AND_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}
def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(item) for item in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {key:_canonical(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(item) for item in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_second_v0_priority_v17_23.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_22_selected_raw_vector","second_v0_priority","completion_payload","deterministic_json","materialize"]
