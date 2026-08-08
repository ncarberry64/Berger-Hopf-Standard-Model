from fractions import Fraction

from bhsm.interface.completion.completion_minimum_input_v14_48 import (
    PRIMARY_VERDICT,
    channel_counterterm_determinant,
    channel_counterterm_matrix,
    completion_payload,
    continuous_effective_inputs,
    einstein_matching_matrix,
    internal_constraint_witnesses,
    matrix_rank_2x2,
    solve_einstein_matching,
)


def test_counterterm_projection_is_rank_two():
    assert channel_counterterm_matrix() == ((5, 25), (12, 144))
    assert channel_counterterm_determinant() == 420
    assert matrix_rank_2x2(channel_counterterm_matrix()) == 2


def test_current_internal_constraints_do_not_fix_two_coefficients():
    witnesses = internal_constraint_witnesses()
    assert [w.rank for w in witnesses] == [0, 0, 1]
    assert max(w.rank for w in witnesses) < 2


def test_einstein_matching_is_a_full_rank_declared_scheme():
    assert einstein_matching_matrix() == ((0, 1), (3, 1))
    assert matrix_rank_2x2(einstein_matching_matrix()) == 2
    assert solve_einstein_matching() == (Fraction(0), Fraction(0))


def test_minimum_effective_input_ledger_is_explicit():
    rows = continuous_effective_inputs()
    assert len(rows) == 4
    assert {row["input"] for row in rows} == {
        "c_R2^ren(mu_star)",
        "c_Ricci2^ren(mu_star)",
        "c_YM(mu_star)",
        "L_star_or_equivalent_scale",
    }


def test_payload_fails_closed():
    payload = completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["validation_passed"] is True
    assert payload["physical_completion"] is False
    assert payload["zero_input_completion_supported"] is False
    assert payload["effective_completion_available_without_new_author_declarations"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["usb_touched"] is False
