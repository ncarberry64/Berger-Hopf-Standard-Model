import numpy as np
from bhsm.interface.muon_reset_constrained_canonical_variation import canonical_variation_embedding
from bhsm.interface.muon_reset_secondary_canonical_source import secondary_compatible_action_source


def test_secondary_conditions_include_direct_source_and_do_not_zero_normal_force():
    H=np.diag([4,5,6,7,8,9,10]).astype(complex);H[0,3]=H[3,0]=.2j;H[1,4]=H[4,1]=.3
    x=np.arange(3);v=3+x;y=np.array([6]);a=canonical_variation_embedding(H,x,v,y,np.zeros((0,4)),source_gradient=np.ones(7)*.03j)
    B=np.zeros((1,7));B[0,0]=1;Bt=np.zeros_like(B);Bt[0,1]=.1;N=np.zeros(7);N[1]=1;Nt=np.zeros(7);Nt[2]=.2
    t=secondary_compatible_action_source(H,a,B,Bt,N,Nt,np.zeros((0,7)),normal_amplitude=1,normal_rate=.3,
        trace_source=np.array([.2]),trace_source_rate=np.array([-.1j]),normal_source=.04j,normal_source_rate=.1)
    d=t['original_master_direction']
    np.testing.assert_allclose(B@d+.2,0,atol=2e-15)
    np.testing.assert_allclose(Bt@d+B[:,x]@d[v]-.1j,0,atol=2e-15)
    np.testing.assert_allclose(N@d+.04j,1,atol=2e-15)
    np.testing.assert_allclose(Nt@d+N[x]@d[v]+.1,.3,atol=2e-15)
    assert abs(t['normal_primary_force'])>1
    assert np.max(abs(t['original_rows']))<2e-15
    assert np.max(abs(t['true_quadratic_stationarity_rows']))<2e-15
