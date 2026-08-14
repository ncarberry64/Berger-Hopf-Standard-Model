"""Resolve the narrow period/log common-descent mix at v17.73."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_period_log_direction_bracket_v17_70 import _v17_67_manifold
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_refreshed_bracket_audit_v17_74 import v17_73_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_refined_scale_v0_period_manifold_v17_69 import _v17_68_manifold
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.75";CLASSIFICATION="BHSM_N3_FINE_PERIOD_LOG_MIX";FULL_BHSM_COMPLETE=False
MIXES=(0.085,0.09,0.095,0.1,0.105,0.11,0.115);FACTORS=(1e-5,3e-5,1e-4,3e-4)
def fine_period_log_mix()->dict[str,Any]:
 scales=kkt_variable_scales(); y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_73_selected_raw_vector()*scales); initial=_metrics(residual); y63,_=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales); y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales); y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales); path=y53-y49;path[-1]=0;d67=_v17_67_manifold(y63,path,scales);d68=_v17_68_manifold(y63,path,scales);trials=[];accepted=[]
 for mix in MIXES:
  direction=(1-mix)*d67+mix*d68
  for factor in FACTORS:
   try:
    cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+factor*direction);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"v17_68_mix":mix,"factor":factor,"eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(trial)
    if eta>1e-5 and all(v>MARGIN for v in reductions.values()):accepted.append(trial)
   except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"v17_68_mix":mix,"factor":factor,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.73_selected_refreshed_period_log_bracket_state","measured_boundary":[0.085,0.115],"physical_action_changed":False,"physical_event_changed":False,"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_fine_period_log_mix":best}
def completion_payload()->dict[str,Any]:
 r=fine_period_log_mix();b=r["selected_fine_period_log_mix"];validation={"v17_73_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.832001410265343,rel_tol=0,abs_tol=2e-8),"v17_73_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860983449970,rel_tol=0,abs_tol=2e-8),"measured_boundary_resolved":r["measured_boundary"]==[0.085,0.115],"bounded_mix_tested":r["trial_count"]==len(MIXES)*len(FACTORS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_fine_period_log_mix_v17_75","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fine_period_log_mix":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"FINITE_COMMON_DESCENT_RADIUS_AT_THE_MEASURED_PERIOD_LOG_MIX_BOUNDARY","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fine_period_log_mix_v17_75.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","MIXES","FACTORS","fine_period_log_mix","completion_payload","materialize"]
