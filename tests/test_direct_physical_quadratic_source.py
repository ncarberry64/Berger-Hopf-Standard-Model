from itertools import product
import pytest
import sympy as sp
from flint import arb, arb_mat, ctx, fmpq
from bhsm.interface.direct_physical_quadratic_source import UpperHessian, physical_quadratic_source


def matrix(m):
    return arb_mat(m.rows,m.cols,[arb(fmpq(str(v))) for v in m])


def tensor(hessians):
    n=len(hessians)
    return UpperHessian([[[h[i,j] for j in range(i,n)] for h in hessians] for i in range(n)])


@pytest.fixture(autouse=True)
def reference_precision():
    previous=ctx.prec;ctx.prec=768
    yield
    ctx.prec=previous


def test_complete_nonlinear_map_with_frames_matches_symbolic_hessian():
    x,y,a,b=variables=sp.symbols('x y a b')
    z0,z1=sp.Matrix([x,y]),sp.Matrix([a,b])
    def rate(z):
        p,q=z
        return sp.Matrix([p*p+p*q,p-q**3])
    step=sp.Rational(1,4)
    midpoint=(z0+z1)/2+step*(rate(z0)-rate(z1))/8
    residual=z1-z0-step*(rate(z0)+4*rate(midpoint)+rate(z1))/6
    point=dict(zip(variables,[sp.Rational(1,2),sp.Rational(-1,4),1,sp.Rational(1,4)]))
    locations=[z0.subs(point),midpoint.subs(point),z1.subs(point)]
    hs=[tensor([matrix(sp.hessian(f,(x,y)).subs(dict(zip((x,y),z)))) for f in rate(z0)]) for z in locations]
    dfs=[matrix(rate(z0).jacobian(z0).subs(dict(zip((x,y),z)))) for z in locations]
    # Different rectangular direction families exercise every Cartesian column,
    # cross-endpoint contributions, nonorthogonal trials, test and inverse.
    u=sp.Matrix([[1,2],[3,-1],[-1,1],[2,4]])
    v=sp.Matrix([[2,-1,1],[1,3,2],[4,1,-2],[-1,2,3]])
    test,right=sp.Matrix([[2,1],[-1,3]]),sp.Matrix([[3,1],[1,2]])
    actual=physical_quadratic_source(hs,dfs,arb(1)/4,*map(matrix,(u[:2,:],u[2:,:],v[:2,:],v[2:,:])),matrix(test),matrix(right))
    expected=[]
    for j in range(u.cols):
        for k in range(v.cols):
            second=sp.Matrix([(u[:,j].T*sp.hessian(f,variables).subs(point)*v[:,k])[0] for f in residual])
            expected.append(-right.inv()*test*second/2)
    reference=matrix(sp.Matrix.hstack(*expected))
    assert actual.ncols()==6
    assert all(a.contains(b) for a,b in zip(actual.entries(),reference.entries(),strict=True))


def test_uncertain_hessian_and_directions_enclose_all_exact_corners():
    h=UpperHessian([[[arb(2,.125),arb(3,.125)],[arb(-1,.125),arb(4,.125)]],
                    [[arb(5,.125)],[arb(6,.125)]]])
    actual=h.cartesian([[arb(1,.125)],[2]],[[3],[arb(-1,.125)]])
    for signs in product((-1,1),repeat=8):
        vals=[sp.Rational(v)+sp.Rational(s,8) for v,s in zip((2,3,-1,4,5,6,1,-1),signs)]
        aa,bb,cc,dd,ee,ff,u,v=vals
        reference=sp.Matrix([(sp.Matrix([u,2]).T*H*sp.Matrix([3,v]))[0]
                             for H in (sp.Matrix([[aa,bb],[bb,ee]]),sp.Matrix([[cc,dd],[dd,ff]]))])
        assert all(a.contains(b) for a,b in zip(actual.entries(),matrix(reference).entries(),strict=True))


def test_explicit_fixed_endpoint_and_mixed_column_order():
    h=UpperHessian([[[2]]])
    value=physical_quadratic_source([h,h,h],[[[2]],[[3]],[[4]]],arb(1)/4,
        [[0,0]],[[1,2]],[[0,0,0]],[[3,4,5]],[[1]],[[1]])
    assert (value[0,1]*3-value[0,0]*4).contains(0)
    assert (value[0,3]-2*value[0,0]).contains(0)
    zero=physical_quadratic_source([h,h,h],[[[2]],[[3]],[[4]]],arb(1)/4,
        [[0]],[[0]],[[0]],[[1]],[[1]],[[1]])
    assert zero[0,0].is_zero()


@pytest.mark.parametrize('rows',[[],[[[1,2],[3,4]]],[[[1,2],[3,4]],[[1,2],[3,4]]],[[[float('inf')]]]])
def test_incomplete_or_nonfinite_upper_tensor_rejected(rows):
    with pytest.raises(ValueError):UpperHessian(rows)


def test_bad_direction_shapes_and_precision_restore():
    h=UpperHessian([[[1]]]);previous=ctx.prec
    with pytest.raises(ValueError):h.cartesian([[1],[2]],[[1]])
    for args in (([h,h],[[1]],[[1]]),([h,h,h],[[1,2]],[[1]])):
        tensors,u0,u1=args
        with pytest.raises(ValueError):
            physical_quadratic_source(tensors,[[[1]]]*3,1,u0,u1,[[1]],[[1]],[[1]],[[1]])
        assert ctx.prec==previous
    with pytest.raises(ValueError):
        physical_quadratic_source([h]*3,[[[1]]]*3,1,[[1]],[[1]],[[1]],[[1]],[[1]],[[1]],precision=True)
