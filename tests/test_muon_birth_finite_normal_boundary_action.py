import numpy as np
import pytest

from bhsm.interface.muon_birth_finite_normal_boundary_action import eliminate_attachment_traces,load_completed_finite_normal_cell


def test_internal_attachment_stationarity_keeps_indefinite_action_and_normal():
    R=np.array([[2.,.1,.5],[.1,-3.,.7],[.5,.7,4.]])
    a=eliminate_attachment_traces(R)
    assert a['trace_lift'][2]==1
    np.testing.assert_allclose((R@a['trace_lift'])[:2],0,atol=2e-16)
    expected=4.-R[2,:2]@np.linalg.solve(R[:2,:2],R[:2,2])
    np.testing.assert_allclose(a['normal_response'],expected,rtol=0,atol=1e-15)
    assert a['attachment_traces_eliminated_not_discarded']


def test_singular_attachment_action_is_not_regularized():
    with pytest.raises(np.linalg.LinAlgError):eliminate_attachment_traces(np.ones((3,3)))


def test_outgoing_omitted_profile_diagnostic_cannot_supply_boundary_form():
    with pytest.raises(ValueError,match='fully converged'):
        load_completed_finite_normal_cell('artifacts/muon_finite_normal_phase_20261011/outgoing_run_1')
