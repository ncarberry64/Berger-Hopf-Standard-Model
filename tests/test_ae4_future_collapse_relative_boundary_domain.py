import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_future_collapse_relative_boundary_domain import (
    claim_boundary,
    future_collapse_domain_contract,
    recovered_child_correspondence_assets,
    reflection_no_go_resolution,
    retarded_child_schur_complement,
)
from scripts.materialize_ae4_future_collapse_relative_boundary_domain import (
    TARGET,
    build_payload,
    main,
    theorem_witness,
)


def test_retarded_schur_complement_preserves_passivity():
    witness = theorem_witness()
    assert witness["causal_dissipation_identity_residual"] < 2e-15
    assert witness["child_retarded_imaginary_part_positive_semidefinite"]
    assert witness["effective_retarded_imaginary_part_positive_semidefinite"]


def test_schur_complement_rejects_incompatible_blocks():
    with pytest.raises(ValueError):
        retarded_child_schur_complement(np.eye(2), np.ones((3, 2)), np.eye(2))
    with pytest.raises(ValueError):
        retarded_child_schur_complement(np.asarray(((1, 1), (0, 1))), np.eye(2), np.eye(2))


def test_future_domain_is_not_reflection_or_static_reset_selection():
    domain = future_collapse_domain_contract()
    resolution = reflection_no_go_resolution()
    assert domain["complete_closed_system_variation_retained"]
    assert domain["reduced_parent_response_may_be_dissipative"]
    assert not domain["advanced_child_to_parent_physical_propagation_allowed"]
    assert not domain["reciprocal_reflected_cap_selected"]
    assert not domain["static_reset_graph_used_as_outer_state_selector"]
    assert not resolution["AE31_no_go_contradicted"]
    assert resolution["AE31_no_go_scope_bypassed_by_new_action_domain"]


def test_domain_class_selected_but_current_child_not_evaluated():
    boundary = claim_boundary()
    assert boundary["AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN_CLASS_SELECTED"]
    assert boundary["AE4_RETARDED_CHILD_SCHUR_COMPLEMENT_DERIVED"]
    assert not boundary["AE4_CURRENT_C2_FUTURE_CHILD_BLOCK_EVALUATED"]
    assert not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]


def test_existing_complete_child_work_is_reused_at_its_actual_strength():
    recovered = recovered_child_correspondence_assets()
    boundary = claim_boundary()
    assert recovered["v17_84_first_variation_and_F_child_formula_reused"]
    assert recovered["v17_86_metric_lapse_finite_chart_slice_evaluated"]
    assert not recovered["v17_86_static_spatial_child_BVP_closed"]
    assert recovered["AE2_zero_threshold_nonfermion_resonance_excluded"]
    assert recovered["v17_88_to_v17_98_retained_boundary_map_closed"]
    assert recovered[
        "v17_99_positive_duration_complete_child_persistence_validated"
    ]
    assert recovered[
        "v21_35_exact_attachment_complete_persistent_orders"
    ] == [3, 4, 5, 6]
    assert recovered["N12_continuum_event_child_certified"]
    assert recovered["N12_physical_time_orientation"] == "ONE_FORWARD"
    assert len(recovered["actual_remaining_domain_puzzle_objects"]) == 2
    assert not recovered[
        "global_forward_reachability_is_required_to_reopen_local_enclosure"
    ]
    assert not recovered["five_v17_84_era_missing_block_list_is_current"]
    assert not recovered["complete_child_calculation_restarted"]
    assert boundary["AE4_V17_87_PERSISTENT_NONEQUILIBRIUM_CHILD_REUSED"]
    assert boundary[
        "AE4_V21_35_N3_TO_N6_COMPLETE_PERSISTENT_CHILDREN_REUSED"
    ]
    assert boundary["AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED"]
    assert boundary["AE4_N12_CONTINUUM_EVENT_CHILD_CERTIFICATE_REUSED"]
    assert not boundary[
        "AE4_GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED"
    ]


def test_materialized_future_domain_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
