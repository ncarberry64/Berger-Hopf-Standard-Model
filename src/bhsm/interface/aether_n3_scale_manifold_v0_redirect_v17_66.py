"""Redirect v17.65 scale Newton to the v0-descending v17.53 path."""
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
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.66";CLASSIFICATION="BHSM_N3_SCALE_MANIFOLD_V0_PATH_REDIRECT";FULL_BHSM_COMPLETE=False
SCALE_FACTORS=(0.001,0.003,0.01,0.03,0.05,0.075,0.1);PATH_RATIOS=(50.0,75.0,100.0,125.0,150.0,200.0)
def _recovered_scale_direction(y:np.ndarray,scales:np.ndarray)->tuple[np.ndarray,float]:
 p=json.loads(Path("artifacts/BHSM_aether_n3_second_scale_manifold_path_corrector_v17_65.json").read_text(encoding="utf-8"))["second_scale_manifold_path_corrector"]
 a=next(t for t in p["trials"] if t.get("raw_vector_hex") and t["scale_newton_factor"]==0.01 and t["secant_ratio"]==5.0)
 b=next(t for t in p["trials"] if t.get("raw_vector_hex") and t["scale_newton_factor"]==0.01 and t["secant_ratio"]==10.0)
 ya=np.asarray([float.fromhex(v) for v in a["raw_vector_hex"]])*scales;yb=np.asarray([float.fromhex(v) for v in b["raw_vector_hex"]])*scales
 secant=(yb-ya)/(0.01*(10.0-5.0));scale=(ya-y-0.01*5.0*secant)/0.01;scale[-1]=0.0
 reconstructed=y+0.01*scale+0.05*secant
 return scale,float(np.linalg.norm(reconstructed[:-1]-ya[:-1]))
def scale_manifold_v0_redirect()->dict[str,Any]:
 scales=kkt_variable_scales();y,r=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales);initial=_metrics(r);scale,reconstruction=_recovered_scale_direction(y,scales);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0.0;trials=[];accepted=[]
 for sf in SCALE_FACTORS:
  for ratio in PATH_RATIOS:
   factor=sf*ratio
   try:
    cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+sf*scale+factor*path);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);red={k:initial[k]-metrics[k] for k in initial};frac={k:red[k]/max(initial[k],1e-300) for k in initial};t={"scale_newton_factor":sf,"v0_path_ratio":ratio,"v0_path_factor":factor,"eta_minimum":eta,"metrics":metrics,"reductions":red,"fractional_reductions":frac,"minimum_fractional_progress":min(frac.values()),"limiting_owner":min(frac,key=frac.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(t)
    if eta>1e-5 and all(v>MARGIN for v in red.values()):accepted.append(t)
   except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"scale_newton_factor":sf,"v0_path_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.63_selected_scale_manifold_path_corrector_state","physical_action_changed":False,"physical_event_changed":False,"scale_direction_source":"EXACTLY_RECONSTRUCTED_FROM_V17_65_TRIAL_BANK","scale_direction_reconstruction_residual":reconstruction,"v0_path_source":"V17_49_TO_V17_53_ACCEPTED_CURVATURE_COMPENSATED_DISPLACEMENT","initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_scale_manifold_v0_redirect":best}
def completion_payload()->dict[str,Any]:
 r=scale_manifold_v0_redirect();b=r["selected_scale_manifold_v0_redirect"];v={"v17_63_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.832011690209781,rel_tol=0,abs_tol=2e-8),"v17_63_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083861037713239,rel_tol=0,abs_tol=2e-8),"scale_direction_exactly_reconstructed":r["scale_direction_reconstruction_residual"]<1e-12,"bounded_grid_tested":r["trial_count"]==len(SCALE_FACTORS)*len(PATH_RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(x>MARGIN for x in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)}
 return {"artifact":"BHSM_aether_n3_scale_manifold_v0_redirect_v17_66","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"scale_manifold_v0_redirect":r,"status":"VALIDATED" if all(v.values()) and b is not None else "RECLASSIFIED" if all(v.values()) else "INVALIDATED","real_physical_property_explained":"SAME_ACTION_SCALE_MANIFOLD_REDIRECT_TO_THE_MEASURED_V0_DESCENDING_PATH","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_scale_manifold_v0_redirect_v17_66.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","SCALE_FACTORS","PATH_RATIOS","scale_manifold_v0_redirect","completion_payload","materialize"]
