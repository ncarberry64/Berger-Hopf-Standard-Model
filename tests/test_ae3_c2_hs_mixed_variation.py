import hashlib
import numpy as np
from bhsm.interface.ae3_c2_hs_mixed_variation import claim_boundary,hs_kernel_candidate_screen,reduced_bilinear_variations
from bhsm.interface.ae3_reciprocal_join_localization import systems_integration_puzzle
from scripts.materialize_ae3_c2_hs_mixed_variation import TARGET,build_payload,main
def variation(background):
 return reduced_bilinear_variations(vertex_diagonal=np.asarray((2.,3.,4.)),vertex_off_diagonal=np.asarray((.5,-.25)),contact_diagonal=np.asarray((1.,2.,3.)),contact_off_diagonal=np.asarray((.1,.2)),fermion_background=np.asarray(background,dtype=complex))
def test_zero_background_mixed_hessian_vanishes_but_vertex_does_not():
 result=variation((0,0,0));assert result["zero_background_mixed_Hessian_vanishes_exactly"];assert result["mixed_HS_fermion_Hessian_norm"]==0;assert result["third_variation_vertex_frobenius_norm"]>0;assert result["fourth_variation_contact_frobenius_norm"]>0
def test_nonzero_background_activates_source_curvature_and_mixed_block():
 result=variation((1,0,0));assert result["nonzero_fermion_coefficient_background_supplied"];assert result["reduced_HS_source"]["real"]==2.;assert result["reduced_HS_curvature"]["real"]==1.;assert result["mixed_HS_fermion_Hessian_norm"]>0
def test_no_historical_kernel_is_silently_attached():
 screen=hs_kernel_candidate_screen();assert screen["attachable_count"]==0;assert screen["selected_current_AE3_kernel"] is None;assert screen["extension_requires_new_action_version_authority"]
def test_claim_boundary_preserves_family_state_without_relabeling_it_as_field():
 boundary=claim_boundary();assert boundary["historical_family_mode_state_preserved"];assert boundary["family_mode_state_is_not_a_classical_Sobolev_fermion_background"];assert not boundary["current_C2_dynamical_HS_kernel_derived"]
def test_materialized_current_C2_variation_is_fail_closed():
 payload=build_payload();assert payload["validation_passed"];assert all(row["zero_background_mixed_Hessian_vanishes_exactly"] for row in payload["reduced_variations"].values());assert not payload["claim_boundary"]["current_C2_broken_LR_saddle_derived"]
def test_result_is_integrated_without_closing_the_HS_kernel():
 section=systems_integration_puzzle()["sections"]["full_field_action"];assert "current_C2_zero_background_HS_fermion_mixed_variation" in section["fitted_pieces"];assert "dynamical_HS_kernel" in section["open_join"]
def test_materialized_artifact_is_deterministic():
 main();first=hashlib.sha256(TARGET.read_bytes()).hexdigest();main();second=hashlib.sha256(TARGET.read_bytes()).hexdigest();assert first==second
