"""CONTROL_ONLY matrix tests of the transported Ward/amputation identity."""
import numpy as np
import pytest
from scipy.linalg import expm
from bhsm.interface.muon_transported_longitudinal_ward import localized_ward_pairing
from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def test_localized_matrix_identity_keeps_both_distinct_external_euler_placements():
    H0=np.array([[.4,.2+.3j],[.2-.3j,-.7]])
    Hn=np.array([[.2,.4j,0],[-.4j,.8,.3],[0,.3,-.6]])
    T=np.array([[.2j,.3],[.4,-.7j],[.8+.2j,-.1]])
    Tr=np.array([[.3,.2j],[-.1j,.2],[.4,-.6j]])
    N=.7;t=.31;U0=expm(-1j*N*H0*t);Un=expm(-1j*N*Hn*t)
    r=localized_ward_pairing(H0,Hn,T,Tr,U0,Un,lapse=N,localization=.4,localization_rate=-.8)
    np.testing.assert_allclose(r['point_identity_residual'],0,atol=3e-16)
    np.testing.assert_allclose(r['external_Euler_source'],0,atol=2e-16)
    assert np.linalg.norm(r['current'])>.1 and np.linalg.norm(r['localization_amputation'])>.1
    # A common-birth inherited trace merely multiplies the fundamental map;
    # the theorem does not require selecting its column or making its graph I.
    inherited_right=np.array([[.2,.4j],[-.3j,.7]])
    inherited_left=np.array([[.1,.3j],[-.4j,.2],[.8,-.6]])
    np.testing.assert_allclose(inherited_left.conj().T@r['point_identity_residual']@inherited_right,0,atol=3e-16)
    # Independent differentiation of the entire localized transported product.
    h=1e-6
    f=lambda s:(.4-.8*s)*expm(1j*N*Hn*(t+s))@(T+s*Tr)@expm(-1j*N*H0*(t+s))
    np.testing.assert_allclose((f(h)-f(-h))/(2*h),r['endpoint_derivative'],rtol=5e-10,atol=8e-11)


def test_constant_hamiltonian_orbit_current_only_vanishes_after_amputation():
    H0=np.diag([.2,-.3]);Hn=np.array([[.4,.1j],[-.1j,.7]])
    T=np.array([[1j,.2],[-.4,.5j]])
    z,w=np.polynomial.legendre.leggauss(32);current=np.zeros((2,2),complex);amp=current.copy()
    for t,weight in zip((z+1)/2,w/2):
        r=localized_ward_pairing(H0,Hn,t*(1-t)*T,(1-2*t)*T,
            expm(-1j*H0*t),expm(-1j*Hn*t),lapse=1.,localization=t*(1-t),localization_rate=1-2*t)
        current+=weight*r['current'];amp+=weight*r['localization_amputation']
    assert np.linalg.norm(current)>.001
    np.testing.assert_allclose(current+amp,0,atol=2e-16)


def test_nonhermitian_lorentz_operator_cannot_be_used_for_unitary_external_ward_claim():
    with pytest.raises(ValueError,match='Hermitian'):
        localized_ward_pairing(np.array([[1j]]),np.eye(1),np.eye(1),np.eye(1),np.eye(1),np.eye(1),
            lapse=1.,localization=1.,localization_rate=0.)


def test_consumed_wall_radial_profile_has_nonzero_trace():
    radial=ghost_radial_values([WALL])[0]
    assert radial[0,0]==0.  # The interior profile cannot test the wall current.
    assert radial[1,0]==1.
