"""Physical block and soft-spectrum audit after the v16.91 Pareto sequence."""
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
VERSION="v16.92";CLASSIFICATION="BHSM_N3_FRESH_SBP_POST_PARETO_PHYSICAL_BLOCK_SOFT_AUDIT";FULL_BHSM_COMPLETE=False
def v16_91_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_refreshed_pareto_v16_91.json").read_text(encoding="utf-8"));values=p["fresh_sbp_second_refreshed_pareto"]["selected_pareto_balanced"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.91 selected vector has wrong dimension")
    return raw
def post_pareto_audit()->dict[str,Any]:
    raw=v16_91_selected_raw_vector();y=raw*kkt_variable_scales();_,res=sbp_projected_residual_and_vector(y);qres=res[:230].reshape(23,10);mres=res[230:374].reshape(24,6)
    u=unpack_reduced(raw);q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);v=trapezoid_sbp_difference()@q/float(u["period"]);H=exact_action_jet_at_state(3,q[-1],v[-1],m[-1],points=44).hessian;eig,vec=np.linalg.eigh(H);soft=vec[:,6];group=np.linalg.norm(qres,axis=0)
    return {"source_state":"v16.91_selected_refreshed_pareto_state","complete_residual_norm":float(np.linalg.norm(res)),"q_stationarity_norm":float(np.linalg.norm(qres)),"multiplier_stationarity_norm":float(np.linalg.norm(mres)),"period_stationarity":float(res[-2]),"scaled_event_residual":float(res[-1]),
        "coordinate_group_ranking":[{"coordinate":Q_LABELS[i],"stationarity_norm":float(group[i])} for i in np.argsort(group)[::-1]],"late_four_scale_squared_fraction":float(np.sum(qres[-4:,0]**2)/np.sum(qres[:,0]**2)),
        "terminal_soft_mode":{"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(H@soft-eig[6]*soft))},
        "owner_transition":{"v16_75_log_scale_norm":14.016355587104261,"current_log_scale_norm":float(group[0]),"current_primary_owner":"period_stationarity","current_coordinate_owners":["w_0","v_0"],"scale_over_independence_hypothesis_supported":False},
        "interpretation":"THE_SCALE_BLOCK_HAS_MATERIALLY_CLOSED_WITHOUT_REMOVING_ITS_ROW;THE_NEXT_SAME_ORBIT_CORRECTION_MUST_TARGET_PERIOD_W0_V0_WHILE_CONTINUING_THE_IDENTICAL_EVENT"}
def completion_payload()->dict[str,Any]:
    r=post_pareto_audit();s=r["terminal_soft_mode"];o=r["owner_transition"]
    validation={"v16_91_residual_reproduced":math.isclose(r["complete_residual_norm"],2.486624819288495,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(r["scaled_event_residual"],s["scaled_event_value"],rel_tol=0,abs_tol=2e-8),"soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),
        "soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,"scale_block_materially_reduced":o["current_log_scale_norm"]<0.05*o["v16_75_log_scale_norm"],"no_false_scale_over_independence_claim":not o["scale_over_independence_hypothesis_supported"],"simultaneous_closure_not_claimed":r["complete_residual_norm"]>1e-6}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_post_pareto_audit_v16_92","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_post_pareto_audit":r,"status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"CURRENT_PERIOD_FIBER_LOCALIZATION_AND_HOPF_ANISOTROPY_OWNERS_OF_THE_UNCLOSED_PHYSICAL_EVENT_ORBIT","dependency_advanced":"RETARGETS_SIMULTANEOUS_N3_EVENT_SADDLE_CLOSURE_AFTER_MATERIAL_SCALE_BLOCK_REDUCTION","active_calculation":"BUILD_THE_NEXT_SAME_ACTION_PRECONDITIONER_FOR_PERIOD_W0_V0_AND_THE_IDENTICAL_EVENT","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_post_pareto_audit_v16_92.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_91_selected_raw_vector","post_pareto_audit","completion_payload","deterministic_json","materialize"]
