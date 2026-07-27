from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import minimum_threading_fold_kinetic as fold


ROOT = Path(__file__).resolve().parents[1]


def test_exact_axiom_text_and_classification():
    axiom = fold.axiom_ledger()
    assert axiom["name"] == "BHSM_MINIMUM_NET_THREADING_AXIOM"
    assert axiom["statement"] == fold.AXIOM_TEXT
    assert axiom["classification"] == "Adopted BHSM axiom"
    assert "Sbar_Sigma(x)=1/2" in axiom["statement"]


def test_axiom_is_not_retroactively_derived_from_old_action():
    axiom = fold.axiom_ledger()
    assert axiom["old_action_derivation_claimed"] is False
    assert "not previously derived" in axiom["historical_status"]


def test_axiom_adds_no_coefficient_or_potential():
    axiom = fold.axiom_ledger()
    assert axiom["coefficient_free"] is True
    assert axiom["new_action_term"] is False
    assert axiom["seam_potential_adopted"] is False
    assert axiom["seam_stiffness_coefficient"] is None


def test_no_spatiotemporal_structure_is_assigned_to_core():
    core = fold.axiom_ledger()["common_core"]
    assert core
    assert all(value is None for value in core.values())
    assert fold.GUARDS["metric_assigned_to_common_core"] is False


def test_required_claim_classifications_only():
    allowed = {
        "Adopted from established physics/mathematics",
        "Adopted BHSM axiom",
        "BHSM identification",
        "Derived consequence",
        "Numerically validated",
        "Rejected by calculation",
        "Active construction target",
    }
    rows = fold.provenance_ledger()
    assert rows
    assert all(row["status"] in allowed for row in rows)
    assert any(row["status"] == "Rejected by calculation" for row in rows)


def test_threading_average_and_Z2_one_cap_equivalence():
    s = sp.symbols("s")
    assert fold.threading_average(s, s) == s
    z2 = fold.consistency_ledger()["Z2"]
    assert z2["average_rule_equivalent_to_one_cap_zero"] is True
    assert z2["glue_jet_difference_preserved"] is True


def test_axiom_is_gauge_invariant():
    gauge = fold.consistency_ledger()["gauge"]
    assert gauge["Sbar_invariant_under_declared_diffeomorphisms"] is True
    assert gauge["E_zero_gauge_allowed"] is True
    assert gauge["fixed_support_form"] == (
        "E=0 and zeta=0 imply S_Sigma=B_Sigma"
    )


def test_axiom_does_not_duplicate_metric_junction():
    junction = fold.consistency_ledger()["junction"]
    assert junction["duplicated_by_axiom"] is False
    assert "kappa_1[Q_mu_nu]" in junction["independent_metric_condition"]


def test_axiom_does_not_duplicate_Ward_identity():
    ward = fold.consistency_ledger()["Ward"]
    assert ward["Codazzi_Bianchi_counted_as_new_equation"] is False
    assert ward["axiom_duplicates_Ward_identity"] is False


def test_fixed_support_is_official_least_assumption_domain():
    support = fold.consistency_ledger()["support"]
    assert support["official"].startswith("fixed-iota")
    assert support["fixed_iota"] == "axiom gives B_Sigma=0 in E=0 gauge"


def test_composite_support_does_not_change_invariant_obstruction():
    support = fold.consistency_ledger()["support"]
    assert "same invariant S_Sigma=0" in support["composite_center_manifold"]
    assert support["support_choice_changes_obstruction"] is False


def test_v616_cost_does_not_derive_a_minimum():
    seam = fold.consistency_ledger()["v6_16_seam_cost"]
    assert seam["zero_trace_is_stationary"] is True
    assert seam["old_action_proves_minimum"] is False
    assert seam["conflict_with_homogeneous_resting_background"] is False


def test_exact_critical_background_functions():
    t = sp.symbols("t")
    assert fold.a0(t) == sp.sqrt(2) * sp.sin(sp.pi * t / 4)
    assert fold.N_0 == sp.pi / 4
    assert fold.X_CRITICAL == 2


def test_inherited_shift_source_is_preserved():
    expected = (
        -3
        * fold.TAU
        * fold.CHI_1
        * fold.T
        / (4 * sp.sin(sp.pi * fold.T / 4) ** 2)
    )
    assert sp.simplify(fold.inherited_shift_source() - expected) == 0


def test_leading_threading_suboperator_is_radial_order_zero():
    operator = fold.leading_constraint_operator_ledger()
    block = operator["critical_subblock"]
    assert block["radial_differential_order"] == 0
    assert "no radial derivative" in block["reason"]
    assert block["equation"] == "J_shift(t)+L_S(t)S_q(t)=0"


def test_exact_threading_operator_coefficient():
    expected = -12 / (
        sp.pi * sp.sin(sp.pi * fold.T / 4) ** 2
    )
    assert sp.simplify(fold.threading_operator_coefficient() - expected) == 0


def test_exact_required_threading_profile():
    expected = -sp.pi * fold.TAU * fold.CHI_1 * fold.T / 16
    assert sp.simplify(fold.required_threading_profile() - expected) == 0


def test_required_profile_solves_momentum_constraint():
    residual = (
        fold.inherited_shift_source()
        + fold.threading_operator_coefficient()
        * fold.required_threading_profile()
    )
    assert sp.simplify(residual) == 0


def test_required_profile_is_pole_regular():
    profile = fold.required_threading_profile()
    assert sp.limit(profile, fold.T, 0, dir="+") == 0
    pole = fold.consistency_ledger()["pole"]
    assert pole["regular"] is True
    assert pole["axiom_alone_conflicts_with_pole_regularity"] is False


def test_required_endpoint_trace_is_nonzero():
    expected = -sp.pi * fold.TAU * fold.CHI_1 / 16
    assert fold.required_endpoint_threading() == expected
    assert expected != 0


@pytest.mark.parametrize("tau", (-1, 1))
def test_axiom_leaves_nonzero_endpoint_momentum_residual(tau):
    residual = fold.axiom_endpoint_residual(tau, fold.CHI_1)
    assert residual == -sp.Rational(3, 2) * tau * fold.CHI_1
    assert residual != 0


def test_critical_scalar_flux_cannot_cancel_residual():
    junction = fold.consistency_ledger()["junction"]
    assert junction["critical_scalar_flux"] == 0
    assert junction["critical_endpoint_H_q"] == "tau*chi_1/2"


def test_condition_count_closes_formally_but_domain_is_empty():
    count = fold.consistency_ledger()["condition_count"]
    assert count["unresolved_trace_before"] == 1
    assert count["new_scalar_trace_conditions"] == 1
    assert count["formal_free_trace_after"] == 0
    assert count["duplicate_conditions"] == 0
    assert count["admissible_dynamical_fold_solutions_after"] == 0


def test_full_constraint_vector_is_recorded_without_fake_operator():
    operator = fold.leading_constraint_operator_ledger()
    assert operator["full_requested_unknown_vector"] == [
        "A",
        "B",
        "psi",
        "E",
        "delta sigma",
        "zeta",
    ]
    assert operator["full_L_C_constructed"] is False
    assert operator["why_full_construction_stops"] == fold.DOMAIN_RESULT


def test_measure_inner_product_and_subblock_adjoint():
    operator = fold.leading_constraint_operator_ledger()
    assert operator["radial_measure"] == (
        "N0*a0(t)^4 dt for the inherited scalar ADM pairing"
    )
    assert operator["formal_adjoint_subblock"] == (
        "L_S^dagger=L_S (real multiplication)"
    )
    assert operator["Green_boundary_form_subblock"] == 0


def test_source_fails_adopted_boundary_compatibility():
    operator = fold.leading_constraint_operator_ledger()
    assert operator["B1_domain_adopted"] == (
        "S_q(1)=0 from S_Sigma(q)=0 for all q"
    )
    assert operator["source_compatibility_condition"] == "J_shift(1)=0"
    assert operator["actual_source_endpoint"] == "-3 tau chi_1/2"
    assert operator["source_compatible"] is False


def test_no_full_kernel_or_Fredholm_claim_is_invented():
    operator = fold.leading_constraint_operator_ledger()
    assert operator["subblock_kernel_dimension"] == 0
    assert operator["full_kernel_dimension"] is None
    assert operator["full_adjoint_kernel_dimension"] is None
    assert operator["Fredholm_index"] is None
    assert operator["strong_ellipticity"] is None


def test_no_generic_pseudoinverse_or_projector():
    operator = fold.leading_constraint_operator_ledger()
    assert operator["projector"] is None
    assert operator["generic_pseudoinverse_used"] is False
    assert fold.GUARDS["generic_pseudoinverse"] is False


def test_local_inverse_fails_to_map_into_adopted_domain():
    green = fold.green_operator_ledger()
    assert green["local_inverse_result"] == (
        "S_q,req=-tau*pi*chi_1*t/16"
    )
    assert green["maps_source_into_adopted_domain"] is False
    assert green["Green_operator_on_adopted_domain"] is None


def test_no_numerical_solver_is_run_after_stop_rule():
    green = fold.green_operator_ledger()
    for key in (
        "shooting_method_run",
        "collocation_method_run",
        "spectral_method_run",
    ):
        assert green[key] is False
    assert green["stop_rule_applied"] is True


def test_endpoint_obstruction_is_sheet_odd_and_scalar_sign_even():
    obstruction = fold.endpoint_obstruction_ledger()
    upper = obstruction["upper_exterior_tau_plus"]
    lower = obstruction["lower_core_tau_minus"]
    assert upper["partial_q_S_required"] == -lower["partial_q_S_required"]
    assert upper["momentum_residual"] == -lower["momentum_residual"]
    assert obstruction["scalar_sign_independent"] is True


def test_normalized_fold_constants_are_preserved():
    obstruction = fold.endpoint_obstruction_ledger()
    assert obstruction["normalized_chi_1"] == pytest.approx(
        5.26830787154212
    )
    assert obstruction["normalized_nu_1"] == pytest.approx(
        109.6666817404231
    )


def test_q_to_zero_sequence_is_analytically_blocked():
    obstruction = fold.endpoint_obstruction_ledger()
    assert obstruction["analytic_q_to_zero"] == (
        "S_Sigma(q)=-tau*pi*chi_1*q/16+O(q^2)"
    )
    assert obstruction["convergence_study_started"] is False
    assert "bounded away from zero" in obstruction["reason"]


def test_kinetic_components_are_not_fabricated():
    kinetic = fold.kinetic_ledger()
    assert kinetic["K_shift_endpoint_red"] is None
    assert kinetic["K_scalar_at_fold"] == ">=2>0"
    assert kinetic["K_Weyl_exact"].endswith(">0")
    assert kinetic["k_q_E"] is None
    assert kinetic["error_estimate"] is None


def test_Weyl_term_exact_and_numeric():
    expected = (
        3
        * fold.CHI_1**2
        * (4 - sp.pi) ** 2
        / (16 * sp.pi)
    )
    assert fold.weyl_kinetic_exact() == expected
    assert fold.kinetic_ledger()["K_Weyl_numeric"] == pytest.approx(
        1.220620174933802
    )


def test_fold_is_not_promoted_or_classified_as_ghost_or_null():
    kinetic = fold.kinetic_ledger()
    assert kinetic["fold_coordinate_promoted_to_4D_field"] is False
    assert kinetic["positive_norm"] is False
    assert kinetic["ghost"] is False
    assert kinetic["null_or_strongly_coupled"] is False
    assert kinetic["domain_inconsistent_for_fold_promotion"] is True


def test_rest_transition_rest_seam_scenario_is_separated():
    phases = fold.phase_separation_ledger()
    assert phases["classification"] == "BHSM identification"
    assert phases["early_or_initial_resting_phase"]["Sbar_Sigma"] == 0
    assert phases["fold_transition_phase"]["D_mu_q"] == "nonzero"
    assert "S_Sigma(x)=-tau*pi*chi_1*q(x)/16" in (
        phases["fold_transition_phase"]["constraint_required_trace"]
    )
    assert phases["late_or_final_resting_phase"][
        "physical_longitudinal_shift"
    ] == 0


def test_white_hole_language_is_conditional_and_core_gets_no_time():
    phases = fold.phase_separation_ledger()
    assert "possible BHSM interpretation" in phases["white_hole_interpretation"]
    assert "not derived" in phases["white_hole_interpretation"]
    assert phases["time_assigned_to_common_core"] is False
    assert phases["time_location"] == "M4/interface history only"


def test_phase_dependent_rule_needs_new_covariant_evolution_law():
    phases = fold.phase_separation_ledger()
    assert phases["rescues_hard_all_harmonic_domain"] is False
    assert "covariant phase criterion" in phases["required_for_adoption"]
    assert "different domain" in phases["reason"]


def test_static_sheet_result_is_preserved_without_mass_claim():
    static = fold.static_sheet_ledger()
    assert static["fixed_mu_curvature"] == (
        "B_tau^red=-tau(nu_1/2)q+O(q^2)"
    )
    assert static["exterior_tau_plus"].startswith("negative")
    assert static["core_tau_minus"].startswith("positive")
    assert static["m_ext_squared"] is None
    assert static["m_core_squared"] is None


def test_exact_domain_and_kinetic_verdicts():
    verdict = fold.verdict_ledger()
    assert verdict["domain_theorem"] == (
        "BHSM_MINIMUM_THREADING_AXIOM_OVERCONSTRAINS_FOLD_CONSTRAINT"
    )
    assert verdict["kinetic_theorem"] == (
        "BHSM_FOLD_KINETIC_REMAINS_UNRESOLVED_BY_EXACT_OPERATOR_OBSTRUCTION"
    )
    assert verdict["admissible_fold_domain_after_axiom"] == (
        "empty at leading D_mu q order"
    )


def test_preserved_v615_v616_and_glue_average_distinction():
    preserved = fold.integrity_ledger()["preserved"]
    assert preserved["v6_15"] == (
        "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE"
    )
    assert preserved["v6_16"] == (
        "BHSM_SEAM_SLIDE_HAS_NONZERO_HIGHER_ORDER_ACTION_COST"
    )
    assert preserved["lambda_jet"] == "S_out,+-S_out,-"
    assert preserved["Sbar"] == "(S_out,++S_out,-)/2"


def test_model_map_contains_all_required_sectors():
    model_map = fold.closure_map_ledger()
    required = {
        "parent_core_topology",
        "P1_geometry",
        "B1_intrinsic_action",
        "scalar_wall_fold",
        "fold_kinetic_sector",
        "gauge_connections",
        "fermionic_action_domain",
        "charged_current_CKM",
        "neutral_propagation_PMNS",
        "dimensionful_scale_bridge",
        "scalar_topographic_sector",
        "prediction_falsification_layer",
    }
    assert set(model_map) == required


def test_integrity_guards():
    assert all(value is False for value in fold.GUARDS.values())
    for payload in fold.artifact_payloads().values():
        assert all(payload[key] is False for key in fold.GUARDS)


def test_exactly_four_deterministic_artifacts():
    expected = fold.artifact_bytes()
    assert len(expected) == 4
    assert set(expected) == set(fold.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = fold.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
