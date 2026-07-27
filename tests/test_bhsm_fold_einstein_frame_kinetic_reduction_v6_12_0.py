from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import fold_einstein_frame_kinetic_reduction as reduction


ROOT = Path(__file__).resolve().parents[1]


def test_critical_profiles_are_exact():
    assert reduction.a0() == sp.sqrt(2) * sp.sin(sp.pi * reduction.T / 4)
    assert reduction.lapse0() == sp.pi / 4
    assert reduction.lapse1() == -reduction.CHI_1 / 4


def test_one_cap_frame_integral():
    assert reduction.one_cap_frame_integral_0() == sp.pi / 4 - sp.Rational(1, 2)


def test_exact_cap_multiplicity_and_B1_contribution():
    ledger = reduction.frame_ledger()
    assert ledger["cap_multiplicity"] == 2
    assert ledger["B1_R4_coefficient"] == "F_B1=2 C_partial=1"
    assert ledger["GHY_R4_coefficient"] == 0


def test_exact_F0():
    assert reduction.frame_F0() == sp.pi / 2
    assert reduction.frame_ledger()["F0"] == "pi/2"


def test_endpoint_differentiation_is_included():
    assert "fixed-domain N(q)=rho_J(q)" in reduction.frame_ledger()["endpoint_differentiation"]


def test_exact_first_frame_derivative():
    expected = reduction.CHI_1 * (sp.pi - 4) / 4
    assert sp.simplify(reduction.frame_F1(1) - expected) == 0
    assert sp.simplify(reduction.frame_F1(-1) + expected) == 0


def test_invalid_sheet_rejected():
    with pytest.raises(ValueError):
        reduction.frame_F1(0)
    with pytest.raises(ValueError):
        reduction.momentum_constraint_zero_shift_mismatch(0)


def test_F2_formula_contains_second_profiles():
    formula = sp.sstr(reduction.frame_F2_formula())
    assert "a_2(t)" in formula
    assert "N_2(t)" in formula
    assert reduction.frame_ledger()["F2_status"].startswith("requires")


def test_Einstein_frame_weyl_factor():
    for tau in (-1, 1):
        assert sp.simplify(
            reduction.omega_squared(tau)
            - reduction.frame_function(tau) / reduction.frame_F0()
        ) == 0
        assert reduction.omega_linear(tau).subs(reduction.Q, 0) == 1


def test_constant_Einstein_Planck_coefficient():
    ledger = reduction.frame_ledger()
    assert ledger["Einstein_metric"] == "g_E=(F/F0)h"
    assert ledger["Einstein_Planck_coefficient"] == "M4^2=F0=pi/2"


def test_Weyl_kinetic_contribution_is_exact_and_positive():
    expected = 3 * reduction.CHI_1**2 * (4 - sp.pi) ** 2 / (16 * sp.pi)
    for tau in (-1, 1):
        value = reduction.weyl_kinetic_at_fold(tau)
        assert sp.simplify(value - expected) == 0
        assert value.is_positive


def test_radial_and_M4_scalar_gauge_transformations_are_recorded():
    gauge = reduction.gauge_ledger()
    assert gauge["radial_parameter"] == "xi^rho(x,t)"
    assert "nabla^mu xi" in gauge["M4_scalar_parameter"]
    assert "xi^rho" in gauge["transformations"]["lapse_A"]
    assert "partial_t xi" in gauge["transformations"]["shift_B"]
    assert gauge["transformations"]["longitudinal_E"] == "E-xi"


def test_endpoint_and_X_gauge_audit():
    gauge = reduction.gauge_ledger()
    assert gauge["transformations"]["endpoint"] == "delta rho_J-xi^rho|J"
    assert "invariant" in gauge["transformations"]["delta_X"]
    assert gauge["fold_not_pure_gauge"] == "delta X=tau chi_1 is intrinsic"


def test_no_gauge_kernel_is_inverted():
    gauge = reduction.gauge_ledger()
    assert gauge["gauge_kernel_inverted"] is False
    assert gauge["complete_gauge_fixed"] is False


def test_radial_ADM_ansatz_includes_shift():
    constraints = reduction.adm_constraint_ledger()
    assert "N^mu" in constraints["ADM_metric"]
    assert any("radial shift" in item for item in constraints["scalar_variables"])


def test_Hamiltonian_and_momentum_constraints_are_present():
    constraints = reduction.adm_constraint_ledger()
    assert constraints["Hamiltonian"].startswith("delta_N S=0")
    assert constraints["momentum"].startswith("D_nu")


def test_exact_static_Hubble_variation():
    expected = reduction.CHI_1 * reduction.T / (
        4 * sp.sin(sp.pi * reduction.T / 4) ** 2
    )
    assert sp.simplify(reduction.static_hubble1() - expected) == 0


@pytest.mark.parametrize("tau", [-1, 1])
def test_zero_shift_momentum_constraint_mismatch(tau):
    expected = -3 * tau * reduction.CHI_1 * reduction.T / (
        4 * sp.sin(sp.pi * reduction.T / 4) ** 2
    )
    assert sp.simplify(
        reduction.momentum_constraint_zero_shift_mismatch(tau) - expected
    ) == 0


def test_zero_shift_is_not_admissible():
    constraints = reduction.adm_constraint_ledger()
    assert constraints["critical_scalar_flux"] == 0
    assert constraints["zero_shift_admissible"] is False


def test_lapse_shift_and_endpoint_solutions_are_not_invented():
    constraints = reduction.adm_constraint_ledger()
    assert constraints["lapse_solution"] is None
    assert constraints["shift_solution"] is None
    assert constraints["endpoint_compensator"] is None


def test_exact_missing_boundary_condition_is_named():
    constraints = reduction.adm_constraint_ledger()
    assert "scalar radial-shift" in constraints["missing_boundary_condition"]
    assert "moving B1 endpoint" in constraints["missing_boundary_condition"]
    assert constraints["unique_constraint_inverse"] is False
    assert constraints["result"] == reduction.PRIMARY_RESULT


def test_boundary_flux_cancellation_remains_unproved():
    assert reduction.adm_constraint_ledger()["boundary_flux_cancellation"] is None


def test_scalar_Jordan_contribution_is_preserved():
    jordan = reduction.jordan_moduli_ledger()
    assert ">=2" in jordan["K_scalar"]


def test_all_gravity_boundary_constraint_contributions_are_classified():
    jordan = reduction.jordan_moduli_ledger()
    for key in ("K_EH", "K_GHY", "K_B1", "K_constraint", "K_endpoint"):
        assert key in jordan
        assert jordan[key]


def test_no_gauge_dependent_partial_sum_is_promoted():
    jordan = reduction.jordan_moduli_ledger()
    assert "gauge dependent separately" in jordan["cancellations"]
    assert jordan["total_K_J"] is None
    assert jordan["hidden_normalization_to_one"] is False


def test_Einstein_kinetic_formula():
    einstein = reduction.einstein_kinetic_ledger()
    assert einstein["Weyl_formula"] == "k_E=(F0/F)K_J+(3F0/2)(F'/F)^2"
    assert "K_scalar" in einstein["total"]
    assert "K_shift_endpoint_red" in einstein["total"]


def test_total_Einstein_kinetic_sign_is_unresolved():
    einstein = reduction.einstein_kinetic_ledger()
    assert einstein["sign"] is None
    assert einstein["positive_norm_certified"] is False
    assert einstein["ghost_certified"] is False
    assert einstein["zero_or_nondynamical_certified"] is False
    assert einstein["result"] == reduction.PRIMARY_RESULT


def test_formal_Einstein_potential_hessian():
    expected = (
        reduction.V2
        - 4 * sp.Symbol("F_1", real=True) * reduction.V1 / reduction.frame_F0()
        + (
            6 * sp.Symbol("F_1", real=True) ** 2 / reduction.frame_F0() ** 2
            - 2 * reduction.F2 / reduction.frame_F0()
        )
        * reduction.V0
    )
    assert sp.simplify(reduction.einstein_potential_hessian_formula() - expected) == 0


def test_v6_11_Gamma_is_not_silently_called_Jordan_potential():
    potential = reduction.potential_ledger()
    assert potential["is_offshell_V_J"] is False
    assert "on-shell regulated action" in potential["frame_classification"]


def test_Einstein_potential_inputs_are_named_exactly():
    potential = reduction.potential_ledger()
    assert potential["missing_inputs"] == [
        "off-shell Jordan coefficients V0,V1,V2 before the X equation",
        "F2 from a2,N2 and moving-endpoint response",
    ]
    assert potential["result"] == reduction.POTENTIAL_RESULT


def test_no_Einstein_curvature_or_mass_is_manufactured():
    potential = reduction.potential_ledger()
    assert potential["B_ext_E"] is None
    assert potential["B_core_E"] is None
    assert potential["canonical_mass_ext"] is None
    assert potential["canonical_mass_core"] is None


def test_physical_classification_is_case_E():
    verdict = reduction.verdict_ledger()
    assert verdict["case"] == "E"
    assert verdict["tachyon"] is False
    assert verdict["ghost"] is False
    assert verdict["gauge"] is False
    assert verdict["nondynamical"] is False
    assert verdict["Morse_index_lower_bound"] is None


def test_invariant_sheet_map_is_preserved():
    verdict = reduction.verdict_ledger()
    assert verdict["sheet_map"] == "sign(X-2)=tau unchanged"
    assert "no sheet is rejected" in verdict["sheet_selection_consequence"]


def test_exact_next_construction_uses_no_new_term():
    integrity = reduction.integrity_ledger()
    assert integrity["new_action_terms"] == []
    assert integrity["new_primitives"] == []
    assert "radial-shift Green function" in integrity["next_construction"]


def test_integrity_guards():
    for payload in reduction.artifact_payloads().values():
        assert payload["new_action_term_introduced"] is False
        assert payload["tau_J_introduced"] is False
        assert payload["new_primitive_introduced"] is False
        assert payload["neutral_transport_used"] is False
        assert payload["fermion_loop_introduced"] is False
        assert payload["measured_inputs_used"] is False
        assert payload["physical_bulk_Dirac_law_introduced"] is False
        assert payload["lambda_geom_changed"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["sheet_map_changed"] is False


def test_exactly_six_deterministic_artifacts():
    expected = reduction.artifact_bytes()
    assert len(expected) == 6
    assert set(expected) == set(reduction.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = reduction.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
