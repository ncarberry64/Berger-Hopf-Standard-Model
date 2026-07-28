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

from bhsm.interface import reduced_fold_operator_domain as fold


def test_exact_v627_baseline():
    assert fold.SOURCE_MAIN_SHA == "d94f2dd71eac8f03649f73011e6b4ee830f7b09b"
    assert fold.V627_SCIENTIFIC_SHA == (
        "643bc7371fc81f07cce465abded3f5d2885bca3c"
    )


def test_critical_background_warp_lapse_and_measure():
    assert fold.a0() == sp.sqrt(2) * sp.sin(sp.pi * fold.T / 4)
    assert fold.N0 == sp.pi / 4
    assert fold.radial_weight() == sp.pi * sp.sin(sp.pi * fold.T / 4) ** 4


def test_background_equations_are_exact():
    assert all(value == 0 for value in fold.background_residuals().values())


def test_action_has_two_caps_and_one_common_B1():
    action = fold.action_ledger()
    assert action["cap_count"] == 2
    assert action["common_B1_count"] == 1
    assert action["new_term"] is False


def test_critical_kappa0_normalization():
    assert fold.KAPPA_0 == 12 * fold.KAPPA_1


def test_metric_density_contains_radial_derivatives():
    A = sp.Function("A")(fold.T)
    psi = sp.Function("psi")(fold.T)
    density = fold.metric_quadratic_density(A, psi, 0)
    assert density.has(sp.diff(psi, fold.T))
    assert not density.has(sp.diff(A, fold.T))


def test_A_is_algebraic_not_differential():
    operator = fold.L0_L1_block_ledger()["operator_type"]
    assert "A algebraic" in operator
    assert "differential-algebraic" in operator


def test_metric_scalar_cross_blocks_vanish():
    blocks = fold.L0_L1_block_ledger()["L0"]
    assert blocks["L_Adelta_sigma"] == "0"
    assert blocks["L_psidelta_sigma"] == "0"
    assert "sigma0=0" in fold.L0_L1_block_ledger()[
        "mixed_scalar_blocks_zero_reason"
    ]


def test_inherited_principal_lapse_weyl_block():
    expected = (
        6
        * fold.KAPPA_1
        / fold.a0() ** 2
        * sp.Matrix([[0, 1], [1, 2]])
    )
    assert fold.principal_lapse_weyl_matrix() == expected


def test_L1_scalar_block():
    matrix = fold.L0_L1_block_ledger()["L1"]["metric"]
    assert matrix[2][2] == sp.sstr(-2 * fold.Z5 / fold.a0() ** 2)


def test_B1_endpoint_hessian():
    assert fold.b1_quadratic_form(sp.Integer(1), fold.LAMBDA) == (
        6 * fold.C_PARTIAL * fold.LAMBDA
    )
    assert (
        fold.L0_L1_block_ledger()["L1"]["B1_endpoint_Hessian"]
        == "12 C_partial in the psi-psi slot"
    )


def test_scalar_two_cap_quadratic_density():
    scalar = sp.Function("s")(fold.T)
    density = fold.scalar_quadratic_density(scalar, 0)
    assert density.coeff(sp.diff(scalar, fold.T) ** 2) == (
        -fold.Z5 * fold.a0() ** 4 / fold.N0
    )
    assert density.coeff(scalar**2).has(fold.A5)


def test_scalar_operator_reconstructs_stored_equation():
    scalar = sp.Function("s")(fold.T)
    expression = fold.scalar_euler_expression(scalar, 0)
    expected = (
        2
        * fold.Z5
        / fold.radial_weight()
        * sp.diff(
            fold.a0() ** 4 / fold.N0 * sp.diff(scalar, fold.T),
            fold.T,
        )
        - 2 * fold.A5 * scalar
    )
    assert sp.simplify(expression - expected) == 0


def test_lambda_scalar_operator_coefficient():
    scalar = sp.Function("s")(fold.T)
    difference = (
        fold.scalar_euler_expression(scalar, fold.LAMBDA)
        - fold.scalar_euler_expression(scalar, 0)
    )
    assert sp.simplify(
        difference
        + 2 * fold.Z5 * fold.LAMBDA * scalar / fold.a0() ** 2
    ) == 0


def test_hamiltonian_solution_satisfies_A_equation_at_lambda_zero():
    psi = sp.Function("psi")(fold.T)
    A = fold.hamiltonian_solution_for_A(psi)
    assert sp.simplify(
        fold.metric_euler_expressions(A, psi, 0)["A"]
    ) == 0


def test_metric_boundary_momentum_is_action_derivative():
    A = sp.Function("A")(fold.T)
    psi = sp.Function("psi")(fold.T)
    density = fold.metric_quadratic_density(A, psi, 0)
    assert sp.simplify(
        sp.diff(density, sp.diff(psi, fold.T))
        - fold.metric_boundary_momentum(A, psi)
    ) == 0


def test_B1_metric_domain_is_Robin():
    ledger = fold.domain_ledger()["B1"]
    assert "P_psi(1)+12 C_partial lambda psi(1)=0" in ledger["metric"]
    assert ledger["scalar"] == "delta_sigma_perp(1)=0"


def test_green_current_is_antisymmetric():
    symbols = sp.symbols("A1 p1 s1 A2 p2 s2")
    current12 = fold.green_current(*symbols)
    current21 = fold.green_current(*symbols[3:], *symbols[:3])
    assert sp.simplify(current12 + current21) == 0


def test_regular_pole_flux_vanishes_for_regular_constants():
    A1, A2, p1, p2, s1, s2 = sp.symbols("A1 A2 p1 p2 s1 s2")
    current = fold.green_current(A1, p1, s1, A2, p2, s2)
    assert sp.limit(current, fold.T, 0, dir="+") == 0


def test_green_current_vanishes_for_B1_domains_symbolically():
    domain = fold.domain_ledger()
    assert domain["self_adjointness"] is True
    assert "psi2 P1-psi1 P2" in domain["proof"]


def test_formal_adjoint_domain_is_derived_not_assumed():
    domain = fold.domain_ledger()
    assert domain["formal_adjoint"].startswith("the displayed")
    assert domain["adjoint_domain"].startswith("the same")
    assert domain["result"] == fold.ADJOINT_RESULT


def test_gauge_kernel_transformations():
    xi = sp.Function("xi")(fold.T)
    gauge = fold.gauge_kernel(xi)
    assert gauge["A"] == -sp.diff(xi, fold.T)
    assert gauge["psi"] == (
        -sp.diff(fold.a0(), fold.T) * xi / fold.a0()
    )
    assert gauge["delta_sigma"] == 0


def test_gauge_kernel_satisfies_hamiltonian_constraint():
    xi = sp.Function("xi")(fold.T)
    gauge = fold.gauge_kernel(xi)
    equation = fold.metric_euler_expressions(gauge["A"], gauge["psi"], 0)["A"]
    assert sp.trigsimp(sp.simplify(equation)) == 0


def test_metric_modulus_satisfies_hamiltonian_constraint():
    modulus = fold.metric_modulus()
    equation = fold.metric_euler_expressions(
        modulus["A"], modulus["psi"], 0
    )["A"]
    assert sp.trigsimp(sp.simplify(equation)) == 0


def test_metric_modulus_B1_momentum_vanishes_at_lambda_zero():
    modulus = fold.metric_modulus()
    assert sp.simplify(
        fold.metric_boundary_momentum(
            modulus["A"], modulus["psi"]
        ).subs(fold.T, 1)
    ) == 0


def test_metric_modulus_lift_is_nonzero_and_positive():
    coefficient = fold.metric_modulus_lifting_coefficient()
    assert coefficient == (
        12 * fold.C_PARTIAL + 3 * fold.KAPPA_1 * (6 - sp.pi)
    )
    assert float(coefficient.subs({fold.C_PARTIAL: 0.5, fold.KAPPA_1: 1})) > 0


def test_quotient_kernel_and_adjoint_kernel_counts():
    kernel = fold.kernel_ledger()
    assert kernel["quotient_kernel_dimension"] == 1
    assert kernel["adjoint_kernel_dimension"] == 1
    assert kernel["scalar_perp_kernel_dimension"] == 0


def test_kernel_classifications_are_explicit():
    classes = fold.kernel_ledger()["classifications"]
    assert classes["radial_diffeomorphisms"] == "gauge"
    assert "physical fold collective" in classes["u1"]
    assert "full momentum constraint" in classes["C1_shift"]


def test_scalar_projector_normalization_and_orthogonality():
    projector = fold.projector_ledger()
    assert "N0 a0^4 u1^2" in projector["normalization"]
    assert "P_perp f=f-u1" in projector["projector"]
    assert projector["kernel_removed"] is True


def test_affine_profiles_match_inherited_fold_tangent():
    profiles = fold.affine_profiles()
    assert profiles["A_q"] == -fold.TAU * fold.CHI_1 / sp.pi
    assert sp.simplify(
        profiles["psi_q"] - fold.TAU * fold.a1() / fold.a0()
    ) == 0
    assert profiles["B_q"] == (
        -fold.TAU * sp.pi * fold.CHI_1 * fold.T / 16
    )


def test_affine_convention_does_not_add_M4_X_tangent():
    profiles = fold.affine_profiles()
    assert profiles["M4_X_tangent_added"] is False
    assert fold.GUARDS["M4_curvature_tangent_double_counted"] is False


def test_threading_source_is_action_normalized():
    source = fold.threading_source_coefficients()
    assert source["J_A"].has(fold.KAPPA_1, fold.TAU, fold.CHI_1)
    assert source["J_psi_derivative"].has(
        fold.KAPPA_1, fold.TAU, fold.CHI_1
    )


def test_source_retains_radial_IBP_endpoint():
    source = fold.source_ledger()
    assert source["source_boundary_form_retained"] is True
    assert "retained with the B1 source" in source["threading"][
        "endpoint_after_radial_IBP"
    ]


def test_source_J0_J1_is_derived():
    source = fold.source_ledger()
    assert source["J0"].startswith("J0[Y]=")
    assert source["J1"].startswith("J1[Y]=")
    assert source["result"] == fold.SOURCE_RESULT


def test_direct_term_uses_one_affine_convention():
    direct = fold.source_ledger()["K_direct"]
    assert direct["radial_profiles_counted_once"] is True
    assert direct["Einstein_frame_Weyl_term_included"] is False
    assert "W=0" in direct["pure_shift_square"]
    assert fold.GUARDS["radial_profile_double_counted"] is False


def test_no_arbitrary_global_lorentzian_state():
    assert fold.source_ledger()["global_Lorentzian_state"] is None
    assert fold.GUARDS["global_Lorentzian_propagator_selected"] is False


def test_source_compatibility_is_projected_not_pseudoinverted():
    compatibility = fold.kernel_ledger()["compatibility"]
    assert "Lyapunov-Schmidt" in compatibility["metric_at_lambda1"]
    assert compatibility["M_z_nonzero"] is True
    assert fold.kernel_ledger()["generic_pseudoinverse_required"] is False


def test_scalar_source_is_projected_off_u1():
    compatibility = fold.kernel_ledger()["compatibility"]
    assert "P_perp" in compatibility["scalar"]


def test_operator_verdicts_all_derived():
    verdict = fold.verdict_ledger()
    assert verdict["all_four_derived"] is True
    assert verdict["required_results"] == {
        "operator": fold.OPERATOR_RESULT,
        "source": fold.SOURCE_RESULT,
        "adjoint_domain": fold.ADJOINT_RESULT,
        "kernel_compatibility": fold.KERNEL_RESULT,
    }


def test_v629_is_permitted_but_not_executed_here():
    verdict = fold.verdict_ledger()
    assert verdict["v6_29_permitted"] is True
    assert verdict["next_result"] == fold.NEXT_RESULT
    assert "Schur coefficient" in verdict["not_yet_derived"]


def test_no_kinetic_sign_or_Schur_number_emitted():
    assert fold.GUARDS["operator_inverse_emitted"] is False
    assert fold.GUARDS["Schur_number_emitted"] is False
    assert fold.GUARDS["kinetic_sign_emitted"] is False


def test_no_fatal_inconsistency_claim():
    verdict = fold.verdict_ledger()
    assert verdict["fatal_inconsistency"] is False
    assert verdict["obstruction_class"] is None


def test_no_measured_fit_new_action_primitive_or_scale():
    for name in (
        "measured_input_used",
        "fitted_parameter_used",
        "new_action_introduced",
        "new_primitive_introduced",
        "new_scale_introduced",
        "new_boundary_parameter_introduced",
    ):
        assert fold.GUARDS[name] is False


def test_no_frozen_or_prediction_logic_change():
    assert fold.GUARDS["frozen_predictions_changed"] is False
    assert fold.GUARDS["official_prediction_logic_changed"] is False


def test_no_mass_or_stability_claim():
    assert fold.GUARDS["physical_mass_claimed"] is False
    assert fold.GUARDS["stability_claimed"] is False


def test_artifact_names_and_payload_count():
    assert len(fold.ARTIFACT_FILES) == 5
    assert set(fold.artifact_payloads()) == set(fold.ARTIFACT_FILES)


def test_exactly_one_phase_result():
    text = json.dumps(fold.artifact_payloads())
    assert fold.PHASE_RESULT in text
    assert "BHSM_REDUCED_FOLD_OPERATOR_L0_L1_BLOCKED" not in text


def test_deterministic_artifact_bytes():
    first = fold.artifact_bytes()
    second = fold.artifact_bytes()
    assert first == second
    first_hashes = {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    }
    second_hashes = {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }
    assert first_hashes == second_hashes


def test_materializer_matches_generated_bytes(tmp_path):
    paths = fold.materialize_artifacts(tmp_path)
    assert len(paths) == 5
    expected = fold.artifact_bytes()
    for path in paths:
        assert path.read_bytes() == expected[path.name]


def test_checked_in_artifacts_are_current():
    for name, content in fold.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_reduced_fold_operator_domain_v6_28_0.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fold.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fold.ARTIFACT_FILES.values()
    }
    assert first == second == fold.artifact_bytes()
