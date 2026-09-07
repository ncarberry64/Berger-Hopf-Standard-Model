import hashlib
import json

import numpy as np
import pytest

from bhsm.interface.owner_authorized_encapsulation_interface_action import (
    DERIVATIVE_CLASS,
    EXACT_NEXT_OBJECT,
    INTERFACE_FREEDOM_CLASS,
    LOOP_CLASS,
    UNIQUE_ACTUALIZATION_CLASS,
    DensityCandidate,
    active_differential_from_gradients,
    active_encapsulation_differential,
    adversarial_density_ledger,
    canonical_lagrangian_status,
    claim_boundary,
    classify_density_candidate,
    closure_and_rank_status,
    control_state_contract,
    derivative_order_adjudication,
    euler_lagrange_system,
    first_variation,
    historical_candidate_comparison,
    interface_variable_contract,
    invariant_control_arguments,
    invariant_density_ledger,
    most_general_action_class,
    no_ex_nihilo_noether_structure,
    owner_authorization,
    parameter_freedom_adjudication,
    passive_mismatch_active_differential,
    pullback_isotropy_residual,
    symmetry_contract,
)
from scripts.materialize_owner_authorized_encapsulation_interface_action import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_owner_authorization_is_new_authority_not_old_action_derivation():
    result = owner_authorization()
    assert result["new_primitive"] == "P-A*"
    assert set(result["must_determine"]) == {"iota_enc", "F_B", "L_s", "Delta_enc"}
    assert result["strength_controls"] == ["M_event", "E_s", "Lambda_s"]
    assert not result["independently_fitted_interface_parameters_allowed"]
    assert not result["part_of_previous_13_term_action"]
    assert not result["mathematical_density_selected_by_authorization"]


def test_interface_variables_use_one_abstract_stratified_carrier_and_relations():
    result = interface_variable_contract()
    carrier = result["carrier"]
    assert "one compact oriented stratified carrier" in carrier["abstract_object"]
    assert "dim M^(s)-1" in carrier["dimension"]
    assert carrier["pregeometry_guardrail"] == "no ordinary embedded carrier is asserted inside C_A"
    assert carrier["topology"].startswith("degree, incidence")
    assert result["attachment"]["map"] == "F_B:Sigma_e->Sigma_c"
    assert result["attachment"]["not_external_input"]
    assert "Gamma(Lag" in result["boundary_relation"]["object"]
    assert "not an arbitrary matrix" in result["boundary_relation"]["meaning"]


def test_controls_are_separated_from_variables_and_superselection_data():
    result = control_state_contract()
    assert result["control_state"] == "Xi_enc=(M_event,E_s,Lambda_s)"
    assert "F_B" in result["dynamical_variables"]
    assert "E_s_components" in result["control_environment_data"]
    assert "degree" in result["frozen_superselection_data"]
    assert "independent child-mode coefficients" in result["forbidden_controls"]
    assert "arbitrary harmonic amplitudes or phases" in result["forbidden_controls"]


def test_symmetry_contract_does_not_assume_excess_symmetry():
    result = symmetry_contract()
    assert "G_SM bundle gauge covariance" in result["required"]
    assert "BRST compatibility on gauge-longitudinal and ghost blocks" in result["required"]
    assert "full Diff across incompatible strata" in result["not_assumed"]
    assert "full Spin(4) on every carrier" in result["not_assumed"]
    assert "dimensionless" in result["action_value"]


def test_density_ledger_is_ORD1_complete_and_rejects_unneeded_second_order():
    rows = invariant_density_ledger()
    families = {row["family"]: row for row in rows}
    assert len(rows) == 12
    assert families["attachment_first_jet"]["status"] == "REQUIRED_CLASS"
    assert families["carrier_first_jet"]["derivative_order"] == 1
    assert families["extrinsic_curvature_or_second_jet"]["status"] == "NOT_REQUIRED"
    assert families["owned_GHY_Hayward"]["status"] == "REDUNDANT_NOT_NEW_INTERFACE_STRENGTH"
    assert families["topological_holonomy"]["status"] == "OPTIONAL_DISCRETE_CLASS"


def test_derivative_order_is_ORD1_not_algebraic_or_new_higher_derivative():
    result = derivative_order_adjudication()
    assert result["classification"] == DERIVATIVE_CLASS == "ORD1"
    assert result["minimum"] == 1
    assert "D F_B" in result["why_ORD0_fails"]
    assert "separate higher-derivative physical choice" in result["ORD2_not_required"]


def test_minimal_invariant_controls_do_not_reuse_rho_hold_or_synthetic_energy():
    result = invariant_control_arguments()
    assert result["dimensionful_anchor"] == "ell_kappa=kappa1^(-1/6)"
    assert "R_reset/ell_kappa" in result["continuous_dimensionless"]
    assert "rho_hold before common charges exist" in result["excluded"]
    assert "historical synthetic E_mode/E_impedance numbers" in result["excluded"]
    assert result["rho_E_over_ST"]["recovered_unique_definition"] is False


def test_general_action_class_is_typed_but_has_no_selected_density():
    result = most_general_action_class()
    assert result["extended_action"] == "S_total=S_registered_13_terms+S_enc"
    assert "new fourteenth authority class" in result["registered_action_relation"]
    assert "W_s" in result["schematic"]
    assert "j1 F_B" in result["schematic"]
    assert not result["density_selected"]
    assert not result["zero_parameter_member_selected"]


def test_full_variation_and_each_euler_lagrange_equation_are_exposed():
    variation = first_variation()
    equations = euler_lagrange_system()
    assert all(token in variation["variation"] for token in ("E_Xe", "E_Xc", "E_iota", "E_F", "E_L"))
    assert "partial W/partial Y" in variation["Euler_operator"]
    assert "[T_bulk.n]" in equations["carrier"]["equation"]
    assert "D_F C_s" in equations["attachment"]["equation"]
    assert "T_Ls Lag" in equations["boundary_relation"]["equation"]
    assert equations["event_field_seam"]["equation"].startswith("Pi_e+")
    assert equations["child_field_seam"]["equation"].startswith("Pi_c+")
    assert not any(row["selects_now"] for key, row in equations.items() if isinstance(row, dict) and "selects_now" in row)


def test_Delta_enc_is_derived_formally_and_passive_mismatch_is_zero():
    result = active_encapsulation_differential()
    assert "Delta_enc:=Pi_c+C(F_B)^*Pi_e" in result["definition_from_total_seam_equations"]
    assert "E_qc(S_enc)+C(F_B)^*E_qe(S_enc)" in result["definition_from_total_seam_equations"]
    assert result["amplitude"] is None
    assert not result["value_derived"]

    transport = np.asarray([[1.0, 0.2], [0.0, 1.0], [0.3, -0.1]])
    passive = passive_mismatch_active_differential([0.5, -0.2, 0.7], [0.1, 0.4], transport)
    assert np.linalg.norm(passive) < 1.0e-14
    active = active_differential_from_gradients([0.4, -0.1, 0.2], [0.3, -0.5], transport)
    assert np.linalg.norm(active) > 0.0


def test_no_ex_nihilo_is_a_noether_identity_with_external_control_caveat():
    result = no_ex_nihilo_noether_structure()
    assert result["local_identity"] == "d J_total_xi=0 in the closed extended event+child+interface/environment system"
    assert "only after xi, reference, ensemble, and common domain exist" in result["integrated_energy_form"]
    assert "explicit work/source term" in result["fixed_control_caveat"]
    assert not result["numerical_charge_balance_evaluable"]


def test_canonical_status_is_conditional_and_finite_chart_residual_is_exact():
    result = canonical_lagrangian_status()
    assert result["conditional_status"] == "CANONICAL_GENERATING_FAMILY_CLASS_DERIVED"
    assert not result["actual_isotropy_verified"]
    assert not result["actual_Lagrangian_verified"]
    dq = np.eye(3)
    dpi = np.diag([1.0, 2.0, 3.0])
    assert pullback_isotropy_residual(dq, dpi) == 0.0
    with pytest.raises(ValueError):
        pullback_isotropy_residual(np.eye(2), np.eye(3))


def test_adversarial_candidates_are_all_rejected_for_the_correct_reasons():
    rows = adversarial_density_ledger()
    assert len(rows) == 7
    assert all(not row["admissible_class_member"] for row in rows)
    failures = {failure for row in rows for failure in row["failures"]}
    assert {
        "NOT_EVENT_MODE_CONDITIONED",
        "PASSIVE_MISMATCH_ONLY_GIVES_ZERO_ACTIVE_DIFFERENTIAL",
        "INDEPENDENT_FITTED_INTERFACE_PARAMETERS_FORBIDDEN",
        "INDEPENDENT_CHILD_MODE_COEFFICIENTS_FORBIDDEN",
        "GAUGE_NONINVARIANT",
        "HIGHER_DERIVATIVE_EXTENSION_NOT_REQUIRED_OR_AUTHORIZED",
        "DUPLICATES_OWNED_ACTION_TERM",
    } <= failures

    structurally_admissible = DensityCandidate(
        "unspecified_invariant_W", 1, True, True, True, True, True, True, True
    )
    classified = classify_density_candidate(structurally_admissible)
    assert classified["admissible_class_member"]
    assert not classified["physical_member_selected"]


def test_IF5_historical_candidates_and_no_small_owner_question():
    freedom = parameter_freedom_adjudication()
    history = historical_candidate_comparison()
    assert freedom["classification"] == INTERFACE_FREEDOM_CLASS == "IF5"
    assert freedom["functions_selected"] == 0
    assert freedom["coefficients_fitted"] == 0
    assert len(history) == 6
    assert all(not row["selected"] for row in history)
    assert any(row["candidate"] == "AE4 impedance/core crossing" for row in history)


def test_LOOP3_UA5_rank_and_downstream_firewalls_remain_closed():
    status = closure_and_rank_status()
    claims = claim_boundary()
    assert status["loop"] == LOOP_CLASS == "LOOP3"
    assert status["unique_actualization"] == UNIQUE_ACTUALIZATION_CLASS == "UA5"
    assert status["selected_carrier"] is status["selected_F_B"] is status["selected_L_s"] is None
    assert status["physical_reset_domain"] is None
    assert status["N12_rank_added"] == 0
    assert status["N12_residual_before_time_quotient"] == 67
    assert status["N12_residual_after_time_quotient"] == 66
    assert status["S1"] is status["S2"] is status["S3"] is status["S4"] is None
    assert claims["OWNER_AUTHORIZED_PRIMITIVE_RECORDED"]
    assert not any(value for key, value in claims.items() if key != "OWNER_AUTHORIZED_PRIMITIVE_RECORDED")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_LEVEL_CONSTITUTIVE_ENVELOPMENT_WORK_DENSITY")


def test_materializer_is_valid_and_byte_deterministic():
    first_payload = build_payload()
    second_payload = build_payload()
    assert first_payload["validation_passed"]
    assert all(first_payload["validation"].values())
    assert deterministic_json(first_payload) == deterministic_json(second_payload)
    main()
    first_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first_hash == second_hash
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert stored["classification"]["interface_freedom"] == "IF5"
    assert stored["validation_passed"]
