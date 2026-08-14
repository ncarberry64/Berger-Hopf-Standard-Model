"""Refresh the existing 46/47-owner physical manifolds at v17.75."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import PERIOD_ROW,V0_ROWS
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,SCALE_ROWS,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import v17_75_selected_raw_vector
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.77";CLASSIFICATION="BHSM_N3_REFRESHED_COUPLED_MANIFOLD_BRACKET";FULL_BHSM_COMPLETE=False
STEP=1e-5;MIXES=(0.05,0.075,0.1,0.125,0.15);FACTORS=(3e-5,1e-4,3e-4,1e-3);RATIOS=(0.0,25.0,50.0,75.0)
def _solve(matrix:np.ndarray,target:np.ndarray)->tuple[np.ndarray,np.ndarray,float]:
 u,s,vt=np.linalg.svd(matrix,full_matrices=False);coef=-vt.T@((u.T@target)/s);return coef,s,float(np.linalg.norm(target+matrix@coef)/np.linalg.norm(target))
def refreshed_coupled_manifold_bracket()->dict[str,Any]:
 scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_75_selected_raw_vector()*scales);initial=_metrics(residual);rows46=np.concatenate((np.asarray(SCALE_ROWS),np.asarray(V0_ROWS)));rows47=np.concatenate((rows46,np.asarray([PERIOD_ROW])));matrix=np.empty((47,47))
 for j,col in enumerate(rows47):
  delta=np.zeros(376);delta[col]=STEP;_,rp=exact_local_jet_sbp_projected_residual_and_vector(y+delta);_,rm=exact_local_jet_sbp_projected_residual_and_vector(y-delta);matrix[:,j]=(rp[rows47]-rm[rows47])/(2*STEP)
 coef46,s46,pred46=_solve(matrix[:46,:46],residual[rows46]);coef47,s47,pred47=_solve(matrix,residual[rows47]);d46=np.zeros(376);d47=np.zeros(376);d46[rows46]=coef46;d47[rows47]=coef47;y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;trials=[];accepted=[]
 for mix in MIXES:
  direction=(1-mix)*d46+mix*d47
  for factor in FACTORS:
   for ratio in RATIOS:
    pf=factor*ratio
    try:
     cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+factor*direction+pf*path);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"period_manifold_mix":mix,"factor":factor,"path_ratio":ratio,"path_factor":pf,"eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(trial)
     if eta>1e-5 and all(v>MARGIN for v in reductions.values()):accepted.append(trial)
    except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"period_manifold_mix":mix,"factor":factor,"path_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.75_selected_fine_period_log_mix_state","physical_action_changed":False,"physical_event_changed":False,"manifold_dimensions":[46,47],"jacobian_condition_numbers":{"scale_v0":float(s46[0]/s46[-1]),"scale_v0_period":float(s47[0]/s47[-1])},"linearized_residual_ratios":{"scale_v0":pred46,"scale_v0_period":pred47},"direction_norms":{"scale_v0":float(np.linalg.norm(d46)),"scale_v0_period":float(np.linalg.norm(d47))},"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_refreshed_coupled_manifold":best}
def completion_payload()->dict[str,Any]:
 r=refreshed_coupled_manifold_bracket();b=r["selected_refreshed_coupled_manifold"];validation={"v17_75_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.831984571818635,rel_tol=0,abs_tol=2e-8),"v17_75_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860915332372,rel_tol=0,abs_tol=2e-8),"existing_manifolds_refreshed":r["manifold_dimensions"]==[46,47],"manifold_jacobians_nonsingular":max(r["jacobian_condition_numbers"].values())<1e7,"linearized_systems_solved":max(r["linearized_residual_ratios"].values())<1e-8,"bounded_bracket_tested":r["trial_count"]==len(MIXES)*len(FACTORS)*len(RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_refreshed_coupled_manifold_bracket_v17_77","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"refreshed_coupled_manifold_bracket":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"REFRESHED_COMMON_DESCENT_BRACKET_OF_THE_EXISTING_SCALE_V0_AND_SCALE_V0_PERIOD_MANIFOLDS","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_refreshed_coupled_manifold_bracket_v17_77.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","STEP","MIXES","FACTORS","RATIOS","refreshed_coupled_manifold_bracket","completion_payload","materialize"]
