from fractions import Fraction as F
import numpy as np
import pytest
from flint import arb, ctx, fmpq
from bhsm.interface.direct_physical_hs_jacobian import physical_hs_blocks, fixed_frame_pullback


def exact(q):
    q = F(q)
    return arb(fmpq(q.numerator, q.denominator))


def contains_rational(ball, q):
    center, radius = F(str(ball.mid().fmpq())), F(str(ball.rad().fmpq()))
    return center-radius <= q <= center+radius


def test_nonlinear_scalar_hs_derivative_matches_independent_polynomial():
    # f(z)=z^2, h=3/8: differentiate the expanded residual as a polynomial
    # with sympy, independently of the implemented Jacobian block formula.
    import sympy as sp
    a,b=sp.symbols('a b')
    h=sp.Rational(3,8)
    midpoint=(a+b)/2+h*(a*a-b*b)/8
    residual=sp.expand(b-a-h*(a*a+4*midpoint**2+b*b)/6)
    left,right=sp.Rational(2,3),sp.Rational(7,5)
    middle=midpoint.subs({a:left,b:right})
    blocks=physical_hs_blocks([[exact(2*F(str(left)))]],[[exact(2*F(str(middle)))]],
                             [[exact(2*F(str(right)))]],exact(F(3,8)))
    for name,symbol in [('residual_left',a),('residual_right',b)]:
        expected=sp.diff(residual,symbol).subs({a:left,b:right})
        assert contains_rational(blocks[name][0,0], F(str(expected)))


def test_nonsymmetric_matrix_order_matches_exact_linear_ode():
    # The midpoint DF deliberately differs and does not commute with endpoint
    # DF. An accidental reversal of products cannot pass this comparison.
    a=np.array([[1,2],[0,3]],dtype=object)
    m=np.array([[2,0],[4,1]],dtype=object)
    b=np.array([[0,3],[2,1]],dtype=object)
    blocks=physical_hs_blocks(a,m,b,exact(F(1,2)))
    eye=np.eye(2,dtype=int).astype(object)
    ml=eye*F(1,2)+a*F(1,16)
    mr=eye*F(1,2)-b*F(1,16)
    expected={'midpoint_left':ml,'midpoint_right':mr,
              'residual_left':-eye-a*F(1,12)-(m@ml)*F(1,3),
              'residual_right':eye-b*F(1,12)-(m@mr)*F(1,3)}
    for name,array in expected.items():
        for i,j in np.ndindex(array.shape):
            assert contains_rational(blocks[name][i,j], array[i,j])


def test_input_uncertainty_encloses_all_scalar_corner_derivatives():
    result=physical_hs_blocks([[arb(2,1)]],[[arb(4,1)]],[[arb(1,1)]],exact(F(1,2)))
    for a in (1,3):
        for m in (3,5):
            for b in (0,2):
                point=physical_hs_blocks([[a]],[[m]],[[b]],exact(F(1,2)))
                assert all(result[k][0,0].contains(point[k][0,0]) for k in result)


def test_fixed_frame_pullback_preserves_nonorthogonal_frames():
    d=[[2,1],[0,3]]
    trial=[[1],[2]]
    test=[[3,4]]
    result=fixed_frame_pullback(d,trial,test,[[2]])
    assert result[0,0] == 18
    with pytest.raises(ArithmeticError):
        fixed_frame_pullback(d,trial,test,[[0]])
    block=physical_hs_blocks([[0]],[[0]],[[0]],1)['residual_left']
    assert fixed_frame_pullback(block,[[2]],[[3]],[[2]])[0,0] == -3


def test_invalid_inputs_fail_and_restore_precision():
    previous=ctx.prec
    for df,h in [([[arb('nan')]],1),([[1]],arb(1,1)),([[1]],0),([[1,2]],1)]:
        with pytest.raises(ValueError):
            physical_hs_blocks(df,df,df,h)
        assert ctx.prec == previous
    with pytest.raises(ValueError):
        fixed_frame_pullback([[1]],[[1]],[[1,2]],[[1]])
    assert ctx.prec == previous
