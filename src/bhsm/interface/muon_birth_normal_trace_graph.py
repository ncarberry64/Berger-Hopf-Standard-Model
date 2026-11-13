"""Exact reached material-normal affine trace graph in the same action.

The graph transports the incoming-minus-child mechanical connection profile
into the independent child connection.  Its value is anchored at the recorded
two-arm base, whereas every geometric first and second derivative remains
active.  Profiles are applied at quadrature points, never projected into a
radial coefficient space.  This is an admissible homogeneous graph trial;
it does not select a physical formation eigenline or certify the fixed-q base.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import (
    M, background_subtracted_maxwell_action_jet,
    full_maxwell_weak_geometric_jets, full_maxwell_gauge_hessian_matrix,
)
from .muon_birth_trace_enriched_action import pointwise_trace_enriched_action
from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_mean_causal_action import VOLUME, MAXWELL_TO_CAP


PROFILE_ORDER = ('connection_lambda', 'lambda_tau', 'lambda_rho')


def affine_connection_profile_two_jet(raw_pair, rho):
    """Return delta-lambda/value-time-radial jets on both geometry100 blocks.

    rho is the fixed material reference coordinate.  The underlying owner
    includes Eulerian coefficient motion plus embedding advection exactly
    once.  lambda_tau and lambda_rho are the actual pulled-back derivatives,
    not independently chosen profiles.  The reference frame is held fixed.
    """
    raw = np.asarray(raw_pair, float)
    if raw.ndim != 2 or raw.shape[0] != 2 or raw.shape[1] < 100 or not np.isfinite(raw).all():
        raise ValueError('finite incoming/child same-vector pair required')
    applications = [geometric_connection_coefficient_jets(
        12, x[:37], x[37:74], x[74:98], rho,
        source_value=x[98], source_rate=x[99]) for x in raw]
    n = len(applications[0]['rows'])
    value = np.empty((n, 3)); first = np.zeros((n, 3, 200))
    second = np.zeros((n, 3, 200, 200))
    for r, (parent, child) in enumerate(zip(applications[0]['rows'], applications[1]['rows'])):
        for k, name in enumerate(PROFILE_ORDER):
            p, c = parent[name], child[name]
            value[r, k] = p.value-c.value
            first[r, k, :100] = p.gradient; first[r, k, 100:] = -c.gradient
            second[r, k, :100, :100] = p.hessian
            second[r, k, 100:, 100:] = -c.hessian
    return dict(value=value, first=first, second=second, applications=applications,
        coordinate_order='incoming geometry100; child geometry100', profile_order=PROFILE_ORDER,
        material_advection_count=1, reference_radial_frame_varied=False)


def compose_action_two_jet(value, gradient, hessian, first_map, second_map):
    """Exact nonlinear pullback: J^T K J + sum_a G_a D2F_a.

    The contact is required off shell and is not a response of the fields.
    This helper has no normalization, sign, quotient or conditioning choice.
    """
    g, k, j, d2 = (np.asarray(x, float) for x in (gradient, hessian, first_map, second_map))
    if k.shape != (len(g), len(g)) or j.ndim != 2 or j.shape[0] != len(g) or d2.shape != (len(g), j.shape[1], j.shape[1]):
        raise ValueError('same action and nonlinear-map dimensions required')
    return dict(value=float(value), gradient=j.T@g,
        hessian=j.T@k@j+np.einsum('a,aij->ij', g, d2))


def _geometry_indices(raw_count):
    return np.r_[np.arange(100), raw_count+np.arange(100)]


def _field_applications(raw, rep, profile_increment):
    n = len(rep['gauge_labels']); b, br = rep['gauge_basis'], rep['gauge_radial_basis']
    fields = dict(gauge=np.einsum('rj...,j->r...', b, raw[100:100+n]),
        gauge_tau=np.einsum('rj...,j->r...', b, raw[100+n:100+2*n]),
        gauge_rho=np.einsum('rj...,j->r...', br, raw[100:100+n]),
        gauge_angular=np.zeros((len(b), 1, 3, 5, 4)))
    for k, name in enumerate(('gauge', 'gauge_tau', 'gauge_rho')):
        fields[name][:, 0, 2:] += profile_increment[:, k, None, None]*M
    return fields


def _gauge_test_maps(rep, first_profile):
    n = len(rep['gauge_labels']); r = len(rep['rho']); count = 2*n+200
    value = np.zeros((r, count, 1, 5, 4)); temporal = value.copy(); radial = value.copy()
    value[:, :n] = rep['gauge_basis']; radial[:, :n] = rep['gauge_radial_basis']
    temporal[:, n:2*n] = rep['gauge_basis']
    for k, target in enumerate((value, temporal, radial)):
        target[:, 2*n:, 0, 2:] = first_profile[:, k, :, None, None]*M
    return dict(tests=value, tests_tau=temporal, tests_rho=radial,
        tests_angular=np.zeros((r, count, 1, 3, 5, 4)))


def _local_profile_dual(geometry, rep, fields):
    """Local action duals to the THREE profile jets, with radial weight once."""
    r = len(rep['rho']); value = np.zeros((r, 3*r, 1, 5, 4))
    temporal = value.copy(); radial = value.copy()
    for p in range(r):
        value[p, 3*p, 0, 2:] = M
        temporal[p, 3*p+1, 0, 2:] = M
        radial[p, 3*p+2, 0, 2:] = M
    result = full_maxwell_weak_geometric_jets(geometry, rep['radial_quadrature'], np.ones(1),
        **fields, tests=value, tests_tau=temporal, tests_rho=radial,
        tests_angular=np.zeros((r, 3*r, 1, 3, 5, 4)))
    return result['weak']['values'].reshape(r, 3)


def normal_trace_graph_action_value(raw_pair, reference_pair, representation, *,
        nu_squared_action, surface_gamma=None):
    """Independent literal scalar action for directional derivative checks.

    This uses the action owners directly without the nonlinear chain-rule
    assembly.  It has the identical anchored profile/domain convention.
    """
    raw, ref = np.asarray(raw_pair, float), np.asarray(reference_pair, float)
    rep = representation; n = len(rep['gauge_labels']); nr = 108+2*n; hs = 100+2*n
    if raw.shape != (2, nr) or ref.shape != raw.shape:raise ValueError('same complete two-arm pair required')
    profile = affine_connection_profile_two_jet(raw, rep['rho'])
    reference = affine_connection_profile_two_jet(ref, rep['rho'])
    parent = pointwise_trace_enriched_action(raw[0], rep, nu_squared_action=nu_squared_action, surface_gamma=surface_gamma)
    child = raw[1]; q, v, m = child[:37], child[37:74], child[74:98]; s, sr = child[98:100]
    cap = moving_cap_action_jet(12, q, v, m, points=rep['cap_points'], source_value=s, source_rate=sr)
    fields = _field_applications(child, rep, profile['value']-reference['value'])
    delta = background_subtracted_maxwell_action_jet(profile['applications'][1], rep['radial_quadrature'], np.ones(1), **fields)
    wp = affine_connection_profile_two_jet(raw, np.array([WALL]))
    wr = affine_connection_profile_two_jet(ref, np.array([WALL]))
    wall = np.einsum('fcj,j->fc', rep['wall_trace_map'], child[100:100+n])
    wall[2:] += (wp['value'][0, 0]-wr['value'][0, 0])*M
    weights = intrinsic_m4_weight_jet(12, q, v, m, source_value=s, source_rate=sr)
    sv = np.zeros((1, 4, 8)); sd = np.zeros((1, 4, 4, 8))
    sv[0, :, :4] = np.eye(4); sd[0, 0, :, 4:] = np.eye(4)
    scalar = material_intrinsic_higgs_gauge_action_jet(weights,
        scalar_coefficients=child[hs:hs+8], scalar_value_map=sv, scalar_derivative_map=sd,
        gauge_coefficients=wall.reshape(20), gauge_trace_map=np.eye(20).reshape(1, 5, 4, 20),
        angular_quadrature=np.ones(1), lambda_H=rep['scalar_matching']['lambda_H'],
        nu_squared_action=nu_squared_action)['action']
    value = parent['value']+cap['total'].value+MAXWELL_TO_CAP*delta['value']+scalar.value/VOLUME**2
    if surface_gamma is not None:value += surface_gamma*cap['surface_per_gamma'].value
    return float(value)


def normal_trace_graph_action_two_jet(raw_pair, reference_pair, representation, *,
        nu_squared_action, surface_gamma=None):
    """Apply all graph first/second/internal contacts to the actual two-arm action.

    Independent child connection gains M*(delta-lambda(raw)-delta-lambda(ref)).
    The same rule is applied to its temporal/radial derivatives.  At the
    recorded base it is identically zero; its response is generally nonzero.
    The child Maxwell baseline subtraction is retained.  Scalar temporal
    trace is material At_ref once, while its spatial wall connection includes
    this exact graph image.  The parent action is unchanged.  Returned
    cotangents are raw real coefficient duals, with scalar 2Re already owned.
    """
    rep = representation; n = len(rep['gauge_labels']); nr = 108+2*n; hs = 100+2*n
    raw, ref = np.asarray(raw_pair, float), np.asarray(reference_pair, float)
    if raw.shape != (2, nr) or ref.shape != raw.shape or not np.isfinite(raw).all() or not np.isfinite(ref).all():
        raise ValueError('same complete two-arm fields/reference required')
    dim = 2*nr; gi = _geometry_indices(nr); child_geo = nr+np.arange(100)
    profile = affine_connection_profile_two_jet(raw, rep['rho'])
    reference = affine_connection_profile_two_jet(ref, rep['rho'])
    increment = profile['value']-reference['value']
    child = raw[1]; q, v, m = child[:37], child[37:74], child[74:98]; s, sr = child[98:100]
    parent = pointwise_trace_enriched_action(raw[0], rep, nu_squared_action=nu_squared_action, surface_gamma=surface_gamma)
    cap = moving_cap_action_jet(12, q, v, m, points=rep['cap_points'], source_value=s, source_rate=sr)
    fields = _field_applications(child, rep, increment)
    geometry = profile['applications'][1]
    delta = background_subtracted_maxwell_action_jet(geometry, rep['radial_quadrature'], np.ones(1), **fields)
    tests = _gauge_test_maps(rep, profile['first'])
    weak = full_maxwell_weak_geometric_jets(geometry, rep['radial_quadrature'], np.ones(1), **fields, **tests)
    gauge = full_maxwell_gauge_hessian_matrix(geometry, rep['radial_quadrature'], np.ones(1), **fields, **tests)
    local_dual = _local_profile_dual(geometry, rep, fields)
    source_contact = np.einsum('rk,rkij->ij', local_dual, profile['second'])
    T = np.zeros((2*n+200, dim)); T[:2*n, nr+100:nr+hs] = np.eye(2*n)
    T[2*n:, gi] = np.eye(200)
    g = np.zeros(dim); h = np.zeros((dim, dim)); value = parent['value']+cap['total'].value+MAXWELL_TO_CAP*delta['value']
    g[:nr] = parent['raw_gradient']; h[:nr, :nr] = parent['raw_hessian']
    g[child_geo] += cap['total'].gradient+MAXWELL_TO_CAP*delta['gradient']
    h[np.ix_(child_geo, child_geo)] += cap['total'].hessian+MAXWELL_TO_CAP*delta['hessian']
    g += MAXWELL_TO_CAP*T.T@weak['weak']['values']
    h += MAXWELL_TO_CAP*T.T@gauge['matrix']@T
    cross = MAXWELL_TO_CAP*T.T@weak['weak']['geometric_jacobian']
    h[:, child_geo] += cross; h[child_geo, :] += cross.T
    h[np.ix_(gi, gi)] += MAXWELL_TO_CAP*source_contact
    # Use the actual twenty wall one-form components as a temporary action
    # chart.  They are images of the SAME coefficients, not independent data.
    wp = affine_connection_profile_two_jet(raw, np.array([WALL]))
    wr = affine_connection_profile_two_jet(ref, np.array([WALL]))
    wall = np.einsum('fcj,j->fc', rep['wall_trace_map'], child[100:100+n])
    wall[2:] += (wp['value'][0, 0]-wr['value'][0, 0])*M
    weights = intrinsic_m4_weight_jet(12, q, v, m, source_value=s, source_rate=sr)
    sv = np.zeros((1, 4, 8)); sd = np.zeros((1, 4, 4, 8))
    sv[0, :, :4] = np.eye(4); sd[0, 0, :, 4:] = np.eye(4)
    wall_identity = np.eye(20).reshape(1, 5, 4, 20)
    scalar = material_intrinsic_higgs_gauge_action_jet(weights,
        scalar_coefficients=child[hs:hs+8], scalar_value_map=sv, scalar_derivative_map=sd,
        gauge_coefficients=wall.reshape(20), gauge_trace_map=wall_identity,
        angular_quadrature=np.ones(1), lambda_H=rep['scalar_matching']['lambda_H'],
        nu_squared_action=nu_squared_action)['action']
    S = np.zeros((128, dim)); S[:100, child_geo] = np.eye(100)
    S[100:108, nr+hs:nr+hs+8] = np.eye(8)
    S[108:, nr+100:nr+100+n] = rep['wall_trace_map'].reshape(20, n)
    wall_profile_map = np.zeros((20, 200)); wall_profile_map.reshape(5, 4, 200)[2:] = M[:, :, None]*wp['first'][0, 0]
    S[108:, gi] += wall_profile_map
    value += scalar.value/VOLUME**2; g += S.T@scalar.gradient/VOLUME**2; h += S.T@scalar.hessian@S/VOLUME**2
    wall_dual = float(np.sum(scalar.gradient[108:].reshape(5, 4)[2:]*M))
    h[np.ix_(gi, gi)] += wall_dual*wp['second'][0, 0]/VOLUME**2
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma) or surface_gamma <= 0:raise ValueError('assigned area coefficient must be positive')
        value += surface_gamma*cap['surface_per_gamma'].value
        g[child_geo] += surface_gamma*cap['surface_per_gamma'].gradient
        h[np.ix_(child_geo, child_geo)] += surface_gamma*cap['surface_per_gamma'].hessian
    normal = np.zeros(dim); normal[[98, nr+98]] = 1.
    rate = np.zeros(dim); rate[[99, nr+99]] = 1.
    directions = np.column_stack((normal, rate))
    area_g = np.zeros(dim); area_h = np.zeros((dim, dim))
    area_g[:100] = parent['surface_gradient_per_gamma']
    area_h[:100, :100] = parent['surface_hessian_per_gamma']
    area_g[child_geo] = cap['surface_per_gamma'].gradient
    area_h[np.ix_(child_geo, child_geo)] = cap['surface_per_gamma'].hessian
    return dict(value=float(value), raw_gradient=g, raw_hessian=h,
        profile_increment=increment, profile_first=profile['first'], profile_second=profile['second'],
        profile_local_action_dual=MAXWELL_TO_CAP*local_dual,
        profile_second_action_contact=MAXWELL_TO_CAP*source_contact,
        scalar_wall_second_action_contact=wall_dual*wp['second'][0, 0]/VOLUME**2,
        normal_trial_directions=directions, normal_first=directions.T@g,
        normal_mixed=directions.T@h, normal_second=directions.T@h@directions,
        surface_value_per_gamma=parent['surface_value_per_gamma']+cap['surface_per_gamma'].value,
        surface_gradient_per_gamma=area_g, surface_hessian_per_gamma=area_h,
        normal_surface_first_per_gamma=directions.T@area_g,
        normal_surface_mixed_per_gamma=directions.T@area_h,
        normal_surface_second_per_gamma=directions.T@area_h@directions,
        normal_scope='common proper-amplitude lateral material-wall trial at birth; not temporal E1 Cauchy normal or selected mechanical mode',
        graph_scope='anchored homogeneous affine mechanical-connection trace graph; parent/child q and all internal jets active; fixed computational radial frame',
        spatial_normal_orientation='increasing chi, +Cstar^-1 partial_chi; spacelike conormal raising has opposite sign in +---',
        temporal_normal='induced_lapse^-1 partial_t distinct from lateral material normal',
        material_advection_count=1, all_Gauss_and_multiplier_coordinates_retained=True,
        source_image_projected=False, full_stationary_birth_or_physical_formation_selected=False,
        surface_gamma=surface_gamma)


def materialize_normal_trace_graph(initial_application, output, *, repository=None,
        quadrature_orders=(48, 64, 96)):
    """Evaluate the actual reached graph and quadrature refinements twice externally.

    The two pointwise Lagrangians are added only to record this local action
    application; that sum is not an integrated temporal junction action or
    the formation Hessian.  The current full220 base is preserved unchanged.
    """
    from .muon_birth_attached_phase import load_attached_endpoint
    from .muon_parent_gauge_geometry_correction import ROOT
    from .muon_birth_phase_continuation import _compressed_npz
    root = ROOT if repository is None else Path(repository); out = Path(output)
    if out.exists():raise FileExistsError('preserve prior application')
    orders = tuple(int(x) for x in quadrature_orders)
    if not orders or any(x < 48 for x in orders):raise ValueError('resolved inherited cap quadrature orders required')
    records = []; first_application = first_input = None
    for points in orders:
        p = load_attached_endpoint(initial_application, side='incoming', repository=root, radial_points=points, cap_points=points)
        c = load_attached_endpoint(initial_application, side='outgoing', repository=root, radial_points=points, cap_points=points)
        raw = np.array([p['raw'], c['raw']]); rep = p['representation']; parameters = p['receipt']['action_parameters']
        a = normal_trace_graph_action_two_jet(raw, raw, rep, **parameters)
        direction = np.zeros(200); direction[[98, 198]] = 1.
        image = a['profile_first'][:, 0]@direction
        b, weights = rep['radial_value_map'], rep['radial_quadrature']
        coeff = np.linalg.lstsq(np.sqrt(weights)[:, None]*b, np.sqrt(weights)*image, rcond=None)[0]
        complement = image-b@coeff
        records.append(dict(points=points, value=a['value'], normal_first=a['normal_first'].tolist(),
            normal_second=a['normal_second'].tolist(), normal_mixed_norm=float(np.linalg.norm(a['normal_mixed'])),
            normal_surface_first_per_gamma=a['normal_surface_first_per_gamma'].tolist(),
            normal_surface_second_per_gamma=a['normal_surface_second_per_gamma'].tolist(),
            source_image_L2_norm=float(np.sqrt(weights@(image*image))),
            unreached_radial_image_complement_L2_norm=float(np.sqrt(weights@(complement*complement))),
            normal_profile_projection_diagnostic=coeff.tolist(), projection_consumed_in_action=False,
            nonlinear_profile_contact_norm=float(np.linalg.norm(a['profile_second_action_contact'])),
            scalar_wall_profile_contact_norm=float(np.linalg.norm(a['scalar_wall_second_action_contact'])),
            Hessian_symmetry_defect=float(np.max(abs(a['raw_hessian']-a['raw_hessian'].T)))))
        if first_application is None:first_application = a; first_input = p; first_rep = rep; first_raw = raw
    a = first_application; raw = first_raw; rep = first_rep
    fd = []; direction = a['normal_trial_directions'][:, 0].reshape(raw.shape)
    for step in (5e-5, 2.5e-5):
        p = normal_trace_graph_action_value(raw+step*direction, raw, rep, **parameters)
        m = normal_trace_graph_action_value(raw-step*direction, raw, rep, **parameters)
        first = (p-m)/(2*step); second = (p-2*a['value']+m)/step**2
        fd.append(dict(step=step, first=first, second=second,
            first_defect=abs(first-a['normal_first'][0]), second_defect=abs(second-a['normal_second'][0, 0])))
    hashes = dict(first_input['receipt']['input_hashes'])
    for path in ('src/bhsm/interface/muon_birth_normal_trace_graph.py', 'src/bhsm/interface/muon_birth_attached_phase.py'):
        hashes[path] = sha256((root/path).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    arrays = dict(raw_pair=raw, raw_gradient=a['raw_gradient'], raw_hessian=a['raw_hessian'],
        normal_directions=a['normal_trial_directions'], normal_first=a['normal_first'],
        normal_mixed=a['normal_mixed'], normal_second=a['normal_second'],
        rho=rep['rho'], radial_quadrature=rep['radial_quadrature'],
        profile_first=a['profile_first'], profile_increment=a['profile_increment'],
        profile_local_action_dual=a['profile_local_action_dual'],
        profile_second_action_contact=a['profile_second_action_contact'],
        scalar_wall_second_action_contact=a['scalar_wall_second_action_contact'])
    arrays.update(surface_value_per_gamma=np.array(a['surface_value_per_gamma']),
        surface_gradient_per_gamma=a['surface_gradient_per_gamma'], surface_hessian_per_gamma=a['surface_hessian_per_gamma'],
        normal_surface_first_per_gamma=a['normal_surface_first_per_gamma'],
        normal_surface_mixed_per_gamma=a['normal_surface_mixed_per_gamma'],
        normal_surface_second_per_gamma=a['normal_surface_second_per_gamma'])
    _compressed_npz(out/'application.npz', arrays)
    md = dict(scope='EVALUATED_EXACT_REACHED_MATERIAL_NORMAL_TRACE_GRAPH_ACTION_APPLICATION',
        initial_application=Path(initial_application).as_posix(), consumed_receipt_sha256=first_input['receipt_sha256'],
        consumed_coefficients_sha256=first_input['receipt']['numerical_sha256'], input_hashes=hashes,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=parameters, reference_pair_value_preserved=True, graph_profile_projected=False,
        quadrature_refinements=records, literal_action_finite_difference=fd,
        normal_scope=a['normal_scope'], graph_scope=a['graph_scope'],
        spatial_normal_orientation=a['spatial_normal_orientation'], temporal_normal=a['temporal_normal'],
        material_advection_count=1, all_internal_Gauss_and_multiplier_jets_retained=True,
        temporal_junction_action_assembled=False, physical_formation_Hessian_evaluated=False,
        selected_mechanical_normal_section=False, fixed_q_physical_closure_assumed=False,
        physical_native_heat_closed=False, physical_Pauli_value=False,
        shared_equations='gamma=alpha_FSC*ell_current^(-m); GF=cF/E_kappa^2; H_form simple oriented crossing with event drive remain common equations, not fitted here',
        error_scope='binary64 action/analytic twojets with quadrature and centered action differences; no rigorous continuum/rounding enclosure')
    (out/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return md


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial-application', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quadrature-orders', type=int, nargs='+', default=[48, 64, 96])
    args = parser.parse_args()
    print(json.dumps(materialize_normal_trace_graph(args.initial_application, args.output,
        quadrature_orders=args.quadrature_orders), sort_keys=True))
