"""Independent finite algebra controls; no physical state selected."""
import numpy as np
from scipy.linalg import eigh
from scipy.integrate import quad
from bhsm.interface.muon_changing_magnetic_open_exchange import (
    magnetic_three_green_kernel,gaussian_spectral_direction,_vertex_sources)


def test_three_green_matches_independent_laplace_convolution():
    # CONTROL_ONLY non-infinitesimal, repeated and widely separated spectra.
    for p in ((2.,3.,7.),(2.,2.,7.),(2.,2.00000001,7.),(2.,2.1,2.15),(1e-2,2.,50.)):
        c=.17
        # Total-time convolution is the second divided difference of g.
        gap=abs(p[0]-p[1]);low=min(p[:2])
        def convolution(s):
            return quad(lambda t:np.exp(-p[2]*(s-t)-low*t)*(t if gap==0 else -np.expm1(-gap*t)/gap),
                0,s,epsabs=1e-13,epsrel=1e-12)[0]
        expected=1/np.prod(p)-quad(convolution,0,c,epsabs=2e-12,epsrel=2e-12)[0]
        r=magnetic_three_green_kernel(*p,cutoff=c)
        assert abs(float(r['value'])-expected)<=r['absolute_approximation_upper']+2e-11*expected


def _graph(P,B,G,L,R,c):
    f,U=eigh(P);b,V=eigh(B,G)
    ll=np.einsum('ifa,fI,aA->iIA',L,U,V)
    rr=np.einsum('fI,fja,aA->IjA',U.conj(),R,V)
    from bhsm.interface.muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel
    k=temporal_image_green_kernel(f[:,None],b[None,:],cutoff=c)['value']
    return -np.einsum('iIA,IjA,IA->ij',ll,rr,k)


def test_all_gaussian_placements_and_field_gram_contacts_literal_fd():
    # CONTROL_ONLY complex non-Hermitian left/right; no forced adjoint.
    rng=np.random.default_rng(174);f=np.array([2.,4.]);b=np.array([.6,1.1,6.])
    L=rng.normal(size=(2,2,3))+1j*rng.normal(size=(2,2,3))
    R=rng.normal(size=(2,2,3))+1j*rng.normal(size=(2,2,3))
    dL=rng.normal(size=L.shape)+1j*rng.normal(size=L.shape)
    dR=rng.normal(size=R.shape)+1j*rng.normal(size=R.shape)
    A=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2));dF=(A+A.conj().T)/2
    A=rng.normal(size=(3,3));dB=(A+A.T)/2
    A=rng.normal(size=(3,3));dG=(A+A.T)/2
    for c in (0.,.13):
        result=gaussian_spectral_direction(f,b,L,R,dF,dB,dL,dR,cutoff=c,dGb=dG)
        h=1e-6
        actual=(_graph(np.diag(f)+h*dF,np.diag(b)+h*dB,np.eye(3)+h*dG,L+h*dL,R+h*dR,c)-
            _graph(np.diag(f)-h*dF,np.diag(b)-h*dB,np.eye(3)-h*dG,L-h*dL,R-h*dR,c))/(2*h)
        np.testing.assert_allclose(result['total'],actual,rtol=2e-7,atol=2e-7)
        assert np.linalg.norm(result['field_Gram_current'])>0
        assert np.linalg.norm(result['field_operator'])>0


def test_zero_cutoff_gram_cancels_in_original_coordinates():
    # CONTROL_ONLY inverse K, hence field Gram must cancel exactly.
    rng=np.random.default_rng(3);f=np.array([2.,5.]);b=np.array([3.,7.])
    L=rng.normal(size=(1,2,2));R=rng.normal(size=(2,1,2));dG=np.array([[.2,.3],[.3,-.4]])
    z=np.zeros((2,2));out=gaussian_spectral_direction(f,b,L,R,z,z,np.zeros_like(L),np.zeros_like(R),dGb=dG)
    np.testing.assert_allclose(out['total'],0,atol=2e-17)


def test_literal_left_does_not_conjugate_temporal_vertex():
    # CONTROL_ONLY Haar1 angular data, anti-Hermitian temporal insertion.
    images={'gaunt_even_odd_source':np.ones((1,1,4))}
    U=np.array([[1j]]);F=np.array([[[2.]]]);V=np.array([[[1j]]])
    r,l=_vertex_sources(F,V,U,'even','even',np.array([0]),images,0)
    assert r[0,0,0]==-2 and l[0,0,0]==2
    assert l[0,0,0]!=r[0,0,0].conjugate()
