"""Full five-component parent Maxwell action in the retained material chart.

All temporal/radial Gauss rows, spatial rows and curvature contacts are
variations of one scalar action.  The evaluated mechanical reference is not
a full stationary gauge solution; matter, boundary and other action rows
must enter the common solve.  Unit-Tr16 real components are used throughout.
The geometric R8 owner already contains the mechanical reference energy;
the added independent Maxwell scalar is S(Abar+a)-S(Abar), not S(Abar+a).
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_birth_candidate_geometry_action import ROOT, RESET_RECEIPT, STATE_SOURCE
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_retarded_hypercharge import WALL, regular_radial_basis
from .muon_matched_mechanical_source import epsilon

FIELD_ORDER = ('A_tau', 'A_rho', 'A_1', 'A_2', 'A_3')
M = np.sqrt(8)*np.column_stack((np.eye(3), np.zeros(3)))


def _bracket(a, b):
    """[H_a,H_b]=epsilon_abc H_c/sqrt(2); H_Y is central."""
    out = np.zeros(np.broadcast_shapes(a.shape, b.shape), float)
    out[..., :3] = np.cross(a[..., :3], b[..., :3])/np.sqrt(2)
    return out


def _curl(a, angular):
    return 2*a+np.einsum('ijk,...jkc->...ic', epsilon(), angular)


def _curl_bracket(a, b):
    result = np.zeros(np.broadcast_shapes(a.shape, b.shape), float)
    eps = epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if eps[i, j, k]:
                    result[..., i, :] += eps[i, j, k]*_bracket(a[..., j, :], b[..., k, :])
    return result


def _validate_fields(fields, derivatives_tau, derivatives_rho, derivatives_angular,
                     radial_count, angular_count, *, indexed=False):
    values = (fields, derivatives_tau, derivatives_rho, derivatives_angular)
    if any(not np.isrealobj(x) for x in values):
        raise ValueError('real unit-Tr16 component applications required; no complex projection')
    a, at, ar, ea = (np.asarray(x, float) for x in values)
    if any(not np.isfinite(x).all() for x in (a, at, ar, ea)):
        raise ValueError('finite common coefficient applications required')
    if indexed:
        if a.ndim != 5 or a.shape[0] != radial_count or a.shape[2:] != (angular_count, 5, 4):
            raise ValueError('indexed tests must have (radial,test,Haar_point,5,4) axes')
    elif a.shape != (radial_count, angular_count, 5, 4):
        raise ValueError('gauge fields must have (radial,Haar_point,5,4) axes')
    if at.shape != a.shape or ar.shape != a.shape or ea.shape != a.shape[:-2]+(3, 5, 4):
        raise ValueError('time/radial/angular derivatives must use the same five-component vector')
    return a, at, ar, ea


def _validate_geometry(coefficients, quadrature, Haar_weights):
    if not np.isrealobj(quadrature) or not np.isrealobj(Haar_weights):
        raise ValueError('real reference integration weights required')
    w, hw = np.asarray(quadrature, float), np.asarray(Haar_weights, float)
    if (w.ndim != 1 or hw.ndim != 1 or len(w) != len(coefficients['rows'])
            or not np.isfinite(w).all() or not np.isfinite(hw).all()
            or np.any(w <= 0) or np.any(hw <= 0)):
        raise ValueError('finite positive common radial and Haar quadrature required')
    if not np.isclose(np.sum(hw), 1., rtol=0, atol=1e-12):
        raise ValueError('Haar weights must average to one; angular 2*pi^2 is already in the densities')
    size = coefficients['coordinate_count']
    required = ('electric', 'radial', 'angular', 'electric_radial', 'shift',
                'connection_lambda', 'lambda_tau', 'lambda_rho')
    for row in coefficients['rows']:
        for key in required:
            x = row[key]
            if (not isinstance(x, Jet) or np.shape(x.gradient) != (size,)
                    or np.shape(x.hessian) != (size, size)
                    or not np.isrealobj(x.value) or not np.isrealobj(x.gradient)
                    or not np.isrealobj(x.hessian)
                    or not np.isfinite(x.value) or not np.isfinite(x.gradient).all()
                    or not np.isfinite(x.hessian).all()):
                raise ValueError('finite real same-coordinate geometry two-jets required')
        if any(row[key].value <= 0 for key in ('electric', 'radial', 'angular', 'electric_radial')):
            raise ValueError('positive literal Maxwell metric densities required')
        # A second independently supplied radial-electric normalization is
        # forbidden: this is the SAME metric pullback through order two.
        identity = row['electric_radial']-row['electric']*row['radial']/row['angular']
        scale = max(1., abs(row['electric_radial'].value))
        if (abs(identity.value) > 5e-12*scale or np.max(abs(identity.gradient)) > 5e-10*scale
                or np.max(abs(identity.hessian)) > 5e-8*scale):
            raise ValueError('F_tau_rho density must equal e*r/d in the same metric two-jet')
    return w, hw, size


def _curvature_polynomials(a, at, ar, ea):
    """Curvature coefficients in (1,h,lambda_tau,lambda_rho,h^2), h=lambda-1."""
    Ai, At, Ar = a[..., 2:, :], a[..., 0, :], a[..., 1, :]
    shape = Ai.shape
    Ft, Fr, B = (np.zeros((5,)+shape) for _ in range(3))
    X = at[..., 1, :]-ar[..., 0, :]+_bracket(At, Ar)
    Ft[0] = at[..., 2:, :]-ea[..., :, 0, :]+_bracket(At[..., None, :], Ai)
    Ft[1] = _bracket(At[..., None, :], M); Ft[2] = M
    Fr[0] = ar[..., 2:, :]-ea[..., :, 1, :]+_bracket(Ar[..., None, :], Ai)
    Fr[1] = _bracket(Ar[..., None, :], M); Fr[3] = M
    B[0] = _curl(Ai, ea[..., :, 2:, :])+.5*_curl_bracket(Ai, Ai)
    B[1] = 2*M+_curl_bracket(M, Ai); B[4] = 2*M
    return X, Ft, Fr, B


def _direction_polynomials(a, direction, dt, dr, ed):
    """Literal first curvature variation for every five-component test."""
    Ai, At, Ar = a[..., 2:, :], a[..., 0, :], a[..., 1, :]
    di, d0, d1 = direction[..., 2:, :], direction[..., 0, :], direction[..., 1, :]
    Ft, Fr, B = (np.zeros((5,)+di.shape) for _ in range(3))
    X = dt[..., 1, :]-dr[..., 0, :]+_bracket(d0, Ar)+_bracket(At, d1)
    Ft[0] = dt[..., 2:, :]-ed[..., :, 0, :]+_bracket(d0[..., None, :], Ai)+_bracket(At[..., None, :], di)
    Ft[1] = _bracket(d0[..., None, :], M)
    Fr[0] = dr[..., 2:, :]-ed[..., :, 1, :]+_bracket(d1[..., None, :], Ai)+_bracket(Ar[..., None, :], di)
    Fr[1] = _bracket(d1[..., None, :], M)
    B[0] = _curl(di, ed[..., :, 2:, :])+_curl_bracket(Ai, di)
    B[1] = _curl_bracket(M, di)
    return X, Ft, Fr, B


def _second_curvatures(v, z):
    """Bilinear nonlinear contacts; no coefficient or derivative is fitted."""
    vi, zi = v[..., 2:, :], z[..., 2:, :]
    X = _bracket(v[..., 0, :], z[..., 1, :])+_bracket(z[..., 0, :], v[..., 1, :])
    Ft = _bracket(v[..., 0, None, :], zi)+_bracket(z[..., 0, None, :], vi)
    Fr = _bracket(v[..., 1, None, :], zi)+_bracket(z[..., 1, None, :], vi)
    B = _curl_bracket(vi, zi)
    return X, Ft, Fr, B


def _parameters(row, size):
    h = row['connection_lambda']-1
    return (Jet.constant(1., size), h, row['lambda_tau'], row['lambda_rho'], h*h)


def _inner(A, B, hw):
    # A: (parameter,Haar_point,spatial,internal),
    # B: (parameter,test,Haar_point,spatial,internal).
    return np.einsum('p,kpic,ljpic->jkl', hw, A, B)


def _accumulator(count, size):
    return dict(values=np.zeros(count), geometric_jacobian=np.zeros((count, size)),
                geometric_hessians=np.zeros((count, size, size)))


def _add_scalar(out, coefficients, jet):
    nonzero = np.flatnonzero(coefficients)
    if len(nonzero):
        c = coefficients[nonzero]
        out['values'][nonzero] += c*jet.value
        out['geometric_jacobian'][nonzero] += c[:, None]*jet.gradient
        out['geometric_hessians'][nonzero] += c[:, None, None]*jet.hessian


def _add_polynomial(out, coefficients, factor, params):
    for i, j in np.argwhere(np.any(coefficients != 0, axis=0)):
        _add_scalar(out, coefficients[:, i, j], factor*params[i]*params[j])


def _row_forms(out, row, params, hw, weight, base, direction):
    X, Ft, Fr, B = base; dX, dFt, dFr, dB = direction
    e, r, d, k, beta = (row[key] for key in ('electric', 'radial', 'angular', 'electric_radial', 'shift'))
    _add_scalar(out, np.einsum('p,pc,jpc->j', hw, X, dX), weight*k)
    _add_polynomial(out, _inner(Ft, dFt, hw), weight*e, params)
    _add_polynomial(out, _inner(Ft, dFr, hw)+_inner(Fr, dFt, hw), -weight*e*beta, params)
    _add_polynomial(out, _inner(Fr, dFr, hw), weight*(e*beta*beta-r), params)
    _add_polynomial(out, _inner(B, dB, hw), -weight*d, params)


def full_maxwell_action_jet(coefficient_jets, quadrature, Haar_weights, *,
        gauge, gauge_tau, gauge_rho, gauge_angular):
    """Differentiate the literal scalar action in all common geometry columns."""
    w, hw, size = _validate_geometry(coefficient_jets, quadrature, Haar_weights)
    a, at, ar, ea = _validate_fields(gauge, gauge_tau, gauge_rho, gauge_angular, len(w), len(hw))
    result = _accumulator(1, size)
    for i, c in enumerate(coefficient_jets['rows']):
        base = _curvature_polynomials(a[i], at[i], ar[i], ea[i])
        direction = (base[0][None],)+tuple(v[:, None] for v in base[1:])
        _row_forms(result, c, _parameters(c, size), hw, .5*w[i], base, direction)
    return dict(value=float(result['values'][0]), gradient=result['geometric_jacobian'][0],
        hessian=result['geometric_hessians'][0], clock=coefficient_jets['clock'],
        field_order=FIELD_ORDER, induced_connection_motion_count=1,
        normalization='per kappa1/SAME embedding index; real unit-Tr16 internal basis',
        action='1/2 integral [k Ftr^2+e(Fti-beta Fri)^2-r Fri^2-d B^2]',
        physical_stationary_base=False, complete_native_action=False)


def background_subtracted_maxwell_action_jet(coefficient_jets, quadrature, Haar_weights, *,
        gauge, gauge_tau, gauge_rho, gauge_angular):
    """Independent gauge scalar S(Abar(q)+a)-S(Abar(q)), in the same chart.

    R8 already owns the mechanical reference curvature.  Subtracting its
    metric and induced-connection derivatives avoids double counting in a
    coupled geometry solve.  Gauge and geometry-gauge derivatives are the
    full weak rows because the subtracted scalar has no independent a.
    """
    fields = dict(gauge=gauge, gauge_tau=gauge_tau, gauge_rho=gauge_rho, gauge_angular=gauge_angular)
    total = full_maxwell_action_jet(coefficient_jets, quadrature, Haar_weights, **fields)
    background = full_maxwell_action_jet(coefficient_jets, quadrature, Haar_weights,
        **{k:np.zeros_like(v) for k,v in fields.items()})
    return dict(value=total['value']-background['value'],
        gradient=total['gradient']-background['gradient'],
        hessian=total['hessian']-background['hessian'],
        full_action_value=total['value'], mechanical_reference_value=background['value'],
        action='S_Maxwell(Abar(q)+a)-S_Maxwell(Abar(q))',
        mechanical_reference_already_in_R8=True, background_energy_added_twice=False,
        clock=coefficient_jets['clock'], normalization=total['normalization'],
        full_weak_gauge_rows_unchanged=True, geometry_gauge_mixed_rows_unchanged=True,
        physical_stationary_base=False, complete_native_action=False)


def full_maxwell_weak_geometric_jets(coefficient_jets, quadrature, Haar_weights, *,
        gauge, gauge_tau, gauge_rho, gauge_angular,
        tests, tests_tau, tests_rho, tests_angular):
    """Actual full Euler weak rows and 100-column geometry derivatives.

    Derivative-form rows already contain the action variation.  The temporal
    momentum is integrated over this cap slice.  The radial momentum output
    is an integrated weak coefficient; an actual wall/pole contact requires
    evaluating its trace on that face, not reusing the radial integral.
    No sourced Gauss equation or independent gauge field is set to zero.
    """
    w, hw, size = _validate_geometry(coefficient_jets, quadrature, Haar_weights)
    a, at, ar, ea = _validate_fields(gauge, gauge_tau, gauge_rho, gauge_angular, len(w), len(hw))
    v, vt, vr, ev = _validate_fields(tests, tests_tau, tests_rho, tests_angular, len(w), len(hw), indexed=True)
    count = v.shape[1]; weak, temporal, radial = (_accumulator(count, size) for _ in range(3))
    for i, c in enumerate(coefficient_jets['rows']):
        params = _parameters(c, size)
        base = _curvature_polynomials(a[i], at[i], ar[i], ea[i])
        direction = _direction_polynomials(a[i], v[i], vt[i], vr[i], ev[i])
        _row_forms(weak, c, params, hw, w[i], base, direction)
        X, Ft, Fr, _ = base
        e, r, k, beta = (c[key] for key in ('electric', 'radial', 'electric_radial', 'shift'))
        _add_scalar(temporal, np.einsum('p,pc,jpc->j', hw, X, v[i, :, :, 1]), w[i]*k)
        _add_scalar(radial, np.einsum('p,pc,jpc->j', hw, X, v[i, :, :, 0]), -w[i]*k)
        for p in range(5):
            ftv = np.einsum('p,pic,jpic->j', hw, Ft[p], v[i, :, :, 2:])
            frv = np.einsum('p,pic,jpic->j', hw, Fr[p], v[i, :, :, 2:])
            _add_scalar(temporal, ftv, w[i]*e*params[p])
            _add_scalar(temporal, frv, -w[i]*e*beta*params[p])
            _add_scalar(radial, ftv, -w[i]*e*beta*params[p])
            _add_scalar(radial, frv, w[i]*(e*beta*beta-r)*params[p])
    return dict(weak=weak, temporal_momentum_test=temporal, radial_momentum_test=radial,
        clock=coefficient_jets['clock'], field_order=FIELD_ORDER,
        temporal_contact='final plus, initial minus; no At temporal momentum',
        radial_contact='wall plus, pole minus; At momentum=-k Ftr, Ar momentum=0',
        radial_momentum_test_scope='integrated radial weak coefficient; evaluate same momenta on the face for a boundary contact',
        derivative_rows_are_full_action_variations=True, event_contacts_appended=False,
        background_connection_motion_count=1, temporal_radial_Gauss_rows_replaced=False,
        unforced_Gauss_imposed=False, independent_gauge_fields_selected=False,
        normalization='per kappa1/SAME embedding index; real unit-Tr16 internal basis',
        physical_stationary_base=False, complete_native_action=False)


def full_maxwell_hessian_pairing(coefficient_jets, quadrature, Haar_weights, *,
        gauge, gauge_tau, gauge_rho, gauge_angular,
        left, left_tau, left_rho, left_angular,
        right, right_tau, right_rho, right_angular, geometric_derivatives=True):
    """Bilinear gauge Hessian with every nonlinear curvature contact retained."""
    w, hw, size = _validate_geometry(coefficient_jets, quadrature, Haar_weights)
    args = ((gauge, gauge_tau, gauge_rho, gauge_angular),
            (left, left_tau, left_rho, left_angular), (right, right_tau, right_rho, right_angular))
    a, l, z = (_validate_fields(*vals, len(w), len(hw)) for vals in args)
    result, contacts = (_accumulator(1, size) for _ in range(2))
    scalar_result = scalar_contact = 0.
    for i, c in enumerate(coefficient_jets['rows']):
        params = _parameters(c, size)
        base = _curvature_polynomials(*(x[i] for x in a))
        dl = _direction_polynomials(a[0][i], *(x[i] for x in l))
        dz = _direction_polynomials(a[0][i], *(x[i] for x in z))
        mixed = _second_curvatures(l[0][i], z[0][i])
        if not geometric_derivatives:
            pv = np.array([x.value for x in params])
            def values(poly):
                return (poly[0],)+tuple(np.einsum('k,kpic->pic', pv, x) for x in poly[1:])
            bval, lv, zv = values(base), values(dl), values(dz)
            e, r, d, k, beta = (c[key].value for key in ('electric', 'radial', 'angular', 'electric_radial', 'shift'))
            inner = lambda x,y: np.einsum('p,...pc,...pc->...', hw, x, y) if x.ndim == 2 else np.einsum('p,pic,pic->', hw, x, y)
            def pairing(left, right):
                return (k*inner(left[0], right[0])
                    +e*inner(left[1]-beta*left[2], right[1]-beta*right[2])
                    -r*inner(left[2], right[2])-d*inner(left[3], right[3]))
            scalar_result += w[i]*pairing(lv, zv)
            scalar_contact += w[i]*pairing(bval, mixed)
            continue
        indexed = (dz[0][None],)+tuple(v[:, None] for v in dz[1:])
        _row_forms(result, c, params, hw, w[i], dl, indexed)
        contact = (mixed[0][None],)+tuple(np.stack((v,)+tuple(np.zeros_like(v) for _ in range(4)))[:, None] for v in mixed[1:])
        _row_forms(contacts, c, params, hw, w[i], base, contact)
    if not geometric_derivatives:
        return dict(value=float(scalar_result+scalar_contact), curvature_contact=float(scalar_contact),
            gradient=None, hessian=None, geometric_derivatives_evaluated=False,
            nonlinear_contacts_retained=True, physical_stationary_base=False)
    return dict(value=float(result['values'][0]+contacts['values'][0]),
        curvature_contact=float(contacts['values'][0]),
        gradient=result['geometric_jacobian'][0]+contacts['geometric_jacobian'][0],
        hessian=result['geometric_hessians'][0]+contacts['geometric_hessians'][0],
        nonlinear_contacts_retained=True, physical_stationary_base=False)


def full_maxwell_gauge_hessian_matrix(coefficient_jets, quadrature, Haar_weights, *,
        gauge, gauge_tau, gauge_rho, gauge_angular,
        tests, tests_tau, tests_rho, tests_angular):
    """Assemble the same-action finite gauge Hessian including all Gauss columns.

    This efficient value-only contraction is consumed by the common geometry /
    gauge coefficient solve.  Tests and derivatives must come from its common
    coefficient basis; no temporal or radial one-form is eliminated here.
    """
    w, hw, size = _validate_geometry(coefficient_jets, quadrature, Haar_weights)
    a = _validate_fields(gauge, gauge_tau, gauge_rho, gauge_angular, len(w), len(hw))
    v = _validate_fields(tests, tests_tau, tests_rho, tests_angular, len(w), len(hw), indexed=True)
    count = v[0].shape[1]
    matrix, contacts = np.zeros((count, count)), np.zeros((count, count))
    for i, c in enumerate(coefficient_jets['rows']):
        params = np.array([x.value for x in _parameters(c, size)])
        base = _curvature_polynomials(*(x[i] for x in a))
        direction = _direction_polynomials(a[0][i], *(x[i] for x in v))
        X = base[0]
        Ft, Fr, B = (np.einsum('l,lpic->pic', params, x) for x in base[1:])
        dX = direction[0]
        dFt, dFr, dB = (np.einsum('l,ljpic->jpic', params, x) for x in direction[1:])
        mixed = _second_curvatures(v[0][i][:, None], v[0][i][None])
        e, r, d, k, beta = (c[key].value for key in ('electric', 'radial', 'angular', 'electric_radial', 'shift'))
        inner0 = lambda x,y:np.einsum('p,jpc,kpc->jk', hw, x, y)
        inner = lambda x,y:np.einsum('p,jpic,kpic->jk', hw, x, y)
        linear = (k*inner0(dX, dX)+e*inner(dFt-beta*dFr, dFt-beta*dFr)
                  -r*inner(dFr, dFr)-d*inner(dB, dB))
        contact = (k*np.einsum('p,pc,jkpc->jk', hw, X, mixed[0])
            +e*np.einsum('p,pic,jkpic->jk', hw, Ft-beta*Fr, mixed[1]-beta*mixed[2])
            -r*np.einsum('p,pic,jkpic->jk', hw, Fr, mixed[2])
            -d*np.einsum('p,pic,jkpic->jk', hw, B, mixed[3]))
        matrix += w[i]*(linear+contact); contacts += w[i]*contact
    return dict(matrix=matrix, curvature_contact_matrix=contacts,
        symmetry_defect=float(np.max(abs(matrix-matrix.T))) if count else 0.,
        field_order=FIELD_ORDER, nonlinear_contacts_retained=True,
        temporal_radial_Gauss_columns_eliminated=False, physical_stationary_base=False,
        normalization='per kappa1/SAME embedding index; real unit-Tr16 internal basis')


def retained_full_background_application(repository=ROOT, *, points=96, test_order=8):
    """Evaluate all five weak rows on the actual E1+ mechanical reference."""
    repository = Path(repository)
    x, w = leggauss(points); rho, w = (x+1)*WALL/2, w*WALL/2
    q, velocity, m = retained_state(repository)
    c = geometric_connection_coefficient_jets(12, q, velocity, m, rho, clock='coordinate_time')
    H, Hr = regular_radial_basis(rho, test_order)
    count = (test_order+1)*5*4
    test = np.zeros((points, count, 1, 5, 4)); tr = np.zeros_like(test)
    labels = []
    for j in range(test_order+1):
        for field in range(5):
            for internal in range(4):
                index = len(labels)
                test[:, index, 0, field, internal] = H[:, j]
                tr[:, index, 0, field, internal] = Hr[:, j]
                labels.append(dict(radial_test=j, field=FIELD_ORDER[field], internal=internal))
    zero = np.zeros((points, 1, 5, 4)); angular = np.zeros((points, 1, 3, 5, 4))
    fields = dict(gauge=zero, gauge_tau=zero, gauge_rho=zero, gauge_angular=angular)
    action = full_maxwell_action_jet(c, w, np.ones(1), **fields)
    independent = background_subtracted_maxwell_action_jet(c, w, np.ones(1), **fields)
    application = full_maxwell_weak_geometric_jets(c, w, np.ones(1), **fields,
        tests=test, tests_tau=np.zeros_like(test), tests_rho=tr,
        tests_angular=np.zeros((points, count, 1, 3, 5, 4)))
    return dict(action=action, independent_action=independent, application=application, labels=labels, rho=rho, quadrature=w,
        coefficient_jets=c, actual_geometry=dict(q=q, velocity=velocity, lapse_shift=m),
        reference='A_tau=A_rho=0, A_i=sqrt(8)H_i(lambda-1); actual induced first derivatives',
        test_scope='CONTROL_ONLY finite-energy radial tests tensor all five components and four real internals',
        Gauss_zero_provenance='At/Ar constant-angular tests: Ftr=0; each background Fti/Fri is parallel to Mi, so <Mi,[eta,Mi]>=0; E_i eta=0. This is an action-derived reference value, not an imposed matter-free physical Gauss constraint.',
        stationary_E1_claim=False, physical_Pauli_contraction=False)


def materialize(output, repository=ROOT):
    """Save a deterministic evaluated full weak background application."""
    repository = Path(repository); output = Path(output)
    if output.exists():
        raise FileExistsError('preserve prior evidence; use a new output directory')
    result = retained_full_background_application(repository)
    arrays = dict(rho=result['rho'], quadrature=result['quadrature'])
    for group in ('weak', 'temporal_momentum_test', 'radial_momentum_test'):
        arrays.update({group+'_'+k:v for k,v in result['application'][group].items()})
    arrays.update({k:result['action'][k] for k in ('gradient', 'hessian')})
    arrays.update({'independent_action_'+k:result['independent_action'][k] for k in ('gradient','hessian')})
    arrays.update(result['actual_geometry'])
    for key in ('electric', 'radial', 'angular', 'electric_radial', 'shift',
                'connection_lambda', 'lambda_tau', 'lambda_rho'):
        rows = [r[key] for r in result['coefficient_jets']['rows']]
        arrays['coefficient_'+key+'_values'] = np.array([v.value for v in rows])
        arrays['coefficient_'+key+'_jacobian'] = np.array([v.gradient for v in rows])
        # Applied weak rows retain their complete100x100 Hessians.  The
        # input coefficients' two normal columns are exported without
        # duplicating every already-owned100x100 coefficient input matrix.
        arrays['coefficient_'+key+'_normal_hessian_columns'] = np.array([v.hessian[:, -2:] for v in rows])
    output.mkdir(parents=True)
    # Deterministic compression preserves every computed array and avoids
    # publishing tens of megabytes of exactzero constraint/reference slots.
    with ZipFile(output/'application.npz', 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, value in sorted(arrays.items()):
            stream = BytesIO()
            np.lib.format.write_array(stream, np.asarray(value), allow_pickle=False)
            member = ZipInfo(name+'.npy', date_time=(1980, 1, 1, 0, 0, 0))
            member.external_attr = 0o600 << 16
            member.compress_type = ZIP_DEFLATED
            archive.writestr(member, stream.getvalue(), compresslevel=9)
    refs = [STATE_SOURCE, RESET_RECEIPT,
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
        'src/bhsm/interface/muon_matched_mechanical_source.py',
        'src/bhsm/interface/aether_diagonal_sp1_m4_attachment_v15_50.py',
        'src/bhsm/interface/aether_exact_radial_schur_lift_v15_83.py']
    weak = result['application']['weak']
    values = weak['values'].reshape(-1, 5, 4)
    gjac = weak['geometric_jacobian'].reshape(-1, 5, 4, 100)
    ghess = weak['geometric_hessians'].reshape(-1, 5, 4, 100, 100)
    receipt = dict(scope='EVALUATED_ACTUAL_E1_PLUS_FULL_FIVE_COMPONENT_MAXWELL_REFERENCE_WEAK_APPLICATION',
        input_hashes={p:sha256((repository/p).read_bytes()).hexdigest() for p in refs},
        numerical_application_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        numerical_packaging='deterministic ZIP_DEFLATED level9; sorted members;1980 timestamps; every array retained',
        labels=result['labels'], field_order=FIELD_ORDER, geometry_coordinate_count=100,
        radial_test_order=8, radial_quadrature_order=96, angular_rule='exact constant right-Maurer field/test Haar average one',
        action_value=result['action']['value'], action_geometry_gradient_norm=float(np.linalg.norm(result['action']['gradient'])),
        full_reference_action_role='diagnostic mechanical Maxwell energy already included in geometric R8; not added again',
        additional_independent_action=result['independent_action']['value'],
        additional_independent_geometry_gradient_norm=float(np.linalg.norm(result['independent_action']['gradient'])),
        additional_independent_geometry_hessian_norm=float(np.linalg.norm(result['independent_action']['hessian'])),
        coupled_geometry_composition='S_R8+c_attachment*(S_Maxwell(Abar(q)+a)-S_Maxwell(Abar(q)))',
        relative_attachment_factor_to_normalized_cap=None,
        relative_attachment_factor_assigned=False,
        background_subtraction_owner='aether_diagonal_sp1_m4_attachment_v15_50.action_ownership_ledger',
        complete_geometry_Euler_claim=False, background_energy_added_twice=False,
        weak_values=weak['values'].tolist(), weak_geometry_jacobian_norm=float(np.linalg.norm(weak['geometric_jacobian'])),
        weak_normal_value_column=weak['geometric_jacobian'][:, -2].tolist(),
        weak_normal_rate_column=weak['geometric_jacobian'][:, -1].tolist(),
        Gauss_reference_max=float(np.max(abs(values[:, :2]))),
        Gauss_reference_geometry_jacobian_max=float(np.max(abs(gjac[:, :2]))),
        Gauss_reference_geometry_hessian_max=float(np.max(abs(ghess[:, :2]))),
        spatial_reference_weak_norm=float(np.linalg.norm(values[:, 2:])),
        Gauss_zero_provenance=result['Gauss_zero_provenance'],
        reference=result['reference'], test_scope=result['test_scope'],
        action_formula=result['action']['action'],
        radial_electric_density='k=e*r/d=common*r_orbit^3/(lapse*C_rho*material_jacobian)',
        curvature_formula=dict(Ftr='d_tau Ar-d_rho At+[At,Ar]',
            Fti='d_tau Ai-E_i At+[At,Ai]', Fri='d_rho Ai-E_i Ar+[Ar,Ai]',
            B='2Ai+epsilon_ijk E_j A_k+1/2 epsilon_ijk[A_j,A_k]'),
        temporal_contact=result['application']['temporal_contact'],
        radial_contact=result['application']['radial_contact'], contacts_appended_twice=False,
        radial_momentum_test_scope=result['application']['radial_momentum_test_scope'],
        normalization=result['action']['normalization'], common_normalization_assigned=False,
        induced_mechanical_motion_count=1, source_value=0., source_rate=0., trial_normal=1.,
        unforced_Gauss_imposed=False, full_gauge_primal_selected=False,
        missing_coupled_terms='same-action matter currents, event matching, gauge fixing/constraints and other scalar sectors remain to be composed in one solve',
        stationary_E1_claim=False, complete_native_action=False, physical_Pauli_contraction=False,
        error_scope='binary64 finite weak application; no stationary-base or continuum-tail enclosure')
    (output/'result.json').write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output), sort_keys=True))
