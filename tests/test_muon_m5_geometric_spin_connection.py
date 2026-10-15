"""Independent local geometric controls; no physical background is selected."""
import numpy as np
import mpmath as mp
import pytest
from scipy.linalg import expm
from bhsm.interface.muon_m5_geometric_spin_connection import (
    m5_geometric_spin_connection,independent_coordinate_tetrad_connection)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace

def gamma():return full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]

def fields(t,r):
    return (mp.exp(.1+.03*t+.04*r+.01*t*r),mp.exp(-.1+.07*t-.03*r+.02*t*t),
        .14+.02*t-.01*r+.013*t*r,mp.exp(.2-.04*t+.03*r+.005*r*r))

def primitives(t,r):
    N,C,z,R=fields(t,r)
    dt=lambda i:mp.diff(lambda x:fields(x,r)[i],t)
    dr=lambda i:mp.diff(lambda x:fields(t,x)[i],r)
    return [N,C,z,R,dr(0),dt(1),dr(1),dr(2),dt(3),dr(3)]

def metric_connection(t,r,eps):
    # Independent coordinate Christoffel construction, not Cartan contacts.
    N,C,z,R=fields(t,r);p=primitives(t,r)
    Nt=mp.diff(lambda x:fields(x,r)[0],t);zt=mp.diff(lambda x:fields(x,r)[2],t)
    _,_,_,_,Nr,Ct,Cr,zr,Rt,Rr=p
    e=mp.diag([N,eps*C,R,R,R]);e[1,0]=eps*C*z
    de=[mp.zeros(5)for _ in range(5)]
    de[0][0,0]=Nt;de[1][0,0]=Nr
    de[0][1,0]=eps*(Ct*z+C*zt);de[0][1,1]=eps*Ct
    de[1][1,0]=eps*(Cr*z+C*zr);de[1][1,1]=eps*Cr
    levi=lambda a,b,c:((b-a)*(c-a)*(c-b)//2 if len({a,b,c})==3 else 0)
    for i in range(3):
        de[0][i+2,i+2]=Rt;de[1][i+2,i+2]=Rr
        for j in range(3):
            for k in range(3):de[j+2][i+2,k+2]=R*levi(i,j,k)
    eta=mp.diag([1,-1,-1,-1,-1]);g=e.T*eta*e;gi=g**-1
    dg=[a.T*eta*e+e.T*eta*a for a in de]
    out=[]
    for mu in range(5):
        Christoffel=mp.matrix(5,5)
        for lam in range(5):
            for nu in range(5):Christoffel[lam,nu]=sum(gi[lam,s]*(dg[mu][s,nu]+dg[nu][s,mu]-dg[s][mu,nu])/2 for s in range(5))
        out.append(eta*(e*Christoffel-de[mu])*(e**-1))
    return out

def test_full_metric_christoffel_and_source_derivative_mp64():
    with mp.workdps(64):
        t,r=mp.mpf('.19'),mp.mpf('.23')
        p=np.array([[float(a)for a in primitives(t,r)],
            [float(mp.diff(lambda x:primitives(x,r)[i],t))for i in range(10)]])
        for eps in(-1,1):
            a=m5_geometric_spin_connection(p,gamma=gamma(),orientation=eps)
            for source in(0,1):
                reference=np.empty((5,5,5))
                for A in range(5):
                    for B in range(5):
                        for mu in range(5):
                            f=lambda x:metric_connection(x,r,eps)[mu][A,B]
                            reference[A,B,mu]=float(f(t)if source==0 else mp.diff(f,t))
                np.testing.assert_allclose(a['lower_connection_coordinate_value_first'][source],reference,rtol=2e-13,atol=2e-14)
            Nt=float(mp.diff(lambda x:fields(x,r)[0],t));zt=float(mp.diff(lambda x:fields(x,r)[2],t))
            c=independent_coordinate_tetrad_connection(p[0],N_time=Nt,z_time=zt,orientation=eps)
            np.testing.assert_allclose(c['lower_connection_coordinate'],a['lower_connection_coordinate_value_first'][0],atol=2e-15)
            assert np.max(abs(c['tetrad_postulate_rows']))<2e-15

def test_full_ordered_spin_contraction_has_owned_right_triple():
    p=np.array([[1.2,.9,.17,1.3,.2,.11,-.09,.08,.05,.12],np.arange(1,11)*.01])
    G=gamma()
    for eps in(-1,1):
        a=m5_geometric_spin_connection(p,gamma=G,orientation=eps)
        for s,contacts in enumerate(a['scalar_contacts']):
            aa,k,H0,H4,invR=contacts
            expected=.5j*G[0]*(k+3*H0)+.5j*eps*G[1]*(aa+3*H4)-1.5j*invR*G[2]@G[3]@G[4]
            np.testing.assert_allclose(a['original_Dirac_geometric_body_value_first'][s],expected,atol=2e-15)
        assert np.linalg.norm(a['Spin_connection_coordinate_value_first'][0,2:])>0

def test_spin_boost_parallel_and_adapted_connection_plus_sign():
    G=gamma();K=G[0]@G[1];omega=.23;eta=.17;eta_t=-.11;dt=.031
    for eps in(-1,1):
        B=expm(eps*eta*K/2);Bi=expm(-eps*eta*K/2);Bt=eps*eta_t*K@B/2
        ambient=eps*omega*K/2;adapted=Bi@ambient@B+Bi@Bt
        np.testing.assert_allclose(adapted,eps*(omega+eta_t)*K/2,atol=2e-15)
        U=expm(-dt*ambient)
        np.testing.assert_allclose(U.conj().T@G[0]@U,G[0],atol=2e-15)
        assert np.max(abs(U.conj().T@U-np.eye(4)))>1e-4

def test_explicit_source_signature_and_chart_guards():
    p=np.array([[1.2,.9,.17,1.3,.2,.11,-.09,.08,.05,.12],np.arange(1,11)*.01])
    with pytest.raises(ValueError):m5_geometric_spin_connection(p[:1],gamma=gamma(),orientation=1)
    with pytest.raises(ValueError):m5_geometric_spin_connection(p,gamma=gamma(),orientation=0)
    wrong=p.astype(complex);wrong[1,0]+=1j
    with pytest.raises(ValueError):m5_geometric_spin_connection(wrong,gamma=gamma(),orientation=1)
    wrong=p.copy();wrong[0,1]=0
    with pytest.raises(ValueError):m5_geometric_spin_connection(wrong,gamma=gamma(),orientation=1)
