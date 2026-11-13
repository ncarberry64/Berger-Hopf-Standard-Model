"""Lifetime matching of the complete temporal four-current rate.

This solves the already evaluated operator's low-energy matching equation.
It does not identify that local operator with the full decay amplitude or
replace the uncomputed non-V-A radiative correction by its V-A value.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq
from .muon_coupled_tensor_decay_rate import tensor_tree_decay_rate


def temporal_tensor_lifetime_match(tensor,temporal_coefficients,*,
        muon_mass_GeV,electron_mass_GeV,lifetime_seconds,hbar_GeV_seconds,
        inclusive_radiative_fraction=0.,radial_order=24):
    """Solve C(E)*(1+delta_decay)=E**4*hbar/tau on one local restriction.

    The supplied delta is an explicit order/model input. The default
    executes the tree equation; it is not a statement that the physical
    correction vanishes. No measured anomaly or magnetic moment enters.
    """
    values=np.asarray([muon_mass_GeV,electron_mass_GeV,lifetime_seconds,
        hbar_GeV_seconds,inclusive_radiative_fraction])
    if (not np.isrealobj(values)or not np.isfinite(values).all()
            or min(values[0],values[2],values[3])<=0
            or not 0<=values[1]<values[0]or values[4]<=-1):
        raise ValueError('ordered measured masses, positive lifetime/hbar and explicit real radiative fraction required')
    M,m,tau,hbar,delta=map(float,values)
    args=dict(muon_mass_GeV=M,electron_mass_GeV=m,radial_order=radial_order)
    static=tensor_tree_decay_rate(tensor,**args)['tree_rate_coefficient_GeV5']
    if static<=0:raise ArithmeticError('zero local decay rate cannot normalize an energy unit')
    observed=hbar/tau;seed=(static*(1+delta)/observed)**.25
    calls=[]
    def rate(E):
        r=tensor_tree_decay_rate(tensor,temporal_coefficients=temporal_coefficients,
            action_energy_unit=E,**args)['tree_rate_coefficient_GeV5']
        calls.append((E,r));return r
    def equation(E):return rate(E)*(1+delta)/(observed*E**4)-1
    lo,hi=seed*.99,seed*1.01
    flo,fhi=equation(lo),equation(hi)
    if flo*fhi>=0:raise ArithmeticError('the local temporal rate does not bracket its static matching branch')
    E=brentq(equation,lo,hi,xtol=seed*2e-14,rtol=2e-14)
    center=rate(E);elasticities=[]
    for step in(1e-3,5e-4):
        elasticities.append((np.log(rate(E*np.exp(step)))-
            np.log(rate(E*np.exp(-step))))/(2*step))
    elasticity=elasticities[-1];den=4-elasticity
    if not np.isfinite(den)or den<=0:
        raise ArithmeticError('conditional lifetime branch loses its positive scale derivative')
    return dict(conditional_E_kappa_GeV=E,conditional_muon_mass_action=M/E,
        conditional_electron_mass_action=m/E,tree_rate_coefficient_GeV5=center,
        inclusive_radiative_fraction=delta,measured_rate_GeV=observed,
        reconstructed_rate_GeV=center*(1+delta)/E**4,
        normalized_matching_residual=center*(1+delta)/(observed*E**4)-1,
        evaluated_rate_calls=np.array(calls),static_matching_seed_GeV=seed,
        temporal_rate_log_energy_elasticity=elasticity,
        elasticity_step_halving_difference=elasticities[-1]-elasticities[0],
        conditional_log_E_derivative_log_lifetime=1/den,
        conditional_log_E_derivative_log_hbar=-1/den,
        conditional_log_E_derivative_radiative_fraction=1/((1+delta)*den),
        conditional_log_mass_derivative_radiative_fraction=-1/((1+delta)*den),
        mass_affine_normal_equation='a_represented(E,delta)=A*m_mu/E+B; da/ddelta=-A*m_mu/[E*(1+delta)*(4-dlogC/dlogE)], with this E0 graph A,B held fixed',
        matching_equation='C_full_temporal(E)*(1+delta_decay)=E^4*hbar/tau_mu',
        full_nonVA_tensor_used=True,physical_nonVA_radiative_fraction_completed=False,
        physical_local_operator_and_external_domain_identified=False,
        physical_unit_selected=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 same local temporal series and spin-summed phase-space contraction; root arithmetic and finite-difference elasticity evaluated, not an action/domain/spatial-momentum/radiative error enclosure')
