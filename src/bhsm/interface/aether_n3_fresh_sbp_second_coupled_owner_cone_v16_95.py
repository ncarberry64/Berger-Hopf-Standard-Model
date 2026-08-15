"""Second coupled period/w0/v0/event normal-metric cone from v16.94."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import coupled_owner_cone_from
VERSION="v16.95";CLASSIFICATION="BHSM_N3_FRESH_SBP_SECOND_COUPLED_PERIOD_W0_V0_EVENT_NORMAL_METRIC_CONE";FULL_BHSM_COMPLETE=False
def v16_94_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_coupled_owner_cone_v16_94.json").read_text(encoding="utf-8"));values=p["fresh_sbp_coupled_owner_cone"]["selected_maximin_all_block"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.94 selected vector has wrong dimension")
    return raw
def second_coupled_owner_cone()->dict[str,Any]:return coupled_owner_cone_from(
    v16_94_selected_raw_vector(),source_state="v16.94_selected_first_coupled_owner_state"
)
def completion_payload()->dict[str,Any]:
    r=second_coupled_owner_cone();b=r["selected_maximin_all_block"]
    validation={"v16_94_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],2.38958494685243,rel_tol=0,abs_tol=2e-8),"v16_94_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.206484326311032,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"common_direction_exists":r["common_all_block_direction_count"]>0,"strict_all_block_candidate_exists":b is not None,"all_metrics_reduced":bool(b is not None and all(v>1e-10 for v in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_second_coupled_owner_cone_v16_95","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_second_coupled_owner_cone":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"PERSISTENCE_OF_COUPLED_PERIOD_FIBER_LOCALIZATION_HOPF_ANISOTROPY_AND_ACTUAL_EVENT_DESCENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_AFTER_THE_SCALE_BLOCK_COLLAPSE","active_calculation":"PROMOTE_IF_VALIDATED_OR_REBUILD_FROM_THE_NEW_ACTIVE_CONSTRAINT_SET","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_second_coupled_owner_cone_v16_95.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_94_selected_raw_vector","second_coupled_owner_cone","completion_payload","deterministic_json","materialize"]
