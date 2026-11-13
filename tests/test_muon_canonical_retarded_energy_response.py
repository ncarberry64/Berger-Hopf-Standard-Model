import numpy as np
import pytest
from scipy.linalg import expm
from bhsm.interface.muon_canonical_retarded_energy_response import canonical_retarded_energy_response,static_normal_frame_energy_identity


def test_actual_retarded_energy_jet_matches_entire_pole_safe_integral():
    H=np.array([[.7,.13j],[-.13j,-.4]]);N=1.2;L=.37;E=.71
    evaluator=lambda t:dict(H_can=H,N=N,Omega_tau=np.zeros((2,2)))
    r=canonical_retarded_energy_response(evaluator,(0,L),E,rtol=2e-12,atol=2e-14)
    actual=static_normal_frame_energy_identity(H,E,N*L)
    np.testing.assert_allclose(r['retarded_energy_response'],actual['finite_retarded_energy_response'],atol=3e-13)
    eps=1e-5
    delta=(static_normal_frame_energy_identity(H,E+eps,N*L)['finite_retarded_energy_response']-static_normal_frame_energy_identity(H,E-eps,N*L)['finite_retarded_energy_response'])/(2*eps)
    np.testing.assert_allclose(r['retarded_energy_first_jet'],delta,atol=2e-11)
    np.testing.assert_allclose(r['canonical_propagator'],expm(-1j*N*L*H),atol=3e-13)
    assert r['static_Fourier_pencil_or_infinite_endpoint_limit_assumed']is False


def test_exact_rest_pole_needs_no_prescribed_width_or_inverse():
    r=static_normal_frame_energy_identity(np.diag([.5,-.5]),.5,.2)
    np.testing.assert_allclose(r['finite_retarded_energy_response'][0,0],-.2j,atol=1e-16)
    np.testing.assert_allclose(r['finite_source_equation_remainder'],0,atol=2e-16)
    np.testing.assert_allclose(r['numerator_product_difference'],0,atol=0)


def test_temporal_frame_and_noncommuting_current_are_not_dropped():
    H=np.array([[.4,.07],[.07,-.2]]);O=1j*np.diag([.3,-.1]);N=.8
    r=canonical_retarded_energy_response(lambda t:dict(H_can=H,N=N,Omega_tau=O),(0,.2),.4)
    np.testing.assert_allclose(r['temporal_unitary_frame'],expm(-N*.2*O),atol=2e-13)
    assert np.linalg.norm(r['temporal_normal_frame_retarded_response']-r['retarded_energy_response'])>1e-3


def test_incomplete_nonhermitian_or_reverse_interval_is_rejected():
    good=lambda t:dict(H_can=np.eye(2),N=1,Omega_tau=np.zeros((2,2)))
    with pytest.raises(ValueError):canonical_retarded_energy_response(good,(1,0),1)
    with pytest.raises(ValueError):canonical_retarded_energy_response(lambda t:dict(H_can=np.array([[1,1j],[0,1]]),N=1,Omega_tau=np.zeros((2,2))),(0,1),1)
