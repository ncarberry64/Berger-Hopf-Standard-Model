import numpy as np
import pytest
from bhsm.interface.muon_common_normal_boundary_form import common_normal_boundary_form


def test_shared_attachment_equation_is_solved_before_elimination():
    p=np.array([[2.,0.,2.],[0.,3.,0.],[2.,0.,5.]])
    c=np.array([[3.,0.,-1.],[0.,4.,1.],[-1.,1.,6.]])
    a=common_normal_boundary_form(p,c,np.eye(3),np.diag([2.,3.,4.]),incoming_lapse=2.,child_lapse=.5)
    phi=np.array([-1/5,-1/7,1.])
    np.testing.assert_allclose(a['common_trace_lift'],phi,atol=0,rtol=0)
    np.testing.assert_allclose(a['attachment_stationarity_residual'],0.,atol=2e-16)
    C=np.vstack((np.eye(3),np.eye(3)));D=np.zeros((6,6));D[:3,:3]=p;D[3:,3:]=c
    np.testing.assert_allclose(a['common_form'],C.T@D@C,atol=0,rtol=0)
    separate=sum(M[2,2]-M[2,:2]@np.linalg.solve(M[:2,:2],M[:2,2])for M in (p,c))
    assert abs(a['combined_signed_action_pairing']-separate)>.1
    np.testing.assert_allclose(a['incoming_proper_inertia_on_common_trace'],2*phi@phi,rtol=1e-15)
    np.testing.assert_allclose(a['child_proper_inertia_on_common_trace'],.5*phi@np.diag([2.,3.,4.])@phi,rtol=1e-15)


def test_signed_indefinite_source_contacts_are_retained_without_symmetrizing():
    p=np.array([[2.,.1,.3],[.1,-3.,-.4],[.3,-.4,1.]])
    c=np.array([[1.,.2,.8],[.200000001,1.,.6],[.8,.6,-2.]])
    a=common_normal_boundary_form(p,c,np.eye(3),np.eye(3),incoming_lapse=1.,child_lapse=1.)
    np.testing.assert_array_equal(a['common_form'],p+c)
    assert np.max(abs(a['form_antisymmetric_rounding']))>0
    np.testing.assert_allclose(a['attachment_stationarity_residual'],0.,atol=3e-16)
    np.testing.assert_allclose(a['combined_signed_action_pairing'],a['direct_combined_pairing'],rtol=0,atol=4e-16)
    assert not a['local_R_or_physical_i_r_drive_c_selected']


def test_singular_shared_attachment_block_is_not_shifted():
    with pytest.raises(np.linalg.LinAlgError):
        common_normal_boundary_form(np.zeros((3,3)),np.eye(3)*np.array([0.,0.,1.]),np.eye(3),np.eye(3),incoming_lapse=1.,child_lapse=1.)


def test_complex_or_zero_clock_rejected():
    with pytest.raises(ValueError):
        common_normal_boundary_form(np.eye(3,dtype=complex),np.eye(3),np.eye(3),np.eye(3),incoming_lapse=1.,child_lapse=1.)
    with pytest.raises(ValueError):
        common_normal_boundary_form(np.eye(3),np.eye(3),np.eye(3),np.eye(3),incoming_lapse=0.,child_lapse=1.)
