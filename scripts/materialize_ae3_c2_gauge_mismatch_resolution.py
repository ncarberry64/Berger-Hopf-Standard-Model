"""Materialize the finite current-C2 gauge mismatch resolution screen."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from bhsm.interface.ae3_c2_gauge_mismatch_resolution import ACTION_VERSION,CLASSIFICATION,SELECTED_ROUTE,exterior_calderon_contract,selection_certificate
A=ROOT/"artifacts"
TARGET=A/"action_extension/BHSM_AE3_C2_GAUGE_MISMATCH_RESOLUTION_SCREEN.json"
INPUTS=(A/"action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",A/"action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",A/"BHSM_action_attachment_wentzell_v14_67.json",A/"BHSM_aether_n3_event_attachment_state_incidence_v17_89.json",A/"BHSM_aether_n3_dynamic_child_wentzell_cauchy_v17_90.json",A/"BHSM_action_sector_provenance_v14_61.json",ROOT/"src/bhsm/interface/ae3_c2_gauge_mismatch_resolution.py")
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest().upper()
def build_payload()->dict[str,Any]:
    if m:=[str(p) for p in INPUTS if not p.is_file()]:raise FileNotFoundError(", ".join(m))
    ae3,h,w,i,d,s=map(load,INPUTS[:6]); cert=selection_certificate(); contract=exterior_calderon_contract()
    validation={"AE3_same_action_valid":ae3["validation_passed"] is True,"AE3_surface_contact_exactly_zero":ae3["euler_lagrange_and_interface_variation"]["surface_contact_term"] is None,"current_Hessian_mismatch_valid":h["validation_passed"] is True and h["decision"]["Z_t_equals_Z_s"] is False,"v14_67_not_unconditional_physical":w["provenance_gate"]["all_physical_provenance_inputs_present"] is False,"v17_dynamic_Wentzell_templates_valid":i["validation_passed"] is True and d["validation_passed"] is True,"relative_spectral_sector_not_ready":s["all_physical_coefficients_and_operators_ready"] is False,"unique_route":cert["certificate_passed"],"no_contact_or_coefficient_added":contract["surface_contact_term"] is None,"photon_not_promoted":not contract["physical_photon_derived"]}
    return {"artifact":"BHSM_AE3_C2_GAUGE_MISMATCH_RESOLUTION_SCREEN","action_version":ACTION_VERSION,"classification":CLASSIFICATION,"selection":cert,"selected_route_contract":contract,"scientific_result":"THE_ONLY_CURRENTLY_ADMISSIBLE_COEFFICIENT_FREE_ROUTE_IS_THE_TWO_SIDED_PARENT_CALDERON_SCHUR_COMPLEMENT;_THE_ACTUAL_CURRENT_C2_EXTERIOR_OPERATOR_IS_NOT_YET_DERIVED","claim_boundary":{"finite_route_screen_complete":True,"exterior_Calderon_operator_derived":False,"Lorentzian_Maxwell_residue_derived":False,"physical_photon_derived":False},"inputs":{str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in INPUTS},"validation":validation,"validation_passed":all(validation.values()),"FULL_BHSM_COMPLETE":False}
def main()->None:
 p=build_payload();
 if not p["validation_passed"]:raise SystemExit("gauge mismatch screen failed")
 TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(TARGET.relative_to(ROOT))
if __name__=="__main__":main()
