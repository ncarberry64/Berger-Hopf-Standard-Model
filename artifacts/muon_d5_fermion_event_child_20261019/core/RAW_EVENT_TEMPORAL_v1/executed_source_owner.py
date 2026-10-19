"""Affected local Higgs-bundle time jets at the final event map.

This is a one-sided E1 connection jet, not the full Spin/reset temporal
map or a boundary history on the child future. All map velocities remain
independent Jacobi coordinates.
"""
from __future__ import annotations
import numpy as np
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def temporal_map_source_ports(A_parent,A_child,kappa,U):
    """All7 independent map slots with the actual unchanged A0 vertices.

    The equation-derived field columns have support only in raw168:180
    and260:264. In d5_trial_stage_coefficients gauge[:,0] is independent
    of those columns and of raw99; mechanical inheritance adds to2: only.
    Thus their direct deltaA0 is exactly0, not an unknown default.
    """
    p,c,u=map(np.asarray,(A_parent,A_child,U));k=complex(kappa)
    if any(a.shape!=(2,2) for a in (p,c,u)):
        raise ValueError('actual original Higgs-representation temporal vertices required')
    J=np.sqrt(2)*higgs_u2_real_representation()['complex_generators'][:3]
    ux=np.zeros((7,2,2),complex);ux[3:6]=J@u;ux[6]=1j*u
    first=np.array([-c@a+k*a@p for a in ux])
    return dict(map_first=ux,temporal_first=first,
        original_rows=first+c@ux-k*ux@p)


def material_velocity_source_from_spin(S,S_source,velocity):
    """Recover the evaluated wall rapidity source; no additional solve."""
    s,x=np.asarray(S),np.asarray(S_source)
    G=full_d5_localized_lepton_trace()['gamma5D_self_dual128']
    if s.shape==(384,384):A=np.kron(np.eye(3),G[0]@G[4])
    elif s.shape==(128,128):A=G[0]@G[4]
    else:raise ValueError('original128 or384 material Spin frame required')
    eta=-2*np.trace(A@x@np.linalg.inv(s))/len(s)
    return (1-complex(velocity)**2)*eta


def normal_rate_clock_ports(kappa,parent_velocity,child_velocity,
        parent_velocity_source,child_velocity_source):
    """Independent proper-normal RATE ports; held geometry has deltaN=0.

    ell=N sqrt(1-U^2); the rate column is raw99 only. No displacement,
    field, native or incoming/outgoing history is set to zero here.
    """
    k,p,c,px,cx=map(complex,(kappa,parent_velocity,child_velocity,
        parent_velocity_source,child_velocity_source))
    return np.array([k*p*px/(1-p*p),-k*c*cx/(1-c*c)])
