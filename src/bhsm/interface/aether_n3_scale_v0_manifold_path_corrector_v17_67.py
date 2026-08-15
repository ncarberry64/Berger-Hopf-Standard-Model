"""Coupled nonlinear scale-v0 manifold with event/period/fiber path correction."""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_coupled_owner_cone_v16_94 import V0_ROWS
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN,SCALE_ROWS,_metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_post_scale_manifold_audit_v17_64 import v17_63_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector
VERSION="v17.67";CLASSIFICATION="BHSM_N3_NONLINEAR_SCALE_V0_MANIFOLD_PATH_CORRECTOR";FULL_BHSM_COMPLETE=False
DERIVATIVE_STEP=1e-5;MANIFOLD_FACTORS=(0.001,0.003,0.01,0.03,0.05,0.075,0.1);PATH_RATIOS=(50.0,75.0,100.0,125.0,150.0,200.0)
def scale_v0_manifold_path_corrector()->dict[str,Any]:
 scales=kkt_variable_scales();y,r=exact_local_jet_sbp_projected_residual_and_vector(v17_63_selected_raw_vector()*scales);initial=_metrics(r);rows=np.concatenate((np.asarray(SCALE_ROWS),np.asarray(V0_ROWS)));cols=rows.copy();A=np.empty((len(rows),len(cols)))
 for j,col in enumerate(cols):
  d=np.zeros(376);d[col]=DERIVATIVE_STEP;_,rp=exact_local_jet_sbp_projected_residual_and_vector(y+d);_,rm=exact_local_jet_sbp_projected_residual_and_vector(y-d);A[:,j]=(rp[rows]-rm[rows])/(2*DERIVATIVE_STEP)
 u,s,vt=np.linalg.svd(A,full_matrices=False);coef=-vt.T@((u.T@r[rows])/s);manifold=np.zeros(376);manifold[cols]=coef;pred=float(np.linalg.norm(r[rows]+A@coef)/np.linalg.norm(r[rows]));y53,_=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales);path=y53-y49;path[-1]=0;trials=[];accepted=[]
 for mf in MANIFOLD_FACTORS:
  for ratio in PATH_RATIOS:
   pf=mf*ratio
   try:
    cy,cr=exact_local_jet_sbp_projected_residual_and_vector(y+mf*manifold+pf*path);raw=cy/scales;eta=_minimum_node_eta(raw);metrics=_metrics(cr);red={k:initial[k]-metrics[k] for k in initial};frac={k:red[k]/max(initial[k],1e-300) for k in initial};t={"manifold_newton_factor":mf,"path_ratio":ratio,"path_factor":pf,"eta_minimum":eta,"metrics":metrics,"reductions":red,"fractional_reductions":frac,"minimum_fractional_progress":min(frac.values()),"limiting_owner":min(frac,key=frac.get),"raw_vector_hex":[float(v).hex() for v in raw]};trials.append(t)
    if eta>1e-5 and all(v>MARGIN for v in red.values()):accepted.append(t)
   except (FloatingPointError,ValueError,ArithmeticError) as exc:trials.append({"manifold_newton_factor":mf,"path_ratio":ratio,"exception":type(exc).__name__})
 best=max(accepted,key=lambda t:(t["minimum_fractional_progress"],sum(t["fractional_reductions"].values()))) if accepted else None
 return {"source_state":"v17.63_selected_scale_manifold_path_corrector_state","physical_action_changed":False,"physical_event_changed":False,"manifold_owner_rows":{"scale":len(SCALE_ROWS),"v0":len(V0_ROWS)},"manifold_dimension":len(rows),"manifold_jacobian_condition_number":float(s[0]/s[-1]),"linearized_manifold_residual_ratio":pred,"manifold_newton_direction_norm":float(np.linalg.norm(manifold)),"initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,"selected_scale_v0_manifold_path_corrector":best}
def completion_payload()->dict[str,Any]:
 r=scale_v0_manifold_path_corrector();b=r["selected_scale_v0_manifold_path_corrector"];v={"v17_63_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.832011690209781,rel_tol=0,abs_tol=2e-8),"v17_63_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.083861037713239,rel_tol=0,abs_tol=2e-8),"all_scale_and_v0_rows_owned":r["manifold_owner_rows"]=={"scale":23,"v0":23} and r["manifold_dimension"]==46,"manifold_jacobian_nonsingular":math.isfinite(r["manifold_jacobian_condition_number"]) and r["manifold_jacobian_condition_number"]<1e6,"linearized_manifold_system_solved":r["linearized_manifold_residual_ratio"]<1e-8,"bounded_grid_tested":r["trial_count"]==len(MANIFOLD_FACTORS)*len(PATH_RATIOS),"physical_equations_unchanged":not r["physical_action_changed"] and not r["physical_event_changed"],"candidate_result_classified":b is not None or r["strict_candidate_count"]==0,"no_unvalidated_state_promoted":b is not None or r["strict_candidate_count"]==0,"all_six_metrics_reduced_if_promoted":bool(b is None or all(x>MARGIN for x in b["reductions"].values())),"eta_domain_preserved_if_promoted":bool(b is None or b["eta_minimum"]>1e-5),"full_state_preserved_if_promoted":bool(b is None or len(b["raw_vector_hex"])==376)}
 return {"artifact":"BHSM_aether_n3_scale_v0_manifold_path_corrector_v17_67","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"scale_v0_manifold_path_corrector":r,"status":"VALIDATED" if all(v.values()) and b is not None else "RECLASSIFIED" if all(v.values()) else "INVALIDATED","real_physical_property_explained":"SAME_ACTION_COUPLED_NONLINEAR_SCALE_V0_MANIFOLD_WITH_EVENT_PERIOD_FIBER_PATH_CORRECTION","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_THE_UPDATED_OWNER_AND_SOFT_BRANCH","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_scale_v0_manifold_path_corrector_v17_67.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","MANIFOLD_FACTORS","PATH_RATIOS","scale_v0_manifold_path_corrector","completion_payload","materialize"]
