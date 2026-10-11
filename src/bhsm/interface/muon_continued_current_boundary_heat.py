"""Regulated current/domain contacts on the continued canonical finite graph.

The temporal variable Gram belongs to the same piecewise-linear coefficient
space as the midpoint first-order action.  Its generalized squared operator
is P=M^-1/2 A† G A M^-1/2.  This finite Riesz construction preserves the
initial-zero/free-final domain; it does not prove a real-Euclidean contour
deformation or identify this component with the complete stratified loop.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh, lu_factor, lu_solve
from .muon_continued_current_factor import _first_order_matrix


def temporal_variable_gram(weights, dimension):
    """Exact linear nodal L2 Gram with initial coordinate fixed to zero.

The supplied positive weights are the actual proper-clock cell quadrature.
The initial node is removed and the final node remains free.  Residual-test
Gram G=diag(weights) is distinct from this variable Gram M.
"""
    w = np.asarray(weights, float)
    if w.ndim != 1 or not np.isfinite(w).all() or np.any(w <= 0):
        raise ValueError('positive actual proper-clock cell weights required')
    d = w/3
    d[:-1] += w[1:]/3
    temporal = np.diag(d)
    temporal += np.diag(w[1:]/6, 1)+np.diag(w[1:]/6, -1)
    return np.kron(temporal, np.eye(dimension))


def spectral_action_factor(A, weights, dimension):
    """Form the canonical generalized square before any regulator action."""
    A = np.asarray(A, complex)
    G = np.repeat(np.asarray(weights, float), dimension)
    if A.shape != (len(G), len(G)) or not np.isfinite(A).all():
        raise ValueError('finite square first-order action on this domain required')
    M = temporal_variable_gram(weights, dimension)
    K = A.conj().T@(G[:, None]*A)
    eigen_M, V = eigh(M)
    X = (V/np.sqrt(eigen_M))@V.T
    P = X@K@X
    eigen_P, U = eigh((P+P.conj().T)/2)
    if eigen_P[0] <= 0:
        raise ValueError('positive finite square required; no numerical shift permitted')
    # XU is an M-orthonormal coefficient basis, not an invented D=sqrt(P).
    C = X@U
    return dict(A=A, G=G, M=M, K=K, P=P, eigenvalues=eigen_P,
                eigenvectors=C, hermitian_rounding_max=float(np.max(abs(P-P.conj().T))),
                variable_Gram_identity_max=float(np.max(abs(C.conj().T@M@C-np.eye(len(C))))))


def regulated_inverse_action(factor, rhs, c):
    """Apply e^(-cP)/P to a coefficient dual on the SAME free-final graph."""
    c = float(c)
    if not np.isfinite(c) or c < 0:
        raise ValueError('nonnegative declared cutoff coordinate required')
    C, lam = factor['eigenvectors'], factor['eigenvalues']
    return C@((np.exp(-c*lam)/lam)[:, None]*(C.conj().T@rhs))


def _solve_action(factor, rhs):
    if '_action_lu' not in factor:
        factor['_action_lu'] = lu_factor(factor['A'])
    return lu_solve(factor['_action_lu'], rhs)


def spectral_divided_g(target, source, c):
    """Stable first divided difference of g_c(x)=exp(-cx)/x."""
    a, b = np.asarray(target)[:, None], np.asarray(source)[None, :]
    gap = a-b
    mid = (a+b)/2
    close = abs(gap) <= 2e-7*mid
    # Exact inverse divided difference plus the exp remainder suppresses
    # cancellation when c is small; the close branch has O(gap^2) error.
    ga = np.expm1(-c*a)/a
    gb = np.expm1(-c*b)/b
    remainder = np.divide(ga-gb, gap, out=np.zeros_like(gap), where=~close)
    derivative = (1-np.exp(-c*mid)*(1+c*mid))/mid**2
    remainder[close] = derivative[close]
    return -1/(a*b)+remainder


def magnetic_regulated_action(source_factor, target_factor, R, delta_forward,
                              delta_reverse, *, c, delta_source=None):
    """Full rectangular square-plus-numerator contact, not inverse-only motion.

For block-diagonal A and independent directed insertions dA_10,dA_01,
dK_10=dA_01†G0 A0+A1†G1 dA_10.  The source dual motion is
d(A†GR)_1=dA_01†G0R0+A1†G1 dR1.  This fixed-geometry magnetic direction
has dM=0; a moving geometry/Gram direction is a separate application.
"""
    s, t = source_factor, target_factor
    f, r = np.asarray(delta_forward, complex), np.asarray(delta_reverse, complex)
    R = np.asarray(R, complex)
    dR = np.zeros((len(t['A']), R.shape[1]), complex) if delta_source is None else np.asarray(delta_source, complex)
    if f.shape != (len(t['A']), len(s['A'])) or r.shape != (len(s['A']), len(t['A'])):
        raise ValueError('both directed first-order magnetic images required')
    B = s['A'].conj().T@(s['G'][:, None]*R)
    dB = r.conj().T@(s['G'][:, None]*R)+t['A'].conj().T@(t['G'][:, None]*dR)
    dK = r.conj().T@(s['G'][:, None]*s['A'])+t['A'].conj().T@(t['G'][:, None]*f)
    C0, C1 = s['eigenvectors'], t['eigenvectors']
    numer = regulated_inverse_action(t, dB, c)
    square = C1@((spectral_divided_g(t['eigenvalues'], s['eigenvalues'], c)
        *(C1.conj().T@dK@C0))@(C0.conj().T@B))
    direct = _solve_action(t, dR-f@_solve_action(s, R))
    return dict(response=square+numer, square_contact=square, numerator_contact=numer,
                c0_direct_inverse_derivative=direct, delta_squared_form=dK,
                delta_source_dual=dB, fixed_geometry_variable_Gram_derivative_zero=True)


def _interior_factor(full, dimension):
    """Restrict K AND M; a second final Dirichlet trace is a reference only."""
    cache_key = '_interior_'+str(dimension)
    if cache_key in full:
        return full[cache_key]
    K, M = full['K'][:-dimension, :-dimension], full['M'][:-dimension, :-dimension]
    ev, V = eigh(M)
    X = (V/np.sqrt(ev))@V.T
    P = X@K@X
    lam, U = eigh((P+P.conj().T)/2)
    full[cache_key] = dict(K=K, M=M, eigenvalues=lam, eigenvectors=X@U)
    return full[cache_key]


def boundary_regulated_current(factor, R, target, *, c, dimension):
    """Subtract the additional final-Dirichlet reference after regulation.

The finite-c return is the full spectral difference, not a heat function of
S(0).  Its resolvent is the frequency-dependent Schur of K-zM, including
the off-diagonal variable-Gram terms.
"""
    B = factor['A'].conj().T@(factor['G'][:, None]*R)
    full = regulated_inverse_action(factor, B, c)
    interior = _interior_factor(factor, dimension)
    dirichlet = regulated_inverse_action(interior, B[:-dimension], c)
    padded = np.r_[dirichlet, np.zeros((dimension, R.shape[1]), complex)]
    returned = full-padded
    return dict(full_response=full, Dirichlet_reference_response=padded,
                boundary_return_response=returned, current_full=target@full,
                current_Dirichlet_reference=target@padded, current_boundary_return=target@returned)


def magnetic_boundary_return(source_factor, target_factor, R, delta_forward,
                             delta_reverse, *, c, source_dimension, target_dimension):
    """Apply the same directed source contact to both squared domains."""
    full = magnetic_regulated_action(source_factor, target_factor, R,
                                    delta_forward, delta_reverse, c=c)
    s = _interior_factor(source_factor, source_dimension)
    t = _interior_factor(target_factor, target_dimension)
    B = (source_factor['A'].conj().T@(source_factor['G'][:,None]*R))[:-source_dimension]
    dB = full['delta_source_dual'][:-target_dimension]
    dK = full['delta_squared_form'][:-target_dimension, :-source_dimension]
    C0, C1 = s['eigenvectors'], t['eigenvectors']
    numer = regulated_inverse_action(t, dB, c)
    square = C1@((spectral_divided_g(t['eigenvalues'], s['eigenvalues'], c)
        *(C1.conj().T@dK@C0))@(C0.conj().T@B))
    reference = np.r_[square+numer, np.zeros((target_dimension,R.shape[1]),complex)]
    return dict(**full, Dirichlet_reference_response=reference,
                boundary_return_response=full['response']-reference)


def boundary_resolvent_schur(factor, z, *, dimension):
    """Action-owned spectral Schur, retaining canonical measure contacts."""
    pencil = factor['K']-complex(z)*factor['M']
    II, IB, BI, BB = (pencil[:-dimension, :-dimension], pencil[:-dimension, -dimension:],
                     pencil[-dimension:, :-dimension], pencil[-dimension:, -dimension:])
    return BB-BI@np.linalg.solve(II, IB)


def rectangular_midpoint_matrix(values):
    v = np.asarray(values, complex)
    diagonal = v/2
    n, nt, ns = v.shape
    out = np.zeros((n*nt, n*ns), complex)
    for j in range(n):
        out[j*nt:(j+1)*nt, j*ns:(j+1)*ns] = diagonal[j]
        if j:
            out[j*nt:(j+1)*nt, (j-1)*ns:j*ns] = diagonal[j]
    return out


def joined_magnetic_heat_inputs(incoming, outgoing, *, Y=0.):
    """Bind the frozen common-frame chronological nodes and both Xi images.

The source axes are the retained first three electromagnetic directions.
The n1 intermediate is the full four-dimensional n1 body representation.
This exact fixed common-frame restriction has T=I and no dT contact; it
does not select the full physical worldvolume transport.
"""
    p, c = incoming, outgoing
    for key in ('alpha6', 'n1_right_body_derivatives', 'family_Y', 'family_indices'):
        if not np.array_equal(p[key], c[key]):
            raise ValueError('identical canonical angular/family representation required')
    data = {k:np.concatenate((p[k], c[k])) for k in (
        'A0_diagonal', 'A0_lower', 'A1_diagonal', 'A1_lower', 'proper_cell_weights',
        'common_Hcan0', 'common_Hcan1', 'R4', 'source_right_map', 'target_left_map',
        'magnetic_right_Y0', 'magnetic_right_Y1', 'magnetic_left_Y0', 'magnetic_left_Y1')}
    A0 = _first_order_matrix(data['A0_diagonal']+Y*data['A1_diagonal'],
                             data['A0_lower']+Y*data['A1_lower']).toarray()
    alpha, E = p['alpha6'], p['n1_right_body_derivatives']
    H = np.array([np.kron(h0+Y*h1, np.eye(4))
        -1j*sum(np.kron(a,e) for a,e in zip(alpha,E))/r
        for h0,h1,r in zip(data['common_Hcan0'],data['common_Hcan1'],data['R4'])])
    weights = data['proper_cell_weights']
    diag = -1j*np.eye(24)[None]/weights[:,None,None]+H/2
    lower = 1j*np.eye(24)[None]/weights[:,None,None]+H/2
    A1 = _first_order_matrix(diag, lower).toarray()
    weighted = weights[:,None,None]*data['target_left_map']/2
    weighted[:-1] += weights[1:,None,None]*data['target_left_map'][1:]/2
    target = weighted.transpose(1,0,2).reshape(6,-1)
    return dict(source_A=A0, target_A=A1, weights=weights,
        source_R=data['source_right_map'].reshape(-1,6), literal_current_target=target,
        magnetic_forward=np.array([rectangular_midpoint_matrix(
            data['magnetic_right_Y0'][:,a]+Y*data['magnetic_right_Y1'][:,a]) for a in range(3)]),
        magnetic_reverse=np.array([rectangular_midpoint_matrix(
            data['magnetic_left_Y0'][:,a]+Y*data['magnetic_left_Y1'][:,a]) for a in range(3)]),
        actual_family_Y=float(Y), common_birth_frame_is_I=True,
        canonical_Xi_is_delta_Hcan=True, temporal_At_placement='-i G/N')
