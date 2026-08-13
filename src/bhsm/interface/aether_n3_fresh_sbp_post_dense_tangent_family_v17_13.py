"""Fresh measured tangent-family selection from the dense v17.12 state."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_tangent_family_selection_v17_08 import tangent_family_selection_from
VERSION="v17.13";CLASSIFICATION="BHSM_N3_FRESH_SBP_POST_DENSE_MEASURED_TANGENT_FAMILY_SELECTION";FULL_BHSM_COMPLETE=False
def v17_12_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_dense_radius_promotion_v17_12.json").read_text(encoding="utf-8"));values=p["fresh_sbp_dense_radius_promotion"]["selected_dense_radius"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v17.12 selected vector has wrong dimension")
    return raw
def post_dense_tangent_family()->dict[str,Any]:return tangent_family_selection_from(v17_12_selected_raw_vector(),source_state="v17.12_selected_dense_radius_state")
def completion_payload()->dict[str,Any]:
    r=post_dense_tangent_family();b=r["selected_family_maximin"]
    validation={"v17_12_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.404622364571847,rel_tol=0,abs_tol=2e-8),"v17_12_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.120562294987129,rel_tol=0,abs_tol=2e-8),"v17_12_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.424584973083391,rel_tol=0,abs_tol=2e-8),"source_state_owned":r["source_state"]=="v17.12_selected_dense_radius_state","physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_tangent_families_tested":r["family_count"]==8,"common_family_exists":r["common_family_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_post_dense_tangent_family_v17_13","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_post_dense_tangent_family":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"FRESH_FINITE_NONLINEAR_SIX_OWNER_DESCENT_AFTER_DENSE_RADIUS_PROMOTION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_REFINE_THE_EXACT_RADIUS_OR_REAUDIT_THE_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_post_dense_tangent_family_v17_13.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_12_selected_raw_vector","post_dense_tangent_family","completion_payload","deterministic_json","materialize"]
