"""Contraction adequacy of coupled measured-tangent passes v17.41-v17.49."""
from __future__ import annotations
import json,math
from pathlib import Path
from typing import Any,Mapping
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
VERSION="v17.50";CLASSIFICATION="BHSM_N3_COUPLED_MEASURED_TANGENT_CONTRACTION_ADEQUACY_AUDIT";FULL_BHSM_COMPLETE=False;TOL=1e-6
SPECS=(
("v17.41","BHSM_aether_n3_fresh_sbp_coupled_period_v0_priority_v17_41.json","fresh_sbp_coupled_period_v0_priority","selected_coupled_period_v0_priority_maximin"),
("v17.42","BHSM_aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42.json","fresh_sbp_asymmetric_period_v0_priority","selected_asymmetric_period_v0_priority_maximin"),
("v17.43","BHSM_aether_n3_fresh_sbp_second_event_priority_v17_43.json","fresh_sbp_second_event_priority","selected_event_priority_maximin"),
("v17.44","BHSM_aether_n3_fresh_sbp_second_asymmetric_period_v0_v17_44.json","fresh_sbp_second_asymmetric_period_v0","selected_second_asymmetric_period_v0_maximin"),
("v17.45","BHSM_aether_n3_fresh_sbp_v0_heavier_period_v0_v17_45.json","fresh_sbp_v0_heavier_period_v0","selected_v0_heavier_period_v0_maximin"),
("v17.46","BHSM_aether_n3_fresh_sbp_second_log_scale_priority_v17_46.json","fresh_sbp_second_log_scale_priority","selected_log_scale_priority_maximin"),
("v17.47","BHSM_aether_n3_fresh_sbp_three_owner_priority_v17_47.json","fresh_sbp_three_owner_priority","selected_three_owner_priority_maximin"),
("v17.48","BHSM_aether_n3_fresh_sbp_four_owner_priority_v17_48.json","fresh_sbp_four_owner_priority","selected_four_owner_priority_maximin"),
("v17.49","BHSM_aether_n3_fresh_sbp_refined_four_owner_v17_49.json","fresh_sbp_refined_four_owner","selected_refined_four_owner_maximin"))
def coupled_contraction_audit()->dict[str,Any]:
 states=[]
 for ver,file,section,selection in SPECS:
  p=json.loads((Path("artifacts")/file).read_text(encoding="utf-8"));s=p[section][selection]
  states.append({"version":ver,"validation_passed":bool(p["validation_passed"]),"metrics":s["metrics"],"minimum_fractional_progress":s["minimum_fractional_progress"],"limiting_owner":s["limiting_owner"]})
 n=len(states)-1;owners=tuple(states[0]["metrics"]);contraction={}
 for o in owners:
  initial=float(states[0]["metrics"][o]);final=float(states[-1]["metrics"][o]);ratio=(final/initial)**(1/n)
  projected=math.ceil(math.log(TOL/final)/math.log(ratio)) if 0<ratio<1 and final>TOL else 0
  contraction[o]={"initial":initial,"final":final,"ratio_per_pass":ratio,"cumulative_fractional_reduction":1-final/initial,"constant_rate_projected_additional_passes":projected}
 bottleneck=max(contraction,key=lambda o:contraction[o]["constant_rate_projected_additional_passes"])
 return {"states":states,"promoted_passes":n,"closure_tolerance":TOL,"contraction_by_owner":contraction,"extrapolation_bottleneck":bottleneck,"projected_additional_passes":contraction[bottleneck]["constant_rate_projected_additional_passes"],"classification_scope":"EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO","interpretation":"COUPLED_MEASURED_TANGENT_PASSES_ADVANCE_GEOMETRY_BUT_EVENT_CONTRACTION_REMAINS_INADEQUATE_FOR_DIRECT_COMPLETION"}
def completion_payload()->dict[str,Any]:
 r=coupled_contraction_audit();v={"nine_validated_states_loaded":len(r["states"])==9 and all(s["validation_passed"] for s in r["states"]),"eight_passes_measured":r["promoted_passes"]==8,"final_residual_reproduced":math.isclose(r["contraction_by_owner"]["complete"]["final"],0.855054105118296,rel_tol=0,abs_tol=2e-8),"event_is_extrapolation_bottleneck":r["extrapolation_bottleneck"]=="event","more_than_one_thousand_projected_passes":r["projected_additional_passes"]>1000,"no_mathematical_no_go_claimed":r["classification_scope"]=="EMPIRICAL_ADEQUACY_NOT_MATHEMATICAL_NO_GO"}
 return {"artifact":"BHSM_aether_n3_coupled_contraction_audit_v17_50","version":VERSION,"classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"coupled_contraction_audit":r,"status":"RECLASSIFIED" if all(v.values()) else "INVALIDATED","dependency_advanced":"REASSESS_EVENT_CLOSURE_DIRECTION_BEFORE_MORE_COUPLED_TANGENT_REPETITION","active_calculation":"DERIVE_A_SAME_ACTION_SOFT_EIGENVALUE_CONSTRAINED_EVENT_CORRECTION_WITH_ORIGINAL_SIX_OWNER_ACCEPTANCE","validation":v,"validation_passed":all(v.values())}
def materialize(directory:str|Path)->Path:
 t=Path(directory);t.mkdir(parents=True,exist_ok=True);p=t/"BHSM_aether_n3_coupled_contraction_audit_v17_50.json";p.write_text(deterministic_json(completion_payload()),encoding="utf-8");return p
__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","coupled_contraction_audit","completion_payload","materialize"]
