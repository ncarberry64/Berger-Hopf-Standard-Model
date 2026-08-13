"""Sixth fresh tangent-family selection after the dense promotion."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_post_acceleration_audit_v17_19 import v17_18_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_tangent_family_selection_v17_08 import tangent_family_selection_from
VERSION="v17.20";CLASSIFICATION="BHSM_N3_FRESH_SBP_SIXTH_POST_DENSE_TANGENT_FAMILY_SELECTION";FULL_BHSM_COMPLETE=False
def sixth_post_dense_family()->dict[str,Any]:return tangent_family_selection_from(v17_18_selected_raw_vector(),source_state="v17.18_selected_fifth_post_dense_family_state")
def completion_payload()->dict[str,Any]:
    r=sixth_post_dense_family();b=r["selected_family_maximin"]
    validation={"v17_18_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.272877993568162,rel_tol=0,abs_tol=2e-8),"v17_18_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.107558924760796,rel_tol=0,abs_tol=2e-8),"v17_18_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.382990119280634,rel_tol=0,abs_tol=2e-8),"source_state_owned":r["source_state"]=="v17.18_selected_fifth_post_dense_family_state","physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_tangent_families_tested":r["family_count"]==8,"common_family_exists":r["common_family_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_sixth_post_dense_family_v17_20","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_sixth_post_dense_family":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"SIXTH_POST_DENSE_WITNESS_OF_FRESH_SIX_OWNER_DESCENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_CONTINUE_OR_REAUDIT_AT_THE_NEXT_OWNER_TRANSITION","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_sixth_post_dense_family_v17_20.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","sixth_post_dense_family","completion_payload","deterministic_json","materialize"]
