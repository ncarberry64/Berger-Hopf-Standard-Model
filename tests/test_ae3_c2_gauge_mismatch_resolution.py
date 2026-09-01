from bhsm.interface.ae3_c2_gauge_mismatch_resolution import SELECTED_ROUTE,candidates,exterior_calderon_contract,selection_certificate
from scripts.materialize_ae3_c2_gauge_mismatch_resolution import build_payload
def test_unique_coefficient_free_route():
 c=selection_certificate();assert c["certificate_passed"];assert c["admissible_count"]==1;assert c["selected_route"]==SELECTED_ROUTE
def test_rejected_routes_fail_at_least_one_hard_condition():
 assert all(not c.admissible for c in candidates() if c.candidate_id!=SELECTED_ROUTE)
def test_exterior_contract_is_two_sided_and_contact_free():
 c=exterior_calderon_contract();assert "N_TOTAL=N_INSIDE" in c["combined_interface_Hessian"];assert c["surface_contact_term"] is None;assert not c["far_Friedrichs_core_is_physical_exterior"];assert not c["physical_photon_derived"]
def test_artifact_fails_closed_at_missing_exterior():
 p=build_payload();assert p["validation_passed"];assert p["claim_boundary"]["finite_route_screen_complete"];assert not p["claim_boundary"]["exterior_Calderon_operator_derived"];assert not p["claim_boundary"]["Lorentzian_Maxwell_residue_derived"]
