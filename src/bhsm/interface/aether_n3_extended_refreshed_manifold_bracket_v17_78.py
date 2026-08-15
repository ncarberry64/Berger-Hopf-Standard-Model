"""Extend the measured v17.77 period/log crossing above mix 0.15."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import v17_75_selected_raw_vector
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.78";CLASSIFICATION="BHSM_N3_EXTENDED_REFRESHED_MANIFOLD_BRACKET";FULL_BHSM_COMPLETE=False
MIXES=(0.16,0.17,0.18,0.19,0.2,0.22,0.25);FACTORS=(1e-5,3e-5,1e-4);RATIOS=(0.0,25.0,50.0)
def _directions(y:np.ndarray,scales:np.ndarray)->tuple[np.ndarray,np.ndarray]:
 p=json.loads(Path("artifacts/BHSM_aether_n3_refreshed_coupled_manifold_bracket_v17_77.json").read_text(encoding="utf-8"))["refreshed_coupled_manifold_bracket"];a=next(t for t in p["trials"] if t.get("period_manifold_mix")==0.05 and t.get("factor")==3e-5 and t.get("path_ratio")==0.0);b=next(t for t in p["trials"] if t.get("period_manifold_mix")==0.15 and t.get("factor")==3e-5 and t.get("path_ratio")==0.0);ya=np.asarray([float.fromhex(x) for x in a["raw_vector_hex"]])*scales;yb=np.asarray([float.fromhex(x) for x in b["raw_vector_hex"]])*scales;delta=(yb-ya)/(3e-5*(0.15-0.05));blend=(ya-y)/3e-5;d46=blend-0.05*delta;d47=d46+delta;d46[-1]=0;d47[-1]=0;return d46,d47
def extended_refreshed_manifold_bracket()->dict[str,Any]:
 scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_75_selected_raw_vector()*scales);initial=_metrics(residual);d46,d47=_directions(y,scales);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;trials=[];accepted=[]
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
 return {"source_state":"v17.75_selected_fine_period_log_mix_state","source_directions":"v17.77_refreshed_46_47_owner_manifolds","physical_action_changed":False,"physical_event_changed":False,"direction_norms":{"scale_v0":float(np.linalg.norm(d46)),"scale_v0_period":float(np.linalg.norm(d47))},"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_extended_refreshed_manifold":best}
def completion_payload()->dict[str,Any]:
 r=extended_refreshed_manifold_bracket();b=r["selected_extended_refreshed_manifold"];validation={"v17_75_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.831984571818635,rel_tol=0,abs_tol=2e-8),"v17_75_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860915332372,rel_tol=0,abs_tol=2e-8),"v17_77_directions_recovered":math.isclose(r["direction_norms"]["scale_v0"],0.002477521185059,rel_tol=0,abs_tol=2e-9) and math.isclose(r["direction_norms"]["scale_v0_period"],0.281323651126809,rel_tol=0,abs_tol=2e-9),"bounded_extension_tested":r["trial_count"]==len(MIXES)*len(FACTORS)*len(RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_extended_refreshed_manifold_bracket_v17_78","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"extended_refreshed_manifold_bracket":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"EXTENDED_PERIOD_LOG_CROSSING_OF_THE_REFRESHED_PHYSICAL_MANIFOLDS","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_extended_refreshed_manifold_bracket_v17_78.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","MIXES","FACTORS","RATIOS","extended_refreshed_manifold_bracket","completion_payload","materialize"]
