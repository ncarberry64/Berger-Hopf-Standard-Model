import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_wigner_y0_formula_contains_phase_reduced_phase_factors():
    expr = gy0.wigner_y0_expression(Fraction(5, 2), Fraction(1, 2), Fraction(1, 2))
    assert "exp(-i*1/2*alpha0)" in expr
    assert "d^(5/2)_(1/2,1/2)(beta0)" in expr
    assert "exp(-i*1/2*gamma0)" in expr


def test_core_formula_uses_k_over_2_and_q_over_2():
    assert gy0.core_formula() == "D^{k/2}_{m,q/2}(y0)=exp(-i*m*alpha0)*d^{k/2}_{m,q/2}(beta0)*exp(-i*(q/2)*gamma0)"
