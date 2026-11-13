from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))
from fractions import Fraction
import pytest
from bhsm_muon_n1_ramp_time_control_20261015 import exact_midpoint_ramp_derivative_integral


def test_rational_ramp_bias_at_all_bounded_rules():
    for m in (1,2,3,4,5,8,16):
        assert exact_midpoint_ramp_derivative_integral(m)==1+Fraction(7,8*m**4)


def test_no_spurious_second_order_term_or_zero_bias():
    a=exact_midpoint_ramp_derivative_integral(2)-1
    b=exact_midpoint_ramp_derivative_integral(4)-1
    c=exact_midpoint_ramp_derivative_integral(8)-1
    assert a==Fraction(7,128) and a/b==b/c==16
    with pytest.raises(ValueError):exact_midpoint_ramp_derivative_integral(0)
