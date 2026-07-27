from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import scalar_wall_fold_morse_sheet_selection as morse
from bhsm.interface import scalar_wall_puiseux_fold as fold


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_puiseux_coefficients_match_repository_regression():
    data = fold.regression_data()
    assert data["chi_abs"] == pytest.approx(float(morse.CHI_1_DECIMAL), rel=2e-12)
    assert data["nu1_abs"] == pytest.approx(float(morse.NU_1_DECIMAL), rel=2e-12)
    assert data["mu1_over_q5"] == pytest.approx(float(morse.MU_C_DECIMAL), rel=2e-12)
    assert data["cap_value"] == pytest.approx(float(morse.U1_CAP_DECIMAL), rel=2e-12)
    assert data["junction_derivative"] == pytest.approx(
        float(morse.U1_JUNCTION_DERIVATIVE_DECIMAL), rel=2e-12
    )


def test_exact_fold_identity_is_preserved():
    relations = morse.exact_fold_relations()
    assert relations["nu_from_chi"] == sp.Rational(3, 4) * morse.CHI_1**3
    assert relations["cusp_A"] == morse.NU_1 / 12
    assert relations["FH_coefficient"] == sp.Rational(1, 4)


@pytest.mark.parametrize("tau", [-1, 1])
def test_branch_derivatives_are_exact(tau):
    derivatives = morse.puiseux_derivatives(tau)
    assert derivatives["d_mu_dr"] == tau * morse.NU_1
    assert derivatives["d_X_dr"] == tau * morse.CHI_1


def test_invalid_sheet_is_rejected():
    with pytest.raises(ValueError):
        morse.puiseux_derivatives(0)
    with pytest.raises(ValueError):
        morse.reduced_action(0)


def test_branch_tangent_changes_the_action_control():
    ledger = morse.branch_control_ledger()
    assert ledger["action_control"] == "mu=-A5/Z5"
    assert ledger["branch_tangent_parameter_changing"] is True
    assert "nonzero" in ledger["reason"]
    assert ledger["d2_onshell_Gamma_dr2_used_as_physical_Hessian"] is False


def test_four_directions_are_not_conflated():
    rows = morse.direction_classification()
    assert [row["id"] for row in rows] == ["A", "B", "C", "D"]
    assert rows[0]["boundary_condition_changing"] is True
    assert rows[2]["parameter_changing"] is True
    assert rows[3]["parameter_changing"] is False


def test_field_space_uses_only_repository_variables():
    fields = morse.field_constraint_ledger()["raw_vector"]
    assert fields == [
        "delta sigma(t)",
        "delta a(t)",
        "delta N(t)",
        "delta rho_J",
        "delta X",
        "delta mu",
    ]


def test_constraint_and_gauge_quotient_are_explicit():
    ledger = morse.field_constraint_ledger()
    assert ledger["physical_space"] == "T_phys=ker C/im G"
    assert "linearized normal/Hamiltonian constraint" in ledger["constraints"][0]
    assert ledger["gauge_action"]["delta_xi_X"] == 0
    assert ledger["gauge_kernel_inverted"] is False


def test_fixed_and_moving_endpoint_gauges_are_equivalent():
    ledger = morse.field_constraint_ledger()
    assert ledger["fixed_domain_gauge"].startswith("t in [0,1]")
    assert "explicit delta rho_J" in ledger["moving_endpoint_gauge"]
    assert "fixed/moving agreement" in ledger["gauge_equivalence"]


def test_finite_cap_tangent_contains_scalar_warp_lapse_and_X():
    tangent = morse.finite_cap_tangent_ledger()
    assert tangent["scalar_component"] == "s u_1"
    assert "a_0/4" in tangent["a_1"]
    assert tangent["N_1"] == "-chi_1/4"
    assert tangent["delta_X"] == "tau chi_1"


def test_endpoint_conditions_are_preserved():
    trace = morse.finite_cap_tangent_ledger()["endpoint_trace"]
    assert trace["u_1(rho_J)"] == 0
    assert trace["a_1(rho_J)"] == 0
    assert trace["junction_derivative"].startswith("delta a'_J=delta X/2")


def test_finite_cap_tangent_is_not_pure_gauge():
    tangent = morse.finite_cap_tangent_ledger()
    assert tangent["constraint_satisfied"] is True
    assert tangent["normal_diffeomorphism_removed"] is True
    assert "intrinsic R4 curvature" in tangent["non_gauge_witness"]


def test_collective_coordinate_is_amplitude_not_literal_translation():
    tangent = morse.finite_cap_tangent_ledger()
    assert tangent["coordinate"] == "q=r=|epsilon| on each sheet; s records the Z2 scalar sign"
    assert tangent["literal_wall_displacement_b"] is False


def test_scalar_kinetic_contribution_is_exactly_positive():
    kinetic = morse.scalar_kinetic_ledger()
    assert kinetic["critical_formula"].startswith("2 integral")
    assert "k_q^scalar>=2" in kinetic["bound"]
    assert kinetic["scalar_sign"] == "strictly positive"


def test_gravity_constraint_and_boundary_kinetic_terms_are_not_dropped():
    kinetic = morse.scalar_kinetic_ledger()
    assert kinetic["gravity_raw"].startswith("P1 kinetic form")
    assert "Schur complement" in kinetic["constraint_correction"]
    assert "GHY+B1" in kinetic["boundary_contribution"]
    assert "transversality" in kinetic["endpoint_contribution"]


def test_B1_scalar_field_is_not_silently_identified_with_q():
    assert "distinct B1 field" in morse.scalar_kinetic_ledger()["known_zero"]


def test_total_kinetic_norm_is_not_set_to_one():
    kinetic = morse.scalar_kinetic_ledger()
    assert kinetic["total"] == "k_q=k_q^scalar+k_q^grav,red"
    assert kinetic["total_sign"] is None
    assert kinetic["k_q_set_to_one"] is False
    assert kinetic["result"] == morse.KINETIC_RESULT


@pytest.mark.parametrize("tau", [-1, 1])
def test_reduced_action_stationarity_reproduces_branch_equation(tau):
    derivative = morse.reduced_stationarity(tau)
    expected = morse.Q * (
        morse.DELTA_MU - tau * morse.NU_1 * morse.Q
    ) / 2
    assert sp.simplify(derivative - expected) == 0
    assert sp.simplify(
        derivative.subs(morse.branch_substitution(tau))
    ) == 0


def test_Feynman_Hellmann_fixes_unfolding_coefficient():
    ledger = morse.lyapunov_schmidt_ledger()
    assert ledger["critical_FH"] == "partial_mu Gamma_hat=q^2/4+O(q^3)"
    assert ledger["unfolding_coefficient"] == "coefficient of delta_mu q^2 is 1/4"


@pytest.mark.parametrize("tau", [-1, 1])
def test_onshell_cusp_is_exactly_reproduced(tau):
    assert morse.onshell_cusp(tau) == tau * morse.NU_1 * morse.Q**3 / 12


def test_cusp_matches_frozen_A():
    assert morse.onshell_cusp(1) / morse.Q**3 == morse.exact_fold_relations()["cusp_A"]


def test_signed_scalar_symmetry_is_not_violated_by_sheet_cubic():
    ledger = morse.lyapunov_schmidt_ledger()
    assert ledger["amplitude"].startswith("q=r=|epsilon|")
    assert "not an odd term in signed epsilon" in ledger["cubic_source"]


@pytest.mark.parametrize("tau", [-1, 1])
def test_fixed_control_Hessian_is_not_onshell_second_derivative(tau):
    expected = -tau * morse.NU_1 * morse.Q / 2
    assert morse.fixed_control_hessian(tau) == expected
    assert morse.lyapunov_schmidt_ledger()["d2_onshell_dr2_substituted"] is False


def test_reduced_Hessian_signs_are_opposite():
    assert morse.fixed_control_hessian(1).is_negative is None
    assert sp.sign(morse.fixed_control_hessian(1).subs(morse.Q, 1)) == -1
    assert sp.sign(morse.fixed_control_hessian(-1).subs(morse.Q, 1)) == 1


def test_tau_to_X_and_sheet_map():
    mapping = morse.sheet_map_ledger()
    assert ">2" in mapping["tau_plus"]["X"]
    assert "<2" in mapping["tau_minus"]["X"]
    assert mapping["tau_plus"]["BHSM_sheet"].startswith("exterior")
    assert mapping["tau_minus"]["BHSM_sheet"].startswith("core-facing")


def test_sheet_map_is_normal_orientation_invariant():
    mapping = morse.sheet_map_ledger()
    assert "leaves intrinsic X and tau unchanged" in mapping["normal_reversal"]
    assert mapping["orientation_invariant_classifier"] == "sign(X-2)=tau"


def test_rho_reversal_does_not_exchange_sheets():
    assert "does not exchange X>2 with X<2" in morse.sheet_map_ledger()["rho_reversal"]


def test_schur_complement_is_Hermitian_after_gauge_removal():
    h_phys = morse.formal_physical_hessian()
    assert h_phys == h_phys.T.conjugate()


def test_no_inverse_is_taken_on_gauge_kernel():
    h_pp = sp.eye(1)
    h_pc = sp.zeros(1, 1)
    with pytest.raises(ValueError, match="gauge kernels"):
        morse.schur_complement(h_pp, h_pc, sp.zeros(1))


def test_morse_classification_does_not_claim_physical_tachyon():
    ledger = morse.morse_ledger()
    assert ledger["physical_tachyon_certified"] is False
    assert ledger["ghost_certified"] is False
    assert ledger["Morse_index_lower_bound"] is None
    assert "positive total kinetic norm" in ledger["reason_no_minmax_certificate"]


def test_core_rejection_is_not_manufactured():
    ledger = morse.morse_ledger()
    assert ledger["core_negative_mode"] is False
    assert ledger["core_result"] == morse.CORE_RESULT
    assert ledger["result"] == morse.PRIMARY_RESULT


def test_upper_result_is_qualified_not_global():
    ledger = morse.morse_ledger()
    assert ledger["exterior_result"] == morse.EXTERIOR_RESULT
    assert ledger["global_stability"] is False
    assert "not certified" in ledger["upper_stability"]


def test_existing_action_does_not_need_tau_J():
    closure = morse.closure_ledger()
    assert closure["tau_J_needed"] is False
    assert closure["existing_action_sufficient_in_principle"] is True
    assert closure["repository_calculation_complete"] is False


def test_exact_next_calculation_is_not_a_new_primitive():
    closure = morse.closure_ledger()
    assert "k_q^grav,red" in closure["exact_active_construction"]
    report = morse.artifact_payloads()["report"]
    assert report["new_primitive_introduced"] is False
    assert report["hidden_inputs"] == []


def test_no_neutral_construction_is_performed():
    closure = morse.closure_ledger()
    assert closure["neutral_statement"].startswith("static junction mixing remains rejected")
    for payload in morse.artifact_payloads().values():
        assert payload["neutral_transport_used"] is False


def test_integrity_guards():
    for payload in morse.artifact_payloads().values():
        assert payload["tau_J_introduced"] is False
        assert payload["new_primitive_introduced"] is False
        assert payload["fermion_loop_introduced"] is False
        assert payload["measured_inputs_used"] is False
        assert payload["physical_bulk_Dirac_law_introduced"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["lambda_geom_changed"] is False


def test_exactly_six_deterministic_artifacts():
    expected = morse.artifact_bytes()
    assert len(expected) == 6
    assert set(expected) == set(morse.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = morse.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
