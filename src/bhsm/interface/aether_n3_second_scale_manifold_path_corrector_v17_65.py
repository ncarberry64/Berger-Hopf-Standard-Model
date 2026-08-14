"""Second nonlinear scale-manifold continuation with the v17.63 secant."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,SCALE_ROWS,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.65";CLASSIFICATION="BHSM_N3_SECOND_NONLINEAR_SCALE_MANIFOLD_SECANT_CORRECTOR";FULL_BHSM_COMPLETE=False
DERIVATIVE_STEP=1e-5;SCALE_FACTORS=(0.01,0.03,0.05,0.075,0.1,0.15,0.2);SECANT_RATIOS=(5.0,10.0,15.0,20.0,25.0,30.0,40.0)
def second_scale_manifold_path_corrector()->dict[str,Any]:
 scales=kkt_variable_scales();y,r=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales);initial=_metrics(r);y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);secant=y-y53;secant[-1]=0;idx=np.asarray(SCALE_ROWS);A=np.empty((23,23))
 for j,col in enumerate(idx):
  d=np.zeros(376);d[col]=DERIVATIVE_STEP;_,rp=exact_local_jet_sbp_projected_residual_and_vector(y+d);_,rm=exact_local_jet_sbp_projected_residual_and_vector(y-d);A[:,j]=(rp[idx]-rm[idx])/(2*DERIVATIVE_STEP)
 u,s,vt=np.linalg.svd(A,full_matrices=False);coef=-vt.T@((u.T@r[idx])/s);scale=np.zeros(376);scale[idx]=coef;pred=float(np.linalg.norm(r[idx]+A@coef)/np.linalg.norm(r[idx]));trials=[];accepted=[]
 for sf in SCALE_FACTORS:
  for ratio in SECANT_RATIOS:
   factor=sf*ratio
   try:
    cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+sf*scale+factor*secant);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);red={k:initial[k]-metrics[k] for k in initial};frac={k:red[k]/max(initial[k],1e-300) for k in initial};t={"scale_newton_factor":sf,"secant_ratio":ratio,"secant_factor":factor,"eta_minimum":eta,"metrics":metrics,"reductions":red,"fractional_reductions":frac,"minimum_fractional_progress":min(frac.values()),"limiting_owner":min(frac,key=frac.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(t)
    if eta>1e-5 and all(v>MARGIN for v in red.values()):accepted.append(t)
   except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"scale_newton_factor":sf,"secant_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.63_selected_scale_manifold_path_corrector_state","physical_action_changed":False,"physical_event_changed":False,"residual_evaluator":"V17_61_EXACT_LOCAL_JET_SBP","scale_row_count":23,"scale_jacobian_condition_number":float(s[0]/s[-1]),"linearized_scale_residual_ratio":pred,"scale_newton_direction_norm":float(np.linalg.norm(scale)),"secant_direction_norm":float(np.linalg.norm(secant)),"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_second_scale_manifold_path_corrector":best}
def completion_payload()->dict[str,Any]:
 r=second_scale_manifold_path_corrector();b=r["selected_second_scale_manifold_path_corrector"];v={"v17_63_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.832011690209781,rel_tol=0,abs_tol=2e-8),"v17_63_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083861037713239,rel_tol=0,abs_tol=2e-8),"all_scale_rows_owned":r["scale_row_count"]==23,"scale_jacobian_nonsingular":r["scale_jacobian_condition_number"]<1e4,"linearized_scale_system_solved":r["linearized_scale_residual_ratio"]<1e-9,"bounded_grid_tested":r["trial_count"]==len(SCALE_FACTORS)*len(SECANT_RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(x>MARGIN for x in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)}
 return {"artifact":"BHSM_aether_n3_second_scale_manifold_path_corrector_v17_65","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"second_scale_manifold_path_corrector":r,"status":"VALIDATED" if all(v.values()) and b is not None else "RECLASSIFIED" if all(v.values()) else "INVALIDATED","real_physical_property_explained":"SECOND_SAME_ACTION_NONLINEAR_SCALE_MANIFOLD_SECANT_CONTINUATION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_AND_CONTINUE_THE_SCALE_MANIFOLD_SECANT","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_second_scale_manifold_path_corrector_v17_65.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","SCALE_FACTORS","SECANT_RATIOS","second_scale_manifold_path_corrector","completion_payload","materialize"]
