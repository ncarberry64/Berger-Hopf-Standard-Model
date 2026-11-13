"""The bosonic two-loop weak leading logarithm in the calibrated gauge EFT.

This is one evaluated part of the bosonic weak correction.  Its Wilson
coefficients come from the retained minimal gauge-current matching; no
Higgs or quark Yukawa is inferred from a measured pole mass.  The finite
bosonic term, fixed-Y scalar corrections and native completion stay separate.
"""
from __future__ import annotations

import math
from fractions import Fraction

BOSONIC_PRIMARY = 'https://arxiv.org/abs/hep-ph/9512369'
EFT_PRIMARY = 'https://arxiv.org/abs/hep-ph/9803384'


def _finite_positive(**values):
    for name, value in values.items():
        if isinstance(value, bool):
            raise ValueError(f'{name} must be a positive finite scalar')
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f'{name} must be a positive finite scalar') from exc
        if not math.isfinite(number) or number <= 0:
            raise ValueError(f'{name} must be a positive finite scalar')


def bosonic_weak_log_eft_identity():
    """Exact rational operator-mixing decomposition, with source equations.

    C_dipole is the magnetic dipole Wilson coefficient, not a Higgs coupling.
    The identical-current 1/2 normalization cancels its two current choices.
    Subtracting closed-muon contractions leaves the no-closed-fermion class.
    """
    full_vector = Fraction(40, 3)
    full_axial = Fraction(808, 9)
    closed_vector = Fraction(32, 9)
    closed_axial = Fraction(48)
    return dict(
        r='1-4*s', s='sin(theta_W)^2=1-MW^2/MZ^2',
        Wilson_coefficients=dict(C_dipole='(5+r^2)/12', C_vector='r^2/8',
                                 C_axial='1/8'),
        anomalous_dimensions=dict(
            dipole='16', identical_vector=str(full_vector),
            identical_axial=str(full_axial),
            closed_muon_vector=str(closed_vector),
            closed_muon_axial=str(closed_axial),
            open_vector=str(full_vector-closed_vector),
            open_axial=str(full_axial-closed_axial)),
        contraction='16*C_dipole+(88/9)*C_vector+(376/9)*C_axial=(107+23*r^2)/9',
        log_squared_scale_coefficient='-(107+23*(1-4*s)^2)/18=(-65+92*s-184*s^2)/9',
        bosonic_class='no closed fermion loop; closed-muon mixing excluded',
        source_records=[
            dict(url=EFT_PRIMARY, version='v1',
                 equations='11-15,19-24', pages='3-5',
                 scope='gauge dipole/tree Z-current coefficients and QED mixing'),
            dict(url=BOSONIC_PRIMARY, version='v3',
                 equations='10-11',
                 scope='exact weak-angle polynomial multiplying log(MW^2/m_mu^2)')],
        full_two_loop_bosonic_constant_inferred=False,
        Higgs_Yukawa_assigned=False, quark_Yukawa_assigned=False)


def bosonic_weak_leading_log(*, alpha_0,
        fermi_constant_GeV_inverse_squared, muon_mass_GeV,
        w_mass_GeV, z_mass_GeV):
    """Evaluate the leading GF*m_mu^2*alpha electroweak bosonic logarithm.

    Uses Thomson alpha, the rematched Fermi coefficient and the on-shell
    weak-angle prescription.  Only the leading m_mu/MW order is retained.
    MW is the logarithm endpoint used in the direct primary calculation;
    changing that endpoint moves a finite term between log and remainder.
    """
    _finite_positive(alpha=alpha_0, GF=fermi_constant_GeV_inverse_squared,
                     m=muon_mass_GeV, MW=w_mass_GeV, MZ=z_mass_GeV)
    alpha, gf, m, w, z = map(float, (alpha_0,
        fermi_constant_GeV_inverse_squared, muon_mass_GeV,
        w_mass_GeV, z_mass_GeV))
    if not m < w < z:
        raise ValueError('the declared weak hierarchy requires m_mu < MW < MZ')
    s = 1-(w/z)**2
    r = 1-4*s
    prefactor = gf*m*m*alpha/(8*math.sqrt(2)*math.pi**3)
    coefficient = (-65+92*s-184*s*s)/9
    logarithm = 2*math.log(w/m)
    value = prefactor*coefficient*logarithm
    coefficient_s = (92-368*s)/9
    derivatives = dict(
        alpha=value/alpha, GF=value/gf,
        muon_mass=prefactor*coefficient*(2*logarithm-2)/m,
        w_mass=prefactor*(-2*w/z**2*coefficient_s*logarithm
                          +2*coefficient/w),
        z_mass=prefactor*2*w*w/z**3*coefficient_s*logarithm)
    eft_parts = dict(dipole=16*(5+r*r)/12,
                     open_vector=float(Fraction(88, 9))*r*r/8,
                     open_axial=float(Fraction(376, 9))/8)
    independent_value = -prefactor*math.fsum(eft_parts.values())*math.log(w/m)
    return dict(
        value=value, a_mu_bosonic_EW2_leading_log=value,
        common_prefactor=prefactor, sin_squared_theta_W=s,
        logarithm_MW_squared_over_muon_squared=logarithm,
        dimensionless_log_coefficient=coefficient,
        independent_EFT_mixing_parts=eft_parts,
        independent_EFT_value=independent_value,
        direct_minus_EFT_arithmetic_residual=value-independent_value,
        derivatives=derivatives,
        logarithm_endpoint_MZ_minus_MW_diagnostic=
            prefactor*coefficient*2*math.log(z/w),
        endpoint_diagnostic_scope='finite convention shift, not a remainder bound or standard uncertainty',
        source=BOSONIC_PRIMARY, equations='10-11, log terms in a_0,a_2,a_4',
        independent_source=EFT_PRIMARY, independent_equations='11-15,19-24',
        normalization='GF*alpha(0)*m_mu^2/(8*sqrt(2)*pi^3); on-shell weak angle',
        perturbative_order='leading GF*m_mu^2*alpha; two-loop electroweak large logarithm',
        approximation='leading m_mu/MW power only; exact sW^2 polynomial for this logarithm',
        closed_fermion_loops_included=False,
        Higgs_mass_or_Yukawa_used=False, quark_Yukawa_assigned=False,
        measured_muon_anomaly_used=False,
        full_bosonic_two_loop=None, finite_bosonic_remainder=None,
        full_EW_two_loop_evaluated=False, native_evaluated=False,
        complete_uncertainty=False)
