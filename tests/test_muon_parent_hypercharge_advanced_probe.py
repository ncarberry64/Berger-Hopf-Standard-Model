import numpy as np
from bhsm.interface.muon_parent_hypercharge_advanced_probe import boundary_probe_on_support


def test_advanced_zero_terminal_and_boundary_reciprocity_for_nonsymmetric_gyro():
    M=np.array([[2.,.1,.3],[.1,1.,.2],[.3,.2,3.]])
    N=np.array([[.2,.4,.3],[-.2,.1,.6],[-.1,-.3,.2]])
    K=np.array([[3.,.2,.1],[.2,4.,.4],[.1,.4,2.]])
    args=dict(M=M,N=N,K=K,source_duration=.7,time_steps=256)
    r=boundary_probe_on_support(**args)
    z=boundary_probe_on_support(**args,reversed_time=True)
    np.testing.assert_array_equal(z['original_time_state'][-1],0.)
    np.testing.assert_array_equal(z['original_time_velocity'][-1],0.)
    np.testing.assert_array_equal(z['N'],-N)
    assert abs(r['boundary_trace_contraction']-z['boundary_trace_contraction'])<1e-9
    assert r['interior_residual_max']<1e-12
    assert z['interior_residual_max']<1e-12
    assert not z['physical_Pauli_evaluated']
