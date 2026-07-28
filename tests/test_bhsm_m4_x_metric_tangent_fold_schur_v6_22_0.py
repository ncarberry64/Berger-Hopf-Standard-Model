import hashlib
import json
import subprocess
from pathlib import Path

import sympy as sp

from bhsm.interface import m4_x_metric_tangent_fold_schur as tangent


ROOT = Path(__file__).resolve().parents[1]


def test_exact_obstruction_verdicts():
    assert tangent.PRIMARY_RESULT == (
        "BHSM_M4_X_METRIC_TANGENT_BLOCKED_BY_"
        "X_TO_R4_NORMALIZATION_CONFLICT"
    )
    assert tangent.SCHUR_RESULT == (
        "BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_"
        "X_TO_R4_NORMALIZATION_CONFLICT"
    )
    assert tangent.KINETIC_RESULT == (
        "BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_"
        "X_TO_R4_NORMALIZATION_CONFLICT"
    )


def test_X_definition_is_homogeneous_not_a_stored_local_field():
    questions = tangent.definition_ledger()["questions"]
    assert questions["X_is_local_scalar_field"] is False
    assert questions["X_is_FRW_H2_plus_a_minus2"] is True
    assert questions["X_is_homogeneous_family_parameter"] is True
    assert questions["X_is_on_shell_branch_coordinate"] is True
    assert questions["hbar_mu_nu_X_declared"] is False


def test_one_critical_X_has_two_distinct_stored_M4_branches():
    ledger = tangent.definition_ledger()
    assert ledger["questions"]["one_X_has_multiple_stored_M4_branches"]
    assert set(ledger["branch_inventory"]) == {
        "maximally_symmetric_dS4",
        "critical_static_RxS3",
    }
    assert "distinct metrics" in ledger["critical_degeneracy"]


def test_exact_FRW_R4_identity_and_branch_derivatives():
    assert tangent.frw_scalar_curvature() == 6 * (tangent.A + tangent.X)
    curvatures = tangent.branch_scalar_curvatures()
    assert curvatures["maximally_symmetric_dS4"] == 12 * tangent.X
    assert curvatures["critical_static_RxS3"] == 6 * tangent.X
    assert tangent.branch_dR4_dX() == {
        "maximally_symmetric_dS4": 12,
        "critical_static_RxS3": 6,
    }


def test_v620_target_conflicts_with_frozen_action_normalization():
    conflict = tangent.normalization_conflict_ledger()
    assert conflict["action_convention"] == "Ric_mu_nu(h)=3X h_mu_nu"
    assert conflict["coefficient_expected"] == 12
    assert conflict["coefficient_stored_in_target"] == 1
    assert conflict["conflict_residual_maximally_symmetric"] == 11
    assert conflict["normalization_resolved"] is False
    assert conflict["earliest_stop"] == tangent.PRIMARY_RESULT


def test_DR_h_symbolic_identity_uses_covariant_metric_variation():
    divdiv, boxtrace, rick = sp.symbols("divdiv boxtrace Ric_k")
    assert tangent.frechet_scalar_curvature(divdiv, boxtrace, rick) == (
        divdiv - boxtrace - rick
    )
    ledger = tangent.metric_tangent_ledger()
    assert ledger["variation_variable"] == "k_mu_nu=delta h_mu_nu"
    assert ledger["signature"] == "Lorentzian M4 (-,+,+,+)"


def test_conformal_special_case_matches_direct_exact_variation():
    expected = -6 * tangent.BOX_PHI - 2 * tangent.R4 * tangent.PHI
    assert tangent.conformal_frechet_scalar_curvature() == expected
    assert tangent.conformal_exact_linear_coefficient() == expected


def test_pure_diffeomorphism_case_is_lie_derivative_of_R4():
    lie_R = sp.symbols("Lie_xi_R4")
    assert tangent.pure_diffeomorphism_curvature_variation(lie_R) == lie_R
    assert tangent.pure_diffeomorphism_curvature_variation(sp.Integer(0)) == 0
    assert "L_xi R4" in tangent.metric_tangent_ledger()[
        "diffeomorphism_check"
    ]


def test_homogeneous_family_check_fails_before_any_inverse():
    check = tangent.metric_tangent_ledger()["homogeneous_check"]
    assert check == {
        "maximally_symmetric_dR4_dX": 12,
        "critical_static_dR4_dX": 6,
        "v6_20_target_dR4_dX": 1,
        "passed": False,
    }
    assert tangent.metric_tangent_ledger()["inverse_constructed"] is False


def test_gauge_and_TT_kernel_are_not_silently_removed():
    ledger = tangent.metric_tangent_ledger()
    assert ledger["gauge_quotient"] is None
    assert ledger["kernel_dimension"] is None
    assert ledger["adjoint_kernel_dimension"] is None
    assert ledger["TT_source_audit"]["action_source_projection_zero_proved"] is False
    assert ledger["TT_source_audit"]["unsourced_TT_freedom_removed"] is False


def test_formal_adjoint_and_green_current_are_recorded_but_domain_is_open():
    adjoint = tangent.formal_adjoint_ledger()
    assert "nabla_mu nabla_nu f" in adjoint["operator"]
    assert "n_mu[" in adjoint["green_current"]
    assert adjoint["flux_status"].startswith("not evaluable")
    assert tangent.metric_tangent_ledger()["domain"] is None


def test_no_source_orthogonality_or_boundary_domain_is_manufactured():
    ledger = tangent.source_domain_ledger()
    for key in (
        "P1_tangent_source",
        "B1_tangent_source",
        "matcher_tangent_source",
        "endpoint_conditions",
        "formal_adjoint_domain",
        "source_orthogonality",
        "source_compatibility",
    ):
        assert ledger[key] is None
    assert ledger["GHY_tangent_cancellation"].startswith("historical")


def test_threading_result_is_preserved_exactly():
    threading = tangent.source_domain_ledger()["preserved_reductions"]
    assert threading["threading"].startswith(
        "Pi_perp S_Sigma=-tau(pi chi_1/16)Pi_perp q"
    )
    assert threading["threading_domain_nonempty"] is True
    assert threading["threading_unresolved_trace_count"] == 0


def test_no_action_insertion_schur_or_downstream_number_is_emitted():
    source = tangent.source_domain_ledger()
    assert source["complete_operator"] is None
    assert source["Schur_inverse"] is None
    assert source["Schur_complement"] is None
    assert source["verdict"] == tangent.SCHUR_RESULT
    kinetic = tangent.kinetic_ledger()
    assert kinetic["K_grav_constraint_J"] is None
    assert kinetic["k_q_E"] is None
    assert kinetic["numerical_method"] is None
    assert kinetic["numerical_uncertainty"] is None
    assert kinetic["sign"] is None


def test_two_cap_common_B1_measure_and_known_K_terms_are_preserved():
    kinetic = tangent.kinetic_ledger()
    assert kinetic["two_cap_multiplicity"] == 2
    assert kinetic["common_B1_multiplicity"] == 1
    assert kinetic["radial_measure"] == "pi sin^4(pi t/4) dt"
    assert kinetic["K_scalar"].endswith(">=2>0")
    assert kinetic["K_Weyl"] == "3 chi_1^2(4-pi)^2/(16 pi)"


def test_no_double_counting_claim_is_made_without_the_tangent():
    audit = tangent.source_domain_ledger()["double_counting_audit"]
    assert audit["X_tangent_role"] is None
    assert audit["separation_proved"] is False
    assert audit["double_counting_performed"] is False


def test_no_measured_fitted_new_primitive_scale_action_or_chat_input():
    for key in (
        "measured_input",
        "fitted_coefficient",
        "chat_only_candidate_imported",
        "new_primitive",
        "new_scale",
        "new_action",
        "new_boundary_parameter",
    ):
        assert tangent.GUARDS[key] is False


def test_no_physical_mass_stability_or_sheet_verdict():
    kinetic = tangent.kinetic_ledger()
    assert kinetic["sheet_dependence"] is None
    assert tangent.GUARDS["physical_mass_claim"] is False
    assert tangent.GUARDS["stability_claim"] is False
    assert "physical mass" in kinetic["physical_claims_not_made"]
    assert "global sheet selection" in kinetic["physical_claims_not_made"]


def test_frozen_prediction_hashes_are_exactly_unchanged():
    expected = {
        "docs/frozen_predictions.md": (
            "9EA147C56537520C86D3C4F9B864C6BA"
            "98BAC9E64931EDAE96449F3B335A36C4"
        ),
        "docs/frozen_predictions.json": (
            "F38210E0689871A25A9D5B0A1A423988"
            "3B7240CD7D0E25CDCF4C8CAB72A2CBE7"
        ),
    }
    for relative, digest in expected.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper()
        assert actual == digest


def test_official_prediction_logic_audit_remains_green():
    result = subprocess.run(
        ["python", "tools/audit_bhsm_status.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(result.stdout)
    assert payload["passed"] is True
    assert payload["checks"]["official_predictions_unchanged"] is True


def test_materialized_artifacts_match_deterministic_bytes():
    for filename, expected in tangent.artifact_bytes().items():
        assert (ROOT / "artifacts" / filename).read_bytes() == expected


def test_artifact_payloads_all_carry_the_same_bounded_verdicts():
    for payload in tangent.artifact_payloads().values():
        assert payload["primary_result"] == tangent.PRIMARY_RESULT
        assert payload["schur_result"] == tangent.SCHUR_RESULT
        assert payload["kinetic_result"] == tangent.KINETIC_RESULT
        assert payload["generic_pseudoinverse"] is False
        assert payload["numerical_solve_launched"] is False
