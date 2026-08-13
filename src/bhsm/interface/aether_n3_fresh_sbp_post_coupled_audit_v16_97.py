"""Complete block and soft-spectrum audit after the v16.96 coupled cone."""
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
VERSION="v16.97";CLASSIFICATION="BHSM_N3_FRESH_SBP_POST_COUPLED_CONE_COMPLETE_BLOCK_SOFT_AUDIT";FULL_BHSM_COMPLETE=False
def v16_96_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_third_coupled_owner_cone_v16_96.json").read_text(encoding="utf-8"));values=p["fresh_sbp_third_coupled_owner_cone"]["selected_maximin_all_block"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.96 selected vector has wrong dimension")
    return raw
def post_coupled_audit()->dict[str,Any]:
    raw=v16_96_selected_raw_vector();y=raw*kkt_variable_scales();_,res=sbp_projected_residual_and_vector(y);qres=res[:230].reshape(23,10);mres=res[230:374].reshape(24,6);u=unpack_reduced(raw);q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);v=trapezoid_sbp_difference()@q/float(u["period"]);H=exact_action_jet_at_state(3,q[-1],v[-1],m[-1],points=44).hessian;eig,vec=np.linalg.eigh(H);soft=vec[:,6];group=np.linalg.norm(qres,axis=0)
    block_rows={"complete":float(np.linalg.norm(res)),"q":float(np.linalg.norm(qres)),"multipliers":float(np.linalg.norm(mres)),"period":abs(float(res[-2])),"event":abs(float(res[-1]))}
    return {"source_state":"v16.96_selected_third_coupled_owner_state","block_norms":block_rows,"coordinate_group_ranking":[{"coordinate":Q_LABELS[i],"stationarity_norm":float(group[i])} for i in np.argsort(group)[::-1]],"terminal_soft_mode":{"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(H@soft-eig[6]*soft))},"eta_minimum_provenance":0.79376789857696,"interpretation":"RECOMPUTE_THE_ACTIVE_OWNER_SET_AFTER_THE_ACCELERATED_COUPLED_STEP_BEFORE_THE_NEXT_FRESH_NORMAL_CONE"}
def completion_payload()->dict[str,Any]:
    r=post_coupled_audit();b=r["block_norms"];s=r["terminal_soft_mode"]
    validation={"v16_96_residual_reproduced":math.isclose(b["complete"],1.913708972481446,rel_tol=0,abs_tol=2e-8),"v16_96_event_reproduced":math.isclose(b["event"],0.138981449509372,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(b["event"],abs(s["scaled_event_value"]),rel_tol=0,abs_tol=2e-8),"soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),"soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,"all_coordinate_groups_measured":len(r["coordinate_group_ranking"])==10,"simultaneous_closure_not_claimed":b["complete"]>1e-6}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_post_coupled_audit_v16_97","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_post_coupled_audit":r,"status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED","real_physical_property_explained":"CURRENT_COMPLETE_RESIDUAL_OWNERS_AND_NORMALIZED_SOFT_MODE_AFTER_ACCELERATED_COUPLED_DESCENT","dependency_advanced":"RETARGETS_THE_NEXT_SIMULTANEOUS_N3_EVENT_SADDLE_CORRECTION_FROM_CURRENT_EVIDENCE","active_calculation":"CONTINUE_THE_COUPLED_OWNER_CONE_WITH_THE_AUDITED_CURRENT_OWNER_SET","validation":validation,"validation_passed":all(validation.values())}
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
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_post_coupled_audit_v16_97.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_96_selected_raw_vector","post_coupled_audit","completion_payload","deterministic_json","materialize"]
