"""Source-directed application of an AVAILABLE photon-action component.

This muon realization uses the saved angular primitive at one actual cut
point. It is not K_0,Q on the stratified domain. In particular, no temporal,
radial, constraint, completion, or induced term is silently set to zero.
The negative Lorentz angular sign is retained; no heat kernel is applied.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import block_diag

from bhsm.interface.muon_matched_mechanical_source import angular_blocks


QNORM = 16 / 3


def primitive_cut_action(saved, geometry, *, radial_index=-1):
    """Materialize the full n1+n3 angular density and geometric one-form Gram.

    Coordinates are the saved b frame: a=T_b b, beta=T_b b. The internal
    coefficient basis has unit Tr16 norm. Its source columns have Gram
    Tr16 Q^2 I8. K is per kappa1; kappa1 is NOT assigned a physical value.
    M is the geometric one-form pairing, not the Maxwell velocity Hessian.
    """
    lam = float(saved['mechanical_lambda'][radial_index])
    density = float(saved['angular_density'][radial_index])
    blocks, source, expected, gradient = [], [], [], []
    for n in (1, 3):
        C, T, B, J, ad = angular_blocks(n)
        d = C + (lam - 1) * T
        h = d.conj().T @ d + 4 * lam * (lam - 1) * B
        # Spectator Wigner index is retained. No projection onto eight modes.
        blocks.append(-density / QNORM * np.kron(h, np.eye(n + 1)))
        source.append(saved[f'transformed_n{n}'].reshape(8, -1).T)
        expected.append(saved[f'weak_angular_row_n{n}'][radial_index].reshape(8, -1).T)
        G0 = np.einsum('imn,cd->icmdn', 2j * J, np.eye(4))
        G1 = np.einsum('icd,mn->icmdn', ad, np.eye(n + 1))
        G = (G0 - G1).reshape(12 * (n + 1), 4 * (n + 1))
        gradient.append(np.kron(G, np.eye(n + 1)))
    K = block_diag(*blocks)
    # Encode the analytic Hermitian density as exactly Hermitian binary64
    # input for the frozen-matrix certificate. This is not a regularizer.
    K = (K + K.conj().T) / 2
    upper = np.triu(K, 1)
    K = upper + upper.conj().T + np.diag(K.diagonal().real)
    S = np.vstack(source)
    G = block_diag(*gradient)
    nu = float(geometry['proper_lapse'][0, radial_index])
    C = float(geometry['C_rho'][0, radial_index])
    r = float(geometry['base_radius'][0, radial_index])
    R = float(geometry['boundary_radius'][0])
    m = nu * C * r / R
    if not m > 0:
        raise ValueError('nondegenerate saved cut point required')
    Tb = float(saved['T_b'])
    checks = dict(
        primitive_saved_row_absolute_residual=float(np.linalg.norm(K @ S - np.vstack(expected))),
        source_Gram_absolute_residual=float(np.linalg.norm(S.conj().T @ S - QNORM * np.eye(8))),
        flat_reference_coexact_residual=float(np.linalg.norm(G.conj().T @ S)),
        primitive_constraint_action_norm=float(np.linalg.norm(G.conj().T @ K @ S)),
        Hermiticity_residual=float(np.linalg.norm(K - K.conj().T)),
        source_frame_identity_residual=abs(2 * np.pi ** 2 * R * Tb ** 2 - 1),
    )
    return dict(K_per_kappa1=K, M_geometric_scalar=m, source_inclusion=S,
                flat_reference_gradient=G, f_R=Tb / R,
                radial_index=radial_index, rho=float(saved['rho'][radial_index]),
                mechanical_lambda=lam, full_pointwise_weight=float(saved['full_pointwise_W'][radial_index]),
                checks=checks)


def reached_current(action, family):
    """Extend the actual retained mode covector in the geometric angular dual.

    S^dagger J = f_R Gamma_bar. This extension is sufficient for this component
    diagnostic. It is not a proof that the native temporal/radial current has
    no additional dual components. All 56 x 4 fermion labels are retained.
    """
    S = action['source_inclusion']
    C = action['f_R'] * family['Gamma_bar_complete'].reshape(8, -1)
    Jbasis = S @ np.linalg.solve(S.conj().T @ S, np.eye(8))
    J = Jbasis @ C
    return dict(mode_current_covector=C, dual_current_basis=Jbasis,
                reached_current_dual=J,
                duality_residual=float(np.linalg.norm(S.conj().T @ J - C)),
                connected_fermion_labels=family['Gamma_bar_complete'].shape[1:])


def _independent_columns(array, *, tolerance):
    """Rank-revealing SVD of an action image; not an operator eigenspectrum."""
    U, s, _ = np.linalg.svd(array, full_matrices=False)
    return U[:, s > tolerance]


def source_directed_component_response(action, current, *, multipliers=(1.25, 2., 4.), target=1e-12):
    """Solve the available component, enriching from its ACTUAL residual.

    Whiten the actual scalar geometric Gram. zeta_hat=zeta/kappa1 is a
    spectral parameter chosen solely above a Frobenius conditioning bound.
    The physical primitive response is u_hat/kappa1. No value of kappa1,
    ell_star, p^2, or q^2 is inserted.
    """
    K, m = action['K_per_kappa1'], action['M_geometric_scalar']
    A = K / m
    B = current['dual_current_basis'] / np.sqrt(m)
    C = current['mode_current_covector']
    size = K.shape[0]
    bound = float(np.linalg.norm(A, 'fro'))
    shifts = np.asarray(multipliers) * bound
    V = _independent_columns(B, tolerance=1e-13 * np.linalg.norm(B))
    records, stages = [], []
    for iteration in range(12):
        projected = V.conj().T @ A @ V
        Bs = V.conj().T @ B
        records = []
        for shift in shifts:
            y = V @ np.linalg.solve(projected + shift * np.eye(len(projected)), Bs)
            u = y / np.sqrt(m)
            residual = (K + shift * m * np.eye(size)) @ u - current['dual_current_basis']
            # Valid for the mathematical frozen Hermitian density; final
            # output also receives an outward Arb arithmetic certificate.
            alpha = m * (shift - bound)
            consumed_bound = np.linalg.norm(current['dual_current_basis']) * np.linalg.norm(residual) / alpha
            records.append(dict(zeta_over_kappa1=float(shift), basis_response=u,
                basis_residual=residual, current_response=u @ C,
                return_basis=current['dual_current_basis'].conj().T @ u,
                consumed_basis_error_estimate=float(consumed_bound)))
        stages.append(dict(iteration=iteration, dimension=V.shape[1],
            maximum_consumed_basis_error_estimate=max(x['consumed_basis_error_estimate'] for x in records)))
        if stages[-1]['maximum_consumed_basis_error_estimate'] <= target:
            break
        AV = A @ V
        remainder = AV - V @ (V.conj().T @ AV)
        remainder -= V @ (V.conj().T @ remainder)
        extra = _independent_columns(remainder, tolerance=2e-12 * max(1., np.linalg.norm(AV)))
        if extra.shape[1] == 0:
            raise ArithmeticError('action image closed but consumed-error target not met')
        V = np.column_stack((V, extra))
        V, _ = np.linalg.qr(V)
    else:
        raise ArithmeticError('bounded source-directed enrichment exhausted')
    # Independent solve in the complete AVAILABLE ambient angular component.
    # This does not certify native domain, temporal/radial or induced tails.
    for record in records:
        H = K + record['zeta_over_kappa1'] * m * np.eye(size)
        full = np.linalg.solve(H, current['dual_current_basis'])
        record['ambient_solve_difference_norm'] = float(np.linalg.norm(full - record['basis_response']))
        record['ambient_return_difference_norm'] = float(np.linalg.norm(
            current['dual_current_basis'].conj().T @ (full - record['basis_response'])))
        record['full_current_residuals'] = np.linalg.norm(H @ record['current_response'] - current['reached_current_dual'], axis=0)
        record['current_return'] = C.conj().T @ current['dual_current_basis'].conj().T @ record['current_response']
    return dict(records=records, stages=stages, independent_frame=V / np.sqrt(m),
                conditioning_frobenius_bound=bound, consumed_target=target)


def certify_frozen_component(action, current, record, *, precision=192):
    """Outward residual/consumed-contraction bound for exact stored matrices.

    This bound deliberately excludes source-representation, geometry,
    continuum, history, native remainder and physical-input errors.
    The exact right side is Jbasis*C; multiplication rounding is propagated.
    """
    from flint import arb, acb, acb_mat, ctx
    ctx.prec = precision
    def matrix(x):
        return acb_mat([[acb(arb(float(v.real)), arb(float(v.imag))) for v in row] for row in np.asarray(x)])
    def upper_norm(x):
        value = arb(0)
        for i in range(x.nrows()):
            for j in range(x.ncols()):
                value += abs(x[i, j]) ** 2
        return value.sqrt().upper()
    def column_norm(x, j):
        return sum((abs(x[i, j]) ** 2 for i in range(x.nrows())), arb(0)).sqrt().upper()
    def up(x):
        return float(np.nextafter(float(x.upper()), np.inf))
    K = matrix(action['K_per_kappa1'])
    m = arb(action['M_geometric_scalar'])
    shift = arb(record['zeta_over_kappa1'])
    H = K + acb_mat(np.eye(K.nrows()).tolist()) * (m * shift)
    alpha = m * shift - upper_norm(K)
    if not alpha > 0:
        raise ArithmeticError('conditioning lower bound not positive')
    Jb, C = matrix(current['dual_current_basis']), matrix(current['mode_current_covector'])
    Ub = matrix(record['basis_response'])
    U = matrix(record['current_response'])
    residual_basis = H * Ub - Jb
    delta_multiply = U - Ub * C
    rbound = upper_norm(residual_basis)
    hbound = upper_norm(H)
    source_norms, residuals, consumed_columns = [], [], []
    for j in range(C.ncols()):
        rho = rbound * column_norm(C, j) + hbound * column_norm(delta_multiply, j)
        # Bound ||(Jb*C)^dagger (u_j-u_exact,j)||, the actual
        # consumed output column, not merely the orthogonal residual.
        output_error = upper_norm(Jb) * upper_norm(C) * rho / alpha
        source_norms.append(up(column_norm(C, j)))
        residuals.append(up(rho))
        consumed_columns.append(up(output_error))
    basis_consumed = upper_norm(Jb) * rbound / alpha
    return dict(classification='CERTIFIED_FROZEN_ANGULAR_MATRIX_ARITHMETIC_ONLY',
        precision_bits=precision, coercivity_lower_arb=str(alpha),
        coercivity_lower=float(np.nextafter(float(alpha.lower()), -np.inf)),
        basis_residual_frobenius_upper=up(rbound),
        basis_consumed_return_error_upper=up(basis_consumed),
        current_residual_absolute_upper=residuals,
        consumed_current_column_error_upper=consumed_columns,
        current_coefficient_column_norm_upper=source_norms,
        current_return_frobenius_error_upper=up(sum((arb(v) ** 2 for v in consumed_columns), arb(0)).sqrt()),
        equation='||J^dagger(u_hat-u_exact)|| <= ||J|| rho / alpha; rho includes post-solve current multiplication error',
        physical_or_native_error_bound=False)


def require_native_photon_action():
    """Fail rather than promote the available angular component to the owner."""
    raise NotImplementedError(
        'The completed same-owner polarization action R_ind(v,j) on these '
        'source-reached directions is not supplied by the primitive arrays. '
        'The angular component response is not the native photon response.')
