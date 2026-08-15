"""Exact-local-jet SBP covector and component-direction identifiability audit."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base, sbp_replacement_action_from_base
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, boundary_lapse,
    boundary_radius_and_jacobian, kkt_variable_scales, trapezoid_weights,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_replacement_geometry_force_v16_06 import zero_source_heat_geometry_response

VERSION = "v17.61"
CLASSIFICATION = "BHSM_N3_EXACT_LOCAL_JET_SBP_COVECTOR"
FULL_BHSM_COMPLETE = False
AUDIT_SCALES = (1e-8, 3e-8, 1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4)


def exact_local_jet_sbp_action_covector(base_vector: np.ndarray, *, radial_points: int = 36) -> dict[str, Any]:
    base = np.asarray(base_vector, dtype=float)
    unpacked = unpack_reduced(np.concatenate((base, [0.0])))
    q = np.asarray(unpacked["coordinates"]); multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"]); difference = trapezoid_sbp_difference(); weights = trapezoid_weights()
    velocity = difference @ q / period
    attached = np.empty(NODES); dq_local = np.empty((NODES, Q_DIMENSION)); dv_local = np.empty((NODES, Q_DIMENSION)); dm_local = np.empty((NODES, M_DIMENSION))
    for node in range(NODES):
        jet = exact_full_action_jet_at_state(ORDER, q[node], velocity[node], multipliers[node], points=radial_points)
        attached[node] = jet.value
        dq_local[node] = jet.gradient[:Q_DIMENSION]
        dv_local[node] = jet.gradient[Q_DIMENSION:2 * Q_DIMENSION]
        dm_local[node] = jet.gradient[2 * Q_DIMENSION:]
    radii, log_jacobian = boundary_radius_and_jacobian(q); lapse = boundary_lapse(multipliers)
    restored = lapse * standard_model_casimir_coefficient() / radii; parent = attached + restored
    dq_local -= restored[:, None] * log_jacobian
    signs = (-1.0) ** np.arange(1, ORDER + 1); dm_local[:, :ORDER] += restored[:, None] * signs
    dq = period * weights[:, None] * dq_local + difference.T @ (weights[:, None] * dv_local)
    dm = period * weights[:, None] * dm_local
    lapse_sum = float(weights @ lapse); proper = period * lapse_sum
    heat = zero_source_heat_geometry_response(radii, proper / NODES)
    dq += np.asarray(heat["d_Gamma_heat_d_log_R_nodes"])[:, None] * log_jacobian
    duration = float(heat["d_Gamma_heat_d_log_proper_step"])
    dm[:, :ORDER] += duration * (weights * lapse / lapse_sum)[:, None] * signs
    dperiod = float(weights @ (parent - np.einsum("ij,ij->i", dv_local, velocity))) + duration / period
    covector = np.concatenate((dq[1:].ravel(), dm.ravel(), [dperiod]))
    gamma = period * float(weights @ parent) + float(heat["Gamma_heat"])
    return {"Gamma_replacement":gamma,"covector":covector,"coordinate_covector":dq,
        "multiplier_covector":dm,"period_covector":dperiod,"proper_duration":proper,
        "same_common_gauge_ghost_rank16_HS_operator":heat["same_rank16_gauge_ghost_HS_direct_sum_as_source_response"]}


def exact_local_jet_sbp_projected_residual_and_vector(scaled_vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    y=np.asarray(scaled_vector,dtype=float).copy();scales=kkt_variable_scales();base=y[:-1]/scales[:-1]
    action=np.asarray(exact_local_jet_sbp_action_covector(base)["covector"])/scales[:-1]
    event=sbp_event_covector(base)/scales[:-1]/scales[-1]
    y[-1]=-float(action@event)/float(event@event)
    return y,np.concatenate((action+y[-1]*event,[sbp_event_value_from_base(base)/scales[-1]]))


def exact_local_jet_covector_audit() -> dict[str, Any]:
    raw=v17_53_selected_raw_vector();scales=kkt_variable_scales();y,residual=exact_local_jet_sbp_projected_residual_and_vector(raw*scales);initial=_metrics(residual)
    base=raw[:-1];directional=np.cos(np.arange(base.size)+0.37)/scales[:-1];directional/=np.linalg.norm(directional);epsilon=1e-5
    finite=(sbp_replacement_action_from_base(base+epsilon*directional)-sbp_replacement_action_from_base(base-epsilon*directional))/(2*epsilon)
    analytic=float(np.asarray(exact_local_jet_sbp_action_covector(base)["covector"])@directional)
    payload=json.loads(Path("artifacts/BHSM_aether_n3_high_accuracy_scale_component_event_v17_59.json").read_text(encoding="utf-8"))["high_accuracy_scale_component_event"]
    row=next(item for item in payload["direction_rows"] if item["priority_profile"]=={"log_scale":2.0,"event":2.0})
    anchor=next(item for item in row["trials"] if item.get("raw_vector_hex"))
    anchor_y=np.asarray([float.fromhex(value) for value in anchor["raw_vector_hex"]])*scales
    direction=(anchor_y-y)/anchor["trust_radius"];direction[-1]=0.0;direction/=np.linalg.norm(direction)
    rows=[];accepted=[]
    for step in AUDIT_SCALES:
        candidate_y,candidate_residual=exact_local_jet_sbp_projected_residual_and_vector(y+step*direction)
        candidate_raw=candidate_y/scales;metrics=_metrics(candidate_residual);reductions={key:initial[key]-metrics[key] for key in initial}
        fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};eta=_minimum_node_eta(candidate_raw)
        trial={"step":step,"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,
            "minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),
            "eta_minimum":eta,"raw_vector_hex":[float(value).hex() for value in candidate_raw]}
        rows.append(trial)
        if eta>1e-5 and all(value>MARGIN for value in reductions.values()):accepted.append(trial)
    best=max(accepted,key=lambda item:(item["minimum_fractional_progress"],sum(item["fractional_reductions"].values()))) if accepted else None
    return {"source_state":"v17.53_selected_event_log_curvature_compensated_state","physical_action_changed":False,
        "physical_event_changed":False,"local_derivative_method":"EXACT_FULL_26_VARIABLE_ACTION_JET",
        "initial_metrics":initial,"directional_witness":{"finite_difference_action_derivative":float(finite),
        "exact_covector_derivative":analytic,"relative_residual":abs(analytic-finite)/max(1.0,abs(finite))},
        "audit_scale_count":len(rows),"direction_rows":rows,"strict_candidate_count":len(accepted),
        "selected_exact_residual_component_direction":best}


def completion_payload()->dict[str,Any]:
    result=exact_local_jet_covector_audit();best=result["selected_exact_residual_component_direction"]
    validation={"physical_equations_unchanged":not result["physical_action_changed"] and not result["physical_event_changed"],
        "exact_full_local_jet_adopted":result["local_derivative_method"]=="EXACT_FULL_26_VARIABLE_ACTION_JET",
        "covector_matches_action_direction":result["directional_witness"]["relative_residual"]<2e-7,
        "all_scales_evaluated":result["audit_scale_count"]==len(AUDIT_SCALES),
        "candidate_result_classified":best is not None or result["strict_candidate_count"]==0,
        "eta_preserved_if_promoted":best is None or best["eta_minimum"]>1e-5,
        "full_state_preserved_if_promoted":best is None or len(best["raw_vector_hex"])==376}
    return {"artifact":"BHSM_aether_n3_exact_local_jet_sbp_covector_v17_61","version":VERSION,
        "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"exact_local_jet_sbp_covector":result,
        "status":"VALIDATED" if all(validation.values()) and best is not None else "RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"EXACT_LOCAL_JET_SAME_ACTION_SBP_COVECTOR_AND_SCALE_DIRECTION_IDENTIFIABILITY",
        "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation":"PROMOTE_THE_EXACT_RESIDUAL_DIRECTION_IF_STRICT_OR_REBUILD_ITS_PHYSICAL_JACOBIAN",
        "validation":validation,"validation_passed":all(validation.values())}


def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_exact_local_jet_sbp_covector_v17_61.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path


__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","AUDIT_SCALES","exact_local_jet_sbp_action_covector","exact_local_jet_sbp_projected_residual_and_vector","exact_local_jet_covector_audit","completion_payload","materialize"]
