from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_support_vs_dynamical_embedding as support


def test_baseline_and_predecessor_are_exact():
    assert support.SOURCE_MAIN_SHA == (
        "4a59a2a3d1dc7e2d21fbc5f0d9e0f69aac28b34e"
    )
    assert support.V624_SCIENTIFIC_SHA.startswith("94879c94")
    assert support.V624_REPRODUCIBILITY_SHA.startswith("16e75be5")


def test_fixed_manifold_and_existing_fields_are_declared():
    domain = support.fixed_manifold_ledger()["domain_F"]
    assert domain["manifold"] == "M5=[0,1]_t×M4 on each cap"
    assert domain["B1"] == "{t=1}"
    assert domain["physical_embedding_variation"] == 0
    assert {"N(t,x)", "N_mu(t,x)", "gamma_mu_nu(t,x)"} <= set(
        domain["fields"]
    )


def test_homogeneous_fold_profiles_and_endpoint():
    assert support.a0(0) == 0
    assert sp.simplify(support.a0(1) - 1) == 0
    assert sp.simplify(support.a1(1)) == 0
    assert support.lapse0() == sp.pi / 4
    assert support.length1() == -support.CHI_1 / 4
    profiles = support.fixed_manifold_ledger()["homogeneous_profiles"]
    assert profiles["delta_X"] == "tau chi_1"
    assert profiles["junction_tangent"].startswith("delta a'_J=delta X/2")


def test_proper_radius_to_fixed_t_coordinate_map():
    rho = support.proper_radius_map()
    assert sp.simplify(rho.subs(support.T, 0)) == 0
    assert sp.simplify(
        rho.subs({support.T: 1, support.Q: 0}) - sp.pi / 4
    ) == 0
    assert sp.simplify(
        sp.diff(rho, support.Q).subs(support.Q, 0)
        - support.T * support.TAU * support.length1()
    ) == 0


def test_induced_shift_matches_v618_exactly():
    assert support.shift_match_residual() == 0
    assert support.linear_shift_profile() == (
        -support.TAU * sp.pi * support.CHI_1 * support.T / 16
    )


def test_induced_metric_rank_one_term():
    coefficient = support.induced_metric_rank_one_coefficient().subs(
        support.Q, 0
    )
    assert sp.simplify(
        coefficient
        - support.T**2 * support.TAU**2 * support.CHI_1**2 / 16
    ) == 0


def test_fixed_lapse_reconstructs_homogeneous_lapse():
    lapse_squared = support.fixed_lapse_squared(0)
    assert sp.simplify(
        lapse_squared - support.cap_length() ** 2
    ) == 0
    derivative = sp.diff(
        support.fixed_lapse_squared(), support.DQ2
    ).subs(support.Q, 0)
    assert derivative != 0


def test_extrinsic_curvature_contains_first_unresolved_hessian():
    assert support.fold_extrinsic_hessian_coefficient() == (
        support.TAU * support.CHI_1 * support.T / 4
    )
    placement = support.fixed_manifold_ledger()["derivative_placement"]
    assert "D_muD_nu q" in placement["O(D2q)"]


def test_complete_quadratic_pullback_does_not_fake_second_responses():
    second = support.fixed_manifold_ledger()["second_response"]
    assert second["ell2"] == "not stored"
    assert second["a2_N2"] == "not stored"
    assert second["needed_for_linear_O(D2q)_support_test"] is False


def test_endpoint_threading_invariant_is_gauge_invariant():
    assert support.threading_gauge_residual() == 0
    gauge = support.gauge_ledger()
    assert gauge["symbolic_invariance_residual"] == "0"


def test_fixed_and_moving_coordinate_pullbacks_are_equivalent():
    moving = support.gauge_ledger()["moving_to_fixed"]
    assert moving["fixed_graph"] == "zeta=0"
    assert moving["pullback_data_equal"] is True
    assert "pi chi_1/16" in moving["generated_B"]


def test_radial_and_m4_scalar_gauge_map_has_full_rank():
    fp = support.faddeev_popov_matrix()
    assert fp == sp.diag(1, -1)
    assert fp.det() == -1
    assert fp.rank() == 2
    count = support.gauge_ledger()["support_count"]
    assert count["M4_scalar_gauge_functions"] == 1
    assert count["M4_scalar_gauge_conditions"] == 1


def test_pole_and_boundary_gauge_conditions_are_compatible():
    conditions = support.gauge_ledger()["pole_and_B1"]
    assert conditions["pole"] == "xi^t(0,x)=0"
    assert conditions["compatible_interpolation"] == "xi^t=-t zeta is smooth"
    assert conditions["residual_normal_gauge"].endswith("after zeta=0")


def test_fixed_support_degree_of_freedom_count_closes_kinematically():
    count = support.gauge_ledger()["support_count"]
    assert count["coordinate_graph_variables_before_fix"] == 1
    assert count["normal_gauge_values_used"] == 1
    assert count["physical_embedding_scalars_added"] == 0
    assert count["unpaired_support_variable"] is None
    assert count["support_specific_count_closes"] is True


def test_ghy_and_matcher_checks_are_retained_without_full_operator():
    checks = support.fixed_support_compatibility_ledger()["known_checks"]
    assert "cancel capwise" in checks["GHY"]
    assert checks["matcher"] == "exact algebraic elimination"
    assert checks["principal_A_psi"].startswith("(6kappa_1/a0^2)")
    assert checks["radial_measure"] == "pi sin^4(pi t/4)dt"


def test_scalar_junction_projection_and_dependency_ranks():
    boundary = support.boundary_equation_ledger()
    projections = boundary["scalar_projections_on_closed_FRW_foliation"]
    assert set(projections) == {
        "Hamiltonian",
        "momentum",
        "spatial_trace",
        "traceless_longitudinal",
    }
    dependency = boundary["dependency"]
    assert dependency["scalar_projection_count"] == 4
    assert dependency["dependency_rank"] == 2
    assert dependency["independent_rank"] == 2
    assert dependency["double_counted"] is False


def test_matcher_equations_close_algebraically():
    matcher = support.boundary_equation_ledger()["matcher"]
    assert matcher["scalar_matcher_components"] == 2
    assert matcher["multiplier_eliminated"] is True
    assert matcher["propagating_multiplier"] is False
    assert matcher["algebraic_closure"] is True


def test_normal_residual_has_primary_action_level_definition():
    residual = support.normal_residual_ledger()
    assert residual["primary_definition"].startswith(
        "R_perp[q]=(sqrt|h|)^-1"
    )
    assert len(residual["action_origin"]) == 5
    assert set(residual["equivalent_routes"]) == {
        "normal_system",
        "Noether",
        "shape",
    }
    assert residual["covariance"] == "scalar on the common B1"


def test_noether_identity_does_not_manufacture_shape_equation():
    audit = support.normal_residual_ledger()["Noether_Bianchi"]
    assert audit["normal_boundary_diffeomorphism_is_Domain_F_gauge"] is False
    assert "does not set R_perp to zero" in audit["identity_role"]
    assert audit["independence_decided"] is False


def test_residual_is_gauge_and_affine_bookkeeping_invariant():
    gauge = support.normal_residual_ledger()["gauge"]
    assert gauge["built_from_covariant_equations"] is True
    assert gauge["transformation"] == "R_perp -> R_perp"
    assert gauge["fixed_moving_coordinate_independent"] is True
    assert gauge["affine_bookkeeping_residual"] == "0"
    assert support.affine_schur_residual() == 0


def test_z2_residual_parity_and_sheet_sign_are_recorded():
    parity = support.normal_residual_ledger()["Z2"]
    assert parity["outward_cap_Hamiltonian_terms"] == "orientation even"
    assert parity["cap_exchange"] == "R_perp is even"
    assert "source sign" in parity["tau"]
    assert "sigma0=0" in parity["scalar_sign_s"]


def test_first_unresolved_residual_order_is_d2q():
    orders = support.normal_residual_ledger()["local_orders"]
    assert orders["first_unresolved_order"] == "O(D2q)"
    assert "D_muD_nu q" in orders["O(D2q)"]
    assert support.normal_residual_ledger()["homogeneous_order"]["O(q)"].startswith(
        "zero"
    )


def test_time_dependent_homogeneous_threading_is_exact_blocker():
    residual = support.normal_residual_ledger()
    assert residual["explicit_result"] is None
    assert residual["proved_zero"] is False
    assert residual["proved_nonzero"] is False
    assert "time-dependent spatially homogeneous" in residual["missing_object"]
    assert residual["result"] == support.RESIDUAL_RESULT


def test_fixed_support_is_representable_but_not_declared_compatible():
    fixed = support.fixed_support_compatibility_ledger()
    assert fixed["localization_map_exists"] is True
    assert fixed["induced_shift_uses_existing_field"] is True
    assert fixed["shift_matches_v6_18_spatial_response"] is True
    assert fixed["closure"]["all_success_criteria_met"] is False
    assert fixed["fixed_support_success"] is False
    assert fixed["failure_proved"] is False


def test_dynamic_domain_path_is_disabled_until_necessity_is_proved():
    dynamic = support.embedding_domain_ledger()
    assert dynamic["reached"] is False
    assert dynamic["necessity_proved"] is False
    assert dynamic["Z2_glue_rule"] is None
    assert dynamic["existing_action_differentiability"] is None
    assert dynamic["new_corner_required"] is None
    assert dynamic["embedding_equation"] is None
    assert dynamic["dynamic_code_path_enabled"] is False


def test_exactly_one_blocked_primary_domain_result_is_emitted():
    decision = support.decision_ledger()
    assert decision["selected_domain"] is None
    assert decision["rejected_alternative"] is None
    assert decision["primary_result"] == support.PRIMARY_RESULT
    assert decision["one_primary_support_result"] is True
    assert "BLOCKED_BY_UNDERIVED_TIME_DEPENDENT" in support.PRIMARY_RESULT


def test_neither_success_nor_dynamic_necessity_is_emitted():
    assert support.GUARDS["fixed_support_success_emitted"] is False
    assert support.GUARDS["dynamical_embedding_necessity_emitted"] is False
    serialized = json.dumps(support.artifact_payloads(), sort_keys=True)
    assert "BHSM_FOLD_LOCALIZATION_COMPATIBLE_WITH_FIXED_B1_SUPPORT" not in serialized
    assert (
        "BHSM_DYNAMICAL_B1_EMBEDDING_REQUIRED_BY_LOCAL_FOLD_RESIDUAL"
        not in serialized
    )


def test_operator_schur_and_kinetic_stay_blocked():
    decision = support.decision_ledger()
    assert decision["operator"]["reopened"] is False
    assert decision["Schur"]["inverse_constructed"] is False
    assert decision["Schur"]["K_grav_constraint_J"] is None
    assert decision["Schur"]["k_q_E"] is None
    assert decision["kinetic"]["sign"] is None
    assert decision["kinetic"]["ghost"] is None
    assert decision["kinetic"]["stability"] is None


def test_scientific_integrity_firewall():
    assert all(value is False for value in support.GUARDS.values())
    assert support.GUARDS["new_corner_term_introduced"] is False
    assert support.GUARDS["new_action_introduced"] is False
    assert support.GUARDS["local_X_field_invented"] is False
    assert support.GUARDS["scalar_curvature_inverse_revived"] is False
    assert support.GUARDS["chat_only_candidate_imported"] is False


def test_frozen_prediction_hashes_are_unchanged():
    expected = {
        "frozen_predictions.md": (
            "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
        ),
        "frozen_predictions.json": (
            "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
        ),
    }
    for filename, digest in expected.items():
        payload = (ROOT / "docs" / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == digest


def test_deterministic_artifact_checkout_policy_is_unchanged():
    attributes = (ROOT / ".gitattributes").read_text(
        encoding="utf-8"
    ).splitlines()
    general = "artifacts/*.json text eol=lf"
    nested = "artifacts/**/*.json text eol=lf"
    exception = "artifacts/CKM_no_fit_operator_output_v1.json text eol=crlf"
    assert general in attributes
    assert nested in attributes
    assert exception in attributes
    assert attributes.index(general) < attributes.index(exception)
    assert attributes.index(nested) < attributes.index(exception)


def test_artifact_payloads_have_required_sections():
    payloads = support.artifact_payloads()
    assert set(payloads) == set(support.ARTIFACT_FILES)
    assert {"fixed_manifold", "gauge"} <= set(payloads["localization"])
    assert {"normal_support_residual", "boundary_equations"} <= set(
        payloads["residual"]
    )
    assert "compatibility" in payloads["fixed"]
    assert "embedding_domain" in payloads["embedding"]
    assert "decision" in payloads["decision"]


def test_artifacts_are_strict_json_and_match_deterministic_lf_bytes():
    expected = support.artifact_bytes()
    assert len(expected) == 5
    for filename, content in expected.items():
        path = ROOT / "artifacts" / filename
        assert path.read_bytes() == content
        decoded = content.decode("utf-8")
        assert decoded.endswith("\n")
        assert "\r" not in decoded
        assert json.loads(decoded)
