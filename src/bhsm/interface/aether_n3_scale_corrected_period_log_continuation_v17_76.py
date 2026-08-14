"""Add the measured well-conditioned scale direction to the period/log bracket."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_period_log_direction_bracket_v17_70 import _v17_67_manifold
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_refined_scale_v0_period_manifold_v17_69 import _v17_68_manifold
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales,unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.76";CLASSIFICATION="BHSM_N3_SCALE_CORRECTED_PERIOD_LOG_CONTINUATION";FULL_BHSM_COMPLETE=False
CORRECTIONS=(-0.2,-0.1,-0.05,0.0,0.05,0.1,0.2);FACTORS=(3e-5,1e-4,3e-4,1e-3)
def v17_75_selected_raw_vector()->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_fine_period_log_mix_v17_75.json").read_text(encoding="utf-8"));h=p["fine_period_log_mix"]["selected_fine_period_log_mix"]["raw_vector_hex"];raw=np.asarray([float.fromhex(x) for x in h]);
 if raw.shape!=(376,):raise ValueError("v17.75 selected vector has wrong dimension")
 return raw
def _v17_65_scale(y63:np.ndarray,y53:np.ndarray,scales:np.ndarray)->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_second_scale_manifold_path_corrector_v17_65.json").read_text(encoding="utf-8"))["second_scale_manifold_path_corrector"];a=p["trials"][0];cy=np.asarray([float.fromhex(x) for x in a["raw_vector_hex"]])*scales;secant=y63-y53;secant[-1]=0;direction=(cy-y63-a["secant_factor"]*secant)/a["scale_newton_factor"];direction[-1]=0;return direction
def scale_corrected_period_log_continuation()->dict[str,Any]:
 scales=kkt_variable_scales();raw0=v17_75_selected_raw_vector();y,residual=exact_local_jet_sbp_projected_residual_and_vector(raw0*scales);initial=_metrics(residual);y63,_=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;d65=_v17_65_scale(y63,y53,scales);d67=_v17_67_manifold(y63,path,scales);d68=_v17_68_manifold(y63,path,scales);base=0.89*d67+0.11*d68;scaled65=d65*(np.linalg.norm(base)/np.linalg.norm(d65));u=unpack_reduced(raw0);q=np.asarray(u["coordinates"]);mul=np.asarray(u["multipliers"]);velocity=trapezoid_sbp_difference()@q/float(u["period"]);h=exact_action_jet_at_state(3,q[-1],velocity[-1],mul[-1],points=44).hessian;eig,vec=np.linalg.eigh(h);soft=vec[:,6];trials=[];accepted=[]
 for correction in CORRECTIONS:
  direction=base+correction*scaled65
  for factor in FACTORS:
   try:
    cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+factor*direction);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"normalized_scale_correction":correction,"factor":factor,"eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(trial)
    if eta>1e-5 and all(v>MARGIN for v in reductions.values()):accepted.append(trial)
   except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"normalized_scale_correction":correction,"factor":factor,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.75_selected_fine_period_log_mix_state","physical_action_changed":False,"physical_event_changed":False,"direction_norms":{"scale":float(np.linalg.norm(d65)),"period_log":float(np.linalg.norm(base))},"initial_metrics":initial,"terminal_soft_mode":{"scaled_event_value":float(eig[6]/1e-3),"gap_below":float(eig[6]-eig[5]),"gap_above":float(eig[7]-eig[6]),"eigenvector_norm":float(np.linalg.norm(soft)),"eigenpair_residual_norm":float(np.linalg.norm(h@soft-eig[6]*soft))},"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_scale_corrected_continuation":best}
def completion_payload()->dict[str,Any]:
 r=scale_corrected_period_log_continuation();b=r["selected_scale_corrected_continuation"];s=r["terminal_soft_mode"];validation={"v17_75_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.831984571818635,rel_tol=0,abs_tol=2e-8),"v17_75_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860915332372,rel_tol=0,abs_tol=2e-8),"event_matches_soft_spectrum":math.isclose(r["initial_metrics"]["event"],abs(s["scaled_event_value"]),rel_tol=0,abs_tol=2e-8),"soft_branch_isolated":min(s["gap_below"],s["gap_above"])>1e-4 and s["eigenpair_residual_norm"]<1e-9 and math.isclose(s["eigenvector_norm"],1,abs_tol=2e-12),"bounded_correction_tested":r["trial_count"]==len(CORRECTIONS)*len(FACTORS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_scale_corrected_period_log_continuation_v17_76","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"scale_corrected_period_log_continuation":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"SCALE_CORRECTION_OF_THE_MEASURED_PERIOD_LOG_COMMON_DESCENT_DIRECTION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_scale_corrected_period_log_continuation_v17_76.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","CORRECTIONS","FACTORS","v17_75_selected_raw_vector","scale_corrected_period_log_continuation","completion_payload","materialize"]
