from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fold_schur_kinetic as kinetic


def test_exact_v628_baseline():
    assert kinetic.SOURCE_MAIN_SHA == (
        "86df2f5c72e8c6fe07c2fb3ee41372a521229c84"
    )
    assert kinetic.V628_SCIENTIFIC_SHA == (
        "853bddac1852c6b328fc4cf7af2786e2f59baf34"
    )


def test_operator_pencil_derivative_identity():
    assert kinetic.schur_derivative_identity_residual() == 0


def test_exact_modulus_source_contains_catalan_and_log2():
    source = kinetic.modulus_source_exact()
    assert source.has(sp.Catalan)
    assert source.has(sp.log(2))
    assert source.has(kinetic.TAU, kinetic.CHI_1, kinetic.KAPPA_1)


def test_exact_modulus_lift_matches_v628():
    assert kinetic.modulus_lift_exact() == (
        12 * kinetic.C_PARTIAL
        + 3 * kinetic.KAPPA_1 * (6 - sp.pi)
    )


def test_modulus_lift_positive_on_normalized_representative():
    value = kinetic.modulus_lift_exact().subs(
        {kinetic.C_PARTIAL: sp.Rational(1, 2), kinetic.KAPPA_1: 1}
    )
    assert value == 3 * (8 - sp.pi)
    assert value > 0


def test_gravitational_schur_sign_is_negative():
    expression = kinetic.gravitational_schur_exact()
    value = expression.subs(
        {
            kinetic.CHI_1: kinetic.CHI_1_REPOSITORY,
            kinetic.C_PARTIAL: kinetic.C_PARTIAL_NORMALIZED,
            kinetic.KAPPA_1: kinetic.KAPPA_1_NORMALIZED,
        }
    )
    assert float(value) < 0


def test_tau_drops_out_of_gravitational_schur():
    assert not kinetic.gravitational_schur_exact().has(kinetic.TAU)


def test_weyl_term_exact_formula():
    assert kinetic.weyl_kinetic_exact() == (
        3 * kinetic.CHI_1**2 * (4 - sp.pi) ** 2 / (16 * sp.pi)
    )


def test_shooting_eigenvalue_reproduces_repository_value():
    result = kinetic.numerical_results()["shooting"]
    assert abs(result["mu"] - 29.430918352947) < 2.0e-12


def test_hypergeometric_eigenvalue_agrees():
    result = kinetic.numerical_results()["hypergeometric"]
    assert abs(result["mu"] - 29.430918352947) < 2.0e-12


def test_two_scalar_methods_agree():
    result = kinetic.numerical_results()
    assert result["method_difference"] < 5.0e-12


def test_scalar_weighted_norms_are_unity():
    result = kinetic.numerical_results()
    assert abs(result["shooting"]["weighted_norm"] - 1) < 1.0e-12
    assert abs(result["hypergeometric"]["weighted_norm"] - 1) < 1.0e-12


def test_scalar_endpoint_residuals():
    result = kinetic.numerical_results()
    assert result["shooting"]["endpoint_residual"] < 1.0e-11
    assert result["hypergeometric"]["endpoint_residual"] < 1.0e-40


def test_scalar_eigen_moment_residual():
    residual = kinetic.numerical_results()["shooting"][
        "eigen_moment_residual"
    ]
    assert residual < 1.0e-10


def test_scalar_kinetic_exceeds_inherited_lower_bound():
    result = kinetic.numerical_results()
    assert result["K_scalar"] > 2
    assert abs(result["K_scalar"] - 6.6734434328801) < 5.0e-12


def test_scalar_perp_gap_is_positive():
    result = kinetic.numerical_results()
    assert result["next_scalar_eigenvalue"] > result["hypergeometric"]["mu"]
    assert result["scalar_perp_gap"] > 60


def test_modulus_source_numeric():
    value = kinetic.numerical_results()["modulus_source"]
    assert abs(value - (-3.73862651321521)) < 5.0e-12


def test_modulus_lift_numeric():
    value = kinetic.numerical_results()["modulus_lift"]
    assert abs(value - 14.5752220392306) < 5.0e-12


def test_gravitational_constraint_value():
    value = kinetic.numerical_results()["K_grav_constraint_J"]
    assert abs(value - (-0.958978749530842)) < 5.0e-12


def test_weyl_value():
    value = kinetic.numerical_results()["K_Weyl"]
    assert abs(value - 1.220620174933802) < 5.0e-13


def test_total_kinetic_sum():
    result = kinetic.numerical_results()
    expected = (
        result["K_scalar"]
        + result["K_grav_constraint_J"]
        + result["K_Weyl"]
    )
    assert abs(result["k_q_E"] - expected) < 1.0e-14
    assert abs(result["k_q_E"] - 6.93508485828307) < 5.0e-12


def test_total_kinetic_is_positive_beyond_uncertainty():
    result = kinetic.numerical_results()
    assert result["k_q_E"] - result["uncertainty"] > 0


def test_scalar_ledger_has_two_cap_factor():
    ledger = kinetic.scalar_ledger()
    assert ledger["cap_multiplicity"] == 2
    assert ledger["formula"].startswith("K_scalar=2 Z5")
    assert ledger["result"] == kinetic.SCALAR_RESULT


def test_schur_uses_projected_inverse_only():
    ledger = kinetic.schur_ledger()
    assert ledger["projected_inverse_only"] is True
    assert ledger["B1_included"] is True
    assert kinetic.GUARDS["unprojected_inverse_used"] is False


def test_affine_terms_cancel_before_modulus_equation():
    ledger = kinetic.schur_ledger()
    assert "L1 v cancels" in ledger["affine_cancellation"]


def test_complementary_J1_enters_only_at_D4():
    ledger = kinetic.schur_ledger()
    assert "O(lambda^2)" in ledger["complement_J1_order"]


def test_one_dimensional_kernel_condition_number():
    validation = kinetic.validation_ledger()["kernel_projection"]
    assert validation["one_by_one_condition_number"] == 1.0


def test_numerical_methods_are_independent():
    methods = kinetic.validation_ledger()["methods"]
    assert len(methods) == 2
    assert "shooting" in methods[0]
    assert "hypergeometric" in methods[1]


def test_precision_and_tolerance_are_reported():
    validation = kinetic.validation_ledger()
    assert validation["precision"]["hypergeometric_dps"] >= 50
    assert validation["precision"]["shooting_rtol"] <= 5.0e-13
    assert validation["platform_tolerance"] == 5.0e-10


def test_conditional_positive_verdict():
    ledger = kinetic.kinetic_ledger()
    assert ledger["sign"] == "positive"
    assert ledger["zero_excluded_by_uncertainty"] is True
    assert ledger["result"] == (
        "BHSM_FOLD_KINETIC_NORM_POSITIVE_CONDITIONALLY"
    )


def test_negative_sign_audit_not_triggered_truthfully():
    ledger = kinetic.kinetic_ledger()
    assert ledger["negative_sign_audit"] == (
        "BHSM_FOLD_NEGATIVE_NORM_AUDIT_NOT_TRIGGERED"
    )
    assert kinetic.GUARDS["negative_sign_hidden"] is False


def test_sheet_and_scalar_sign_independence():
    ledger = kinetic.kinetic_ledger()
    assert "tau" in ledger["sheet_dependence"]
    assert "quadratically" in ledger["scalar_sign_dependence"]


def test_positive_kinetic_does_not_claim_potential_stability():
    ledger = kinetic.kinetic_ledger()
    assert ledger["potential_stability"] == (
        "not decided by a kinetic sign"
    )
    assert kinetic.GUARDS["stability_claimed"] is False


def test_v630_handoff_permitted():
    handoff = kinetic.handoff_ledger()
    assert handoff["v6_30_permitted"] is True
    assert handoff["next_result"] == kinetic.NEXT_RESULT
    assert handoff["fatal_inconsistency"] is False


def test_no_dimensionless_mass_yet():
    missing = kinetic.handoff_ledger()["not_derived"]
    assert "dimensionless fold mass" in missing
    assert "physical mass" in missing


def test_repository_chi_is_not_measured_input():
    representative = kinetic.kinetic_ledger()["normalized_representative"]
    assert "not measured input" in representative["chi_1_source"]
    assert kinetic.GUARDS["measured_input_used"] is False


def test_no_fit_chat_value_or_new_physics():
    for name in (
        "fitted_parameter_used",
        "chat_only_value_imported",
        "new_action_introduced",
        "new_primitive_introduced",
        "new_scale_introduced",
    ):
        assert kinetic.GUARDS[name] is False


def test_kernel_B1_and_cap_guards():
    for name in (
        "kernel_ignored",
        "B1_source_dropped",
        "two_cap_factor_dropped",
        "Weyl_term_double_counted",
        "generic_pseudoinverse_used",
    ):
        assert kinetic.GUARDS[name] is False


def test_no_frozen_or_official_logic_change():
    assert kinetic.GUARDS["frozen_predictions_changed"] is False
    assert kinetic.GUARDS["official_prediction_logic_changed"] is False


def test_no_physical_mass_claim():
    assert kinetic.GUARDS["physical_mass_claimed"] is False


def test_artifact_count_and_names():
    assert len(kinetic.ARTIFACT_FILES) == 5
    assert set(kinetic.artifact_payloads()) == set(kinetic.ARTIFACT_FILES)


def test_one_kinetic_verdict_only():
    text = json.dumps(kinetic.artifact_payloads())
    assert kinetic.PRIMARY_RESULT in text
    assert "BHSM_FOLD_KINETIC_NORM_NEGATIVE_CONDITIONALLY" not in text
    assert "BHSM_FOLD_KINETIC_NORM_NULL_CONDITIONALLY" not in text


def test_deterministic_artifact_bytes():
    first = kinetic.artifact_bytes()
    second = kinetic.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_materializer_matches_generated_bytes(tmp_path):
    paths = kinetic.materialize_artifacts(tmp_path)
    assert len(paths) == 5
    expected = kinetic.artifact_bytes()
    for path in paths:
        assert path.read_bytes() == expected[path.name]


def test_checked_in_artifacts_are_current():
    for name, content in kinetic.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = ROOT / "scripts" / "materialize_fold_schur_kinetic_v6_29_0.py"
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in kinetic.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in kinetic.ARTIFACT_FILES.values()
    }
    assert first == second == kinetic.artifact_bytes()
