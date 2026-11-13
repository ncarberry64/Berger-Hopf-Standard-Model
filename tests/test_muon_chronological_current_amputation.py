import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_chronological_current_amputation import (
    nonstationary_endpoint_amputation,exterior_current_pole_matrix)


def test_noncommuting_body_and_both_boundary_amputations_at_local_eigenvalue():
    H=np.array([[[.4,.3j],[-.2,.7]],[[.8,.1],[.2j,.3]],[[.6,-.2j],[.3,.4]]],complex)
    h=np.array([.07,.04+.02j,.03-.01j]);E=.4
    a=nonstationary_endpoint_amputation(h,H,energy=E)
    np.testing.assert_allclose(a['left_amputation_original_rows'],0,atol=4e-16)
    np.testing.assert_allclose(a['right_amputation_original_rows'],0,atol=4e-16)
    assert np.linalg.norm(a['nonstationary_left_amputation_contact'])>.01
    assert np.linalg.norm(a['nonstationary_left_amputation_contact']-a['nonstationary_right_amputation_contact'])>1e-4
    e=2e-5
    fd=(nonstationary_endpoint_amputation(h,H,energy=E+e)['continued_source_response']-
        nonstationary_endpoint_amputation(h,H,energy=E-e)['continued_source_response'])/(2*e)
    np.testing.assert_allclose(a['continued_source_energy_first'],fd,atol=2e-11,rtol=2e-9)


def test_finite_initial_inverse_has_no_pole_but_exterior_boundary_can_have_one():
    h=np.array([.12,.14]);H=np.tile(np.diag([.4,-.4]),(2,1,1))
    a=nonstationary_endpoint_amputation(h,H,energy=.4)
    I=np.eye(2);z=np.zeros((2,2))
    finite=exterior_current_pole_matrix(a['energy_shifted_core_trace'],a['energy_shifted_core_trace_first'],I,z)
    np.testing.assert_allclose(finite['exterior_pole_matrix'],I,atol=0)
    np.testing.assert_allclose(finite['exterior_pole_matrix_energy_first'],z,atol=0)
    # Independent boundary graph, used only as an equation control.
    B=-np.linalg.inv(a['energy_shifted_core_trace']);Bp=np.array([[.1,.2j],[.3,-.2]])
    ext=exterior_current_pole_matrix(a['energy_shifted_core_trace'],a['energy_shifted_core_trace_first'],I,B,boundary_final_first=Bp)
    np.testing.assert_allclose(ext['exterior_pole_matrix'],z,atol=2e-16)
    e=1e-6;UE=a['energy_shifted_core_trace'];L=sum(h)
    fd=((I+(B+e*Bp)@(np.exp(e*L)*UE))-(I+(B-e*Bp)@(np.exp(-e*L)*UE)))/(2*e)
    np.testing.assert_allclose(ext['exterior_pole_matrix_energy_first'],fd,atol=2e-10)
