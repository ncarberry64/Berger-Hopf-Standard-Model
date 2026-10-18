"""Consume the evaluated operator current in the open classical wall relation.

The extra900 real coordinates describe a Hermitian finite occupation operand;
no occupation, reference or wall condition is selected. This is the known affine
component at the retained base, before the missing physical sectors are added.
"""
from __future__ import annotations
import numpy as np


def hermitian_labels(size=30):
    labels=[(0,i,i) for i in range(size)]
    for i in range(size):
        for j in range(i+1,size):
            labels.extend(((1,i,j),(2,i,j)))
    return np.asarray(labels,dtype=np.int64)


def operator_columns(operators):
    """Trace-dual columns for an orthonormal Hermitian Hilbert-Schmidt basis.

    All complex roundoff entries remain in the output. The antisymmetric basis
    has T_ij=+i/sqrt(2), T_ji=-i/sqrt(2); this fixes its trace-dual sign.
    """
    a=np.asarray(operators)
    if a.ndim!=3 or a.shape[-2:]!=(30,30) or not np.isfinite(a).all():
        raise ValueError('finite rows-by30-by30 current operators required')
    columns=[]
    for kind,i,j in hermitian_labels():
        value=a[:,i,i] if kind==0 else ((a[:,i,j]+a[:,j,i])/np.sqrt(2)
                if kind==1 else 1j*(a[:,j,i]-a[:,i,j])/np.sqrt(2))
        columns.append(value)
    return np.asarray(columns).T


def hermitian_coordinates(operand):
    """Explicit finite Hermitian matrix coordinates, without physical admission."""
    n=np.asarray(operand,complex)
    if n.shape!=(30,30) or not np.isfinite(n).all() or np.max(abs(n-n.conj().T))>1e-12:
        raise ValueError('explicit finite Hermitian30x30 operand required')
    return np.asarray([n[i,i].real if kind==0 else np.sqrt(2)*(
        n[i,j].real if kind==1 else n[i,j].imag) for kind,i,j in hermitian_labels()])


def assemble_known_open_system(classical,current):
    """Eliminate the evaluated scalar matter forcing into actual common rows.

    Unknown geometry/current/reference/exterior/native terms are additional
    operands. Setting this known contribution to zero would not close them.
    """
    W=classical['classical_wall_map'];F=classical['classical_final_map']
    E=classical['wall_temporal_endpoint']
    if W.shape!=(134,574) or F.shape!=(440,574) or E.shape!=W.shape:
        raise ValueError('original574 open classical maps required')
    C=operator_columns(current['actual_direct_plus_causal_wall134_hat'])
    terminal=np.zeros((440,900),complex)
    terminal[408:]=operator_columns(current['scalar_forced_final'])
    endpoint=operator_columns(current['wall_gauge_temporal_endpoint_hat'])
    return dict(known_wall_map=np.c_[W,C],known_final_map=np.c_[F,terminal],
        known_wall_temporal_endpoint_map=np.c_[E,endpoint],
        current_wall_columns=C,current_scalar_final_columns=terminal[408:],
        scalar_initial_current_covectors=operator_columns(current['matter_pullback574_hat'][408:440]),
        scalar_symplectic_endpoint_columns=operator_columns(current['scalar_symplectic_endpoint166_hat']),
        occupation_HS_labels=hermitian_labels())
