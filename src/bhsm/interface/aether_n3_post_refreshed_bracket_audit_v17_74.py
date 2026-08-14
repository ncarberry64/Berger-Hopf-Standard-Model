"""Soft-branch audit after the v17.73 physical promotion."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales,unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
VERSION="v17.74"; CLASSIFICATION="BHSM_N3_POST_REFRESHED_BRACKET_SOFT_AUDIT"; FULL_BHSM_COMPLETE=False; TOLERANCE=1e-6
def v17_73_selected_raw_vector()->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_refreshed_period_log_bracket_v17_73.json").read_text(encoding="utf-8")); h=p["refreshed_period_log_bracket"]["selected_refreshed_period_log_bracket"]["raw_vector_hex"]; raw=np.asarray([float.fromhex(x) for x in h]);
 if raw.shape!=(376,): raise ValueError("v17.73 selected vector has wrong dimension")
 return raw
def post_refreshed_bracket_audit()->dict[str,Any]:
 p=json.loads(Path("artifacts/BHSM_aether_n3_refreshed_period_log_bracket_v17_73.json").read_text(encoding="utf-8"))["refreshed_period_log_bracket"]; b=p["selected_refreshed_period_log_bracket"]; raw=v17_73_selected_raw_vector(); _,residual=exact_local_jet_sbp_projected_residual_and_vector(raw*kkt_variable_scales()); metrics=_metrics(residual); u=unpack_reduced(raw); q=np.asarray(u["coordinates"]); mul=np.asarray(u["multipliers"]); velocity=trapezoid_sbp_difference()@q/float(u["period"]); h=exact_action_jet_at_state(3,q[-1],velocity[-1],mul[-1],points=44).hessian; eig,vec=np.linalg.eigh(h); soft=vec[:,6]; contraction={}
 for owner,fraction in b["fractional_reductions"].items():
  ratio=1-float(fraction); passes=math.ceil(math.log(TOLERANCE/metrics[owner])/math.log(ratio)) if 0<ratio<1 and metrics[owner]>TOLERANCE else 0; contraction[owner]={"ratio_per_pass":ratio,"constant_rate_projected_additional_passes":passes}
 bottleneck=max(contraction,key=lambda owner:contraction[owner]["constant_rate_projected_additional_passes"])
 return {"source_state":"v17.73_selected_refreshed_period_log_bracket_state","metrics":metrics,"terminal_soft_mode":{"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(h@soft-eig[6]*soft))},"eta_minimum_provenance":b["eta_minimum"],"contraction_by_owner":contraction,"extrapolation_bottleneck":bottleneck,"projected_additional_passes":contraction[bottleneck]["constant_rate_projected_additional_passes"],"classification_scope":"EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"}
def completion_payload()->dict[str,Any]:
 r=post_refreshed_bracket_audit(); m=r["metrics"]; s=r["terminal_soft_mode"]; validation={"v17_73_residual_reproduced":math.isclose(m["complete"],0.832001410265343,rel_tol=0,abs_tol=2e-8),"v17_73_event_reproduced":math.isclose(m["event"],0.083860983449970,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(m["event"],abs(s["scaled_event_value"]),rel_tol=0,abs_tol=2e-8),"soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),"soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,"eta_domain_preserved":r["eta_minimum_provenance"]>1e-5,"constant_rate_still_inadequate":r["projected_additional_passes"]>1000,"no_no_go_claimed":r["classification_scope"]=="EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"}; passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_post_refreshed_bracket_audit_v17_74","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"post_refreshed_bracket_audit":r,"status":"RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"ISOLATED_SOFT_BRANCH_AFTER_THE_REFRESHED_PERIOD_LOG_PROMOTION","dependency_advanced":"RESOLVE_THE_MEASURED_PERIOD_LOG_MIX_BOUNDARY_AT_V17_73","active_calculation":"REFINE_THE_PERIOD_LOG_MIX_NEAR_0_10","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory); target.mkdir(parents=True,exist_ok=True); path=target/"BHSM_aether_n3_post_refreshed_bracket_audit_v17_74.json"; path.write_text(deterministic_json(completion_payload()),encoding="utf-8"); return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_73_selected_raw_vector","post_refreshed_bracket_audit","completion_payload","materialize"]
