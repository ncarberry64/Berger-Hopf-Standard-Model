"""Consume saved D5 responses without selecting their physical boundary data.

All homogeneous coordinates and their source variations are supplied explicitly.
The source direction of a saved response remains the declared Xi direction;
neither a physical constrained tangent nor a continuum error bound follows
from a finite response application.
"""
from __future__ import annotations

import numpy as np

from .muon_d5_temporal_bulk_refinement import apply_refined_fundamental
from .muon_d5_independent_residuals import (
    independent_residual_application, original_d5_coefficient_callback,
)


def _finite(value, shape, name):
    a = np.asarray(value, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError(name + ' must have the complete finite declared shape')
    return a


def tied_normal_amplitudes(g, g_source, *, right_plus, right_minus,
        left_plus, left_minus, right_plus_source, right_minus_source,
        left_plus_source, left_minus_source, left_projector, right_projector):
    """Apply the common-g collar identities with independent profile germs.

    The four profile values are not normalization integrals. Their source
    variations include whatever mode/normalization variations the caller has
    actually determined; no missing profile germ defaults to zero here.
    """
    g = np.asarray(g, complex)
    if g.ndim != 3 or g.shape[1] != 18 or not min(g.shape) or not np.isfinite(g).all():
        raise ValueError('shared g must be amplitude-time by localized18 by application-column')
    gx = _finite(g_source, g.shape, 'shared g source')
    pl = _finite(left_projector, (18, 18), 'original localized left projector')
    pr = _finite(right_projector, (18, 18), 'original localized right projector')
    if max(np.max(abs(pl+pr-np.eye(18))), np.max(abs(pl@pl-pl)),
            np.max(abs(pr@pr-pr)), np.max(abs(pl@pr)), np.max(abs(pr@pl))) > 1e-13:
        raise ValueError('complementary original localized chiral projectors required')
    profiles = {}
    for name, value in (('right_plus', right_plus), ('right_minus', right_minus),
            ('left_plus', left_plus), ('left_minus', left_minus),
            ('right_plus_source', right_plus_source), ('right_minus_source', right_minus_source),
            ('left_plus_source', left_plus_source), ('left_minus_source', left_minus_source)):
        profiles[name] = _finite(value, (len(g),), name)[:, None, None]
    if np.any(profiles['left_plus'] == 0) or np.any(profiles['left_minus'] == 0):
        raise ValueError('the declared LR/RL quotient requires nonzero left profile values')
    lg = np.einsum('ij,tjk->tik', pl, g)
    rg = np.einsum('ij,tjk->tik', pr, g)
    lgx = np.einsum('ij,tjk->tik', pl, gx)
    rgx = np.einsum('ij,tjk->tik', pr, gx)
    rp, rm, lp, lm = (profiles[k] for k in ('right_plus','right_minus','left_plus','left_minus'))
    rpx, rmx, lpx, lmx = (profiles[k+'_source'] for k in ('right_plus','right_minus','left_plus','left_minus'))
    value = dict(a_R=rp*lg+rm*rg, a_LR=g/lp, a_RL=g/lm)
    source = dict(a_R=rpx*lg+rp*lgx+rmx*rg+rm*rgx,
        a_LR=gx/lp-g*lpx/lp**2, a_RL=gx/lm-g*lmx/lm**2)
    return value, source


def assemble_wall_combination(arrays, side, amplitudes, amplitude_sources, *,
        homogeneous, homogeneous_source):
    """P a + Q h and its full Xi product derivative, using all366 h slots.

    The same h must be supplied to the two collar calls when those calls
    represent the common same-history solution. This routine neither solves
    nor chooses h, g, their derivatives, or any normal profile.
    """
    if side not in ('plus','minus'):
        raise ValueError('same-history plus/minus eta collar required')
    n = len(arrays['times'])
    na = len(arrays['amplitude_times'])
    h = np.asarray(homogeneous, complex)
    if h.ndim != 3 or h.shape[:2] != (n,366) or not h.shape[-1] or not np.isfinite(h).all():
        raise ValueError('all366 homogeneous coordinates at every refined node required')
    hx = _finite(homogeneous_source, h.shape, 'all homogeneous source coordinates')
    k = h.shape[-1]
    values = {}
    sources = {}
    for slot in ('a_R','a_LR','a_RL'):
        values[slot] = _finite(amplitudes[slot], (na,18,k), slot).reshape(na*18,k)
        sources[slot] = _finite(amplitude_sources[slot], (na,18,k), slot+' source').reshape(na*18,k)
    q = _finite(arrays['wall_'+side+'_complement_basis'], (n,384,366), 'saved full homogeneous wall basis')
    qx = _finite(arrays['wall_'+side+'_complement_basis_source'], q.shape, 'saved homogeneous basis source')
    wall_h = q@h
    wall_hx = qx@h+q@hx
    wall_p = np.zeros((n,384,k),complex)
    wall_px = np.zeros_like(wall_p)
    terms = [(side+'_seed','a_R')]
    if side == 'minus':
        terms += [('minus_LR','a_LR'),('minus_RL','a_RL')]
    for label, slot in terms:
        p = _finite(arrays[label+'_wall'], (n,384,18*na), label+' saved wall map')
        px = _finite(arrays[label+'_wall_source'], p.shape, label+' saved wall source')
        wall_p += p@values[slot]
        wall_px += px@values[slot]+p@sources[slot]
    return dict(wall=wall_p+wall_h, wall_source=wall_px+wall_hx,
        particular_wall=wall_p, particular_wall_source=wall_px,
        homogeneous_wall=wall_h, homogeneous_wall_source=wall_hx,
        homogeneous_coordinate_shape=h.shape, homogeneous_coordinates_selected=False,
        physical_outer_conditions_solved=False, physical_admission=False)


def reconstruct_combination(arrays, side, wall, wall_source, *, times, radii):
    """Apply the completed factors; perform no new ODE or boundary selection."""
    return apply_refined_fundamental(arrays, side, wall, wall_source,
        times=times, radii=radii)


def independent_combination_checks(arrays, side, wall, wall_source, points, *, history):
    """Check the actual reconstructed combination with original coefficients.

    The returned source is the actual saved Xi coefficient/field variation
    plus the explicitly supplied amplitude and homogeneous variations. A
    complete physical tangent requires its other constraint equations.
    """
    if side not in ('plus','minus'):
        raise ValueError('same-history collar identity required')
    points = np.asarray(points,float)
    if points.ndim != 2 or points.shape[1] != 2 or not len(points):
        raise ValueError('nonempty independent original (time,rho) points required')
    def field(t,r):
        result = reconstruct_combination(arrays,side,wall,wall_source,times=[t],radii=[r])
        return {key: value[0,0] for key,value in result.items()}
    coefficient = original_d5_coefficient_callback(
        lambda t:(history.value(t)[0],history.source(t)[0]),
        sheet_orientation=1 if side == 'plus' else -1,
        gauge_basis_evaluate=history.gauge_basis)
    values, report = independent_residual_application(field,coefficient,points)
    report.update(homogeneous_coordinates_per_time_node=366,
        source_scope='saved original Xi plus explicit amplitude/h source germs; not a complete constrained physical tangent',
        physical_admission=False, finite_probe_set_is_continuum_bound=False)
    return values,report


def event_matching_rows(child_trace, child_total_source, parent_trace,
        parent_fixed_coordinate_source, parent_gradient, *, transfer,
        transfer_source, total_base_source, trace_contact_scope):
    """Execute Gamma_c-U(Gamma_p o F) and its complete declared first row.

    All parent arguments have already been evaluated at F_B. The gradient
    axis lists the original parent coordinates (time,rho,or a wider chart).
    ``total_base_source`` includes D F_B delta x_child exactly once.
    ``child_total_source`` already includes the child moving evaluation
    point, so this routine does not append that contact a second time.
    Frame, density and normal-trace contacts belong in the supplied traces,
    trace sources and U source according to ``trace_contact_scope``.
    """
    p = np.asarray(parent_trace,complex)
    c = np.asarray(child_trace,complex)
    if p.ndim != 3 or c.ndim != 3 or p.shape[0] != c.shape[0] or p.shape[2] != c.shape[2]:
        raise ValueError('point by carrier by common application-column traces required')
    if not np.isfinite(p).all() or not np.isfinite(c).all():
        raise ValueError('finite actual trace operands required')
    px = _finite(parent_fixed_coordinate_source,p.shape,'parent fixed-coordinate trace source')
    cx = _finite(child_total_source,c.shape,'child total trace source')
    u = _finite(transfer,(len(p),c.shape[1],p.shape[1]),'actual bundle transmission')
    ux = _finite(transfer_source,u.shape,'actual bundle transmission source')
    g = np.asarray(parent_gradient,complex)
    if g.ndim != 4 or g.shape[0] != len(p) or g.shape[2:] != p.shape[1:] or not np.isfinite(g).all():
        raise ValueError('point by parent-coordinate by carrier by column gradient required')
    fx = _finite(total_base_source,(len(p),g.shape[1]),'total event base variation')
    if not isinstance(trace_contact_scope,dict) or not all(
            isinstance(trace_contact_scope.get(key),str) and trace_contact_scope[key]
            for key in ('frame','density','normal_profile','child_evaluation')):
        raise ValueError('explicit frame/density/normal/child-evaluation source scope required')
    base = np.einsum('pa,padk->pdk',fx,g)
    state = u@px
    frame = ux@p
    base_contact = u@base
    return dict(event_rows=c-u@p,
        event_source_rows=cx-frame-state-base_contact,
        child_total_source=cx,parent_state_contact=-state,
        bundle_transfer_contact=-frame,base_pullback_contact=-base_contact,
        parent_total_pullback_source=px+base,
        original_event_equation='Gamma0_child-U_R (Gamma0_parent composed with F_B)=0',
        original_event_source_equation='delta Gamma0_child-delta U_R Gamma0_parent-U_R(delta Gamma0_parent+d Gamma0_parent delta F_B)=0',
        trace_contact_scope=dict(trace_contact_scope),
        moving_child_evaluation_appended_again=False,physical_admission=False)


def event_representation_error_transport(child_error, child_source_error,
        parent_error, parent_source_error, parent_gradient_error, *, transfer,
        transfer_source, total_base_source, operand_scope):
    """Transport explicitly supplied finite representation differences/errors.

    Original strong residuals are NOT trace-error estimates. Those estimates
    require a physical outer/initial stability or Green estimate which this
    API does not manufacture. The absolute majorants here are algebraic
    budgets over the supplied finite error operands only.
    """
    if operand_scope not in ('finite_representation_difference','supplied_pointwise_error_bound'):
        raise ValueError('explicit finite error-operand scope required')
    result = event_matching_rows(child_error,child_source_error,parent_error,
        parent_source_error,parent_gradient_error,transfer=transfer,
        transfer_source=transfer_source,total_base_source=total_base_source,
        trace_contact_scope=dict(frame='included in supplied error operands',
            density='included in supplied error operands',
            normal_profile='included in supplied error operands',
            child_evaluation='total child error source; total deltaF_B supplied once'))
    c,cx,p,px,g,u,ux,f = (np.abs(np.asarray(a)) for a in (
        child_error,child_source_error,parent_error,parent_source_error,
        parent_gradient_error,transfer,transfer_source,total_base_source))
    result['event_absolute_budget'] = c+u@p
    result['event_source_absolute_budget'] = cx+ux@p+u@px+u@np.einsum('pa,padk->pdk',f,g)
    result.update(operand_scope=operand_scope,finite_algebraic_budget_only=True,
        strong_residual_identified_as_trace_error=False,continuum_error_bound=False)
    return result
