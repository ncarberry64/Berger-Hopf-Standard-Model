"""Finite transverse W-loop Higgs/photon Pauli projection with fixed Y_mu.

The retained minimal local Higgs kinetic matching gives g_hWW=2 MW^2/v.
The radial lepton vertex is the action-owned Y_mu/sqrt(2), rather than a
Yukawa inferred from a measured pole.  This implements Ilisie (2015),
Eqs. (21),(28), with the transverse-vertex and leading external-mass scope
of sections 4.1-4.2.  It does not complete the finite bosonic EW correction.
"""
from __future__ import annotations

import math

from scipy.integrate import quad

from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator

PRIMARY = 'https://arxiv.org/abs/1502.04199'


def _positive(**values):
    for name, value in values.items():
        if isinstance(value, bool):
            raise ValueError(f'{name} must be a positive finite scalar')
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f'{name} must be a positive finite scalar') from exc
        if not math.isfinite(number) or number <= 0:
            raise ValueError(f'{name} must be a positive finite scalar')


def _log_quotient(z, t):
    """log(z/t)/(z-t) and its log(z) derivative, including z=t."""
    u = (z-t)/t
    if abs(u) < 1e-4:
        # These are analytic removable-singularity continuations, not a
        # threshold prescription.  Six terms suffice at this switch.
        ell = math.fsum((-u)**k/(k+1) for k in range(7))/t
        dot = math.fsum((-1)**(k+1)*u**k/((k+1)*(k+2))
                        for k in range(7))/t
    else:
        log = math.log(z)-math.log(t)
        ell = log/(z-t)
        dot = (1-z*ell)/(z-t)
    return ell, dot


def transverse_w_higgs_kernel(z, *, epsabs=2e-11, epsrel=2e-12):
    """Return F3(z) and dF3/dlog(z) for positive mass-ratio squared.

    Symmetrizing x and 1-x gives the equivalent coefficient 19/2-15t,
    t=x(1-x).  QUADPACK errors are numerical estimates, not enclosures.
    """
    _positive(z=z, epsabs=epsabs, epsrel=epsrel)
    z = float(z)

    def integrand(x, derivative=False):
        t = x*(1-x)
        ell, dot = _log_quotient(z, t)
        a = 9.5-15*t
        numerator = a*z-t
        return .5*(a*z*ell+numerator*dot if derivative else numerator*ell)

    points = None
    if z < .25:
        root = math.sqrt(1-4*z)
        points = [(1-root)/2, (1+root)/2]
    elif z == .25:
        points = [.5]
    value, error = quad(integrand, 0., 1., points=points,
                        epsabs=epsabs, epsrel=epsrel, limit=300)
    dot, dot_error = quad(lambda x: integrand(x, True), 0., 1.,
                          points=points, epsabs=epsabs, epsrel=epsrel,
                          limit=300)
    if not all(math.isfinite(x) for x in (value, error, dot, dot_error)):
        raise ValueError('transverse W/Higgs kernel application was nonfinite')
    return dict(value=value, log_z_derivative=dot,
                quadrature_error_estimate=error,
                derivative_quadrature_error_estimate=dot_error,
                numerical_method='symmetrized F3; analytic removable singularity; adaptive quadrature',
                numerical_error_is_enclosure=False)


def bosonic_higgs_photon_w_projection(*, alpha_0,
        fermi_constant_GeV_inverse_squared, muon_mass_GeV,
        w_mass_GeV, higgs_mass_GeV, epsabs=2e-11, epsrel=2e-12):
    """Evaluate only the finite transverse H-gamma/W-loop projection.

    At fixed action Yukawa the external pole-mass partial is a/m_mu,
    not 2a/m_mu.  The pole is an external calibrated on-shell argument;
    no intrinsic pole matching or actual E1 Higgs profile is inferred.
    """
    _positive(alpha=alpha_0, GF=fermi_constant_GeV_inverse_squared,
              m=muon_mass_GeV, MW=w_mass_GeV, MH=higgs_mass_GeV)
    alpha, gf, m, w, h = map(float, (alpha_0,
        fermi_constant_GeV_inverse_squared, muon_mass_GeV,
        w_mass_GeV, higgs_mass_GeV))
    if m >= min(w, h):
        raise ValueError('the declared external-mass expansion requires m_mu < MW,MH')
    y = float(charged_lepton_yukawa_operator()['eigenvalues_heavy_middle_light'][1])
    g = y/math.sqrt(2)
    v = 1/math.sqrt(math.sqrt(2)*gf)
    z = (w/h)**2
    kernel = transverse_w_higgs_kernel(z, epsabs=epsabs, epsrel=epsrel)
    prefactor = alpha*m*g/(8*math.pi**3*v)
    value = prefactor*kernel['value']
    dot = prefactor*kernel['log_z_derivative']
    return dict(
        value=value, a_mu_transverse_W_Hgamma=value,
        kernel=kernel, z_MW_squared_over_MH_squared=z,
        v_GeV=v, fixed_Y_mu=y, radial_H_muon_coupling=g,
        relative_H_muon_coupling_diagnostic=g*v/m,
        relative_H_W_coupling_from_minimal_kinetic_matching=1.,
        relative_H_muon_coupling_is_fit=False,
        prefactor=prefactor,
        derivatives=dict(alpha=value/alpha, GF=value/(2*gf),
                         muon_mass=value/m, w_mass=2*dot/w,
                         higgs_mass=-2*dot/h),
        quadrature_error_estimate=abs(prefactor)*kernel['quadrature_error_estimate'],
        source=PRIMARY, version='v3', equations='21,28',
        source_scope='section4.1 transverse gauge-independent vertex; section4.2 leading external-mass expansion',
        normalization='alpha(0)*m_mu*(Y_mu/sqrt(2))/(8*pi^3*v); v=(sqrt(2)*GF)^(-1/2)',
        perturbative_order='finite two-loop W/Hgamma projection, leading external m_mu/heavy-mass power',
        no_log_of_external_muon_mass=True,
        gauge_dependent_vertex_and_non_Barr_Zee_completion_included=False,
        HZ_counterpart_included=False,
        full_bosonic_two_loop=None, finite_bosonic_remainder=None,
        numerical_error_is_enclosure=False, complete_uncertainty=False,
        closed_fermion_loops_included=False, quark_Yukawa_assigned=False,
        measured_muon_anomaly_used=False, native_evaluated=False,
        full_EW_two_loop_evaluated=False)
