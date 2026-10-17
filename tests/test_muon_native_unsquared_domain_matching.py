import numpy as np
from bhsm.interface.muon_native_unsquared_domain_matching import native_unsquared_domain_matching


def _application(body=lambda t:np.diag([.3,-.4,.2,.5,-.3,.6])+t*np.ones((6,6))*.2):
    q=[];xs,weights=np.polynomial.legendre.leggauss(5);n=5
    for edge in range(n-1):
        for x,weight in zip((xs+1)/2,weights/2):
            t=(edge+x)/(n-1);H=body(t).astype(complex);w=1.+.1j*t
            q.append(dict(rows=((edge,1-x,-(n-1)),(edge+1,x,n-1)),
                H=H,Hsharp=H.conj().T,R=1.,Rsharp=1.,right_clock=w,reflected_clock=w.conjugate(),
                measure=weight/(n-1),original_holomorphic_measure=w*weight/(n-1),t=t))
    def source(q):
        J=np.eye(6)[:,:2]*(1.+q['t']**2+.3j*q['t'])
        return J,(np.diag(np.arange(1,7))@J).T
    return native_unsquared_domain_matching(q,temporal_nodes=n,angular_derivatives=np.zeros((3,1,1)),
        alpha=np.zeros((3,6,6)),source_sampler=source)


def test_actual_source_range_contacts_and_literal_transpose_identity():
    r=_application()
    for measure in('geometric','analytic'):
        np.testing.assert_allclose(r[measure+'_current'],r[measure+'_independent_transpose_current'],rtol=1e-12,atol=2e-14)
        np.testing.assert_allclose(r[measure+'_original_weak_rows'],0,atol=2e-14)
        np.testing.assert_allclose(r[measure+'_original_transpose_rows'],0,atol=2e-14)
    np.testing.assert_allclose(r['range_identity_original_row_residual'],0,atol=3e-14)
    assert np.linalg.norm(r['acted_source_range_contact'])>1e-4
    assert np.linalg.norm(r['geometric_factor_current']-r['geometric_current'])>1e-4
    assert np.linalg.norm(r['analytic_current']-r['geometric_current'])>1e-4


def test_source_inside_derivative_image_restores_first_order_factorization():
    # A=partial_t, so a constant source belongs exactly to the piecewise
    # derivative range. This contrasts the variable-source control above.
    q=[]
    for edge in range(3):
        for x,wt in zip((np.array([-np.sqrt(3/5),0,np.sqrt(3/5)])+1)/2,np.array([5/18,4/9,5/18])):
            q.append(dict(rows=((edge,1-x,-3),(edge+1,x,3)),H=np.zeros((6,6)),Hsharp=np.zeros((6,6)),
                R=1.,Rsharp=1.,right_clock=1.,reflected_clock=1.,measure=wt/3,original_holomorphic_measure=wt/3))
    J=np.eye(6)[:,:1]
    r=native_unsquared_domain_matching(q,temporal_nodes=4,angular_derivatives=np.zeros((3,1,1)),
        alpha=np.zeros((3,6,6)),source_sampler=lambda q:(J,J.T))
    np.testing.assert_allclose(r['native_factor_response'],r['geometric_weak_response'],rtol=1e-13,atol=1e-14)
    np.testing.assert_allclose(r['geometric_factor_weak_equation_defect'],0,atol=1e-14)
