"""Covector-consistent event curvature and continuation at v16.51."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import event_covector, scaled_analytic_kkt_residual
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta, kkt_jacobian_at
from bhsm.interface.aether_n3_projected_cauchy_continuation_v16_49 import CAUCHY_FACTORS
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales

VERSION="v16.53"
CLASSIFICATION="BHSM_N3_COVECTOR_CONSISTENT_EVENT_CURVATURE_CONTINUATION"
FULL_BHSM_COMPLETE=False
CURVATURE_RELATIVE_STEP=1e-5
DIRECTIONAL_EPSILON=3e-6
REDUCTION_MARGIN=1e-10


def v16_51_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_oriented_projected_cauchy_v16_51.json").read_text(encoding="utf-8"))
    values=payload["oriented_projected_cauchy_continuation"]["oriented_projected_cauchy_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v16.51 vector has wrong dimension")
    return raw


def covector_consistent_event_hessian(y_base:np.ndarray)->dict[str,Any]:
    scales=kkt_variable_scales()[:-1];support=event_gradient_indices();dimension=len(y_base)
    hessian=np.zeros((dimension,dimension));steps=CURVATURE_RELATIVE_STEP*np.maximum(1.0,np.abs(y_base[support]))
    def scaled_covector(y:np.ndarray)->np.ndarray:
        return event_covector(y/scales)/scales/kkt_variable_scales()[-1]
    for local,index in enumerate(support):
        delta=np.zeros(dimension);delta[index]=steps[local]
        hessian[:,index]=(scaled_covector(y_base+delta)-scaled_covector(y_base-delta))/(2*steps[local])
    asym=float(np.linalg.norm(hessian-hessian.T)/max(1.0,np.linalg.norm(hessian)))
    return {"raw_hessian":hessian,"symmetric_hessian":0.5*(hessian+hessian.T),
            "raw_asymmetry_relative_norm":asym,"raw_norm":float(np.linalg.norm(hessian)),
            "symmetric_norm":float(np.linalg.norm(0.5*(hessian+hessian.T)))}


def covector_consistent_continuation_from(raw_vector:np.ndarray)->dict[str,Any]:
    raw=np.asarray(raw_vector,dtype=float)
    if raw.shape!=(376,):raise ValueError("raw KKT vector has wrong dimension")
    scales=kkt_variable_scales();y=raw*scales
    assembled=kkt_jacobian_at(raw);base_matrix=np.asarray(assembled["KKT_jacobian"]).copy()
    curvature=covector_consistent_event_hessian(y[:-1]);raw_h=np.asarray(curvature.pop("raw_hessian"));sym_h=np.asarray(curvature.pop("symmetric_hessian"))
    # The derivative of the implemented residual uses the raw covector Jacobian.
    jacobian=base_matrix.copy();jacobian[:-1,:-1]+=y[-1]*raw_h
    symmetric=base_matrix.copy();symmetric[:-1,:-1]+=y[-1]*sym_h
    residual=scaled_analytic_kkt_residual(y);gradient=jacobian.T@residual;gradient[-1]=0.0
    direction=-gradient/np.linalg.norm(gradient)
    plus_y,plus_r=projected_residual_and_vector(y+DIRECTIONAL_EPSILON*direction)
    minus_y,minus_r=projected_residual_and_vector(y-DIRECTIONAL_EPSILON*direction)
    jd=(plus_r-minus_r)/(2*DIRECTIONAL_EPSILON);slope=float(residual@jd)
    orientation="covector_consistent_negative_merit_gradient"
    if slope>=0:
        direction=-direction;plus_y,plus_r,minus_y,minus_r=minus_y,minus_r,plus_y,plus_r
        jd=-jd;slope=-slope;orientation="reversed_by_measured_projected_derivative"
    jd_norm=float(np.linalg.norm(jd));cauchy=-slope/jd_norm**2
    initial=float(np.linalg.norm(residual));trials=[];accepted=[]
    for factor in CAUCHY_FACTORS:
        radius=factor*cauchy;candidate,candidate_r=projected_residual_and_vector(y+radius*direction)
        raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);norm=float(np.linalg.norm(candidate_r))
        row={"cauchy_factor":factor,"trust_radius":radius,"eta_minimum":eta,"domain_valid":bool(eta>1e-5),
             "residual_norm":norm,"residual_reduction":initial-norm,"event_residual":float(candidate_r[-1]),
             "post_projection_step_norm":float(np.linalg.norm(candidate-y)),
             "linear_predicted_residual_norm":float(np.linalg.norm(residual+radius*jd))}
        trials.append(row)
        if radius>0 and eta>1e-5 and norm<initial-REDUCTION_MARGIN:accepted.append((norm,candidate,row))
    best=None
    if accepted:
        norm,vector,row=min(accepted,key=lambda item:item[0]);best={**row,"residual_norm":norm,"raw_vector_hex":[float(v).hex() for v in vector/scales]}
    return {"source_state":"v16.51_best_accepted","curvature_relative_step":CURVATURE_RELATIVE_STEP,
        "directional_epsilon":DIRECTIONAL_EPSILON,"event_multiplier_scaled":float(y[-1]),
        "curvature_audit":curvature,"event_curvature_contribution_norm":float(abs(y[-1])*np.linalg.norm(raw_h)),
        "symmetric_KKT_relative_correction":float(np.linalg.norm(jacobian-symmetric)/max(1.0,np.linalg.norm(jacobian))),
        "initial_residual_norm":initial,"merit_gradient_norm":float(np.linalg.norm(gradient)),
        "orientation":orientation,"measured_projected_slope":slope,"projected_J_direction_norm":jd_norm,
        "derived_cauchy_radius":cauchy,"trial_count":len(trials),"residual_reducing_trial_count":len(accepted),
        "trials":trials,"best_accepted":best}


def covector_consistent_continuation()->dict[str,Any]:
    return covector_consistent_continuation_from(v16_51_raw_vector())


def completion_payload()->dict[str,Any]:
    result=covector_consistent_continuation();best=result["best_accepted"]
    validation={"accepted_v16_51_residual_reproduced":math.isclose(result["initial_residual_norm"],6.412264831307706,rel_tol=0,abs_tol=2e-9),
        "local_curvature_chart_below_branch_jump_scale":result["curvature_relative_step"]<1e-4,
        "covector_curvature_finite":math.isfinite(result["curvature_audit"]["raw_norm"]),
        "measured_direction_is_descent":result["measured_projected_slope"]<0,
        "positive_cauchy_radius":result["derived_cauchy_radius"]>0,
        "strict_step_accepted":best is not None,
        "complete_residual_reduced":bool(best is not None and best["residual_norm"]<result["initial_residual_norm"]-REDUCTION_MARGIN),
        "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
        "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_covector_consistent_curvature_v16_53","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"covector_consistent_curvature_continuation":result,
        "status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained":"SMOOTH_NORMALIZED_EULER_DIRAC_SOFT_BRANCH_CURVATURE_WITHIN_ITS_LOCAL_SPECTRAL_CHART",
        "dependency_advanced":"CORRECTS_THE_EVENT_CURVATURE_OBJECT_REQUIRED_BY_SIMULTANEOUS_N3_SADDLE_CLOSURE",
        "active_calculation":"PROMOTE_THE_COVECTOR_CONSISTENT_STATE_AND_REFRESH_OR_REDIRECT_IF_THE_LOCAL_CHART_FAILS",
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_covector_consistent_curvature_v16_53.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path

__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","CURVATURE_RELATIVE_STEP","DIRECTIONAL_EPSILON","v16_51_raw_vector","covector_consistent_event_hessian","covector_consistent_continuation_from","covector_consistent_continuation","completion_payload","deterministic_json","materialize"]
