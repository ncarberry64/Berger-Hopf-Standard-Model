"""Fixed-Y scalar matching functional on an executed global impulse kernel.

This finite log interval retains the original complex clock and the full
coupled source image. It is an action-consumer restriction, not a quantum
covariance, omitted-tail bound, or continuum overlap subtraction.
"""
from __future__ import annotations
import numpy as np


def global_scalar_matching_weight(radial_pairing, measure, relative_clock, future_mask,
        *, matched_mass_action, fixed_Y, kinetic_residue, log_edges=(0., 8., 16., 24., 32.),
        quadrature_order=8):
    """Evaluate the existing scalar numerator on minus the driven response.

    x=1-exp(-y), s=m*x*exp(y/2) and
    F=-Y^2*m^2*Z/(16*pi^2) int x^2*(2-x)*Tr(G_inv(s))/4 dy.
    The independently traced angular spectators have already been summed
    in radial_pairing. No cross-spectator multi-RHS products enter here.
    """
    p = np.asarray(radial_pairing, complex)
    mu, tau = (np.asarray(a, complex) for a in (measure, relative_clock))
    future = np.asarray(future_mask, bool)
    edges = np.asarray(log_edges, float)
    m, Y, Z = map(float, (matched_mass_action, fixed_Y, kinetic_residue))
    if (p.ndim != 3 or p.shape[1:] != (4, 4) or mu.shape != (len(p),)
            or tau.shape != mu.shape or future.shape != mu.shape
            or not all(np.isfinite(a).all() for a in (p, mu, tau, edges))
            or min(m, Y, Z) <= 0 or not np.isfinite([m, Y, Z]).all()
            or edges.ndim != 1 or len(edges) < 2 or edges[0] != 0
            or np.any(np.diff(edges) <= 0) or type(quadrature_order) is not int
            or quadrature_order < 4 or not np.any(future)):
        raise ValueError('complete four-source pairing, original clock and declared finite matching interval required')
    g, gw = np.polynomial.legendre.leggauss(quadrature_order)
    y = np.concatenate([a+(b-a)*(g+1)/2 for a, b in zip(edges[:-1], edges[1:])])
    weights = np.concatenate([gw*(b-a)/2 for a, b in zip(edges[:-1], edges[1:])])
    x = -np.expm1(-y)
    rates = m*x*np.exp(y/2)
    exponent = -rates[:, None]*tau[None]
    if np.max(exponent.real) > np.log(np.finfo(float).max)-4:
        raise FloatingPointError('actual continued-clock exponential exceeds finite range; no old static tail substitution')
    exp = np.exp(exponent)
    driven = np.einsum('sq,q,qab->sab', exp[:, future], mu[future], p[future])
    before = np.einsum('sq,q,qab->sab', exp[:, ~future], mu[~future], p[~future])
    inverse = -driven
    numerator = -Y*Y*m*m*Z/(16*np.pi**2)*x*x*(2-x)
    samples = numerator*np.trace(inverse, axis1=1, axis2=2)/4
    return dict(log_nodes=y, quadrature_weights=weights, quadrature_x=x,
        proper_Laplace_rates=rates, finite_radial_inverse_action_Green=inverse,
        finite_before_source_pairing=before, scalar_matching_weight=numerator,
        finite_global_scalar_covector_samples=samples,
        finite_global_scalar_covector=np.array(weights@samples),
        original_clock_exponential_modulus_max=float(np.exp(np.max(exponent.real))),
        future_clock_exponential_modulus_max=float(np.exp(np.max(exponent[:, future].real))),
        original_clock_exponential_argument_max=float(np.max(abs(exponent.imag))),
        integrated_absolute_sample_value=float(weights@abs(samples)),
        log_interval_end=float(edges[-1]), quadrature_order=quadrature_order,
        complex_clock_replaced_by_absolute_measure=False,
        omitted_high_s_tail_or_quantum_Pauli_enclosed=False)


def high_frequency_clock_amplification(relative_clock, *, matched_mass_action,
                                       log_coordinates=(32., 48., 64.)):
    """Expose retained exponential growth scales, without claiming integral growth.

    The maximal log modulus is an actual clock coefficient diagnostic.
    Oscillatory cancellations and spectral/corner returns are not replaced
    by this pointwise maximum. It is not an omitted-tail error bound.
    """
    t = np.asarray(relative_clock, complex)
    y = np.asarray(log_coordinates, float)
    m = float(matched_mass_action)
    if (t.ndim != 1 or not len(t) or y.ndim != 1 or m <= 0
            or not np.isfinite(t).all() or not np.isfinite(y).all() or not np.isfinite(m)):
        raise ValueError('actual future clock and the same action mass required')
    s = m*(-np.expm1(-y))*np.exp(y/2)
    return dict(log_coordinates=y, proper_Laplace_rates=s,
        future_exponential_log_modulus_max=-s*np.min(t.real),
        future_exponential_argument_max=s*np.max(abs(t.imag)),
        pointwise_amplification_identified_with_integrated_tail=False,
        prior_static_Schur_tail_transferred_to_global_clock=False)


def same_clock_scalar_reference_impulse(reference_coefficients, relative_clock,
                                        final_clock, laplace_rates):
    """Transport the owned local scalar comparator to the SAME proper action.

    The original comparator is C_L(z)=-Z*a+Z*z^2. The literal action
    continuation L_E=-L_L with v_L=i*v_E yields M_E=Z, K_E=Z*a;
    its positive action impulse solves -Z*h''+Z*a*h=delta. Thus
    h(0)=0, h'(0+)=-1/Z, h=-sinh(sqrt(a)*tau)/(Z*sqrt(a)).
    This uses the same initial-Cauchy/free-final canonical graph and
    original complex tau, rather than subtracting the meromorphic local
    1/C_L(-is) or changing the clock to its absolute value.

    The original weak row is tested with 2r whereas deltaH=r*h and r²=1/2;
    its projected impulse and conormal are twice the effective h action.
    The current pairing itself is h and carries no extra factor2.
    """
    C = np.asarray(reference_coefficients, complex)
    t = np.asarray(relative_clock, complex)
    T = complex(final_clock)
    rates = np.asarray(laplace_rates, complex)
    if (C.shape != (3, 4, 4) or t.ndim != 1 or rates.ndim != 1
            or not all(np.isfinite(v).all() for v in (C, t, rates)) or not np.isfinite(T)):
        raise ValueError('owned scalar comparator, actual global clock and finite rates required')
    Z = C[2, 0, 0]
    a = -C[0, 0, 0]/Z
    if (Z.imag != 0 or Z.real <= 0 or a.imag != 0 or a.real <= 0
            or not np.array_equal(C[2], Z*np.eye(4))
            or not np.array_equal(C[0], C[0, 0, 0]*np.eye(4)) or np.any(C[1])):
        raise ValueError('the exact stored isotropic same-coordinate scalar reference must be retained')
    omega = np.sqrt(a)
    phi = -np.sinh(omega*t)/(Z*omega)
    final_value = -np.sinh(omega*T)/(Z*omega)
    final_velocity = -np.cosh(omega*T)/Z
    eye = np.eye(4, dtype=complex)
    final_conormal = (2*Z*final_velocity*np.exp(-rates*T))[:, None, None]*eye
    differential_boundary = (Z*np.exp(-rates*T)*(final_velocity+rates*final_value))[:, None, None]*eye
    return dict(reference_driven_point_pairing=phi[:, None, None]*eye,
        reference_final_dynamic_value=np.array(final_value),
        reference_final_dynamic_velocity=np.array(final_velocity),
        reference_weak_impulse_source=np.broadcast_to(2*eye, (len(rates), 4, 4)).copy(),
        reference_final_weak_conormal_contact=final_conormal,
        reference_Laplace_differential_endpoint_contact=differential_boundary,
        proper_reference_inverse_action_coefficients=np.array([Z*a, 0j, -Z]),
        reference_initial_coordinate_and_canonical_trace_zero=True,
        reference_field_source_measure_identical_to_global_graph=True,
        continuum_meromorphic_overlap_substituted=False)
