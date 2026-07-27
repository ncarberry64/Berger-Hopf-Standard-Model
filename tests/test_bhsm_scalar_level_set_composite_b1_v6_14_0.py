from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import scalar_level_set_composite_b1 as composite


ROOT = Path(__file__).resolve().parents[1]


def test_inherited_v6_1_7_fold_constants():
    payload = composite.artifact_payloads()["geometry"]["fold_constants"]
    assert payload["chi_1"] == "5.268307871542"
    assert payload["nu_1"] == "109.666681740423"
    assert payload["u1_junction_derivative"] == "-9.124976903426"
    assert payload["weighted_norm"] == 1


def test_hindsight_provenance_uses_required_status_vocabulary():
    allowed = {
        "Adopted from established physics/mathematics",
        "Adopted BHSM axiom",
        "BHSM identification",
        "Derived consequence",
        "Numerically validated",
        "Needs empirical test",
        "Rejected by calculation",
        "Active construction target",
    }
    rows = composite.provenance_ledger()
    assert rows
    assert all(row["status"] in allowed for row in rows)
    assert any(row["status"] == "Adopted BHSM axiom" for row in rows)


def test_sigma_zero_background_is_identically_zero_and_singular():
    ledger = composite.direct_level_set_ledger()
    assert ledger["critical_sigma"] == "sigma_0(rho)=0 for every rho"
    assert ledger["critical_gradient"] == 0
    assert ledger["q_zero_regular_value"] is False
    assert ledger["result"] == composite.DIRECT_RESULT


def test_direct_level_set_is_regular_for_small_positive_q():
    ledger = composite.direct_level_set_ledger()
    assert ledger["q_positive_regular_value"] is True
    assert "sufficiently small q>0" in ledger["regularity_scope"]
    leading = sp.expand(composite.direct_normal_derivative_series()).coeff(
        composite.Q, 1
    )
    assert leading == composite.S * composite.U1_PRIME


def test_junction_zero_is_unique_and_no_interior_nodes_occur():
    ledger = composite.direct_level_set_ledger()
    assert ledger["junction_zero_locally_unique"] is True
    assert ledger["additional_cap_zeros"] is False
    assert "lowest" in ledger["additional_zero_reason"]
    assert "no interior nodes" in ledger["additional_zero_reason"]


def test_scalar_sign_does_not_change_support():
    ledger = composite.direct_level_set_ledger()
    assert "not the zero set" in ledger["scalar_sign_independence"]
    assert composite.amplitude_and_blowup_ledger()["scalar_sign_support"] == (
        "independent"
    )


def test_sheet_changes_response_not_regularity():
    ledger = composite.direct_level_set_ledger()
    assert "rho_J'(0)=-tau chi_1/4" in ledger["sheet_dependence"]
    assert composite.endpoint_slope(1) == -composite.CHI_1 / 4
    assert composite.endpoint_slope(-1) == composite.CHI_1 / 4


def test_Z2_caps_share_the_level_set():
    ledger = composite.direct_level_set_ledger()
    assert "common sigma=0 junction" in ledger["Z2_caps"]


def test_invariant_amplitude_uses_exact_stored_measure():
    ledger = composite.amplitude_and_blowup_ledger()
    assert ledger["proper_normal_measure"] == (
        "Q[sigma]^2=integral_0^rhoJ a^4 sigma^2 d rho"
    )
    assert ledger["fixed_domain_measure"] == (
        "Q[sigma]^2=integral_0^1 N a^4 sigma^2 dt"
    )


def test_Q_equals_q_through_leading_order():
    assert composite.amplitude_series() == (
        composite.Q + composite.ALPHA * composite.Q**2
    )
    assert sp.diff(composite.amplitude_series(), composite.Q).subs(
        composite.Q, 0
    ) == 1


def test_sigma_hat_limit_is_signed_ground_mode():
    assert composite.blowup_profile_series().subs(composite.Q, 0) == (
        composite.S * composite.U1
    )
    ledger = composite.amplitude_and_blowup_ledger()
    assert ledger["limit"].startswith("sigma_hat -> s u1")


def test_blowup_zero_set_is_regular_at_the_fold():
    ledger = composite.amplitude_and_blowup_ledger()
    assert ledger["critical_support"] == "Sigma_0={u1=0}={rho_J}"
    assert ledger["critical_regular"] is True
    assert "!=0" in ledger["critical_witness"]


def test_support_is_invariant_under_nonzero_profile_rescaling():
    ledger = composite.amplitude_and_blowup_ledger()
    assert "zero set" in ledger["normalization_dependence"]
    assert "fixed sqrt(2)" in ledger["cap_multiplicity"]


def test_blowup_chart_is_radially_and_tangentially_covariant():
    ledger = composite.amplitude_and_blowup_ledger()
    assert "invariant scalar integral" in ledger["radial_gauge_covariance"]
    assert "tangential reparameterizations" in (
        ledger["M4_diffeomorphism_covariance"]
    )


def test_sigma_hat_is_a_chart_not_a_field():
    ledger = composite.amplitude_and_blowup_ledger()
    assert ledger["field_status"] == (
        "nonlocal collective-coordinate chart, not a new field"
    )
    assert ledger["result"] == composite.CHART_RESULT


def test_off_center_manifold_limit_is_ambiguous():
    ledger = composite.amplitude_and_blowup_ledger()
    assert "different projective profiles" in ledger["off_center_status"]
    assert ledger["valid_perturbation_space"] == "the one-dimensional fold mode only"


def test_composite_displacement_formula():
    assert composite.composite_displacement() == (
        -composite.DELTA_F / composite.NORMAL_F
    )


@pytest.mark.parametrize("tau", [-1, 1])
@pytest.mark.parametrize("scalar_sign", [-1, 1])
def test_blowup_response_reproduces_v6_1_7_endpoint_slope(tau, scalar_sign):
    expected = composite.endpoint_slope(tau) * composite.DELTA_Q
    assert sp.simplify(
        composite.recovered_endpoint_displacement(tau, scalar_sign) - expected
    ) == 0


def test_endpoint_response_exact_coefficient_not_just_sign():
    ledger = composite.embedding_response_ledger()
    assert ledger["endpoint_slope_plus"] == "-chi_1/4"
    assert ledger["endpoint_slope_minus"] == "+chi_1/4"
    assert "exactly reproduces" in ledger["v6_1_7_comparison"]


def test_independent_and_dependent_embedding_count():
    ledger = composite.configuration_space_ledger()
    assert len(ledger["current_independent"]) == 6
    assert ledger["current_embedding"] == "fixed iota in the provisional B1 domain"
    assert ledger["candidate_dependent_support"] == "iota=iota[sigma_hat]"
    assert ledger["required_by_current_action"] is False
    assert ledger["currently_adopted"] is False


def test_bulk_sigma_is_not_intrinsic_sigma_partial():
    ledger = composite.configuration_space_ledger()
    assert ledger["sigma_partial_relation"].startswith("independent")
    assert composite.GUARDS["sigma_identified_with_sigma_partial"] is False


def test_composite_support_is_an_additional_domain_identification():
    ledger = composite.configuration_space_ledger()
    assert ledger["coefficient_free_on_center_manifold"] is True
    assert "additional off-shell domain restriction" in ledger["classification"]


def test_distributional_surface_formula_is_only_a_crosscheck():
    ledger = composite.action_and_variation_ledger()
    assert "delta(f)|grad f|" in ledger["fixed_regular_surface_identity"]
    assert ledger["distributional_role"] == "cross-check only; no duplicate action term"
    assert ledger["two_cap_count"].startswith("the common Z2 junction is counted once")


def test_fixed_and_field_dependent_support_are_not_variationally_equivalent():
    ledger = composite.action_and_variation_ledger()
    assert ledger["fixed_f_equivalence"].startswith("surface and delta-function")
    assert ledger["varied_f_equivalence"] is False
    assert "moves support" in ledger["reason_varied_f_changes_domain"]


def test_no_new_density_but_conditional_domain_coupling():
    ledger = composite.action_and_variation_ledger()
    assert ledger["new_local_term"] is False
    assert ledger["new_coefficient"] is False
    assert "scalar-B1 coupling" in ledger["conditional_interaction"]


def test_shape_equation_is_not_promoted_from_an_unadopted_domain():
    ledger = composite.action_and_variation_ledger()
    assert ledger["shape_status_current_action"].startswith("absent")
    assert ledger["Noether_identity"] is True
    assert "normal diffeomorphism Ward combination" in (
        ledger["shape_status_conditional"]
    )


def test_Dirichlet_data_are_not_double_imposed():
    ledger = composite.scalar_boundary_ledger()
    assert "independently imposed Dirichlet" in ledger["fixed_support"]
    assert ledger["composite_support_identity"].startswith(
        "delta sigma_hat_Sigma"
    )
    assert ledger["double_imposition_allowed"] is False


def test_composite_scalar_variation_derives_no_current_action_flux_condition():
    ledger = composite.scalar_boundary_ledger()
    assert ledger["natural_flux_condition_derived"] is False
    assert ledger["new_wall_pressure_condition_derived"] is False
    assert "no variational force" in ledger["current_action_result"]


def test_composite_threading_invariant_substitutes_displacement():
    expected = (
        composite.B_SHIFT
        - composite.N0**2 * composite.DELTA_HAT / composite.NORMAL_HAT
        - composite.A0**2 * composite.E_RHO
    )
    assert sp.simplify(composite.composite_threading_invariant() - expected) == 0


def test_composite_support_does_not_set_threading_invariant():
    ledger = composite.threading_and_power_ledger()
    assert ledger["support_condition_supplies"].startswith("one relation fixing zeta")
    assert ledger["condition_on_S_Sigma"] is None
    assert ledger["B1_conditions_on_invariant_threading"] == 0
    assert ledger["unresolved_endpoint_traces"] == 1


def test_constraint_order_and_kernel_are_not_invented():
    ledger = composite.threading_and_power_ledger()
    assert ledger["radial_constraint_order"].startswith("not derived")
    assert "at least one boundary trace" in ledger["residual_kernel_dimension"]
    assert ledger["pseudoinverse"] is False
    assert ledger["Green_ready"] is False


def test_q_to_zero_power_counting():
    power = composite.threading_and_power_ledger()["power_counting"]
    assert power["sigma_prime_Sigma"] == "O(q)"
    assert power["sigma_hat_prime_Sigma"] == "O(1)"
    assert "delta sigma/q" in power["zeta_direct_generic"]
    assert "delta sigma_hat" in power["zeta_blowup_center_tangent"]


def test_only_center_manifold_tangents_are_finite():
    ledger = composite.threading_and_power_ledger()
    assert any("fixed (tau,s)" in item for item in ledger["finite_variations"])
    assert "scalar-sign flip" in ledger["discrete_not_infinitesimal"]
    assert "arbitrary off-branch scalar fluctuations" in ledger["singular_or_ambiguous"]


def test_fold_kinetic_coefficient_remains_unavailable():
    ledger = composite.threading_and_power_ledger()
    assert ledger["k_q_E_at_fold_calculable"] is False
    assert "controlled q->0 limit" in ledger["fold_route"]
    assert ledger["result"] == composite.PRIMARY_RESULT


def test_preserved_v6_12_and_v6_13_results():
    preserved = composite.integrity_ledger()["preserved"]
    assert preserved["F0_equals_M4_squared"] == "pi/2"
    assert preserved["K_scalar"] == ">=2>0"
    assert "(4-pi)^2" in preserved["K_Weyl"]
    assert preserved["v6_13_result"].endswith("SHIFT_BOUNDARY_DATA")


def test_integrity_guards():
    for payload in composite.artifact_payloads().values():
        assert all(payload[name] is False for name in composite.GUARDS)


def test_exactly_three_deterministic_artifacts():
    expected = composite.artifact_bytes()
    assert len(expected) == 3
    assert set(expected) == set(composite.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = composite.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
