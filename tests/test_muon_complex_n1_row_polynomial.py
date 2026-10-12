"""The changing shift raises the literal Maxwell row polynomial to degree5."""
import numpy as np

from test_muon_complex_n1_literal_action import _fixture, _literal_pair
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization


def test_shift_field_density_linear_germ_requires_degree_five_coefficient_extraction():
    row, lifts, (u, ud, v, vd) = _fixture()
    rng = np.random.default_rng(501)
    dA = .3*(rng.normal(size=row['A'].shape) + .2j*rng.normal(size=row['A'].shape))
    dc = np.zeros_like(row['densities']); dc[:, 0] = .4 + .07j; dc[:, 4] = .6 - .03j
    angular = scalar_s3_discretization(1)
    ids = np.flatnonzero([label[0] == 1 for label in angular['real_basis_labels']])
    Y = angular['real_basis_values'][:, ids]
    EY = angular['real_basis_derivative_values'][:, :, ids]
    def value(z):
        moved = row | dict(A=row['A']+z*dA, densities=row['densities']+z*dc)
        return _literal_pair(moved, lifts, Y, EY, angular['haar_weights'], u, ud, v, vd)
    # The polynomial is degree <=5. Eight roots independently extract all
    # coefficients without a small derivative step or a background dagger.
    roots = np.exp(2j*np.pi*np.arange(8)/8)
    samples = np.array([value(z) for z in roots])
    coefficients = np.array([np.sum(samples/roots**k)/8 for k in range(8)])
    assert abs(coefficients[5]) > 1e-7
    np.testing.assert_allclose(coefficients[6:], 0, rtol=0, atol=3e-14)
    h = .7
    p = [value(t*h)-value(-t*h) for t in (1, 2, 3)]
    cubic_only = (8*p[0]-p[1])/(12*h)
    degree_five = (45*p[0]-9*p[1]+p[2])/(60*h)
    np.testing.assert_allclose(degree_five, coefficients[1], rtol=3e-12, atol=3e-14)
    np.testing.assert_allclose(cubic_only-coefficients[1], -4*h**4*coefficients[5], rtol=3e-10, atol=3e-14)
