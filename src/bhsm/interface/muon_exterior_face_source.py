"""Saved muon source at the C2 cut; no exterior propagator is fabricated.

The angular calculation assumes a matched coframe/carrier in the local
quotient section (u,v)=(w,1). That matching is NOT supplied by this module.
Its arrays are conditional diagnostics, not an actual parent coefficient,
an AE4 Hessian, or a radial lift.
"""
from __future__ import annotations

import numpy as np


def mechanical_angular_source(real_modes, jmath, Q, curl):
    """Conditional d_omega application, keeping the charge output.

    Coefficients multiply normalized spin-1/2 Wigner functions in the
    saved body coframe.  omega=lambda theta, source=-i Q T_b Y_A.
    Return factors of T_b and lambda separately; neither is a vertex fit.
    This assumes the saved modes and theta are the SAME coframe, including
    its Hodge sign and carrier trivialization. The retained producers have
    not established that identification. Do not use it as a parent source
    action before applying the actual coframe/carrier/source conversion.
    """
    Y = np.asarray(real_modes, complex)
    J, q, k = map(lambda x: np.asarray(x, complex), (jmath, Q, curl))
    if Y.shape != (8, 3, 2, 2) or J.shape != (3, 16, 16):
        raise ValueError('saved eight modes and rank16 mechanical carrier required')
    if q.shape != (16, 16) or k.shape != (8, 8):
        raise ValueError('saved Q and eight-mode curl required')
    eps = np.zeros((3, 3, 3))
    for c, a, b in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        eps[c, a, b] = 1
        eps[c, b, a] = -1
    source_generator = -1j*q
    comm = J @ source_generator - source_generator @ J
    # curl(Y_A)=sum_B curl[B,A]Y_B in the saved function convention.
    dY = np.einsum('ba,bcmk->acmk', k, Y)
    plain = dY[..., None, None]*source_generator
    complement = np.einsum('cab,Abmk,aij->Acmkij', eps, Y, comm)
    gram = lambda x, y: np.einsum('acmkij,bcmkij->ab', x.conj(), y)
    # Reuse the established exact trace; do not redetermine the index8
    # conversion or count the carrier/family/modes again.
    qnorm = 16/3
    return dict(source_generator=source_generator, commutator=comm,
                commutator_Gram=np.einsum('aij,bij->ab', comm.conj(), comm),
                angular_plain=plain, angular_connection=complement,
                QQ_plain=gram(plain, plain)/qnorm,
                QQ_cross=gram(plain, complement)/qnorm,
                QQ_connection=gram(complement, complement)/qnorm,
                Q_norm=qnorm)


def conditional_angular_coefficient(parent, principal, angular):
    """Contract the assumed-frame QQ row; do not add it to the weak solve.

    This is a conditional QQ compression only. It does not establish a
    nonzero mixed Hessian: the curvature contact and other rows may cancel.
    It does not eliminate constraints or the AE4 induced remainder.
    It supplies no radial profile or temporal endpoint condition.
    """
    A, B, C, r = [np.asarray(parent[k], float) for k in
                   ('A', 'B', 'C_rho', 'base_radius')]
    lam = A*A/(A*A+B*B)
    density = np.zeros_like(r)
    regular = r > 0
    density[regular] = (principal['r'][regular] *
                        (C[regular]/r[regular])**2)
    # At the regular pole W=O(rho^3), r=O(rho): W/r=O(rho^2).
    # This local coefficient has limit zero; it is not a pole boundary load.
    if np.any(~regular & (parent['rho'][None, :] != 0)):
        raise ValueError('only the inherited regular pole may have r=0')
    cross = angular['QQ_cross'] + angular['QQ_cross'].conj().T
    matrix = (angular['QQ_plain'][None, None] +
              lam[..., None, None]*cross[None, None] +
              lam[..., None, None]**2*angular['QQ_connection'][None, None])
    return dict(mechanical_lambda=lam, angular_density_per_kappa1=density,
                QQ_covariant_angular_matrix=matrix,
                QQ_angular_stiffness_per_kappa1=density[..., None, None]*matrix)


def face_source_kinematics(log_radius, H, electric, shift):
    """Pointwise trace-source and known terms in temporal momentum.

    For the unit b direction at a material boundary corner, b_tau=0, b=1.
    pi_tau=-e*zeta*b_rho-e*H/2.  b_rho is explicitly unevaluated.
    A source-direction coefficient held at one is not a constant physical
    beta field: T_b and its derivative are retained.
    """
    x, h = float(log_radius), float(H)
    Tb = float(np.exp(-x/2)/np.sqrt(2*np.pi**2))
    f = float(Tb/np.exp(x))
    return dict(T_b=Tb, f_R=f, T_b_prime=-h*Tb/2,
                f_R_prime=-3*h*f/2, H=h,
                temporal_radial_jet_coefficient=-float(electric)*float(shift),
                temporal_known_moving_frame_term=-float(electric)*h/2,
                radial_jet=None, complete_temporal_momentum=None,
                exterior_affine_return=None)


def cut_orientations():
    return dict(past_core_outward=-1, past_prefix_outward=1,
                future_core_outward=1, future_face='owned canonical stop',
                future_exterior_outward=None,
                transmission='core_outward_traction=-prefix_outward_traction',
                material_outward='radial conormal, not temporal momentum')
