import numpy as np

from bhsm.interface.muon_magnetic_birth_ward_mean import named_ward_mean_application


def test_named_row_identities_retain_all_original_equations_without_spectral_selection():
    independent=np.array([[1.,2.,0.,1.],[0.,1.,3.,-1.]])
    J=np.r_[independent,independent[0:1]+2*independent[1:2],3*independent[0:1]-independent[1:2]]
    source=np.array([[.3,-.4],[.7,.2],[1.7,0.],[.2,-1.4]])
    L=np.array([[-1.,-2.,1.,0.],[-3.,1.,0.,1.]])
    a=named_ward_mean_application(J,source,np.array([2.,.5,.3,1.]),np.array([.7,1.2,2.,.4]),L)
    np.testing.assert_allclose(a['original_residual'],0.,atol=3e-15)
    np.testing.assert_allclose(a['named_source_compatibility'],0.,atol=3e-15)
    assert a['literal_original_row_count']==4 and a['independent_named_quotient_row_count']==2
    assert a['numerical_spectral_directions_removed']==0
    assert a['stored_action_arithmetic_certificate']['quotient_equation_residual_upper']<1e-40


def test_incompatible_source_is_exposed_in_original_rows_not_erased():
    J=np.array([[1.,0.,0.],[0.,1.,0.],[1.,1.,0.],[2.,-1.,0.]])
    L=np.array([[-1.,-1.,1.,0.],[-2.,1.,0.,1.]])
    source=np.array([[0.],[0.],[.2],[0.]])
    a=named_ward_mean_application(J,source,np.ones(4),np.ones(3),L)
    assert np.max(abs(a['named_source_compatibility']))==.2
    assert np.linalg.norm(a['original_residual'])>.01
    assert a['stored_action_arithmetic_certificate']['original_all_row_residual_upper']>.01
