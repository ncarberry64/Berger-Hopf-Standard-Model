"""Fourth coupled period/w0/v0/event normal-metric cone from v16.96."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any, Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import coupled_owner_cone_from
VERSION="v16.98"; CLASSIFICATION="BHSM_N3_FRESH_SBP_FOURTH_COUPLED_PERIOD_W0_V0_EVENT_NORMAL_METRIC_CONE"; FULL_BHSM_COMPLETE=False

def v16_96_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_third_coupled_owner_cone_v16_96.json").read_text(encoding="utf-8"))
    values=p["fresh_sbp_third_coupled_owner_cone"]["selected_maximin_all_block"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,): raise ValueError("v16.96 selected vector has wrong dimension")
    return raw

def fourth_coupled_owner_cone()->dict[str,Any]:
    return coupled_owner_cone_from(v16_96_selected_raw_vector(),source_state="v16.96_selected_third_coupled_owner_state")

def completion_payload()->dict[str,Any]:
    r=fourth_coupled_owner_cone(); b=r["selected_maximin_all_block"]
    validation={
        "v16_96_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.913708972481446,rel_tol=0,abs_tol=2e-8),
        "v16_96_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.138981449509372,rel_tol=0,abs_tol=2e-8),
        "source_state_owned":r["source_state"]=="v16.96_selected_third_coupled_owner_state",
        "physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],
        "common_direction_exists":r["common_all_block_direction_count"]>0,
        "strict_all_block_candidate_exists":b is not None,
        "all_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),
        "positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),
        "eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376),
    }
    return {"artifact":"BHSM_aether_n3_fresh_sbp_fourth_coupled_owner_cone_v16_98","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_fourth_coupled_owner_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"CONTINUED_SIMULTANEOUS_PERIOD_FIBER_HOPF_AND_IDENTICAL_EVENT_DESCENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_RECOMPUTE_THE_COMPLETE_ACTIVE_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}

def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value,np.bool_): return bool(value)
    if isinstance(value,np.integer): return int(value)
    if isinstance(value,np.floating): value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping): return {key:_canonical(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)): return [_canonical(item) for item in value]
    return value

def deterministic_json(payload:Mapping[str,Any])->str: return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory); target.mkdir(parents=True,exist_ok=True); path=target/"BHSM_aether_n3_fresh_sbp_fourth_coupled_owner_cone_v16_98.json"; path.write_text(deterministic_json(completion_payload()),encoding="utf-8"); return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_96_selected_raw_vector","fourth_coupled_owner_cone","completion_payload","deterministic_json","materialize"]
