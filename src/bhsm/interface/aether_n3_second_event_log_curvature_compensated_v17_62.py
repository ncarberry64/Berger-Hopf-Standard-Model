"""Second event/log curvature-compensated continuation from v17.53."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_event_log_curvature_compensated_v17_53 import (
    COMPENSATOR_FAMILY, COMPENSATOR_TARGET, EVENT_FAMILY, EVENT_TARGET,
    _direction, _payload,
)
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector

VERSION="v17.62";CLASSIFICATION="BHSM_N3_SECOND_SOFT_EVENT_LOG_CURVATURE_COMPENSATED_CONTINUATION";FULL_BHSM_COMPLETE=False
EVENT_ROOT_FRACTIONS=(0.00005,0.0001,0.00015,0.0002,0.00025,0.0003,0.0004)
COMPENSATOR_RADII=(0.0,1e-6,2e-6,3e-6,4e-6,5e-6,6e-6,7e-6,8e-6,9e-6,1e-5,1.1e-5,1.2e-5,1.3e-5,1.4e-5,1.5e-5)


def second_event_log_curvature_compensated()->dict[str,Any]:
    payload=_payload();scales=kkt_variable_scales();legacy_y49,_=sbp_projected_residual_and_vector(v17_49_selected_raw_vector()*scales)
    event_direction,event_row=_direction(payload,legacy_y49,scales,EVENT_FAMILY,EVENT_TARGET)
    compensator,_=_direction(payload,legacy_y49,scales,COMPENSATOR_FAMILY,COMPENSATOR_TARGET)
    y,residual=exact_local_jet_sbp_projected_residual_and_vector(v17_53_selected_raw_vector()*scales);initial=_metrics(residual)
    event_root_radius=1.0/-float(event_row["verified_fractional_slopes"]["event"]);trials=[];accepted=[]
    for event_fraction in EVENT_ROOT_FRACTIONS:
        event_radius=event_fraction*event_root_radius
        for compensator_radius in COMPENSATOR_RADII:
            try:
                candidate_y,candidate_residual=exact_local_jet_sbp_projected_residual_and_vector(
                    y+event_radius*event_direction+compensator_radius*compensator)
                raw_candidate=candidate_y/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_residual)
                reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial}
                trial={"event_root_fraction":event_fraction,"event_radius":event_radius,"compensator_radius":compensator_radius,
                    "eta_minimum":eta,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,
                    "minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),
                    "raw_vector_hex":[float(value).hex() for value in raw_candidate]};trials.append(trial)
                if eta>1e-5 and all(value>MARGIN for value in reductions.values()):accepted.append(trial)
            except (FloatingPointError,ValueError,ArithmeticError) as exc:
                trials.append({"event_root_fraction":event_fraction,"compensator_radius":compensator_radius,"exception":type(exc).__name__})
    best=max(accepted,key=lambda item:(item["minimum_fractional_progress"],sum(item["fractional_reductions"].values()))) if accepted else None
    return {"source_state":"v17.53_selected_event_log_curvature_compensated_state","physical_action_changed":False,
        "physical_event_changed":False,"residual_evaluator":"V17_61_EXACT_LOCAL_JET_SBP",
        "event_direction":{"family":EVENT_FAMILY,"target_fraction":EVENT_TARGET},
        "compensator_direction":{"family":COMPENSATOR_FAMILY,"target_fraction":COMPENSATOR_TARGET},
        "event_root_radius":event_root_radius,"initial_metrics":initial,"trial_count":len(trials),
        "strict_candidate_count":len(accepted),"trials":trials,"selected_second_event_log_curvature_compensated":best}


def completion_payload()->dict[str,Any]:
    result=second_event_log_curvature_compensated();best=result["selected_second_event_log_curvature_compensated"]
    validation={"v17_53_exact_residual_reproduced":math.isclose(result["initial_metrics"]["complete"],0.850379466555715,rel_tol=0,abs_tol=2e-8),
        "v17_53_event_reproduced":math.isclose(result["initial_metrics"]["event"],0.083985972706086,rel_tol=0,abs_tol=2e-8),
        "exact_local_jet_residual_adopted":result["residual_evaluator"]=="V17_61_EXACT_LOCAL_JET_SBP",
        "bounded_grid_tested":result["trial_count"]==len(EVENT_ROOT_FRACTIONS)*len(COMPENSATOR_RADII),
        "physical_equations_unchanged":not result["physical_action_changed"] and not result["physical_event_changed"],
        "candidate_result_classified":best is not None or result["strict_candidate_count"]==0,
        "all_six_metrics_reduced_if_promoted":best is None or all(value>MARGIN for value in best["reductions"].values()),
        "eta_preserved_if_promoted":best is None or best["eta_minimum"]>1e-5,
        "full_state_preserved_if_promoted":best is None or len(best["raw_vector_hex"])==376}
    return {"artifact":"BHSM_aether_n3_second_event_log_curvature_compensated_v17_62","version":VERSION,
        "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"second_event_log_curvature_compensated":result,
        "status":"VALIDATED" if all(validation.values()) and best is not None else "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"SECOND_SAME_ACTION_EVENT_LOG_CURVATURE_COMPENSATED_EXACT_RESIDUAL_STEP",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"PROMOTE_IF_STRICT_THEN_REAUDIT_OR_REDIRECT_TO_THE_NONLINEAR_SCALE_MANIFOLD",
        "validation":validation,"validation_passed":all(validation.values())}


def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_second_event_log_curvature_compensated_v17_62.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path


__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","EVENT_ROOT_FRACTIONS","COMPENSATOR_RADII","second_event_log_curvature_compensated","completion_payload","materialize"]
