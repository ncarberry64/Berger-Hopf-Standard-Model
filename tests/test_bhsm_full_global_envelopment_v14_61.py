from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.completion.full_global_envelopment_v14_61 import (
    EXACT_NEXT_OBJECT,
    action_sector_ledger,
    artifact_payloads,
    branch_search_payload,
    coefficient_readiness,
    completion_gate_payload,
    euler_lagrange_contract_payload,
    gauge_reduced_hessian,
    gauge_reduction_fixture_payload,
    global_action_gradient,
    global_action_hessian,
    global_action_value,
    materialize,
    neutrino_handoff_payload,
    newton_solve,
    physical_execution_gate,
    precomparison_freeze_manifest,
    require_physical_execution_ready,
    scale_stationarity_components,
    stationary_fixture_certificate,
    synthetic_global_action,
)


def target_state():
    model = synthetic_global_action()
    return model, np.concatenate([model.target_u, np.array([model.target_x])])


def test_action_sector_ledger_has_expected_scale_powers() -> None:
    powers = {s.name: s.scale_power for s in action_sector_ledger()}
    assert powers["M8_volume"] == 8
    assert powers["M8_two_derivative_geometry_eta"] == 6
    assert powers["collar_GHY_interface"] == 3
    assert powers["M4_local_action"] == 0
    assert powers["relative_nonlocal_spectral"] is None


def test_xi_branch_is_locked_but_does_not_make_physical_action_ready() -> None:
    ledger = {s.name: s for s in action_sector_ledger()}
    assert ledger["Berger_connection_curvature_endomorphism"].physical_ready is True
    assert ledger["Berger_connection_curvature_endomorphism"].coefficient_status == "XI_EQUALS_ZERO"
    assert coefficient_readiness()["all_physical_coefficients_and_operators_ready"] is False


def test_no_measured_data_fill_missing_coefficients() -> None:
    payload = coefficient_readiness()
    assert payload["measured_particle_data_used_to_fill_missing_entries"] is False
    assert len(payload["missing_sectors"]) >= 6


def test_synthetic_target_is_stationary() -> None:
    model, z = target_state()
    assert np.linalg.norm(global_action_gradient(z, model)) < 1e-12


def test_scale_equation_closes_at_fixture_target() -> None:
    model, z = target_state()
    comp = scale_stationarity_components(z, model)
    assert abs(comp["sum"]) < 1e-12
    assert comp["Z"] < 0.0


def test_analytic_hessian_matches_finite_difference_gradient() -> None:
    model, z = target_state()
    H = global_action_hessian(z, model)
    eps = 1e-6
    numeric = np.zeros_like(H)
    for j in range(z.size):
        d = np.zeros_like(z); d[j] = eps
        numeric[:, j] = (global_action_gradient(z+d, model)-global_action_gradient(z-d, model))/(2*eps)
    assert np.linalg.norm(H-numeric) < 2e-7


def test_action_gradient_matches_finite_difference_value() -> None:
    model, z = target_state()
    g = global_action_gradient(z, model)
    eps = 1e-6
    numeric = np.zeros_like(g)
    for j in range(z.size):
        d = np.zeros_like(z); d[j] = eps
        numeric[j]=(global_action_value(z+d,model)-global_action_value(z-d,model))/(2*eps)
    assert np.linalg.norm(g-numeric) < 2e-7


def test_fixture_hessian_is_positive_and_nondegenerate() -> None:
    payload = stationary_fixture_certificate()
    assert payload["isolated_local_stationary_branch"] is True
    assert payload["positive_local_hessian_in_fixture"] is True
    assert payload["global_uniqueness_proved"] is False
    assert payload["physical_BHSM_solution"] is False


def test_newton_solver_recovers_fixture_from_displaced_seed() -> None:
    model, z = target_state()
    seed = z.copy(); seed[:-1] += np.linspace(-0.08,0.07,z.size-1); seed[-1] += 0.25
    result = newton_solve(seed, model)
    assert result["converged"] is True
    assert result["gradient_norm"] < 1e-10
    assert np.linalg.norm(result["state"]-z) < 1e-8


def test_branch_search_is_explicitly_not_global_proof() -> None:
    payload = branch_search_payload()
    assert payload["seed_count"] == 15
    assert payload["converged_seed_count"] == 15
    assert payload["distinct_stationary_clusters_in_frozen_search"] == 1
    assert payload["all_converged_to_single_fixture_branch"] is True
    assert payload["global_branch_exhaustion_proved"] is False
    assert payload["physical_branch_search_executed"] is False


def test_gauge_reduction_removes_flat_gauge_coordinate() -> None:
    payload = gauge_reduction_fixture_payload()
    assert payload["raw_hessian_has_zero_mode"] is True
    assert payload["physical_dimension"] == 4
    assert payload["gauge_reduced_hessian_nondegenerate"] is True
    assert payload["gauge_reduced_hessian_positive"] is True
    assert payload["physical_BHSM_gauge_ghost_operator_inserted"] is False


def test_gauge_reduced_hessian_supports_constraints_and_gauge_rows() -> None:
    H=np.diag([0.,2.,3.,4.])
    G=np.array([[1.,0.,0.,0.]])
    C=np.array([[0.,1.,0.,0.]])
    reduced=gauge_reduced_hessian(H,G,C)
    assert reduced["physical_dimension"] == 2
    assert np.allclose(reduced["eigenvalues"],[3.,4.])


def test_global_EL_contract_has_correct_scale_derivative() -> None:
    payload=euler_lagrange_contract_payload()
    assert "8 exp(8x)A8" in payload["scale_equation"]
    assert "6 exp(6x)A6" in payload["scale_equation"]
    assert "3 exp(3x)A3" in payload["scale_equation"]
    assert payload["seam_rule"].startswith("seam value and traction are outputs")
    assert payload["physical_coefficients_inserted"] is False


def test_freeze_manifest_is_deterministic_and_contains_no_experimental_targets() -> None:
    a=precomparison_freeze_manifest(); b=precomparison_freeze_manifest()
    assert a==b
    assert a["experimental_neutrino_targets_present"] is False
    assert a["measured_particle_masses_present"] is False
    assert a["measured_CKM_PMNS_values_present"] is False
    assert a["retuning_after_comparison_allowed"] is False


def test_physical_gate_fails_closed() -> None:
    gate=physical_execution_gate()
    assert gate["verdict"] == "PHYSICAL_EXECUTION_BLOCKED"
    assert gate["full_BHSM_complete"] is False
    assert gate["mark_III"] == "NOT_REACHED"
    assert gate["physical_prediction_emitted"] is False
    assert gate["usb_touched"] is False


def test_physical_execute_raises_instead_of_fabricating_background() -> None:
    with pytest.raises(RuntimeError, match="physical execution blocked"):
        require_physical_execution_ready()


def test_neutrino_handoff_preserves_pair_wake_contract_without_prediction() -> None:
    p=neutrino_handoff_payload()
    assert p["fixed_inception_pair_identity"] is True
    assert p["three_wake_projection_basis_required"] is True
    assert p["physical_inputs_available"] is False
    assert p["physical_neutrino_execution_performed"] is False
    assert p["no_PMNS_or_mass_splitting_emitted"] is True


def test_completion_gate_records_architectural_bypass_not_completion() -> None:
    gate=completion_gate_payload()
    assert gate["v14_59_local_inverse_boundary_obstruction"] == "ARCHITECTURALLY_BYPASSED_BY_GLOBAL_ENVELOPMENT_VARIATION"
    assert gate["v14_60_reduced_global_selection_mechanism"] == "VALIDATED"
    assert gate["full_action_EL_interface"] == "FORMULATED"
    assert gate["full_BHSM_complete"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    a=tmp_path/'a'; b=tmp_path/'b'
    pa=materialize(a); pb=materialize(b)
    assert len(pa)==len(pb)==len(artifact_payloads())==8
    for x,y in zip(pa,pb):
        assert x.name==y.name
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())


def test_fixture_is_nonphysical_and_nesting_ratio_not_prediction() -> None:
    p=stationary_fixture_certificate()
    assert p["fixture_status"] == "SYNTHETIC_NONPHYSICAL_THEOREM_WITNESS"
    assert 0.0 < p["diagnostic_nesting_ratio"] < 1.0
    assert p["physical_BHSM_solution"] is False


def test_hessian_is_symmetric() -> None:
    model,z=target_state(); H=global_action_hessian(z,model)
    assert np.linalg.norm(H-H.T) < 1e-13
