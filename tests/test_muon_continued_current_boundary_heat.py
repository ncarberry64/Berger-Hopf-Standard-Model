"""Independent mathematical checks; small arrays are numerical fixtures."""
import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_continued_current_boundary_heat import (
    temporal_variable_gram, spectral_action_factor, regulated_inverse_action,
    magnetic_regulated_action, boundary_regulated_current, boundary_resolvent_schur)


def test_temporal_gram_equals_integral_of_linear_coefficients():
    w = np.array([.2,.5,.3])
    x = np.array([.7,-.4,1.2])
    v = np.r_[0.,x]
    integral = sum(h*(a*a+a*b+b*b)/3 for h,a,b in zip(w,v[:-1],v[1:]))
    assert abs(x@temporal_variable_gram(w,1)@x-integral)<2e-16
    assert temporal_variable_gram(w,1)[-1,-1]==w[-1]/3


def test_regulated_generalized_inverse_matches_matrix_exponential():
    A = np.array([[2+1j,0],[.4j,3-.2j]])
    w = np.array([.2,.4])
    f = spectral_action_factor(A,w,1)
    R = np.array([[.3+.1j],[.5j]])
    B = A.conj().T@(w[:,None]*R)
    for c in (0.,.17):
        expected = expm(-c*np.linalg.solve(f['M'],f['K']))@np.linalg.solve(f['K'],B)
        assert np.allclose(regulated_inverse_action(f,B,c),expected,rtol=2e-13,atol=2e-15)


def test_rectangular_square_and_numerator_equal_full_directional_derivative():
    A0 = np.array([[2+1j,0],[.4j,3-.2j]])
    A1 = np.array([[1.7+.2j,0],[.3,2.6-.1j]])
    w = np.array([.2,.4])
    d10 = np.array([[.2j,.1],[.3,.2-.4j]])
    d01 = np.array([[.1,.5j],[.2j,.3]])
    R = np.array([[.3+.1j],[.5j]])
    s,t = spectral_action_factor(A0,w,1),spectral_action_factor(A1,w,1)
    result = magnetic_regulated_action(s,t,R,d10,d01,c=.13)
    def apply(eps):
        A = np.block([[A0,eps*d01],[eps*d10,A1]])
        M = np.block([[s['M'],np.zeros((2,2))],[np.zeros((2,2)),t['M']]])
        G = np.r_[w,w]
        K = A.conj().T@(G[:,None]*A)
        rhs = A.conj().T@(G[:,None]*np.r_[R,np.zeros_like(R)])
        return (expm(-.13*np.linalg.solve(M,K))@np.linalg.solve(K,rhs))[2:]
    difference = (apply(1e-5)-apply(-1e-5))/(2e-5)
    assert np.allclose(result['response'],difference,rtol=2e-8,atol=2e-10)
    zero = magnetic_regulated_action(s,t,R,d10,d01,c=0.)
    assert np.allclose(zero['response'],zero['c0_direct_inverse_derivative'],rtol=3e-13,atol=3e-15)
    assert np.linalg.norm(zero['numerator_contact'])>0


def test_boundary_return_uses_frequency_dependent_mass_schur():
    A = np.array([[2+1j,0],[.4j,3-.2j]])
    w = np.array([.2,.4])
    f = spectral_action_factor(A,w,1)
    R = np.array([[.3+.1j],[.5j]])
    L = np.array([[.5,.2j]])
    zero = boundary_regulated_current(f,R,L,c=0.,dimension=1)
    assert np.allclose(zero['full_response'],np.linalg.solve(A,R),rtol=2e-13,atol=2e-15)
    regulated = boundary_regulated_current(f,R,L,c=.19,dimension=1)
    assert np.allclose(regulated['current_full'],
        regulated['current_Dirichlet_reference']+regulated['current_boundary_return'])
    for z in (.1j,-.3):
        pencil=f['K']-z*f['M']
        schur=boundary_resolvent_schur(f,z,dimension=1)
        assert np.allclose(np.linalg.det(pencil),np.linalg.det(pencil[:-1,:-1])*np.linalg.det(schur))
    assert not np.allclose(boundary_resolvent_schur(f,0,dimension=1),
        boundary_resolvent_schur(f,.1j,dimension=1))
