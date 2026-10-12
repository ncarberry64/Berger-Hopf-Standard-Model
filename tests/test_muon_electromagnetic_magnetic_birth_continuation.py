"""Finite algebra checks; oscillator operands are CONTROL_ONLY."""
import numpy as np
import pytest

import bhsm.interface.muon_electromagnetic_magnetic_birth_continuation as owner


@pytest.fixture(scope='module')
def continued_oscillator():
    # This literal positive kinetic/negative potential action checks the
    # canonical matching and the nonzero-initial advanced Green identity.
    mass=np.eye(408)*4
    mixed=np.zeros((408,408))
    stiffness=np.zeros((408,408));stiffness[0,0]=-16
    stiffness[0,400]=stiffness[400,0]=2
    scalar_stiffness=np.zeros((408,408));scalar_stiffness[400,0]=3
    f=dict(M=mass,B=mixed,K=stiffness,
        At_value_map=np.zeros((1,408)),At_velocity_map=np.zeros((1,408)),
        Gauss_matrix=np.eye(1),Gauss_value_row=np.zeros((1,408)),
        Gauss_velocity_row=np.zeros((1,408)))
    zeros=np.zeros((8,409))
    form=dict(final_time=.2,duration=.05,
        gauge_weak_rows=lambda t:(zeros,zeros,zeros,zeros),
        intrinsic_raw_M=lambda t:np.zeros((408,408)),
        intrinsic_raw_B=lambda t:np.zeros((408,408)),
        intrinsic_raw_K=lambda t:scalar_stiffness,
        source_map=lambda t:np.zeros((400,8)),
        source_rate_map=lambda t:np.zeros((400,8)))
    initial=np.zeros((800,8));initial[0,0]=.7;initial[400,0]=.8
    original=owner._reduced_at
    owner._reduced_at=lambda form,t:f
    try:
        result=owner.magnetic_birth_continuation_application(form,initial,time_steps=16,rtol=1e-12,atol=1e-14)
    finally:
        owner._reduced_at=original
    return result,initial,f


def test_continuation_matches_canonical_trace_not_previous_velocity(continued_oscillator):
    result,initial,f=continued_oscillator
    np.testing.assert_array_equal(result['state'][0],initial)
    # p=4*xdot: copying the incoming velocity would be wrong when mass changes.
    assert result['velocity'][0,0,0]==pytest.approx(.2)
    np.testing.assert_allclose(f['M'][:400,:400]@result['velocity'][0],initial[400:],atol=2e-16)
    t=result['times'];omega=2
    expected=.7*np.cos(omega*t)+.1*np.sin(omega*t)+.125*(1-np.cos(omega*t))
    np.testing.assert_allclose(result['state'][:,0,0],expected,rtol=2e-12,atol=2e-13)


def test_nonzero_initial_state_is_retained_in_advanced_pairing(continued_oscillator):
    result,initial,_=continued_oscillator
    initial_term=result['advanced_adjoint'][0].T@initial
    assert abs(initial_term[0,0])>1
    # Simpson's finite quadrature error is recorded, not called an enclosure.
    assert result['adjoint_pairing_maximum_defect']<2e-10
    np.testing.assert_allclose(result['adjoint_output'],result['adjoint_source_pairing'],atol=2e-10)
    assert not result['physical_Pauli_value']


def test_missing_or_nonfinite_incoming_canonical_state_rejected():
    form=dict(final_time=.1,duration=.025)
    with pytest.raises(ValueError,match='incoming canonical'):
        owner.magnetic_birth_continuation_application(form,np.zeros((400,8)))
    state=np.zeros((800,8));state[0,0]=np.nan
    with pytest.raises(ValueError,match='incoming canonical'):
        owner.magnetic_birth_continuation_application(form,state)
