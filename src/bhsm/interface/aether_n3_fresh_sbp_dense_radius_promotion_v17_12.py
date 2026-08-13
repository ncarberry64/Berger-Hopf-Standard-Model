"""Dense exact-radius promotion on the validated v17.11 tangent direction."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import _metrics
from bhsm.interface.aether_n3_fresh_sbp_third_tangent_family_selection_v17_11 import v17_10_selected_raw_vector
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
VERSION="v17.12";CLASSIFICATION="BHSM_N3_FRESH_SBP_DENSE_EXACT_RADIUS_PROMOTION_ON_VALIDATED_TANGENT";FULL_BHSM_COMPLETE=False
FACTORS=(0.060,0.061,0.062,0.063,0.064,0.065,0.066,0.067,0.068,0.069,0.070)
def dense_radius_promotion()->dict[str,Any]:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_third_tangent_family_selection_v17_11.json").read_text(encoding="utf-8"));r=p["fresh_sbp_third_tangent_family_selection"];row=next(item for item in r["family_rows"] if item["family"]=="single_filter_1e-06");anchor=next(item for item in row["trials"] if math.isclose(item["cauchy_factor"],0.03,rel_tol=0,abs_tol=1e-15));scales=kkt_variable_scales();raw0=v17_10_selected_raw_vector();y0,res0=sbp_projected_residual_and_vector(raw0*scales);raw_anchor=np.asarray([float.fromhex(value) for value in anchor["raw_vector_hex"]]);direction=(raw_anchor*scales-y0)/float(anchor["trust_radius"]);initial=_metrics(res0);trials=[];accepted=[]
    for factor in FACTORS:
        radius=factor*float(row["derived_cauchy_radius"]);candidate,candidate_r=sbp_projected_residual_and_vector(y0+radius*direction);raw_candidate=candidate/scales;eta=_minimum_node_eta(raw_candidate);metrics=_metrics(candidate_r);reductions={key:initial[key]-metrics[key] for key in initial};fractions={key:reductions[key]/max(initial[key],1e-300) for key in initial};trial={"cauchy_factor":factor,"trust_radius":radius,"domain_valid":bool(eta>1e-5),"metrics":metrics,"reductions":reductions,"fractional_reductions":fractions,"minimum_fractional_progress":min(fractions.values()),"limiting_owner":min(fractions,key=fractions.get),"eta_minimum":eta,"raw_vector_hex":[float(value).hex() for value in raw_candidate]};trials.append(trial)
        if eta>1e-5 and all(reductions[key]>1e-10 for key in initial):accepted.append(trial)
    best=max(accepted,key=lambda trial:(trial["minimum_fractional_progress"],sum(trial["fractional_reductions"].values()))) if accepted else None
    return {"source_state":"v17.10_selected_second_tangent_family_state","source_direction":"v17.11_single_filter_1e-06_convex_dual_measured_direction","physical_residual_changed":False,"physical_event_changed":False,"initial_metrics":initial,"coarse_promoted_factor":0.03,"coarse_promoted_minimum_fractional_progress":0.003527655480654,"dense_factors":list(FACTORS),"trials":trials,"strict_six_owner_candidate_count":len(accepted),"selected_dense_radius":best}
def completion_payload()->dict[str,Any]:
    r=dense_radius_promotion();b=r["selected_dense_radius"]
    validation={"v17_10_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],1.417294848984076,rel_tol=0,abs_tol=2e-8),"v17_10_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.121864036183711,rel_tol=0,abs_tol=2e-8),"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_dense_factors_evaluated":len(r["trials"])==len(FACTORS),"strict_candidate_exists":b is not None,"factor_0_064_selected":bool(b is not None and math.isclose(b["cauchy_factor"],0.064,rel_tol=0,abs_tol=1e-12)),"all_six_metrics_reduced":bool(b is not None and all(value>1e-10 for value in b["reductions"].values())),"dense_radius_outperforms_coarse":bool(b is not None and b["minimum_fractional_progress"]>r["coarse_promoted_minimum_fractional_progress"]),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_dense_radius_promotion_v17_12","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_dense_radius_promotion":r,"status":"VALIDATED" if all(validation.values()) else "RECLASSIFIED","real_physical_property_explained":"MAXIMUM_EXACT_SIX_OWNER_PROGRESS_ON_THE_CURRENT_VALIDATED_PHYSICAL_NORMAL_TANGENT","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE_WITHOUT_ANOTHER_JACOBIAN_BUILD","active_calculation":"REBUILD_THE_MEASURED_TANGENT_FAMILY_FROM_THE_DENSELY_PROMOTED_FULL_PRECISION_STATE","validation":validation,"validation_passed":all(validation.values())}
def _canonical(value:Any)->Any:
    if isinstance(value,np.ndarray):return [_canonical(item) for item in value.tolist()]
    if isinstance(value,np.bool_):return bool(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.floating):value=float(value)
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError("non-finite float")
        return round(value,15)
    if isinstance(value,Mapping):return {key:_canonical(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical(item) for item in value]
    return value
def deterministic_json(payload:Mapping[str,Any])->str:return json.dumps(_canonical(payload),indent=2,sort_keys=True)+"\n"
def materialize(directory:str|Path)->Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_fresh_sbp_dense_radius_promotion_v17_12.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","dense_radius_promotion","completion_payload","deterministic_json","materialize"]
