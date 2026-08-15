"""Physical block and normalized soft-mode audit after v16.55."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales,open_difference_matrix,unpack_reduced
from bhsm.interface.aether_physical_inverse_closure_v16_36 import Q_LABELS

VERSION="v16.56"
CLASSIFICATION="BHSM_N3_POST_CURVATURE_NORMALIZED_SOFT_MODE_PHYSICAL_AUDIT"
FULL_BHSM_COMPLETE=False

def v16_55_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_covector_curvature_continuation_v16_55.json").read_text(encoding="utf-8"))
    values=payload["covector_curvature_multirefresh_continuation"]["final_raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.55 vector has wrong dimension")
    return raw

def post_curvature_soft_mode_audit()->dict[str,Any]:
    raw=v16_55_raw_vector();y=raw*kkt_variable_scales();_,residual=projected_residual_and_vector(y)
    qres=residual[:230].reshape(23,10);mres=residual[230:374].reshape(24,6)
    unpacked=unpack_reduced(raw);q=np.asarray(unpacked["coordinates"]);m=np.asarray(unpacked["multipliers"]);period=float(unpacked["period"])
    velocity=open_difference_matrix()@q/period
    hessian=exact_action_jet_at_state(3,q[-1],velocity[-1],m[-1],points=44).hessian
    eigenvalues,eigenvectors=np.linalg.eigh(hessian);soft=eigenvectors[:,6];eigenvalue=float(eigenvalues[6])
    roles={"log_scale":"boundary_scale_and_common_pushforward_geometry","u_1":"conformal_shape_and_reconstruction_geometry",
        "u_2":"conformal_shape_and_reconstruction_geometry","u_3":"conformal_shape_and_reconstruction_geometry",
        "w_0":"normal/fiber_localization_geometry","w_1":"normal/fiber_localization_geometry","w_2":"normal/fiber_localization_geometry",
        "v_0":"Hopf_anisotropy_and_gauge_breaking_background_geometry","v_1":"Hopf_anisotropy_and_gauge_breaking_background_geometry",
        "v_2":"Hopf_anisotropy_and_gauge_breaking_background_geometry"}
    group=np.linalg.norm(qres,axis=0);flat=np.argsort(np.abs(qres.ravel()))[::-1][:16]
    previous=json.loads(Path("artifacts/BHSM_aether_n3_physical_residual_role_audit_v16_45.json").read_text(encoding="utf-8"))["physical_residual_role_audit"]
    previous_groups={row["coordinate"]:row["stationarity_norm"] for row in previous["coordinate_group_ranking"]}
    return {"source_state":"v16.55_final","complete_residual_norm":float(np.linalg.norm(residual)),
        "q_stationarity_norm":float(np.linalg.norm(qres)),"multiplier_stationarity_norm":float(np.linalg.norm(mres)),
        "period_stationarity":float(residual[-2]),"scaled_event_residual":float(residual[-1]),"event_multiplier_scaled":float(y[-1]),
        "coordinate_group_ranking":[{"coordinate":Q_LABELS[i],"stationarity_norm":float(group[i]),"v16_45_stationarity_norm":float(previous_groups[Q_LABELS[i]]),
            "change_from_v16_45":float(group[i]-previous_groups[Q_LABELS[i]]),"physical_role":roles[Q_LABELS[i]]} for i in np.argsort(group)[::-1]],
        "largest_coordinate_components":[{"node":int(i//10+1),"coordinate":Q_LABELS[i%10],"residual":float(qres.ravel()[i]),"physical_role":roles[Q_LABELS[i%10]]} for i in flat],
        "terminal_soft_mode":{"ordered_index":6,"eigenvalue":eigenvalue,"scaled_event_value":eigenvalue/1e-3,
            "gap_below":float(eigenvalue-eigenvalues[5]),"gap_above":float(eigenvalues[7]-eigenvalue),
            "eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(hessian@soft-eigenvalue*soft)),
            "normalized_eigenvector":[float(v) for v in soft],"full_terminal_spectrum":[float(v) for v in eigenvalues]},
        "interpretation":"THE_SOFT_MODE_IS_NORMALIZED_AND_SPECTRALLY_ISOLATED_BUT_THE_PARENT_ORBIT_IS_NOT_YET_A_SIMULTANEOUS_SADDLE;_NO_GAUGE_OR_RANK16_PROJECTION_IS_PROMOTED_YET"}

def completion_payload()->dict[str,Any]:
    result=post_curvature_soft_mode_audit();soft=result["terminal_soft_mode"]
    validation={"accepted_v16_55_residual_reproduced":math.isclose(result["complete_residual_norm"],6.40276417658978,rel_tol=0,abs_tol=2e-9),
        "soft_event_matches_KKT_residual":math.isclose(soft["scaled_event_value"],result["scaled_event_residual"],rel_tol=0,abs_tol=2e-9),
        "soft_eigenvector_normalized":math.isclose(soft["eigenvector_norm"],1.0,rel_tol=0,abs_tol=2e-12),
        "soft_eigenpair_resolved":soft["eigenpair_residual_norm"]<1e-9,
        "soft_branch_isolated":min(soft["gap_below"],soft["gap_above"])>1e-4,
        "all_coordinate_roles_classified":len(result["coordinate_group_ranking"])==10,
        "simultaneous_saddle_not_falsely_claimed":result["q_stationarity_norm"]>abs(result["scaled_event_residual"])}
    return {"artifact":"BHSM_aether_n3_post_curvature_soft_mode_audit_v16_56","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"post_curvature_soft_mode_audit":result,
        "status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"NORMALIZATION_AND_SPECTRAL_IDENTIFIABILITY_OF_THE_ACTUAL_TERMINAL_EULER_DIRAC_SOFT_MODE",
        "dependency_advanced":"MEASURES_THE_SOFT_VECTOR_AND_REMAINING_PARENT_GEOMETRY_BLOCKS_ON_THE_LATEST_INDEPENDENT_N3_ORBIT",
        "active_calculation":"CONTINUE_THE_COVECTOR_CONSISTENT_N3_SADDLE_BEFORE_THE_COMMON_GAUGE_RANK16_LR_PUSHFORWARD",
        "validation":validation,"validation_passed":all(validation.values())}

def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(v) for v in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {k:_canonical(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(v) for v in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_post_curvature_soft_mode_audit_v16_56.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_55_raw_vector","post_curvature_soft_mode_audit","completion_payload","deterministic_json","materialize"]
