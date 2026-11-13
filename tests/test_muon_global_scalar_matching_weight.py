import numpy as np
from scipy.integrate import quad
from bhsm.interface.muon_global_scalar_matching_weight import (
    global_scalar_matching_weight, high_frequency_clock_amplification,
    same_clock_scalar_reference_impulse)


def test_complex_clock_impulse_matching_equals_independent_closed_transfer_integral():
    g, w = np.polynomial.legendre.leggauss(80)
    clock = .9+.2j
    T = 3*clock
    tau = T*(g+1)/2
    mu = T*w/2
    p = tau[:, None, None]*np.eye(4)[None]
    m, Y, Z = .2, .3, 1.4
    a = global_scalar_matching_weight(p, mu, tau, np.ones(len(g), bool),
        matched_mass_action=m, fixed_Y=Y, kinetic_residue=Z,
        log_edges=np.linspace(0, 4, 5), quadrature_order=12)

    def independent(y):
        x = 1-np.exp(-y)
        s = m*x*np.exp(y/2)
        # Integral of tau*exp(-s*tau) on the same complex segment.
        G = (1-np.exp(-s*T)*(1+s*T))/s**2 if s else T*T/2
        return Y*Y*m*m*Z/(16*np.pi**2)*x*x*(2-x)*G

    expected = quad(lambda y: independent(y).real, 0, 4, epsabs=1e-13)[0]
    expected += 1j*quad(lambda y: independent(y).imag, 0, 4, epsabs=1e-13)[0]
    np.testing.assert_allclose(a['finite_global_scalar_covector'], expected, rtol=3e-13, atol=1e-17)
    assert abs(a['finite_global_scalar_covector'].imag) > 1e-6
    assert np.max(abs(a['finite_before_source_pairing'])) == 0
    d = high_frequency_clock_amplification(np.array([-.02+.1j, .03+.2j]),
        matched_mass_action=m, log_coordinates=(4., 8.))
    np.testing.assert_allclose(d['future_exponential_log_modulus_max'], .02*d['proper_Laplace_rates'])
    assert not d['pointwise_amplification_identified_with_integrated_tail']


def test_signed_action_reference_retains_canonical_endpoint_instead_of_meromorphic_subtraction():
    g, gw = np.polynomial.legendre.leggauss(70)
    T = .4+.2j
    tau = T*(g+1)/2
    mu = T*gw/2
    Z, a = 1.3, 2.1
    C = np.array([-Z*a*np.eye(4), np.zeros((4, 4)), Z*np.eye(4)])
    rates = np.array([.1, 1., 4.+.2j])
    r = same_clock_scalar_reference_impulse(C, tau, T, rates)
    driven = np.einsum('sq,q,qab->sab', np.exp(-rates[:, None]*tau), mu,
                       r['reference_driven_point_pairing'])
    D = Z*(a-rates*rates)
    residual = D[:, None, None]*driven-np.eye(4)[None]-r['reference_Laplace_differential_endpoint_contact']
    np.testing.assert_allclose(residual, 0., atol=7e-16)
    assert np.linalg.norm(r['reference_final_weak_conormal_contact']) > 1
    # The finite impulse obeys the signed original equation and is not 1/C(-is).
    assert np.linalg.norm(driven+np.eye(4)[None]/(Z*(a+rates*rates))[:, None, None]) > .1
