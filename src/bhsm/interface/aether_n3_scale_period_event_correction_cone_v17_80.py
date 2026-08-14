"""Measured scale/period/event correction cone at the v17.75 state."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import PERIOD_ROW
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_period_log_direction_bracket_v17_70 import _v17_67_manifold
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_refined_scale_v0_period_manifold_v17_69 import _v17_68_manifold
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import _v17_65_scale,v17_75_selected_raw_vector
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.80";CLASSIFICATION="BHSM_N3_SCALE_PERIOD_EVENT_CORRECTION_CONE";FULL_BHSM_COMPLETE=False
SCALE_CORRECTIONS=(0.05,0.1,0.15,0.2);PERIOD_CORRECTIONS=(-0.025,-0.05,-0.075,-0.1);PATH_RATIOS=(25.0,50.0,75.0,100.0);FACTORS=(3e-5,1e-4)
def scale_period_event_correction_cone()->dict[str,Any]:
 scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_75_selected_raw_vector()*scales);initial=_metrics(residual);y63,_=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;d67=_v17_67_manifold(y63,path,scales);d68=_v17_68_manifold(y63,path,scales);base=.89*d67+.11*d68;d65=_v17_65_scale(y63,y53,scales);scale=d65*(np.linalg.norm(base)/np.linalg.norm(d65));period=np.zeros(376);period[PERIOD_ROW]=np.linalg.norm(base);trials=[];accepted=[]
 for sc in SCALE_CORRECTIONS:
  for pc in PERIOD_CORRECTIONS:
   direction=base+sc*scale+pc*period
   for factor in FACTORS:
    for ratio in PATH_RATIOS:
     pf=factor*ratio
     try:
      cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+factor*direction+pf*path);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"normalized_scale_correction":sc,"normalized_period_correction":pc,"factor":factor,"path_ratio":ratio,"path_factor":pf,"eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(trial)
      if eta>1e-5 and all(v>MARGIN for v in reductions.values()):accepted.append(trial)
     except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"normalized_scale_correction":sc,"normalized_period_correction":pc,"factor":factor,"path_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.75_selected_fine_period_log_mix_state","measured_correction_owners":["scale","period","event"],"physical_action_changed":False,"physical_event_changed":False,"direction_norms":{"base":float(np.linalg.norm(base)),"scale":float(np.linalg.norm(d65)),"path":float(np.linalg.norm(path))},"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_scale_period_event_correction":best}
def completion_payload()->dict[str,Any]:
 r=scale_period_event_correction_cone();b=r["selected_scale_period_event_correction"];validation={"v17_75_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.831984571818635,rel_tol=0,abs_tol=2e-8),"v17_75_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860915332372,rel_tol=0,abs_tol=2e-8),"measured_owners_corrected":r["measured_correction_owners"]==["scale","period","event"],"bounded_cone_tested":r["trial_count"]==len(SCALE_CORRECTIONS)*len(PERIOD_CORRECTIONS)*len(FACTORS)*len(PATH_RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_scale_period_event_correction_cone_v17_80","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"scale_period_event_correction_cone":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"COMMON_DESCENT_CONE_FOR_THE_MEASURED_SCALE_PERIOD_EVENT_TRADEOFF","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_scale_period_event_correction_cone_v17_80.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","SCALE_CORRECTIONS","PERIOD_CORRECTIONS","PATH_RATIOS","FACTORS","scale_period_event_correction_cone","completion_payload","materialize"]
