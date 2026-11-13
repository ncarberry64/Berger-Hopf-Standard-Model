import numpy as np

from bhsm.interface.muon_birth_chronological_boundary_action import discrete_boundary_two_jet
from bhsm.interface.muon_birth_inhomogeneous_canonical_mean import inhomogeneous_canonical_step


def test_source_application_matches_independent_full_endpoint_action_rows():
    H=np.array([[-2.,.12,.3],[.12,1.,-.2],[.3,-.2,1.7]])
    g=np.array([[.7,-.2],[.4,.9],[-.1,.6]]);initial=np.array([[.2,.3],[-.4,.1]]);h=.17
    b=discrete_boundary_two_jet(H,np.zeros(3),h,1)
    # Independent endpoint action: z=(x0,x1,y), eta=Q z.
    Q=np.array([[.5,.5,0.],[-1/h,1/h,0.],[0.,0.,1.]])
    K=b['hessian'];force=h*Q.T@g
    unknown=np.linalg.solve(K[np.ix_([0,2],[1,2])],
        np.r_[-initial[1:2]-K[:1,:1]@initial[:1]-force[:1],
              -K[2:,:1]@initial[:1]-force[2:]])
    z=np.r_[initial[:1],unknown[:1],unknown[1:]]
    expected=np.r_[z[1:2],(K@z+force)[1:2]]
    a=inhomogeneous_canonical_step(H,h,g,initial)
    np.testing.assert_allclose(a['final_canonical_state'],expected,rtol=3e-15,atol=3e-15)
    cert=a['stored_action_arithmetic_certificate']
    assert cert['literal_equation_residual_upper']<1e-40
    assert cert['all_algebraic_equations_residual_upper']<1e-40
    assert a['momentum_source_count']==1


def test_pure_momentum_source_does_not_become_a_spurious_second_impulse():
    H=np.diag([-2.,1.,1.7]);g=np.array([[0.],[3.],[0.]])
    a=inhomogeneous_canonical_step(H,.1,g,np.zeros((2,1)))
    # L+epsilon*3v is an exact endpoint term. At fixed total p0,
    # v starts shifted by -3 and the source appears once in total p1.
    generator=np.array([[0.,1.],[-2.,0.]])
    M=np.linalg.solve(np.eye(2)-.05*generator,np.eye(2)+.05*generator)
    expected=M@np.array([[0.],[-3.]])+np.array([[0.],[3.]])
    np.testing.assert_allclose(a['final_canonical_state'],expected,rtol=3e-15,atol=3e-15)
    assert np.max(abs(a['canonical_evolution_defect']))<1e-14


def test_named_frame_reaction_retains_incompatible_source_original_row():
    H=np.diag([-.4,1.,2.]);g=np.array([[.3],[.8],[.6]])
    a=inhomogeneous_canonical_step(H,.2,g,np.zeros((2,1)),np.array([[1.]]))
    assert a['frame_reactions'][0,0]!=0
    assert abs(a['midpoint_velocity_algebraic_lift'][1,0])<1e-40
    assert np.max(abs(a['initial_canonical_reaction_defect']))<1e-15
    assert a['spectral_directions_removed']==0
    assert not a['physical_E0_or_birth_graph_selected']


def test_pair_axes_are_preserved_without_halving_and_covariance_padding_is_exact():
    H=np.diag([-2.,1.,1.7]);g=np.zeros((3,8,8));g[0,:3,:3]=np.eye(3)
    a=inhomogeneous_canonical_step(H,.1,g,np.zeros((2,8,8)))
    assert a['final_canonical_state'].shape==(2,8,8)
    assert np.count_nonzero(a['final_canonical_state'][:,3:])==0
    assert np.count_nonzero(a['final_canonical_state'][:,:,3:])==0
    assert a['final_canonical_state'][1,0,0]>0
