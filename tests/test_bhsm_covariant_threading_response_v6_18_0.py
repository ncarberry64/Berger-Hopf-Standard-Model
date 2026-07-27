from pathlib import Path
import pytest
import sympy as sp

from bhsm.interface import covariant_threading_response as response

ROOT = Path(__file__).resolve().parents[1]


def test_corrected_resting_principle_selects_only_constant():
    row = response.corrected_resting_principle()
    assert row["C_Sigma"] == 0
    assert row["classification"] == "Adopted BHSM axiom"
    assert row["partial_q_Sbar_imposed_zero"] is False
    assert row["tau_switches_to_zero"] is False
    assert row["time_assigned_to_common_core"] is False


def test_v617_history_is_not_rewritten():
    assert response.corrected_resting_principle()["v6_17_history_rewritten"] is False


def test_harmonic_kernel_spectrum():
    a = sp.symbols("a", positive=True)
    assert response.threading_kernel_eigenvalue(0, a) == 0
    assert response.threading_kernel_eigenvalue(1, a) == -6 / a**4
    assert response.threading_kernel_eigenvalue(2, a) == -16 / a**4
    with pytest.raises(ValueError):
        response.threading_kernel_eigenvalue(-1, a)


@pytest.mark.parametrize("ell", [1, 2, 5])
@pytest.mark.parametrize("tau", [-1, 1])
def test_source_response_equation(ell, tau):
    q, chi, a = sp.symbols("q chi a", positive=True)
    K = response.threading_kernel_eigenvalue(ell, a)
    J = response.source_eigenvalue(ell, tau, q, chi, a)
    S = response.dynamic_response(ell, tau, q, chi)
    assert sp.simplify(K * S + J) == 0


def test_homogeneous_mode_is_integration_constant():
    q = sp.symbols("q")
    assert response.dynamic_response(0, 1, q) == 0
    assert response.kernel_ledger()["ell_0"] == "kernel/integration constant"


def test_sheet_sign_and_scalar_sign():
    q, chi = sp.symbols("q chi", positive=True)
    assert response.dynamic_response(1, 1, q, chi) == -sp.pi * chi * q / 16
    assert response.dynamic_response(1, -1, q, chi) == sp.pi * chi * q / 16
    assert response.source_ledger()["scalar_sign_independent"] is True
    with pytest.raises(ValueError):
        response.dynamic_response(1, 0, q)


def test_action_is_induced_not_fundamental():
    action = response.action_ledger()
    assert action["fundamental_boundary_action"] is False
    assert action["induced_effective_action"] is True
    assert action["new_action_term"] is False
    assert action["result"] == response.PRIMARY_RESULT


def test_exact_inner_product_and_z2_count():
    action = response.action_ledger()
    assert action["inner_product"].startswith("<f,g>_Sigma=integral_B1")
    assert action["interface_count"] == "the common Z2 interface is counted once"
    assert "tau changes the source sign" in action["orientation"]


def test_lambda_is_normalized_to_threading_trace():
    assert response.action_ledger()["normalization"] == (
        "lambda of v6.16 shifts Sbar by lambda, so delta Sbar=lambda"
    )


def test_general_kernel_nonlocal_but_symmetric_background_known():
    action = response.action_ledger()
    assert action["general_Dirichlet_to_Neumann_operator"].startswith("nonlocal")
    kernel = response.kernel_ledger()
    assert kernel["general_order"] == 4
    assert kernel["round_S3_operator"] == "Khat_Sigma=(2/a^2)D_spatial^2"


def test_signature_claims_are_conservative():
    kernel = response.kernel_ledger()
    assert kernel["Lorentzian_action_sign"].startswith("negative")
    assert kernel["Euclidean_Hessian_sign"].startswith("not certified")
    assert kernel["canonical_Hamiltonian_sign"].startswith("not certified")
    assert kernel["stability"] == "constraint-indefinite; not a ghost theorem"


def test_no_unsupported_stiffness():
    assert response.kernel_ledger()["unsupported_stiffness_added"] is False
    assert response.GUARDS["unsupported_stiffness"] is False


def test_source_is_derived_relative_to_same_hessian():
    source = response.source_ledger()
    assert source["bulk_source"].startswith("J_shift(t)=")
    assert source["B1_response"] == "partial_q Sbar_Sigma=-tau pi chi_1/16"
    assert source["coefficient_inserted_by_hand"] is False


def test_source_free_rest_needs_no_threshold():
    source = response.source_ledger()
    assert source["source_free_condition"].startswith("Pi_perp q=0")
    audit = response.activation_audit()
    assert audit["selected_model"] == "A: no explicit threshold"
    assert audit["E_crit"] is None
    assert audit["selected_invariant"] is None
    assert audit["result"] == response.THRESHOLD_RESULT


def test_activation_candidates_are_all_audited():
    audit = response.activation_audit()
    required = {
        "Delta_X=X-2", "lambda_fold_min", "sigma_squared",
        "normal_sigma_squared", "nabla_sigma_squared", "U5_difference",
        "Dq_squared", "fold_energy_density", "normal_stress",
        "intrinsic_curvature",
    }
    assert required.issubset(audit)
    assert audit["Dq_squared"]["sign_definite"] is False
    assert audit["fold_energy_density"]["new_observer"] is True
    assert audit["normal_stress"]["dimension"] == "pressure/stress"


def test_no_hard_switch_or_new_scale():
    audit = response.activation_audit()
    assert audit["hard_Heaviside"] is False
    assert audit["new_scale"] is False
    assert response.GUARDS["fitted_threshold"] is False
    assert response.GUARDS["arbitrary_switch"] is False


def test_dynamic_domain_replaces_hard_zero():
    domain = response.response_domain_ledger()
    assert domain["dynamic_boundary_equation_replaces_hard_zero"] is True
    assert domain["hard_zero_also_imposed_during_transition"] is False
    assert domain["admissible_dynamic_domain_nonempty"] is True
    assert domain["result"] == response.DOMAIN_RESULT


def test_domain_gauge_z2_junction_and_Ward_consistency():
    domain = response.response_domain_ledger()
    assert domain["gauge_invariant"] is True
    assert domain["Z2_compatible"] is True
    assert domain["pole_regular"] is True
    assert domain["duplicate_junction_equation"] is False
    assert domain["duplicate_Ward_identity"] is False
    assert domain["fixed_composite_same_trace"] is True


def test_trace_count_closes():
    domain = response.response_domain_ledger()
    assert domain["unresolved_trace_before_resting_selection"] == 1
    assert domain["unresolved_trace_after_resting_selection"] == 0


def test_rest_transition_rest_is_constraint_comparison_not_relaxation():
    history = response.rest_transition_rest_ledger()
    assert history["initial"] == "J_Sigma=0, C_Sigma=0, Sbar=0"
    assert "K_Sigma^-1" in history["transition"]
    assert history["retarded_relaxation_derived"] is False
    assert history["dissipation_derived"] is False
    assert history["white_hole_interpretation"] == "conditional BHSM identification"
    assert history["time_assigned_to_core"] is False


def test_full_constraint_vector_and_exact_remaining_obstruction():
    ledger = response.constraint_and_kinetic_ledger()
    assert ledger["full_Y"] == ["A", "B", "psi", "E", "delta sigma", "zeta"]
    assert ledger["full_L_C"] is None
    assert "finite-q ADM Hessian" in ledger["reason_full_operator_open"]
    assert ledger["source_compatible"] is True
    assert ledger["full_Green_operator"] is None


def test_no_generic_pseudoinverse():
    ledger = response.constraint_and_kinetic_ledger()
    assert "no generic pseudoinverse" in ledger["threading_projected_inverse"]
    assert response.GUARDS["generic_pseudoinverse"] is False


def test_kinetic_result_remains_open_without_fake_number():
    ledger = response.constraint_and_kinetic_ledger()
    assert ledger["K_shift_endpoint_red"] is None
    assert ledger["K_scalar"] == ">=2>0"
    assert ledger["K_Weyl"] == pytest.approx(1.220620174933802)
    assert ledger["k_q_E"] is None
    assert ledger["kinetic_result"] == response.KINETIC_RESULT
    assert ledger["physical_mass"] is None


def test_exact_response_threshold_domain_verdicts():
    verdict = response.verdict_ledger()
    assert verdict["response_theorem"] == response.PRIMARY_RESULT
    assert verdict["threshold_theorem"] == response.THRESHOLD_RESULT
    assert verdict["domain_theorem"] == response.DOMAIN_RESULT
    assert verdict["new_fundamental_action_required"] is False
    assert verdict["new_threshold_scale_required"] is False


def test_model_map_has_required_sectors():
    assert len(response.model_map()) == 13
    assert "threading response" in response.model_map()
    assert "fold kinetic sector" in response.model_map()


def test_integrity_guards():
    assert all(value is False for value in response.GUARDS.values())
    for payload in response.artifact_payloads().values():
        assert all(payload[key] is False for key in response.GUARDS)


def test_four_deterministic_artifacts():
    expected = response.artifact_bytes()
    assert len(expected) == 4
    assert set(expected) == set(response.ARTIFACT_FILES.values())
    assert all(blob.endswith(b"\n") for blob in expected.values())


def test_materialized_artifacts_match():
    for filename, expected in response.artifact_bytes().items():
        assert (ROOT / "artifacts" / filename).read_bytes() == expected
