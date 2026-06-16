import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_scalar_trace_sums_and_beta_are_exact():
    assert rg.scalar_trace_sums_active_doublet() == (
        Fraction(3, 10),
        Fraction(1, 2),
        Fraction(0),
    )
    scalar = rg.scalar_beta_active_doublet()
    assert scalar.as_tuple() == (Fraction(1, 10), Fraction(1, 6), Fraction(0))


def test_scalar_trace_sum_documentation():
    rg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_scalar_trace_sums.md").read_text(
        encoding="utf-8"
    )
    assert "sum_s T1 = 2*(3/5)*(1/2)^2 = 3/10" in text
    assert "b1_scalar = (1/3)*(3/10) = 1/10" in text
    assert "b_scalar = (1/10,1/6,0)" in text
    assert "conditional scalar-sector input" in text
    assert "BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL" in text
