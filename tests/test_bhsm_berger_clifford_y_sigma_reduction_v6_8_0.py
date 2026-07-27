from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import berger_clifford_y_sigma_reduction as reduction


ROOT = Path(__file__).resolve().parents[1]


def exact_zero(expression):
    if isinstance(expression, sp.MatrixBase):
        return all(sp.simplify(entry) == 0 for entry in expression)
    return sp.simplify(expression) == 0


@pytest.fixture(scope="session")
def geometry():
    return {
        "metric": reduction.coordinate_metric(),
        "expected_metric": reduction.expected_coordinate_metric(),
        "inverse": reduction.inverse_metric(),
        "coframe": reduction.coframe_matrix(),
        "dual": reduction.dual_frame_matrix(),
    }


def test_exact_coordinate_metric(geometry):
    assert exact_zero(geometry["metric"] - geometry["expected_metric"])


def test_exact_determinant():
    expected = (
        reduction.R**6
        * sp.exp(2 * reduction.BETA)
        * sp.sin(reduction.THETA) ** 2
        / 64
    )
    assert exact_zero(reduction.metric_determinant() - expected)


def test_exact_inverse_metric(geometry):
    assert exact_zero(geometry["metric"] * geometry["inverse"] - sp.eye(3))


def test_coframe_reconstructs_metric(geometry):
    assert exact_zero(
        geometry["coframe"].T * geometry["coframe"] - geometry["metric"]
    )


def test_orthonormal_frame_rotation_preserves_metric(geometry):
    alpha = sp.symbols("alpha", real=True)
    rotation = sp.ImmutableMatrix(
        [
            [sp.cos(alpha), sp.sin(alpha), 0],
            [-sp.sin(alpha), sp.cos(alpha), 0],
            [0, 0, 1],
        ]
    )
    rotated = rotation * geometry["coframe"]
    assert exact_zero(rotated.T * rotated - geometry["metric"])


def test_dual_frame_is_derived_inverse(geometry):
    assert exact_zero(geometry["coframe"] * geometry["dual"].T - sp.eye(3))
    assert exact_zero(
        geometry["dual"] - reduction.expected_dual_frame_matrix()
    )


def test_vertical_dual_frame_has_exp_minus_beta():
    vertical = reduction.expected_dual_frame_matrix()[2, 2]
    assert exact_zero(
        vertical - 2 * sp.exp(-reduction.BETA) / reduction.R
    )


def test_exact_volume_density_and_total_volume():
    density = (
        reduction.R**3
        * sp.exp(reduction.BETA)
        * sp.sin(reduction.THETA)
        / 8
    )
    assert exact_zero(reduction.volume_density() - density)
    assert exact_zero(
        reduction.total_volume()
        - 2 * sp.pi**2 * reduction.R**3 * sp.exp(reduction.BETA)
    )


def test_round_limit_is_round_sphere_not_collapse():
    round_volume = reduction.total_volume().subs(reduction.BETA, 0)
    assert exact_zero(round_volume - 2 * sp.pi**2 * reduction.R**3)
    assert round_volume != 0


def test_reversed_euler_fiber_convention_preserves_scalar_geometry(geometry):
    fiber_reversal = sp.diag(1, 1, -1)
    transformed = fiber_reversal.T * geometry["metric"] * fiber_reversal
    assert exact_zero(transformed.det() - geometry["metric"].det())
    assert exact_zero(
        sp.sqrt(transformed.det()) ** 2 - sp.sqrt(geometry["metric"].det()) ** 2
    )
    assert (
        reduction.gamma_star_classification()["declared_Gamma_star"][
            "Berger_beta_dependence"
        ]
        == "none"
    )


def test_correct_euler_angle_periods_are_serialized():
    payload = reduction.artifact_payloads()["geometry"]
    assert payload["ranges"] == {
        "theta": "[0,pi]",
        "phi": "[0,2pi]",
        "psi": "[0,4pi]",
    }


def test_levi_civita_connection_round_limit():
    connection = reduction.levi_civita_connection()
    beta0 = {key: sp.simplify(value.subs(reduction.BETA, 0)) for key, value in connection.items()}
    assert beta0 == {
        "omega_12_on_e3": -1 / reduction.R,
        "omega_13_on_e2": 1 / reduction.R,
        "omega_23_on_e1": -1 / reduction.R,
    }


def test_homogeneous_mode_is_exactly_normalized():
    assert reduction.normalized_mode_integral() == 1
    expected_density = 1 / (
        2 * sp.pi**2 * reduction.R**3 * sp.exp(reduction.BETA)
    )
    assert exact_zero(
        reduction.normalized_invariant_mode_density() - expected_density
    )


def test_internal_operator_has_correct_round_eigenvalue():
    eigenvalue = reduction.invariant_dirac_eigenvalue()
    assert exact_zero(
        eigenvalue.subs(reduction.BETA, 0) - sp.Rational(3, 2) / reduction.R
    )


def test_mode_status_does_not_claim_global_spectrum():
    status = reduction.mode_status()
    assert "no global-lowest spectrum claim" in status["spectral_scope"]
    assert status["cos_squared_candidate"]["repository_source_found"] is False
    assert status["cos_squared_candidate"]["used_in_theorem"] is False


def test_coordinate_gamma_psi_has_mixing_and_vertical_scaling():
    coefficients = reduction.coordinate_gamma_coefficients()["psi"]
    expected = (
        -2
        * sp.sin(reduction.PSI)
        * sp.cos(reduction.THETA)
        / (reduction.R * sp.sin(reduction.THETA)),
        -2
        * sp.cos(reduction.PSI)
        * sp.cos(reduction.THETA)
        / (reduction.R * sp.sin(reduction.THETA)),
        2 * sp.exp(-reduction.BETA) / reduction.R,
    )
    assert all(exact_zero(actual - wanted) for actual, wanted in zip(coefficients, expected))
    assert coefficients[0] != 0
    assert coefficients[1] != 0


def test_gamma_star_is_the_collar_operator():
    row = reduction.gamma_star_classification()
    declared = row["declared_Gamma_star"]
    assert declared["definition"] == "K=i Gamma_n Gamma_star"
    assert declared["Berger_beta_dependence"] == "none"
    assert row["Gamma_star_equals_Gamma_psi"] is False
    assert row["gamma_star_projection_exp_minus_beta"] is False


def test_orthonormal_internal_candidates_have_no_scale():
    candidates = reduction.gamma_star_classification()["candidates"]
    assert candidates["Gamma_hat3"]["Berger_beta_dependence"] == "none"
    assert (
        candidates["internal_volume"]["Berger_beta_dependence"]
        == "none in an orthonormal frame"
    )


def test_coordinate_operator_is_not_a_scalar_exp_minus_beta_projection():
    candidate = reduction.gamma_star_classification()["candidates"]["Gamma_psi"]
    assert "transverse frame mixing" in candidate["Berger_beta_dependence"]
    assert "Gamma^hat1" in candidate["formula"]
    assert "Gamma^hat2" in candidate["formula"]
    assert "exp(-beta) Gamma^hat3" in candidate["formula"]


def test_canonical_kinetic_normalization_cancels_berger_volume():
    row = reduction.canonical_reduction()
    assert row["Z_psi"].endswith("= 1")
    assert row["I_sigma"].endswith("= Gamma_star")
    assert row["canonical_normalization_cancellation"] is True


def test_sigma_is_not_given_an_invented_scalar_normalization():
    row = reduction.canonical_reduction()
    assert "already-reduced" in row["sigma_ontology"]
    assert row["Z_sigma"].startswith("not applicable")


def test_four_dimensional_coupling_is_beta_independent():
    row = reduction.canonical_reduction()
    assert row["four_dimensional_coupling"] == "y_sigma^(4)(beta)=lambda_geom"
    assert row["relative_coupling"].endswith("=1")
    assert row["absolute_lock"] is False
    assert row["relative_exp_minus_beta_lock"] is False
    assert row["surviving_primitive"] == "lambda_geom = y_sigma(0)"


def test_round_limit_retains_the_primitive():
    row = reduction.canonical_reduction()
    assert row["round_limit"] == "y_sigma^(4)(0)=lambda_geom"
    assert reduction.GUARDS["lambda_geom_set_to_one"] is False


def test_hopf_stiffness_identity_is_true_but_not_a_coupling_proof():
    inverse_square_root = sp.exp(-reduction.BETA)
    ratio = sp.exp(2 * reduction.BETA)
    assert exact_zero(inverse_square_root**2 - 1 / ratio)
    hopf = reduction.artifact_payloads()["reduction"]["Hopf_stiffness"]
    assert hopf["identity_proves_wall_coupling"] is False


def test_dimensions_are_consistent():
    dimensions = reduction.canonical_reduction()["dimensions"]
    assert dimensions["f_beta"] == "length^(-3/2)"
    assert dimensions["dvol_B"] == "length^3"
    assert dimensions["Z_psi"] == "dimensionless"
    assert dimensions["lambda_geom"] == "dimensionless"


def test_charge_family_conjugation_and_wall_kill_tests():
    checks = reduction.kill_tests()
    for key in (
        "charge_and_Y_BH_compatible",
        "family_universal",
        "conjugation_compatible",
        "wall_parity_preserved",
        "scalar_wall_sign_preserved",
    ):
        assert checks[key]


def test_hidden_input_audit():
    report = reduction.artifact_payloads()["report"]
    assert report["measured_inputs"] == []
    assert report["fitted_parameters"] == []
    assert report["retained_primitive_count"] == 1
    assert report["new_artifact_count"] == 4
    assert all(
        report[key] is False
        for key in (
            "frozen_predictions_changed",
            "official_prediction_logic_changed",
            "measured_derivation_input_used",
            "physical_bulk_Dirac_parent_law_introduced",
            "sector_dependent_coupling_introduced",
            "global_spectrum_claimed",
        )
    )


def test_primary_theorem_rejects_exp_minus_beta():
    report = reduction.artifact_payloads()["report"]
    assert reduction.PRIMARY_RESULT == (
        "BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION"
    )
    assert report["theorem"]["verdict"] == "rejected for the adopted Gamma_star"
    assert report["theorem"]["actual_law"] == (
        "y_sigma(beta)=y_sigma(0)=lambda_geom"
    )


def test_exactly_four_deterministic_artifacts():
    assert tuple(reduction.ARTIFACT_FILES) == (
        "geometry",
        "gamma",
        "reduction",
        "report",
    )
    assert len(reduction.artifact_bytes()) == 4


def test_materialization_is_byte_deterministic(tmp_path):
    first = reduction.materialize_artifacts(tmp_path)
    first_bytes = {path.name: path.read_bytes() for path in first}
    second = reduction.materialize_artifacts(tmp_path)
    second_bytes = {path.name: path.read_bytes() for path in second}
    assert first_bytes == second_bytes == reduction.artifact_bytes()


def test_committed_artifacts_match_materializer():
    expected = reduction.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
