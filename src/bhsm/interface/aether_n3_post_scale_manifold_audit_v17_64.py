"""Soft-branch and contraction audit after v17.63 scale-manifold continuation."""
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
VERSION="v17.64";CLASSIFICATION="BHSM_N3_POST_SCALE_MANIFOLD_SOFT_CONTRACTION_AUDIT";FULL_BHSM_COMPLETE=False;TOLERANCE=1e-6
def v17_63_selected_raw_vector()->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_scale_manifold_path_corrector_v17_63.json").read_text(encoding="utf-8"));h=p["scale_manifold_path_corrector"]["selected_scale_manifold_path_corrector"]["raw_vector_hex"];raw=np.asarray([float.fromhex(x) for x in h]);
 if raw.shape!=(376,):raise ValueError("v17.63 selected vector has wrong dimension")
 return raw
def post_scale_manifold_audit()->dict[str,Any]:
 p=json.loads(Path("artifacts/BHSM_aether_n3_scale_manifold_path_corrector_v17_63.json").read_text(encoding="utf-8"))["scale_manifold_path_corrector"];b=p["selected_scale_manifold_path_corrector"];raw=v17_63_selected_raw_vector();_,r=exact_local_jet_sbp_projected_residual_and_vector(raw*kkt_variable_scales());m=_metrics(r);u=unpack_reduced(raw);q=np.asarray(u["coordinates"]);mul=np.asarray(u["multipliers"]);v=trapezoid_sbp_difference()@q/float(u["period"]);h=exact_action_jet_at_state(3,q[-1],v[-1],mul[-1],points=44).hessian;eig,vec=np.linalg.eigh(h);soft=vec[:,6];contraction={}
 for owner,fraction in b["fractional_reductions"].items():
  ratio=1-float(fraction);passes=math.ceil(math.log(TOLERANCE/m[owner])/math.log(ratio)) if 0<ratio<1 and m[owner]>TOLERANCE else 0;contraction[owner]={"ratio_per_pass":ratio,"constant_rate_projected_additional_passes":passes}
 bottleneck=max(contraction,key=lambda owner:contraction[owner]["constant_rate_projected_additional_passes"])
 return {"source_state":"v17.63_selected_scale_manifold_path_corrector_state","metrics":m,"terminal_soft_mode":{"eigenvalue":float(eig[6]),"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(h@soft-eig[6]*soft))},"eta_minimum_provenance":b["eta_minimum"],"contraction_by_owner":contraction,"extrapolation_bottleneck":bottleneck,"projected_additional_passes":contraction[bottleneck]["constant_rate_projected_additional_passes"],"classification_scope":"EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"}
def completion_payload()->dict[str,Any]:
 r=post_scale_manifold_audit();m=r["metrics"];s=r["terminal_soft_mode"];v={"v17_63_residual_reproduced":math.isclose(m["complete"],0.832011690209781,rel_tol=0,abs_tol=2e-8),"v17_63_event_reproduced":math.isclose(m["event"],0.083861037713239,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(m["event"],abs(s["scaled_event_value"]),rel_tol=0,abs_tol=2e-8),"soft_vector_normalized":math.isclose(s["eigenvector_norm"],1,rel_tol=0,abs_tol=2e-12),"soft_eigenpair_resolved":s["eigenpair_residual_norm"]<1e-9,"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4,"eta_domain_preserved":r["eta_minimum_provenance"]>1e-5,"constant_rate_still_inadequate":r["projected_additional_passes"]>1000,"no_no_go_claimed":r["classification_scope"]=="EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"}
 return {"artifact":"BHSM_aether_n3_post_scale_manifold_audit_v17_64","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"post_scale_manifold_audit":r,"status":"RECLASSIFIED" if all(v.values()) else "INVALIDATED","real_physical_property_explained":"IDENTICAL_ISOLATED_SOFT_BRANCH_AFTER_NONLINEAR_SCALE_MANIFOLD_CONTINUATION","dependency_advanced":"CONTINUE_THE_VALIDATED_SCALE_MANIFOLD_PATH_CORRECTION","active_calculation":"RECOMPUTE_THE_SCALE_MANIFOLD_AT_V17_63_AND_CONTINUE_WITH_THE_SAME_SIX_OWNER_GATE","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);path=t/"BHSM_aether_n3_post_scale_manifold_audit_v17_64.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v17_63_selected_raw_vector","post_scale_manifold_audit","completion_payload","materialize"]
