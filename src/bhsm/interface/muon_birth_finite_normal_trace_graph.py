"""Same-action two-arm graph on the exact finite anchored material trial.

The two-harmonic chart is determined by its owned f/sigma wall traces.
This isolated continuation replaces the old quadratic response only; all
Maxwell/Gauss, scalar, profile and second-map contacts are retained.  It
selects neither a physical normal eigenline nor a stationary birth.
"""
from __future__ import annotations
import numpy as np
from .muon_exact_material_response import (
    exact_geometric_connection_coefficient_jets as geometric_connection_coefficient_jets,
    exact_moving_cap_action_jet as moving_cap_action_jet,
)
from .muon_parent_maxwell_full_weak import (
    M, background_subtracted_maxwell_action_jet,
    full_maxwell_weak_geometric_jets, full_maxwell_gauge_hessian_matrix,
)
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_normal_trace_graph import (
    compose_action_two_jet, _geometry_indices, _field_applications,
    _gauge_test_maps, _local_profile_dual,
)
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



def pointwise_finite_normal_action(raw_coefficients,representation,*,nu_squared_action,surface_gamma=None):
    """Literal raw(100+2*N+8) action; all first/second and mixed rows."""
    rep=representation;N=len(rep['gauge_labels']);raw=np.asarray(raw_coefficients,float);nr=108+2*N;hs=100+2*N
    if raw.shape!=(nr,) or not np.isfinite(raw).all():raise ValueError('finite enlarged same coefficient vector required')
    if not np.isfinite(nu_squared_action) or nu_squared_action<0:raise ValueError('explicit nonnegative scalar action parameter required')
    q,v,m=raw[:37],raw[37:74],raw[74:98];s,sr=raw[98:100];a,at=raw[100:100+N],raw[100+N:100+2*N];H,Ht=raw[hs:hs+4],raw[hs+4:]
    cap=moving_cap_action_jet(12,q,v,m,points=rep['cap_points'],source_value=s,source_rate=sr)
    geo=geometric_connection_coefficient_jets(12,q,v,m,rep['rho'],source_value=s,source_rate=sr)
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis'];count=len(gb)
    tv=np.zeros((count,2*N,1,5,4));tt=tv.copy();tr=tv.copy();ta=np.zeros((count,2*N,1,3,5,4))
    tv[:,:N]=gb;tr[:,:N]=gr;tt[:,N:]=gb
    fields=dict(gauge=np.einsum('rj...,j->r...',gb,a),gauge_tau=np.einsum('rj...,j->r...',gb,at),
        gauge_rho=np.einsum('rj...,j->r...',gr,a),gauge_angular=np.zeros((count,1,3,5,4)))
    tests=dict(tests=tv,tests_tau=tt,tests_rho=tr,tests_angular=ta)
    delta=background_subtracted_maxwell_action_jet(geo,rep['radial_quadrature'],np.ones(1),**fields)
    weak=full_maxwell_weak_geometric_jets(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    gauge=full_maxwell_gauge_hessian_matrix(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    G=np.zeros(nr);K=np.zeros((nr,nr));value=cap['total'].value+MAXWELL_TO_CAP*delta['value']
    G[:100]=cap['total'].gradient+MAXWELL_TO_CAP*delta['gradient'];K[:100,:100]=cap['total'].hessian+MAXWELL_TO_CAP*delta['hessian']
    G[100:hs]=MAXWELL_TO_CAP*weak['weak']['values'];K[100:hs,100:hs]=MAXWELL_TO_CAP*gauge['matrix']
    cross=MAXWELL_TO_CAP*weak['weak']['geometric_jacobian'];K[100:hs,:100]=cross;K[:100,100:hs]=cross.T
    weights=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
    sv=np.zeros((1,4,8));sd=np.zeros((1,4,4,8));sv[0,:,:4]=np.eye(4);sd[0,0,:,4:]=np.eye(4)
    scalar=material_intrinsic_higgs_gauge_action_jet(weights,scalar_coefficients=np.r_[H,Ht],scalar_value_map=sv,scalar_derivative_map=sd,
        gauge_coefficients=a,gauge_trace_map=rep['wall_trace_map'][None],angular_quadrature=np.ones(1),
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)['action']
    S=np.zeros((108+N,nr));S[:100,:100]=np.eye(100);S[100:108,hs:hs+8]=np.eye(8);S[108:,100:100+N]=np.eye(N)
    value+=scalar.value/VOLUME**2;G+=S.T@scalar.gradient/VOLUME**2;K+=S.T@scalar.hessian@S/VOLUME**2
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma) or surface_gamma<=0:raise ValueError('assigned area coefficient must be positive')
        value+=surface_gamma*cap['surface_per_gamma'].value;G[:100]+=surface_gamma*cap['surface_per_gamma'].gradient;K[:100,:100]+=surface_gamma*cap['surface_per_gamma'].hessian
    coordinates=generic_coordinate_lift(rep['gauge_labels']);P=coordinates['lift'];g=P.T@G;k=P.T@K@P;nx=coordinates['x_count']
    return dict(value=float(value),raw_gradient=G,raw_hessian=K,gradient=g,hessian=k,coordinates=coordinates,
        Lxx=k[:nx,:nx],Lxv=k[:nx,nx:2*nx],Lxy=k[:nx,2*nx:],Lvx=k[nx:2*nx,:nx],Lvv=k[nx:2*nx,nx:2*nx],Lvy=k[nx:2*nx,2*nx:],
        Lyx=k[2*nx:,:nx],Lyv=k[2*nx:,nx:2*nx],Lyy=k[2*nx:,2*nx:],
        surface_value_per_gamma=cap['surface_per_gamma'].value,surface_gradient_per_gamma=cap['surface_per_gamma'].gradient,
        surface_hessian_per_gamma=cap['surface_per_gamma'].hessian,full_stationary_birth_or_native_Pauli_established=False)



def finite_normal_trace_graph_action_value(raw_pair, reference_pair, representation, *,
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
    parent = pointwise_finite_normal_action(raw[0], rep, nu_squared_action=nu_squared_action, surface_gamma=surface_gamma)
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


def finite_normal_trace_graph_action_two_jet(raw_pair, reference_pair, representation, *,
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
    parent = pointwise_finite_normal_action(raw[0], rep, nu_squared_action=nu_squared_action, surface_gamma=surface_gamma)
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

