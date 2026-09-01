"""Materialize the reciprocal two-sided Calderon no-go."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));A=ROOT/"artifacts"
from bhsm.interface.ae3_c2_two_sided_calderon import ACTION_VERSION,CLASSIFICATION,irreducible_decision_surface,operator_domain_transport_certificate,reflection_certificate,two_sided_residue_certificate
TARGET=A/"action_extension/BHSM_AE3_C2_TWO_SIDED_CALDERON_REFLECTION_NO_GO.json"
INPUTS=(A/"action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",A/"action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",A/"action_extension/BHSM_AE3_C2_GAUGE_MISMATCH_RESOLUTION_SCREEN.json",ROOT/"src/bhsm/interface/ae3_c2_two_sided_calderon.py")
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest().upper()
def build_payload()->dict[str,Any]:
 if m:=[str(p) for p in INPUTS if not p.is_file()]:raise FileNotFoundError(", ".join(m))
 ae3,h,screen=map(load,INPUTS[:3]);r=reflection_certificate();o=operator_domain_transport_certificate();t=two_sided_residue_certificate();d=irreducible_decision_surface()
 v={"AE3_valid":ae3["validation_passed"] is True,"inside_Hessian_valid":h["validation_passed"] is True,"selected_route_predecessor_valid":screen["validation_passed"] is True and screen["selection"]["selected_route"]=="TWO_SIDED_CURRENT_C2_PARENT_CALDERON_SCHUR_COMPLEMENT","reciprocal_reflection_exact":r["reflection_isometry_exact"],"reflection_numerical_audit_passed":r["numerical_audit_passed"],"full_regular_domain_transported":o["full_regular_domain_transport_derived"],"zero_surface_contact_retained":o["surface_contact_term"] is None,"exterior_equals_inside":t["N_exterior_zero"]==t["N_inside_zero"],"two_sided_ratio_unchanged":t["Zt_over_Zs_two_sided"]==t["Zt_over_Zs_inside"],"mismatch_remains_strict":0<t["Zt_over_Zs_two_sided"]<1,"no_retained_route_left":d["coefficient_free_retained_routes_remaining"]==0,"choice_not_fabricated":not d["choice_made_here"],"photon_not_promoted":not d["physical_photon_derived"]}
 return {"artifact":"BHSM_AE3_C2_TWO_SIDED_CALDERON_REFLECTION_NO_GO","action_version":ACTION_VERSION,"classification":CLASSIFICATION,"reflection":r,"operator_domain_transport":o,"two_sided_residue":t,"irreducible_physical_theory_decision_surface":d,"claim_boundary":{"two_sided_parent_Calderon_evaluated":True,"Lorentzian_Maxwell_residue_derived":False,"physical_photon_derived":False},"inputs":{str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in INPUTS},"validation":v,"validation_passed":all(v.values()),"FULL_BHSM_COMPLETE":False}
def main()->None:
 p=build_payload();
 if not p["validation_passed"]:raise SystemExit("two-sided Calderon validation failed")
 TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(TARGET.relative_to(ROOT))
if __name__=="__main__":main()
