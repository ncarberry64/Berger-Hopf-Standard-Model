import hashlib

from bhsm.interface.ae3_family_mass_ontology_recovery import (
    claim_boundary,
    lineage_ledger,
    missing_bridge_decomposition,
    recovered_hopf_semigroup_candidate,
)
from scripts.materialize_ae3_family_mass_ontology_recovery import TARGET, build_payload, main


def test_relative_energy_ontology_survives_local_I3_no_go():
    result = lineage_ledger()
    assert result["mass_ontology_preserved"]
    assert not result["local_I3_overlap_proves_equal_total_parent_relative_energies"]
    assert result["historical_semigroup_candidate_present_in_corpus"]
    assert not result["historical_semigroup_candidate_present_in_active_AE3_dependency_graph"]


def test_historical_semigroup_candidate_is_recovered_not_promoted():
    result = recovered_hopf_semigroup_candidate()
    assert result["three_distinct_weights"]
    assert result["heat_semigroup_weights"][0] > result["heat_semigroup_weights"][1] > result["heat_semigroup_weights"][2]
    assert result["classification"] == "RECOVERED_HISTORICAL_CONDITIONAL_CANDIDATE"
    assert not result["equals_evaluated_parent_relative_energy"]
    assert not result["measured_lepton_mass_used"]


def test_missing_bridge_is_more_than_a_numeric_radius():
    result = missing_bridge_decomposition()
    assert not result["single_missing_numeric_radius_only"]
    assert len(result["relative_energy_route"]) == 5
    assert len(result["semigroup_insertion_route"]) == 5


def test_claim_boundary_preserves_the_candidate_without_claiming_masses():
    boundary = claim_boundary()
    assert boundary["v14_54_mass_ontology_recovered"]
    assert boundary["historical_Hopf_semigroup_candidate_recovered"]
    assert not boundary["historical_conditional_numbers_promoted"]
    assert not boundary["current_AE3_family_mass_hierarchy_derived"]


def test_materialized_recovery_audit_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
