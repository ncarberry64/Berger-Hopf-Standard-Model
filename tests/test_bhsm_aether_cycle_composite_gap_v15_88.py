from bhsm.interface.aether_cycle_composite_gap_v15_88 import (
    completion_payload,
    cycle_gap_rows,
    cycle_gap_theorem,
)


def test_same_cycle_gap_operator_is_positive_and_strictly_subcritical():
    rows = cycle_gap_rows()
    assert all(0.0 < row["gap_operator_at_zero"] < 1.0e-3 for row in rows)
    assert all(row["composite_quadratic_coefficient"] > 100.0 for row in rows)


def test_monotone_susceptibility_excludes_nonzero_gap_solution():
    theorem = cycle_gap_theorem()
    assert theorem["instantaneous_gap_operator_envelope"][1] < 7.1e-5
    assert theorem["PCHIP_cycle_average_gap_operator"] < 7.0e-5
    assert theorem["nonzero_gap_solution_exists"] is False
    assert theorem["cycle_composite_background"] == 0.0
    assert theorem["cycle_Yukawa_vertex_nonzero"] is True


def test_payload_validates_one_unsplit_pushforward():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["no_split_normalization"]
    assert payload["claim_boundary"]["nonzero_fermion_mass_derived"] is False
