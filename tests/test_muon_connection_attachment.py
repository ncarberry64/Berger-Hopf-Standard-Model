"""New action compatibility checks; no old mechanical producer is called."""
import json
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/muon_connection_attachment_20261002/replay_reference'


def test_right_maurer_curvature_has_no_parallel_doublet():
    # d theta_R^1=2 theta_R^2 wedge theta_R^3; h=lambda-1.
    L=sp.Symbol('lambda',real=True)
    e=[sp.Matrix([[0,-sp.I],[-sp.I,0]]),sp.Matrix([[0,-1],[1,0]]),sp.diag(-sp.I,sp.I)]
    h=L-1
    F23=2*h*e[0]+h**2*(e[1]*e[2]-e[2]*e[1])
    assert sp.simplify(F23-2*L*(L-1)*e[0])==sp.zeros(2)
    assert sp.factor(F23.det())==4*L**2*(L-1)**2
    # Invertibility excludes every nonzero parallel doublet at 0<lambda<1,
    # rather than checking only the displayed Higgs vector.
    result=json.loads((ART/'higgs_connection_obligation.json').read_text())
    expression=result['one_curvature_component_determinant'].replace('lambda','L')
    assert sp.sympify(expression,locals={'L':L})==F23.det().factor()


def test_neutral_photon_still_has_a_mixed_higgs_row():
    L,t=sp.symbols('lambda t',real=True)
    y1,y2,y3=sp.symbols('y1 y2 y3',real=True)
    e=[sp.Matrix([[0,-sp.I],[-sp.I,0]]),sp.Matrix([[0,-1],[1,0]]),sp.diag(-sp.I,sp.I)]
    H=sp.Matrix([0,1]);Q=sp.diag(1,0)
    z1,z2=sp.symbols('z1 z2',complex=True);v=sp.Matrix([z1,z2])
    a=[-sp.I*Q*y for y in (y1,y2,y3)]
    # Differentiate the unreduced bilinear independently of the saved kernel.
    q=sum((((L*E+t*A)*v).conjugate().T*((L*E+t*A)*H))[0] for E,A in zip(e,a))
    dq=sp.simplify(sp.diff(q,t).subs(t,0))
    assert all(A*H==sp.zeros(2,1) for A in a)
    assert sp.simplify(dq-L*sp.conjugate(z1)*(y1-sp.I*y2))==0
    assert sp.simplify(sp.diff(sum((((L*E+t*A)*H).conjugate().T*((L*E+t*A)*H))[0] for E,A in zip(e,a)),t,2))==0


def phi(n,alpha,beta,gamma):
    j=n/2;m=np.arange(n,-n-1,-2)/2
    plus=np.zeros((n+1,n+1))
    for k in range(1,n+1):plus[k-1,k]=np.sqrt((j-m[k])*(j+m[k]+1))
    Jy=(plus-plus.T)/(2j)
    D=np.exp(-1j*m*alpha)[:,None]*expm(-1j*beta*Jy)*np.exp(-1j*m*gamma)[None]
    return np.sqrt(n+1)*D.conj()


def test_new_mixed_action_on_actual_eight_sources():
    # Pointwise evaluation independently checks the saved finite Gaunt action.
    # It makes no statement about physical state selection or operator tails.
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as p:Y=p['real_mode_coefficients']
    with np.load(ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz') as p:R=p['rotation_coefficients']
    with np.load(ART/'conditional_higgs_source_actions.npz') as p:
        C={n:p[f'Higgs_mixed_unit_n{n}'] for n in (1,3)}
        assert np.all(p['unit_column_norm2']>0)
        for angles in [(0.21,0.43,0.78),(1.1,1.3,2.2),(3.7,2.4,0.3)]:
            modes={n:phi(n,*angles) for n in (1,2,3)}
            yp=np.einsum('Acmk,mk->Ac',Y,modes[1])
            rp=np.einsum('acmk,mk->ac',R,modes[2])
            direct=np.einsum('Ac,c->A',yp,rp[:,0]-1j*rp[:,1])
            reconstructed=sum(np.einsum('Apmk,mk->Ap',C[n],modes[n]) for n in (1,3))
            np.testing.assert_allclose(reconstructed[:,0],direct,rtol=2e-14,atol=2e-14)
            np.testing.assert_array_equal(reconstructed[:,1],0)
