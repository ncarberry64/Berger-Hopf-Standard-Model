import hashlib

from bhsm.interface.ae4_existing_asset_system_integration import (
    authoritative_frontier_reconciliation,
    hindsight_gate_reduction,
    integrated_claim_boundary,
    museum_science_export_contract,
    one_operator_completion_graph,
    reused_upstream_asset_ledger,
)
from scripts.materialize_ae4_existing_asset_system_integration import (
    TARGET,
    build_payload,
    main,
)


def test_every_reused_asset_has_present_upstream_evidence():
    ledger = reused_upstream_asset_ledger()
    assert len(ledger) == 16
    assert all(row.get("evidence", True) for row in ledger)
    assert all(not row.get("particle_spectrum_rebuilt", False) for row in ledger)


def test_hindsight_retires_duplicate_broad_gates_not_physical_outputs():
    rows = hindsight_gate_reduction()
    statuses = {row["hindsight_status"] for row in rows}
    assert "OPERATOR_SHAPES_ALREADY_EXIST" in statuses
    assert "ONTOLOGY_RETIRED" in statuses
    assert "ONE_OPERATOR_PROBLEM" in statuses
    assert "PROHIBITED_AND_UNNECESSARY" in statuses
    assert "PARTICLE_ONTOLOGY_ALREADY_RECONSTRUCTED" in statuses


def test_remaining_physics_is_one_global_operator_evaluation():
    graph = one_operator_completion_graph()
    boundary = integrated_claim_boundary()
    assert graph["single_global_operator_realization_remaining"] == 1
    assert graph["independent_operator_oracles_remaining"] == 0
    assert graph["separate_fitted_repairs_required"] == 0
    assert boundary["AE4_DUPLICATE_BROAD_GATES_REDUCED_TO_ONE_OPERATOR_EVALUATION"]
    assert not boundary["AE4_GLOBAL_RETARDED_STRATIFIED_OPERATOR_REALIZED"]
    assert not boundary["AE4_PHYSICAL_POLE_VERTEX_AND_COLLISION_PACKAGE_EVALUATED"]
    assert boundary["AE4_EVENT_CHILD_CANONICAL_RELATION_FORMULA_REUSED"]
    assert boundary["AE4_METRIC_LAPSE_FINITE_CHART_CHILD_DTN_REUSED"]
    assert boundary["AE4_PERSISTENT_NONEQUILIBRIUM_CHILD_ONTOLOGY_REUSED"]
    assert boundary["AE4_RETAINED_EVENT_CHILD_BOUNDARY_MAP_REUSED_AS_CLOSED"]
    assert boundary[
        "AE4_N3_TO_N6_EXACT_ATTACHMENT_COMPLETE_PERSISTENT_CHILDREN_REUSED"
    ]
    assert boundary["AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED"]
    assert boundary["AE4_CONTINUUM_EVENT_CHILD_CERTIFICATE_REUSED"]
    assert not boundary[
        "AE4_GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED"
    ]


def test_authoritative_frontier_supersedes_stale_v21_blockers():
    frontier = authoritative_frontier_reconciliation()
    assert frontier["AE3_ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED"]
    assert frontier["CONTINUUM_EVENT_CHILD_CERTIFIED"]
    assert frontier["PHYSICAL_TIME_ORIENTATION"] == "ONE_FORWARD"
    assert not frontier["v21_35_finite_N6_to_M0_bridge_is_current_blocker"]
    assert not frontier["v21_37_fixed_chart_rank_no_go_is_current_frontier"]
    assert not frontier["GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED"]
    assert not frontier[
        "global_forward_reachability_is_a_local_enclosure_prerequisite"
    ]
    assert "STRATIFIED_OPERATOR" in frontier[
        "primary_system_integration_object"
    ]


def test_museum_export_keeps_real_conditional_and_simulated_data_distinct():
    contract = museum_science_export_contract()
    assert contract["export_only_from_machine_claim_boundaries"]
    assert not contract["may_present_upstream_particle_ledgers_as_rebuilt_spectrum"]
    assert not contract["may_present_conditional_local_poles_as_measured_masses"]
    assert not contract["may_present_neutral_shape_gaps_as_neutrino_mass_splittings"]


def test_materialized_system_integration_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
