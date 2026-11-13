"""Independent controls for the existing-form strong conormal realization."""
from __future__ import annotations

import mpmath as mp
import numpy as np
import pytest

from bhsm.interface.muon_reflected_native_conormal_graph import reflected_native_conormal_graph_jets


def _zero_jet(a):
    a=np.asarray(a,complex)
    result=np.zeros((4,)+a.shape,complex);result[0]=a
    return result


@pytest.mark.parametrize('seed',(15161,15197))
def test_noncommuting_complex_graph_jets_against_mp70_literal(seed):
    rng=np.random.default_rng(seed)
    c=rng.normal(size=(4,2,2))+1j*rng.normal(size=(4,2,2))
    g=rng.normal(size=(4,2,2))+1j*rng.normal(size=(4,2,2))
    g=(g+g.conj().swapaxes(-1,-2))/9;g[0]=np.array([[2.,.2+.15j],[.2-.15j,1.4]])
    b=np.array([1.2+.31j,.11-.06j,-.09+.14j,.04+.07j])
    z=np.array([-.8+.19j,.07+.04j,-.05+.03j,.03-.02j])
    got=reflected_native_conormal_graph_jets(b_jet=b,density_jet=g,body_jet=c,spectral_parameter_jet=z)
    with mp.workdps(70):
        number=lambda x:mp.mpc(str(x.real),str(x.imag))
        matrix=lambda a:mp.matrix([[number(v)for v in row]for row in a])
        gm,cm=[matrix(a)for a in g],[matrix(a)for a in c]
        bm,zm=[number(a)for a in b],[number(a)for a in z]
        def literal(x,y):
            G=gm[0]+x*gm[1]+y*gm[2]+x*y*gm[3]
            C=cm[0]+x*cm[1]+y*cm[2]+x*y*cm[3]
            B=bm[0]+x*bm[1]+y*bm[2]+x*y*bm[3]
            Z=zm[0]+x*zm[1]+y*zm[2]+x*y*zm[3]
            H=mp.matrix(4,4)
            H[:2,:2]=-C/B;H[:2,2:]=(mp.conj(B)*B*G)**-1
            H[2:,:2]=-Z*G;H[2:,2:]=C.H/mp.conj(B)
            return H
        h=mp.mpf('1e-15');zero=mp.mpf(0)
        reference=[literal(zero,zero),
            (literal(h,zero)-literal(-h,zero))/(2*h),
            (literal(zero,h)-literal(zero,-h))/(2*h),
            (literal(h,h)-literal(h,-h)-literal(-h,h)+literal(-h,-h))/(4*h*h)]
        exact=np.array([[[complex(v)for v in row]for row in a.tolist()]for a in reference])
    assert np.max(abs(got['canonical_generator_jet']-exact))<3e-14
    assert np.max(abs(got['current_identity_defect_jet']))<3e-14
    assert np.linalg.norm(c[0]@g[0]-g[0]@c[0])>.1
    assert np.linalg.norm(c[0]-c[0].conj().T)>.1


def test_owned_antihermitian_connection_special_case_keeps_omega():
    W=np.array([[.7,.2+.1j],[.2-.1j,-.3]])
    Omega=np.array([[.2j,.08+.03j],[-.08+.03j,-.1j]])
    z=-.4
    got=reflected_native_conormal_graph_jets(b_jet=_zero_jet(1.),density_jet=_zero_jet(np.eye(2)),
        body_jet=_zero_jet(W+Omega),spectral_parameter_jet=_zero_jet(z))
    expected=np.block([[-W-Omega,np.eye(2)],[-z*np.eye(2),W-Omega]])
    assert np.max(abs(got['canonical_generator_jet'][0]-expected))<1e-15
    assert np.linalg.norm(got['canonical_generator_jet'][0][:2,:2]+W)>.1


def test_nonconstant_clock_density_green_identity_and_forced_graph():
    """Literal differential identity retains b', G' and general C'."""
    with mp.workdps(65):
        I=mp.j
        G0=mp.matrix([[2,.2+.1*I],[.2-.1*I,1.5]])
        G1=mp.matrix([[.3,.04-.02*I],[.04+.02*I,-.1]])
        C0=mp.matrix([[.7+.2*I,.1-.3*I],[-.2+.1*I,-.4+.15*I]])
        C1=mp.matrix([[.03-.04*I,.08+.02*I],[.01-.05*I,.02+.07*I]])
        v0=mp.matrix([1+.2*I,-.3+.1*I]);v1=mp.matrix([.2-.1*I,.4+.3*I]);v2=mp.matrix([.1+.04*I,-.2+.05*I])
        u0=mp.matrix([-.4+.3*I,.7-.2*I]);u1=mp.matrix([.1+.2*I,-.2+.1*I])
        def literal(s):
            b=1+(.1+.2*I)*s;db=.1+.2*I;G=G0+s*G1;C=C0+s*C1
            u=u0+s*u1;v=v0+s*v1+s*s*v2;dv=v1+2*s*v2;ddv=2*v2
            Au=b*u1+C*u;Av=b*dv+C*v
            p=mp.conj(b)*G*Av
            dp=mp.conj(db)*G*Av+mp.conj(b)*G1*Av+mp.conj(b)*G*(db*dv+b*ddv+C1*v+C*dv)
            P=G**-1*(-dp+C.H*G*Av)
            integrand=(Au.H*G*Av-u.H*G*P)[0]
            return b,G,C,u,v,dv,p,dp,P,integrand
        integral=mp.quad(lambda s:literal(s)[-1],[0,1])
        start,end=literal(mp.mpf(0)),literal(mp.mpf(1))
        boundary=(end[3].H*end[6]-start[3].H*start[6])[0]
        assert abs(integral-boundary)<mp.mpf('1e-55')
        for s in (mp.mpf('.13'),mp.mpf('.51'),mp.mpf('.87')):
            b,G,C,u,v,dv,p,dp,P,_=literal(s);z=-.6+.14j
            array=lambda a:np.array([[complex(v)for v in row]for row in a.tolist()])
            got=reflected_native_conormal_graph_jets(b_jet=_zero_jet(complex(b)),density_jet=_zero_jet(array(G)),
                body_jet=_zero_jet(array(C)),spectral_parameter_jet=_zero_jet(z))
            state=np.r_[array(v)[:,0],array(p)[:,0]]
            actual=np.r_[array(dv)[:,0],array(dp)[:,0]]
            forced=np.r_[np.zeros(2),-array(G*(P-mp.mpc(z)*v))[:,0]]
            assert np.max(abs(actual-got['canonical_generator_jet'][0]@state-forced))<5e-15


def test_incomplete_or_nonpositive_pairing_rejected():
    args=dict(b_jet=_zero_jet(1+1j),density_jet=_zero_jet(np.eye(2)),
        body_jet=_zero_jet(np.array([[1,2j],[.3,-.4j]])),spectral_parameter_jet=_zero_jet(-1))
    for key in args:
        with pytest.raises(ValueError):
            reflected_native_conormal_graph_jets(**dict(args,**{key:None}))
    with pytest.raises(ValueError):
        reflected_native_conormal_graph_jets(**dict(args,b_jet=_zero_jet(0)))
    with pytest.raises(ValueError):
        reflected_native_conormal_graph_jets(**dict(args,density_jet=_zero_jet(np.diag([1,-1]))))
    G=args['density_jet'].copy();G[3,0,1]=.1j
    with pytest.raises(ValueError):
        reflected_native_conormal_graph_jets(**dict(args,density_jet=G))
