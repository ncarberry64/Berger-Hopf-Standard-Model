from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from bhsm.interface.completion.eta_fr_current_quantization_v14_29 import fr_quantization_payload
from bhsm.interface.completion.eta_g2_composite_intrinsic_torsion_v14_29 import composite_theta, composite_theta_bundle_payload, reductive_dimensions, theta_hessian_payload
from bhsm.interface.completion.eta_minimally_gauged_p2_p8_action_v14_29 import action_current, collar_density, covariant_derivative, kinetic_invariant, minimally_gauged_action_payload, su3_generators
from bhsm.interface.completion.eta_su3_noether_current_v14_29 import noether_current_payload, pure_wall_current_payload, selector_background_witness, tangent_mode_payload, tangent_mode_witness
from bhsm.interface.completion.recovered_gauge_chiral_no_go_v14_29 import chiral_overlap_no_go_payload, gauge_normalization_no_go_payload, six_pi_squared_identity
from bhsm.interface.completion.v14_9_28_lineage_recovery_v14_29 import lineage_recovery_payload
from bhsm.interface.completion.view2_completion_gate_v14_29 import OWNERSHIP_NEXT_OBJECT, all_payloads, completion_payload, materialization_hashes
from bhsm.interface.completion.wilson_singlet_source_functional_v14_29 import meson_amplitudes, singlet_color_invariants, wilson_singlet_payload
from bhsm.interface.confinement.view2_coupled_bvp_v14_29 import coupled_bvp_payload, reduced_tension, stationary_equation, transverse_flux_payload, wall_only_solution, wallless_solution
from bhsm.interface.master_action.view2_master_action_promotion_v14_29 import master_action_payload


def test_01_reductive_decomposition_is_8_plus_6():
    dims = reductive_dimensions()
    assert dims["su3"] + dims["m_real"] == dims["g2"] == 14


def test_02_twisted_bundle_retains_general_c2_sectors():
    payload = composite_theta_bundle_payload()
    assert "arbitrary retained c2" in payload["physical_color_bundle"]
    assert payload["validation"]["associated_coset_bundle_retains_parent_c2"]


def test_03_theta_is_composite():
    assert np.allclose(composite_theta(range(6), np.ones(6)), np.arange(6) + 1)
    assert composite_theta_bundle_payload()["validation"]["theta_is_composite"]


def test_04_no_independent_theta_variation():
    payload = composite_theta_bundle_payload()
    assert payload["configuration_space"].startswith("Conn(P_color)")
    assert payload["validation"]["independent_theta_variation_absent"]


def test_05_no_six_vector_principal_symbol():
    payload = theta_hessian_payload()
    assert payload["vector_pole_count_added"] == 0
    assert payload["principal_symbol"]["theta"] is None


def test_06_gauged_action_reduces_to_old_action_at_A_zero():
    eta = np.array([1, 2j, -0.5], complex)
    partial = np.array([[0.3j, -0.1, 0.2]], complex)
    assert np.allclose(covariant_derivative(eta, partial, np.zeros((1, 8))), partial)
    assert minimally_gauged_action_payload()["validation"]["ungauged_action_recovered_at_A_zero"]


def test_07_constant_gauge_covariance_and_action_invariance():
    generators = su3_generators()
    eta = np.array([0.2 + 0.1j, -0.3j, 0.7], complex)
    partial = np.array([[0.1, 0.2j, -0.2]], complex)
    a = np.array([[0.3, -0.1, 0.2, 0.0, 0.1, -0.2, 0.05, 0.4]])
    d = covariant_derivative(eta, partial, a)
    u = expm(0.37 * generators[7])
    connection = sum(a[0, k] * generators[k] for k in range(8))
    transformed = u @ connection @ u.conj().T
    a_prime = np.array([[2 * np.trace(g.conj().T @ transformed).real for g in generators]])
    d_prime = covariant_derivative(u @ eta, np.array([u @ partial[0]]), a_prime)
    assert np.allclose(d_prime, np.array([u @ d[0]]))
    assert np.isclose(kinetic_invariant(d), kinetic_invariant(d_prime))


def test_08_current_equals_exact_connection_variation():
    eta = np.array([0.2 + 0.1j, -0.4j, 0.7], complex)
    partial = np.array([[0.1, 0.2j, -0.2]], complex)
    a = np.zeros((1, 8))
    d = covariant_derivative(eta, partial, a)
    current = action_current(eta, d)
    eps = 1e-6
    for index in (0, 3, 7):
        plus, minus = a.copy(), a.copy()
        plus[0, index] += eps
        minus[0, index] -= eps
        numeric = (collar_density(kinetic_invariant(covariant_derivative(eta, partial, plus))) - collar_density(kinetic_invariant(covariant_derivative(eta, partial, minus)))) / (2 * eps)
        assert np.isclose(numeric, -current[0, index], rtol=2e-5, atol=2e-7)


def test_09_noether_identity_is_recorded_off_shell():
    payload = noether_current_payload()
    assert "E_eta" in payload["Noether_identity"]
    assert payload["validation"]["identity_is_off_shell"]


def test_10_on_shell_covariant_conservation_follows():
    assert noether_current_payload()["on_shell_consequence"] == "D_mu J^mu=0 when E_eta=0"


def test_11_background_selector_current_vanishes():
    _, current = selector_background_witness()
    assert np.allclose(current, 0)


def test_12_pure_normal_wall_current_vanishes():
    payload = pure_wall_current_payload()
    assert payload["validation"]["D_eta_zero_on_pure_selector_wall"]


def test_13_tangent_mode_current_nonzero():
    _, _, current = tangent_mode_witness()
    assert np.linalg.norm(current) > 0


def test_14_z_eta_positive_on_retained_branch():
    payload = tangent_mode_payload()
    assert payload["normalization"]["Z_eta_dimensionless_reference"] > 0


def test_15_canonical_normalization_adds_no_coupling():
    assert minimally_gauged_action_payload()["coefficient_ledger"]["new"] == []


def test_16_berry_and_physical_connections_remain_distinct():
    assert master_action_payload()["validation"]["A_P_distinct_from_A_physical"]


def test_17_fr_current_is_not_double_counted():
    payload = fr_quantization_payload()
    assert payload["validation"]["classical_and_Dirac_currents_not_summed"]


def test_18_global_singlet_has_zero_total_color_charge():
    assert singlet_color_invariants()["one_point_total_charge"] == 0
    assert np.isclose(np.vdot(meson_amplitudes(np.eye(3)), meson_amplitudes(np.eye(3))).real, 1)


def test_19_mesonic_correlation_is_minus_four_thirds():
    assert np.isclose(singlet_color_invariants()["summed_endpoint_correlation"], -4 / 3)


def test_20_frozen_predictions_unchanged():
    assert not completion_payload()["frozen_predictions_changed"]


def test_21_forbidden_physical_outputs_absent():
    payload = completion_payload()
    assert not payload["physical_outputs_emitted"]
    assert all(value is None for value in payload["forbidden_outputs"].values())


def test_22_materialization_is_deterministic(tmp_path: Path):
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert len(first) >= 11


def test_23_canonical_completion_gate_consistent():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["exact_next_object"] == OWNERSHIP_NEXT_OBJECT
    assert payload["downstream_BVP_object"] == coupled_bvp_payload()["exact_next_object"]


def test_24_historical_download_lineage_explicitly_classified():
    payload = lineage_recovery_payload()
    assert payload["validation_passed"]
    assert len(payload["rows"]) == 20
    assert {row["classification"] for row in payload["rows"]} >= {"VALIDATED", "VALIDATED_CONDITIONALLY", "RECLASSIFIED", "INVALIDATED"}
    assert all(row["sha256"] for row in payload["rows"])


def test_25_required_artifact_names_present():
    names = all_payloads()
    assert "BHSM_completion_gate_v14_29.json" in names
    assert "BHSM_Wilson_singlet_operator_source_v14_29.json" in names


def test_26_master_action_owns_view2_without_duplicate_eta_term():
    payload = master_action_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["eta_term_not_duplicated"]
    assert payload["authoritative_action"] is None
    assert payload["validation"]["preexisting_parent_action_derivation_absent"]


def test_27_wallless_and_wall_only_extrema_are_exact():
    for b, tau, solver in ((3.0, 0.0, wallless_solution), (0.0, 3.0, wall_only_solution)):
        radius, tension = solver(2.0, b or tau)
        assert abs(stationary_equation(radius, 2.0, b, tau)) < 1e-11
        assert abs(reduced_tension(radius, 2.0, b, tau) - tension) < 1e-11


def test_28_stable_tube_is_not_promoted_to_area_law():
    payload = transverse_flux_payload()
    assert payload["validation"]["stable_tube_not_called_area_law"]
    assert coupled_bvp_payload()["status"].startswith("OPEN")


def test_29_materialized_payloads_are_json_stable(tmp_path: Path):
    hashes = materialization_hashes(tmp_path)
    combined = hashlib.sha256("".join(sorted(hashes.values())).encode()).hexdigest()
    assert len(combined) == 64


def test_30_wilson_source_is_not_a_dynamical_action_term():
    assert wilson_singlet_payload()["validation"]["source_not_confused_with_dynamical_action"]


def test_31_six_pi2_is_normalization_not_physical_coupling():
    identity = six_pi_squared_identity()
    assert np.isclose(identity["product"], 6 * np.pi**2)
    assert gauge_normalization_no_go_payload()["validation_passed"]


def test_32_single_wall_chiral_pair_and_overlap_no_go_recovered():
    payload = chiral_overlap_no_go_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["single_wall_supplies_one_chiral_branch_not_Dirac_pair"]
    assert payload["validation"]["common_profile_overlap_is_family_central"]


def test_33_final_verdict_is_outcome_b_not_action_owned_outcome_a():
    payload = completion_payload()
    assert payload["primary_verdict"].startswith("BHSM_VIEW2_MINIMALLY_GAUGED_ETA_ACTION")
    assert master_action_payload()["authoritative_action"] is None


def test_34_tangent_witness_uses_stabilizer_zero_chart_and_phase_mode():
    background, _ = selector_background_witness()
    tangent, derivative, current = tangent_mode_witness()
    assert np.allclose(background, 0)
    assert np.vdot(tangent, derivative).imag != 0
    assert np.linalg.norm(current) > 0


def test_35_formal_scientific_audit_records_proof_and_blockers():
    report = (Path(__file__).parents[1] / "docs" / "BHSM_VIEW2_SCIENTIFIC_PROOF_AUDIT_V14_29.md").read_text(encoding="utf-8")
    for required in ("Outcome B", "delta_A S_etaA^cand", "Quadratic Hessian", "Double-counting audit", "COMMON_DOMAIN_ETA_TO_PHYSICAL_SU3"):
        assert required in report
