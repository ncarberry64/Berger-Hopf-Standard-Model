"""Structural external-test compression retaining the full neutral return.

The right covariant tests contain Omega J as well as J. Thus a charged
four-dimensional injection is insufficient for the full FW covector on
the actual interacting background. I6, or I6 tensor the three inherited
coordinate columns, supplies a complete analytic basis without SVD.
"""
from __future__ import annotations
import numpy as np

from .muon_changing_normal_current_readout import _finite
from .muon_intrinsic_covariant_open_current_jet import normal_coordinate_first_momentum_lift


def compress_normal_current_maps(maps, *, radius):
    """Reduce explicit dyads to 6 constant or 18 coordinate right tests.

    Every right coordinate test lies in C6 tensor span{X1,X2,X3}; all
    spin/gauge connection multiplication remains in C6. The coefficient
    Gram solve changes the representation of the same linear covector,
    rather than selecting an external state or dropping a neutral mode.
    Binary reconstruction residuals are returned, not called enclosures.
    """
    r = float(_finite(radius, 'actual normal radius', (), real=True))
    if r <= 0:
        raise ValueError('positive actual radius required')
    J = _finite(maps.get('charged_injection'), 'same full C6 charged injection', (6, 4))
    Q = normal_coordinate_first_momentum_lift(r)['scalar_coordinate_coefficients']
    complete = {'C': np.eye(6), 'T': np.kron(np.eye(6), Q.T)}
    restricted = {'C': J.T, 'T': np.kron(J.T, Q.T)}
    answer = dict(complete_constant_right_dimension=6,
        complete_coordinate_right_dimension=18,
        structural_right_space='C6 for constant; C6 tensor span{X1,X2,X3} for coordinate',
        neutral_complement_removed=False, SVD_or_numerical_rank_selection_used=False,
        charged_only_basis_sufficient_for_full_covariant_readout=False,
        reconstruction_error_enclosed=False)
    names = ('right_mass_C', 'right_FW_C', 'Weyl_mass_C',
        'Weyl_mass_T', 'Weyl_FW_C', 'Weyl_FW_T')
    for name in names:
        if name not in maps or len(maps[name]) != 3:
            raise ValueError('all three actual spin covectors are required')
        R = complete[name[-1]]
        Gram = R @ R.conj().T
        charged = restricted[name[-1]]
        cg = charged @ charged.conj().T
        rows = []
        for bundle in maps[name]:
            W = _finite(bundle.get('tensor_weight'), 'complete literal covector weight')
            if W.ndim != 2 or W.shape[1] != R.shape[1]:
                raise ValueError('same spin-major external input ordering required')
            L = np.linalg.solve(Gram.T, (W @ R.conj().T).T).T
            residual = W - L @ R
            cl = np.linalg.solve(cg.T, (W @ charged.conj().T).T).T
            ce = W - cl @ charged
            rows.append(dict(coefficients=np.ones(len(R)),
                left_tests=L.T, right_tests=R.copy(), tensor_weight=W.copy(),
                right_test_Gram=Gram.copy(),
                reconstruction_residual=residual,
                reconstruction_residual_norm=float(np.linalg.norm(residual)),
                charged_only_projection_residual=ce,
                charged_only_projection_residual_norm=float(np.linalg.norm(ce)),
                charged_only_projection_relative_residual=float(np.linalg.norm(ce)/np.linalg.norm(W))
                    if np.linalg.norm(W) else 0.,
                adjoint_of_literal_left_imposed=False))
        answer[name] = rows
    return answer
