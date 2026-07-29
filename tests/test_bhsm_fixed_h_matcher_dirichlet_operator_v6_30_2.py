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

from bhsm.interface import fixed_h_matcher_dirichlet_operator as fixed
from bhsm.interface import reduced_fold_operator_domain as robin


def test_v6301_merge_ancestry_pin():
    assert fixed.SOURCE_MAIN_SHA == (
        "57f5945f93b7db6d5781a2b919904073dcc05def"
    )
    assert fixed.V6301_SCIENTIFIC_SHA == (
        "e54960b714edd4baba740d9fcb1a587ff0d64f1c"
    )


def test_full_frozen_action_is_varied_before_scalar_reduction():
    ledger = fixed.action_variation_ledger()
    for sector in ("S_P1,+", "S_GHY,+", "S_scalar", "S_B1", "S_match"):
        assert sector in ledger["total_action"]
    assert ledger["new_action_term"] is False


def test_fixed_h_and_arbitrary_multiplier_variations_are_separated():
    ledger = fixed.action_variation_ledger()
    assert ledger["fixed_h_variation"] == "delta h_mu_nu=0"
    assert "delta Lambda" in ledger["arbitrary_variations"][1]
    assert "h_mu_nu-iota^*gamma_mu_nu=0" in (
        ledger["matcher_equations"]["delta_Lambda"]
    )


def test_matcher_reaction_equation_has_action_sign():
    equation = fixed.action_variation_ledger()["matcher_equations"]["delta_gamma"]
    assert equation == "Pi_cap,mu_nu-Lambda_mu_nu=0"
    assert "minus" in fixed.kkt_operator_ledger()["matcher_sign"]


def test_GHY_cancellation_and_two_cap_orientation():
    ledger = fixed.action_variation_ledger()
    assert "cancels normal derivatives" in ledger["GHY"]
    assert "add" in ledger["two_cap_orientation"]


def test_intrinsic_B1_is_fixed_h_data_not_bulk_Robin_hessian():
    ledger = fixed.action_variation_ledger()
    assert ledger["intrinsic_B1_in_radial_KKT"] is False
    assert "independent fixed h" in ledger["intrinsic_B1_reason"]
    assert fixed.kkt_operator_ledger()["intrinsic_B1_Hessian_included"] is False


def test_complete_scalar_trace_map():
    psi, E, boxE = sp.symbols("psi E boxE")
    trace = fixed.scalar_trace_map(psi, E, boxE)
    assert trace["trace_scalar"] == psi + boxE / 4
    assert trace["scalar_longitudinal"] == E


def test_radial_lapse_and_shift_are_not_induced_metric_trace_data():
    trace = fixed.scalar_trace_ledger()
    assert any(row.startswith("A ") for row in trace["does_not_enter_trace"])
    assert any(row.startswith("B ") for row in trace["does_not_enter_trace"])


def test_two_scalar_matcher_reaction_channels_are_retained_pre_gauge():
    reactions = fixed.scalar_trace_ledger()["matcher_reactions"]
    assert len(reactions) == 2
    assert "eta_tr" in reactions[0]
    assert "eta_L" in reactions[1]


def test_homogeneous_reduction_recovers_psi_Dirichlet():
    psi = sp.symbols("psi")
    assert fixed.reduced_homogeneous_trace(psi) == psi
    reduction = fixed.scalar_trace_ledger()["homogeneous_reduction"]
    assert reduction["minimum_condition_recovered"] == "psi(1)=0"


def test_scalar_field_boundary_and_momentum_constraint_are_separate():
    equations = fixed.scalar_trace_ledger()["separate_equations"]
    assert equations["bulk_scalar"] == "delta_sigma(1)=0"
    assert "W=0" in equations["momentum"]
    assert "E=0" in equations["gauge"]


def test_matcher_hessian_is_symmetric_and_indefinite():
    p1, p2, e1, e2 = sp.symbols("p1 p2 e1 e2")
    q12 = fixed.matcher_hessian_bilinear(p1, e1, p2, e2)
    q21 = fixed.matcher_hessian_bilinear(p2, e2, p1, e1)
    assert sp.simplify(q12 - q21) == 0
    assert q12 == -e1 * p2 - e2 * p1


def test_KKT_matrix_contains_B_and_B_dagger_with_no_multiplier_square():
    matrix = fixed.kkt_block_matrix()
    assert matrix[1][3] == "-B_D^dagger"
    assert matrix[3][1] == "-B_D"
    assert matrix[3][3] == "0"


def test_KKT_reconstructs_bulk_operator_without_Robin_replacement():
    ledger = fixed.kkt_operator_ledger()
    assert ledger["L_bulk"] == robin.L0_L1_block_ledger()
    assert ledger["B_D"] == "endpoint evaluation psi -> psi(1)"
    assert ledger["operator_type"].endswith("not a Robin realization")


def test_natural_reaction_and_constraint_are_distinct_KKT_rows():
    ledger = fixed.kkt_operator_ledger()
    assert ledger["natural_boundary_reaction"] == "P_psi(1)-eta_tr=r_eta"
    assert "B_D psi=b_D" in ledger["strong_equations"]


def test_extended_green_current_is_antisymmetric():
    variables = sp.symbols("A1 p1 s1 e1 A2 p2 s2 e2")
    current12 = fixed.extended_green_current(*variables)
    current21 = fixed.extended_green_current(
        *variables[4:], *variables[:4]
    )
    assert sp.simplify(current12 + current21) == 0


def test_matcher_pairing_cancels_endpoint_canonical_momentum():
    A1, A2, p1, p2, dp1, dp2 = sp.symbols(
        "A1 A2 p1 p2 dp1 dp2"
    )
    psi1 = p1 + dp1 * (fixed.T - 1)
    psi2 = p2 + dp2 * (fixed.T - 1)
    s1 = fixed.T - 1
    s2 = 2 * (fixed.T - 1)
    eta1 = robin.metric_boundary_momentum(A1, psi1).subs(fixed.T, 1)
    eta2 = robin.metric_boundary_momentum(A2, psi2).subs(fixed.T, 1)
    current = fixed.extended_green_current(
        A1, psi1, s1, eta1, A2, psi2, s2, eta2
    )
    assert sp.simplify(sp.trigsimp(current.subs(fixed.T, 1))) == 0


def test_regular_pole_current_vanishes():
    A1, A2, p1, p2, s1, s2, e1, e2 = sp.symbols(
        "A1 A2 p1 p2 s1 s2 e1 e2"
    )
    current = fixed.extended_green_current(
        A1, p1, s1, e1, A2, p2, s2, e2
    )
    # The finite matcher pairing lives only at B1, not at the pole.
    bulk = current - p1 * e2 + p2 * e1
    assert sp.limit(bulk, fixed.T, 0, dir="+") == 0


def test_adjoint_domain_is_derived_and_equal():
    ledger = fixed.green_adjoint_ledger()
    assert ledger["domains_equal"] is True
    assert "matcher pairing cancels" in ledger["adjoint_domain"]
    assert ledger["result"] == fixed.ADJOINT_RESULT


def test_old_metric_modulus_is_rejected_exactly():
    assert fixed.metric_modulus_dirichlet_residual() == 1
    modulus = fixed.fixed_h_kernel_ledger()["metric_modulus"]
    assert modulus["Dirichlet_residual"] == 1
    assert modulus["admitted"] is False


def test_fixed_h_kernel_is_scalar_Jacobi_only():
    ledger = fixed.fixed_h_kernel_ledger()
    assert ledger["quotient_kernel"] == "span{u1}"
    assert ledger["kernel_dimension"] == 1
    assert "(0,0,u1,0)" in ledger["scalar_Jacobi"]["vector"]


def test_no_matcher_only_or_threading_zero_mode():
    ledger = fixed.fixed_h_kernel_ledger()
    assert "no multiplier zero mode" in ledger["matcher_only"]
    assert "W=0" in ledger["threading"]


def test_adjoint_kernel_Fredholm_index_and_closed_range():
    ledger = fixed.fixed_h_kernel_ledger()
    assert ledger["adjoint_kernel"] == "span{u1}"
    assert ledger["adjoint_kernel_dimension"] == 1
    assert ledger["Fredholm_index"] == 0
    assert ledger["closed_range"] is True


def test_exact_source_compatibility_condition():
    ledger = fixed.fixed_h_kernel_ledger()
    assert "<u1,f_sigma>_w=0" in ledger["compatibility"]
    assert "Noether identity" in ledger["compatibility"]


def test_metric_areal_inverse_solves_algebraic_A_row():
    source = sp.Function("f_A")(fixed.T)
    response = fixed.metric_areal_inverse(source)
    c = robin.metric_q0_coefficients()
    l_aa = sp.simplify(2 * c["cAA"] / robin.radial_weight())
    assert sp.simplify(l_aa * response["A"] - source) == 0
    assert response["psi"] == 0


def test_metric_inverse_reaction_is_canonical_momentum():
    source = sp.Function("f_A")(fixed.T)
    response = fixed.metric_areal_inverse(source)
    expected = robin.metric_boundary_momentum(
        response["A"], response["psi"]
    ).subs(fixed.T, 1)
    assert sp.simplify(response["eta_tr"] - expected) == 0


def test_scalar_complement_inverse_is_spectral_not_pseudoinverse():
    ledger = fixed.inverse_ledger()
    assert "sum_{n>=2}" in ledger["scalar_inverse"]
    assert ledger["v6_28_Robin_inverse_used"] is False
    assert ledger["generic_pseudoinverse_used"] is False


def test_complement_inverse_two_method_validation():
    diagnostics = fixed.complement_inverse_diagnostics()
    assert len(diagnostics["methods"]) == 2
    assert diagnostics["positive_complement_gap"] > 64
    assert diagnostics["route_difference"]["certified_upper_bound"] == 1e-10
    assert diagnostics["projector_residual"]["certified_upper_bound"] == 1e-10


def test_complement_inverse_boundary_and_matcher_residuals():
    diagnostics = fixed.complement_inverse_diagnostics()
    assert diagnostics["Dirichlet_residual"]["certified_upper_bound"] == 1e-10
    assert diagnostics["pole_residual"]["certified_upper_bound"] == 1e-10
    assert (
        diagnostics["matcher_parameter_residual"]["certified_upper_bound"]
        == 1e-8
    )


def test_nonlinear_Dirichlet_sources_orders_one_to_three():
    a1, a2 = sp.symbols("a1 a2")
    assert fixed.dirichlet_metric_source(1, {}) == 0
    assert fixed.dirichlet_metric_source(2, {1: a1}) == -a1**2
    assert fixed.dirichlet_metric_source(3, {1: a1, 2: a2}) == (
        -3 * a1 * a2
    )


def test_nonlinear_Dirichlet_map_vanishes_recursively_on_fixed_h_data():
    for order in range(1, 8):
        assert fixed.dirichlet_metric_source(
            order, {n: sp.Integer(0) for n in range(1, order)}
        ) == 0


def test_warp_to_additive_Weyl_conversion_uses_same_factorial_convention():
    a1, a2, a3 = sp.symbols("a1 a2 a3")
    rows = {1: a1, 2: a2, 3: a3}
    assert fixed.warp_to_weyl_coefficient(1, rows) == a1
    assert fixed.warp_to_weyl_coefficient(2, rows) == a2 + a1**2
    assert fixed.warp_to_weyl_coefficient(3, rows) == a3 + 3 * a1 * a2


def test_arbitrary_order_reaction_reproduces_linear_action_momentum():
    assert fixed.linear_reaction_identity_residual() == 0
    assert fixed.nonlinear_boundary_ledger()[
        "linear_reaction_matches_v6_28_momentum"
    ] is True


def test_second_order_matcher_reaction_is_generated_not_assumed_zero():
    A1, A2, p1, p2, dp1, dp2 = sp.symbols(
        "A1 A2 p1 p2 dp1 dp2"
    )
    reaction = fixed.matcher_reaction_coefficient(
        2,
        {1: A1, 2: A2},
        {1: p1, 2: p2},
        {1: dp1, 2: dp2},
    )
    assert reaction != 0
    assert reaction.has(A2, p2, dp2)


def test_all_five_phase_A_verdicts_are_emitted_once_in_scoped_ledgers():
    ledgers = [
        fixed.action_variation_ledger(),
        fixed.kkt_operator_ledger(),
        fixed.green_adjoint_ledger(),
        fixed.fixed_h_kernel_ledger(),
        fixed.inverse_ledger(),
        fixed.nonlinear_boundary_ledger(),
    ]
    text = json.dumps(ledgers)
    for verdict in (
        fixed.OPERATOR_RESULT,
        fixed.ADJOINT_RESULT,
        fixed.RANGE_RESULT,
        fixed.INVERSE_RESULT,
        fixed.NONLINEAR_RESULT,
    ):
        assert text.count(verdict) == 1


def test_integrity_guards():
    for key, value in fixed.GUARDS.items():
        assert value is False, key


def test_empirical_inverse_is_quarantined():
    text = json.dumps(fixed.artifact_payloads())
    for forbidden in ('"m_tau"', '"m_mu"', '"m_e"'):
        assert forbidden not in text


def test_artifact_count_and_names():
    assert len(fixed.ARTIFACT_FILES) == 5
    assert set(fixed.artifact_payloads()) == set(fixed.ARTIFACT_FILES)


def test_deterministic_artifact_bytes():
    first = fixed.artifact_bytes()
    second = fixed.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_checked_in_artifacts_are_current():
    for name, content in fixed.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_fixed_h_matcher_dirichlet_operator_v6_30_2.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fixed.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fixed.ARTIFACT_FILES.values()
    }
    assert first == second == fixed.artifact_bytes()
