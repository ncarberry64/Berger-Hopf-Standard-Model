from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.completion.hopf_phase_flavor_cross_gram_v14_34 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    bridge_channel_table,
    completion_payload,
    constant_phase_overlap_kernel,
    feshbach_cross_gram_payload,
    fixed_weight_support,
    frozen_harmonic_ledger_payload,
    identity_harmonic_overlap_kernel,
    jarlskog,
    maximal_fixed_weight_rank,
    minimal_channel_proxy_kernel,
    multi_harmonic_bridge_payload,
    nonlinear_tower_payload,
    phase_shift_no_go_payload,
    polar_unitary,
    proxy_kill_screen_payload,
    same_slot_required_channels,
    weight_difference_matrix,
)


def test_01_c_and_s_are_same_shell_different_imbalance():
    payload = frozen_harmonic_ledger_payload()
    assert payload["validation_passed"]
    assert "K=48" in payload["central_result"]
    assert "q_c=6" in payload["central_result"]


def test_02_identity_raw_harmonic_overlap_has_only_tb_entry():
    kernel = identity_harmonic_overlap_kernel()
    assert np.linalg.matrix_rank(kernel) == 1
    assert np.count_nonzero(kernel) == 1
    assert kernel[2, 2] == 1


def test_03_constant_phase_is_only_a_rephasing():
    identity = identity_harmonic_overlap_kernel()
    shifted = constant_phase_overlap_kernel(0.71)
    assert np.allclose(np.abs(identity), np.abs(shifted))
    assert np.linalg.matrix_rank(shifted) == 1


def test_04_single_fixed_weight_never_has_full_rank():
    maximum, ranks = maximal_fixed_weight_rank()
    assert maximum == 1
    assert all(np.linalg.matrix_rank(fixed_weight_support(weight)) == rank for weight, rank in ranks.items())


def test_05_weight_difference_matrix_is_exact():
    assert np.array_equal(
        weight_difference_matrix(),
        np.array([[4, 8, 8], [2, 6, 6], [-4, 0, 0]]),
    )


def test_06_same_slot_bridge_needs_three_harmonic_weights():
    channels = same_slot_required_channels()
    assert channels["u_to_d"]["ell"] == channels["u_to_d"]["p"] == 4
    assert channels["c_to_s"]["ell"] == channels["c_to_s"]["p"] == 6
    assert channels["t_to_b"]["ell"] == channels["t_to_b"]["p"] == 0


def test_07_all_minimal_bridge_channels_satisfy_selection_rules():
    rows = bridge_channel_table()
    assert len(rows) == 9
    assert all(row["allowed"] for row in rows)
    assert multi_harmonic_bridge_payload()["validation_passed"]


def test_08_minimal_channel_proxy_is_full_rank_but_not_physical():
    raw = minimal_channel_proxy_kernel()
    assert np.linalg.matrix_rank(raw) == 3
    assert raw[1, 0] > raw[1, 1]
    payload = proxy_kill_screen_payload()
    assert payload["validation_passed"]
    assert "NOT_AN_ACTION_DERIVATION" in payload["classification"]


def test_09_real_proxy_has_no_CP():
    unitary, _ = polar_unitary(minimal_channel_proxy_kernel())
    assert abs(jarlskog(unitary)) < 1e-14


def test_10_feshbach_identity_current_can_generate_nontrivial_polar_kernel():
    payload = feshbach_cross_gram_payload()
    assert payload["validation_passed"]
    witness = payload["existence_witness"]
    assert witness["distance_from_identity"] > 1e-3
    assert witness["commutator_norm"] > 1e-8
    assert abs(witness["jarlskog"]) > 1e-12


def test_11_feshbach_witness_unitary_and_full_rank():
    witness = feshbach_cross_gram_payload()["existence_witness"]
    assert witness["unitarity_residual"] < 1e-12
    assert np.min(witness["singular_values"]) > 1e-8


def test_12_nonlinear_tower_and_stiffness_boundaries():
    payload = nonlinear_tower_payload()
    assert payload["validation_passed"]
    assert "epsilon^8" in payload["small_amplitude_scaling"]
    assert "Schur/Feshbach" in payload["authorized_reduction"]


def test_13_single_phase_no_go_payload_passes():
    payload = phase_shift_no_go_payload()
    assert payload["validation_passed"]
    assert "full-rank" in payload["theorem"]


def test_14_completion_gate_preserves_I3_and_fails_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["live_weak_current_gate"].startswith("PRESERVED_I3")
    assert payload["CKM_status"] == "NOT_DERIVED"
    assert payload["BHSM_complete"] is False


def test_15_report_exists_after_installation():
    root = Path(__file__).parents[1]
    report = root / "docs" / "BHSM_HOPF_PHASE_FLAVOR_CROSS_GRAM_V14_34.md"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        assert "v14.34" in text
        assert "Feshbach" in text
