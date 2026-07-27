from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface import junction_eft_sheet_index_closure as closure


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def projectors():
    return closure.light_projector(), closure.heavy_projector()


def test_light_projector_idempotent(projectors):
    p_l, _ = projectors
    assert p_l * p_l == p_l
    assert p_l.rank() == 3


def test_heavy_projector_idempotent(projectors):
    _, p_h = projectors
    assert p_h * p_h == p_h
    assert p_h.rank() == 3


def test_projectors_are_orthogonal_and_complete(projectors):
    p_l, p_h = projectors
    assert p_l * p_h == sp.zeros(6)
    assert p_h * p_l == sp.zeros(6)
    assert p_l + p_h == sp.eye(6)


def test_truncated_basis_is_complete_and_neutral():
    basis = closure.basis_ledger()
    assert len(basis["basis_order"]) == 6
    assert basis["charge"] == 0
    assert basis["Q_em"].startswith("zero")
    assert basis["Y_BH"].startswith("zero")
    assert basis["arbitrary_neutral_mixing_matrix"] is False


def test_triality_action_is_unitary_and_preserves_blocks(projectors):
    cycle = closure.triality_cycle()
    p_l, p_h = projectors
    assert cycle.T * cycle == sp.eye(6)
    assert cycle**3 == sp.eye(6)
    assert cycle * p_l == p_l * cycle
    assert cycle * p_h == p_h * cycle


def test_available_operator_is_hermitian():
    operator = closure.full_truncated_operator(0)
    assert operator == operator.T.conjugate()
    assert operator.is_hermitian


def test_junction_extended_operator_is_hermitian():
    operator = closure.full_truncated_operator(closure.J_J)
    assert operator == operator.T.conjugate()
    assert operator.is_hermitian


def test_available_light_heavy_block_is_exactly_zero():
    blocks = closure.static_blocks(0)
    assert blocks["V_LH"] == sp.zeros(3)
    assert blocks["V_HL"] == sp.zeros(3)
    assert closure.available_light_heavy_result()["V_LH_is_zero"]


def test_V_HL_is_the_adjoint_of_V_LH():
    blocks = closure.static_blocks(closure.J_J)
    assert blocks["V_HL"] == blocks["V_LH"].T.conjugate()


def test_missing_junction_overlap_is_one_universal_scalar():
    blocks = closure.static_blocks(closure.J_J)
    assert blocks["V_LH"] == closure.J_J * sp.eye(3)
    result = closure.available_light_heavy_result()
    assert "j_J=<f0,C_junction f1>" in result["missing_invariant"]
    assert "triality-singlet" in result["missing_invariant_symmetry"]


def test_selection_rule_zeros_are_exact_or_named():
    rows = closure.selection_rule_table()
    assert len(rows) == 7
    junction = next(row for row in rows if row["term"] == "C_junction")
    assert junction["matrix_element"] == "j_J I_3"
    for row in rows:
        if row is not junction:
            assert row["matrix_element"].startswith("0")


def test_heavy_gap_is_positive_by_declared_symbol():
    assert closure.M_H.is_positive
    blocks = closure.static_blocks(0)
    assert sp.simplify(blocks["H_HH"][0, 0] - blocks["H_LL"][0, 0]) == closure.M_H


def test_schur_complement_identity():
    blocks = closure.static_blocks(closure.J_J)
    expected = (
        blocks["H_LL"]
        - closure.E * sp.eye(3)
        - blocks["V_LH"]
        * (blocks["H_HH"] - closure.E * sp.eye(3)).inv()
        * blocks["V_HL"]
    )
    assert sp.simplify(expected - closure.schur_inverse_operator()) == sp.zeros(3)


def test_resolvent_domain_excludes_the_heavy_pole():
    denominator = closure.P + closure.M_H - closure.E
    assert denominator.subs(closure.E, closure.P + closure.M_H) == 0
    ledger = closure.schur_ledger()
    assert ledger["resolvent_domain"] == "E not equal to p+M_H"
    assert "<<" in ledger["controlled_regime"]


def test_resolvent_expansion_is_controlled():
    delta = sp.symbols("delta", real=True)
    series = sp.series(1 / (closure.M_H - delta), delta, 0, 3).removeO()
    expected = (
        1 / closure.M_H
        + delta / closure.M_H**2
        + delta**2 / closure.M_H**3
    )
    assert sp.simplify(series - expected) == 0


def test_exact_light_dispersion_solves_reduced_equation():
    equation = closure.schur_inverse_operator()[0, 0]
    assert sp.simplify(equation.subs(closure.E, closure.light_energy())) == 0


def test_light_root_connects_to_massless_dispersion():
    assert closure.light_energy().subs(closure.J_J, 0) == closure.P


def test_leading_energy_shift_is_E0_not_inverse_momentum():
    shift = closure.light_energy_shift_series()
    assert shift == -closure.J_J**2 / closure.M_H + closure.J_J**4 / closure.M_H**3
    assert closure.P not in shift.free_symbols
    assert closure.schur_ledger()["energy_scaling"].startswith("E^0")


def test_schur_response_is_channel_universal():
    operator = closure.schur_inverse_operator()
    assert operator[0, 0] == operator[1, 1] == operator[2, 2]
    assert all(operator[i, j] == 0 for i in range(3) for j in range(3) if i != j)


def test_K_prop_is_not_manufactured():
    ledger = closure.schur_ledger()
    assert ledger["K_prop_defined"] is False
    assert "no kappa_i/(2p)" in ledger["reason_no_K_prop"]
    assert ledger["relative_neutral_phase"].startswith("zero")


def test_available_operator_has_no_schur_response():
    ledger = closure.schur_ledger()
    assert ledger["available_operator_j_J"] == 0
    assert ledger["available_operator_delta_E"] == 0


def test_schur_dimensional_consistency():
    ledger = closure.schur_ledger()
    assert ledger["leading_term_dimension"] == "mass: [j_J]^2/[M_H]"


def test_gate_b_physical_hessians_are_hermitian():
    for sheet in (-1, 1):
        hessian = closure.physical_hessian(sheet)
        assert hessian == hessian.T.conjugate()


def test_gate_b_known_kinetic_subblock_is_positive():
    metric = closure.physical_kinetic_metric()
    assert metric[:2, :2] == sp.diag(1, sp.Rational(6, 7))
    assert metric.det() == sp.Rational(6, 7) * closure.K_B
    assert closure.K_B.is_positive


def test_gate_b_witness_has_positive_conditional_kinetic_norm():
    witness = closure.bending_witness()
    norm = (witness.T * closure.physical_kinetic_metric() * witness)[0]
    assert norm == closure.K_B
    assert norm.is_positive


def test_gate_b_exact_lower_rayleigh_quotient():
    assert closure.bending_rayleigh(-1) == closure.B_MINUS / closure.K_B


def test_gate_b_exact_upper_rayleigh_quotient():
    assert closure.bending_rayleigh(1) == closure.B_PLUS / closure.K_B


def test_gate_b_does_not_infer_instability_from_constraint_block():
    ledger = closure.sheet_kill_ledger()
    assert "no determinant sign is used" in ledger["gauge_null_handling"]
    assert ledger["lower_sheet_rejected"] is False
    assert ledger["existing_repository_value"] is None


def test_gate_b_distinguishes_tachyon_ghost_and_artifact():
    ledger = closure.sheet_kill_ledger()
    assert ledger["tachyon_condition"] != ledger["ghost_condition"]
    assert "gauge kernel" in ledger["constraint_artifact_condition"]


def test_gate_b_names_exact_missing_invariant():
    ledger = closure.sheet_kill_ledger()
    assert ledger["result"] == closure.GATE_B_RESULT
    assert "H_PP-H_PC H_CC^(-1)H_CP" in ledger["missing_invariant"]
    assert ledger["nonnegative_small_trial_proves_full_stability"] is False


def test_callias_principal_symbol_is_elliptic():
    symbol = closure.callias_symbol()
    assert sp.factor(symbol.det()) == -closure.XI**2
    assert symbol.det() != 0


def test_callias_not_APS_is_the_declared_decision():
    ledger = closure.callias_index_ledger()
    assert ledger["Callias_applicable"] is True
    assert ledger["APS_applicable"] is False
    assert "eta invariant" in ledger["APS_reason"]


def test_callias_fredholm_conditions_are_explicit():
    ledger = closure.callias_index_ledger()
    assert ledger["Fredholm"] is True
    assert len(ledger["Callias_conditions"]) == 4
    assert any("m_minus<0<m_plus" in row for row in ledger["Callias_conditions"])


def test_auxiliary_index_one_and_triality_total():
    ledger = closure.callias_index_ledger()
    assert ledger["index_per_selected_slot"] == 1
    assert ledger["triality_total_index"] == 3
    assert ledger["result"] == closure.GATE_C_RESULT


def test_index_and_total_kernel_are_distinguished():
    ledger = closure.callias_index_ledger()
    assert ledger["kernel_A_adjoint"] == 0
    assert ledger["paired_zero_modes_excluded"].startswith("yes for the rank-one")
    assert ledger["compact_cap_physical_domain_selected"] is False
    assert ledger["physical_index_claimed"] is False


def test_callias_result_matches_compact_diagnostic_only_conditionally():
    ledger = closure.callias_index_ledger()
    assert "v6.7 diagnostic index one" in ledger["comparison"]
    assert "magnitude does not change the index" in ledger["lambda_geom_status"]


def test_no_physical_bulk_Dirac_parent_law():
    ledger = closure.callias_index_ledger()
    assert ledger["role"].endswith("not a physical bulk Dirac law")
    payload = closure.artifact_payloads()["index"]
    assert payload["physical_bulk_Dirac_parent_law_introduced"] is False


def test_lambda_geom_remains_universal_primitive():
    hidden = closure.artifact_payloads()["hidden"]
    assert hidden["lambda_geom"] == "one universal dimensionless primitive"
    assert hidden["lambda_geom_set_to_one"] is False
    assert hidden["sector_dependent_coupling_introduced"] is False


def test_hidden_input_integrity():
    hidden = closure.artifact_payloads()["hidden"]
    assert hidden["new_fitted_parameters"] == []
    assert hidden["measured_inputs"] == []
    assert hidden["arbitrary_neutral_mixing_matrix"] is False
    assert hidden["K_prop_manufactured"] is False
    assert hidden["lower_sheet_selection_manufactured"] is False


def test_frozen_and_official_logic_unchanged():
    report = closure.artifact_payloads()["report"]
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["measured_derivation_input_used"] is False


def test_exactly_six_deterministic_artifacts():
    assert len(closure.ARTIFACT_FILES) == 6
    assert len(closure.artifact_bytes()) == 6


def test_materialization_is_byte_deterministic(tmp_path):
    first = closure.materialize_artifacts(tmp_path)
    first_bytes = {path.name: path.read_bytes() for path in first}
    second = closure.materialize_artifacts(tmp_path)
    second_bytes = {path.name: path.read_bytes() for path in second}
    assert first_bytes == second_bytes == closure.artifact_bytes()


def test_committed_artifacts_match_materializer():
    expected = closure.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
