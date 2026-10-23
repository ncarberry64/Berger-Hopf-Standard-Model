"""Independent energy/strong-residual identities; synthetic fields are CONTROL_ONLY."""
from math import factorial
import numpy as np
import pytest
import sympy as sp
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad

from bhsm.interface.muon_parent_hypercharge_energy_residual import (
    radial_basis_two_jet, frozen_coefficient_one_jet, strong_residual,
    normal_energy_identity_density, normal_energy_growth_rates,
    quintic_hermite_jet, load_retained_probe, reconstruct_nodal_acceleration,
    load_support_adjoint_pair, advanced_goal_residual_estimate,
    _temporal_samples,
)
from bhsm.interface.muon_parent_retarded_hypercharge import (
    WALL, ALPHA, frozen_e1_coefficients, regular_radial_basis,
)


def control_coefficients(x):
    # Smooth supplied coefficient control, not a selected physical action.
    return dict(electric=np.exp(x), radial=np.exp(2*x), potential=np.exp(-.5*x),
        shift=.4+.2*x, electric_derivative=np.exp(x),
        radial_derivative=2*np.exp(2*x), potential_derivative=-.5*np.exp(-.5*x),
        shift_derivative=np.zeros_like(x)+.2,
        electric_log_derivative=np.ones_like(x),
        radial_log_derivative=np.zeros_like(x)+2,
        potential_log_derivative=np.zeros_like(x)-.5)


def test_energy_identity_includes_both_nonzero_boundary_terms_and_all_signed_rates():
    # Independently differentiate E using the two first-order equations.
    def differentiated_energy(x):
        c = control_coefficients(x)
        e, r, V, beta = (c[k] for k in ('electric', 'radial', 'potential', 'shift'))
        a, b, bp, pi, pip, f = 1+x*x, 2*x, 2., .3+np.sin(x), np.cos(x), np.cos(2*x)
        at = pi/e+beta*b
        bt = (pip-pi)/e+.2*b+beta*bp
        pit = .2*pi+beta*pip+2*r*b+r*bp-V*a+f
        return pi*pit/e+r*b*bt+V*a*at
    def identity_interior(x):
        return normal_energy_identity_density(1+x*x, .3+np.sin(x), 2*x,
            np.cos(2*x), control_coefficients(x))[0]
    def flux(x):
        return normal_energy_identity_density(1+x*x, .3+np.sin(x), 2*x,
            np.cos(2*x), control_coefficients(x))[1]
    lhs = quad(differentiated_energy, .1, 1.2, epsabs=1e-11)[0]
    rhs = quad(identity_interior, .1, 1.2, epsabs=1e-11)[0]+flux(1.2)-flux(.1)
    assert lhs == pytest.approx(rhs, rel=2e-13)
    assert abs(flux(1.2)-flux(.1)) > 10
    rates = normal_energy_growth_rates(control_coefficients(np.array([.5])))
    np.testing.assert_allclose(rates, [[.7, -.8, .05]], atol=2e-16)


def test_strong_residual_is_euler_operator_with_shift_and_coefficient_derivatives():
    t, x = sp.symbols('t x', real=True)
    e, r, V, beta = 2+x, 3+x*x, 4+x, x/3
    a = t**3*(1+x*x)+t*x**3
    pi = e*(sp.diff(a, t)-beta*sp.diff(a, x))
    independent = sp.diff(pi, t)-sp.diff(beta*pi+r*sp.diff(a, x), x)+V*a
    xs = np.linspace(.1, 1.3, 7); ts = np.linspace(.2, .9, 7)
    ev = lambda f: sp.lambdify((t, x), f, 'numpy')(ts, xs)
    c = dict(electric=2+xs, radial=3+xs*xs, potential=4+xs, shift=xs/3,
        electric_derivative=np.ones_like(xs), radial_derivative=2*xs,
        shift_derivative=np.ones_like(xs)/3)
    actual = strong_residual(ev(a), ev(sp.diff(a, t)), ev(sp.diff(a, t, 2)),
        ev(sp.diff(a, x)), ev(sp.diff(a, t, x)), ev(sp.diff(a, x, 2)), c)
    np.testing.assert_allclose(actual, ev(independent), rtol=2e-15, atol=5e-15)


def test_exact_green_identity_has_outward_sign_and_requires_advanced_residual_term():
    # Polynomial CONTROL_ONLY fields satisfy zero primal initial/error trace
    # and zero advanced terminal data.  Neither solves a physical field.
    t, x = sp.symbols('t x', real=True)
    e, r, V, beta = 2+x, 3+x*x, 4+x, x*(1-x)/3
    w, z = t*t*x*x*(1-x), (1-t)**2*(1+x)
    def pi(a):
        return e*(sp.diff(a, t)-beta*sp.diff(a, x))
    def flux(a):
        return beta*pi(a)+r*sp.diff(a, x)
    def L(a):
        return sp.diff(pi(a), t)-sp.diff(flux(a), x)+V*a
    spacetime = sp.integrate(z*L(w)-w*L(z), (x, 0, 1), (t, 0, 1))
    boundary = -sp.integrate((z*flux(w)-w*flux(z)).subs(x, 1)
        -(z*flux(w)-w*flux(z)).subs(x, 0), (t, 0, 1))
    assert sp.simplify(spacetime-boundary) == 0
    assert spacetime != 0
    # The advanced approximation residual contributes; silently dropping
    # it would not produce the stated boundary contraction identity.
    assert sp.integrate(w*L(z), (x, 0, 1), (t, 0, 1)) != 0


def test_actual_advanced_consumer_estimate_retains_large_remainder_and_no_enclosure_claim():
    pair, info, provenance = load_support_adjoint_pair()
    times, _, state, velocity, acc = _temporal_samples(pair['retarded'], info, 3, info['source_duration'])
    from bhsm.interface.muon_parent_retarded_hypercharge import compact_trace_pulse
    pulse = compact_trace_pulse(times, info['source_duration'])
    for actual, exact in zip((state[:, -1], velocity[:, -1], acc[:, -1]), pulse):
        np.testing.assert_array_equal(actual, exact)
    result = advanced_goal_residual_estimate(pair, info,
        radial_quadrature=160, temporal_quadrature=2, growth_grid=1025)
    assert result['primal_strong_residual_L2_time_space'] > 1000
    assert result['advanced_strong_residual_L2_time_space'] > 1
    assert result['advanced_energy_remainder_estimate'] > 50
    assert abs(result['finite_weak_correction']) < 1e-5
    assert result['strong_weak_green_identity_defect'] < 1e-5
    assert not result['bound_premises_certified']
    assert not result['continuum_pairing_enclosed']
    assert not result['numerical_Galerkin_orthogonality_is_physical_cancellation']
    assert not result['physical_Pauli_contraction']
    assert len(provenance['solution_sha256']['advanced']) == 64


def test_exact_quintic_temporal_jet_does_not_replace_derivative_with_ode_rhs():
    # Recover a vector-valued quintic exactly from its endpoint jets.
    coefficients = np.array([[1., -2.], [.2, 1.], [-.3, .7], [.6, -.4], [.1, .2], [-.2, .3]])
    def jet(t, derivative):
        return sum(factorial(j)/factorial(j-derivative)
                   *coefficients[j]*t**(j-derivative) for j in range(derivative, 6))
    nodes = np.linspace(0, 1, 13)
    q, v, acc = quintic_hermite_jet(jet(0, 0), jet(0, 1), jet(0, 2),
        jet(.7, 0), jet(.7, 1), jet(.7, 2), .7, nodes)
    for actual, derivative in ((q, 0), (v, 1), (acc, 2)):
        np.testing.assert_allclose(actual, np.array([jet(.7*z, derivative) for z in nodes]), atol=1e-13)
    with pytest.raises(ValueError, match='positive finite'):
        quintic_hermite_jet([0], [0], [0], [1], [0], [0], 0, nodes)


def test_jacobi_second_jet_is_the_same_retained_basis_and_has_friedrichs_exponent():
    x = np.linspace(.1, WALL-.1, 31)
    B, D, D2 = radial_basis_two_jet(x, 12)
    oldB, oldD = regular_radial_basis(x, 12)
    np.testing.assert_allclose(B, oldB, rtol=3e-15, atol=5e-13)
    np.testing.assert_allclose(D, oldD, rtol=5e-14, atol=1e-11)
    h = 2e-6
    plus, minus = radial_basis_two_jet(x+h, 12)[1], radial_basis_two_jet(x-h, 12)[1]
    np.testing.assert_allclose(D2, (plus-minus)/(2*h), rtol=2e-7, atol=6e-4)
    assert ALPHA*(ALPHA+3) == pytest.approx(9)
    np.testing.assert_array_equal(radial_basis_two_jet([WALL], 2)[0][0, :-1], 0)


def test_actual_analytic_coefficient_derivatives_match_retained_values_and_independent_differences():
    x = np.linspace(.05, WALL-.05, 37)
    c = frozen_coefficient_one_jet(x)
    original = frozen_e1_coefficients(x)
    for key in ('electric', 'radial', 'shift'):
        np.testing.assert_allclose(c[key], original[key], rtol=3e-15, atol=1e-13)
    np.testing.assert_allclose(c['potential'], 9*original['angular'], rtol=3e-15)
    h = 1e-6
    cp, cm = frozen_e1_coefficients(x+h), frozen_e1_coefficients(x-h)
    for key in ('electric', 'radial', 'shift'):
        np.testing.assert_allclose(c[key+'_derivative'], (cp[key]-cm[key])/(2*h), rtol=3e-7, atol=2e-6)
    np.testing.assert_allclose(c['potential_derivative'], 9*(cp['angular']-cm['angular'])/(2*h), rtol=3e-7, atol=2e-6)
    assert not c['physical_background_stationarity']


def test_exact_wall_zero_and_finite_pole_rates_do_not_remove_interior_shift():
    c = frozen_coefficient_one_jet(np.array([1e-7, WALL]))
    assert c['shift'][-1] == 0
    assert abs(c['shift'][0]) > 0
    np.testing.assert_allclose(normal_energy_growth_rates(c)[0], c['pole_rates'], atol=1e-9, rtol=2e-12)
    reverse = frozen_coefficient_one_jet(np.array([1e-7, WALL]), shift_sign=-1)
    np.testing.assert_allclose(normal_energy_growth_rates(reverse), -normal_energy_growth_rates(c), atol=0)


def test_actual_strong_residual_is_not_the_nearly_zero_finite_matrix_residual():
    data, info, provenance = load_retained_probe()
    acc = reconstruct_nodal_acceleration(data, info['source_duration'])
    matrix_residual = acc@data['M'].T+data['velocity']@(data['N'].T-data['N']).T+data['state']@data['K'].T
    assert np.max(abs(matrix_residual[:, :-1])) < 4e-7
    i = np.argmin(abs(data['times']-.2))
    x, w = leggauss(128)
    rho, w = (x+1)*WALL/2, w*WALL/2
    B, D, D2 = radial_basis_two_jet(rho, info['radial_order'])
    c = frozen_coefficient_one_jet(rho)
    R = strong_residual(data['state'][i]@B.T, data['velocity'][i]@B.T,
        acc[i]@B.T, data['state'][i]@D.T, data['velocity'][i]@D.T,
        data['state'][i]@D2.T, c)
    assert np.sqrt(np.dot(w, R*R/c['electric'])) > 100
    assert len(provenance['solution_sha256']) == 64


@pytest.mark.parametrize('rho,order', [([0], 2), ([WALL+.1], 2), ([.3], True), ([.3], 0)])
def test_basis_domain_guards(rho, order):
    with pytest.raises(ValueError):
        radial_basis_two_jet(rho, order)
