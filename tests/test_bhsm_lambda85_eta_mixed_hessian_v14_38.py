from __future__ import annotations

import numpy as np

from bhsm.interface.completion.lambda85_eta_mixed_hessian_completion_gate_v14_38 import (
    all_payloads,
    materialization_hashes,
)
from bhsm.interface.completion.lambda85_eta_mixed_hessian_v14_38 import (
    REQUESTED_CHANNELS,
    V14_37_ETA_CURVATURES,
    attachment_roots,
    c3_projection_payload,
    completion_payload,
    family_projector_basis_response,
    homogeneous_character_overlap,
    hypothetical_threshold_rows,
    kkt_tangent_matrices,
    lambda85_selection_rule_payload,
    lambda_multiplier_hessian,
    lower_attachment_root,
    normalized_mixed_singular_value,
    reduced_lambda85_mixed_block,
    zero_crossing_payload,
)


def test_v11_3_kkt_branch_remains_positive_and_matches_stored_root() -> None:
    gram, hessian = kkt_tangent_matrices()
    assert np.min(np.linalg.eigvalsh(gram)) > 0.0
    assert np.min(np.linalg.eigvalsh(hessian)) > 0.0
    roots = attachment_roots()
    assert 0.0 < roots[0] < roots[1]
    assert abs(lower_attachment_root() - 0.1633821478999081549) < 1.0e-13


def test_lambda85_is_a_constraint_multiplier_not_a_propagating_attachment_mode() -> None:
    assert lambda_multiplier_hessian() == 0.0


def test_homogeneous_attachment_is_orthogonal_to_every_requested_flavor_channel() -> None:
    assert homogeneous_character_overlap(0, 0) == 1.0
    for channel in REQUESTED_CHANNELS:
        assert homogeneous_character_overlap(*channel) == 0.0
    assert np.array_equal(reduced_lambda85_mixed_block(), np.zeros((5, 1)))


def test_normalized_zero_crossing_singular_value_is_exactly_zero() -> None:
    block = reduced_lambda85_mixed_block()
    eta = [V14_37_ETA_CURVATURES[channel] for channel in REQUESTED_CHANNELS]
    sigma = normalized_mixed_singular_value(block, eta, [lower_attachment_root()])
    assert sigma == 0.0
    assert sigma < 1.0


def test_canonical_C3_projection_is_diagonal_in_family_projector_basis() -> None:
    matrix = family_projector_basis_response()
    assert np.allclose(matrix, np.diag(np.diag(matrix)), atol=1.0e-13)
    assert np.min(np.real(np.diag(matrix))) > 0.0
    payload = c3_projection_payload()
    assert payload["validation_passed"]
    for key, value in payload["offdiagonal_family_chain_entries"].items():
        assert abs(value) < 1.0e-13, key


def test_hypothetical_thresholds_are_positive_but_current_block_does_not_cross() -> None:
    rows = hypothetical_threshold_rows()
    assert len(rows) == 5
    for row in rows:
        assert row["critical_mixed_magnitude"] > 0.0
        assert row["actual_reduced_Lambda85_mixed_magnitude"] == 0.0
        assert row["crossing_on_current_reduction"] is False


def test_scientific_payloads_validate_and_fail_closed() -> None:
    for payload in (
        lambda85_selection_rule_payload(),
        c3_projection_payload(),
        zero_crossing_payload(),
        completion_payload(),
    ):
        assert payload["validation_passed"]
    gate = completion_payload()
    assert gate["Lambda85_reduced_mixed_Hessian_gate"] == "FAILED_EXACT_ZERO_IN_NONTRIVIAL_ELL_P_CHANNELS"
    assert gate["canonical_C3_family_chain_gate"] == "FAILED_OFFDIAGONAL_ENTRIES_ZERO"
    assert gate["Spin4_mixed_Hessian_gate"] == "OPEN_MATCHED_TETRAD_SPIN_CONNECTION_PULLBACK"
    assert gate["bifurcation_status"] == "OFF_ON_CURRENT_ACTION_OWNED_REDUCTION"
    assert gate["BHSM_complete"] is False


def test_deterministic_materialization(tmp_path) -> None:
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert len(first) == len(all_payloads()) == 4
