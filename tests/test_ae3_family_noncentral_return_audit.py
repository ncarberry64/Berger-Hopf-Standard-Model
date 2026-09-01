from bhsm.interface.ae3_family_noncentral_return_audit import audit_certificate,candidates,irreducible_family_decision_surface
from scripts.materialize_ae3_family_noncentral_return_audit import build_payload
def test_all_retained_candidate_classes_are_fail_closed():
 rows=candidates();assert len(rows)==9;assert not any(row.admissible for row in rows)
def test_audit_reuses_families_without_rebuilding_spectrum():
 audit=audit_certificate();assert audit["certificate_passed"];assert audit["historical_particle_and_family_projectors_reused"];assert not audit["particle_spectrum_rebuilt"]
def test_decision_surface_selects_no_new_action():
 decision=irreducible_family_decision_surface();assert len(decision["decision_classes"])==3;assert not decision["choice_made_here"];assert not decision["family_mass_hierarchy_derived"]
def test_materialized_audit_is_fail_closed():
 payload=build_payload();assert payload["validation_passed"];assert payload["claim_boundary"]["family_modes_preserved"];assert not payload["claim_boundary"]["CKM_PMNS_derived"]
