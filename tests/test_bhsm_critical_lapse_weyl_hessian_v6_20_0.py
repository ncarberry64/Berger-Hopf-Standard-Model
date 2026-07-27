from pathlib import Path

import sympy as sp

from bhsm.interface import critical_lapse_weyl_hessian as hessian


ROOT = Path(__file__).resolve().parents[1]


def test_exactly_one_primary_theorem():
    assert hessian.PRIMARY_RESULT == (
        "BHSM_CRITICAL_LAPSE_WEYL_DOMAIN_IS_UNDERDETERMINED"
    )


def test_predecessor_results_are_preserved_exactly():
    assert hessian.PRESERVED_RESULTS == [
        "BHSM_INDUCED_THREADING_ACTION_REPRODUCES_CONSTRAINT_RESPONSE",
        "BHSM_FOLD_SOURCE_VANISHING_REPLACES_EXPLICIT_ENERGY_THRESHOLD",
        "BHSM_THREADING_RESPONSE_ACTION_RESTORES_NONEMPTY_FOLD_DOMAIN",
        "BHSM_FOLD_KINETIC_REQUIRES_ONE_MISSING_ACTION_BLOCK",
    ]


def test_action_provenance_has_every_frozen_sector_and_no_new_coefficient():
    ledger = hessian.action_provenance_ledger()
    normalization = ledger["normalization"]
    assert set(normalization) == {
        "representative", "P1", "GHY", "B1", "matcher", "scalar", "cap_count"
    }
    assert normalization["cap_count"].startswith("two reflected")
    assert ledger["new_coefficient_used"] is False
    assert len(ledger["source_locations"]) == 9


def test_determinant_and_inverse_metric_expansions():
    eps, psi = hessian.EPSILON, hessian.PSI
    assert hessian.determinant_factor_expansion() == (
        1 + 4 * eps * psi + 4 * eps**2 * psi**2
    )
    assert hessian.inverse_metric_factor_expansion() == (
        1 - 2 * eps * psi + 4 * eps**2 * psi**2
    )


def test_critical_background_identities_vanish_exactly():
    assert all(
        sp.simplify(value) == 0
        for value in hessian.background_identity_residuals().values()
    )


def test_action_measure_is_derived_not_assumed():
    assert sp.simplify(
        hessian.radial_weight()
        - hessian.lapse0() * hessian.a0() ** 4
    ) == 0
    assert hessian.expansion_ledger()["radial_measure"] == (
        "pi*sin(pi*t/4)**4"
    )


def test_ansatz_gauge_and_threading_order_are_explicit():
    ledger = hessian.expansion_ledger()
    assert ledger["ansatz"].startswith("N=N0(1+A)")
    assert ledger["fixed_support"] == "zeta=0"
    assert ledger["gauge_order"].endswith("choose E=0")
    assert "C_Sigma=0" in ledger["threading"]


def test_eh_ghy_b1_matcher_scalar_decomposition():
    ledger = hessian.expansion_ledger()
    assert ledger["bulk_principal_density"].startswith("6*kappa_1")
    assert ledger["GHY"].startswith("normal derivatives")
    assert ledger["B1_endpoint"] == "6 C_partial (D psi_J)^2"
    assert ledger["matcher"].startswith("algebraic")
    assert ledger["scalar_direct"].endswith(">=2")


def test_bulk_hessian_components_are_exact():
    a = hessian.a0()
    assert hessian.H_AA_crit() == 0
    assert sp.simplify(hessian.C_H_crit() - 6 * hessian.KAPPA_1 / a**2) == 0
    assert hessian.C_H_crit_dagger() == hessian.C_H_crit()
    assert sp.simplify(
        hessian.H_psipsi_crit() - 12 * hessian.KAPPA_1 / a**2
    ) == 0


def test_saddle_matrix_and_nonzero_determinant():
    matrix = hessian.L_Apsi_crit()
    assert matrix.shape == (2, 2)
    assert matrix[0, 0] == 0
    assert matrix[0, 1] == matrix[1, 0]
    assert sp.simplify(matrix.det() + hessian.C_H_crit() ** 2) == 0


def test_B1_endpoint_hessian_and_cap_count():
    assert hessian.B1_endpoint_hessian() == 12 * hessian.C_PARTIAL
    assert (
        hessian.action_provenance_ledger()["normalization"]["cap_count"]
        == "two reflected bulk caps; one common B1"
    )


def test_formal_adjoint_and_green_form_are_recorded():
    ledger = hessian.operator_ledger()
    assert ledger["formal_adjoint"].startswith("L_bulk^dagger=L_bulk")
    assert ledger["bulk_Green_form"].startswith("0 ")
    assert ledger["B1_antisymmetric_Green_form"].endswith("=0")
    assert ledger["order_in_t_bulk_principal"] == 0


def test_momentum_threading_response_is_reproduced():
    t, tau, chi = sp.symbols("t tau chi", real=True)
    assert hessian.threading_profile(t, tau, chi) == -tau * sp.pi * chi * t / 16
    reduction = hessian.domain_and_reduction_ledger()
    assert reduction["momentum_constraint_reproduced"] is True
    assert reduction["threading_unresolved_trace_count"] == 0


def test_partial_mixed_sources_are_action_derived_but_not_promoted_to_full_J():
    assert hessian.J_A_threading() != 0
    assert "partial_t" in hessian.J_psi_threading_operator()
    ledger = hessian.domain_and_reduction_ledger()
    assert ledger["J_rad_complete"] is False
    assert ledger["Hamiltonian_constraint_reproduced"].startswith("principal")
    assert ledger["Weyl_equation_reproduced"].endswith("missing")


def test_missing_object_is_one_precise_tensor_operator():
    missing = hessian.missing_metric_tangent_ledger()
    assert missing["name"] == "covariant X-metric pullback tangent T_X"
    assert "delta hbar_mu_nu" in missing["formula"]
    assert missing["tensor_operator_type"].startswith("symmetric-2-tensor-valued")
    assert missing["coefficient_dimensions"].startswith("L^2")
    assert missing["new_action_required"] is False


def test_missing_object_has_action_boundary_role_and_exact_entry_points():
    missing = hessian.missing_metric_tangent_ledger()
    assert missing["action_sectors"] == (
        "P1 R4 + intrinsic B1 R4 + exact metric matcher"
    )
    assert "independent scalar B1 junction" in missing["boundary_domain_role"]
    assert len(missing["exact_repository_entry_points"]) == 5


def test_domain_kernel_adjoint_and_compatibility_are_not_fabricated():
    ledger = hessian.domain_and_reduction_ledger()
    assert ledger["full_operator_order"] is None
    assert ledger["domain_condition_count"] is None
    assert ledger["B1_conditions"] is None
    assert ledger["kernel_dimension"] is None
    assert ledger["adjoint_kernel_dimension"] is None
    assert ledger["source_compatibility"] is None
    assert ledger["Fredholm_status"] is None


def test_stop_rule_prevents_schur_or_numerical_pseudoinverse():
    ledger = hessian.domain_and_reduction_ledger()
    assert ledger["earliest_obstruction"] == "domain/source completion requires T_X"
    assert ledger["analytic_elimination_launched"] is False
    assert ledger["numerical_solve_launched"] is False
    assert ledger["generic_pseudoinverse_used"] is False
    assert "not defined" in ledger["Schur_complement"]


def test_kinetic_verdict_preserves_known_terms_without_fake_sign():
    verdict = hessian.kinetic_verdict_ledger()
    assert verdict["K_scalar"].endswith(">=2>0")
    assert verdict["K_Weyl_numeric"] == 1.220620174933802
    assert verdict["K_shift_endpoint_red"] is None
    assert verdict["k_q_E"] is None
    assert verdict["uncertainty"] is None
    assert verdict["sign"] is None
    assert verdict["physical_mass"] is None


def test_sheet_and_scalar_sign_are_not_overclaimed():
    verdict = hessian.kinetic_verdict_ledger()
    assert verdict["sheet_dependence"] is None
    assert verdict["scalar_sign_dependence"].endswith("independent")


def test_integrity_guards():
    assert all(value is False for value in hessian.GUARDS.values())
    for payload in hessian.artifact_payloads().values():
        assert all(payload[key] is False for key in hessian.GUARDS)


def test_exactly_two_deterministic_artifacts():
    blobs = hessian.artifact_bytes()
    assert set(blobs) == set(hessian.ARTIFACT_FILES.values())
    assert len(blobs) == 2
    assert all(blob.endswith(b"\n") for blob in blobs.values())


def test_materialized_artifacts_match():
    for filename, expected in hessian.artifact_bytes().items():
        assert (ROOT / "artifacts" / filename).read_bytes() == expected
