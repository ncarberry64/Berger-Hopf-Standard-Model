from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.aether_event_flux_sigma_trace_v15_27 import (
    affine_self_adjoint_trace_audit,
    canonical_integer_dual_pairing_audit,
    completion_payload,
    downstream_nonuniqueness_witness,
    event_coupling_selection_audit,
    event_sector_ledger,
    event_sigma_variation,
    materialize,
    signed_degree_jump,
    smooth_event_current,
    weak_distribution_witness,
)


def test_stokes_flux_is_exact_signed_degree_jump() -> None:
    assert signed_degree_jump(0, 1)["Q_Gamma"] == 1
    assert signed_degree_jump(1, 1)["Q_Gamma"] == 0
    assert signed_degree_jump(1, -1)["Q_Gamma"] == -2
    assert signed_degree_jump(0, 1)["orientation_reversal_Q_Gamma"] == -1


def test_smooth_event_current_integrates_to_topological_jump() -> None:
    coordinate = np.linspace(-2.0, 2.0, 80001)
    result = smooth_event_current(
        coordinate, width=0.05, incoming_degree=0, outgoing_degree=1
    )
    assert abs(result["integrated_flux"] - 1.0) < 1.0e-12
    assert abs(result["first_moment"]) < 1.0e-13
    assert not result["regularizer_is_physical_width"]


def test_distribution_converges_weakly_to_event_delta() -> None:
    witness = weak_distribution_witness()
    assert witness["absolute_errors_decrease"]
    assert abs(witness["narrowest_flux_error"]) < 1.0e-12


def test_event_variation_gives_oriented_canonical_jump() -> None:
    result = event_sigma_variation(topological_flux=1, coupling=1.5, zsigma=2.0)
    assert result["Pi_jump"] == 1.5
    assert result["orientation_reversed_Pi_jump"] == -1.5
    assert result["canonical_velocity_jump_magnitude"] == 0.75


def test_affine_event_background_has_self_adjoint_fluctuations() -> None:
    result = affine_self_adjoint_trace_audit()
    assert result["fluctuation_Green_form_norm"] < 1.0e-13
    assert result["self_adjoint_fluctuation_operator"]
    assert not result["self_adjointness_fixes_affine_source_magnitude"]


def test_event_sector_is_not_selected_by_degree_arithmetic() -> None:
    ledger = event_sector_ledger()
    assert ledger["candidate_reconstruction_0_to_1"]["Q_Gamma"] == 1
    assert not ledger["outgoing_degree_one_Hopf_child_constructed"]
    assert not ledger["actual_BHSM_event_sector_pair_selected"]


def test_topology_does_not_silently_fix_event_coupling() -> None:
    audit = event_coupling_selection_audit()
    assert audit["topological_flux_fixed_after_sector_selection"]
    assert audit["different_physical_impulses"]
    assert not audit["lambda_Gamma_action_selected"]
    assert not audit["physical_sigma_trace_closed"]


def test_integer_dual_circle_is_not_the_retained_material_sigma() -> None:
    audit = canonical_integer_dual_pairing_audit()
    assert audit["Pontryagin_dual"] == "U1"
    assert audit["eta_endpoint_characters_equal_for_all_tested_integer_charges"]
    assert not audit["retained_material_action_is_period_one"]
    assert not audit["material_sigma_identified_with_Z_dual_angle"]
    assert not audit["canonical_duality_fixes_lambda_Gamma_for_material_sigma"]


def test_conditional_impulse_dynamics_exposes_remaining_dependence() -> None:
    witness = downstream_nonuniqueness_witness()
    assert witness["all_solvers_succeeded"]
    assert witness["same_Q_different_lambda_changes_trajectory"]
    assert witness["same_Q_lambda_different_response_changes_trajectory"]
    assert not witness["controls_are_predictions"]


def test_completion_payload_is_valid_and_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert not payload["FULL_BHSM_COMPLETE"]
    assert not payload["event_coupling_selection"]["lambda_Gamma_action_selected"]
    assert not payload["event_sector_ledger"]["actual_BHSM_event_sector_pair_selected"]


def test_materialization_is_deterministic(tmp_path: Path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
