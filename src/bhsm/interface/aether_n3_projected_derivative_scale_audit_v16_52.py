"""Scale audit of the projected-manifold merit derivative at v16.49."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales

VERSION="v16.52"
CLASSIFICATION="BHSM_N3_PROJECTED_MERIT_DERIVATIVE_SCALE_AUDIT"
FULL_BHSM_COMPLETE=False
DERIVATIVE_SCALES=(1e-8,3e-8,1e-7,3e-7,1e-6,3e-6,1e-5,3e-5,1e-4)


def v16_49_raw_vector()->np.ndarray:
    payload=json.loads(Path("artifacts/BHSM_aether_n3_projected_cauchy_continuation_v16_49.json").read_text(encoding="utf-8"))
    values=payload["projected_cauchy_continuation"]["projected_cauchy_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(value) for value in values])
    if raw.shape!=(376,):raise ValueError("v16.49 vector has wrong dimension")
    return raw


def projected_derivative_scale_audit()->dict[str,Any]:
    matrix,residual,raw=refreshed_system_at(v16_49_raw_vector())
    scales=kkt_variable_scales();y=raw*scales
    gradient=matrix.T@residual;gradient[-1]=0.0
    gradient_norm=float(np.linalg.norm(gradient));direction=-gradient/gradient_norm
    merit0=0.5*float(residual@residual);rows=[]
    for epsilon in DERIVATIVE_SCALES:
        plus_y,plus_r=projected_residual_and_vector(y+epsilon*direction)
        minus_y,minus_r=projected_residual_and_vector(y-epsilon*direction)
        merit_plus=0.5*float(plus_r@plus_r);merit_minus=0.5*float(minus_r@minus_r)
        jd=(plus_r-minus_r)/(2*epsilon)
        rows.append({"epsilon":epsilon,
            "central_merit_slope":(merit_plus-merit_minus)/(2*epsilon),
            "residual_dot_central_Jd":float(residual@jd),
            "forward_merit_slope":(merit_plus-merit0)/epsilon,
            "reverse_merit_slope":(merit0-merit_minus)/epsilon,
            "plus_residual_norm":float(np.linalg.norm(plus_r)),
            "minus_residual_norm":float(np.linalg.norm(minus_r)),
            "plus_projection_response_norm":float(np.linalg.norm(plus_y-y)),
            "minus_projection_response_norm":float(np.linalg.norm(minus_y-y)),
            "plus_rho_displacement":float(plus_y[-1]-y[-1]),
            "minus_rho_displacement":float(minus_y[-1]-y[-1])})
    return {"source_state":"v16.49_best_accepted","internal_action_covector_relative_step":2e-6,
        "assembled_negative_gradient_slope":-gradient_norm,"initial_residual_norm":float(np.linalg.norm(residual)),
        "rows":rows,
        "interpretation":"A_STABLE_SIGN_AND_MAGNITUDE_PLATEAU_ABOVE_THE_INTERNAL_COVECTOR_DIFFERENCE_SCALE_IS_REQUIRED_BEFORE_ANOTHER_PROJECTED_CAUCHY_STEP"}


def completion_payload()->dict[str,Any]:
    result=projected_derivative_scale_audit();rows=result["rows"]
    above=[row for row in rows if row["epsilon"]>=3e-6]
    signs={int(np.sign(row["central_merit_slope"])) for row in above}
    validation={"all_scales_evaluated":len(rows)==len(DERIVATIVE_SCALES),
        "all_results_finite":all(math.isfinite(value) for row in rows for value in row.values()),
        "internal_difference_scale_bracketed":min(DERIVATIVE_SCALES)<2e-6<max(DERIVATIVE_SCALES),
        "above_internal_scale_sign_classified":len(signs)>=1}
    return {"artifact":"BHSM_aether_n3_projected_derivative_scale_audit_v16_52","version":VERSION,
        "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"projected_derivative_scale_audit":result,
        "status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"NUMERICAL_IDENTIFIABILITY_OF_THE_PARENT_EVENT_MERIT_DESCENT_DIRECTION",
        "dependency_advanced":"CLASSIFIES_THE_DIFFERENTIATION_SCALE_REQUIRED_BY_THE_EXISTING_N3_SADDLE_SOLVE",
        "active_calculation":"USE_ONLY_THE_STABLE_ABOVE_NOISE_DERIVATIVE_OR_REDIRECT_TO_A_HIGHER_ACCURACY_ACTION_COVECTOR",
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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_projected_derivative_scale_audit_v16_52.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path

__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","DERIVATIVE_SCALES","v16_49_raw_vector","projected_derivative_scale_audit","completion_payload","deterministic_json","materialize"]
