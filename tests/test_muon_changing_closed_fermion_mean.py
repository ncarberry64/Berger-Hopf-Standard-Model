import numpy as np
from scipy.linalg import eigh
from scipy.special import exp1
from bhsm.interface.muon_changing_closed_fermion_mean import heat_gradient_divided_differences,even_y_trace_duals
from bhsm.interface.muon_primal_cell_native_heat import _divided_differences


def test_stable_heat_divided_differences_against_independent_simplex_integration():
    values=np.array([2.,2.+1e-12,2.1,2.4]);c=.27
    f,s=heat_gradient_divided_differences(values,c)
    oldf,olds=_divided_differences(values,c,24)
    np.testing.assert_allclose(f,oldf,rtol=1e-14,atol=1e-15)
    np.testing.assert_allclose(s(slice(0,4)),olds,rtol=1e-13,atol=1e-15)
    assert np.max(s(slice(0,4)))<0


def test_actual_Y2_functional_calculus_and_generalized_Gram_cotangent():
    rng=np.random.default_rng(591)
    def sym():
        a=rng.normal(size=(4,4));return (a+a.T)/2
    K=np.diag([2.,3.,4.,5.])+sym()*.08;C=sym()*.2;B=np.eye(4)*.3+sym()*.02
    G=np.diag([1.,1.1,.9,1.2]);dK=sym()*.3;dC=sym()*.1;dB=sym()*.1;dG=sym()*.03;c=.27
    a=even_y_trace_duals(K,C,B,G,c)
    # E1 is the unchanged action function, evaluated independently on the pencil.
    h=1e-3
    trace=lambda y:np.sum(exp1(c*eigh(K+y*C+y*y*B,G,eigvals_only=True)))
    second=(trace(h)+trace(-h)-2*trace(0))/(2*h*h)
    np.testing.assert_allclose(a['even_Y2_coefficient'],second,rtol=2e-7,atol=2e-9)
    derivative=sum(np.trace(x@y).real for x,y in zip(a['action_duals'],(dK,dC,dB)))-np.trace(a['Gram_dual']@dG).real
    step=1e-5
    plus=even_y_trace_duals(K+step*dK,C+step*dC,B+step*dB,G+step*dG,c)['even_Y2_coefficient']
    minus=even_y_trace_duals(K-step*dK,C-step*dC,B-step*dB,G-step*dG,c)['even_Y2_coefficient']
    np.testing.assert_allclose(derivative,(plus-minus)/(2*step),rtol=2e-8,atol=2e-10)


def test_zero_cutoff_and_widely_separated_positive_poles():
    x=np.array([1.,1.e5,1.e11]);f,s=heat_gradient_divided_differences(x,0.)
    np.testing.assert_allclose(f,1/(x[:,None]*x[None,:]),rtol=1e-15)
    np.testing.assert_allclose(s(slice(0,3)),-1/(x[:,None,None]*x[None,:,None]*x[None,None,:]),rtol=1e-15)
    f,s=heat_gradient_divided_differences(x,1.e-3)
    assert np.isfinite(f).all()and np.isfinite(s(slice(0,3))).all()
