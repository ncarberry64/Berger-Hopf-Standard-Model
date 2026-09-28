import pytest
from flint import arb_mat
from bhsm.interface.formation_stationarity_kkt import assemble_stationarity,stationary_first_jet,reset_tangent_blocks


def circle(**changes):
    # Gamma=y1+p*y2; R=(y1^2+y2^2-1)/2 at p=0,y=(1,0),mu=-1.
    data=dict(constraints=arb_mat([[0]]),constraint_y=arb_mat([[1,0]]),
        constraint_p=arb_mat([[0]]),multipliers=arb_mat([[-1]]),
        action_y=arb_mat([[1],[0]]),action_yy=arb_mat(2,2),action_yp=arb_mat([[0],[1]]),
        constraint_yy=[arb_mat([[1,0],[0,1]])],constraint_yp=[arb_mat(2,1)])
    data.update(changes);return assemble_stationarity(**data)


def test_curved_constraint_gives_correct_physical_first_jet():
    data=circle();answer=stationary_first_jet(data)
    # Exact branch y=(1,p)/sqrt(1+p^2), mu=-sqrt(1+p^2).
    assert data['residual']==arb_mat(3,1)
    assert answer['response']==arb_mat([[0],[1],[0]])
    assert answer['replay']==arb_mat(3,1)
    assert data['constrained_hessian']==arb_mat([[-1,0],[0,-1]])


def test_constraint_normal_force_does_not_change_stationary_physics():
    # Gamma -> Gamma+7R, mu -> mu-7 leaves the same constrained action.
    original=circle()
    changed=circle(action_y=arb_mat([[8],[0]]),action_yy=arb_mat([[7,0],[0,7]]),multipliers=arb_mat([[-8]]))
    for key in ('residual','jacobian','forcing'):assert changed[key]==original[key]


def test_moving_parameter_constraint_normal_is_retained():
    # R=(y1^2+y2^2-1)/2+p*y2; stationarity gives dy2=0 at p=0.
    data=circle(constraint_yp=[arb_mat([[0],[1]])])
    assert stationary_first_jet(data)['response']==arb_mat(3,1)


def test_absent_history_gradient_cannot_be_replaced_by_zero():
    with pytest.raises(ValueError,match='joint-action'):circle(action_y=None)
    with pytest.raises(ValueError,match='curvature'):circle(constraint_yy=[])


def test_legitimate_null_requires_explicit_slice_and_its_forcing():
    data=dict(jacobian=arb_mat([[1,0],[0,0]]),forcing=arb_mat([[-2],[0]]))
    with pytest.raises((ValueError,ZeroDivisionError)):stationary_first_jet(data)
    with pytest.raises(ValueError,match='action-owned'):
        stationary_first_jet(data,owned_border={})
    result=stationary_first_jet(data,owned_border=dict(
        columns=arb_mat([[0],[1]]),rows=arb_mat([[0,1]]),forcing=arb_mat([[-3]]),
        owner='Synthetic test: prescribed physical parameter coordinate y2=3p'))
    assert result['response']==arb_mat([[2],[3],[0]])
    assert result['replay']==arb_mat(3,1)


def test_reduced_curved_stationarity_matches_full_border():
    system=circle();Q=arb_mat([[0],[1]])
    reduced=reset_tangent_blocks(system,Q)
    assert reduced['hessian']==arb_mat([[-1]])
    assert reduced['physical_covector']==arb_mat(1,1)
    y=-reduced['hessian'].solve(reduced['launch_forcing'])
    assert Q*y+reduced['constraint_normal_launch']==arb_mat([[0],[1]])
    assert reduced['reset_tangent_replay']==arb_mat(1,1)


def test_moving_reset_normal_enters_reduced_launch_forcing():
    # Synthetic Gamma=(y1^2+2*y1*y2+3*y2^2)/2, R=y1-p.
    # Stationary branch y1=p,y2=-p/3; Q^T Gamma_yp alone would give zero.
    system=assemble_stationarity(constraints=arb_mat([[0]]),
        constraint_y=arb_mat([[1,0]]),constraint_p=arb_mat([[-1]]),
        multipliers=arb_mat([[0]]),action_y=arb_mat(2,1),
        action_yy=arb_mat([[1,1],[1,3]]),action_yp=arb_mat(2,1),
        constraint_yy=[arb_mat(2,2)],constraint_yp=[arb_mat(2,1)])
    Q=arb_mat([[0],[1]]);reduced=reset_tangent_blocks(system,Q)
    assert reduced['launch_forcing']==arb_mat([[1]])
    assert reduced['reset_normal_replay']==arb_mat(1,1)
    y=-reduced['hessian'].solve(reduced['launch_forcing'])
    reconstructed=Q*y+reduced['constraint_normal_launch']
    full=stationary_first_jet(system)['response']
    assert all((reconstructed[i,0]-full[i,0]).contains(0) for i in range(2))
