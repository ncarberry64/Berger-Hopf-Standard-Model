from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb,ctx,fmpq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_physical_midpoint_incidence_errors as producer


def contains_rational(ball,value):
    exact=fmpq(value.numerator,value.denominator)
    return ball.lower().fmpq()<=exact<=ball.upper().fmpq()


def test_surjective_recovery_and_inconsistent_extra_column_detection():
    old=ctx.prec;ctx.prec=512
    try:
        m=np.array([[arb(1),arb(0),arb(2)],[arb(0),arb(1),arb(-1)]],dtype=object)
        derivative=producer.cert._mat(np.array([[1.5,-2.],[0.25,3.]]))
        image=producer.cert._array(derivative*producer.cert._arb_mat_from_array(m))
        recovered,inverse_error=producer.recover_ambient(m,image,np.array([0,2]))
        assert inverse_error<1
        for i,j in np.ndindex((2,2)):assert recovered[i,j].contains(derivative[i,j])
        image[0,1]+=arb(1)
        with pytest.raises(ArithmeticError):producer.recover_ambient(m,image,np.array([0,2]))
        with pytest.raises(ValueError):producer.recover_ambient(m,image,np.array([0,0]))
    finally:ctx.prec=old


def test_signed_physical_incidence_is_not_lost_below_binary64_resolution():
    old=ctx.prec;ctx.prec=512
    try:
        derivative=producer.cert._arb_mat_from_array(np.array([[arb(4)+arb(2)**-90]],dtype=object))
        stored=np.array([[[-0.25]],[[0.]]])
        arrays,bounds=producer.output_errors(np.array([[2.]]),np.array([[3.]]),derivative,0.5,stored)
        for label,sign in (('left',-1),('right',1)):
            expected=sign*Fraction(1,2**95)
            ball=arb(float(arrays[label+'_output_error_mid'][0,0]),float(arrays[label+'_output_error_radius'][0,0]))
            assert contains_rational(ball,expected)
            assert Fraction(bounds[label]['operator_error_upper'])>=abs(expected)
    finally:ctx.prec=old


def test_singular_direction_square_cannot_be_used_as_a_derivative():
    m=np.array([[arb(1),arb(2)],[arb(2),arb(4)]],dtype=object)
    with pytest.raises(ArithmeticError):producer.recover_ambient(m,m,np.array([0,1]))
