import numpy as np
import pytest

from bhsm.interface.muon_d5_refined_domain_application import polynomial_time_pairing
from bhsm.interface.muon_d5_complement_bulk_response import nodal_derivative
from bhsm.interface.muon_d5_complement_event_return import consume_event_trace_operand


@pytest.mark.parametrize('n', [6, 10, 14])
def test_refined_temporal_mass_has_original_endpoint_green_identity(n):
    z = -np.cos(np.linspace(0, np.pi, n))
    t = (z+1)*5e-6-1e-5
    d = nodal_derivative(t)
    mass, rows = polynomial_time_pairing(t, d)
    assert np.max(abs(rows)) < 2e-12
    assert np.min(np.linalg.eigvalsh(mass)) > 0
    # An independent monomial-moment integral checks the dense mass, including
    # its off-diagonal entries. This tests the fixed time chart, not products
    # with a variable physical D5 coefficient or a continuum error enclosure.
    v = np.polynomial.polynomial.polyvander(z, n-1)
    inverse = np.linalg.inv(v)
    ij = np.add.outer(np.arange(n), np.arange(n))
    moment = np.where(ij % 2 == 0, 2/(ij+1), 0.)*5e-6
    exact = inverse.T @ moment @ inverse
    np.testing.assert_allclose(mass, exact, atol=2e-15, rtol=2e-7)


def test_event_jacobi_retains_reset_derivative_and_parent_derivative():
    rng = np.random.default_rng(465)
    v = rng.normal(size=(2, 3, 2))+1j*rng.normal(size=(2, 3, 2))
    vx = rng.normal(size=v.shape)+1j*rng.normal(size=v.shape)
    u = rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3))
    ux = rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3))
    child_source = rng.normal(size=v.shape)+1j*rng.normal(size=v.shape)
    event = consume_event_trace_operand(v, vx, coordinate_times=np.array([0.]),
        event_time_index=0, fibre_width=3, branch_identity='same_original_parent_test')
    # delta Gamma_child - (delta U_R) Gamma_parent - U_R delta Gamma_parent.
    actual = child_source + ux @ event['event_Jacobi_coefficient_of_reset_lift_first']
    actual += u @ event['event_Jacobi_coefficient_of_reset_lift']
    eps = 1e-5
    plus = eps*child_source-(u+eps*ux)@(v+eps*vx)
    minus = -eps*child_source-(u-eps*ux)@(v-eps*vx)
    np.testing.assert_allclose(actual, (plus-minus)/(2*eps), atol=3e-10, rtol=3e-10)
    assert event['reset_lift_assigned'] is False
    assert event['child_trace_assigned'] is False
    assert event['held_event_residual'] is None
