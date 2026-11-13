import numpy as np
from bhsm.interface.muon_common_y_current_response import block_bidiagonal, common_y_inverse_action
from bhsm.interface.muon_joined_common_y_current import block_current_coefficients, rectangular_block_source_jet, midpoint_current_coefficients


def test_block_solve_matches_independent_noncommuting_dense_action_and_jet():
    rng = np.random.default_rng(428)
    d = np.array([3*np.eye(2)+.1*rng.normal(size=(2,2))+1j*np.eye(2) for _ in range(5)])
    l = .1*rng.normal(size=d.shape)
    b = .1*rng.normal(size=d.shape)
    c = .1*rng.normal(size=d.shape)
    r = rng.normal(size=(1,5,2,3)).astype(complex)
    u = block_current_coefficients(d,l,b,c,r)
    actual = common_y_inverse_action(block_bidiagonal(d,l), block_bidiagonal(b,c), r.reshape(1,10,3))
    np.testing.assert_allclose(u['coefficients'].reshape(5,10,3), actual['coefficients'], rtol=5e-15, atol=2e-16)
    direction = rng.normal(size=(2,5,2,2))*.1
    jet = rectangular_block_source_jet(u['coefficients'], d,l,b,c,direction,direction)
    y = .02
    A = block_bidiagonal(d+y*b,l+y*c)
    D = block_bidiagonal(direction[0]+y*direction[1],direction[0]+y*direction[1])
    direct = -np.linalg.solve(A,D@np.linalg.solve(A,r[0].reshape(10,3)))
    polynomial = sum(y**k*v.reshape(10,3) for k,v in enumerate(jet['coefficients']))
    np.testing.assert_allclose(polynomial,direct,rtol=1e-10,atol=1e-12)


def test_birth_frame_current_uses_transported_preceding_trace():
    u = np.arange(16).reshape(1,4,2,2).astype(complex)
    T = np.array([[0,1],[-1,0]],complex)
    L = np.repeat(np.eye(2)[None],4,axis=0)
    value = midpoint_current_coefficients(L,np.ones(4),u,birth_index=2,birth_transport=T)
    direct = (u[0,0]+u[0,1]+u[0,0]+u[0,2]+T@u[0,1]+u[0,3]+u[0,2])/2
    np.testing.assert_array_equal(value[0],direct)
