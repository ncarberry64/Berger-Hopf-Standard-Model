"""Materialize the current-C2 reduced HS/fermion mixed variation."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));A=ROOT/"artifacts"
from bhsm.interface.ae3_c2_action_puzzle import reduced_product_dirac_hs_source_jet
from bhsm.interface.ae3_c2_hs_mixed_variation import ACTION_VERSION,CLASSIFICATION,claim_boundary,hs_kernel_candidate_screen,reduced_bilinear_variations
PUZZLE=A/"action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json";LOCALIZATION=A/"action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json";NPZ=A/"flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz";V1605=A/"BHSM_aether_common_gauge_hs_pushforward_v16_05.json";V1602=A/"BHSM_aether_hs_channel_normalization_v16_02.json";V1575=A/"BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json";V1572=A/"BHSM_aether_legendre_crossing_unified_condensation_v15_72.json"
TARGET=A/"action_extension/BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json"
INPUTS=(PUZZLE,LOCALIZATION,NPZ,V1605,V1602,V1575,V1572,ROOT/"src/bhsm/interface/ae3_c2_hs_mixed_variation.py")
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest().upper()
def build_payload()->dict[str,Any]:
 if missing:=[str(p) for p in INPUTS if not p.is_file()]:raise FileNotFoundError(", ".join(missing))
 puzzle,localization,v1605,v1602,v1575,v1572=map(load,(PUZZLE,LOCALIZATION,V1605,V1602,V1575,V1572));channels={}
 with np.load(NPZ) as data:
  h=np.asarray(data["segment_proper_duration_proof_center"],dtype=float)
  for chirality,suffix in ((1,"product_Dirac_lambda1_5_chirality_plus"),(-1,"product_Dirac_lambda1_5_chirality_minus")):
   W=np.asarray(data[f"{suffix}__element_coefficient"],dtype=float);jet=reduced_product_dirac_hs_source_jet(proper_durations=h,base_W=W,source_profile=np.ones_like(W));variation=reduced_bilinear_variations(vertex_diagonal=jet["vertex_diagonal"],vertex_off_diagonal=jet["vertex_off_diagonal"],contact_diagonal=jet["contact_diagonal"],contact_off_diagonal=jet["contact_off_diagonal"],fermion_background=np.zeros(W.size,dtype=complex));channels[suffix]={"chirality":chirality,**variation}
 screen=hs_kernel_candidate_screen();boundary=claim_boundary();validation={"current_C2_puzzle_valid":puzzle["validation_passed"] is True,"AE3_family_mode_fibers_preserved":localization["family_mode_C2_instantiation"]["certificate_passed"] is True,"family_mode_not_promoted_to_field_coordinate":localization["current_full_field_attachment"]["blocks"]["fermion"]["current_C2_coordinates_present"] is False,"both_zero_background_mixed_blocks_vanish":all(row["zero_background_mixed_Hessian_vanishes_exactly"] for row in channels.values()),"both_third_variation_vertices_nonzero":all(row["third_variation_vertex_frobenius_norm"]>0 for row in channels.values()),"both_contact_tensors_nonzero":all(row["fourth_variation_contact_frobenius_norm"]>0 for row in channels.values()),"historical_v16_05_wrong_saddle":v1605["claim_boundary"]["replacement_quantum_saddle_solved"] is False,"historical_v16_02_direction_unselected":v1602["claim_boundary"]["physical_single_Higgs_direction_selected"] is False,"first_order_EC_is_unattached_extension":v1575["first_order_parent_action"]["first_order_spin_connection_completion_historically_explicit"] is False and v1575["first_order_parent_action"]["new_continuous_coefficient"] is False,"historical_Lstar_not_diagonalized":v1572["claim_boundary"]["exact_L_star_numerically_diagonalized"] is False,"no_current_dynamic_HS_kernel":screen["attachable_count"]==0,"no_action_extension_silently_selected":screen["extension_requires_new_action_version_authority"],"spectrum_not_rebuilt":not boundary["particle_spectrum_rebuilt"]}
 return {"artifact":"BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION","action_version":ACTION_VERSION,"classification":CLASSIFICATION,"background":"CURRENT_ATTACHED_SYMMETRIC_C2_SLICE_WITH_NO_CLASSICAL_FERMION_COEFFICIENT_COORDINATE","reduced_variations":channels,"HS_kernel_candidate_screen":screen,"claim_boundary":boundary,"inputs":{str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in INPUTS},"validation":validation,"validation_passed":all(validation.values()),"FULL_BHSM_COMPLETE":False}
def main()->None:
 payload=build_payload()
 if not payload["validation_passed"]:raise SystemExit("current-C2 HS mixed-variation validation failed")
 TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(TARGET.relative_to(ROOT))
if __name__=="__main__":main()
