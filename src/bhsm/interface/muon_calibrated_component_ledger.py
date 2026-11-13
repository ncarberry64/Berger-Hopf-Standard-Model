"""Shared-input accounting for evaluated calibrated Pauli components.

The caller supplies a sum of actually evaluated components, not a completed
BHSM observable.  Derivatives are added before covariance propagation.  In
particular the optical mass is shared by the anomaly and its SI magneton;
it is not an independent uncertainty appended to the magnetic moment.
"""
from __future__ import annotations

import numpy as np
import math

from .muon_calibrated_current_response import magnetic_moment_accounting
from .muon_calibrated_local_pauli import lepton_vacuum_polarization_pauli


def leading_top_electromagnetic_vp(*, alpha, muon_mass_GeV, top_pole_mass_GeV):
    """Lowest electromagnetic top-current VP with its actual heavy mass.

    The vector-current color/charge factor is Nc*Q_t^2=4/3; no top
    Higgs Yukawa is inferred from its mass.  The five-flavor data do not
    include this sector.  QCD/weak corrections to this top loop are not
    evaluated here.
    """
    a,m,M=map(float,(alpha,muon_mass_GeV,top_pole_mass_GeV))
    if not np.isfinite([a,m,M]).all() or min(a,m,M)<=0:
        raise ValueError('positive finite alpha and pole masses required')
    insertion=lepton_vacuum_polarization_pauli(m/M,eps=1e-18)
    prefactor=(4/3)*(a/math.pi)**2
    value=prefactor*insertion['coefficient']
    log_derivative=prefactor*insertion['derivative_log_mass_ratio']
    return dict(value=value,derivative_alpha=2*value/a,
        derivative_muon_mass=log_derivative/m,derivative_top_mass=-log_derivative/M,
        heavy_leading_upper=(4/3)*(a/math.pi)**2*(m/M)**2/45,
        upper_provenance='log(1+z)<=z in the Thomson-subtracted one-loop VP integral',
        quadrature_error_estimate=prefactor*insertion['quadrature_error_estimate'],
        color_charge_factor=4/3,top_Higgs_Yukawa_assigned=False,
        current_scope='lowest electromagnetic Dirac top vector-current loop; no five-flavor spectral overlap',
        uncomputed_QCD_weak_width_correction_estimate=abs(value),
        error_scope='quadrature estimate and deliberately conservative100%-of-leading higher-interaction size estimate, not a full BHSM bound',
        full_top_current_evaluated=False)


def shared_observable_uncertainty(*, a_subtotal, mass_GeV,
                                  component_gradients, mass_gradient,
                                  standard_uncertainties, charge_sign,
                                  primitive_covariance=None):
    """Propagate one common input vector to (a, g, mu_z) at first order.

    With covariance absent, the diagonal calculation is illustrative and
    the absolute-gradient sum is an input standard-uncertainty upper bound
    over all possible primitive correlations.  Neither is a confidence
    interval or a bound on omitted native/theory contributions.
    """
    gradients=np.asarray(component_gradients,dtype=float)
    mass_row=np.asarray(mass_gradient,dtype=float)
    std=np.asarray(standard_uncertainties,dtype=float)
    if (gradients.ndim!=2 or not len(gradients) or
            gradients.shape[1:]!=mass_row.shape or std.shape!=mass_row.shape or
            mass_row.ndim!=1 or np.any(std<0) or
            not all(np.isfinite(x).all() for x in (gradients,mass_row,std))):
        raise ValueError('finite common primitive gradients and nonnegative standard uncertainties required')
    accounting=magnetic_moment_accounting(a_mu=a_subtotal,mass_GeV=mass_GeV,
                                          charge_sign=charge_sign)
    a_row=np.sum(gradients,axis=0)
    rows=np.stack((a_row,2*a_row,
        accounting['da_to_dmoment_J_per_T']*a_row+
        accounting['dmass_to_dmoment_J_per_T_per_GeV']*mass_row))
    assumed=primitive_covariance is None
    covariance=np.diag(std**2) if assumed else np.asarray(primitive_covariance,float)
    n=len(std)
    if covariance.shape!=(n,n) or not np.isfinite(covariance).all():
        raise ValueError('finite common primitive covariance required')
    scale=max(float(np.max(abs(covariance))),np.finfo(float).tiny)
    if (not np.allclose(covariance,covariance.T,atol=scale*1e-13,rtol=1e-13) or
            np.min(np.linalg.eigvalsh(covariance)) < -scale*1e-12):
        raise ValueError('symmetric positive-semidefinite primitive covariance required')
    if not np.allclose(np.diag(covariance),std**2,atol=scale*1e-13,rtol=1e-10):
        raise ValueError('covariance diagonal must equal supplied primitive variances')
    output=rows@covariance@rows.T
    return dict(accounting=accounting,output_order=['a_subtotal','g_subtotal','mu_z_subtotal_J_per_T'],
        summed_a_gradient=a_row.tolist(),output_gradient=rows.tolist(),
        propagated_covariance=output.tolist(),
        input_standard_uncertainties=np.sqrt(np.maximum(np.diag(output),0)).tolist(),
        input_standard_uncertainty_upper_over_all_correlations=(abs(rows)@std).tolist(),
        primitive_independence_is_only_illustrative=assumed,
        supplied_primitive_covariance=None if assumed else covariance.tolist(),
        error_scope='first-order shared metrological inputs of evaluated components only; no omitted-component or probability enclosure',
        complete_observable=False)
