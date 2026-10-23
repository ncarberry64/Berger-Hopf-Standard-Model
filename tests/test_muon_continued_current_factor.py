import numpy as np
from bhsm.interface.muon_continued_current_factor import midpoint_factor_coefficients,squared_current_inverse


def test_same_domain_squared_inverse_and_free_final_face():
    # Algebraic verification of the application; this is not a physical base.
    t=np.linspace(0,.7,9);N=np.linspace(.8,1.2,8);H=np.zeros((8,6,6),complex)
    H[:]=np.diag(np.arange(6)-2.5);c=midpoint_factor_coefficients(t,N,H,np.zeros_like(H))
    R=np.broadcast_to(np.eye(6),(8,6,6));L=R.copy();a=squared_current_inverse(c,0.,R,L)
    assert a['inverse_identity_max']<2e-14
    assert a['current_adjoint_pairing_max']<3e-15
    assert a['squared_original_residual_max']<2e-13
    assert np.linalg.norm(a['actual_free_final_value'])>.1
    assert np.max(abs(a['squared_final_face_residual']))<5e-13


def test_current_left_map_is_literal_not_conjugated():
    t=np.linspace(0,.2,5);N=np.ones(4);H=np.zeros((4,6,6),complex)
    c=midpoint_factor_coefficients(t,N,H,H);R=np.broadcast_to(np.eye(6),(4,6,6));L=(1+2j)*R
    a=squared_current_inverse(c,0,R,R);b=squared_current_inverse(c,0,R,L)
    np.testing.assert_allclose(b['literal_left_current_contraction'],(1+2j)*a['literal_left_current_contraction'],atol=2e-15)


def test_exact_linear_y_residual_blocks_have_both_nodal_contacts():
    rng=np.random.default_rng(71);t=np.linspace(0,.6,6);N=np.ones(5)
    H0=rng.normal(size=(5,6,6));H0=(H0+H0.swapaxes(-1,-2))/2
    H1=rng.normal(size=H0.shape);H1=(H1+H1.swapaxes(-1,-2))/2
    c=midpoint_factor_coefficients(t,N,H0,H1);e=1e-5
    cp=midpoint_factor_coefficients(t,N,H0+e*H1,np.zeros_like(H1))
    cm=midpoint_factor_coefficients(t,N,H0-e*H1,np.zeros_like(H1))
    np.testing.assert_allclose((cp['A0_diagonal']-cm['A0_diagonal'])/(2*e),c['A1_diagonal'],atol=2e-11)
    np.testing.assert_array_equal(c['A1_lower'],c['A1_diagonal'])
