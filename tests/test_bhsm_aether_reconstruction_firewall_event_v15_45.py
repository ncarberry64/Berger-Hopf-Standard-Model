import numpy as np

from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import (
    boundary_identity_chain_complex,
    completion_payload,
    deterministic_json,
    oriented_cut_and_event_data,
    reconstruction_seed,
)


def test_boundary_identity_complex_does_not_exchange_parent_and_child():
    result = boundary_identity_chain_complex()
    boundary = np.asarray(result["boundary_matrix_d1"])
    assert result["boundary_identity_exchange"] is False
    assert result["selected_matrix_differs_from_exchange"]
    assert np.array_equal(boundary[:, 0], [-1, 0, 1, 0])
    assert np.array_equal(boundary[:, 1], [0, -1, 0, 1])


def test_only_metric_free_invariants_cross_the_firewall():
    result = oriented_cut_and_event_data()
    assert result["topological_degree_conserved"]
    assert result["FR_parity_conserved"]
    assert result["surviving_data"]["global_event_degree"] == 1
    assert result["surviving_data"]["FR_parity"] == -1
    assert "metric" in result["not_transported_as_pregeometric_primitives"]
    assert "canonical_metric_momentum" in result[
        "not_transported_as_pregeometric_primitives"
    ]


def test_reconstruction_seed_keeps_child_interior_and_full_preimage():
    result = reconstruction_seed()
    assert result["child_boundary"] == "Sigma_c=S3_times_S3"
    assert result["outer_layer_only_crosses_firewall"]
    assert result["interior_erased_at_contact"] is False


def test_payload_is_deterministic_and_post_cut_metric_remains_active():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["Lorentzian_separation_before_firewall_derived"]
    assert payload["claim_boundary"]["post_cut_reconstructed_metric_child_solved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
