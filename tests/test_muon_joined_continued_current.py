import numpy as np
from bhsm.interface.muon_continued_current_factor import midpoint_factor_coefficients
from bhsm.interface.muon_joined_continued_current import join_current_coefficients,joined_squared_current_application


def fixture():
    n=5;H=np.zeros((n,6,6),complex);H[:]=np.diag(np.arange(6)*.2)
    c=midpoint_factor_coefficients(np.linspace(0,.3,n+1),np.ones(n),H,H*0)
    c.update(source_right_map=np.broadcast_to(np.eye(6),(n,6,6)),target_left_map=np.broadcast_to(np.eye(6),(n,6,6)),
        canonical_Gram_I6=np.eye(6),family_indices=np.arange(18).reshape(3,6),family_Y=np.arange(3),alpha6=np.zeros((3,6,6)),
        common_Hcan0=H,common_Hcan1=H*0,R4=np.ones(n),N=np.ones(n))
    return c


def test_join_retains_child_initial_trace_and_boundary_return():
    c=fixture();j=join_current_coefficients(c,c,np.eye(6));a=joined_squared_current_application(j)
    assert a['first_order_identity_max']<2e-14
    assert a['boundary_reconstruction_identity_max']<2e-14
    assert a['current_boundary_decomposition_max']<1e-14
    assert a['current_source_adjoint_max']<2e-15
    assert np.linalg.norm(a['actual_outgoing_initial_trace'])>.1
    assert np.linalg.norm(a['current_boundary_return'])>.1


def test_transported_birth_target_and_squared_form_use_same_unitary():
    c=fixture();T=np.diag(np.exp(1j*np.arange(6)*.3));j=join_current_coefficients(c,c,T)
    a=joined_squared_current_application(j)
    np.testing.assert_allclose(a['actual_outgoing_initial_trace'],T@a['actual_birth_canonical_trace'])
    assert a['boundary_reconstruction_identity_max']<2e-14
    assert a['current_source_adjoint_max']<2e-15
