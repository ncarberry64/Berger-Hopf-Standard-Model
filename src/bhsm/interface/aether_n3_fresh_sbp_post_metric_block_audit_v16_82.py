"""Residual-block and soft-spectrum audit after the v16.81 metric sequence."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales,unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_physical_inverse_closure_v16_36 import Q_LABELS
VERSION="v16.82";CLASSIFICATION="BHSM_N3_FRESH_SBP_POST_METRIC_SEQUENCE_BLOCK_SOFT_AUDIT";FULL_BHSM_COMPLETE=False
def v16_81_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_fifth_metric_projected_newton_v16_81.json").read_text(encoding="utf-8"));values=p["fresh_sbp_fifth_metric_projected_newton"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.81 selected vector has wrong dimension")
    return raw
def post_metric_block_soft_audit()->dict[str,Any]:
    raw=v16_81_selected_raw_vector();y=raw*kkt_variable_scales();_,res=sbp_projected_residual_and_vector(y);qres=res[:230].reshape(23,10);mres=res[230:374].reshape(24,6)
    u=unpack_reduced(raw);q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);period=float(u["period"]);velocity=trapezoid_sbp_difference()@q/period
    h=exact_action_jet_at_state(3,q[-1],velocity[-1],m[-1],points=44).hessian;eig,vec=np.linalg.eigh(h);soft=vec[:,6];group=np.linalg.norm(qres,axis=0);flat=np.argsort(np.abs(qres.ravel()))[::-1][:20]
    scale_sq=float(np.sum(qres[:,0]**2));late4=float(np.sum(qres[-4:,0]**2)/scale_sq)
    return {"source_state":"v16.81_selected_fifth_metric_projected_state","complete_residual_norm":float(np.linalg.norm(res)),"q_stationarity_norm":float(np.linalg.norm(qres)),"multiplier_stationarity_norm":float(np.linalg.norm(mres)),
        "period_stationarity":float(res[-2]),"scaled_event_residual":float(res[-1]),"event_multiplier_scaled":float(y[-1]),"late_four_scale_squared_fraction":late4,
        "coordinate_group_ranking":[{"coordinate":Q_LABELS[i],"stationarity_norm":float(group[i])} for i in np.argsort(group)[::-1]],
        "largest_coordinate_components":[{"node":int(i//10+1),"coordinate":Q_LABELS[i%10],"residual":float(qres.ravel()[i])} for i in flat],
        "terminal_soft_mode":{"ordered_index":6,"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),
            "eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(h@soft-eig[6]*soft)),"normalized_eigenvector":[float(v) for v in soft]},
        "interpretation":"THE_POST_METRIC_SEQUENCE_REMAINS_DOMINATED_BY_MEASURED_OPEN_ORBIT_GEOMETRY;THE_BLOCK_AND_LATE_NODE_FRACTIONS_DECIDE_THE_NEXT_PRECONDITIONER_WITHOUT_CHANGING_THE_ACTION"}
def completion_payload()->dict[str,Any]:
    r=post_metric_block_soft_audit();s=r["terminal_soft_mode"]
    validation={"v16_81_residual_reproduced":math.isclose(r["complete_residual_norm"],10.539813695735257,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(r["scaled_event_residual"],s["scaled_event_value"],rel_tol=0,abs_tol=2e-8),
        "soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),"soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,
        "all_coordinate_groups_measured":len(r["coordinate_group_ranking"])==10,"simultaneous_closure_not_claimed":r["complete_residual_norm"]>1e-6}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_post_metric_block_audit_v16_82","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_post_metric_block_soft_audit":r,
        "status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED","real_physical_property_explained":"CURRENT_PARENT_GEOMETRY_OWNER_AND_NORMALIZED_SOFT_MODE_AFTER_FIVE_METRIC_PROJECTED_REFRESHES",
        "dependency_advanced":"MEASURES_THE_CURRENT_N3_BLOCKS_REQUIRED_FOR_SIMULTANEOUS_EVENT_SADDLE_CLOSURE","active_calculation":"CONTINUE_THE_METRIC_PROJECTION_OR_TARGET_THE_DOMINANT_MEASURED_OPEN_ORBIT_BLOCK","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_post_metric_block_audit_v16_82.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_81_selected_raw_vector","post_metric_block_soft_audit","completion_payload","deterministic_json","materialize"]
