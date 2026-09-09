from itertools import product
import pytest
import sympy as sp
from flint import arb, arb_mat, ctx, fmpq
from bhsm.interface.direct_physical_hs_second_variation import (
    physical_hs_second_residual, frozen_newton_quadratic_source,
)


@pytest.fixture(autouse=True)
def reference_precision():
    # Reference rational enclosures must be tighter than the 512-bit result;
    # a default 53-bit reference ball need not fit inside a sharper enclosure.
    previous = ctx.prec
    ctx.prec = 768
    try:
        yield
    finally:
        ctx.prec = previous


def matrix(exact):
    return arb_mat(exact.rows, exact.cols, [arb(fmpq(str(v))) for v in exact])


def test_vector_nonlinear_hs_matches_independent_symbolic_hessian():
    x,y,a,b = variables = sp.symbols('x y a b')
    z0,z1 = sp.Matrix([x,y]),sp.Matrix([a,b])
    def rate(z):
        p,q = z
        return sp.Matrix([p*p+p*q, p-q**3])
    h = sp.Rational(1,4)
    midpoint = (z0+z1)/2+h*(rate(z0)-rate(z1))/8
    residual = z1-z0-h*(rate(z0)+4*rate(midpoint)+rate(z1))/6
    point = dict(zip(variables,[sp.Rational(1,2),sp.Rational(-1,4),1,sp.Rational(1,4)]))
    physical_midpoint = midpoint.subs(point)
    rate_hessians = [sp.hessian(f,(x,y)) for f in rate(z0)]
    df = rate(z0).jacobian(z0).subs(dict(zip((x,y),physical_midpoint)))
    dm = midpoint.jacobian(variables).subs(point)
    pairs = [(sp.eye(4)[:,i],sp.eye(4)[:,j]) for i,j in ((0,0),(0,3),(2,3))]
    pairs += [(sp.Matrix([1,2,-1,1]),sp.Matrix([-2,1,3,-1]))]
    left,middle,right = [],[],[]
    expected_r,expected_m = [],[]
    def contraction(hessians, u,v, substitutions):
        return sp.Matrix([(u.T*H.subs(substitutions)*v)[0] for H in hessians])
    for u,v in pairs:
        left.append(contraction(rate_hessians,u[:2,0],v[:2,0],point))
        right.append(contraction(rate_hessians,u[2:,0],v[2:,0],{x:point[a],y:point[b]}))
        middle.append(contraction(rate_hessians,dm*u,dm*v,dict(zip((x,y),physical_midpoint))))
        expected_r.append(contraction([sp.hessian(f,variables) for f in residual],u,v,point))
        expected_m.append(contraction([sp.hessian(f,variables) for f in midpoint],u,v,point))
    result = physical_hs_second_residual(*[matrix(sp.Matrix.hstack(*v)) for v in (left,middle,right)],
                                       matrix(df), arb(1)/4)
    for name,expected in (('residual_second',expected_r),('midpoint_second',expected_m)):
        values = matrix(sp.Matrix.hstack(*expected))
        assert all(a.contains(b) for a,b in zip(result[name].entries(),values.entries(),strict=True))
    # Nonorthogonal frame and non-diagonal inverse: multiplication order and
    # Newton/Taylor signs are checked against an exact rational matrix solve.
    t,r = sp.Matrix([[2,1],[-1,3]]),sp.Matrix([[3,1],[1,2]])
    source = frozen_newton_quadratic_source(result['residual_second'],matrix(t),matrix(r))
    exact = matrix(-r.inv()*t*sp.Matrix.hstack(*expected_r)/2)
    assert all(a.contains(b) for a,b in zip(source.entries(),exact.entries(),strict=True))


def test_midpoint_second_derivative_is_not_omitted_or_wrong_signed():
    result = physical_hs_second_residual([[1]],[[2]],[[4]],[[3]],.5)
    assert result['midpoint_second'][0,0] == arb(-3)/16
    assert result['residual_second'][0,0].contains(arb(-43)/48)
    source = frozen_newton_quadratic_source(result['residual_second'],[[1]],[[1]])
    assert source[0,0].contains(arb(43)/96)


def test_interval_contractions_enclose_all_exact_corners():
    values = [arb(1,.125),arb(2,.125),arb(4,.125),arb(3,.125)]
    result = physical_hs_second_residual(*[[[v]] for v in values], .5)['residual_second'][0,0]
    for perturbations in product((-1,1),repeat=4):
        left,middle,right,df = [sp.Rational(v)+sp.Rational(p,8) for v,p in zip((1,2,4,3),perturbations)]
        h = sp.Rational(1,2)
        exact = -h*(left+4*middle+right)/6 - h*h*df*(left-right)/12
        assert result.contains(arb(fmpq(str(exact))))


def test_linear_rate_has_zero_quadratic_source():
    result = physical_hs_second_residual([[0],[0]],[[0],[0]],[[0],[0]],[[1,2],[3,4]],1)
    source = frozen_newton_quadratic_source(result['residual_second'],[[1,2]],[[3]])
    assert all(value.is_zero() for value in source.entries())


def test_taylor_mixed_term_keeps_factor_two():
    # The residual Hessian is [[2,3],[3,4]], packed as LL, LT, TT.
    q = frozen_newton_quadratic_source([[2,3,4]],[[1]],[[1]])
    l,t = arb(2),arb(5)
    packed = q[0,0]*l*l+2*q[0,1]*l*t+q[0,2]*t*t
    assert packed == -(2*l*l+6*l*t+4*t*t)/2


@pytest.mark.parametrize('step',[0,-1,arb(1,.125),float('inf')])
def test_nonexact_or_invalid_steps_fail_and_restore_precision(step):
    previous = ctx.prec
    with pytest.raises(ValueError):
        physical_hs_second_residual([[1]],[[2]],[[3]],[[4]],step)
    assert ctx.prec == previous


def test_missing_contraction_and_bad_shapes_are_not_zero_defaults():
    for left,df in ((None,[[1]]),([[1]],[[1,2]])):
        with pytest.raises(ValueError):
            physical_hs_second_residual(left,[[2]],[[3]],df,1)
    with pytest.raises(ValueError):
        frozen_newton_quadratic_source([[1],[2]],[[1]],[[1]])


def test_singular_inverse_and_bad_precision_fail_closed():
    previous = ctx.prec
    with pytest.raises(ArithmeticError):
        frozen_newton_quadratic_source([[1]],[[1]],[[0]])
    for precision in (True,63):
        with pytest.raises(ValueError):
            physical_hs_second_residual([[1]],[[1]],[[1]],[[1]],1,precision=precision)
        with pytest.raises(ValueError):
            frozen_newton_quadratic_source([[1]],[[1]],[[1]],precision=precision)
    assert ctx.prec == previous
