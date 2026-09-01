from bhsm.interface.ae3_c2_two_sided_calderon import irreducible_decision_surface,operator_domain_transport_certificate,reflection_certificate,two_sided_residue_certificate
from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import gauge_ghost_hessian_claim_boundary
from bhsm.interface.ae3_reciprocal_join_localization import systems_integration_puzzle
from scripts.materialize_ae3_c2_two_sided_calderon import build_payload
def test_reciprocal_join_reflection_is_exact():
 r=reflection_certificate();assert r["reflection_isometry_exact"];assert r["numerical_audit_passed"];assert r["numerical_audit"]["sigma_antisymmetry_residual"]<2e-15;assert r["numerical_audit"]["weight_symmetry_residual"]<2e-15
def test_full_regular_maxwell_brst_domain_is_transported():
 o=operator_domain_transport_certificate();assert o["full_regular_domain_transport_derived"];assert o["constraint_block_preserved"];assert o["BRST_gauge_fixing_and_ghost_complex_preserved"];assert o["surface_contact_term"] is None
def test_two_sided_sum_doubles_but_does_not_match():
 t=two_sided_residue_certificate();assert t["N_total_zero"]==2*t["N_inside_zero"];assert t["minus_dq2_N_total_zero"]==2*t["minus_dq2_N_inside_zero"];assert t["Zt_over_Zs_two_sided"]==t["Zt_over_Zs_inside"];assert not t["one_positive_Lorentzian_residue"]
def test_decision_surface_does_not_choose_new_physics():
 d=irreducible_decision_surface();assert d["coefficient_free_retained_routes_remaining"]==0;assert len(d["decision_classes"])==3;assert not d["choice_made_here"];assert not d["physical_photon_derived"]
def test_materialized_result_is_fail_closed():
 p=build_payload();assert p["validation_passed"];assert p["claim_boundary"]["two_sided_parent_Calderon_evaluated"];assert not p["claim_boundary"]["Lorentzian_Maxwell_residue_derived"]
def test_result_is_integrated_as_a_decision_surface():
 h=gauge_ghost_hessian_claim_boundary();assert "FINITE_DECISION" in h["next_required_action_domain_object"];p=systems_integration_puzzle()["sections"]["full_field_action"];assert "two_sided_reciprocal_Calderon_reflection_no_go" in p["fitted_pieces"];assert "finite_action_domain_decision" in p["open_join"]
