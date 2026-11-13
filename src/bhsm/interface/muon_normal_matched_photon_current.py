"""Full angular current image of the evaluated normal-matched C covectors.

The current is restricted before the original coupled field inverse.  This
keeps its n4 fermion image even when a particular constant-right magnetic
bridge has an exactly vanishing n4 source.  The covectors are the evaluated
same-current matching tests; this module does not assign an LSZ residue.
"""
from __future__ import annotations

from functools import lru_cache
import numpy as np
from scipy.linalg import solve


@lru_cache(maxsize=1)
def complete_normal_current_gaunt():
    """n1 field times n1+n3 external has the complete even0/2/4 image."""
    from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
    a = scalar_s3_discretization(4)
    labels = a['real_basis_labels']
    field = np.array([j for j, x in enumerate(labels) if x[0] == 1])
    external = np.array([j for j, x in enumerate(labels) if x[0] in (1, 3)])
    internal = np.array([j for j, x in enumerate(labels) if x[0] in (0, 2, 4)])
    y = a['real_basis_values']
    g = np.einsum('qi,qh,qx,q->ihx', y[:, internal], y[:, field],
                  y[:, external], a['haar_weights'], optimize=True)
    ni = np.array([labels[j][0] for j in internal])
    nx = np.array([labels[j][0] for j in external])
    allowed = ((abs(ni[:, None]-nx[None, :]) <= 1)
               & (ni[:, None]+nx[None, :] >= 1)
               & ((ni[:, None]+nx[None, :]+1) % 2 == 0))
    forbidden = np.max(abs(g * (~allowed)[:, None, :]))
    if forbidden > 2e-12:
        raise ArithmeticError('real Gaunt degree/parity identity was not resolved')
    g *= allowed[:, None, :]
    return dict(gaunt=g, internal_degrees=ni, external_degrees=nx,
                internal_labels=tuple(labels[j] for j in internal),
                external_labels=tuple(labels[j] for j in external),
                field_labels=tuple(labels[j] for j in field),
                forbidden_gaunt_quadrature_max=float(forbidden))


def normal_matched_left_current_moments(nodes, trace_map, H_coordinates, *,
                                       temporal_cells, family):
    """Literal left current in FE x even0/2/4, before C and field inverse.

    The field coordinate is the original proper-Euclidean At coordinate;
    the retained action map applies At_L=i*N*At_E once.  Scalar driving
    current rows are excluded by the electromagnetic charge restriction,
    while every coupled Higgs response column remains in the field inverse.
    """
    from .muon_piecewise_euclidean_action import _basis
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    from .muon_literal_euclidean_wall_action import natural_wall_current_maps
    from .muon_changing_magnetic_momentum_columns import generalized_vertex_sources
    from .muon_source_directed_em_normal_current import neutral_wall_trace_map

    p = np.asarray(trace_map, complex)
    h = np.asarray(H_coordinates, complex)
    n = temporal_cells
    if (type(n) is not int or n < 1 or family not in (1, 2)
            or p.ndim != 2 or p.shape[0] != 96
            or h.shape != (len(nodes['weight']), 4)):
        raise ValueError('same original n1 wall map, H chart and temporal representation required')
    angular = complete_normal_current_gaunt()
    g = angular['gaunt']
    nb = p.shape[1]
    left = np.zeros((120, n*210, n*nb), complex)
    for iq, t in enumerate(nodes['proper_time']):
        selected = neutral_wall_trace_map(p, h[iq])['wall_trace_map']
        v = euclidean_open_action_vertices(nodes['R'][iq], nodes['N'][iq],
                                          family=family)['vertices']
        maps = natural_wall_current_maps(v, selected, nodes['N'][iq], 4)
        field = maps['Lorentz_field_image'].reshape(24, 4, nb)
        _, ell = generalized_vertex_sources(field, v, np.eye(35), g)
        if ell.shape != (120, 210, nb):
            raise ArithmeticError('complete spin-major current image was not retained')
        for j, pj, _ in _basis(t, nodes['total_proper_clock'], n):
            si = slice(j*210, (j+1)*210)
            for k, pk, _ in _basis(t, nodes['total_proper_clock'], n):
                sb = slice(k*nb, (k+1)*nb)
                left[:, si, sb] += float(nodes['weight'][iq])*pj*pk*ell
    return dict(literal_left_current=left, **angular,
                temporal_cells=n, internal_spin_count=6,
                electromagnetic_source_only=True, induced_H_response_retained=True,
                electric_charge_reinserted=False, physical_LSZ_assigned=False)


def normal_matched_field_adjoint(field, left_current, left_tests):
    """Apply the evaluated C tests BEFORE the original transpose saddle.

    p columns are (literal external dyad6, internal FE x even0/2/4).
    No Hilbert conjugation is made on the analytic left current or tests.
    """
    k = np.asarray(field['original_Hessian'], complex)
    c = np.asarray(field['frame_rows'], complex)
    left = np.asarray(left_current, complex)
    tests = np.asarray(left_tests, complex)
    nb = len(k)
    if (k.shape != (nb, nb) or c.ndim != 2 or c.shape[1] != nb
            or left.shape != (120, 420, nb)
            or tests.shape != (3, 6, 120)):
        raise ValueError('complete natural-wall action and three evaluated C tests required')
    soft = np.einsum('ado,ofb->adfb', tests, left, optimize=True)
    sources = soft.transpose(0, 3, 1, 2).reshape(3, nb, -1)
    return normal_matched_source_adjoint(field, sources)


def normal_matched_adjoint_sources(nodes, trace_map, H_coordinates, left_tests, *,
                                  temporal_cells, family):
    """Integrate C times the literal current without a large unused tensor.

    This is the same contraction as ``left_tests @ left_current`` before
    the inverse.  It does not compress the 35-harmonic internal image.
    """
    from .muon_piecewise_euclidean_action import _basis
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    from .muon_literal_euclidean_wall_action import natural_wall_current_maps
    from .muon_source_directed_em_normal_current import neutral_wall_trace_map

    p, h, tests = (np.asarray(x, complex) for x in (trace_map, H_coordinates, left_tests))
    n = temporal_cells
    if (type(n) is not int or n != 2 or family not in (1, 2)
            or p.ndim != 2 or p.shape[0] != 96
            or h.shape != (len(nodes['weight']), 4) or tests.shape != (3, 6, 120)):
        raise ValueError('complete actual wall, H chart and evaluated C tests required')
    g = complete_normal_current_gaunt()['gaunt']
    nb = p.shape[1]
    result = np.zeros((3, n*nb, 6, n*210), complex)
    c = tests.reshape(3, 6, 6, 20)
    for iq, t in enumerate(nodes['proper_time']):
        selected = neutral_wall_trace_map(p, h[iq])['wall_trace_map']
        v = euclidean_open_action_vertices(nodes['R'][iq], nodes['N'][iq], family=family)['vertices']
        maps = natural_wall_current_maps(v, selected, nodes['N'][iq], 4)
        current = np.einsum('adox,foj,ihx->adjifh', c, v, g, optimize=True)
        soft = (current.reshape(3*6*210, 96) @ maps['Lorentz_field_image']).reshape(3, 6, 210, nb)
        for j, pj, _ in _basis(t, nodes['total_proper_clock'], n):
            si = slice(j*210, (j+1)*210)
            for k, pk, _ in _basis(t, nodes['total_proper_clock'], n):
                sb = slice(k*nb, (k+1)*nb)
                result[:, sb, :, si] += float(nodes['weight'][iq])*pj*pk*soft.transpose(0, 3, 1, 2)
    return result.reshape(3, n*nb, 6*n*210)


def normal_matched_source_adjoint(field, sources):
    """Solve the original transpose action with already integrated C sources."""
    k = np.asarray(field['original_Hessian'], complex)
    c = np.asarray(field['frame_rows'], complex)
    sources = np.asarray(sources, complex)
    nb = len(k)
    if (k.shape != (nb, nb) or c.ndim != 2 or c.shape[1] != nb
            or sources.shape != (3, nb, 2520)):
        raise ValueError('the complete original action and full C source image required')
    saddle = np.block([[k, c.T], [c, np.zeros((len(c), len(c)), complex)]])
    rhs = np.concatenate((sources, np.zeros((3, len(c), sources.shape[2]), complex)), axis=1)
    solved = solve(saddle.T, rhs.transpose(1, 0, 2).reshape(len(saddle), -1),
                   assume_a='gen').reshape(len(saddle), 3, -1).transpose(1, 0, 2)
    p, reaction = solved[:, :nb], solved[:, nb:]
    residual = np.einsum('ij,ajk->aik', k.T, p)+np.einsum('ij,ajk->aik', c.T, reaction)-sources
    frames = np.einsum('ij,ajk->aik', c, p)
    return dict(field_adjoint=p, frame_reactions=reaction,
                literal_adjoint_source=sources,
                original_adjoint_residual=residual, frame_residual=frames,
                p_column_order=('literal dyad6', 'FE2 x spin6 x even0/2/4'),
                transpose_dual_not_Hilbert_dagger=True, physical_LSZ_assigned=False)


def constant_right_bridge_embedding(bridge, *, temporal_cells=2):
    """Keep the full p image; prove the n4 bridge source is exactly zero.

    The current right fermion is n1 and its source field is n1.  Each
    angular derivative preserves degree, hence both unsquared placements
    and the source numerator have only even0/2 images.  This assertion
    applies to this constant-right path, not a momentum-right n1 source.
    """
    b = np.asarray(bridge, complex)
    n = temporal_cells
    if type(n) is not int or n < 1 or b.shape != (3, n*60, n*24):
        raise ValueError('the actual constant-right magnetic bridge is required')
    g = complete_normal_current_gaunt()
    ext1 = np.flatnonzero(g['external_degrees'] == 1)
    rows4 = np.flatnonzero(g['internal_degrees'] == 4)
    if np.any(g['gaunt'][rows4][:, :, ext1] != 0):
        raise ArithmeticError('n1 x n1 unexpectedly reaches n4')
    rows02 = np.flatnonzero(g['internal_degrees'] <= 2)
    idx = np.array([j*210+s*35+i for j in range(n) for s in range(6) for i in rows02])
    complete = np.zeros((3, n*210, n*24), complex)
    complete[:, idx] = b
    return dict(original_current_magnetic_internal_bridge=complete,
                retained_even02_indices=idx, n4_source_exact_zero=True,
                current_right_shell=1, magnetic_source_shell=1,
                p_source_n4_removed=False, complete_starting_loop_claimed=False)
