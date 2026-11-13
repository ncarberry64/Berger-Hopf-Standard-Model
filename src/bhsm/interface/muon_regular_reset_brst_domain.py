"""FP adjoint domain induced by the owned regular same-E1 reset incidence.

This is a material-pullback evaluator, not an exterior/domain selector.
It uses the retained FP cross-Green trace pairing.  It does not choose a
gauge-fixing functional, a physical differential FP operator or its bulk
background.  Its graph is the regular interface component of that domain.
Every child operand is already evaluated at F(x).  J is the TOTAL boundary
measure ratio F* dmu_child / dmu_parent, not merely a Haar map Jacobian and
not a second copy of an already density-valued momentum.  Conormals here
are outward scalar Riesz values relative to each side's displayed measure.
The independent antighost is a field, not that cotangent momentum.

Four entries mean value, x derivative, y derivative, mixed xy derivative
for REAL parameters.  All entries, including any owned zero, are explicit.
Moving F, embedding, metric and frame contacts belong in the supplied total
pulled jets.  No temporal component, source jet or projector is inferred.
"""
from __future__ import annotations

import numpy as np


JET_ORDER = ('value', 'x', 'y', 'xy')
REGULAR_OWNER = 'covariant_bubble_interface_mechanics.build_payload.carrier_reset'
AFFINE_OWNER = 'gauge_connection_reset_bundle_lift_adjudication.induced_connection_transport'


def _jet(value, name, shape=None, real=False):
    if value is None:
        raise ValueError(f'explicit {name} jets required')
    a = np.asarray(value)
    if a.ndim < 1 or a.shape[0] != 4 or not np.isfinite(a).all():
        raise ValueError(f'{name} needs four finite entries: {JET_ORDER}')
    if shape is not None and a.shape[1:] != shape:
        raise ValueError(f'{name} jet shape mismatch')
    if real:
        if np.iscomplexobj(a) and np.any(a.imag != 0):
            raise ValueError(f'real {name} jets required')
        a = np.asarray(a.real, float)
    return a


def _mul(a, b):
    return np.stack((a[0]@b[0], a[1]@b[0]+a[0]@b[1],
        a[2]@b[0]+a[0]@b[2],
        a[3]@b[0]+a[1]@b[2]+a[2]@b[1]+a[0]@b[3]))


def _dagger(a):
    return a.conj().swapaxes(-1, -2)


def _scale(a, j):
    j = j[..., None, None]
    return np.stack((a[0]*j[0], a[1]*j[0]+a[0]*j[1],
        a[2]*j[0]+a[0]*j[2],
        a[3]*j[0]+a[1]*j[2]+a[2]*j[1]+a[0]*j[3]))


def _pair(a, b):
    return np.trace(_mul(_dagger(a), b), axis1=-2, axis2=-1)


def regular_reset_fp_domain_jets(*, bundle_jet, boundary_density_ratio_jet,
        ghost_parent_jet, ghost_child_pulled_jet,
        ghost_parent_outward_conormal_jet, ghost_child_pulled_outward_conormal_jet,
        antighost_parent_jet, antighost_child_pulled_jet,
        antighost_parent_outward_conormal_jet,
        antighost_child_pulled_outward_conormal_jet, tolerance=1e-10):
    """Construct ghost and adjoint-antighost graph rows and their full jets.

    C q = U q U^dagger at F(x), C* p = J U^dagger p(F(x)) U.
    Both independent fields use q_child=C q_parent.  Their own conormal
    balance is p_parent+C* p_child=0 (two outward normals).  A positive-time
    canonical momentum or density must first be converted explicitly.

    The exact cross-Green identity is returned even OFF the graph.  It
    proves that these antighost rows are the adjoint-domain conditions of
    the ghost rows; no arbitrary antighost sign or density is introduced.
    """
    U = _jet(bundle_jet, 'bundle')
    if U.ndim != 4 or U.shape[-1] != U.shape[-2] or U.shape[1] == 0 or U.shape[-1] == 0:
        raise ValueError('bundle jets need (4,points,fiber,fiber)')
    shape = U.shape[1:]
    J = _jet(boundary_density_ratio_jet, 'total boundary density ratio',
             shape=(shape[0],), real=True)
    if np.any(J[0] <= 0):
        raise ValueError('positive boundary measure ratio required')
    unit = _mul(_dagger(U), U)
    target = np.zeros_like(unit)
    target[0] = np.eye(shape[-1])
    if np.max(abs(unit-target)) > tolerance:
        raise ValueError('bundle value, first and mixed jets must be unitary')
    names = ('ghost_parent', 'ghost_child_pulled',
        'ghost_parent_outward_conormal', 'ghost_child_pulled_outward_conormal',
        'antighost_parent', 'antighost_child_pulled',
        'antighost_parent_outward_conormal', 'antighost_child_pulled_outward_conormal')
    values = (ghost_parent_jet, ghost_child_pulled_jet,
        ghost_parent_outward_conormal_jet, ghost_child_pulled_outward_conormal_jet,
        antighost_parent_jet, antighost_child_pulled_jet,
        antighost_parent_outward_conormal_jet,
        antighost_child_pulled_outward_conormal_jet)
    gp, gc, pp, pc, bp, bc, pbp, pbc = (
        _jet(a, name, shape) for a, name in zip(values, names))
    primal = lambda q: _mul(_mul(U, q), _dagger(U))
    adjoint = lambda p: _scale(_mul(_mul(_dagger(U), p), U), J)
    rgq, rgp = gc-primal(gp), pp+adjoint(pc)
    rbq, rbp = bc-primal(bp), pbp+adjoint(pbc)
    # Pairing is pointwise; independent reference quadrature is not silently
    # inserted.  Child physical measure is represented exactly once by J.
    green = (_pair(bp, pp)-_pair(pbp, gp)
             + _pair(bc, _scale(pc, J))-_pair(_scale(pbc, J), gc))
    factored = (_pair(bp, rgp)-_pair(rbp, gp)
                +_pair(rbq, _scale(pc, J))-_pair(_scale(pbc, J), rgq))
    return dict(jet_order=JET_ORDER,
        ghost_trace_rows=rgq, ghost_outward_conormal_rows=rgp,
        independent_antighost_trace_rows=rbq,
        independent_antighost_outward_conormal_rows=rbp,
        cross_green_form=green, cross_green_factorization=factored,
        cross_green_identity_defect=green-factored,
        measure_scope='J=F*dmu_child/dmu_parent; conormals are scalar Riesz values',
        derivative_scope='supplied total material-pulled real x,y,xy jets only',
        antighost_is_independent_field=True,
        physical_map_selected=False, physical_outgoing_domain_evaluated=False)


def regular_reset_internal_brst_intertwiner(*, bundle, bundle_spatial_derivatives,
        parent_connection, child_connection_pulled, parent_ghost,
        parent_ghost_spatial_derivatives):
    """Build Dc(Cghost c)-Cconnection(Dp c) on explicit supplied axes.

    child_connection_pulled is (DF)^T A_child(F), including ALL supplied
    axes.  No A_t=0 or time-jet convention is selected.  With three supplied
    axes this certifies only the spatial incidence.  For the owned affine
    connection law, the residual vanishes identically.  Matrix coefficients
    stand for independent Grassmann generators; their statistics are not
    replaced by commuting physical ghost amplitudes.

    This certifies covariance of the linear sA=D_A c incidence at the
    supplied U/F.  It does not derive sU/sF jets or certify the full nonlinear,
    nilpotent or spacetime-diffeomorphism BRST complex.
    """
    U, dU, Ap, Ac, c, dc = map(np.asarray, (bundle,
        bundle_spatial_derivatives, parent_connection, child_connection_pulled,
        parent_ghost, parent_ghost_spatial_derivatives))
    if U.ndim != 3 or U.shape[-1] != U.shape[-2]:
        raise ValueError('bundle needs (points,fiber,fiber)')
    if c.shape != U.shape or dU.ndim != 4 or dU.shape[0] != len(U):
        raise ValueError('ghost/bundle shape mismatch')
    if any(a.shape != dU.shape for a in (Ap, Ac, dc)):
        raise ValueError('each explicit derivative/connection axis must match')
    if dU.shape[2:] != U.shape[1:] or not all(np.isfinite(a).all()
            for a in (U,dU,Ap,Ac,c,dc)):
        raise ValueError('finite common fiber operands required')
    Ud = U.conj().swapaxes(-1,-2)
    dUd = dU.conj().swapaxes(-1,-2)
    if not np.allclose(Ud@U, np.eye(U.shape[-1]), atol=1e-10, rtol=0):
        raise ValueError('unitary bundle required')
    if not np.allclose(dUd@U[:,None]+Ud[:,None]@dU, 0, atol=1e-10, rtol=0):
        raise ValueError('bundle spatial derivatives must be unitary tangents')
    cc = U@c@Ud
    dcc = dU@c[:,None]@Ud[:,None]+U[:,None]@dc@Ud[:,None]+U[:,None]@c[:,None]@dUd
    Dcc = dcc+Ac@cc[:,None]-cc[:,None]@Ac
    Dcp = dc+Ap@c[:,None]-c[:,None]@Ap
    transported = U[:,None]@Dcp@Ud[:,None]
    incidence = Ac-(U[:,None]@Ap@Ud[:,None]-dU@Ud[:,None])
    return dict(child_ghost_pulled=cc,
        child_ghost_pulled_spatial_derivatives=dcc,
        child_covariant_ghost_derivative_pulled=Dcc,
        transported_parent_covariant_ghost_derivative=transported,
        internal_brst_intertwining_rows=Dcc-transported,
        affine_connection_incidence_rows=incidence,
        explicit_axis_count=dU.shape[1], temporal_axis_inferred=False,
        physical_map_selected=False, physical_outgoing_domain_evaluated=False)
