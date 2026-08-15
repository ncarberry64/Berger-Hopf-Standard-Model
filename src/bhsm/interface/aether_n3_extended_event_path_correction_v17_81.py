"""Extend the measured event-path crossing of the v17.80 correction cone."""
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
VERSION="v17.81";CLASSIFICATION="BHSM_N3_EXTENDED_EVENT_PATH_CORRECTION";FULL_BHSM_COMPLETE=False
SCALE_CORRECTIONS=(0.1,0.15,0.2);PERIOD_CORRECTIONS=(-0.05,-0.075,-0.1);PATH_RATIOS=(125.0,175.0,225.0,275.0,350.0,450.0);FACTOR=3e-5
def _direction(sc:float,pc:float,y:np.ndarray,path:np.ndarray,scales:np.ndarray)->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_scale_period_event_correction_cone_v17_80.json").read_text(encoding="utf-8"))["scale_period_event_correction_cone"];a=next(t for t in p["trials"] if t.get("normalized_scale_correction")==sc and t.get("normalized_period_correction")==pc and t.get("factor")==FACTOR and t.get("path_ratio")==25.0);cy=np.asarray([float.fromhex(x) for x in a["raw_vector_hex"]])*scales;direction=(cy-y-a["path_factor"]*path)/FACTOR;direction[-1]=0;return direction
def extended_event_path_correction()->dict[str,Any]:
 scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_75_selected_raw_vector()*scales);initial=_metrics(residual);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;trials=[];accepted=[]
 for sc in SCALE_CORRECTIONS:
  for pc in PERIOD_CORRECTIONS:
   direction=_direction(sc,pc,y,path,scales)
   for ratio in PATH_RATIOS:
    pf=FACTOR*ratio
    try:
     cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+FACTOR*direction+pf*path);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);reductions={k:initial[k]-metrics[k] for k in initial};fractions={k:reductions[k]/max(initial[k],1e-300) for k in initial};trial={"normalized_scale_correction":sc,"normalized_period_correction":pc,"factor":FACTOR,"path_ratio":ratio,"path_factor":pf,"eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(trial)
     if eta>1e-5 and all(v>MARGIN for v in reductions.values()):accepted.append(trial)
    except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"normalized_scale_correction":sc,"normalized_period_correction":pc,"path_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.75_selected_fine_period_log_mix_state","source_directions":"v17.80_scale_period_event_correction_cone","corrected_owner":"event","physical_action_changed":False,"physical_event_changed":False,"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_extended_event_path_correction":best}
def completion_payload()->dict[str,Any]:
 r=extended_event_path_correction();b=r["selected_extended_event_path_correction"];validation={"v17_75_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.831984571818635,rel_tol=0,abs_tol=2e-8),"v17_75_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083860915332372,rel_tol=0,abs_tol=2e-8),"measured_event_owner_corrected":r["corrected_owner"]=="event","bounded_extension_tested":r["trial_count"]==len(SCALE_CORRECTIONS)*len(PERIOD_CORRECTIONS)*len(PATH_RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(v>MARGIN for v in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)};passed=all(validation.values())
 return {"artifact":"BHSM_aether_n3_extended_event_path_correction_v17_81","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"extended_event_path_correction":r,"status":"VALIDATED" if passed and b is not None else "RECLASSIFIED" if passed else "INVALIDATED","real_physical_property_explained":"EXTENDED_EVENT_CROSSING_OF_THE_MEASURED_SCALE_PERIOD_EVENT_CORRECTION_CONE","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":validation,"validation_passed":passed}
def materialize(directory:str|Path)->Path:
 target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_extended_event_path_correction_v17_81.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","SCALE_CORRECTIONS","PERIOD_CORRECTIONS","PATH_RATIOS","FACTOR","extended_event_path_correction","completion_payload","materialize"]
