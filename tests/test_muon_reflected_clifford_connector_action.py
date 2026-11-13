import numpy as np
from bhsm.interface.muon_reflected_clifford_connector_action import (
    reflected_clock_pair, reflected_connector_forms,
    reflected_derivative_green_identity)


def test_reflected_clock_vertical_and_oblique_principal():
    a=reflected_clock_pair(1.,1.,-1j)
    assert a['right_clock']==1 and a['reflected_clock']==1
    b=reflected_clock_pair(.7+.04j,.7-.04j,2.-3j)
    np.testing.assert_allclose(b['reflected_clock'],b['right_clock'].conjugate())
    np.testing.assert_allclose(b['paired_principal'],1/abs(b['right_clock'])**2)
    assert abs(b['left_boundary_ratio']-1)>0.1


def test_independent_source_square_and_both_placements():
    rng=np.random.default_rng(30)
    H=np.diag([.3,.8]);T=np.diag([.2,.7,.9])
    x=rng.normal(size=(2,3,2))+1j*rng.normal(size=(2,3,2))
    r=rng.normal(size=(2,2,3))+1j*rng.normal(size=(2,2,3))
    xs=(x.real-1j*x.imag)*np.array([1.+.3j,.7-.1j])[:,None,None]
    rs=(r.real-1j*r.imag)*np.array([1.+.3j,.7-.1j])[:,None,None]
    branches=lambda t:(H,T,1.,H,T,1.)
    sources=lambda t:(x,r,xs,rs)
    f=reflected_connector_forms([(branches,sources,0j,-1j)],current=np.eye(2),cells_per_segment=1)
    # Direct independent unsquared block integration; coefficient tangents
    # are the same complex numbers on both branches, not their conjugates.
    def integrated(a,b):
        gx,gw=np.polynomial.legendre.leggauss(4);result=np.zeros((10,10),complex)
        for z,w in zip(gx,gw):
            p=[(1-z)/2,(1+z)/2];d=[-1,1]
            hr=np.block([[H,a*r[0]+b*r[1]],[a*x[0]+b*x[1],T]])
            hl=np.block([[H,a*rs[0]+b*rs[1]],[a*xs[0]+b*xs[1],T]])
            for j in range(2):
                for k in range(2):
                    result[5*j:5*j+5,5*k:5*k+5]+=w/2*(d[j]*np.eye(5)+p[j]*hl)@(d[k]*np.eye(5)+p[k]*hr)
        return result
    idxs=np.array([0,1,5,6]);idxt=np.array([2,3,4,7,8,9])
    eps=2e-4
    da=(integrated(eps,0)-integrated(-eps,0))/(2*eps)
    dab=(integrated(eps,eps)-integrated(eps,-eps)-integrated(-eps,eps)+integrated(-eps,-eps))/(4*eps**2)
    np.testing.assert_allclose(f['magnetic_delta_K10'][0],da[np.ix_(idxt,idxs)],atol=1e-12)
    np.testing.assert_allclose(f['magnetic_delta_K01'][0],da[np.ix_(idxs,idxt)],atol=1e-12)
    np.testing.assert_allclose(f['source_square_contact'][0,1],dab[np.ix_(idxs,idxs)],atol=2e-9)


def test_green_boundary_has_independent_clock_contact():
    gx,gw=np.polynomial.legendre.leggauss(32);s=(gx+1)/2;weights=gw/2
    w=1+.2j*s;ws=1-.2j*s
    l=(1+s)[:,None];r=(2-s*s)[:,None]
    a=reflected_derivative_green_identity(w,ws,np.full_like(s,.2j,dtype=complex),np.full_like(s,-.2j,dtype=complex),
            l,np.ones_like(l),r,(-2*s)[:,None],weights)
    boundary=(1+.2j)/(1-.2j)*2-2
    np.testing.assert_allclose(a['boundary_derivative_integral'],boundary,atol=2e-14)
    assert abs(a['clock_contact_integral'])>.1
