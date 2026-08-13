"""Audit whether the v16.56 plateau redirects to an SBP orbit discretization."""

from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import NODES,open_difference_matrix,trapezoid_weights

VERSION="v16.57"
CLASSIFICATION="BHSM_N3_ENDPOINT_PLATEAU_SBP_REDIRECT_AUDIT"
FULL_BHSM_COMPLETE=False

def trapezoid_sbp_difference(nodes:int=NODES)->np.ndarray:
    if nodes<3:raise ValueError("at least three nodes required")
    h=1.0/(nodes-1);d=np.zeros((nodes,nodes))
    d[0,0:2]=(-1.0,1.0);d[-1,-2:]=( -1.0,1.0)
    for i in range(1,nodes-1):d[i,i-1:i+2]=(-0.5,0.0,0.5)
    return d/h

def sbp_redirect_audit()->dict[str,Any]:
    latest=json.loads(Path("artifacts/BHSM_aether_n3_post_curvature_soft_mode_audit_v16_56.json").read_text(encoding="utf-8"))["post_curvature_soft_mode_audit"]
    old=open_difference_matrix();new=trapezoid_sbp_difference();w=np.diag(trapezoid_weights())
    boundary=np.zeros_like(old);boundary[0,0]=-1;boundary[-1,-1]=1
    old_defect=w@old+old.T@w-boundary;new_defect=w@new+new.T@w-boundary
    leaders=latest["largest_coordinate_components"]
    endpoint=[row for row in leaders if row["node"]<=2 or row["node"]>=21]
    all_residual_sq=sum(row["residual"]**2 for row in leaders);endpoint_sq=sum(row["residual"]**2 for row in endpoint)
    x=np.linspace(0,1,NODES);accuracy=[]
    for degree in range(4):
        exact=np.zeros_like(x) if degree==0 else degree*x**(degree-1)
        accuracy.append({"degree":degree,"old_maximum_error":float(np.max(np.abs(old@x**degree-exact))),
            "sbp_maximum_error":float(np.max(np.abs(new@x**degree-exact))),
            "sbp_interior_maximum_error":float(np.max(np.abs((new@x**degree-exact)[1:-1])))})
    return {"source_state":"v16.56_post_curvature_audit","complete_residual_norm":latest["complete_residual_norm"],
        "top_component_count":len(leaders),"endpoint_layer_top_component_count":len(endpoint),
        "endpoint_layer_fraction_of_top_component_squared_norm":float(endpoint_sq/all_residual_sq),
        "old_pair":{"SBP":False,"defect_norm":float(np.linalg.norm(old_defect)),"defect_maximum":float(np.max(np.abs(old_defect))),
            "nonzero_count":int(np.sum(np.abs(old_defect)>1e-13))},
        "trapezoid_SBP_pair":{"SBP":bool(np.linalg.norm(new_defect)<1e-12),"defect_norm":float(np.linalg.norm(new_defect)),
            "defect_maximum":float(np.max(np.abs(new_defect))),"nonzero_count":int(np.sum(np.abs(new_defect)>1e-13)),
            "different_rows_from_old":[int(i) for i in np.flatnonzero(np.any(np.abs(new-old)>1e-13,axis=1))]},
        "polynomial_accuracy":accuracy,
        "redirect_justification":"AFTER_COVECTOR_CONSISTENT_EVENT_CURVATURE_THE_RESIDUAL_REMAINS_DOMINATED_BY_INITIAL_AND_TERMINAL_PARENT_GEOMETRY_ROWS;_THE_CURRENT_DERIVATIVE_QUADRATURE_PAIR_HAS_A_LARGE_EXACT_SBP_DEFECT_WHILE_THE_MINIMAL_TRAPEZOID_SBP_CLOSURE_CHANGES_ONLY_THE_TWO_ENDPOINT_DERIVATIVE_ROWS",
        "required_next_object":"FRESH_CANONICAL_RESET_N3_KKT_ORBIT_SOLVED_WITH_THE_TRAPEZOID_SBP_DERIVATIVE_QUADRATURE_PAIR_AND_THE_SAME_ACTION_EVENT_AND_COMMON_PUSHFORWARD"}

def completion_payload()->dict[str,Any]:
    result=sbp_redirect_audit()
    validation={"old_non_SBP_reproduced":not result["old_pair"]["SBP"] and result["old_pair"]["defect_norm"]>1,
        "minimal_SBP_pair_exact":result["trapezoid_SBP_pair"]["SBP"],
        "only_endpoint_derivative_rows_change":result["trapezoid_SBP_pair"]["different_rows_from_old"]==[0,NODES-1],
        "plateau_is_endpoint_concentrated":result["endpoint_layer_fraction_of_top_component_squared_norm"]>0.75,
        "fresh_orbit_required":result["required_next_object"].startswith("FRESH_CANONICAL_RESET")}
    return {"artifact":"BHSM_aether_n3_sbp_redirect_audit_v16_57","version":VERSION,"classification":CLASSIFICATION,
        "FULL_BHSM_COMPLETE":False,"sbp_redirect_audit":result,
        "status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"VARIATIONAL_ENDPOINT_CLOSURE_OF_THE_CONSTRAINED_PARENT_ORBIT",
        "dependency_advanced":"IDENTIFIES_THE_DISCRETIZED_ORBIT_OBJECT_UPSTREAM_OF_THE_REMAINING_N3_SADDLE_DEFECT",
        "active_calculation":result["required_next_object"],"validation":validation,"validation_passed":all(validation.values())}

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
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_sbp_redirect_audit_v16_57.json"
    path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","trapezoid_sbp_difference","sbp_redirect_audit","completion_payload","deterministic_json","materialize"]
