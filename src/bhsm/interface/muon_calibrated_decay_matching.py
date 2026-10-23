"""Selected-input, inclusive local Fermi-theory muon-decay application.

The finite electron-mass tree phase space and the massless O(alpha) QED
coefficient are evaluated separately in the additive Gamma/Gamma_0
convention.  Their sum is a partial decay factor, not a replacement for
the reference two-loop MuLan extraction or a complete BHSM matching.
"""
from __future__ import annotations

import math


FERMI_DECAY_SOURCE = 'https://arxiv.org/abs/hep-ph/9904240'
MULAN_SOURCE = 'https://arxiv.org/abs/1211.0960'
MULAN2013_ROUNDED_ONE_LOOP = -4233.7e-6
MULAN2013_ROUNDED_TWO_LOOP = 36.3e-6


def _positive(value, name):
    if value is None or isinstance(value, bool):
        raise ValueError(f'{name} must be a finite positive scalar')
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{name} must be a finite positive scalar') from exc
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f'{name} must be a finite positive scalar')
    return result


def calibrated_muon_decay_one_loop(*, alpha_0, muon_electron_ratio,
                                   reference_decay_factor=None):
    """Compute F(x)+delta_q1_massless at the supplied Thomson charge.

    x=(m_e/m_mu)^2, F=1-8x-12x^2 log(x)+8x^3-x^4 and
    delta_q1_massless=alpha(0)/(2*pi)*(25/4-pi^2), with massless neutrinos.
    These are Eqs.(2.7)-(2.8) of van Ritbergen/Stuart.  The tree term
    is exact in x within those assumptions; the one-loop term is only
    its electron-mass-independent part.

    MuLan's rounded -4233.7 ppm one-loop term already uses its alpha_e(m_mu)
    and nonzero electron-mass terms; +36.3 ppm is the reference two-loop
    correction including hadronic/tau terms and the finite-mass amendment.
    Thus a difference from those values is not a rounding-only discrepancy.
    Changing from alpha(0) to alpha_e(m_mu) reorganizes O(alpha^2) and higher
    terms.  It requires consistent two-loop accounting, not an additional
    one-loop term to add to this partial alpha(0) calculation.

    The optional reference factor is comparison data.  No configuration,
    Fermi constant, scalar coupling or native correction is updated here.
    """
    alpha = _positive(alpha_0, 'alpha_0')
    ratio = _positive(muon_electron_ratio, 'muon_electron_ratio')
    if ratio <= 1:
        raise ValueError('muon_electron_ratio must exceed one for muon decay')
    x = (1/ratio)**2
    log_x = -2*math.log(ratio)
    phase_correction = math.fsum((-8*x, -12*x*x*log_x, 8*x**3, -x**4))
    phase = 1 + phase_correction
    coefficient = 25/4 - math.pi**2
    q1 = alpha/(2*math.pi)*coefficient
    partial = phase + q1
    dphase_log_ratio = math.fsum((16*x, 24*x*x*(2*log_x+1), -48*x**3, 8*x**4))
    if reference_decay_factor is None:
        reference = phase + MULAN2013_ROUNDED_ONE_LOOP + MULAN2013_ROUNDED_TWO_LOOP
        reference_role = 'SELECTED_TREE_PHASE_PLUS_ROUNDED_MULAN_REFERENCE_CORRECTIONS'
    else:
        reference = _positive(reference_decay_factor, 'reference_decay_factor')
        reference_role = 'CALLER_SUPPLIED_COMPARISON_ONLY'
    return {
        'alpha_0': alpha,
        'muon_electron_ratio': ratio,
        'electron_muon_squared_ratio': x,
        'tree_phase_space': phase,
        'delta_q0': phase_correction,
        'massless_one_loop_coefficient_alpha_over_2pi': coefficient,
        'delta_q1_massless_alpha_0': q1,
        'partial_decay_factor_tree_plus_massless_one_loop': partial,
        'normalization': 'Gamma=G_F^2*m_mu^5/(192*pi^3)*(1+sum delta_q_i); additive in Gamma/Gamma_0',
        'derivative_alpha_0': coefficient/(2*math.pi),
        'derivative_log_muon_electron_ratio': dphase_log_ratio,
        'reference_comparison': {
            'reference_role': reference_role,
            'reference_decay_factor': reference,
            'partial_factor_minus_reference': partial-reference,
            'relative_partial_factor_minus_reference': partial/reference-1,
            'rounded_MuLan_delta_q1': MULAN2013_ROUNDED_ONE_LOOP,
            'massless_alpha_0_delta_q1_minus_rounded_MuLan': q1-MULAN2013_ROUNDED_ONE_LOOP,
            'rounded_MuLan_delta_q2': MULAN2013_ROUNDED_TWO_LOOP,
            'comparison_is_rounding_only': False,
            'reference_one_loop_scope': 'alpha_e(m_mu) and nonzero electron-mass terms; MuLan2013 p28',
            'reference_two_loop_scope': 'photonic, electron, muon, tau, hadronic loops and finite-electron-mass amendment; MuLan2013 p28',
        },
        'sources': {
            'decay_formula': {'url': FERMI_DECAY_SOURCE, 'equations': '2.6-2.8; alpha_e scheme discussion4.13'},
            'reference': {'url': MULAN_SOURCE, 'equations': '23; pp27-28'},
        },
        'massless_neutrinos_assumed': True,
        'finite_electron_mass_tree_evaluated': True,
        'finite_electron_mass_one_loop_remainder': None,
        'running_coupling_reorganization_included': False,
        'complete_order_alpha_squared_correction': None,
        'higher_local_order_correction': None,
        'native_lifetime_correction': None,
        'perturbative_truncation_bound': None,
        'complete_decay_factor': None,
        'complete_GF_matching': False,
        'input_configuration_changed': False,
        'measured_muon_anomaly_used': False,
        'action_selected': False,
        'Gate7_closed': False,
        'scope': 'CALIBRATED_LOCAL_FERMI_DECAY_TREE_PLUS_MASSLESS_ONE_LOOP_COMPONENT_ONLY',
    }
