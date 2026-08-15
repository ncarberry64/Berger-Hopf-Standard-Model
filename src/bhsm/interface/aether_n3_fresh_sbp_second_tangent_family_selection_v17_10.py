"""Second nonlinear selection across measured tangent families from v17.08."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_post_tangent_family_audit_v17_09 import v17_08_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_tangent_family_selection_v17_08 import tangent_family_selection_from
VERSION="v17.10";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_MEASURED_TANGENT_FAMILY_NONLINEAR_SELECTION";FULL_BHSM_COMPLETE=False
def second_tangent_family_selection()->dict[str,Any]:return tangent_family_selection_from(v17_08_selected_raw_vector(),source_state="v17.08_selected_tangent_family_state")
def completion_payload()->dict[str,Any]:
    r=second_tangent_family_selection();b=r["selected_family_maximin"]
    validation={"v17_08_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.42316795263958,rel_tol=0,abs_tol=2e-8),"v17_08_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.122413241634702,rel_tol=0,abs_tol=2e-8),"v17_08_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.430530541254035,rel_tol=0,abs_tol=2e-8),"source_state_owned":r["source_state"]=="v17.08_selected_tangent_family_state","physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_tangent_families_tested":r["family_count"]==8,"common_family_exists":r["common_family_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_tangent_family_selection_v17_10","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_second_tangent_family_selection":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"PERSISTENCE_OF_FINITE_NONLINEAR_SIX_OWNER_DESCENT_ACROSS_THE_MEASURED_NORMAL_TANGENT_FAMILY","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_REAUDIT_OR_REPEAT_FROM_THE_NEW_FULL_PRECISION_STATE","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_second_tangent_family_selection_v17_10.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","second_tangent_family_selection","completion_payload","deterministic_json","materialize"]
