"""On-shell NLO HVP projections of the retained measured two-current spectrum.

The exact spacelike kernels are Balzani--Laporta--Passera, arXiv:2112.05704v3,
Eqs. (21)--(27). These are matched minimal-current hadronic components, not
the complete BHSM photon/vertex remainder. The input spectrum is unchanged.
"""
from __future__ import annotations

import math
import mpmath as mp
import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_calibrated_hvp_spectral import delta_alpha_had_spacelike

KERNEL_SOURCE = 'https://arxiv.org/abs/2112.05704'


def _positive(value, name):
    try:
        value = float(value)
    except (ValueError,TypeError,OverflowError) as error:
        raise ValueError('finite positive ' + name + ' required') from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError('finite positive ' + name + ' required')
    return value


def nlo_photonic_kernel_log_endpoint(v, *, decimal_precision=90):
    """Exact kappa^(4)(1-exp(-v)), with cancellation evaluated in mp arithmetic.

    v is a numerical integration coordinate, not a physical cutoff. Keeping
    u=-exp(-v) in high precision avoids binary64 x rounding to one. The
    rational/dilogarithmic formula has large cancelling terms near u=0.
    """
    v = _positive(v, 'v')
    if not isinstance(decimal_precision, int) or decimal_precision < 40:
        raise ValueError('integer decimal_precision>=40 required')
    # Near u=0 individual terms grow as exp(2v), and the final F4 is O(u).
    # Three v/log(10) digits may cancel. Preserve at least 25 guard digits.
    if decimal_precision < 3*v/math.log(10) + 25:
        raise ValueError('insufficient kernel decimal precision for endpoint coordinate')
    with mp.workdps(decimal_precision):
        u = -mp.exp(-mp.mpf(str(v)))
        R1 = (23*u**6-37*u**5+124*u**4-86*u**3-57*u**2+99*u+78)/(72*(u-1)**2*u*(u+1))
        R2 = (12*u**8-11*u**7-78*u**6+21*u**5+4*u**4-15*u**3+13*u+6)/(12*(u-1)**3*u*(u+1)**2)
        R3 = (u+1)*(-u**3+7*u**2+8*u+6)/(12*u**2)
        R4 = (-7*u**4-8*u**3+8*u+7)/(12*u**2)
        R5 = -(3*u**4+5*u**3+7*u**2+5*u+3)/(6*u**2)
        F4 = (R1 + R2*mp.log(-u) + R3*mp.log1p(u) + R4*mp.log1p(-u)
              + R5*(4*mp.polylog(2,u)+2*mp.polylog(2,-u)
                    + mp.log(-u)*(2*mp.log1p(-u)+mp.log1p(u))))
        return float(2*(1-u)/((1+u)*u)*F4)


def one_loop_lepton_delta_alpha(Q_squared, mass, alpha0):
    """Thomson-subtracted positive lepton VP, Eq. (27).

    Delta=(alpha/pi)*2 int_0^1 dy y(1-y) log(1+k y(1-y)).
    The elementary integral and its small-k beta series avoid cancellations.
    The alternating-series remainder is <= the first omitted term; floating
    arithmetic is not enclosed by that statement.
    """
    Q = float(Q_squared)
    m = _positive(mass, 'lepton pole mass')
    a = _positive(alpha0, 'alpha0')
    if not math.isfinite(Q) or Q < 0:
        raise ValueError('finite nonnegative Q_squared required')
    k = Q/(m*m)
    if not math.isfinite(k):
        raise ValueError('finite Q_squared/mass_squared required')
    if k < 1:
        term = k/15
        terms = []
        for n in range(1,33):
            terms.append(term)
            term *= -k*n*(n+2)**2/((n+1)*(2*n+5)*(2*n+4))
        integral = math.fsum(terms)
    else:
        beta = math.sqrt(1+4/k)
        L = 2*math.asinh(math.sqrt(k)/2)
        integral = 4/(3*k)-5/9+(1-2/k)*beta*L/3
    return a/math.pi*integral


def _row(value, stat, systematic, undressing):
    se = float(np.linalg.norm(stat))
    sy = float(np.linalg.norm(systematic))
    return dict(value=float(value), statistical_error=se, systematic_error=sy,
                spectral_error=float(np.hypot(se,sy)),
                statistical_error_vector=stat.tolist(), systematic_error_vector=systematic.tolist(),
                undressing_error_estimate=float(undressing))


def next_to_leading_hvp_pauli(spectrum, alpha0, m_mu, m_e, m_tau, *,
                            order=24, spectral_order=20, endpoint_v=32.,
                            kernel_decimal_precision=90):
    """Evaluate all three NLO HVP classes against the same physical spectrum.

    Class 4a includes the muon VP in the two-loop muon kernel; 4b inserts
    electron/tau VP only; 4c has two hadronic insertions. Internal HVP
    radiation (4d) already belongs to the supplied inclusive R and is not
    added. Uncertainty vectors remain shared, including between the classes.
    Nonlinear 4c errors are first-order covariance propagation, not enclosures.
    """
    a = _positive(alpha0,'alpha0')
    m = _positive(m_mu,'muon pole mass')
    me = _positive(m_e,'electron pole mass')
    mt = _positive(m_tau,'tau pole mass')
    V = _positive(endpoint_v,'endpoint_v')
    if V < 8 or not isinstance(order,int) or order < 4:
        raise ValueError('endpoint_v>=8 and integer order>=4 required')
    if not isinstance(spectral_order,int) or spectral_order < 4:
        raise ValueError('integer spectral_order>=4 required')
    if not isinstance(kernel_decimal_precision,int) or kernel_decimal_precision < 3*V/math.log(10)+25:
        raise ValueError('insufficient high-precision endpoint kernel arithmetic')
    edges = sorted(set([0.,1.,2.,4.,8.,16.,V] + ([32.] if V>32 else [])))
    edges = [v for v in edges if v <= V]
    z,w = leggauss(order)
    values = np.zeros(3)
    stat = systematic = None
    undressing = np.zeros(3)
    source_tails = np.zeros(3)
    for lo,hi in zip(edges[:-1],edges[1:]):
        for v,weight in zip((lo+hi)/2+(hi-lo)/2*z, (hi-lo)/2*w):
            end = math.exp(-v)
            x = -math.expm1(-v)
            Q = m*m*x*x/end
            hrow = delta_alpha_had_spacelike(spectrum,Q,a,order=spectral_order)
            h = hrow['value']
            lepton = (one_loop_lepton_delta_alpha(Q,me,a)
                      + one_loop_lepton_delta_alpha(Q,mt,a))
            k4 = nlo_photonic_kernel_log_endpoint(float(v),decimal_precision=kernel_decimal_precision)
            factors = np.array([(a/math.pi)**2*k4*end,
                                a/math.pi*2*lepton*end*end,
                                a/math.pi*end*end]) * weight
            values += factors*np.array([h,h,h*h])
            gradient = factors*np.array([1.,1.,2*h])
            st = np.asarray(hrow['statistical_error_vector'])
            sy = np.asarray(hrow['systematic_error_vector'])
            if stat is None:
                stat = np.zeros((3,len(st)))
                systematic = np.zeros((3,len(sy)))
            stat += gradient[:,None]*st
            systematic += gradient[:,None]*sy
            undressing += np.abs(gradient)*hrow['undressing_error_estimate']
            tail = hrow['tail_asymptotic_estimate']
            source_tails += factors*np.array([tail,tail,2*h*tail+tail*tail])
    classes = {name:_row(values[i],stat[i],systematic[i],undressing[i])
               for i,name in enumerate(['4a_photonic_and_muon_VP','4b_electron_tau_VP','4c_double_hadronic_VP'])}
    total = _row(float(np.sum(values)),np.sum(stat,axis=0),np.sum(systematic,axis=0),float(np.sum(undressing)))
    return dict(NLO_HVP=total,classes=classes,alpha0=a,m_mu_GeV=m,m_e_GeV=me,m_tau_GeV=mt,
                numerical_method='exact spacelike kernels; x=1-exp(-v); piecewise Gauss quadrature; high-precision dilogarithmic kernel',
                outer_order=order,spectral_order=spectral_order,endpoint_v=V,
                kernel_decimal_precision=kernel_decimal_precision,
                numerical_endpoint_remainder_included=False,
                numerical_endpoint_remainder_enclosure=None,
                source_ultraviolet_tail_asymptotic_estimate=float(np.sum(source_tails)),
                source_ultraviolet_tail_class_estimates=source_tails.tolist(),
                error_scope='shared source covariance propagated to first order; quadrature/refinement estimates require comparison; neither endpoint nor full-QCD tail rigorously enclosed',
                kernel_source=KERNEL_SOURCE,kernel_equations='21-27',
                overlap={'4d_internal_hadronic_radiation':'already inside inclusive spectral input; excluded here',
                         'pure_leptonic_QED':'not included',
                         'muon_VP':'in 4a; not added again to 4b'},
                classification='CALIBRATED_MINIMAL_CURRENT_HADRONIC_NLO_PROJECTION',
                measured_anomaly_used=False,SM_total_used=False,complete_native_remainder=False,
                action_selected=False,Gate7_closed=False)
