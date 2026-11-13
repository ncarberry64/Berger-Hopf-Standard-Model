"""Action evolution/independent reflected dual controls, not a primal choice."""
import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_euclidean_cell_sewing import canonical_segment_application,canonical_segment_parameter_variation


def _functions(variable=False):
    Hs=np.array([[.2,.04+.03j],[.04-.03j,-.3]])
    Ht=np.array([[.1,.02,0],[.02,-.2,.05j],[0,-.05j,.4]])
    Ks=np.array([[.07,.01j],[-.01j,.1]])
    Kt=np.array([[.03,.02j,0],[-.02j,-.04,.01],[0,.01,.08]])
    X=np.array([[[.1+.02j,.05],[.03j,-.02],[.04,.07j]]])
    X1=np.array([[[.03j,.02],[-.01,.04j],[.01+.02j,.03]]])
    def coeff(t):return(Hs+t*Ks,Ht+t*Kt,1+.1*t)if variable else(Hs,Ht,1.)
    def source(t):return(X+t*X1,X.conj().swapaxes(-1,-2)+t*X1.conj().swapaxes(-1,-2))if variable else(X,X.conj().swapaxes(-1,-2))
    return coeff,source


def test_constant_connector_and_both_source_orders_equal_full_action_exponential():
    C,X=_functions();start,stop=.01-.03j,.08+.02j;result=canonical_segment_application(C,X,start,stop,substeps=4)
    hs,ht,N=C(0);xi,rev=X(0);h=stop-start
    np.testing.assert_allclose(result['source_trace'],expm(-1j*h*hs),atol=6e-16)
    np.testing.assert_allclose(result['target_trace'],expm(-1j*h*ht),atol=6e-16)
    def full(epsilon):
        H=np.block([[ht,epsilon*xi[0]],[epsilon*rev[0],hs]])
        return expm(-1j*h*H)
    step=2e-5;delta=(full(step)-full(-step))/(2*step)
    np.testing.assert_allclose(result['magnetic_forward_trace'][0],delta[:3,3:],rtol=2e-11,atol=2e-15)
    np.testing.assert_allclose(result['magnetic_reverse_trace'][0],delta[3:,:3],rtol=2e-11,atol=2e-15)
    assert result['reflected_source_dual_residual_max']<8e-16
    assert result['reflected_target_dual_residual_max']<8e-16
    assert result['reflected_source_contact_dual_residual_max']<2e-16


def test_noncommuting_changing_action_has_converging_subdivision_and_independent_dual():
    C,X=_functions(True);start,stop=.01-.03j,.08+.02j
    a=[canonical_segment_application(C,X,start,stop,substeps=n)for n in(2,4,8)]
    first=np.linalg.norm(a[0]['source_trace']-a[1]['source_trace'])
    second=np.linalg.norm(a[1]['source_trace']-a[2]['source_trace'])
    assert 0<second<first/3
    assert a[-1]['reflected_source_dual_residual_max']<2e-15
    assert a[-1]['reflected_source_contact_dual_residual_max']<2e-16
    assert np.linalg.norm(a[-1]['source_trace'].conj().T@a[-1]['source_trace']-np.eye(2))>.01


def test_clock_and_metric_parameter_contact_matches_independent_shifted_action():
    C,X=_functions(True);a,b=.01-.03j,.08+.02j;da,db=.003+.007j,-.004+.002j
    Hparam=np.array([[.03,.01j],[-.01j,.02]]);Nparam=.04
    def jet(t,dt):
        H,_,N=C(t);_,_,Nt=C(0);Ht=np.array([[.07,.01j],[-.01j,.1]])
        return H,N,Hparam+dt*Ht,Nparam+.1*dt
    actual=canonical_segment_parameter_variation(jet,a,b,start_first=da,stop_first=db,substeps=4)
    def changed(e):
        def coeff(t):
            H,T,N=C(t);return H+e*Hparam,T,N+e*Nparam
        return canonical_segment_application(coeff,X,a+e*da,b+e*db,substeps=4)['source_trace']
    step=1e-5;numeric=(changed(step)-changed(-step))/(2*step)
    np.testing.assert_allclose(actual['trace_first'],numeric,atol=2e-11,rtol=2e-8)
    assert actual['pairing_first_residual_max']<2e-18
