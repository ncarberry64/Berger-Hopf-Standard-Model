import math

from bhsm.interface.gauge_coupling_spectral_residue import candidate_lambda_reference
from bhsm.interface.sector_boundary_operator import (
    ACTS_ON,
    FRAME_COUNT,
    PRINCIPAL_SYMBOL,
    candidate_operator_table,
    effective_frame_normalized_residue,
    frame_normalized_principal_residue_table,
    has_laplace_type_principal_symbol,
    sector_boundary_operator_candidate,
)


def test_v4_5_dimensions_residues_weyl_and_lambdas_do_not_drift():
    table = frame_normalized_principal_residue_table()
    assert [table[s]["gauge_algebra_dimension"] for s in ("U1", "SU2", "SU3")] == [1, 3, 8]
    assert [table[s]["active_residue"] for s in ("U1", "SU2", "SU3")] == [1, 2, 7]
    assert candidate_lambda_reference("U1") == 1.0 / (6.0 * math.pi**2)
    assert [table[s]["lambda_reference"] for s in table] == [candidate_lambda_reference(s) for s in table]
    assert all(row["is_gauge_boson_count"] is False for row in table.values())


def test_candidate_acts_on_adjoint_one_forms_and_has_laplace_symbol():
    for candidate in (sector_boundary_operator_candidate(s) for s in ("U1", "SU2", "SU3")):
        assert candidate.acts_on == ACTS_ON
        assert candidate.principal_symbol == PRINCIPAL_SYMBOL
        assert has_laplace_type_principal_symbol(candidate)
        assert "Hodge-de Rham" in candidate.operator_family
        assert "Berger boundary metric" in candidate.berger_hodge_relation
    assert set(candidate_operator_table()) == {"U1", "SU2", "SU3"}


def test_frame_state_cancels_raw_one_form_rank_without_closing_action_average():
    assert FRAME_COUNT == 3
    assert [effective_frame_normalized_residue(s) for s in ("U1", "SU2", "SU3")] == [1.0, 2.0, 7.0]
    table = frame_normalized_principal_residue_table()
    assert all(row["effective_frame_factor"] == 1.0 for row in table.values())
