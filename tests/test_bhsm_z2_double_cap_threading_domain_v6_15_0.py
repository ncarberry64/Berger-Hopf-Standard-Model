from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import z2_double_cap_threading_domain as domain


ROOT = Path(__file__).resolve().parents[1]


def test_signed_coordinate_reconstructs_the_two_caps():
    rho, rho_j = sp.symbols("rho rho_J", real=True)
    assert domain.signed_coordinate("+", rho, rho_j) == rho - rho_j
    assert domain.signed_coordinate("-", rho, rho_j) == rho_j - rho
    with pytest.raises(ValueError):
        domain.signed_coordinate("unknown", rho, rho_j)


def test_cap_derivative_and_outward_normal_reversal():
    assert domain.cap_derivative_to_common_factor("+") == 1
    assert domain.cap_derivative_to_common_factor("-") == -1
    assert domain.outward_to_common_factor("+") == 1
    assert domain.outward_to_common_factor("-") == -1
    normals = domain.orientation_ledger()["normals"]
    assert normals["required_check"] == (
        "n_-=-n_+ under the interface identification"
    )


def test_common_and_outward_extrinsic_curvature_signs_are_distinct():
    curvature = domain.orientation_ledger()["extrinsic_curvature"]
    assert curvature["common"] == "K_common,-=-K_common,+"
    assert curvature["outward"] == (
        "K_out,-=K_out,+ for reflection-copied caps"
    )
    assert curvature["Q"].endswith("[Q]=2Q_common,+")
    assert curvature["nonzero_allowed"] is True
    assert curvature["K_zero_inferred"] is False


def test_scalar_normal_derivative_signs_are_oriented():
    scalar = domain.orientation_ledger()["scalar_normal_derivative"]
    assert scalar["signed_y"] == "partial_y sigma is reflection even"
    assert scalar["common"] == "(n_common sigma)_-=(n_common sigma)_+"
    assert scalar["outward"] == "(n_- sigma)_-=-(n_+ sigma)_+"


def test_metric_component_parity_is_derived_from_pullback():
    assert domain.reflection_component_parity(0) == 1
    assert domain.reflection_component_parity(1) == -1
    assert domain.reflection_component_parity(2) == 1
    with pytest.raises(ValueError):
        domain.reflection_component_parity(-1)
    ledger = domain.parity_ledger()
    assert "Jacobian diag(-1,1,1,1,1)" in ledger["derivation"]
    assert ledger["metric_pullback"] == {
        "g_yy": "even",
        "g_y_mu": "odd",
        "g_mu_nu": "even",
    }


def test_ADM_lapse_shift_and_metric_scalar_parities():
    fields = domain.parity_ledger()["ADM_fields_signed_y"]
    assert fields["N"].startswith("even")
    assert fields["N_mu"] == "odd"
    assert fields["B"] == "odd"
    assert fields["psi"] == "even"
    assert fields["E"] == "even"


def test_scalar_background_fold_and_gauge_parities_are_separated():
    scalar = domain.parity_ledger()["scalar"]
    assert scalar["background"].startswith("odd")
    assert scalar["fold_amplitude_perturbation"] == "odd"
    assert scalar["sigma_hat"].startswith("odd")
    assert "decomposes into even and odd" in (
        scalar["unrestricted_cover_perturbation"]
    )
    assert "sigma_0' is even" in scalar["pure_radial_gauge_perturbation"]


def test_fixed_gluing_gauge_parameters_have_derived_parity():
    gauge = domain.parity_ledger()["gauge_parameters"]
    assert gauge["xi^y"].startswith("odd")
    assert gauge["xi^y_at_Sigma"] == 0
    assert gauge["xi"] == "even tangential scalar"


def test_endpoint_gauge_invariants_have_consistent_parity():
    invariants = domain.parity_ledger()["gauge_invariants"]
    assert invariants["Psi_Sigma"] == "even"
    assert invariants["delta_sigma_Sigma"].startswith("odd")
    assert invariants["delta_X_Sigma"] == "even"
    assert invariants["S_Sigma_common"] == "odd one-sided trace"
    assert invariants["S_Sigma_outward"].startswith("equal")


def test_Z2_relates_threading_traces_but_does_not_set_zero():
    parity = domain.parity_ledger()
    assert parity["threading_relations"]["common"] == (
        "S_common,-=-S_common,+"
    )
    assert parity["threading_relations"]["outward"] == "S_out,-=S_out,+"
    assert parity["threading_relations"]["zero_forced_by_parity"] is False
    trace = domain.threading_trace()
    assert domain.common_threading_from_outward("+", trace) == trace
    assert domain.common_threading_from_outward("-", trace) == -trace


def test_background_fixed_and_moving_Z2_are_not_conflated():
    ledger = domain.z2_notions_ledger()
    assert ledger["A_background_cap_exchange"]["contained"] is True
    assert ledger["B_fixed_support_orbifold_parity"]["contained"] is True
    assert ledger["C_moving_covariant_reflection"]["contained"] is False
    assert "does not promote R" in ledger["homogeneous_family"]
    assert ledger["result"] == domain.MOVING_RESULT


def test_junction_regularity_does_not_impose_smooth_K_zero():
    ledger = domain.regularity_ledger()
    assert "continuous induced metric" in ledger["geometry_class"]
    assert "normal derivative may jump" in ledger["h_mu_nu"]
    assert ledger["K_and_Q"].startswith("finite one-sided")
    assert ledger["erroneous_smoothness_condition"] == "K=0 is rejected"


def test_odd_trace_vanishing_requires_continuity():
    ledger = domain.regularity_ledger()
    assert "only after continuity" in ledger["odd_trace_rule"]
    assert ledger["B_zero_from_parity"] is False
    assert ledger["partial_y_E_zero_from_parity"] is False


def test_allowed_double_cap_diffeomorphisms_preserve_gluing():
    ledger = domain.diffeomorphism_ledger()
    assert "xi^y|Sigma=0" in ledger["gluing_preserving"]
    assert "changes the declared fixed set" in ledger["interface_moving"]
    assert ledger["S_Sigma_gauge_invariant"] is True
    assert ledger["global_Z2_removes_trace_as_gauge"] is False


def test_gauge_choices_cannot_delete_threading_trace():
    choices = domain.diffeomorphism_ledger()["gauge_choices"]
    assert "not a removal of S_Sigma" in choices["zeta_zero"]
    assert choices["E_zero"] == "allowed with even xi"
    assert "cannot change the invariant" in choices["B_zero"]
    assert "only when S_Sigma was already zero" in choices["all_three_zero"]


@pytest.mark.parametrize("tau", [-1, 1])
def test_reflected_source_sign_in_both_orientation_conventions(tau):
    source = domain.one_cap_shift_source(tau=tau)
    assert domain.reflected_shift_source("+", orientation="outward", tau=tau) == (
        source
    )
    assert domain.reflected_shift_source("-", orientation="outward", tau=tau) == (
        source
    )
    assert domain.reflected_shift_source("+", orientation="common", tau=tau) == (
        source
    )
    assert domain.reflected_shift_source("-", orientation="common", tau=tau) == (
        -source
    )


def test_two_cap_source_sector_sheet_and_scalar_sign():
    ledger = domain.constraint_source_ledger()
    assert ledger["signed_interval_sector"] == "odd"
    assert ledger["tau_dependence"].startswith("tau reverses")
    assert ledger["scalar_sign_dependence"] is False
    assert ledger["sheet_dependence"] is True
    assert ledger["result"] == domain.SOURCE_PARITY_RESULT


def test_source_has_only_partial_automatic_compatibility():
    ledger = domain.constraint_source_ledger()
    assert ledger["even_weight_integral"] == 0
    assert "even constant test mode" in ledger["automatic_compatibility"]
    assert ledger["full_Fredholm_compatibility_certified"] is False
    assert "adjoint kernels" in ledger["reason_full_compatibility_open"]


def test_exact_cap_metric_and_scalar_canonical_pairs():
    ledger = domain.canonical_pairing_ledger()
    assert ledger["cap_metric_pair"]["configuration"] == "gamma_mu_nu"
    assert "Q_out" in ledger["cap_metric_pair"]["momentum"]
    assert "[Q_mu_nu]" in ledger["common_orientation_metric_sum"]
    assert ledger["scalar_pair"]["configuration"] == "delta sigma_Sigma"
    assert "n_out sigma" in ledger["scalar_pair"]["momentum"]


def test_matching_multiplier_is_eliminated_not_propagated():
    ledger = domain.canonical_pairing_ledger()
    assert "algebraically" in ledger["matcher"]
    assert "cancels from the combined junction" in ledger["matcher"]


def test_threading_is_multiplier_trace_not_canonical_pair():
    threading = domain.canonical_pairing_ledger()["threading"]
    assert "multiplier trace" in threading["classification"]
    assert threading["canonical_momentum"] == 0
    assert threading["Euler_Lagrange_partner"] == (
        "bulk longitudinal momentum constraint"
    )
    assert threading["independent_interface_conjugate"] is None
    assert threading["present_in_symplectic_form"] is False


def test_scalar_junction_projection_count_and_Ward_dependencies():
    ledger = domain.junction_projection_ledger()
    assert ledger["raw_projection_count"] == 4
    assert ledger["scalar_Ward_relations"] == 2
    assert ledger["independent_scalar_equation_count"] == 2
    assert ledger["longitudinal_counted_twice"] is False
    assert "Codazzi" in ledger["dependencies"]["longitudinal"]


def test_no_independent_junction_projection_fixes_threading():
    ledger = domain.junction_projection_ledger()
    assert "no independent scalar projection" in ledger["S_occurrence"]
    assert ledger["condition_on_S_Sigma"] is None


def test_total_symplectic_flux_uses_all_action_sectors():
    ledger = domain.symplectic_flux_ledger()
    assert "Theta_Sigma,total" in ledger["boundary_form"]
    assert "J_mu_nu" in ledger["metric_term"]
    assert "n_out sigma" in ledger["scalar_term"]
    assert ledger["matcher_term"].startswith("zero after")
    assert len(ledger["conditions_applied"]) == 6


def test_flux_vanishes_without_a_threading_condition():
    ledger = domain.symplectic_flux_ledger()
    assert ledger["metric_flux_on_domain"] == 0
    assert ledger["scalar_flux_on_fixed_Dirichlet_domain"] == 0
    assert ledger["S_Sigma_term"] is None
    assert ledger["vanishing_flux_requires"].startswith("no condition")
    assert ledger["result"] == domain.PRIMARY_RESULT


def test_all_candidate_flux_conditions_are_classified():
    options = domain.symplectic_flux_ledger()["options"]
    assert options["S_zero"] is False
    assert options["common_orientation_relation"] == "S_common,-=-S_common,+"
    assert options["outward_orientation_relation"] == "S_out,-=S_out,+"
    assert options["momentum_matching_for_S"] is False
    assert options["Robin_relation"] is False
    assert options["cap_flux_cancellation_for_arbitrary_common_trace"] is True


def test_presymplectic_null_trace_dimension():
    ledger = domain.symplectic_flux_ledger()
    assert ledger["parity_allowed_null_trace_dimension"] == 1
    assert ledger["Robin_family_parameter_dimension"] is None
    assert "presymplectic null direction" in (
        ledger["maximal_isotropic_conclusion"]
    )


def test_fixed_support_leaves_one_trace():
    case = domain.support_domain_ledger()["Case_I_fixed_iota"]
    assert case["adopted"] is True
    assert case["zeta"] == 0
    assert case["symplectic_condition_on_S"] is None
    assert case["unresolved_interface_traces"] == 1


def test_composite_support_still_leaves_one_trace():
    case = domain.support_domain_ledger()["Case_II_composite_support"]
    assert case["adopted"] is False
    assert case["zeta"].startswith("-delta sigma_hat")
    assert case["symplectic_condition_on_S"] is None
    assert case["unresolved_interface_traces"] == 1
    assert case["closes_domain"] is False
    assert "identify iota off shell" in case["required_axiom"]


def test_moving_reflection_center_is_an_extra_domain_datum():
    case = domain.support_domain_ledger()["moving_reflection_center"]
    assert case["adopted"] is False
    assert case["adapted_coordinate"] == "y_tilde=y-zeta(x)"
    assert case["fixed_double_diffeomorphism"] is False
    assert "gauge-invariant S_Sigma" in case["S_in_adapted_coordinate"]


def test_adapted_zero_threading_shortcut_is_rejected():
    shortcut = domain.support_domain_ledger()["zero_threading_shortcut"]
    assert shortcut["accepted"] is False
    assert len(shortcut["failures"]) == 5
    assert any("continuity of B" in item for item in shortcut["failures"])
    assert any("partial_y E" in item for item in shortcut["failures"])
    assert shortcut["result"] == domain.SHORTCUT_RESULT


def test_constraint_compensator_and_interface_domain_count():
    ledger = domain.domain_count_ledger()
    assert ledger["bulk_scalar_metric_function_count"] == 4
    assert ledger["differential_order_each_cap"] is None
    assert "not invented" in ledger["order_status"]
    assert ledger["unresolved_interface_trace_count"] == 1
    assert "S_out,+ = S_out,-" in ledger["free_trace"]


def test_pole_regularity_and_matching_data_are_recorded():
    ledger = domain.domain_count_ledger()
    assert ledger["pole_regularity"]["M_+"] == "regular at rho_+=0"
    assert ledger["pole_regularity"]["M_-"] == "regular at rho_-=0"
    assert len(ledger["interface_matching"]) == 4
    assert len(ledger["gauge_kernels"]) == 2


def test_no_physical_kernel_or_Green_domain_is_invented():
    ledger = domain.domain_count_ledger()
    assert ledger["physical_homogeneous_kernel_dimension"] is None
    assert "not promoted to a physical radion" in ledger["kernel_status"]
    assert ledger["Green_ready"] is False
    assert ledger["boundary_operator_for_next_sprint"] is None
    assert ledger["adjoint_interface_operator"] is None
    assert ledger["pseudoinverse_used"] is False


def test_exact_primary_verdict_and_fold_route_decision():
    verdict = domain.verdict_ledger()
    assert verdict["primary_theorem"] == (
        "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE"
    )
    assert verdict["selected_threading_condition"] is None
    assert verdict["unresolved_interface_trace_count"] == 1
    assert verdict["coefficient_free_closure_achieved"] is False
    assert verdict["Green_operator_ready"] is False
    assert verdict["fold_route_decision"].startswith("C.")
    assert verdict["k_q_E_certified"] is False


def test_required_status_vocabulary():
    allowed = {
        "Adopted from established physics/mathematics",
        "Adopted BHSM axiom",
        "BHSM identification",
        "Derived consequence",
        "Numerically validated",
        "Rejected by calculation",
        "Active construction target",
    }
    rows = domain.provenance_ledger()
    assert rows
    assert all(row["status"] in allowed for row in rows)
    assert any(row["status"] == "Rejected by calculation" for row in rows)


def test_inherited_results_are_preserved():
    preserved = domain.integrity_ledger()["preserved"]
    assert preserved["v6_13"].endswith("SHIFT_BOUNDARY_DATA")
    assert preserved["v6_14"].endswith("THREADING_OPEN")
    assert preserved["endpoint_response"] == "partial_q rho_J,tau=-tau chi_1/4"
    assert preserved["fold_displacement"] == "zeta_0=-tau chi_1 delta q/4"
    assert preserved["F0_equals_M4_squared"] == "pi/2"
    assert preserved["K_scalar"] == ">=2>0"
    assert "(4-pi)^2" in preserved["K_Weyl"]


def test_integrity_guards():
    assert all(value is False for value in domain.GUARDS.values())
    for payload in domain.artifact_payloads().values():
        assert all(payload[name] is False for name in domain.GUARDS)


def test_exactly_three_deterministic_artifacts():
    expected = domain.artifact_bytes()
    assert len(expected) == 3
    assert set(expected) == set(domain.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = domain.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
