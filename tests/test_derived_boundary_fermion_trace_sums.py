import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_fermion_trace_sums_and_beta_are_exact():
    assert rg.fermion_trace_sums_one_generation() == (
        Fraction(2),
        Fraction(2),
        Fraction(2),
    )
    one = rg.fermion_beta_one_generation()
    assert one.as_tuple() == (Fraction(4, 3), Fraction(4, 3), Fraction(4, 3))
    assert rg.number_of_boundary_generations() == 3
    all_gen = rg.fermion_beta_all_generations()
    assert all_gen.as_tuple() == (Fraction(4), Fraction(4), Fraction(4))


def test_fermion_trace_sum_documentation():
    rg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_fermion_trace_sums.md").read_text(
        encoding="utf-8"
    )
    assert "b_f/gen = (2/3)*(2,2,2) = (4/3,4/3,4/3)" in text
    assert "b_f = 3*(4/3,4/3,4/3) = (4,4,4)" in text
    assert "BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL" in text
