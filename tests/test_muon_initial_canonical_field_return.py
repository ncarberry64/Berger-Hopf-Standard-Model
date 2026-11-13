import numpy as np
from bhsm.interface.muon_initial_canonical_field_return import initial_canonical_field_return


def test_actual_Cauchy_recurrence_and_literal_adjoint_keep_Gauss_and_frame():
    n=8;d=5;field=4;At=1;h=.1
    # At is algebraic; x/y are dynamic; coordinate3 is the named frame.
    C=np.eye(field)[[3]];D=np.zeros((n,d,d),complex)
    U=np.zeros((n-1,d,d),complex);L=U.copy()
    H01=np.zeros((field,field),complex)
    H01[1:3,1:3]=-np.eye(2)/h
    for j in range(n):
        D[j,0,0]=2.;D[j,1:3,1:3]=np.eye(2)*(2/h if j<n-1 else 1/h)
        D[j,3,3]=1.;D[j,3,4]=D[j,4,3]=1.
        # Nonsymmetric complex original harmonic chart, independent dual.
        D[j,1,2]+=.1j;D[j,2,1]-=.1j
        D[j,0,1]=.04;D[j,1,0]=.07
        if j<n-1:U[j,1:3,1:3]=L[j,1:3,1:3]=-np.eye(2)/h
    b=np.zeros((n,d,2),complex);b[3,1:3]=np.array([[1,.2j],[.1,1]])
    left=np.zeros_like(b);left[5,1:3]=np.array([[.3j,1],[1,-.2j]])
    r=initial_canonical_field_return(D,U,L,b,left,H01,
        frame_rows=C,gauss_count=At,field_count=field)
    x=r['initial_canonical_response']
    # Initial p=0 gives x1=0, then the original second-order equations
    # propagate exact zero until the birth impulse row is reached.
    np.testing.assert_allclose(x[:4,:field],0.,atol=3e-15)
    np.testing.assert_allclose(r['initial_admissible_conormal'],0.,atol=2e-14)
    np.testing.assert_allclose(r['original_action_rows'],r['expected_original_action_boundary_rows'],atol=4e-14)
    np.testing.assert_allclose(r['original_transpose_rows'],r['expected_original_transpose_boundary_rows'],atol=5e-14)
    np.testing.assert_allclose(r['source_transpose_pairing_difference'],0.,atol=4e-14)
    np.testing.assert_allclose(x[:,3],0.,atol=2e-15)
    np.testing.assert_allclose(r['original_action_rows'][:,0],0.,atol=2e-15)
    assert np.linalg.norm(r['final_dynamic_force'])>0
    assert r['final_source_to_initial_conormal_numeric_rank']==2
