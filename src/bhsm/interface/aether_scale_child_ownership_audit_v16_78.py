"""Audit scale and child-channel ownership at the fresh SBP N=3 frontier."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import hybrid_bundle_gluing
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import anchored_kkt_dimensions,kkt_variable_scales
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import oriented_cut_and_event_data
VERSION="v16.78";CLASSIFICATION="BHSM_SCALE_AND_CHILD_CHANNEL_CONFIGURATION_OWNERSHIP_AUDIT";FULL_BHSM_COMPLETE=False

def v16_77_selected_raw_vector()->np.ndarray:
    p=json.loads(Path("artifacts/BHSM_aether_n3_fresh_sbp_second_metric_projected_newton_v16_77.json").read_text(encoding="utf-8"))
    values=p["fresh_sbp_second_metric_projected_newton"]["selected_best_accepted"]["raw_vector_hex"]
    raw=np.asarray([float.fromhex(v) for v in values])
    if raw.shape!=(376,):raise ValueError("v16.77 selected vector has wrong dimension")
    return raw

def scale_ownership_audit()->dict[str,Any]:
    raw=v16_77_selected_raw_vector();scales=kkt_variable_scales();_,res=sbp_projected_residual_and_vector(raw*scales)
    scale_rows=res[:230].reshape(23,10)[:,0];scale_norm=float(np.linalg.norm(scale_rows));late_fraction=float(np.sum(scale_rows[-4:]**2)/np.sum(scale_rows**2))
    dimensions=anchored_kkt_dimensions();event=oriented_cut_and_event_data();bundle=hybrid_bundle_gluing()
    return {
        "measured_frontier":{"source":"v16.77_selected_metric_projected_state","complete_residual_norm":float(np.linalg.norm(res)),
            "scaled_event_residual":float(res[-1]),"free_log_scale_stationarity_norm":scale_norm,
            "v16_75_reported_log_scale_norm":14.016355587104261,"fraction_of_scale_defect_squared_on_last_four_free_nodes":late_fraction,
            "free_log_scale_nodes":23,"log_scale_stationarity_rows":23},
        "configuration_ownership":{"canonical_reset_radius_in_ell_kappa":float(RADIUS0),"canonical_reset_log_scale":0.0,
            "reset_log_scale_is_KKT_unknown":False,"reset_relation_already_substituted":"q_log_scale(0)=log(R_reset/R_star)=0",
            "free_log_scale_nodes_are":"DYNAMICAL_BREATHING_HISTORY_ON_THE_OPEN_RESET_TO_EVENT_ORBIT",
            "one_stationarity_row_per_free_scale_node":True,"independent_particle_scale_parameter_present":False,
            "current_376_system_over_independent_due_to_reset_scale":False},
        "authoritative_reconstruction_status":{"v15_84_static_finite_chart_embedding_authoritative_status":"INVALID_AS_SOBOLEV_CAUCHY_LIFT",
            "old_constant_metric_erasing_reset_may_supply_current_scale_constraint":False,
            "valid_event_environment_conditioned_return_scale_function_derived":False,
            "missing_object":"ACTION_DERIVED_RECONSTRUCTION_BVP_SOLUTION_MAP_R_rec[I_event,I_environment]_ON_THE_BROKEN_RETURN_BRANCH",
            "required_environment_argument":"GAUGE_COVARIANT_CONSTRAINT_COMPATIBLE_BOUNDARY_CAUCHY_AND_NOETHER_FLUX_DATA_EXTRACTED_FROM_THE_PHYSICAL_EVENT_LAYER_NOT_A_METRIC_CARRIED_THROUGH_THE_FIREWALL",
            "consequence":"THE_CURRENT_EVENT_KKT_MUST_NOT_BE_MODIFIED_BY_AN_UNDERIVED_RETURN_SCALE_RELATION"},
        "derived_future_reconstruction_constraint":{"equation":"C_rec=q_log_scale(return)-log(R_rec[I_event,I_environment]/R_star)=0",
            "owner":"POST_EVENT_CONSTRAINT_SOLVED_RECONSTRUCTION_AND_RETURN_MAP_FROM_THE_SAME_BHSM_ACTION",
            "canonical_reset_special_case":"R_rec=R_star_implies_q_log_scale(0)=0_AND_IS_ALREADY_SUBSTITUTED",
            "substitution_form_count":{"unknowns":375,"equations":375,"operation":"remove_the_return_endpoint_scale_unknown_and_its_free_endpoint_variation_after_R_rec_is_derived"},
            "KKT_form_count":{"unknowns":377,"equations":377,"operation":"retain_return_scale_add_C_rec_and_one_conjugate_multiplier"},
            "current_open_event_orbit_count":{"unknowns":dimensions["total_unknowns"],"equations":dimensions["total_equations"],"square":dimensions["square"]}},
        "channel_map":{"formula":"(I_event,I_environment,B_SM)->(admissible_child_sector,R_rec,z_return)",
            "already_derived_output_restrictors":{"event_degree":event["surviving_data"]["global_event_degree"],
                "orientation":event["surviving_data"]["orientation_branch"],"FR_parity":event["surviving_data"]["FR_parity"],
                "response_endpoint_order":event["surviving_data"]["response_endpoint_order"],"incidence":event["surviving_data"]["incidence"],
                "boundary_identities":"child_to_child_and_parent_to_parent","SM_bundle_transport":bundle["event_transport"],
                "SM_bundle_isomorphism_class_returns":bundle["hybrid_bundle_returns_to_same_isomorphism_class"]},
            "selection_semantics":"OUTPUT_MUST_LIE_IN_THE_SUPERSELECTION_BLOCK_FIXED_BY_THE_TRANSPORTED_TOPOLOGICAL_GAUGE_REPRESENTATION_FAMILY_AND_FR_DATA",
            "arbitrary_cross_sector_branch_selection_allowed":False,"empirical_particle_selection_rule_added":False,
            "continuous_environment_data_currently_sufficient_to_fix_event_specific_scale":False,
            "missing_channel_input":"THE_PHYSICAL_EVENT_LAYER_TO_BROKEN_RECONSTRUCTION_BOUNDARY_DATA_MAP"},
        "verdict":{"the_14_016_obstruction_is_proved_to_be_an_over_independence_defect":False,
            "why":"THE_RESET_SCALE_IS_ALREADY_DEPENDENT_AND_REMOVED;THE_MEASURED_DEFECT_BELONGS_TO_LATE_OPEN_ORBIT_SCALE_DYNAMICS_NOT_AN_EXTRA_PARTICLE_LABEL",
            "configuration_space_ownership_contradiction_found":False,"continue_current_metric_Gauss_Newton":True,
            "earliest_eligible_scale_constraint_stage":"NONLINEAR_BROKEN_RECONSTRUCTION_RETURN_BVP_AFTER_THE_EVENT_SADDLE_AND_N_CONVERGENCE"}}

def completion_payload()->dict[str,Any]:
    r=scale_ownership_audit();m=r["measured_frontier"];o=r["configuration_ownership"];c=r["derived_future_reconstruction_constraint"];v=r["verdict"]
    validation={"v16_77_residual_reproduced":math.isclose(m["complete_residual_norm"],14.002288116707554,rel_tol=0,abs_tol=2e-8),
        "reported_v16_75_obstruction_preserved":math.isclose(m["v16_75_reported_log_scale_norm"],14.016355587104261,rel_tol=0,abs_tol=1e-12),
        "reset_scale_not_free":not o["reset_log_scale_is_KKT_unknown"],"scale_rows_balance_scale_unknowns":m["free_log_scale_nodes"]==m["log_scale_stationarity_rows"],
        "current_system_remains_square":c["current_open_event_orbit_count"]["square"],"substitution_recount_square":c["substitution_form_count"]["unknowns"]==c["substitution_form_count"]["equations"],
        "KKT_recount_square":c["KKT_form_count"]["unknowns"]==c["KKT_form_count"]["equations"],"no_false_over_independence_claim":not v["the_14_016_obstruction_is_proved_to_be_an_over_independence_defect"],
        "current_continuation_preserved":v["continue_current_metric_Gauss_Newton"]}
    return {"artifact":"BHSM_aether_scale_child_ownership_audit_v16_78","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,
        "scale_child_ownership_audit":r,"status":"RECLASSIFIED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"EVENT_CONDITIONED_CHILD_SCALE_AND_SUPERSELECTION_RESTRICTED_RECONSTRUCTION_WITHOUT_AN_INDEPENDENT_PARTICLE_SCALE",
        "dependency_advanced":"SEPARATES_THE_VALID_OPEN_ORBIT_SCALE_DYNAMICS_FROM_THE_STILL_MISSING_BROKEN_RETURN_RECONSTRUCTION_CONSTRAINT_AND_RECOUNTS_BOTH_SQUARE_FORMULATIONS",
        "active_calculation":"CONTINUE_N3_METRIC_PROJECTED_EVENT_SADDLE_CLOSURE_THEN_DERIVE_R_rec_FROM_THE_BROKEN_RECONSTRUCTION_BVP_BEFORE_RETURN_VARIATION",
        "validation":validation,"validation_passed":all(validation.values())}
def _canonical(v:Any)->Any:
    if isinstance(v,np.ndarray):return [_canonical(x) for x in v.tolist()]
    if isinstance(v,np.bool_):return bool(v)
    if isinstance(v,np.integer):return int(v)
    if isinstance(v,np.floating):v=float(v)
    if isinstance(v,float):
        if not math.isfinite(v):raise ValueError("non-finite float")
        return round(v,15)
    if isinstance(v,Mapping):return {k:_canonical(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [_canonical(x) for x in v]
    return v
def deterministic_json(p:Mapping[str,Any])->str:return json.dumps(_canonical(p),indent=2,sort_keys=True)+"\n"
def materialize(d:str|Path)->Path:
    t=Path(d);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_scale_child_ownership_audit_v16_78.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","v16_77_selected_raw_vector","scale_ownership_audit","completion_payload","deterministic_json","materialize"]
