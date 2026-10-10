"""Same-vector intrinsic Higgs birth equations and their action cotangents.

The current mechanics owner identifies H_child(F(x)) = U_H(x) H_parent(x)
at the same E1 birth.  Positive-time canonical p_H already carries the
metric density.  Its endpoint signs are parent +p_H and child -p_H.  Thus
the scalar boundary variation gives p_parent - T^* p_child = 0: the area
action has no direct H argument at fixed geometry.  This is an application
of the retained boundary law, not independently supplied scalar Cauchy data.

Reference quadrature, a moving material Jacobian and the endpoint metric
density are distinct.  The latter belongs in a field Gram, and must not
multiply canonical momentum density a second time.  A projected transport
does not erase its unrepresented image.  Both trace and momentum image
remainders are retained below.  No physical worldvolume or primal is chosen.
"""
from __future__ import annotations

import numpy as np

from .muon_intrinsic_worldvolume_scalar_transport import (
    scalar_birth_transport_application, unit_s3_material_frame,
)


def _finite(value, name, *, complex_value=False):
    array = np.asarray(value, dtype=complex if complex_value else float)
    if not np.isfinite(array).all():
        raise ValueError(f'finite {name} required')
    return array


def _realify(value):
    value = np.asarray(value)
    return np.concatenate((value.real.ravel(), value.imag.ravel()))


def scalar_birth_action_rows(*, transport, parent_birth_points,
                             birth_parent_time, birth_child_time, quadrature,
                             basis_evaluator, density_evaluator,
                             parent_coefficient_map, child_coefficient_map,
                             parent_momentum_coefficient_map,
                             child_momentum_coefficient_map,
                             time_index=-1, parent_birth_points_variation=None,
                             delta_quadrature=None):
    """Apply H trace and canonical flux matching on one real coefficient vector.

    All four extraction maps are fixed maps of ``transport['coefficients']``;
    momentum maps represent the SAME canonical density p_H unknowns.  The
    evaluators/transport differentiate metric, basis, bundle, moving points
    and Jacobian from that vector.  If a coefficient map itself moves, use a
    fixed computational chart with that motion in its evaluator instead.

    ``delta_quadrature`` is optional independent reference-domain motion,
    assigned only once; metric density and material Jacobian motion already
    belong to the existing transport application.  A tangent uses the
    transport's actual coefficient_variation.  The sampled trace rows are
    retained without claiming a square or closed finite Newton system.
    """
    c = _finite(transport['coefficients'], 'common coefficients')
    if c.ndim != 1:
        raise ValueError('one real common coefficient vector required')
    direction = transport.get('coefficient_variation')
    tangent = direction is not None
    if tangent:
        direction = _finite(direction, 'common coefficient direction')
        if direction.shape != c.shape:
            raise ValueError('coefficient direction must act on the same vector')
    elif delta_quadrature is not None:
        raise ValueError('reference quadrature motion needs a coefficient tangent')
    captured = {}

    def capture_basis(side, points, coefficients, variation):
        data = basis_evaluator(side, points, coefficients, variation)
        captured[side] = (points, data)
        return data

    app = scalar_birth_transport_application(
        transport=transport, parent_birth_points=parent_birth_points,
        birth_parent_time=birth_parent_time, birth_child_time=birth_child_time,
        quadrature=quadrature, basis_evaluator=capture_basis,
        density_evaluator=density_evaluator,
        parent_coefficient_map=parent_coefficient_map,
        child_coefficient_map=child_coefficient_map,
        pairing='real_2Re', time_index=time_index,
        parent_birth_points_variation=parent_birth_points_variation)
    Bp, Bc = (np.asarray(captured[s][1]['basis'], complex)
              for s in ('parent', 'child'))
    quad = _finite(quadrature, 'reference quadrature')
    J = np.asarray(transport['haar_jacobian'][time_index], float)
    maps = [_finite(M, name) for M, name in (
        (parent_coefficient_map, 'parent H map'),
        (child_coefficient_map, 'child H map'),
        (parent_momentum_coefficient_map, 'parent canonical p map'),
        (child_momentum_coefficient_map, 'child canonical p map'))]
    for M, B in zip(maps, (Bp, Bc, Bp, Bc)):
        if M.shape != (B.shape[2], len(c)):
            raise ValueError('all H/p maps must extract the same coefficient vector')
    hp, hc, pp, pc = [M @ c for M in maps]
    p_parent = Bp @ pp
    p_child = Bc @ pc
    image = app['scalar_transport_image']
    T, Gp, Gc = (app[key] for key in (
        'trace_transport', 'parent_pairing', 'child_pairing'))

    def dual(B, p, weights):
        return 2*np.einsum('pid,pi,p->d', B.conj(), p, weights).real

    dp = dual(Bp, p_parent, quad)
    dc = dual(Bc, p_child, quad*J)
    returned = dual(image, p_child, quad*J)
    projected_return = T.T @ dc
    # Riesz values are useful for consumers of the metric-paired transport
    # dual.  They are NOT raw canonical momentum coefficients.
    rp, rc = np.linalg.solve(Gp, dp), np.linalg.solve(Gc, dc)
    trace_coeff = hc-T@hp
    momentum = dp-returned
    residual = np.concatenate((_realify(app['trace_residual']), momentum))
    out = dict(
        transport_application=app,
        trace_residual=app['trace_residual'],
        trace_coefficient_residual=trace_coeff,
        canonical_parent_density=p_parent, canonical_child_density=p_child,
        parent_momentum_dual=dp, child_momentum_dual=dc,
        parent_momentum_riesz=rp, child_momentum_riesz=rc,
        exact_child_momentum_return=returned,
        projected_child_momentum_return=projected_return,
        unrepresented_momentum_return=returned-projected_return,
        momentum_residual=momentum,
        projected_momentum_residual=dp-projected_return,
        residual=residual, pairing='real_2Re',
        momentum_convention='positive-time p_H; outward parent +p_H, child -p_H',
        direct_fixed_geometry_surface_H_cotangent=0,
        scalar_event_load_role='produced from parent canonical unknowns, not supplied data',
        sampled_trace_equations_retained=True,
        finite_image_invariance_claim=False, physical_primal_claim=False)
    if not tangent:
        return out

    vpoints = (parent_birth_points_variation,
               transport['material_points_variation'][time_index])
    dB = []
    for side, velocity in zip(('parent', 'child'), vpoints):
        points, data = captured[side]
        velocity = _finite(velocity, f'{side} point variation')
        xi = np.einsum('pia,pi->pa', unit_s3_material_frame(points), velocity)
        dB.append(np.asarray(data['basis_variation'], complex)
                  + np.einsum('paid,pa->pid',
                              data['basis_spatial_derivatives'], xi))
    vBp, vBc = dB
    vJ = np.asarray(transport['haar_jacobian_variation'][time_index], float)
    dq = np.zeros_like(quad) if delta_quadrature is None else _finite(
        delta_quadrature, 'reference quadrature variation')
    if dq.shape != quad.shape:
        raise ValueError('reference quadrature direction shape mismatch')
    vimage = app['scalar_transport_image_variation']
    vGp, vGc, vT = (app[key].copy() for key in (
        'parent_pairing_variation', 'child_pairing_variation',
        'trace_transport_variation'))
    # The retained producer keeps reference quadrature fixed.  Add this
    # independent domain motion to its Gram/transport jets exactly once.
    if np.any(dq):
        parent_density = density_evaluator(
            'parent', captured['parent'][0], c, direction)['density']
        child_density = app['child_pulled_pairing_density']

        def pair(A, B, weights):
            return 2*np.einsum('pid,pie,p->de', A.conj(), B, weights).real

        qGp = pair(Bp, Bp, dq*np.asarray(parent_density))
        qGc = pair(Bc, Bc, dq*child_density)
        qK = pair(Bc, image, dq*child_density)
        vT += np.linalg.solve(Gc, qK-qGc@T)
        vGp += qGp
        vGc += qGc
    vpp, vpc = maps[2]@direction, maps[3]@direction
    vp_parent, vp_child = vBp@pp+Bp@vpp, vBc@pc+Bc@vpc
    vdp = (dual(vBp, p_parent, quad)+dual(Bp, vp_parent, quad)
           +dual(Bp, p_parent, dq))
    vdc = (dual(vBc, p_child, quad*J)+dual(Bc, vp_child, quad*J)
           +dual(Bc, p_child, dq*J+quad*vJ))
    vreturned = (dual(vimage, p_child, quad*J)
                 +dual(image, vp_child, quad*J)
                 +dual(image, p_child, dq*J+quad*vJ))
    vprojected = vT.T@dc+T.T@vdc
    vmomentum = vdp-vreturned
    out.update(
        trace_residual_variation=app['trace_residual_variation'],
        trace_coefficient_residual_variation=(maps[1]@direction
            -vT@hp-T@(maps[0]@direction)),
        parent_momentum_dual_variation=vdp,
        child_momentum_dual_variation=vdc,
        parent_momentum_riesz_variation=np.linalg.solve(Gp, vdp-vGp@rp),
        child_momentum_riesz_variation=np.linalg.solve(Gc, vdc-vGc@rc),
        exact_child_momentum_return_variation=vreturned,
        projected_child_momentum_return_variation=vprojected,
        unrepresented_momentum_return_variation=vreturned-vprojected,
        momentum_residual_variation=vmomentum,
        projected_momentum_residual_variation=vdp-vprojected,
        residual_variation=np.concatenate((
            _realify(app['trace_residual_variation']), vmomentum)))
    return out


def scalar_birth_action_jacobian(coefficients, row_application):
    """Assemble boundary columns using same-vector directional applications.

    ``row_application(c, direction)`` constructs the worldvolume transport
    and the rows above from c, with None for the base and each real unit
    direction for a tangent.  This consumes the actual boundary producer;
    it does not accept an incoming H trace/load packet or fabricate closure.
    """
    c = _finite(coefficients, 'common coefficients')
    if c.ndim != 1 or len(c) == 0:
        raise ValueError('nonempty common vector required')
    base = row_application(c, None)
    residual = _finite(base['residual'], 'birth residual')
    columns = []
    for j in range(len(c)):
        direction = np.zeros_like(c)
        direction[j] = 1
        column = _finite(row_application(c, direction)['residual_variation'],
                         'birth Jacobian column')
        if column.shape != residual.shape:
            raise ValueError('boundary columns must share one residual space')
        columns.append(column)
    return dict(residual=residual, jacobian=np.column_stack(columns),
                application=base, physical_primal_claim=False,
                square_system_claim=False)
