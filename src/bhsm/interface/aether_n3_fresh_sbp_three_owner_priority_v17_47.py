"""Bounded period/v0/log-scale continuation from validated v17.46."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any
import numpy as np
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import MARGIN, period_priority_family_from
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import parallel_sbp_physical_jacobian

VERSION="v17.47"
CLASSIFICATION="BHSM_N3_FRESH_SBP_PERIOD_V0_LOG_SCALE_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE=False
PRIORITY_PROFILES=((4.,12.,4.),(6.,16.,6.),(6.,16.,8.),(8.,20.,8.),
    (8.,24.,10.),(10.,24.,12.),(12.,28.,12.),(12.,32.,16.))

def v17_46_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_log_scale_priority_v17_46.json").read_text(encoding="utf-8"))
    h=p["fresh_sbp_second_log_scale_priority"]["selected_log_scale_priority_maximin"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(x) for x in h])
    if raw.shape!=(376,): raise ValueError("v17.46 selected vector has wrong dimension")
    return raw

def three_owner_priority()->dict[str,Any]:
    return period_priority_family_from(v17_46_selected_raw_vector(),
        source_state="v17.46_selected_second_log_scale_priority_state",
        priority_owner="period",additional_priority_owners=("v0","log_scale"),
        priority_key="period_v0_log_scale_profile",
        selection_key="selected_three_owner_priority_maximin",
        priority_profiles=PRIORITY_PROFILES,cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian)

def completion_payload()->dict[str,Any]:
    r=three_owner_priority(); best=r["selected_three_owner_priority_maximin"]
    profile=best.get("period_v0_log_scale_profile",{}) if best else {}
    v={
      "v17_46_residual_reproduced":math.isclose(r["initial_metrics"]["complete"],0.905943090332693,rel_tol=0,abs_tol=2e-8),
      "v17_46_event_reproduced":math.isclose(r["initial_metrics"]["event"],0.084408573065833,rel_tol=0,abs_tol=2e-8),
      "v17_46_period_reproduced":math.isclose(r["initial_metrics"]["period"],0.475657599035912,rel_tol=0,abs_tol=2e-8),
      "v17_46_v0_reproduced":math.isclose(r["initial_metrics"]["v0"],0.459766885614552,rel_tol=0,abs_tol=2e-8),
      "v17_46_log_scale_reproduced":math.isclose(r["initial_metrics"]["log_scale"],0.309368919828107,rel_tol=0,abs_tol=2e-8),
      "source_state_owned":r["source_state"]=="v17.46_selected_second_log_scale_priority_state",
      "three_owner_profile_owned":r.get("priority_owners")==["period","v0","log_scale"],
      "bounded_profiles_tested":r.get("priority_profiles_tested")==8,
      "selected_profile_owned":set(profile)=={"period","v0","log_scale"},
      "parallel_jacobian_adopted":r.get("assembly_workers")==8,
      "physical_equations_unchanged":not r["physical_residual_changed"] and not r["physical_event_changed"],
      "all_families_tested":r["family_count"]==7,"expanded_radius_grid_tested":len(RADII)==12,
      "common_direction_exists":r["common_direction_count"]>0,"strict_candidate_exists":best is not None,
      "all_six_metrics_reduced":bool(best is not None and all(x>MARGIN for x in best["reductions"].values())),
      "positive_maximin_progress":bool(best is not None and best["minimum_fractional_progress"]>0),
      "eta_domain_preserved":bool(best is not None and best["eta_minimum"]>1e-5),
      "full_precision_state_preserved":bool(best is not None and len(best["raw_vector_hex"])==376)}
    return {"artifact":"BHSM_aether_n3_fresh_sbp_three_owner_priority_v17_47","version":VERSION,
      "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"fresh_sbp_three_owner_priority":r,
      "status":"VALIDATED" if all(v.values()) else "RECLASSIFIED",
      "real_physical_property_explained":"SAME_ACTION_SIX_OWNER_DESCENT_WITH_BOUNDED_PERIOD_V0_LOG_SCALE_PRECONDITIONING",
      "dependency_advanced":"SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
      "active_calculation":"PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET","validation":v,"validation_passed":all(v.values())}

def materialize(directory:str|Path)->Path:
    t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_fresh_sbp_three_owner_priority_v17_47.json"
    p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p

__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","PRIORITY_PROFILES","v17_46_selected_raw_vector","three_owner_priority","completion_payload","materialize"]
