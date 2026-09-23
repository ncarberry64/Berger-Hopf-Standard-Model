from fractions import Fraction
import pytest
from flint import arb, ctx
from bhsm.interface.exact_arb_ball_restore import restore_exact_ball


def test_saved_balls_retain_both_exact_endpoints():
    old = ctx.prec
    ctx.prec = 512
    try:
        values = [arb(0), arb(1)/3, (arb(7)/13).exp(), arb((123456789, -500), (987654321, -900)),
                  arb((-7, 900), (1, 100)), arb(0, (1, -900))]
        for original in values:
            m, r = [Fraction(str(v.fmpq())) for v in (original.mid(), original.rad())]
            restored = restore_exact_ball(str(m), str(r))
            mm, rr = [Fraction(str(v.fmpq())) for v in (restored.mid(), restored.rad())]
            assert (mm-rr, mm+rr) == (m-r, m+r)
    finally:
        ctx.prec = old


def test_rejects_nonrepresentable_input_instead_of_relaxing_it():
    with pytest.raises(ValueError):
        restore_exact_ball('1/3', '0')
    with pytest.raises(ValueError):
        restore_exact_ball('0', '-1')
    with pytest.raises(ValueError):
        restore_exact_ball('0', str(2**31+1))
