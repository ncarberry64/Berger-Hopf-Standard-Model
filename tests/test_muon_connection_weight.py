"""Focused normalization and parent-kinetic checks; no anomaly test."""
from pathlib import Path
import json
from fractions import Fraction
import numpy as np
import pytest
try:
    from muon_connection_weight import rank16_connection_attachment,eta_kinetic_weight
except ModuleNotFoundError:
    from bhsm.interface.muon_connection_weight import rank16_connection_attachment,eta_kinetic_weight

HERE=Path(__file__).resolve().parent
REP=HERE/'representation_input.json'
CACHE=HERE.parent/'BHSM_muon_parent_geometry_524ed906_20261001/run_2/local_parent_velocity_density.npz'
if not REP.exists():
    REP=HERE.parent/'artifacts/muon_connection_weight_20261001/representation_input.json'
    CACHE=HERE.parent/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'

def attached():
    return rank16_connection_attachment(json.loads(REP.read_text())['bundle']['multiplets'])

def test_quaternion_bracket_and_geometric_component_action_matching():
    a=attached();j=a['jmath']
    for i,k,l in [(0,1,2),(1,2,0),(2,0,1)]:
        assert np.array_equal(j[i]@j[k]-j[k]@j[i],2*j[l])
    # An independent two-source action pairing, not a chosen trace constant.
    f=np.array([.3,-.7,1.1]);g=np.array([-.4,.2,.8])
    jf=np.einsum('a,aij->ij',f,j);jg=np.einsum('a,aij->ij',g,j)
    assert np.trace(jf.conj().T@jg)/8==pytest.approx(f@g,rel=2e-15)
    assert a['component_to_Tr16_index']==8
    assert a['K_Q_over_K_component']==Fraction(2,3)
    assert a['exact_traces']==dict(I_jmath='8',Tr_T3_squared='2',
        Tr_Y_squared='10/3',Tr_T3Y='0',Tr_Q_squared='16/3')

def test_nonabelian_curvature_has_same_coordinate_conversion():
    a=attached();T=a['T'];j=a['jmath']
    # Two noncommuting connection directions check the factor on curvature,
    # not only on a linearized generator. No finite model replaces an operator.
    omega1=np.array([.2,-.1,.4]);omega2=np.array([-.3,.7,.2])
    jacobian=np.array([.6,.1,-.2]) # d_mu omega_nu-d_nu omega_mu
    omega_mu=np.einsum('a,aij->ij',omega1,j)
    omega_nu=np.einsum('a,aij->ij',omega2,j)
    mechanical=np.einsum('a,aij->ij',jacobian,j)+omega_mu@omega_nu-omega_nu@omega_mu
    Wmu=np.einsum('a,aij->ij',2*omega1,T)
    Wnu=np.einsum('a,aij->ij',2*omega2,T)
    canonical=np.einsum('a,aij->ij',2*jacobian,T)-1j*(Wmu@Wnu-Wnu@Wmu)
    assert np.allclose(mechanical,-1j*canonical,rtol=0,atol=3e-16)
    # Compare the Q source in the two equivalent coordinate descriptions.
    Q=a['Q'];J3=j[2];Y=a['Y']
    physical_Q_insertion=.5*J3-1j*Y
    assert np.array_equal(physical_Q_insertion,-1j*Q)
    assert np.trace(Q.conj().T@Q)/8==pytest.approx(2/3,rel=2e-15)

def test_eta_weight_from_full_parent_lorentzian_metric_contraction():
    with np.load(CACHE,allow_pickle=False) as z:
        fields={k:np.array(z[k]) for k in z.files}
    weight=eta_kinetic_weight(fields)
    for node,radial in [(0,32),(47,48)]:
        C,A,B,nu,zeta=[float(fields[k][node,radial]) for k in
                       ('C_rho','A','B','proper_lapse','proper_shift_rho')]
        chi=fields['rho'][radial]/2
        metric=np.diag([-nu*nu,C*C,*([A*A]*3),*([B*B]*3)])
        metric[0,0]+=C*C*zeta*zeta;metric[0,1]=metric[1,0]=C*C*zeta
        # Pullback target Gram of eta=(cos chi*u,sin chi*v), f=chi.
        pullback=np.diag([0,.25,*([np.cos(chi)**2]*3),*([np.sin(chi)**2]*3)])
        X=np.trace(np.linalg.solve(metric,pullback))
        assert X==pytest.approx(weight['X_eta'][node,radial],rel=3e-15)
        # Direct derivative of the owned F(X)=X/2+X^4/8 gives 2F'(X).
        h=1e-5
        F=lambda x:x/2+x**4/8
        derivative=(F(X+h)-F(X-h))/h
        assert derivative==pytest.approx(weight['L_eta'][node,radial],rel=2e-10)
    assert np.isfinite(weight['X_eta'][:,0]).all() # analytic pole limit
