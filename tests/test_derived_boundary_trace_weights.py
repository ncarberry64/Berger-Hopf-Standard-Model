import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_boundary_hypercharge_rows_and_multiplicities():
    assert trace.channel_multiplicity(0) == 1
    assert trace.channel_multiplicity(1) == 3
    assert trace.active_Y(0) == Fraction(-1)
    assert trace.active_Y(1) == Fraction(1, 3)
    assert trace.conjugate_inactive_Y(0, 1) == Fraction(0)
    assert trace.conjugate_inactive_Y(0, -1) == Fraction(2)
    assert trace.conjugate_inactive_Y(1, 1) == Fraction(-4, 3)
    assert trace.conjugate_inactive_Y(1, -1) == Fraction(2, 3)

    with pytest.raises(ValueError):
        trace.channel_multiplicity(2)
    with pytest.raises(ValueError):
        trace.inactive_Y(0, 0)


def test_exact_boundary_trace_weights():
    assert isinstance(trace.active_hypercharge_trace_contribution(), Fraction)
    assert isinstance(trace.inactive_hypercharge_trace_contribution(), Fraction)
    assert trace.active_hypercharge_trace_contribution() == Fraction(2, 3)
    assert trace.inactive_hypercharge_trace_contribution() == Fraction(8, 3)
    assert trace.K1_hypercharge_trace_weight() == Fraction(10, 3)
    assert trace.K2_orientation_trace_weight() == Fraction(2, 1)
    assert trace.K3_cyclic_trace_weight() == Fraction(2, 1)


def test_trace_weight_documentation():
    trace.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_trace_weights.md").read_text(encoding="utf-8")
    assert "K1 = 2/3 + 8/3 = 10/3" in text
    assert "K2 = (1+3)*(1/2) = 2" in text
    assert "K3 = 4*(1/2) = 2" in text
    assert "BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL" in text
