"""CONTROL_ONLY analytic finite checks; no physical operator/state selection."""
import numpy as np
import mpmath as mp
import pytest
from flint import ctx

from bhsm.interface.muon_native_even_y_target_certificate import (
    cutoff_divided_differences,reference_coefficient_and_cotangent_matrices,
    _reference_directional_target,_mismatch_bounds,
)
from bhsm.interface.muon_native_even_y_remainder_certificate import (
    certify_generalized_even_pencil,even_y_tail_bounds,
)


def encloses(ball,value):
    # Exact binary endpoints avoid decimal display rounding of Arb balls.
    def exact(point):
        mantissa,exponent=point.man_exp()
        return mp.mpf(int(mantissa))*mp.mpf(2)**int(exponent)
    return exact(ball.lower()) <= value <= exact(ball.upper())


def test_analytic_equal_pole_first_and_second_limits():
    old=ctx.prec
    try:
        ctx.prec=192;g,first,second=cutoff_divided_differences([2.,2.,3.],.7)
        with mp.workdps(90):
            f=lambda x:-mp.exp(-mp.mpf(.7)*x)/x
            assert encloses(g[0],f(mp.mpf(2)))
            assert encloses(first[0][1],mp.diff(f,2,1))
            assert encloses(second(0,1,0),mp.diff(f,2,2)/2)
            repeated=(mp.diff(f,2,1)-(f(3)-f(2)))/(mp.mpf(2)-3)
            assert encloses(second(0,1,2),repeated)
    finally:ctx.prec=old


def test_close_poles_are_enclosed_without_threshold_coalescing():
    old=ctx.prec
    try:
        ctx.prec=256;x=2.;y=np.nextafter(x,np.inf);z=np.nextafter(y,np.inf)
        _,first,second=cutoff_divided_differences([x,y,z],.7)
        with mp.workdps(140):
            a,b,c=map(mp.mpf,(x,y,z));f=lambda t:-mp.exp(-mp.mpf(.7)*t)/t
            one=(f(b)-f(a))/(b-a)
            two=((f(c)-f(b))/(c-b)-one)/(c-a)
            assert encloses(first[0][1],one)
            assert encloses(second(0,1,2),two)
            assert second(0,1,2).rad() < 1e-35
    finally:ctx.prec=old


def test_first_and_second_are_symmetric_for_all_stored_poles():
    old=ctx.prec
    try:
        ctx.prec=192;_,first,second=cutoff_divided_differences([1.,2.,4.],.5)
        for i in range(3):
            for j in range(3):
                assert first[i][j].overlaps(first[j][i])
                for k in range(3):assert second(i,j,k).overlaps(second(k,i,j))
    finally:ctx.prec=old


def test_exact_Y2_coefficient_matches_independent_eigenvalue_derivative():
    old=ctx.prec
    try:
        ctx.prec=192;A=np.diag(np.sqrt([2.,3.]));M=np.array([[0.,.2],[.2,0.]])
        C=A@M+M@A;B=M@M
        value=reference_coefficient_and_cotangent_matrices([2.,3.],C,B,.7)['coefficient']
        # Independently use the exact stored C/B entries in a Hermitian
        # two-by-two polynomial, rather than assuming sqrt products exact.
        with mp.workdps(90):
            def trace(y):
                aa=mp.mpf(2)+mp.mpf(B[0,0])*y*y;bb=mp.mpf(3)+mp.mpf(B[1,1])*y*y
                disc=mp.sqrt((aa-bb)**2+4*mp.mpf(C[0,1])**2*y*y)
                return sum(mp.e1(mp.mpf(.7)*e) for e in ((aa+bb-disc)/2,(aa+bb+disc)/2))
            assert encloses(value,mp.diff(trace,0,2)/2)
    finally:ctx.prec=old


def test_raw_directional_mass_and_Gram_cotangents_match_exact_matrix_derivatives():
    old=ctx.prec
    try:
        ctx.prec=192;A=np.diag([1.,2.]);M=np.array([[0.,.25],[.25,0.]])
        mass_variation=np.array([[0.,.125],[.125,0.]]);ratio=.125
        read=reference_coefficient_and_cotangent_matrices([1.,4.],A@M+M@A,M@M,.5)
        sample=dict(u=np.eye(2),Au=A,Mu=M,deltaA=np.array([np.zeros((2,2)),-ratio/2*A]),
            deltaMu=np.array([mass_variation,-ratio/2*M]),measure=np.array([0.,ratio]),weight=1.)
        rows=_reference_directional_target(sample,read)
        with mp.workdps(90):
            def coefficient(t,kind):
                def trace(y):
                    mass=mp.mpf('.25')+(mp.mpf('.125')*t if kind==0 else 0)
                    aa=1+mass*mass*y*y;bb=4+mass*mass*y*y;off=3*mass*y
                    disc=mp.sqrt((aa-bb)**2+4*off*off)
                    divisor=1+mp.mpf('.125')*t if kind==1 else 1
                    return sum(mp.e1(mp.mpf('.5')*v/divisor) for v in ((aa+bb-disc)/2,(aa+bb+disc)/2))
                return mp.diff(trace,0,2)/2
            for i in range(2):assert encloses(rows[i],mp.diff(lambda t:coefficient(t,i),0))
            assert not rows[1].contains(0)
    finally:ctx.prec=old


@pytest.mark.parametrize('poles,cutoff', [([0.,1.],.5),([1.,np.nan],.5),([1.,2.],0.),([1.,2.],np.inf)])
def test_divided_difference_domain_failures(poles,cutoff):
    with pytest.raises(ValueError):cutoff_divided_differences(poles,cutoff)


def test_nonfinite_and_mixed_dimension_Taylor_inputs_rejected():
    with pytest.raises(ValueError):reference_coefficient_and_cotangent_matrices([1.,2.],np.eye(3),np.eye(2),.5)
    with pytest.raises(ValueError):reference_coefficient_and_cotangent_matrices([1.,2.],np.full((2,2),np.nan),np.eye(2),.5)


def test_FE_reference_value_and_direction_error_bounds_enclose_exact_Gram_mismatch():
    old=ctx.prec
    try:
        ctx.prec=192;A=np.diag([1.,2.]);M=np.array([[0.,.25],[.25,0.]])
        dm=np.array([[0.,.125],[.125,0.]]);C=A@M+M@A;B=M@M
        rawC=C*1.00001;rawB=B*.99998;Gram=np.diag([1.001,.998]);lam=np.array([1.,4.])
        data=dict(actual_FE_K0=np.diag(lam),actual_FE_K1=rawC,actual_FE_K2=rawB,actual_FE_Gram=Gram,
            computed_generalized_eigenvectors=np.eye(2),normalized_P0_eigenvalues=lam,normalized_P1=C,normalized_P2=B,
            u_Frobenius_upper=np.array([np.sqrt(2.)]),Au_Frobenius_upper=np.array([np.linalg.norm(A)]),
            Mu_Frobenius_upper=np.array([np.linalg.norm(M)]),sample_weight=np.array([1.]),
            deltaA_Frobenius_upper=np.array([[0.]]),deltaMu_Frobenius_upper=np.array([[np.linalg.norm(dm)]]),
            abs_deltaN_over_N=np.array([[0.]]))
        receipt=dict(parameter=.5,fixed_Y_middle=.05,fixed_Y_light=.004)
        constants,_=certify_generalized_even_pencil(np.diag(lam),rawC,rawB,Gram,np.eye(2),lam,[1,-1])
        tail=even_y_tail_bounds(constants,.5,.05,.004)
        read=reference_coefficient_and_cotangent_matrices(lam,C,B,.5)
        value_bound,derivative_bound,_=_mismatch_bounds(data,receipt,constants,read,tail['circle_radius_exact_binary64'])
        dC=A@dm+dm@A;dB=M@dm+dm@M
        with mp.workdps(90):
            def coefficient(t,true):
                g0,g1=map(mp.mpf,np.diag(Gram)) if true else (mp.mpf(1),mp.mpf(1))
                cc,bb=(rawC,rawB) if true else (C,B)
                def trace(y):
                    aa=(1+(mp.mpf(bb[0,0])+t*mp.mpf(dB[0,0]))*y*y)/g0
                    b=(4+(mp.mpf(bb[1,1])+t*mp.mpf(dB[1,1]))*y*y)/g1
                    off=(mp.mpf(cc[0,1])+t*mp.mpf(dC[0,1]))*y/mp.sqrt(g0*g1)
                    disc=mp.sqrt((aa-b)**2+4*off*off)
                    return sum(mp.e1(mp.mpf('.5')*v) for v in ((aa+b-disc)/2,(aa+b+disc)/2))
                return mp.diff(trace,0,2)/2
            difference=mp.mpf(.05)**2-mp.mpf(.004)**2
            error=(coefficient(0,True)-coefficient(0,False))*difference
            derivative_error=mp.diff(lambda t:coefficient(t,True)-coefficient(t,False),0)*difference
            assert abs(error)>0 and abs(error)<float(value_bound.upper())
            assert abs(derivative_error)>0 and abs(derivative_error)<derivative_bound[0,0]
    finally:ctx.prec=old
