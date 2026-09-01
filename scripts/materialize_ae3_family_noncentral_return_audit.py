"""Materialize the AE3 family-noncentral return provenance audit."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));A=ROOT/"artifacts"
from bhsm.interface.ae3_family_noncentral_return_audit import ACTION_VERSION,CLASSIFICATION,audit_certificate,irreducible_family_decision_surface
TARGET=A/"action_extension/BHSM_AE3_FAMILY_NONCENTRAL_RETURN_PROVENANCE_AUDIT.json"
INPUTS=(A/"action_extension/BHSM_AE3_FAMILY_HIERARCHY_INTERFACE.json",A/"BHSM_triality_Berger_family_mass_operator_v6_3_0.json",A/"BHSM_canonical_C3_attachment_family_chain_no_go_v14_38.json",A/"BHSM_junction_invariant_and_triality_commutant_v6_10_0.json",A/"BHSM_family_coherence_circularity_gate_v14_40.json",A/"BHSM_lambda85_family_projection_no_go_v14_52.json",A/"BHSM_family_generation_band_gate_v14_79.json",A/"BHSM_aether_hybrid_yukawa_mass_semantics_v15_56.json",A/"BHSM_aether_cycle_family_centrality_v15_87.json",ROOT/"src/bhsm/interface/ae3_family_noncentral_return_audit.py")
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest().upper()
def build_payload()->dict[str,Any]:
 if missing:=[str(p) for p in INPUTS if not p.is_file()]:raise FileNotFoundError(", ".join(missing))
 hierarchy,mass,c3,junction,coherence,lambda85,bands,wilson,cycle=map(load,INPUTS[:9]);audit=audit_certificate();decision=irreducible_family_decision_surface()
 validation={"current_hierarchy_predecessor_valid":hierarchy["validation_passed"] is True,"conditional_v6_mass_not_promoted":mass["dressed_candidate_status_preserved"]=="CANDIDATE" and not mass["absolute_masses_derived"],"canonical_projection_twofold_degenerate":c3["validation"]["twofold_degeneracy_preserved"],"optional_junction_term_absent":junction["triality"]["coefficients_fixed"]==[] and not junction["physical_bulk_Dirac_parent_law_introduced"],"coherence_source_is_circular":coherence["validation"]["using_unowned_coherence_as_mixing_source_is_circular"],"lambda85_family_blind":lambda85["validation"]["C3_equivariant_operator_is_character_diagonal"],"band_mass_spectrum_open":bands["mass_spectrum_status"].startswith("OPEN_"),"intrinsic_Wilson_entries_underived":not wilson["claim_boundary"]["intrinsic_Yukawa_Wilson_matrices_derived"],"current_cycle_family_central":cycle["claim_boundary"]["family_centrality_derived"] and not cycle["claim_boundary"]["family_hierarchy_derived"],"no_admissible_retained_candidate":audit["admissible_count"]==0,"no_action_choice_fabricated":not decision["choice_made_here"],"spectrum_not_rebuilt":not audit["particle_spectrum_rebuilt"]}
 return {"artifact":"BHSM_AE3_FAMILY_NONCENTRAL_RETURN_PROVENANCE_AUDIT","action_version":ACTION_VERSION,"classification":CLASSIFICATION,"audit":audit,"irreducible_family_decision_surface":decision,"claim_boundary":{"family_modes_preserved":True,"family_mass_hierarchy_derived":False,"CKM_PMNS_derived":False},"inputs":{str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in INPUTS},"validation":validation,"validation_passed":all(validation.values()),"FULL_BHSM_COMPLETE":False}
def main()->None:
 payload=build_payload()
 if not payload["validation_passed"]:raise SystemExit("family return audit failed")
 TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(TARGET.relative_to(ROOT))
if __name__=="__main__":main()
