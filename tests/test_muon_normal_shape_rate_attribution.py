import numpy as np
from bhsm.interface.muon_normal_shape_rate_attribution import bounded_normal_shape_rate_attribution


def test_fixed_rhs_and_literal_original_target_stay_distinct():
    rng=np.random.default_rng(233);n=2;m=1
    H=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5));H[2:,2:]+=4*np.eye(3)
    G=rng.normal(size=5)+1j*rng.normal(size=5);v=rng.normal(size=2);clock=rng.normal(size=5)*.1
    F=np.array([[.2,1.,-.3]],complex);K=np.block([[H[n:,n:],F.T],[F,np.zeros((1,1))]])
    rhs=np.r_[np.r_[G[:n],0]-H[n:,:n]@v-clock[n:],0];rhs[0]+=1e-7
    z=np.linalg.solve(K,rhs)
    a=bounded_normal_shape_rate_attribution(H,G,v,clock,F,rhs,z)
    assert a['fixed_rhs']['exact_stored']['bordered_residual_upper']<1e-28
    assert a['fixed_rhs']['stored_rhs_assembly_difference_upper']>9e-8
    assert np.max(abs(a['exact_assembly_minus_stored_rhs']))>9e-8
    assert a['exact_assembly_bordered_upper']<1e-28
    # Original equations distinguish the named border reaction as well.
    assert a['exact_assembly_original_upper']>.01
    assert abs(a['exact_assembly_original_upper']-a['exact_assembly_frame_reaction_upper'])<1e-14
