"""Consumed total branch contractions for the adopted AE4 cutoff.

These small helpers evaluate supplied form/branch jets. They do not generate
a physical interface branch, event or heat action from finite photon probes.
All form matrices must already include their owned geometric pairing and
domain pullback. Parameter derivatives are real; complex currents are then
extended linearly in the real Hessian coefficients.
"""
from __future__ import annotations

import numpy as np

from .ae4_stratified_dirac_zeta_induced_owner import native_heat_length_squared_jets


def quadratic_form_branch_jets(K, psi, *, K_x, K_y, K_xy, psi_x, psi_y, psi_xy):
    """Full total two-jet of <psi,K psi>, without an eigenline assumption.

    Source/event/domain/pairing motion is included in the supplied total
    K/psi jets. No second surface-motion correction belongs after this call.
    In particular both second embedding terms involving psi_xy are retained.
    """
    K, K_x, K_y, K_xy = [np.asarray(z, complex) for z in (K,K_x,K_y,K_xy)]
    p, px, py, pxy = [np.asarray(z, complex) for z in (psi,psi_x,psi_y,psi_xy)]
    def b(left, form, right): return np.vdot(left, form@right)
    base = b(p,K,p)
    x = b(px,K,p)+b(p,K_x,p)+b(p,K,px)
    y = b(py,K,p)+b(p,K_y,p)+b(p,K,py)
    xy = (b(pxy,K,p)+b(px,K_y,p)+b(px,K,py)
          +b(py,K_x,p)+b(p,K_xy,p)+b(p,K_x,py)
          +b(py,K,px)+b(p,K_y,px)+b(p,K,pxy))
    return dict(value=base,x=x,y=y,xy=xy,
                scope='SUPPLIED_TOTAL_FORM_AND_EMBEDDING_JETS__NOT_A_PHYSICAL_PRODUCER')


def cutoff_from_total_contractions(r, i):
    """Compose total scalar contractions with the adopted quotient rule."""
    r0, i0 = complex(r['value']), complex(i['value'])
    if r0.imag != 0 or i0.imag != 0:
        raise ValueError('real physical base resistance/inertia contractions required')
    return native_heat_length_squared_jets(
        r=r0.real,i=i0.real,r_x=r['x'],r_y=r['y'],r_xy=r['xy'],
        i_x=i['x'],i_y=i['y'],i_xy=i['xy'])


def lower_limit_coefficients(*, r, i, r_x, r_y, r_xy, i_x, i_y, i_xy):
    """Exact adopted quotient consumed into the existing AE4 length term.

    Accepts numbers or symbolic total contractions. No heat trace is supplied
    here. H_x=STr(exp(-cP)P_x), H_y similarly, H_P=STr(P exp(-cP)).
    T is STr(exp(-cP)); all have the SAME grading, quotient and domain.
    """
    dx = r*i_x-i*r_x
    dy = r*i_y-i*r_y
    return {
        'c':i/r,
        'coefficient_H_y':-dx/(2*r**2),
        'coefficient_H_x':-dy/(2*r**2),
        'coefficient_T':(i_xy/i-i_x*i_y/i**2-r_xy/r+r_x*r_y/r**2)/2,
        'coefficient_H_P':-dx*dy/(2*i*r**3),
        'scope':'EXACT_CONDITIONAL_LENGTH_TERM__NATIVE_HEAT_COTANGENTS_NOT_GENERATED',
    }
