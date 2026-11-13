import numpy as np
from scipy.linalg import expm

from bhsm.interface.muon_d5_pole_admissibility import (
    original_n0_pole_indicial,frobenius_regular_seed,propagate_regular_frame,
    regular_frame_at,pole_boundary_rows,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule


def test_original_pole_exponents_and_positive_cauchy_exclusion():
    full=full_d5_localized_lepton_trace()
    for branch in ('particle','conjugate'):
        for eps in (-1,1):
            a=original_n0_pole_indicial(full['gamma5D_'+branch],sheet_orientation=eps)
            A,P,Q=(a[k] for k in ('indicial','regular_projector','singular_projector'))
            np.testing.assert_allclose(A@P,P,atol=0)
            np.testing.assert_allclose(A@Q,-2*Q,atol=0)
            np.testing.assert_allclose(P+Q,np.eye(64),atol=0)
            assert np.linalg.matrix_rank(P)==np.linalg.matrix_rank(Q)==32
            # Norm power is3+2lambda, and integrability requires power>-1.
            assert 3+2*int(a['regular_exponent'])>-1
            assert 3+2*int(a['singular_exponent'])==-1
            np.testing.assert_array_equal(a['indicial_source'],np.zeros((64,64)))


def test_actual_frobenius_recursion_and_independent_regular_frame_derivative():
    A=np.diag([1.,-2.]);P=np.diag([1.,0.]);G0=np.diag([.2,-.3]);Gx=np.diag([.1,.4])
    epsilon=1e-5
    seed=frobenius_regular_seed(A,P,G0,Gx,epsilon=epsilon)
    np.testing.assert_allclose(seed['original_first_recursion_rows'],0,atol=0)
    b=np.linspace(epsilon,5*epsilon,5);nodes,_,_,_=_collocation_rule(3)
    radii=b[:-1,None]+np.diff(b)[:,None]*nodes
    gs=np.array([[(A-np.eye(2))/r+G0 for r in row] for row in radii])
    gxs=np.broadcast_to(Gx,gs.shape)
    app=propagate_regular_frame(b,gs,gxs,seed['regular_seed'],seed['regular_seed_source'])
    r=3.4*epsilon;v=regular_frame_at(app,r)
    exact=r*np.exp(.2*(r-epsilon))*(1+.2*epsilon)
    np.testing.assert_allclose(v['value'][:,0],[exact,0],rtol=3e-15,atol=1e-18)
    residual=v['radial']-(A/r+G0)@v['value']
    np.testing.assert_allclose(residual,0,atol=3e-15)


def test_boundary_law_keeps_regular_amplitudes_and_its_full_source():
    Y=np.array([[1.,.2],[.3,1.1],[-.2,.4],[.7,-.1]])
    Yx=np.array([[.04,-.03],[.1,.2],[-.3,.1],[.03,.01]])
    rows=pole_boundary_rows(Y,Yx)
    np.testing.assert_allclose(rows['original_regular_rows'],0,atol=2e-16)
    np.testing.assert_allclose(rows['original_regular_source_rows'],0,atol=2e-16)
    h=1e-20
    p=rows['regular_pivot_rows'];free=rows['dependent_rows']
    def law(s):
        Z=Y+s*Yx;B=np.eye(4,dtype=complex)[free].copy()
        B[:,p]=-np.linalg.solve(Z[p].T,Z[free].T).T
        return B
    np.testing.assert_allclose(law(1j*h).imag/h,rows['boundary_source'],atol=8e-17,rtol=3e-14)
