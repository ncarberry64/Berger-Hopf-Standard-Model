import numpy as np
from bhsm.interface.muon_common_graph_radial_matching import common_graph_radial_application


def test_common_graph_source_and_transpose_keep_algebraic_frames_and_both_directed_returns():
    D=np.array([[[4,.2,0],[.1,2,1],[0,1,0]],[[5,.3,0],[.4,3,1],[0,1,0]],[[6,.5,0],[.2,4,1],[0,1,0]]],complex)
    U=np.zeros((2,3,3),complex);L=U.copy();U[:,0,0]=-.3;L[:,0,0]=-.2
    R=np.array([[1+.2j],[0],[0]]);SL=np.array([[.4-.3j],[0],[0]])
    a=common_graph_radial_application(D,U,L,R,SL,birth_index=1,gauss_count=1,field_count=2)
    full=np.zeros((9,9),complex)
    for i in range(3):full[3*i:3*i+3,3*i:3*i+3]=D[i]
    for i in range(2):full[3*i:3*i+3,3*i+3:3*i+6]=U[i];full[3*i+3:3*i+6,3*i:3*i+3]=L[i]
    rhs=np.zeros((9,1),complex);lhs=rhs.copy();rhs[3:6]=R;lhs[3:6]=SL
    np.testing.assert_allclose(a['full_field_response'].reshape(9,1),np.linalg.solve(full,rhs),atol=2e-15)
    np.testing.assert_allclose(a['full_literal_adjoint'].reshape(9,1),np.linalg.solve(full.T,lhs),atol=2e-15)
    assert np.max(abs(a['source_transpose_pairing_difference']))<2e-15
    assert np.linalg.norm(a['named_frame_reactions'])>1e-3
