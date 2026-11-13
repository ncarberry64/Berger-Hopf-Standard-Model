"""Unassigned tension coefficient of the original endpoint action.

This is an affine parameter application at a held canonical state. Its
Legendre cotangent and algebraic source are retained independently; it
does not assert stationarity of that state at nonzero tension.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt


def original_endpoint_area_coefficient(raw,coordinate_lift):
    raw=np.asarray(raw,complex);P=np.asarray(coordinate_lift,complex)
    if raw.shape!=(268,)or P.shape!=(268,252):raise ValueError('original full raw268/phase252 chart required')
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw[:100])
    F=_fields(12,q,v,m,wall);A,B,N=(F[k]for k in('A','B','N'))
    U=F['C']*(dr+F['beta'])/N
    area=-N*A**3*B**3*_sqrt(1-U*U)
    Q=P[:100];gradient=Q.T@area.gradient;hessian=Q.T@area.hessian@Q
    return dict(value=area.value,gradient=gradient,hessian=hessian,
        raw_geometry_gradient=area.gradient,raw_geometry_Hessian=area.hessian,
        position_force=gradient[:106],Legendre_cotangent=gradient[106:212],
        algebraic_source=gradient[212:],wall_velocity=U.value,
        explicit_coordinate_clock_first=0j,
        surface_gamma_assigned=False,parameter_action='-gamma*N*(A^3 B^3)*sqrt(1-U^2)',
        phase_parameter_or_parent_reference_motion_included=False)


def held_endpoint_hamiltonian_area_coefficients(coefficients,Pi,action,area):
    e=np.asarray(coefficients,complex);Pi=np.asarray(Pi,complex);n=len(Pi);v=e[n:2*n]
    return dict(base=Pi@v-action['value'],
        fixed_target_Pi_area_coefficient=-area['value'],
        same_state_Legendre_Pi_area_coefficient=area['Legendre_cotangent']@v-area['value'],
        same_state_Pi_area_coefficient=area['Legendre_cotangent'],
        fixed_state_original_constitutive_area_source=np.r_[area['Legendre_cotangent'],area['algebraic_source']],
        same_state_momentum_reset_does_not_cancel_algebraic_area_source=True,
        fixed_state_stationarity_at_nonzero_gamma_claimed=False)
