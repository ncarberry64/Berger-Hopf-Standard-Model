"""PROPOSED material attachment; never imported by the native operator.

This is one explicit additional domain postulate, not a recovered BHSM law.
It uses the action-associated Dirac-bar Green form, not the bare D5 adjoint
or the conormal of D5^dagger D5. Numerical functions below apply the proposal
only to the retained charged LL source sector. The e_R conjugate sector is
specified in the report, not misidentified with right-spin LL coordinates.
"""
from __future__ import annotations
import numpy as np

CLASSIFICATION = 'PROPOSED_DYNAMIC_AVERAGE_TRACE_ATTACHMENT_NOT_ADOPTED'


def charged_left_projector():
    """Actual Spin4 x SM16 order: LL=6,7, Lorentz left=0,1."""
    mask = np.zeros((4, 16))
    mask[:2, 6:8] = 1
    return np.diag(mask.ravel()).astype(complex)


def apply_spin(matrix, array):
    return np.einsum('oi,imkj->omkj', matrix, array, optimize=True)


def sharp(matrix, source_pairing, target_pairing):
    """Geometric dual; source/target refer to the map's Hilbert spaces."""
    return np.linalg.solve(source_pairing, matrix.conj().T @ target_pairing)


def sharp_jet(matrix, matrix_A, source_pairing, source_pairing_A,
              target_pairing, target_pairing_A):
    adjoint = sharp(matrix, source_pairing, target_pairing)
    return np.linalg.solve(source_pairing,
        matrix_A.conj().T @ target_pairing + matrix.conj().T @ target_pairing_A
        - source_pairing_A @ adjoint)


def source_total_jet(F, F_A, p, p_A, W, W_A, B, B_A):
    """Ordered total derivative, including moving complement/source maps.

    Supplied jets are required, never defaulted to zero. This algebraic
    evaluator does not produce the physical source-dependent maps itself.
    """
    chi = p-W @ (B @ p)
    chi_A = p_A-W_A @ (B @ p)-W @ (B_A @ p)-W @ (B @ p_A)
    return F @ chi, F_A @ chi+F @ chi_A


def readout_jet(kappa, kappa_A, injection_sharp, injection_sharp_A,
                average, average_A, chi, chi_A):
    """Full boundary-map total jet, with no assumed vanishing terms."""
    F = injection_sharp @ average/kappa
    F_A = (-kappa_A/kappa)*F + (
        injection_sharp_A @ average+injection_sharp @ average_A)/kappa
    return F @ chi, F_A @ chi+F @ chi_A


def actual_source_readout(wall, green):
    """Apply proposed F to cached chi=p-W Bp; no old producer replay.

    Both oriented traces are first transported to the inherited common
    section. The cached material source trace is zero; trace(W)=kappa Xi.
    Consequently gamma_average chi=-kappa*b_volume*Xi. This says nothing
    about membership of p in an operator domain or about a stationary flux.
    """
    P = charged_left_projector()
    kappa = float(wall['material_trace'][0])
    b = float(wall['B_volume'][1])
    if float(wall['material_trace'][1]) != 0 or np.any(wall['material_source_trace']):
        raise ValueError('this calculation requires the saved compact material trace')
    if kappa != float(green['kappa']) or float(wall['M4']) != float(green['mu4']):
        raise ValueError('different inclusion/Green pairing')
    j = green['Dirac_bar_Green_density']/float(green['mu4'])
    data = dict(P_left=P, action_Green_Riesz=j,
        readout_average_kernel_left=P/kappa)
    left_norm2 = unmatched_norm2 = 0.
    for n in (1, 3):
        xi = wall[f'normalized_wall_W_input_n{n}']
        average = -kappa*b*xi
        left = -b*apply_spin(P, xi)
        unmatched = average-kappa*left
        # An e_R result is zero here because the actual source is LL-only.
        outside_LL = xi.reshape(4, 16, n+1, n+1, 12).copy()
        outside_LL[:, 6:8] = 0
        if np.any(outside_LL):
            raise ValueError('source is not the saved LL carrier; use full conjugate-sector map')
        data[f'average_trace_chi_n{n}'] = average
        data[f'J_chi_left_n{n}'] = left
        data[f'J_chi_right_singlet_n{n}'] = np.zeros((2, n+1, n+1, 12), complex)
        data[f'unmatched_average_trace_n{n}'] = unmatched
        # Partial at fixed trace/injection/map. Along the material relation,
        # the trace's kappa variation cancels this partial kernel.
        data[f'partial_dJ_d_log_kappa_at_fixed_trace_n{n}'] = -left
        data[f'original_transmission_jump_chi_n{n}'] = np.zeros_like(xi)
        left_norm2 += float(np.vdot(left, left).real)
        unmatched_norm2 += float(np.vdot(unmatched, unmatched).real)
    return data, dict(kappa=kappa, b_volume=b, mu4=float(wall['M4']),
        J_left_column_Frobenius_norm=float(np.sqrt(left_norm2)),
        unmatched_average_column_Frobenius_norm=float(np.sqrt(unmatched_norm2)),
        right_singlet_zero_reason='no e_c/conjugate-e_R carrier in these12 source columns',
        derivative_status='full ordered total-jet formula supplied; physical map/state jets not evaluated; no total derivative set to zero')


def actual_green_controls(wall, green):
    """New average/jump and local dynamic-force controls on actual arrays.

    These are algebra controls of the proposed law, not a native evaluation
    or proof of global closedness, hyperbolicity, tail control or uniqueness.
    """
    P = charged_left_projector(); Q = np.eye(64)-P
    mu = float(wall['M4']); kappa = float(green['kappa'])
    j = green['Dirac_bar_Green_density']/mu
    errors = {'action_Green_skew': float(np.linalg.norm(j+j.conj().T)),
              'action_Green_square': float(np.linalg.norm(j@j+np.eye(64)))}
    average_error = cancel_error = readout_error = 0.
    for n in (1, 3):
        xi = wall[f'normalized_wall_W_input_n{n}']
        apply = lambda matrix, x: apply_spin(matrix, x).reshape(-1, 12)
        # Actual retained source columns; no new angular truncation/profile.
        a = xi; b = apply_spin(j, xi)
        avg = (a+b)/2; jump = apply_spin(j, a-b)
        original = mu*(apply(np.eye(64),a).conj().T@apply(j,a)
                      -apply(np.eye(64),b).conj().T@apply(j,b))
        transformed = mu*(apply(np.eye(64),avg).conj().T@jump.reshape(-1,12)
                          -jump.reshape(-1,12).conj().T@apply(np.eye(64),avg))
        average_error = max(average_error, float(np.linalg.norm(original-transformed)))
        # Allowed trace coordinates for the PROPOSED LL material domain.
        w = apply_spin(P, xi)
        g0 = kappa*w+apply_spin(Q, xi)
        g1 = 1j*kappa*w
        left = g0+apply_spin(-j, g1)/2
        right = g0-apply_spin(-j, g1)/2
        body = mu*(apply(np.eye(64),left).conj().T@apply(j,left)
                  -apply(np.eye(64),right).conj().T@apply(j,right))
        wall_force = -kappa*apply_spin(P,g1)
        force_form = mu*(w.reshape(-1,12).conj().T@wall_force.reshape(-1,12)
                        -wall_force.reshape(-1,12).conj().T@w.reshape(-1,12))
        cancel_error = max(cancel_error, float(np.linalg.norm(body+force_form)))
        readout_error = max(readout_error, float(np.linalg.norm(
            apply_spin(P,g0)/kappa-w)))
    errors.update(average_jump_identity=average_error,
                  proposed_material_Green_balance=cancel_error,
                  proposed_matched_average_constraint=readout_error)
    return errors
