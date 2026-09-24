"""Exact implicit and normalized derivatives, independent of BHSM anchors."""
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_implicit_response_jet import solve,mixed_response,normalized_mixed
from bhsm.interface.shared_eigenline_jet import second_variations


@pytest.fixture(autouse=True)
def precision():
    old=ctx.prec;ctx.prec=256
    yield
    ctx.prec=old


def domain():return TaylorDomain([(0,1,'interval')],1)


def test_affine_residual_retains_shared_cancellation():
    d=domain();x=d.affine(2,[3]);one=d.affine(1)
    answer,proof=solve([[one]],[x],arb_mat([[1]]),[arb(1)],arb(0))
    assert answer[0].c==2 and answer[0].a[0,0]==3
    assert answer[0].r.is_zero() and proof['weighted_residual_upper'].is_zero()


def test_nonconstant_inverse_covers_exact_reciprocal():
    d=domain();K=d.affine(2,[arb('0.1')]);b=d.affine(1)
    x,_=solve([[K]],[b],arb_mat([[arb('0.5')]]),[arb(1)],arb('0.05'))
    for t in (-1,0,1):
        value=x[0].c+x[0].a[0,0]*t+arb(0,x[0].r)
        assert value.contains(1/(2+arb('0.1')*t))


def test_mixed_response_combines_forcing_before_support():
    d=domain();a=d.affine;z=a(0);one=a(1);t=a(0,[1])
    # x=1 with F=K. F_uv and K_uv*x cancel exactly, including the shared t.
    x,proof=mixed_response([[one]],[[z]],[[z]],[[t]],[t],[one],[z],[z],
                           arb_mat([[1]]),[arb(1)],arb(0))
    assert x[0].support().is_zero()
    assert proof['complete_mixed_rhs_models'][0].support().is_zero()


def test_inverse_without_domain_contraction_is_rejected():
    d=domain();one=d.affine(1)
    with pytest.raises(ValueError,match='q<1'):
        solve([[one]],[one],arb_mat([[1]]),[arb(1)],arb(1))


def test_mixed_parameter_identity_is_rejected():
    d=domain();e=domain()
    with pytest.raises(ValueError,match='namespace'):
        solve([[d.affine(1)]],[e.affine(1)],arb_mat([[1]]),[arb(1)],arb(0))


def test_normalization_matches_unit_circle_and_excludes_descriptor():
    d=domain();a=d.affine
    # U(t)=(1,t,2), physical norm sqrt(1+t^2), at t=0.
    # f''=(-1,0,-2); putting descriptor in the norm gives a wrong answer.
    f,_=normalized_mixed([a(1),a(0),a(2)],[a(0),a(1),a(0)],
        [a(0),a(1),a(0)],[a(0)]*3,2)
    for value,expected in zip(f,(-1,0,-2)):
        assert value.enclosure().contains(expected)
        assert value.r<arb('1e-60')


def test_zero_crossing_normalization_is_rejected():
    d=domain();a=d.affine
    with pytest.raises(ArithmeticError,match='positive normalization'):
        normalized_mixed([a(0,[1])],[a(1)],[a(1)],[a(0)],1)


def test_matrix_free_action_eigenline_matches_exact_rotating_line():
    # S(t,y,z)=y^2+t*y*z+(5/2)z^2. H=[[2,t],[t,5]].
    # At t=0 the lower eigenpair has lambda''=-2/3, psi'=(0,-1/3),
    # psi''=(-1/9,0). This catches border sign and the normalization term.
    d=domain();a=d.affine;zero=a(0)
    def evaluate(legs):
        if len(legs)==2:
            l,r=legs;return 2*l[1]*r[1]+5*l[2]*r[2]
        if len(legs)==3:
            import itertools
            return sum((legs[0][i]*legs[1][j]*legs[2][k]
                        for i,j,k in itertools.permutations(range(3))),zero)
        if len(legs)==4:return zero
        raise AssertionError('unneeded derivative order')
    R=arb_mat([[0,0,1],[0,arb(1)/3,0],[1,0,0]])
    # Use a dyadic inverse approximation and certify its exact residual q.
    R[1,1]=R[1,1].mid()
    q=abs(1-3*R[1,1]).upper()
    result=second_variations(evaluate,[a(1),zero],a(2),[a(1),zero,zero],
        [a(1),zero,zero],1,R,[arb(1)]*3,q)
    for key,expected in [('psi_u',[arb(0),-arb(1)/3]),('psi_uv',[-arb(1)/9,arb(0)])]:
        for value,want in zip(result[key],expected):
            assert value.enclosure().contains(want)
            assert value.r<arb('1e-60')
    assert result['lambda_uv'].enclosure().contains(-arb(2)/3)


def test_action_eigenvalue_derivative_is_uniform_on_shared_parameter_domain():
    # S(t,y)=t^2*y^2/2, psi=1, lambda=t^2 on t=2+theta/8.
    # The derivative is 2*t, not the slope of the affine value enclosure.
    d=domain();a=d.affine;t=a(2,[arb('0.125')]);zero=a(0);one=a(1)
    def evaluate(legs):
        if len(legs)==2:return t*t*legs[0][1]*legs[1][1]
        if len(legs)==3:
            return 2*t*legs[0][1]*legs[1][1]*legs[2][0]
        if len(legs)==4:
            return 2*legs[0][1]*legs[1][1]*legs[2][0]*legs[3][0]
        raise AssertionError('unneeded derivative order')
    result=second_variations(evaluate,[one],t*t,[one,zero],[one,zero],1,
                             arb_mat([[0,1],[1,0]]),[arb(1)]*2,arb(0))
    for theta in (-1,0,1):
        jet=result['lambda_u']
        predicted=jet.c+jet.a[0,0]*theta+arb(0,jet.r)
        assert predicted.contains(2*(2+arb('0.125')*theta))
    assert result['lambda_uv'].enclosure().contains(2)
