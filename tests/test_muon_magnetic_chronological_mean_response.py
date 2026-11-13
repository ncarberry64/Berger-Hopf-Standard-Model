import numpy as np

from bhsm.interface.muon_birth_inhomogeneous_canonical_mean import inhomogeneous_canonical_step
from bhsm.interface.muon_magnetic_chronological_mean_response import mean_birth_canonical_state,past_directed_canonical_mean


def test_reverse_action_with_physical_momentum_sign_recovers_the_initial_state():
    H=np.array([[-2.,.12,.3],[.12,1.,-.2],[.3,-.2,1.7]])
    g=np.array([[.7,-.2],[.4,.9],[-.1,.6]]);s=np.array([[.2,.3],[-.4,.1]])
    forward=inhomogeneous_canonical_step(H,.17,g,s)
    backward=past_directed_canonical_mean(H,.17,g,forward['final_canonical_state'])
    np.testing.assert_allclose(backward['far_canonical_state'],s,atol=4e-15,rtol=4e-15)
    np.testing.assert_allclose(backward['future_midpoint_velocity_algebraic_lift'],
        forward['midpoint_velocity_algebraic_lift'],atol=4e-15,rtol=4e-15)


def test_birth_total_canonical_dual_contains_the_source_once_and_no_new_density():
    H=np.diag([-2.,1.,1.7]);P=np.eye(3);delta=np.zeros((3,1,1));g=np.array([.7,3.,.2])[:,None,None]
    a=mean_birth_canonical_state(delta,H,g,P,1)
    assert a['canonical_state'][1,0,0]==3.
    assert a['algebraic_constitutive_defect'][0,0,0]==.2
    assert a['momentum_source_count']==1
