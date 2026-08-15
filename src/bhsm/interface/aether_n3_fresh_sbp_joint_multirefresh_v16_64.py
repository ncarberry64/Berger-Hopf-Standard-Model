"""Two-refresh strict joint-filter continuation from v16.63."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import sbp_descent_from
VERSION="v16.64";CLASSIFICATION="BHSM_N3_FRESH_SBP_STRICT_JOINT_FILTER_MULTIREFRESH";FULL_BHSM_COMPLETE=False;ITERATIONS=2
def v16_63_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_joint_filter_v16_63.json").read_text(encoding="utf-8"));values=p["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values]);
    if raw.shape!=(376,):raise ValueError("v16.63 selected vector has wrong dimension")
    return raw
def joint_multirefresh()->dict[str,Any]:
    raw=v16_63_selected_raw_vector();rows=[];initial=None;initial_event=None;termination="ITERATION_LIMIT"
    for iteration in range(1,ITERATIONS+1):
        r=sbp_descent_from(raw,joint_filter=True);minimum=r["best_accepted"];selected=r["best_joint_filter_accepted"]
        if initial is None:initial=r["initial_residual_norm"];initial_event=r["initial_event_residual"]
        row={"iteration":iteration,"initial_residual_norm":r["initial_residual_norm"],"initial_event_residual":r["initial_event_residual"],
            "merit_gradient_norm":r["merit_gradient_norm"],"measured_projected_slope":r["measured_projected_slope"],
            "derived_cauchy_radius":r["derived_cauchy_radius"],"joint_candidate_count":r["joint_filter_reducing_trial_count"],
            "minimum_total_candidate":None if minimum is None else {k:minimum[k] for k in ("cauchy_factor","residual_norm","event_residual","eta_minimum")},
            "accepted":selected is not None}
        if selected is None:rows.append(row);termination="NO_STRICT_JOINT_DESCENT";break
        row.update({"selected_factor":selected["cauchy_factor"],"selected_residual_norm":selected["residual_norm"],
            "selected_event_residual":selected["event_residual"],"selected_eta_minimum":selected["eta_minimum"],
            "selected_step_norm":selected["post_projection_step_norm"]});rows.append(row)
        raw=np.asarray([float.fromhex(v) for v in selected["raw_vector_hex"]])
    last=rows[-1]
    return {"iterations_requested":ITERATIONS,"iterations_accepted":sum(row["accepted"] for row in rows),"termination":termination,
        "initial_residual_norm":initial,"initial_event_residual":initial_event,
        "final_residual_norm":last.get("selected_residual_norm",last["initial_residual_norm"]),
        "final_event_residual":last.get("selected_event_residual",last["initial_event_residual"]),
        "final_eta_minimum":last.get("selected_eta_minimum"),"rows":rows,"final_raw_vector_hex":[float(v).hex() for v in raw]}
def completion_payload()->dict[str,Any]:
    r=joint_multirefresh()
    validation={"selected_v16_63_residual_reproduced":math.isclose(r["initial_residual_norm"],39.40229627868378,rel_tol=0,abs_tol=2e-8),
        "selected_v16_63_event_reproduced":math.isclose(r["initial_event_residual"],0.370232077820356,rel_tol=0,abs_tol=2e-8),
        "all_refreshes_accepted":r["iterations_accepted"]==ITERATIONS,
        "strict_complete_descent_each_step":all(row["selected_residual_norm"]<row["initial_residual_norm"]-1e-10 for row in r["rows"] if row["accepted"]),
        "strict_actual_event_descent_each_step":all(abs(row["selected_event_residual"])<abs(row["initial_event_residual"])-1e-10 for row in r["rows"] if row["accepted"]),
        "eta_domain_preserved":r["final_eta_minimum"] is not None and r["final_eta_minimum"]>1e-5,
        "full_precision_state_preserved":len(r["final_raw_vector_hex"])==376}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_joint_multirefresh_v16_64","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "fresh_sbp_joint_multirefresh":r,"selection_rule":"MINIMUM_COMPLETE_RESIDUAL_AMONG_STEPS_THAT_STRICTLY_REDUCE_COMPLETE_RESIDUAL_AND_ABSOLUTE_ACTUAL_EVENT",
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"PERSISTENCE_OF_SIMULTANEOUS_PARENT_STATIONARITY_AND_ACTUAL_EVENT_DESCENT_ON_THE_FRESH_SBP_ORBIT",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_ON_THE_EXACT_SBP_DISCRETIZATION",
        "active_calculation":"CONTINUE_THE_STRICT_JOINT_FILTER_UNTIL_ALL_N3_BLOCKS_CLOSE_OR_A_NEW_UPSTREAM_DEFECT_IS_MEASURED",
        "validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_joint_multirefresh_v16_64.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","ITERATIONS","v16_63_selected_raw_vector","joint_multirefresh","completion_payload","deterministic_json","materialize"]
