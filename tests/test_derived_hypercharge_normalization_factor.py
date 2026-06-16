import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_hypercharge_normalization_factor_exact():
    assert trace.eta_Y_normalization_factor() == Fraction(3, 5)
    assert trace.normalized_K1() == Fraction(2, 1)
    assert trace.trace_weights_unify_after_eta() is True
    assert trace.coupling_convention_g1_squared_over_gY_squared() == Fraction(5, 3)


def test_hypercharge_normalization_documentation():
    trace.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_hypercharge_normalization_factor.md").read_text(
        encoding="utf-8"
    )
    assert "eta_Y = K2/K1 = 3/5" in text
    assert "eta_Y*K1 = K2 = K3" in text
    assert "g1^2 = (5/3) gY^2" in text
    assert "not a measured coupling prediction" in text
    assert "BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL" in text
