from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import seam_slide_symmetry_quotient as seam


ROOT = Path(__file__).resolve().parents[1]


def test_core_contact_source_ledger_finds_no_functional():
    ledger = seam.source_and_provenance_ledger()
    assert ledger["stored_action"]["core_contact_functional"] is None
    assert ledger["core_contact_functional_present"] is False
    assert ledger["result"] == seam.CORE_RESULT


def test_stored_action_and_domain_are_separated_from_proposal():
    ledger = seam.source_and_provenance_ledger()
    assert ledger["stored_action"]["P1"] == "explicit"
    assert ledger["stored_action"]["metric_matcher"] == "explicit"
    assert ledger["stored_domain"]["fixed_B1_embedding"] == "explicit"
    assert ledger["stored_domain"]["seam_slide_group"] is None
    assert "candidate coefficient-free BHSM identification" in (
        ledger["uniform_contact_statement"]
    )


def test_no_metric_or_spatiotemporal_data_are_assigned_to_core():
    core = seam.source_and_provenance_ledger()["core_doctrine"]
    assert core["stored_statement"] == "common core is non-spatiotemporal"
    for key in (
        "metric",
        "distance",
        "duration",
        "density",
        "ordinary_inside_outside",
        "core_transfer_mechanism",
    ):
        assert core[key] is None
    assert seam.GUARDS["metric_assigned_to_common_core"] is False


def test_required_provenance_vocabulary():
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
    rows = seam.provenance_ledger()
    assert rows
    assert all(row["status"] in allowed for row in rows)
    assert any(row["status"] == "BHSM identification" for row in rows)


def test_zeta_q_and_threading_are_distinct_variables():
    ledger = seam.variable_separation_ledger()
    assert ledger["wall_position"]["variable"] == "zeta(x)"
    assert ledger["fold_amplitude"]["variable"] == "q(x)"
    assert ledger["threading"]["variable"] == "S_Sigma(x)"
    assert ledger["wall_translation_is_seam_slide"] is False


def test_minimal_seam_candidate_moves_only_threading():
    candidate = seam.variable_separation_ledger()["minimal_seam_candidate"]
    assert candidate["delta_zeta"] == 0
    assert candidate["delta_q"] == 0
    assert candidate["delta_scalar_support"] == 0
    assert candidate["delta_S_Sigma"] == "lambda"


def test_collar_gluing_zeroth_and_first_jets():
    ledger = seam.gluing_jet_ledger()
    assert ledger["collars"]["U_+"] == "[-epsilon,0] x Sigma"
    assert ledger["collars"]["U_-"] == "[0,+epsilon] x Sigma"
    assert ledger["zeroth_jet"].startswith("Phi_0=phi_Sigma=id")
    assert ledger["first_jet"] == "V^mu=partial_y Phi_y^mu|0"
    assert ledger["decomposition"] == "V^mu=D^mu lambda_jet+V_T^mu"


def test_metric_pullback_fixes_glue_jet_normalization():
    ledger = seam.gluing_jet_ledger()
    assert "V^mu-N_-^mu" in ledger["metric_pullback"]
    assert ledger["cross_metric_relation"] == "V_mu=N_+,mu+N_-,mu"
    scalar = ledger["gauge_completed_scalar_relation"]
    assert scalar["common"] == "lambda_jet=S_common,++S_common,-"
    assert scalar["outward"] == "lambda_jet=S_out,+-S_out,-"
    assert scalar["normalization"] == "V^mu=D^mu lambda_jet"


def test_glue_jet_is_difference_while_threading_is_average():
    assert seam.glue_jet_potential() == seam.S_PLUS - seam.S_MINUS
    assert seam.threading_average() == (seam.S_PLUS + seam.S_MINUS) / 2
    reduced = seam.z2_reduce_gluing_data(sp.Symbol("s"))
    assert reduced["glue_jet_potential"] == 0
    assert reduced["threading_average"] == sp.Symbol("s")


def test_Z2_compatibility_does_not_fix_threading_average():
    ledger = seam.gluing_jet_ledger()
    assert ledger["Z2"]["relation"] == "S_out,+=S_out,-"
    assert ledger["Z2"]["glue_jet"] == 0
    assert ledger["first_jet_controls_unresolved_trace"] is False
    assert ledger["result"] == seam.JET_RESULT


def test_infinitesimal_candidate_has_derived_orientation_signs():
    ledger = seam.infinitesimal_candidate_ledger()
    assert ledger["definition_outward"].endswith("=lambda")
    assert "S_common,+=lambda" in ledger["definition_common"]
    assert "S_common,-=-lambda" in ledger["definition_common"]
    assert ledger["normal_shift"] == (
        "delta N_mu=D_mu lambda in each outward convention"
    )


def test_infinitesimal_candidate_is_not_wall_motion_or_old_gauge():
    laws = seam.infinitesimal_candidate_ledger()["minimal_field_laws"]
    assert laws["zeta"] == 0
    assert laws["q"] == 0
    assert laws["bulk_sigma"] == 0
    ledger = seam.infinitesimal_candidate_ledger()
    assert ledger["old_diffeomorphism"] is False
    assert "leave S_Sigma invariant" in ledger["reason_not_old_gauge"]


def test_candidate_preserves_induced_data_but_changes_Q():
    ledger = seam.infinitesimal_candidate_ledger()
    assert ledger["induced_metric"] == "unchanged at fixed support"
    assert ledger["scalar_pullback"] == "unchanged"
    assert ledger["boundary_stress"] == "intrinsic B1 stress unchanged"
    assert ledger["Q_jump"].startswith("changed generically")
    assert ledger["preserves_all_attempted_data"] is False


def test_extrinsic_curvature_and_Q_variations():
    x, y = sp.symbols("x y")
    hessian = sp.Matrix([[x, 0], [0, y]])
    assert seam.delta_extrinsic_curvature(hessian, 1) == sp.ImmutableMatrix(
        [[-x, 0], [0, -y]]
    )
    assert seam.delta_Q(hessian, 1) == sp.ImmutableMatrix(
        [[y, 0], [0, x]]
    )
    with pytest.raises(ValueError):
        seam.delta_Q(sp.Matrix([[1, 2]]))


def test_finite_map_identity_composition_and_inverse():
    s_plus, s_minus = sp.symbols("s_plus s_minus")
    lam1, lam2 = sp.symbols("lambda_1 lambda_2")
    assert seam.seam_slide_outward(s_plus, s_minus, 0) == (s_plus, s_minus)
    first = seam.seam_slide_outward(s_plus, s_minus, lam1)
    second = seam.seam_slide_outward(*first, lam2)
    combined = seam.seam_slide_outward(
        s_plus, s_minus, seam.compose_parameters(lam1, lam2)
    )
    assert second == combined
    assert seam.inverse_parameter(lam1) == -lam1


def test_finite_map_common_orientation_preserves_Z2_odd_relation():
    s, lam = sp.symbols("s lambda")
    transformed = seam.seam_slide_common(s, -s, lam)
    assert transformed == (s + lam, -s - lam)
    assert transformed[1] == -transformed[0]


def test_finite_map_regular_extension_and_global_status():
    ledger = seam.finite_map_ledger()
    assert ledger["domain"].startswith("maps the broad off-shell")
    assert ledger["extension_uniqueness"] is False
    assert "vanish near both poles" in ledger["extension_requirement"]
    assert ledger["Z2"].startswith("preserved")
    assert ledger["topology_change"] is False
    assert ledger["normal_bundle_holonomy"] is False
    assert "determinant is independent of shift" in ledger["metric_nondegeneracy"]


def test_constant_local_and_harmonic_behavior():
    ledger = seam.finite_map_ledger()
    assert "trivial scalar-potential stabilizer" in (
        ledger["constant_spacetime_lambda"]
    )
    harmonics = ledger["spatial_harmonics"]
    assert harmonics["ell=0_time_independent"] == "trivial stabilizer"
    assert harmonics["ell>=1"] == "nonzero Hessian and action cost"
    assert "D_time lambda" in harmonics["ell=0_time_dependent"]


def test_collar_flow_is_not_the_threading_slide_group():
    flow = seam.finite_map_ledger()["collar_flow_candidate"]
    assert flow["local_and_compact_global_flow"] is True
    assert flow["arbitrary_gradient_family_closed_under_composition"] is False
    assert "not generally a gradient" in flow["reason"]
    assert flow["acts_on"].endswith("not S_bar")


def test_shift_quadratic_density():
    x, y, z = sp.symbols("x y z")
    hessian = sp.diag(x, y, z)
    expected = (
        x**2 + y**2 + z**2 - (x + y + z) ** 2
    ) / seam.N**2
    assert sp.simplify(seam.shift_quadratic_density(hessian) - expected) == 0
    with pytest.raises(ValueError):
        seam.shift_quadratic_density(sp.Matrix([[1, 2]]))


def test_round_S3_harmonic_quadratic_cost():
    assert seam.s3_harmonic_integrated_density(0) == 0
    assert seam.s3_harmonic_integrated_density(1) == -6 / seam.A**4
    assert seam.s3_harmonic_integrated_density(2) == -16 / seam.A**4
    with pytest.raises(ValueError):
        seam.s3_harmonic_integrated_density(-1)


def test_action_is_not_off_shell_invariant():
    action = seam.action_audit_ledger()
    assert action["P1_plus_GHY"]["off_shell"] == "not invariant"
    assert "momentum-constraint contraction" in (
        action["P1_plus_GHY"]["linear"]
    )
    assert "(D_muD_nu lambda)^2" in action["P1_plus_GHY"]["quadratic"]
    assert action["invariance_levels"]["fully_off_shell"] is False
    assert action["invariance_levels"]["after_metric_matching"] is False


def test_linear_constraint_degeneracy_is_quadratically_lifted():
    action = seam.action_audit_ledger()
    levels = action["invariance_levels"]
    assert levels["after_bulk_constraints_linear_order"] is True
    assert levels["after_junction_linear_order"] is True
    assert levels["static_fold_linear_order"] is True
    assert levels["static_fold_quadratic_order"] is False
    assert action["first_possible_nonzero_order_on_solution"] == 2
    assert action["result"] == seam.PRIMARY_RESULT


def test_scalar_B1_matcher_and_Z2_action_sectors():
    action = seam.action_audit_ledger()
    assert "not invariant for a general off-shell field" in (
        action["bulk_scalar"]["off_shell"]
    )
    assert action["bulk_scalar"]["static_fold"].startswith("invariant")
    assert action["intrinsic_B1"].startswith("exactly unchanged")
    assert action["metric_matcher"].endswith("unchanged")
    assert action["Z2_factor"] == "preserved"
    assert action["stored_core_or_topological_contact_term"] is None


def test_no_anchoring_term_is_added_to_find_cost():
    action = seam.action_audit_ledger()
    assert action["anchoring_term_added"] is False
    assert seam.GUARDS["anchoring_potential"] is False
    assert seam.GUARDS["anchoring_coefficient"] is False


def test_uniform_core_contact_is_unadopted_identification():
    core = seam.uniform_core_contact_ledger()
    assert core["stored_functional"] is False
    assert core["derived_from_action"] is False
    assert core["follows_from_absence_of_action_dependence"] is False
    assert core["admissible_coefficient_free_identification"] is True
    assert core["status"] == "BHSM identification"
    assert core["adopted"] is False


def test_uniform_contact_does_not_assign_core_metric_or_prove_equivalence():
    core = seam.uniform_core_contact_ledger()
    assert core["conflicts_with_nonspatiotemporal_core"] is False
    assert core["inserted_into_action"] is False
    assert core["metric_assigned_to_core"] is False
    assert core["sufficient_to_derive_T_lambda"] is False
    assert core["action_blindness_equals_physical_equivalence"] is False


def test_observable_invariance_and_changes_are_distinguished():
    observables = seam.observable_ledger()
    assert observables["induced_metric"] == "exactly invariant"
    assert observables["intrinsic_curvature"] == "exactly invariant"
    assert observables["bulk_curvature_invariants"] == "changed generically"
    assert observables["one_sided_extrinsic_curvature"].startswith("changed")
    assert observables["Q_jump"].startswith("changed")
    assert observables["exact_quotient_observable_test_passed"] is False


def test_scalar_sheet_topology_and_orientation_observables():
    observables = seam.observable_ledger()
    for key in (
        "scalar_pullback",
        "scalar_wall_zero_set",
        "zeta",
        "q",
        "tau",
        "scalar_sign_s",
        "topology",
        "orientation",
        "frozen_predictions",
    ):
        assert observables[key] == "exactly invariant"


def test_unavailable_observables_are_not_asserted_invariant():
    observables = seam.observable_ledger()
    assert observables["matching_multiplier_after_elimination"] == (
        "not a physical observable"
    )
    assert observables["bulk_gravitational_charge_change"] == "not evaluated"
    assert observables["stored_core_contact_label"] == "undefined"


def test_interface_and_nonlinear_multiplier_null_are_not_gauge_proof():
    noether = seam.noether_ledger()
    assert "Omega_Sigma=0" in noether["interface_presymplectic"]
    assert "remains null" in noether["nonlinear_extended_ADM_presymplectic"]
    assert noether["candidate_generator_for_multiplier_shift"] == (
        "G_multiplier[lambda]=0"
    )
    assert noether["zero_generator_implies_gauge"] is False


def test_actual_first_class_generator_does_not_move_threading():
    noether = seam.noether_ledger()
    assert "C_mu" in noether["actual_momentum_generator"]
    assert noether["actual_generator_action_on_S"] == "delta_xi S_Sigma=0"
    assert noether["new_Noether_identity"] is False
    assert noether["new_first_class_constraint"] is False
    assert noether["boundary_charge"] is None
    assert noether["result"] == seam.NOETHER_RESULT


def test_exact_classification_is_lifted_linear_null_not_flat_modulus():
    verdict = seam.classification_ledger()
    assert verdict["exact_interface_redundancy"] is False
    assert verdict["global_on_shell_degeneracy"] is False
    assert verdict["physical_flat_modulus"] is False
    assert verdict["accidental_linearized_null"] is True
    assert verdict["domain_label_remains"] is True
    assert verdict["higher_order_lifting"] is True
    assert verdict["first_lifting_order"] == 2
    assert verdict["primary_result"] == seam.PRIMARY_RESULT


def test_no_quotient_or_zero_threading_slice_is_licensed():
    quotient = seam.quotient_ledger()
    assert quotient["quotient_adopted"] is False
    assert quotient["equivalence_relation"] is None
    assert quotient["local_slice"] is None
    assert quotient["residual_group"] is None
    assert quotient["Jacobian"] is None
    assert quotient["S_Sigma_zero_slice_valid"] is False
    assert "arbitrary interface condition" in quotient["S_Sigma_zero_status"]
    assert quotient["result"] == seam.SHORTCUT_RESULT


def test_threading_count_remains_one_and_Green_domain_stays_open():
    ledger = seam.threading_and_fold_ledger()
    assert ledger["unresolved_interface_trace_count_before"] == 1
    assert ledger["unresolved_interface_trace_count_after"] == 1
    assert ledger["Green_operator_domain_ready"] is False
    assert ledger["representative_condition"] is None
    assert ledger["expected_kernel_count"] is None


def test_fold_route_remains_paused_and_q_is_not_promoted():
    ledger = seam.threading_and_fold_ledger()
    assert ledger["fold_route"] == "paused"
    assert ledger["q_as_certified_4D_field"] is False
    assert ledger["uniform_core_contact_required_for_current_verdict"] is False
    assert "insufficient by itself" in (
        ledger["uniform_core_contact_if_adopted"]
    )
    for key in (
        "k_q_E",
        "B_ext_E",
        "B_core_E",
        "m_ext_squared",
        "m_core_squared",
    ):
        assert ledger[key] is None


def test_v6_15_and_fold_data_are_preserved():
    preserved = seam.integrity_ledger()["preserved"]
    assert preserved["v6_15"] == (
        "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE"
    )
    assert preserved["canonical_momentum_S"] == 0
    assert preserved["unresolved_interface_trace_count"] == 1
    assert preserved["q_status"] == "static fold coordinate"
    assert preserved["F0_equals_M4_squared"] == "pi/2"
    assert preserved["K_scalar"] == ">=2>0"
    assert "(4-pi)^2" in preserved["K_Weyl"]


def test_integrity_guards():
    assert all(value is False for value in seam.GUARDS.values())
    for payload in seam.artifact_payloads().values():
        assert all(payload[name] is False for name in seam.GUARDS)


def test_exactly_three_deterministic_artifacts():
    expected = seam.artifact_bytes()
    assert len(expected) == 3
    assert set(expected) == set(seam.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = seam.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
