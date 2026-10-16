import numpy as np
import pytest
import mpmath as mp
from scipy.special import roots_jacobi

from bhsm.interface.electromagnetic_carrier_cap_domain import coexact_indicial_data, coexact_radial_jacobi


@pytest.mark.parametrize('lam', [4., 9., 16.])
def test_indicial_equation_energy_and_weighted_jacobi_gram(lam):
    d = coexact_indicial_data(lam)
    a, bad = d['alpha'], d['negative_alpha']
    assert abs(a*(a+3)-lam) < 8e-15
    assert abs(bad*(bad+3)-lam) < 2e-14
    assert a > -1.5 and bad < -1.5
    assert d['inverse_square_potential'] > .75
    wall = 1.7
    y, w = roots_jacobi(32, 2., 4+2*a)
    x = (y+1)/2
    b, _ = coexact_radial_jacobi(wall*x, 5, curl_squared=lam, wall=wall)
    p = b[:, :-1]/(x**a*(1-x))[:, None]
    gram = p.T@((w/2**(7+2*a))[:, None]*p)
    np.testing.assert_allclose(gram, np.eye(5), atol=5e-14, rtol=0)
    bw, _ = coexact_radial_jacobi([wall], 5, curl_squared=lam, wall=wall)
    np.testing.assert_array_equal(bw, [[0, 0, 0, 0, 0, 1]])


def test_literal_mp64_derivatives_and_old_lambda9_owner_parity():
    mp.mp.dps = 64
    rho, wall = .37, 1.4
    for lam in [4, 16]:
        a = (-3+mp.sqrt(9+4*lam))/2
        _, db = coexact_radial_jacobi([rho], 4, curl_squared=lam, wall=wall)
        for j in range(4):
            ja, jb = mp.mpf(2), 4+2*a
            norm = mp.gamma(j+ja+1)*mp.gamma(j+jb+1)/(mp.factorial(j)*mp.gamma(j+ja+jb+1)*(2*j+ja+jb+1))
            def literal(r):
                x = r/mp.mpf(wall)
                return x**a*(1-x)*mp.jacobi(j, ja, jb, 2*x-1)/mp.sqrt(norm)
            np.testing.assert_allclose(db[0,j], float(mp.diff(literal, mp.mpf(rho))),
                                       rtol=3e-15, atol=5e-14)
    from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis, WALL
    r = np.linspace(.01, WALL, 21)
    old = regular_radial_basis(r, 4)
    new = coexact_radial_jacobi(r, 4, curl_squared=9, wall=WALL)
    for left, right in zip(old, new):
        np.testing.assert_allclose(left, right, atol=3e-13, rtol=2e-14)


@pytest.mark.parametrize('rho,lam,wall', [([],4,1),([0],4,1),([.2],0,1),([.2+1j],4,1),([.2],4,np.nan)])
def test_invalid_or_longitudinal_inputs_are_not_admitted(rho,lam,wall):
    with pytest.raises(ValueError):
        coexact_radial_jacobi(rho,2,curl_squared=lam,wall=wall)
