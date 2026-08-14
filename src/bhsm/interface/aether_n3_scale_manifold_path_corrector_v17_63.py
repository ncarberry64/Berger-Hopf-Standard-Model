"""Nonlinear scale-manifold Newton step with accepted-path correction."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, SCALE_ROWS, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector

VERSION="v17.63";CLASSIFICATION="BHSM_N3_NONLINEAR_SCALE_MANIFOLD_ACCEPTED_PATH_CORRECTOR";FULL_BHSM_COMPLETE=False
SCALE_DERIVATIVE_STEP=1e-5
SCALE_NEWTON_FACTORS=(0.001,0.003,0.01,0.03,0.05,0.1,0.2)
PATH_CORRECTOR_RATIOS=(50.0,75.0,100.0,125.0,150.0,200.0)


def scale_manifold_path_corrector()->dict[str,Any]:
    scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);initial=_metrics(residual)
    y49,_=exact_local_jet_sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales)
    path_direction=y-y49;path_direction[-1]=0.0
    indices=np.asarray(SCALE_ROWS,dtype=int);matrix=np.empty((len(indices),len(indices)))
    for column_index,column in enumerate(indices):
        delta=np.zeros(376);delta[column]=SCALE_DERIVATIVE_STEP
        _,plus=exact_local_jet_sbp_projected_residual_and_vector(y+delta)
        _,minus=exact_local_jet_sbp_projected_residual_and_vector(y-delta)
        matrix[:,column_index]=(plus[indices]-minus[indices])/(2*SCALE_DERIVATIVE_STEP)
    u,singular_values,vt=np.linalg.svd(matrix,full_matrices=False)
    coefficient=-vt.T@((u.T@residual[indices])/singular_values)
    scale_direction=np.zeros(376);scale_direction[indices]=coefficient
    predicted_ratio=float(np.linalg.norm(residual[indices]+matrix@coefficient)/np.linalg.norm(residual[indices]))
    trials=[];accepted=[]
    for scale_factor in SCALE_NEWTON_FACTORS:
        for ratio in PATH_CORRECTOR_RATIOS:
            path_factor=scale_factor*ratio
            try:
                candidate_y,candidate_residual=exact_local_jet_sbp_projected_residual_and_vector(
                    y+scale_factor*scale_direction+path_factor*path_direction)
                raw_candidate=candidate_y/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_residual)
                reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial}
                trial={"scale_newton_factor":scale_factor,"path_corrector_ratio":ratio,"path_corrector_factor":path_factor,
                    "eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,
                    "minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),
                    "raw_vector_hex":[float(value).hex() for value in raw_candidate]};trials.append(trial)
                if eta>1e-5 and all(value>MARGIN for value in reductions.values()):accepted.append(trial)
            except (FloatingPointError,ValueError,ArithmeticError) as exc:
                trials.append({"scale_newton_factor":scale_factor,"path_corrector_ratio":ratio,"exception":type(exc).__name__})
    best=max(accepted,key=lambda item:(item["minimum_fractional_progress"],sum(item["fractional_reductions"].values()))) if accepted else None
    return {"source_state":"v17.53_selected_event_log_curvature_compensated_state","physical_action_changed":False,
        "physical_event_changed":False,"residual_evaluator":"V17_61_EXACT_LOCAL_JET_SBP","scale_row_count":len(indices),
        "scale_jacobian_condition_number":float(singular_values[0]/singular_values[-1]),
        "scale_newton_direction_norm":float(np.linalg.norm(scale_direction)),
        "linearized_scale_residual_ratio":predicted_ratio,"accepted_path_direction_norm":float(np.linalg.norm(path_direction)),
        "initial_metrics":initial,"trial_count":len(trials),"strict_candidate_count":len(accepted),"trials":trials,
        "selected_scale_manifold_path_corrector":best}


def completion_payload()->dict[str,Any]:
    result=scale_manifold_path_corrector();best=result["selected_scale_manifold_path_corrector"]
    validation={"v17_53_exact_residual_reproduced":math.isclose(result["initial_metrics"]["complete"],0.850379466555715,rel_tol=0,abs_tol=2e-8),
        "v17_53_event_reproduced":math.isclose(result["initial_metrics"]["event"],0.083985972706086,rel_tol=0,abs_tol=2e-8),
        "all_scale_rows_owned":result["scale_row_count"]==23,
        "scale_jacobian_nonsingular":math.isfinite(result["scale_jacobian_condition_number"]) and result["scale_jacobian_condition_number"]<1e4,
        "linearized_scale_system_solved":result["linearized_scale_residual_ratio"]<1e-9,
        "bounded_grid_tested":result["trial_count"]==len(SCALE_NEWTON_FACTORS)*len(PATH_CORRECTOR_RATIOS),
        "physical_equations_unchanged":not result["physical_action_changed"] and not result["physical_event_changed"],
        "strict_candidate_exists":best is not None,
        "all_six_metrics_reduced":bool(best is not None and all(value>MARGIN for value in best["reductions"].values())),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_scale_manifold_path_corrector_v17_63","version":VERSION,
        "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"scale_manifold_path_corrector":result,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"SAME_ACTION_NONLINEAR_SCALE_MANIFOLD_WITH_ACCEPTED_EVENT_PERIOD_FIBER_PATH_CORRECTION",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"PROMOTE_IF_VALIDATED_THEN_AUDIT_SCALE_MANIFOLD_CONTRACTION_AND_SOFT_BRANCH",
        "validation":validation,"validation_passed":all(validation.values())}


def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_scale_manifold_path_corrector_v17_63.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path


__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","SCALE_NEWTON_FACTORS","PATH_CORRECTOR_RATIOS","scale_manifold_path_corrector","completion_payload","materialize"]
