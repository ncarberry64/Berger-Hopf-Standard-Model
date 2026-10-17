"""Literal changing Euclidean action inverse on the reached H wall image.

The saved full480 internal action has zero gauge/H cross blocks because
its interior gauge trial has zero wall trace.  This exact represented
reduction does not apply to natural/transmission gauge wall variables.
The intrinsic H action is continued bilinearly, including its temporal
connection cross; no reflected absolute-square replacement is made.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.linalg import cholesky, solve, solve_triangular

from .muon_piecewise_euclidean_action import _basis
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def literal_proper_euclidean_forms(forms, lapse, gauss_count):
    """Continue L_E=-L_L/N with v_L=i*N*R^-1*v_E.

    A_tau,E=(-i/N)A_t,L.  The lapse is a background coefficient,
    not a varied coordinate.  Its coordinate-map derivative multiplies
    only the unused algebraic At velocity slot, whose rows are checked.
    """
    M, B, K = tuple(np.asarray(a, complex) for a in forms)
    N = complex(lapse)
    if (M.ndim != 2 or M.shape[0] != M.shape[1] or B.shape != M.shape or K.shape != M.shape
        or not np.isfinite([M, B, K]).all() or not np.isfinite(N) or N == 0
        or type(gauss_count) is not int or not 0 <= gauss_count < len(M)):
        raise ValueError('complete same-action forms, lapse and explicit Gauss count required')
    a = gauss_count
    scale = max(1., np.max(abs(M)), np.max(abs(B)))
    if a and max(np.max(abs(M[:a])), np.max(abs(M[:, :a])), np.max(abs(B[:, :a]))) > 1e-12*scale:
        raise ValueError('the temporal connection has an unaccounted velocity row')
    rotation = np.ones(len(M), complex)
    rotation[:a] = -1j/N
    inverse = 1/rotation
    congruence = inverse[:, None]*inverse[None, :]
    return dict(forms=(N*congruence*M, -1j*congruence*B, -congruence*K/N),
        coordinate_rotation=rotation, original_lapse=N,
        analytic_transpose_pairing=True, reflected_absolute_square_substituted=False)


def continued_action_polynomial(times, forms):
    """Continue the declared saved cubic action interpolation cell by cell."""
    times = np.asarray(times, float)
    arrays = tuple(np.asarray(a) for a in forms)
    if (times.ndim != 1 or len(times) < 4 or np.any(np.diff(times) <= 0)
        or any(a.shape != (len(times), 488, 488) or not np.isrealobj(a)
               or not np.isfinite(a).all() for a in arrays)):
        raise ValueError('ordered actual full488 saved action nodes required')
    polynomials = tuple(CubicSpline(times, a) for a in arrays)
    def evaluate(anchor, offset=0j):
        j = min(max(np.searchsorted(times, float(anchor), side='right')-1, 0), len(times)-2)
        z = complex(anchor)+complex(offset)-times[j]
        return tuple(sum(p.c[k, j]*z**(3-k) for k in range(4)) for p in polynomials)
    return evaluate


def internal_harmonic_indices(harmonics):
    """Full24 field fibers: At/Ar/Ai unit-Tr16 plus intrinsic realH4."""
    h = np.asarray(harmonics)
    if h.ndim != 1 or not np.issubdtype(h.dtype, np.integer) or len(set(h.tolist())) != len(h) or np.any((h < 0)|(h >= 20)):
        raise ValueError('distinct retained odd harmonic indices required')
    return (np.arange(24)[:, None]*20+h[None]).ravel()


def literal_higgs_weak_form(nodes, action_polynomial, *, temporal_cells, harmonics):
    """Integrate the original H Hessian on the executed proper-time nodes.

    All gauge/H zero blocks are tested at every complex coefficient node.
    The original full n1 field blocks and Gauss matrices remain returned,
    while their H restriction is the exact consumed current image.
    """
    n = int(temporal_cells)
    if type(temporal_cells) is not int or n < 1:
        raise ValueError('positive explicit temporal cell count required')
    idx = internal_harmonic_indices(harmonics)
    nh = len(harmonics)
    d = 4*nh
    hidx = idx[20*nh:]
    K = np.zeros((n*d, n*d), complex)
    Mgram = np.zeros_like(K)
    point_M, point_B, point_K, cross = [], [], [], []
    gauss_min = np.inf
    reflection = 0.
    for q, tau in enumerate(nodes['proper_time']):
        forms = action_polynomial(nodes['coordinate_anchor'][q], nodes['coordinate_offset'][q])
        sharp = action_polynomial(nodes['coordinate_anchor'][q], nodes['reflected_coordinate_offset'][q])
        cross_value = max(np.max(abs(a[:400, 400:480])) for a in forms)
        cross_value = max(cross_value, max(np.max(abs(a[400:480, :400])) for a in forms))
        if cross_value != 0:
            raise ValueError('the saved Dirichlet gauge/H restriction is no longer exact; retain the joint field block')
        full = tuple(a[np.ix_(idx, idx)]*MAXWELL_TO_CAP for a in forms)
        cont = literal_proper_euclidean_forms(full, nodes['N'][q], 4*nh)['forms']
        fullsharp = tuple(a[np.ix_(idx, idx)]*MAXWELL_TO_CAP for a in sharp)
        # Opposite branch reverses the Wick phases rather than reusing the
        # forward At rotation.  The action's stored real coefficients fix it.
        csharp = tuple(a.conj() for a in literal_proper_euclidean_forms(
            tuple(a.conj() for a in fullsharp), nodes['N'][q], 4*nh)['forms'])
        reflection = max(reflection, max(float(np.max(abs(a-b.conj()))) for a, b in zip(cont, csharp)))
        Mh, Bh, Kh = tuple(a[np.ix_(hidx, hidx)]*MAXWELL_TO_CAP for a in forms)
        Mh, Bh, Kh = literal_proper_euclidean_forms((Mh, Bh, Kh), nodes['N'][q], 0)['forms']
        point_M.append(cont[0]); point_B.append(cont[1]); point_K.append(cont[2]); cross.append(cross_value)
        gauss_min = min(gauss_min, float(np.linalg.svd(cont[2][:4*nh, :4*nh], compute_uv=False)[-1]))
        basis = _basis(tau, nodes['total_proper_clock'], n)
        w = float(nodes['weight'][q])
        for j, pj, dj in basis:
            sj = slice(j*d, (j+1)*d)
            for k, pk, dk in basis:
                sk = slice(k*d, (k+1)*d)
                K[sj, sk] += w*(dj*dk*Mh+pj*dk*Bh+dj*pk*Bh.T+pj*pk*Kh)
                Mgram[sj, sk] += w*pj*pk*Mh
    G = (Mgram+Mgram.conj().T)/2
    C = cholesky(G, lower=True)
    P = solve_triangular(C, K, lower=True)
    P = solve_triangular(C, P.conj().T, lower=True).conj().T
    Hpart = (P+P.conj().T)/2
    eig = np.linalg.eigvalsh(Hpart)
    inverse = solve(K, np.eye(len(K)), assume_a='gen')
    return dict(Higgs_original_action_Hessian=K, Higgs_analytic_kinetic_Gram=Mgram,
        kinetic_Gram_Hermitian_part=G, normalized_action=P,
        normalized_Hermitian_part_eigenvalues=eig, original_action_Green=inverse,
        original_action_inverse_residual_max=float(np.max(abs(K@inverse-np.eye(len(K))))),
        operator_Hermiticity_defect=float(np.linalg.norm(P-P.conj().T)/np.linalg.norm(P)),
        complete_point_M=np.array(point_M), complete_point_B=np.array(point_B), complete_point_K=np.array(point_K),
        original_Gauss_smallest_singular_value_min=gauss_min, independent_branch_reflection_max=reflection,
        gauge_H_cross_max=np.array(cross), harmonics=np.asarray(harmonics, int), temporal_cells=n,
        numerical_initial_trace_zero=True, final_natural_action_cotangent_kept=True,
        Dirichlet_interior_gauge_current_zero_only_on_this_represented_image=True,
        positive_ADM_or_reflected_absolute_square_substituted=False,
        physical_P_strat_or_complete_native_domain_identified=False)


def intrinsic_higgs_open_current_application(nodes, fermion_coefficients,
        fermion_weak_form, Higgs_form, scalar_vertices, *, temporal_cells):
    """Gaussian -V (A_E†A_E)^-1 A_E† V K_H^-1 with literal current.

    This is the c=0 open Gaussian restriction of the executed action.  It
    is not a finite-c P_cycle statistical assignment or an on-shell F2.
    Both original finite action inverses are used, rather than identifying
    the continued Higgs operator with a positive reference square.
    """
    V = np.asarray(scalar_vertices, complex)
    if V.shape != (4, 6, 6) or not np.isfinite(V).all():
        raise ValueError('all four fixed-Y canonical realified Higgs vertices required')
    n = int(temporal_cells)
    nh = len(Higgs_form['harmonics'])
    df, dh = 6*nh, 4*nh
    if fermion_coefficients['forward'].shape[1:] != (df, df):
        raise ValueError('the same full fermion angular image is required')
    R = np.zeros((df, 6, dh), complex)
    L = np.zeros((6, df, dh), complex)
    for h in range(nh):
        for c in range(4):
            R[np.arange(6)*nh+h, :, c*nh+h] = V[c]
            L[:, np.arange(6)*nh+h, c*nh+h] = V[c]
    numerator = np.zeros((n*df, 6, n*dh), complex)
    left = np.zeros((6, n*df, n*dh), complex)
    for q, tau in enumerate(nodes['proper_time']):
        basis = _basis(tau, nodes['total_proper_clock'], n)
        w = float(nodes['weight'][q])
        for j, pj, dj in basis:
            sf = slice(j*df, (j+1)*df)
            dual = dj*np.eye(df)+pj*fermion_coefficients['reflected'][q]
            for k, pk, _ in basis:
                sh = slice(k*dh, (k+1)*dh)
                numerator[sf, :, sh] += w*pk*np.einsum('ab,bih->aih', dual, R)
                left[:, sf, sh] += w*pj*pk*L
    KF = fermion_weak_form['K']
    response = solve(KF, numerator.reshape(n*df, -1), assume_a='gen').reshape(n*df, 6, n*dh)
    GH = Higgs_form['original_action_Green']
    value = -np.einsum('ofh,fik,hk->oi', left, response, GH, optimize=True)
    return dict(open_Gaussian_current=value, literal_left_current=left, actual_A_sharp_source_numerator=numerator,
        fermion_source_response=response,
        original_fermion_source_rows_max=float(np.max(abs(np.einsum('fg,gih->fih', KF, response)-numerator))),
        scalar_Gaussian_sign=-1, field_current_angular_normalization='phi_h=Y_h/sqrt(V), phi0=1/sqrt(V), unnormalized dOmega; no second V in the vertex',
        external_test='all six canonical constant external coefficient tests; no external pole or selected state',
        common_native_cutoff=None, finite_c_mixed_P_cycle_assignment_completed=False,
        native_Pauli_or_physical_a_mu=None)
