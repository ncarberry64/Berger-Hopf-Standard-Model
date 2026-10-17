import numpy as np
from bhsm.interface.muon_exact_stored_phase_reset_value import exact_stored_phase_reset_value


def test_independent_transpose_full_phase_port_keeps_original_coefficients():
    K=np.array([[2+.1j,.3,-.2],[.5,1.4-.2j,.6],[.2,-.1,1.7]],complex)
    rhs=np.eye(3,dtype=complex);theta=np.array([.8+.3j,-.2,1.1])
    app=dict(projection=dict(saddle=K,saddle_rhs=rhs,analytic_temporal_dual=theta,
        common_trace_map=np.eye(3),common_trace_cotangent=np.linalg.solve(K,rhs).T@theta),
        residual=np.zeros(226,complex),groups=dict(common_attachment_temporal_dual=[223,224],common_normal_temporal_dual=[225]))
    # The actual attachment map is also applied; check the direct common
    # port before that fixed row chart is introduced.
    a=exact_stored_phase_reset_value(app,np.zeros(37))
    direct=np.linalg.solve(K.T,theta)
    assert np.max(abs(a['common_port_high']-direct))<2e-15
    assert a['exact_stored_primal_rows_upper']<1e-45
    assert a['exact_stored_transpose_rows_upper']<1e-45
    assert np.array_equal(a['stored_saddle'],K)
    assert np.array_equal(a['unchanged_temporal_dual'],theta)
    assert np.linalg.norm(direct-np.linalg.solve(K.conj().T,theta))>.01
