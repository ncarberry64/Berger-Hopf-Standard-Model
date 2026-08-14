"""Event/log-refined four-owner continuation from validated v17.48."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import MARGIN,period_priority_family_from
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import parallel_sbp_physical_jacobian
VERSION="v17.49";CLASSIFICATION="BHSM_N3_FRESH_SBP_REFINED_FOUR_OWNER_PRIORITY_FAMILY";FULL_BHSM_COMPLETE=False
PRIORITY_PROFILES=((10.,24.,16.,6.),(12.,28.,20.,8.),(12.,32.,24.,10.),(12.,32.,28.,12.),
 (14.,32.,32.,14.),(16.,36.,32.,16.),(16.,40.,40.,20.),(20.,48.,48.,24.))
def v17_48_selected_raw_vector()->np.ndarray:
 p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_four_owner_priority_v17_48.json").read_text(encoding="utf-8"));h=p["fresh_sbp_four_owner_priority"]["selected_four_owner_priority_maximin"]["raw_vector_hex"]
 raw=np.asarray([float.fromhex(x) for x in h]);
 if raw.shape!=(376,):raise ValueError("v17.48 selected vector has wrong dimension")
 return raw
def refined_four_owner()->dict[str,Any]:
 return period_priority_family_from(v17_48_selected_raw_vector(),source_state="v17.48_selected_four_owner_priority_state",priority_owner="period",additional_priority_owners=("v0","log_scale","event"),priority_key="four_owner_profile",selection_key="selected_refined_four_owner_maximin",priority_profiles=PRIORITY_PROFILES,cauchy_factors=RADII,jacobian_builder=parallel_sbp_physical_jacobian)
def completion_payload()->dict[str,Any]:
 r=refined_four_owner();b=r["selected_refined_four_owner_maximin"];p=b.get("four_owner_profile",{}) if b else {}
 v={"v17_48_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.856932797541498,rel_tol=0,abs_tol=2e-8),"v17_48_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.084045632483275,rel_tol=0,abs_tol=2e-8),"v17_48_period_reproduced":math.isclose(r["initial_metrics"]["period"],0.459410588927536,rel_tol=0,abs_tol=2e-8),"v17_48_v0_reproduced":math.isclose(r["initial_metrics"]["v0"],0.415294477026052,rel_tol=0,abs_tol=2e-8),"v17_48_log_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.298176934178732,rel_tol=0,abs_tol=2e-8),"source_state_owned":r["source_state"]=="v17.48_selected_four_owner_priority_state","four_owner_profile_owned":r.get("priority_owners")==["period","v0","log_scale","event"],"bounded_profiles_tested":r.get("priority_profiles_tested")==8,"selected_profile_owned":set(p)=={"period","v0","log_scale","event"},"parallel_jacobian_adopted":r.get("assembly_workers")==8,"physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],"all_families_tested":r["family_count"]==7,"expanded_radius_grid_tested":len(RADII)==12,"common_direction_exists":r["common_direction_count"]>0,"strict_candidate_exists":b is not None,"all_six_metrics_reduced":bool(b is not None and all(x>MARGIN for x in b["reductions"].values())),"positive_maximin_progress":bool(b is not None and b["minimum_fractional_progress"]>0),"eta_domain_preserved":bool(b is not None and b["eta_minimum"]>1e-5),"full_precision_state_preserved":bool(b is not None and len(b["raw_vector_hex"])==376)}
 return {"artifact":"BHSM_aether_n3_fresh_sbp_refined_four_owner_v17_49","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_refined_four_owner":r,"status":"VALIDATED" if all(v.values()) else "RECLASSIFIED","real_physical_property_explained":"SAME_ACTION_SIX_OWNER_DESCENT_WITH_EVENT_LOG_REFINED_FOUR_OWNER_PRECONDITIONING","dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE","active_calculation":"PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_refined_four_owner_v17_49.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","PRIORITY_PROFILES","v17_48_selected_raw_vector","refined_four_owner","completion_payload","materialize"]
