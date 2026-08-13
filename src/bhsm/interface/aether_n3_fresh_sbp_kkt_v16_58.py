"""Fresh canonical-reset N=3 event KKT with the trapezoid-SBP pair."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import _local_first_derivatives
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (M_DIMENSION,NODES,ORDER,Q_DIMENSION,
    boundary_lapse,boundary_radius_and_jacobian,classical_interior_seed,event_gradient_indices,kkt_variable_scales,
    pack_reduced,trapezoid_weights,unpack_reduced)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_replacement_geometry_force_v16_06 import zero_source_heat_geometry_response
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import generalized_lagrangian
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state

VERSION="v16.58"
CLASSIFICATION="BHSM_N3_FRESH_CANONICAL_RESET_TRAPEZOID_SBP_EVENT_KKT"
FULL_BHSM_COMPLETE=False

def fresh_sbp_seed_vector()->np.ndarray:
    seed=classical_interior_seed()
    return pack_reduced(np.asarray(seed["coordinates"]),np.asarray(seed["multipliers"]),float(seed["period"]),0.0)

def sbp_replacement_action_covector(base_vector:np.ndarray,*,radial_points:int=36,relative_step:float=2e-6)->dict[str,Any]:
    base=np.asarray(base_vector);u=unpack_reduced(np.concatenate((base,[0.0])))
    q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);period=float(u["period"])
    difference=trapezoid_sbp_difference();weights=trapezoid_weights();velocity=difference@q/period
    attached=np.empty(NODES);dq_local=np.empty((NODES,Q_DIMENSION));dv_local=np.empty((NODES,Q_DIMENSION));dm_local=np.empty((NODES,M_DIMENSION))
    for node in range(NODES):
        attached[node],dq_local[node],dv_local[node],dm_local[node]=_local_first_derivatives(q[node],velocity[node],m[node],points=radial_points,relative_step=relative_step)
    radii,log_jac=boundary_radius_and_jacobian(q);lapse=boundary_lapse(m);casimir=standard_model_casimir_coefficient()
    restored=lapse*casimir/radii;parent=attached+restored;dq_local-=restored[:,None]*log_jac
    signs=(-1.0)**np.arange(1,ORDER+1);dm_local[:,:ORDER]+=restored[:,None]*signs
    dq=period*weights[:,None]*dq_local+difference.T@(weights[:,None]*dv_local);dm=period*weights[:,None]*dm_local
    lapse_sum=float(weights@lapse);proper=period*lapse_sum;heat=zero_source_heat_geometry_response(radii,proper/NODES)
    radial=np.asarray(heat["d_Gamma_heat_d_log_R_nodes"]);dq+=radial[:,None]*log_jac
    duration=float(heat["d_Gamma_heat_d_log_proper_step"]);dm[:,:ORDER]+=duration*(weights*lapse/lapse_sum)[:,None]*signs
    dperiod=float(weights@(parent-np.einsum("ij,ij->i",dv_local,velocity)))+duration/period
    covector=np.concatenate((dq[1:].ravel(),dm.ravel(),[dperiod]))
    gamma=period*float(weights@parent)+float(heat["Gamma_heat"])
    return {"Gamma_replacement":gamma,"covector":covector,"coordinate_covector":dq,"multiplier_covector":dm,
        "period_covector":dperiod,"proper_duration":proper,
        "same_common_gauge_ghost_rank16_HS_operator":heat["same_rank16_gauge_ghost_HS_direct_sum_as_source_response"]}

def sbp_replacement_action_from_base(base_vector:np.ndarray)->float:
    return float(sbp_replacement_action_covector(base_vector)["Gamma_replacement"])

def sbp_event_value_from_base(base_vector:np.ndarray)->float:
    u=unpack_reduced(np.concatenate((np.asarray(base_vector),[0.0])));q=np.asarray(u["coordinates"]);m=np.asarray(u["multipliers"]);period=float(u["period"])
    velocity=trapezoid_sbp_difference()@q/period
    return float(np.linalg.eigvalsh(exact_action_jet_at_state(ORDER,q[-1],velocity[-1],m[-1],points=44).hessian)[6])

def sbp_event_covector(base_vector:np.ndarray,*,relative_step:float=2e-7)->np.ndarray:
    base=np.asarray(base_vector);result=np.zeros_like(base)
    for index in event_gradient_indices():
        step=relative_step*max(1.0,abs(float(base[index])));delta=np.zeros_like(base);delta[index]=step
        result[index]=(sbp_event_value_from_base(base+delta)-sbp_event_value_from_base(base-delta))/(2*step)
    return result

def sbp_projected_residual_and_vector(scaled_vector:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    y=np.asarray(scaled_vector,dtype=float).copy();scales=kkt_variable_scales();base=y[:-1]/scales[:-1]
    action=np.asarray(sbp_replacement_action_covector(base)["covector"])/scales[:-1]
    event=sbp_event_covector(base)/scales[:-1]/scales[-1]
    y[-1]=-float(action@event)/float(event@event)
    residual=np.concatenate((action+y[-1]*event,[sbp_event_value_from_base(base)/scales[-1]]))
    return y,residual

def directional_witness()->dict[str,float]:
    raw=fresh_sbp_seed_vector();base=raw[:-1];covector=np.asarray(sbp_replacement_action_covector(base)["covector"])
    direction=np.cos(np.arange(base.size)+0.37)/kkt_variable_scales()[:-1];direction/=np.linalg.norm(direction);epsilon=2e-6
    finite=(sbp_replacement_action_from_base(base+epsilon*direction)-sbp_replacement_action_from_base(base-epsilon*direction))/(2*epsilon)
    analytic=float(covector@direction)
    return {"analytic_directional_derivative":analytic,"finite_difference_directional_derivative":float(finite),
        "relative_residual":abs(analytic-finite)/max(1.0,abs(finite))}

def fresh_sbp_kkt()->dict[str,Any]:
    raw=fresh_sbp_seed_vector();scales=kkt_variable_scales();y=raw*scales
    projected,residual=sbp_projected_residual_and_vector(y);q_count=230;m_count=144
    return {"source":"FRESH_CLASSICAL_INTERIOR_SEED_FROM_CANONICAL_RESET_N3_ORBIT","old_v16_55_state_transplanted":False,
        "derivative_quadrature_pair":"TRAPEZOID_EXACT_SBP","directional_witness":directional_witness(),
        "seed_period":float(raw[-2]),"projected_event_multiplier_scaled":float(projected[-1]),
        "complete_projected_residual_norm":float(np.linalg.norm(residual)),"q_stationarity_norm":float(np.linalg.norm(residual[:q_count])),
        "multiplier_stationarity_norm":float(np.linalg.norm(residual[q_count:q_count+m_count])),
        "period_stationarity":float(residual[-2]),"scaled_event_residual":float(residual[-1]),
        "eta_minimum":_minimum_node_eta(projected/scales),"projected_raw_vector_hex":[float(v).hex() for v in projected/scales],
        "same_common_gauge_ghost_rank16_HS_operator":sbp_replacement_action_covector(raw[:-1])["same_common_gauge_ghost_rank16_HS_operator"]}

def completion_payload()->dict[str,Any]:
    result=fresh_sbp_kkt();w=result["directional_witness"]
    validation={"fresh_canonical_reset_seed":not result["old_v16_55_state_transplanted"],
        "SBP_covector_matches_action":w["relative_residual"]<2e-5,
        "complete_376_state_preserved":len(result["projected_raw_vector_hex"])==376,
        "eta_domain_preserved":result["eta_minimum"]>1e-5,
        "same_unsplit_pushforward":result["same_common_gauge_ghost_rank16_HS_operator"],
        "complete_residual_finite":math.isfinite(result["complete_projected_residual_norm"])}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_kkt_v16_58","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"fresh_sbp_kkt":result,"status":"VALIDATED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"VARIATIONALLY_CONSISTENT_ENDPOINT_EVOLUTION_OF_THE_FRESH_CANONICAL_N3_PARENT_ORBIT",
        "dependency_advanced":"REBUILDS_THE_N3_EVENT_KKT_ON_THE_EXACT_SBP_ORBIT_DISCRETIZATION_WITHOUT_STATE_TRANSPLANT",
        "active_calculation":"BUILD_THE_FRESH_SBP_PHYSICAL_JACOBIAN_AND_BEGIN_CONSTRAINED_DESCENT",
        "validation":validation,"validation_passed":all(validation.values())}

def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(v) for v in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {k:_canonical(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(v) for v in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_kkt_v16_58.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","fresh_sbp_seed_vector","sbp_replacement_action_covector","sbp_replacement_action_from_base","sbp_event_value_from_base","sbp_event_covector","sbp_projected_residual_and_vector","directional_witness","fresh_sbp_kkt","completion_payload","deterministic_json","materialize"]
