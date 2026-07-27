from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import moving_endpoint_shift_domain as domain


ROOT = Path(__file__).resolve().parents[1]


def test_exact_endpoint_pullback_contains_lapse_shift_and_embedding():
    pullback = domain.pullback_ledger()
    assert "N_mu D_nu zeta" in pullback["induced_metric_exact"]
    assert "N^2" in pullback["induced_metric_exact"]
    assert pullback["shift_enters_induced_metric_at"] == "quadratic derivative order"
    assert pullback["scalar_pullback"].endswith("sigma0'")


def test_endpoint_normal_and_relative_shift():
    pullback = domain.pullback_ledger()
    assert pullback["level_set_normal"] == "s_A=(1,-D_mu zeta)"
    assert pullback["relative_shift_one_form"] == "V_mu=N_mu+N^2 D_mu zeta"
    assert "N^mu+N^2 D^mu zeta" in pullback["unit_normal_linear"]


def test_radial_and_longitudinal_gauge_transformations():
    gauge = domain.gauge_ledger()
    assert gauge["transformations"]["zeta"] == "zeta+xi^rho|Sigma"
    assert gauge["transformations"]["E"] == "E-xi"
    assert "N0^2 xi^rho" in gauge["transformations"]["B"]


def test_endpoint_shift_combination_is_exactly_gauge_invariant():
    assert sp.simplify(
        domain.transformed_endpoint_shift_invariant()
        - domain.endpoint_shift_invariant()
    ) == 0
    assert domain.gauge_ledger()["endpoint_shift_invariant"] == (
        "S_Sigma=[B+N0^2 zeta-a0^2 partial_rho E]_Sigma"
    )


def test_endpoint_conformal_pullback_is_radially_invariant():
    transformed = domain.transformed_endpoint_variables()
    value = domain.endpoint_conformal_pullback(
        transformed["psi"], transformed["zeta"]
    )
    assert sp.simplify(value - domain.endpoint_conformal_pullback()) == 0


def test_endpoint_scalar_pullback_is_radially_invariant():
    transformed = domain.transformed_endpoint_variables()
    value = domain.endpoint_scalar_pullback(
        transformed["delta_sigma"], transformed["zeta"]
    )
    assert sp.simplify(value - domain.endpoint_scalar_pullback()) == 0


def test_delta_X_remains_intrinsic():
    transformed = domain.transformed_endpoint_variables()
    value = domain.endpoint_curvature_pullback(
        transformed["delta_X"], transformed["zeta"]
    )
    assert sp.simplify(value - domain.endpoint_curvature_pullback()) == 0
    assert "terms cancel" in domain.gauge_ledger()["delta_X_intrinsic_proof"]


def test_fixed_endpoint_and_longitudinal_gauges_do_not_change_S_Sigma():
    residual = domain.gauge_ledger()["residual_classification"]
    assert "unchanged" in residual
    assert "not residual gauge" in residual


def test_repository_fixes_embedding_not_metric_trace():
    ledger = domain.repository_domain_ledger()
    assert ledger["embedding_varied"] is False
    assert ledger["zeta_action_variable"] is False
    assert "exact multiplier constraint" in ledger["metric_ontology"]
    assert ledger["boundary_domains_frozen"] is True


def test_rho_J_is_a_static_solved_domain_not_an_embedding_field():
    ledger = domain.repository_domain_ledger()
    assert "solved by the homogeneous boundary-value" in ledger["rho_J_static_status"]
    assert "not promoted" in ledger["rho_J_static_status"]
    assert "one-dimensional" in ledger["static_transversality"]


def test_first_variation_derives_metric_junction():
    variation = domain.first_variation_ledger()
    assert variation["derived_metric_condition"] == (
        "kappa_1[Q_mu_nu]+2C_partial G_mu_nu"
        "=T_partial,mu_nu"
    )
    assert "momentum constraint" not in variation["derived_metric_condition"]


def test_shift_variation_has_no_radial_endpoint_term():
    variation = domain.first_variation_ledger()
    assert variation["bulk_shift_radial_endpoint_term"] == 0
    assert "no radial derivative" in variation["reason_no_shift_endpoint_term"]


def test_longitudinal_junction_projection_is_a_Ward_identity():
    variation = domain.first_variation_ledger()
    assert variation["longitudinal_junction_identity"].startswith("D^mu")
    assert "Codazzi/Bianchi Ward identity" in variation["longitudinal_classification"]
    assert "not an independent endpoint-domain" in (
        variation["longitudinal_classification"]
    )


def test_scalar_endpoint_is_dirichlet():
    assert "fixes delta sigma_Sigma=0" in (
        domain.first_variation_ledger()["scalar_endpoint_term"]
    )


def test_no_free_endpoint_shift_variation_exists():
    variation = domain.first_variation_ledger()
    assert variation["x_dependent_embedding_variation"] is False
    assert variation["coefficient_of_free_delta_S_Sigma"] is None
    assert variation["endpoint_condition"] is None
    assert variation["junction_is_shift_boundary_condition"] is False
    assert variation["result"] == domain.PRIMARY_RESULT


def test_boundary_condition_is_absent_not_guessed():
    classification = domain.first_variation_ledger()["condition_classification"]
    assert classification == "absent because embedding/threading data are not varied"
    assert domain.GUARDS["arbitrary_boundary_condition_added"] is False


def test_boundary_data_ledger_is_complete():
    ledger = domain.boundary_data_ledger()
    assert set(ledger) == {
        "fixed",
        "freely_varied",
        "constrained",
        "gauge",
        "physically_dynamical",
        "unspecified",
        "radion_status",
    }
    assert "gauge-invariant endpoint threading S_Sigma" in ledger["unspecified"]


@pytest.mark.parametrize("tau", [-1, 1])
def test_reproduces_exact_v6_12_mismatch(tau):
    expected = (
        -3
        * tau
        * domain.CHI_1
        * domain.T
        / (4 * sp.sin(sp.pi * domain.T / 4) ** 2)
    )
    assert sp.simplify(domain.zero_shift_mismatch(tau) - expected) == 0


def test_invalid_sheet_rejected():
    with pytest.raises(ValueError):
        domain.zero_shift_mismatch(0)


def test_constraint_operator_not_constructed_without_domain():
    ledger = domain.constraint_and_kinetic_ledger()
    assert ledger["endpoint_condition_derived"] is False
    assert ledger["L_C_constructed"] is False
    assert ledger["differential_order"] is None
    assert ledger["kernel"] is None
    assert ledger["adjoint_kernel"] is None


def test_no_pseudoinverse_or_Green_operator_is_manufactured():
    ledger = domain.constraint_and_kinetic_ledger()
    assert ledger["Green_operator_constructed"] is False
    assert ledger["Green_operator_exists"] is None
    assert ledger["pseudoinverse_used"] is False


def test_homogeneous_trace_classification_is_bounded():
    classification = domain.constraint_and_kinetic_ledger()["homogeneous_trace"]
    assert "not residual gauge" in classification
    assert "cannot be called a physical radion" in classification


def test_fold_kinetic_inputs_are_preserved_but_total_is_open():
    ledger = domain.constraint_and_kinetic_ledger()
    assert ledger["preserved"]["F0_equals_M4_squared"] == "pi/2"
    assert ledger["preserved"]["K_scalar"] == ">=2>0"
    assert "(4-pi)^2" in ledger["preserved"]["K_Weyl"]
    assert ledger["K_shift_endpoint_red"] is None
    assert ledger["k_q_E"] is None
    assert ledger["kinetic_sign"] is None


def test_no_physical_masses_are_calculated():
    assert (
        domain.constraint_and_kinetic_ledger()["physical_masses_calculated"]
        is False
    )


def test_exact_next_input_is_named():
    next_input = domain.constraint_and_kinetic_ledger()["exact_next_input"]
    assert "whether iota is fixed or freely varied" in next_input
    assert "action-derived boundary threading domain" in next_input


def test_integrity_guards():
    for payload in domain.artifact_payloads().values():
        assert payload["arbitrary_boundary_condition_added"] is False
        assert payload["embedding_variation_assumed"] is False
        assert payload["new_action_term_introduced"] is False
        assert payload["new_primitive_introduced"] is False
        assert payload["tau_J_introduced"] is False
        assert payload["boundary_tension_introduced"] is False
        assert payload["radion_potential_introduced"] is False
        assert payload["measured_input_used"] is False
        assert payload["neutral_work_performed"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_exactly_two_deterministic_artifacts():
    expected = domain.artifact_bytes()
    assert len(expected) == 2
    assert set(expected) == set(domain.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = domain.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
