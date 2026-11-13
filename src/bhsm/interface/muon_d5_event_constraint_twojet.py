"""Actual E1 connection-constraint curvature and known weak action contacts.

This is a coefficient application in the original field chart. Constraint
multipliers, physical outer data, native/state loads and fermionic boundary
coordinates remain unknown. No multiplier is fitted to a classical load.
"""
from __future__ import annotations

import numpy as np

from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from .muon_actual_normal_shape_source import (
    proper_normal_shape_coefficient, mixed_normal_shape_weak_source,
)
from .muon_d5_event_formation_constraints import proper_normal_coordinate_columns
from .muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from .muon_d5_spatial_bundle_application import cross_matrix, spatial_connection_row
from .muon_holomorphic_normal_geometry import (
    _geometry_variables, _fields, _sqrt, holomorphic_geometry_rows,
    holomorphic_cap_and_weights,
)
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


# Five literal geometry streams: current parent, current child, inherited
# born parent, anchored parent reference, anchored child reference. The
# independent wall one-forms retain At/Ar alongside all spatial entries.
GEOMETRY_STREAMS = ('parent', 'child', 'born_parent', 'reference_parent', 'reference_child')
CHART_SIZE = 546
PARENT_WALL = slice(500, 520)
CHILD_WALL = slice(520, 540)
BASE_ROTATION = slice(540, 543)
GAUGE_ROTATION = slice(543, 546)


def _real(a, name):
    a = np.asarray(a)
    if np.iscomplexobj(a) and np.any(a.imag != 0):
        raise ValueError('real original '+name+' required; no projection is allowed')
    a = np.asarray(a.real if np.iscomplexobj(a) else a, float)
    if not np.isfinite(a).all():
        raise ValueError('finite '+name+' required')
    return a


def _radius_squared(raw):
    q, v, m, _, _, wall, _ = _geometry_variables(raw[:100])
    f = _fields(12, q, v, m, wall)
    return (f['A']*f['B'])**2/(f['A']**2+f['B']**2)


def _wall_map(history):
    b = np.asarray(history.gauge_basis(np.array([WALL])))
    if b.shape != (1, 20, 80):
        raise ValueError('actual original full80-to-wall20 gauge map required')
    return _real(b[0], 'wall gauge map')


def _transform(a, O, R):
    return np.column_stack((O.T@a[:, :3]@R.T, O.T@a[:, 3]))


def event_constraint_twojet(geometry_streams, independent_wall_connections,
        base_rotation, gauge_rotation):
    """Evaluate radius² plus all12 spatial connection rows and their two-jet.

    The rotation charts are O=O0 exp(Omega_b), R=exp(Omega_g) R0.
    Both candidates' O0/R0 are supplied from actual value equations, never
    inferred from a fermion residual. The full546 chart remains explicit.
    """
    raw = _real(geometry_streams, 'five geometry streams')
    independent = _real(independent_wall_connections, 'independent wall one-forms')
    O, R = (_real(a, 'SO3 factor') for a in (base_rotation, gauge_rotation))
    if raw.shape != (5, 100) or independent.shape != (2, 5, 4):
        raise ValueError('five geometry100 streams and two full wall5x4 one-forms required')
    if O.shape != (3, 3) or R.shape != (3, 3):
        raise ValueError('actual base and gauge rotations required')
    if max(np.max(abs(a.T@a-np.eye(3))) for a in (O, R)) > 2e-12 or min(np.linalg.det(O), np.linalg.det(R)) < 0:
        raise ValueError('orientation-preserving orthogonal value factors required')
    lambdas = [holomorphic_geometry_rows(x, [WALL], connection_only=True)['rows'][0]['connection_lambda']
        for x in raw]
    lam = np.array([a.value for a in lambdas])
    parent = independent[0, 2:].copy()+M*(lam[0]-1)
    child = independent[1, 2:].copy()+M*(lam[2]-lam[3]+lam[4]-1)
    values = np.zeros(13, complex)
    J = np.zeros((13, CHART_SIZE), complex)
    H = np.zeros((13, CHART_SIZE, CHART_SIZE), complex)
    rp, rc = (_radius_squared(x) for x in raw[:2])
    values[0] = rc.value-rp.value
    for stream, jet, sign in ((0, rp, -1), (1, rc, 1)):
        sl = slice(100*stream, 100*(stream+1))
        J[0, sl] = sign*jet.gradient
        H[0, sl, sl] = sign*jet.hessian
    values[1:] = spatial_connection_row(parent, child, O, R)
    # Each stream remains independent, including born/reference geometry.
    factors = {0: -_transform(M, O, R), 2: M, 3: -M, 4: M}
    for stream, factor in factors.items():
        sl = slice(100*stream, 100*(stream+1))
        f = factor.ravel()
        J[1:, sl] = f[:, None]*lambdas[stream].gradient[None]
        H[1:, sl, sl] = f[:, None, None]*lambdas[stream].hessian[None]
    for k in range(12):
        e = np.zeros((3, 4)); e.ravel()[k] = 1
        J[1:, 508+k] = -_transform(e, O, R).ravel()
        J[1+k, 528+k] = 1
    target = _transform(parent, O, R)
    basis = [cross_matrix(e) for e in np.eye(3)]
    for i, L in enumerate(basis):
        J[1:, 540+i] = (L@target).ravel()
        a = np.zeros((3, 4), complex); a[:, :3] = target[:, :3]@L
        J[1:, 543+i] = a.ravel()
        for j, P in enumerate(basis):
            sym = (L@P+P@L)/2
            H[1:, 540+i, 540+j] = (-sym@target).ravel()
            a = np.zeros((3, 4), complex); a[:, :3] = -target[:, :3]@sym
            H[1:, 543+i, 543+j] = a.ravel()
            a = np.zeros((3, 4), complex); a[:, :3] = -L@target[:, :3]@P
            H[1:, 540+i, 543+j] = H[1:, 543+j, 540+i] = a.ravel()
        # Rotation/field and rotation/geometric mixed placements follow
        # from the literal transformed PARENT operand; child is independent.
        for column in list(range(100))+list(range(508, 520)):
            if column < 100:
                dp = M*lambdas[0].gradient[column]
            else:
                dp = np.zeros((3, 4)); dp.ravel()[column-508] = 1
            dp = _transform(dp, O, R)
            b = (L@dp).ravel()
            H[1:, 540+i, column] = H[1:, column, 540+i] = b
            b = np.zeros((3, 4), complex); b[:, :3] = dp[:, :3]@L
            H[1:, 543+i, column] = H[1:, column, 543+i] = b.ravel()
    return dict(value=values, gradient=J, hessian=H,
        parent_total_spatial_connection=parent, child_total_spatial_connection=child,
        chart_geometry_streams=raw, chart_independent_wall_connections=independent,
        base_rotation=O, gauge_rotation=R)


def known_action_normal_contacts(history, source_directions, source_time_directions, *, cap_points):
    """Apply the exact known geometry action to actual normal source slots.

    The recorded reference Casimir is removed algebraically in this new
    E1 application; no local Maxwell/Higgs functional is inserted. The
    native/reference replacement, phase, state and domain actions stay
    separate unknown terms. The result is a weak action coefficient,
    rather than a completed Euler/formation Hessian or a physical force.
    """
    raw, rate = history.value(0.)
    raw, rate = _real(raw, 'E1 raw268'), _real(rate, 'original coordinate rate268')
    directions = _real(source_directions, 'source directions')
    direction_times = _real(source_time_directions, 'source coordinate-time derivatives')
    if directions.ndim != 2 or directions.shape[1] != 268 or direction_times.shape != directions.shape:
        raise ValueError('explicit complete source268 and source-time268 rows required')
    if not isinstance(cap_points, (int, np.integer)) or cap_points < 24:
        raise ValueError('explicit original action cap quadrature from its pinned receipt required')
    points = int(cap_points)
    cap = holomorphic_cap_and_weights(raw[:100], points=points)
    q, v, m, _, _, wall, _ = _geometry_variables(raw[:100])
    fields = _fields(12, q, v, m, wall)
    radius = fields['A']*fields['B']/_sqrt(fields['A']**2+fields['B']**2)
    removed_reference = standard_model_casimir_coefficient()*fields['N']/radius
    known = cap['total']+removed_reference
    P = history.original_phase_operands['resolved_phase_coordinate_lift']
    a = proper_normal_shape_coefficient(raw, P)
    sector = {}
    for name, action in (('known_geometry', known), ('surface_per_gamma', cap['surface_per_gamma'])):
        rows = []; weak = []; rate_rows = []; shape_values = []
        for psi, psit in ((1., 0.), (0., 1.)):
            applied = mixed_normal_shape_weak_source(action.gradient, action.hessian, rate[:100],
                a['value'], a['raw_gradient'], a['raw_hessian'], normal_position=98,
                normal_velocity=99, amplitude=psi, amplitude_coordinate_first=psit)
            state, phase_rate = (applied[k] for k in ('full_weak_state_source', 'full_weak_phase_rate_source'))
            rows.append(state); rate_rows.append(phase_rate); shape_values.append(applied['shape_action_first'])
            weak.append(state@directions[:, :100].T+phase_rate@direction_times[:, :100].T)
        sector[name+'_action_value'] = np.array(action.value)
        sector[name+'_raw_gradient100'] = action.gradient
        sector[name+'_raw_Hessian100'] = action.hessian
        sector[name+'_normal_weak_state_rows'] = np.array(rows)
        sector[name+'_normal_weak_phase_rate_rows'] = np.array(rate_rows)
        sector[name+'_normal_first_action_coefficients'] = np.array(shape_values)
        sector[name+'_actual_source_weak_Jacobi_contacts'] = np.array(weak)
    sector['exact_reference_removal_value'] = np.array(removed_reference.value)
    sector['ambient_lapse'] = np.array(fields['N'].value)
    sector['induced_lapse'] = np.array(cap['N'].value)
    return sector


def constraint_normal_stationarity_contact(twojet, normal_basis, normal_basis_source, source):
    """Return C_psi^T lambda and its complete supplied-direction coefficient.

    D(C_psi^T lambda)=(B^T C_zz Xi+(D_Xi B)^T C_z)lambda
    +C_psi^T Dlambda. Both multiplier slots remain unassigned.
    """
    J, H = twojet['gradient'], twojet['hessian']
    B, Bx, xi = map(np.asarray, (normal_basis, normal_basis_source, source))
    if B.shape != (CHART_SIZE, 4) or Bx.shape != B.shape or xi.shape != (CHART_SIZE,):
        raise ValueError('all four mechanical columns, their source and complete chart source required')
    source_hessian = np.einsum('kij,j->ki', H, xi)
    first = B.T@J.T
    curvature = B.T@source_hessian.T
    frame = Bx.T@J.T
    return dict(normal_constraint_multiplier_coefficients=first,
        normal_constraint_multiplier_source_curvature=curvature,
        normal_constraint_multiplier_source_frame=frame,
        normal_constraint_multiplier_complete_source=curvature+frame,
        normal_constraint_multiplier_first_variation_coefficient=first.copy(),
        normal_constraint_Jacobi_load=J@xi,
        raw_constraint_hessian_times_source=source_hessian,
        normal_raw_Hessian_multiplier_coefficients=np.einsum('ia,kij,jb->kab', B, H, B))


def two_sided_constraint_application(parent_history, child_history, spatial_arrays,
        original_normal_pivots, *, action_cap_points, candidate_indices=(2, 3)):
    """Execute two actual value-compatible connection branches separately.

    All source amplitudes are derivative coefficients of the previous
    provisional response. Free psi-time, rotation, outer and h coordinates
    remain represented separately and are not physical zero data.
    """
    histories = (parent_history, child_history)
    own = [_real(h.value(0.)[0], 'E1 raw') for h in histories]
    rate = [_real(h.value(0.)[1], 'E1 rate') for h in histories]
    wall_maps = [_wall_map(h) for h in histories]
    independent = np.array([(b@x[100:180]).reshape(5, 4) for b, x in zip(wall_maps, own)])
    operands = child_history.original_phase_operands
    geometry = np.array([own[0][:100], own[1][:100], operands['initial_pair'][0, :100],
        operands['reference_pair'][0, :100], operands['reference_pair'][1, :100]])
    norm = [proper_normal_shape_coefficient(x, h.original_phase_operands['resolved_phase_coordinate_lift'])
        for x, h in zip(own, histories)]
    B = np.zeros((CHART_SIZE, 4), complex)
    for side, h in enumerate(histories):
        B[100*side:100*(side+1), 2*side:2*side+2] = proper_normal_coordinate_columns(
            own[side], rate[side], h.original_phase_operands['resolved_phase_coordinate_lift'])['raw_normal_columns'][:100]
    psi = _real(original_normal_pivots, 'executed proper-normal source pivots')
    if psi.shape != (2,):
        raise ValueError('two saved normal source coefficients required')
    old = [tuple(_real(v, 'original Xi') for v in h.source(0.)) for h in histories]
    normal = [tuple(_real(v, 'normal corrected Xi') for v in ProvisionalNormalSourceHistory(h, p).source(0.))
        for h, p in zip(histories, psi)]
    # A spatial field correction has no geometry component and the known
    # bare sector has no independent wall-gauge argument. Evaluate each
    # identical E1 action once, retaining its whole two-jet for both branches.
    known_actions = [known_action_normal_contacts(h,
        np.array([before[0], after[0], after[0]]),
        np.array([before[1], after[1], after[1]]), cap_points=action_cap_points)
        for h, before, after in zip(histories, old, normal)]
    out = dict(normal_coordinate_basis=B, geometry_streams=geometry,
        independent_wall_connections=independent, candidate_indices=np.array(candidate_indices),
        parent_wall_gauge_map20x80=wall_maps[0], child_wall_gauge_map20x80=wall_maps[1])
    reports = []
    for candidate in candidate_indices:
        O, R = (spatial_arrays[k][candidate] for k in ('base_rotations', 'gauge_rotations'))
        jets = event_constraint_twojet(geometry, independent, O, R)
        raw_source = [row[0].copy() for row in normal]
        raw_time = [row[1].copy() for row in normal]
        raw_source[1] += spatial_arrays['child_raw_field_source_corrections'][candidate]
        if not np.array_equal(raw_source[1][:100], normal[1][0][:100]):
            raise ValueError('this known-action cache requires the field correction to hold geometry fixed')
        xi = np.zeros(CHART_SIZE, complex); Bx = np.zeros_like(B)
        for side in range(2):
            xi[100*side:100*(side+1)] = raw_source[side][:100]
            xi[500+20*side:520+20*side] = wall_maps[side]@raw_source[side][100:180]
            a = norm[side]; d = raw_source[side][:100]; dt = raw_time[side][:100]
            ax = a['raw_gradient']@d
            atx = d@a['raw_hessian']@rate[side][:100]+a['raw_gradient']@dt
            Bx[100*side+98, 2*side] = Bx[100*side+99, 2*side+1] = ax
            Bx[100*side+99, 2*side] = atx
        for stream in range(2, 5):
            x = geometry[stream]; xi[100*stream:100*(stream+1)][:37] = x[37:74]
            xi[100*stream+98] = x[99]
        app = constraint_normal_stationarity_contact(jets, B, Bx, xi)
        # A literal field/geometry pivot describes the entire finite
        # constraint kernel. It fixes no free coordinate or physical state.
        pivot_columns = np.r_[100, np.arange(528, 540)]
        free_columns = np.array(sorted(set(range(CHART_SIZE))-set(pivot_columns)))
        pivot = jets['gradient'][:, pivot_columns]
        kernel = np.eye(CHART_SIZE, dtype=complex)[:, free_columns]
        kernel[pivot_columns] = -np.linalg.solve(pivot, jets['gradient'][:, free_columns])
        free_rotation_source = np.zeros((CHART_SIZE, 6), complex)
        free_rotation_source[540:546] = np.eye(6)
        raw_rotation_fields = spatial_arrays['child_raw_field_free_rotation_coefficients'][candidate]
        free_rotation_source[520:540] = wall_maps[1]@raw_rotation_fields[100:180]
        rotation_curvature = np.einsum('ia,kij,jb->bak', B, jets['hessian'], free_rotation_source)
        prefix = 'candidate_'+str(candidate)+'_'
        out.update({prefix+k: v for k, v in jets.items()})
        out.update({prefix+k: v for k, v in app.items()})
        out[prefix+'normal_basis_source'] = Bx
        out[prefix+'actual_chart_source'] = xi
        out[prefix+'actual_own_raw_sources'] = np.array(raw_source)
        out[prefix+'actual_own_raw_source_time'] = np.array(raw_time)
        out[prefix+'constraint_pivot_columns'] = pivot_columns
        out[prefix+'constraint_free_columns'] = free_columns
        out[prefix+'constraint_kernel_all533_free_coordinates'] = kernel
        out[prefix+'constraint_kernel_original_rows'] = jets['gradient']@kernel
        out[prefix+'free_rotation_chart_source_coefficients'] = free_rotation_source
        out[prefix+'free_rotation_original_constraint_rows'] = jets['gradient']@free_rotation_source
        out[prefix+'normal_multiplier_curvature_free_rotation_coefficients'] = rotation_curvature
        for side, action in enumerate(known_actions):
            out.update({prefix+GEOMETRY_STREAMS[side]+'_'+k: v for k, v in action.items()})
        # The child12 wall slots are literal identity columns; the radius
        # row has an independent nonzero geometry covector. No kernel is
        # promoted into gauge data and no spectral coordinates are deleted.
        child_pivot = jets['gradient'][1:, 528:540]
        if not np.array_equal(child_pivot, np.eye(12)):
            raise ArithmeticError('original child12 wall field pivot changed')
        reports.append(dict(candidate_index=int(candidate),
            original_constraint_value_max=float(np.max(abs(jets['value']))),
            actual_constraint_source_max=float(np.max(abs(app['normal_constraint_Jacobi_load']))),
            multiplier_source_curvature_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_source_curvature']))),
            multiplier_source_frame_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_source_frame']))),
            full_multiplier_source_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_complete_source']))),
            exact_constraint_kernel_row_max=float(np.max(abs(jets['gradient']@kernel))),
            free_rotation_constraint_row_max=float(np.max(abs(jets['gradient']@free_rotation_source))),
            independent_connection_field_rows=12, radius_geometry_row_nonzero=bool(np.max(abs(jets['gradient'][0])) > 0),
            constraint_rank_in_declared546_chart=13, unconstrained_coordinate_dimension_in_declared_chart=CHART_SIZE-13))
    report = dict(classification='EVALUATED_TWO_SIDED_ORIGINAL_CONSTRAINT_CURVATURE_AND_KNOWN_WEAK_ACTION_CONTACT',
        chart_size=CHART_SIZE, chart_order='five geometry100 streams; parent20 and child20 wall one-forms; base3 and gauge3 infinitesimal rotations',
        geometry_stream_order=list(GEOMETRY_STREAMS), candidate_reports=reports,
        actual_constraint='R_child²−R_parent²=0 and [C_child−O.T C_parent R.T, y_child−O.T y_parent]=0',
        executed_stationarity_contact='D(C_psi.T lambda)=[B.T C_zz Xi+(D_Xi B).T C_z]lambda+C_psi.T Dlambda',
        multipliers_assigned=False, multiplier_firsts_assigned=False,
        actual_known_action='exact original anchored cap geometry+FR+moving GHY/Hayward, with the old reference Casimir absent; no recorded local Maxwell/Higgs functional is included',
        local_removal_repeated=False, independent_local_force_added=False,
        surface_scope='exact area weak contact returned per gamma; gamma unassigned',
        known_action_contact_scope='raw weak state AND independent phase-rate source placements; not a complete Euler operator or full constrained formation Hessian',
        known_action_source_order=['original Xi', 'normal corrected Xi', 'normal plus full connection-field corrected Xi'],
        known_action_twojets_evaluated_once_per_history=True,
        known_action_cap_points=int(action_cap_points),
        known_action_field_correction_scope='the newly evaluated spatial wall-field correction has exactly zero geometry component; the known bare geometric action has no such field argument, so the matching known action contact is reused, not a declaration of zero native field dependence',
        physical_native_action_Hessian=None, full_action_Hessian=None, full_formation_stationarity_residual=None,
        outer_residual=None, full_normal_profile_normalization=None,
        homogeneous_coordinates_per_side_per_time_node=366, parent_homogeneous_coordinates=3660,
        child_homogeneous_domain_coordinates=None,
        constraint_direct_h_derivative='zero only for these classical metric/connection constraints by their explicit equations; induced interacting field/state/backreaction derivatives remain uncomputed',
        numerical_constraint_kernel_is_gauge=False,
        retained_unknowns='six rotation source coordinates, initial right translation and central phase, spin signs, full outer/state/normal data and all parent fermion h/dh; no minimum-norm state or quotient selected',
        source_scope='fixed E1 coefficient application; constant normal-function and constant spatial wall-field source extensions are provisional; full moving child-domain and physical source supplied by their separate producer',
        complete_physical_derivative=False, physical_guard=2e-10, physical_admission=False,
        NEXT_OPERAND='consume the exact constraint curvature coefficients with actual constraint multipliers and the same-domain native/state/outer action Hessian in the complete two-sided formation KKT; use the full spatial field/source applications without assigning remaining fermion boundary data')
    return out, report
