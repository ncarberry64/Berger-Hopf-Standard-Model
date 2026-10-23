"""Moving geometric trace and actual temporal cotangent endpoint applications.

The physical incoming-final and child-initial momenta are pulled back with
opposite signs.  The child affine connection image is applied pointwise;
its position/time/radial derivatives are not projected into the numerical
radial space.  This extends the represented endpoint correction to moving
geometric traces.  It is not the complete physical formation or scale solve.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_birth_finite_normal_trace_graph import (
    finite_normal_trace_graph_action_two_jet as normal_trace_graph_action_two_jet, affine_connection_profile_two_jet,
    _field_applications, _gauge_test_maps,
)
from .muon_birth_normal_constrained_action import constrained_velocity_trial
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action as pointwise_trace_enriched_action
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_phase_continuation import _compressed_npz
from .muon_parent_gauge_geometry_correction import ROOT, STATE_SOURCE
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order, _trace_jacobian_at_order, _symmetric_power
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_parent_maxwell_full_weak import FIELD_ORDER, M, _curvature_polynomials, _direction_polynomials, _parameters
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _positive_log_jet(jet):
    if jet.value <= 0 or not np.isfinite(jet.value):
        raise ValueError('positive finite metric coefficient required')
    return Jet(np.log(jet.value), jet.gradient/jet.value,
        jet.hessian/jet.value-np.outer(jet.gradient, jet.gradient)/jet.value**2)


def moving_geometric_trace_jet(raw):
    """Pull the retained log-metric and attachment observables to the wall.

    At n=0 the three log values are exactly the retained trace3*q and
    the attachment pair is the retained q_w,q_0-q_w.  The moved chart
    uses the same A,B,C and quotient radius R4=AB/sqrt(A^2+B^2).
    All metric and normal mixed derivatives remain active.
    """
    x = np.asarray(raw, float)
    if x.ndim != 1 or len(x) < 100:
        raise ValueError('same complete moving geometric state required')
    w = intrinsic_m4_weight_jet(12, x[:37], x[37:74], x[74:98], source_value=x[98], source_rate=x[99])
    f = w['fields']; logR0 = np.log(RADIUS0)
    trace = [_positive_log_jet(f['C'])-logR0, _positive_log_jet(f['A'])-logR0+np.log(2)/2,
             _positive_log_jet(f['B'])-logR0+np.log(2)/2]
    qw = _positive_log_jet(2*w['R4']/RADIUS0)
    # q0 is the retained log ambient scale, not a measured mass/unit fit.
    q0 = Jet.affine(x[0], np.eye(100)[0])
    attachment = [qw, q0-qw]
    all_values = trace+[attachment[1]]
    return dict(value=np.array([j.value for j in all_values]),
        first=np.array([j.gradient for j in all_values]),
        second=np.array([j.hessian for j in all_values]),
        attachment_value=np.array([j.value for j in attachment]),
        attachment_first=np.array([j.gradient for j in attachment]),
        attachment_second=np.array([j.hessian for j in attachment]),
        wall=w['wall'].value, geometry=w,
        normalization='retained trace and attachment constants; moving wall pulled through the same metric')


def pair_master_chart(representation):
    c = generic_coordinate_lift(representation['gauge_labels']); P = c['lift']; nr, nm = P.shape
    R = np.zeros((2*nr, 2*nm)); R[:nr, :nm] = P; R[nr:, nm:] = P
    n = c['x_count']; m = c['y_count']
    xi = np.r_[np.arange(n), nm+np.arange(n)]
    vi = np.r_[np.arange(n, 2*n), nm+np.arange(n, 2*n)]
    yi = np.r_[np.arange(2*n, nm), nm+np.arange(2*n, nm)]
    return dict(lift=R, one_lift=P, raw_count=nr, master_count=nm,
        dynamic_count=n, algebraic_count=m, x_indices=xi, v_indices=vi, y_indices=yi, coordinates=c)


def temporal_birth_cotangent(graph, parent, chart):
    """Exact oriented canonical pullback, parent final+ and child initial-.

    If F_parent is the identity and F_child is the affine trace graph,
    Pi_graph=F_parent^T Pi_parent+F_child^T Pi_child.  Thus the birth
    cotangent is 2*pad(Pi_parent)-Pi_graph.  Its derivative retains the
    nonlinear profile/metric contacts from the same action Hessian.
    """
    R = chart['lift']; P = chart['one_lift']; n = chart['dynamic_count']; nm = chart['master_count']
    vi = chart['v_indices']; pg = P.T@parent['raw_gradient']; ph = P.T@parent['raw_hessian']@P
    g = R.T@graph['raw_gradient']; h = R.T@graph['raw_hessian']@R
    theta = -g[vi]; dtheta = -h[vi].copy()
    theta[:n] += 2*pg[n:2*n]; dtheta[:n, :nm] += 2*ph[n:2*n]
    return dict(value=theta, first=dtheta, master_gradient=g, master_hessian=h,
        parent_master_gradient=pg, parent_master_hessian=ph,
        common_normal_raw_cotangent=float(theta[37]+theta[n+37]),
        temporal_orientation='incoming-final +Pi; child-initial -Pi',
        action_sum_momentum_not_temporal_jump=True)


def moving_trace_saddle_data(raw_pair, representation, chart):
    """Exact moved attachment B/D_B plus separate normal trace rows."""
    raw = np.asarray(raw_pair, float); nr = chart['raw_count']; nm = chart['master_count']; n = chart['dynamic_count']
    R = chart['lift']; rv = R[:, chart['v_indices']]; rx = R[:, chart['x_indices']]
    B = np.zeros((6, 2*n)); DB = np.zeros((2*nm, 6, 2*n)); jets = []
    for arm in range(2):
        w = moving_geometric_trace_jet(raw[arm]); jets.append(w)
        local = slice(arm*nr, arm*nr+100)
        # A scalar attachment chart depends on positions only.  Its gradient
        # acting on velocity components uses the identical x/v coordinate map.
        B[2*arm:2*arm+2] = w['attachment_first']@rx[local]
        DB[:, 2*arm:2*arm+2] = np.einsum('aki,kj,il->jal',
            w['attachment_second'], R[local], rx[local], optimize=True)
    B[4, 37] = B[5, n+37] = 1.
    return dict(B=B, DB=DB, jets=jets, raw_velocity_lift=rv)


def anchored_reference_clock_work(raw_pair, reference_pair, representation, graph, chart):
    """Known explicit-time work from the anchored reference connection jet.

    F_child(x,t)=a_child+M*(delta_lambda(x)-delta_lambda_ref(t)) has
    F_t=-M*delta_lambda_ref,t.  Thus E_physical=E_pullback-Pi*delta_lambda_ref,t.
    This is an owned temporal derivative at the reference, not a fitted
    drive.  Its first derivative is the literal electric/shift current
    application, retaining connection and all common field derivatives.
    """
    rep = representation; raw = np.asarray(raw_pair); nr = chart['raw_count']; N = len(rep['gauge_labels'])
    current = affine_connection_profile_two_jet(raw, rep['rho'])
    reference = affine_connection_profile_two_jet(reference_pair, rep['rho'])
    shape = reference['value'][:, 1]
    fields = _field_applications(raw[1], rep, graph['profile_increment'])
    tests = _gauge_test_maps(rep, graph['profile_first']); count = 2*N+200
    work = 0.; geometric = np.zeros(100); fields_first = np.zeros(count)
    for r, row in enumerate(current['applications'][1]['rows']):
        a, at, ar, angular = (fields[name][r] for name in ('gauge', 'gauge_tau', 'gauge_rho', 'gauge_angular'))
        base = _curvature_polynomials(a, at, ar, angular)
        direction = _direction_polynomials(a, *(tests[name][r] for name in ('tests', 'tests_tau', 'tests_rho', 'tests_angular')))
        params = _parameters(row, 100); beta = row['shift']; electric = row['electric']
        factor = rep['radial_quadrature'][r]*shape[r]*MAXWELL_TO_CAP
        temporal = Jet.constant(0., 100)
        for k in range(5):
            ft = float(np.sum(base[1][k]*M)); fr = float(np.sum(base[2][k]*M))
            temporal += params[k]*(ft-beta*fr)
        w = factor*electric*temporal; work += w.value; geometric += w.gradient
        values = np.array([p.value for p in params])
        dt = np.einsum('k,ktpic->tpic', values, direction[1])
        dr = np.einsum('k,ktpic->tpic', values, direction[2])
        fields_first += factor*electric.value*np.sum((dt-beta.value*dr)*M, axis=(1, 2, 3))
    T = np.zeros((count, 2*nr)); T[:2*N, nr+100:nr+100+2*N] = np.eye(2*N)
    geo_indices = np.r_[np.arange(100), nr+np.arange(100)]; T[2*N:, geo_indices] = np.eye(200)
    derivative = T.T@fields_first; derivative[nr:nr+100] += geometric
    return dict(value=float(work), master_first=derivative@chart['lift'],
        reference_time_profile=shape, reference_coordinate_frame_held_fixed=True,
        convention='E_child=E_joint_graph-E_parent-reference_clock_work; F_t=-M*delta_lambda_ref,t')


def projected_birth_cotangent(graph, parent, raw_pair, representation, *,
                              action_evaluator=None, difference_step=2e-5,
                              coordinate_weights=None, compute_derivative=True):
    """Project the actual face cotangent through the full constraint saddle.

    Four directional Hessian applications supply the implicit lift
    derivative.  The face-cotangent derivative itself is analytic.  No
    old geometric-only p2, positive inverse-A or mode ordering is reused.
    """
    chart = pair_master_chart(representation); f = temporal_birth_cotangent(graph, parent, chart)
    t = moving_trace_saddle_data(raw_pair, representation, chart)
    vi, yi = chart['v_indices'], chart['y_indices']; H = f['master_hessian']; dim = len(H); n = len(vi)
    C = H[np.ix_(yi, vi)]
    base = constrained_velocity_trial(H[np.ix_(vi, vi)], C, t['B'], velocity_cotangent=f['value'])
    reaction = base['solution'][n:]; ell = base['velocity_lift']; K = base['saddle']; scale = base['row_scale']
    dual_rhs = np.r_[f['value'], np.zeros(len(reaction))]
    adjoint = scale*np.linalg.solve(scale[:, None]*K*scale[None, :], scale*dual_rhs)
    common = np.zeros((6, 3)); common[[0, 2], 0] = 1.; common[[1, 3], 1] = 1.; common[[4, 5], 2] = 1.
    result = dict(cotangent=common.T@base['trial_momentum'], six_trace_cotangent=base['trial_momentum'],
        common_trial_map=common, base=base, face=f, trace=t, chart=chart, adjoint=adjoint,
        kinetic_adjoint_residual=K@adjoint-dual_rhs)
    if not compute_derivative:
        return result
    if action_evaluator is None:
        raise ValueError('same action evaluator required for implicit saddle cotangent')
    weights = np.ones(dim) if coordinate_weights is None else np.asarray(coordinate_weights, float)
    if weights.shape != (dim,) or np.any(weights <= 0) or difference_step <= 0:
        raise ValueError('positive common-coordinate weights and difference step required')
    av = np.zeros(dim); av[vi] = adjoint[:n]; av[yi] = adjoint[n+6:]
    ay = np.zeros(dim); ay[yi] = adjoint[n+6:]
    b = np.zeros((dim, 6)); b[vi] = ell; b[yi] = reaction[6:]
    by = np.zeros_like(b); by[yi] = reaction[6:]
    eta = chart['lift'].T@np.asarray(raw_pair).reshape(-1); applications = []
    def derivative(direction):
        mag = float(np.max(abs(weights*direction)))
        if mag == 0:
            return np.zeros_like(H)
        unit = direction/mag
        p = action_evaluator(eta+difference_step*unit)['master_hessian']
        m = action_evaluator(eta-difference_step*unit)['master_hessian']
        applications.append(dict(unit_direction=unit, restored_magnitude=mag, step=difference_step))
        return mag*(p-m)/(2*difference_step)
    third = derivative(av)@b-derivative(ay)@by
    contact = np.empty((dim, 6))
    for k, db in enumerate(t['DB']):
        contact[k] = adjoint[:n]@db.T@reaction[:6]+adjoint[n:n+6]@db@ell
    derivative_matrix = (f['first'].T@ell-third-contact).T
    result.update(derivative=common.T@derivative_matrix, six_trace_derivative=derivative_matrix,
        third_action_contraction=third.T, boundary_contact=contact.T,
        directional_hessian_applications=applications, difference_step=difference_step,
        error_scope='centered directional binary64 Hessian differences; no rigorous D3/rounding/continuum bound')
    return result


def moving_endpoint_rows(raw_pair, reference_pair, representation, state_weights,
                         normalization_coordinates, *, difference_step=2e-5,
                         compute_cotangent_derivative=True):
    """Full represented field/geometry/normal temporal rows on one vector."""
    raw = np.asarray(raw_pair, float); chart = pair_master_chart(representation); R = chart['lift']; P = chart['one_lift']
    nr = chart['raw_count']; nm = chart['master_count']; n = chart['dynamic_count']; vi = chart['v_indices']; yi = chart['y_indices']
    if raw.shape != (2, nr):
        raise ValueError('same complete incoming/child vector required')
    params = representation['endpoint_action_parameters']
    graph = normal_trace_graph_action_two_jet(raw, reference_pair, representation, **params)
    parent = pointwise_trace_enriched_action(raw[0], representation, **params)
    f = temporal_birth_cotangent(graph, parent, chart); g, h = f['master_gradient'], f['master_hessian']; eta = R.T@raw.reshape(-1)
    def evaluate(e):
        a = normal_trace_graph_action_two_jet((R@e).reshape(2, nr), reference_pair, representation, **params)
        return dict(master_hessian=R.T@a['raw_hessian']@R)
    weights = np.asarray(state_weights, float)
    rawweights = np.tile(np.r_[weights, np.ones(nr-98)], 2); mw = abs(R.T)@rawweights
    projected = projected_birth_cotangent(graph, parent, raw, representation, action_evaluator=evaluate,
        difference_step=difference_step, coordinate_weights=mw, compute_derivative=compute_cotangent_derivative)
    rows = []; jac = []; groups = {}
    def append(name, value, derivative):
        start = len(rows); value = np.atleast_1d(value); derivative = np.atleast_2d(derivative)
        rows.extend(value); jac.extend(derivative); groups[name] = (start, len(rows))
    for arm in range(2):
        indices = yi[arm*chart['algebraic_count']:(arm+1)*chart['algebraic_count']]
        scale = np.r_[1/weights[74:98], np.ones(chart['algebraic_count']-24)]
        append(('incoming' if arm == 0 else 'child')+'_constraints', scale*g[indices], scale[:, None]*h[indices])
    v = np.zeros(2*nm); v[vi] = eta[vi]
    E = float(v@g-graph['value']); dE = h@v-g; dE[vi] += g[vi]
    pv = np.zeros(nm); pv[n:2*n] = eta[n:2*n]
    pg, ph = f['parent_master_gradient'], f['parent_master_hessian']
    Ep = float(pv@pg-parent['value']); dEp = np.zeros(2*nm); dEp[:nm] = ph@pv-pg; dEp[n:2*n] += pg[n:2*n]
    clock_work = anchored_reference_clock_work(raw, reference_pair, representation, graph, chart)
    append('incoming_energy', Ep, dEp)
    append('child_energy', E-Ep-clock_work['value'], dE-dEp-clock_work['master_first'])
    labels = representation['gauge_labels']; dynamic = chart['coordinates']['dynamic_gauge_indices']; N = len(labels); hs = 100+2*N
    affine = np.zeros(len(dynamic))
    for k, i in enumerate(dynamic):
        label = labels[i]; field = FIELD_ORDER.index(label['field'])
        if field >= 2 and label['internal'] == field-2:
            affine[k] = np.sqrt(8)*representation['affine_difference_coefficients'][label['radial']]
    for name, rawindices, offset, positions in (
        ('gauge', 100+dynamic, affine, np.arange(38, n-4)),
        ('Higgs', np.arange(hs, hs+4), np.zeros(4), np.arange(n-4, n))):
        d = np.zeros((len(rawindices), 2*nr)); d[:, rawindices] = -np.eye(len(rawindices)); d[:, nr+rawindices] = np.eye(len(rawindices))
        append(name+'_trace', raw[1, rawindices]-raw[0, rawindices]-offset, d@R)
        append(name+'_temporal_dual', f['value'][positions]+f['value'][n+positions], f['first'][positions]+f['first'][n+positions])
    trace = projected['trace']['jets']; baseB = _attachment_jacobian_at_order(12, normalization_coordinates)
    normal_trace = np.vstack((_trace_jacobian_at_order(12), baseB[1]))
    norm = _symmetric_power(normal_trace@np.diag(1/weights[:37]**2)@normal_trace.T, -.5)
    T = np.zeros((4, 2*nr)); T[:, :100] = -trace[0]['first']; T[:, nr:nr+100] = trace[1]['first']
    append('moving_geometric_trace', norm@(trace[1]['value']-trace[0]['value']), norm@T@R)
    dn = np.zeros(2*nr); dn[nr+98] = 1; dn[98] = -1
    append('normal_position_trace', raw[1, 98]-raw[0, 98], dn@R)
    dc = np.zeros((3, 2*nm)) if not compute_cotangent_derivative else projected['derivative']
    attachment_norm = _symmetric_power(baseB@baseB.T, .5)
    append('common_attachment_temporal_dual', attachment_norm@projected['cotangent'][:2], attachment_norm@dc[:2])
    append('common_normal_temporal_dual', projected['cotangent'][2], dc[2])
    return dict(residual=np.asarray(rows), jacobian=np.asarray(jac), groups=groups, graph=graph, parent=parent,
        chart=chart, projected=projected, constraint_energy=np.array([Ep, E-Ep-clock_work['value']]),
        reference_clock_work=clock_work,
        reference_pair=np.asarray(reference_pair), source_profile_projected=False,
        temporal_normal_row_not_physical_formation_condition=True)


def solve_moving_endpoint(initial, reference, representation, state_weights, normalization_coordinates,
                          *, max_iterations=6, tolerance=2e-10, difference_step=2e-5,
                          checkpoint=None, row_scale=None, iteration_offset=0):
    raw = np.array(initial, float, copy=True); chart = pair_master_chart(representation); R = chart['lift']
    weights = abs(R.T)@np.tile(np.r_[state_weights, np.ones(chart['raw_count']-98)], 2)
    eta = R.T@raw.reshape(-1); history = []; records = []; status = 'MAXIMUM_ITERATIONS'
    evaluate = lambda x, derivative=True: moving_endpoint_rows(x, reference, representation, state_weights, normalization_coordinates,
        difference_step=difference_step, compute_cotangent_derivative=derivative)
    current = evaluate(raw); scale = row_scale
    for k in range(max_iterations+1):
        J = current['jacobian']
        if scale is None:
            scale = 1/np.maximum(np.max(abs(J/weights), axis=1), 1.)
        norm = float(np.linalg.norm(scale*current['residual']))
        if checkpoint is not None:
            checkpoint(iteration_offset+k, raw, current, scale, history)
        if norm < tolerance:
            status = 'REPRESENTED_MOVING_TRACE_TOLERANCE'; break
        if k == max_iterations:
            break
        U, s, V = np.linalg.svd(scale[:, None]*J/weights, full_matrices=True); keep = s > 1e-12*max(s)
        correction = -(V[:len(s)][keep].T@((U[:, keep].T@(scale*current['residual']))/s[keep]))/weights
        accepted = False; trials = []
        for j in range(18):
            damping = 2.**(-j); trialeta = eta+damping*correction; trial = (R@trialeta).reshape(raw.shape)
            try:
                candidate = evaluate(trial, False); newnorm = float(np.linalg.norm(scale*candidate['residual']))
                good = np.isfinite(newnorm) and newnorm < norm
            except (ValueError, FloatingPointError, OverflowError, np.linalg.LinAlgError):
                newnorm = None; good = False
            trials.append(dict(damping=damping, scaled_residual=newnorm, accepted=bool(good)))
            if good:
                accepted = True; break
        history.append(dict(iteration=iteration_offset+k, scaled_residual=norm, rank=int(sum(keep)),
            weighted_step_norm=float(np.linalg.norm(weights*correction)), damping_history=trials,
            omitted_left_source_norm=float(np.linalg.norm(U[:, ~keep].T@(scale*current['residual']))),
            linearized_scaled_residual=float(np.linalg.norm(scale*(J@correction+current['residual'])))))
        records.append(dict(jacobian=J, linearization_raw=raw.copy(), correction=correction,
            singular_values=s, right_vectors=V, left_vectors=U, retained_singular_values=keep))
        if not accepted:
            status = 'DAMPING_STALL'; break
        eta = trialeta; raw = trial; current = evaluate(raw)
    return dict(raw=raw, application=current, history=history, records=records, status=status,
        row_scale=scale, coordinate_weights=weights, scaled_residual=float(np.linalg.norm(scale*current['residual'])))


def materialize_moving_endpoint(initial_application, output, *, repository=ROOT,
                                max_iterations=6, difference_step=2e-5, resume_checkpoint=None):
    root = Path(repository); out = Path(output)
    if out.exists():
        raise FileExistsError('preserve earlier production')
    loaded = load_attached_endpoint(initial_application, side='incoming', repository=root)
    source = loaded['source']; rep = loaded['representation']; rep['endpoint_action_parameters'] = loaded['receipt']['action_parameters']
    with np.load(source/'application.npz', allow_pickle=False) as a:
        reference = a['updated_raw_pair'].copy()
    with np.load(root/STATE_SOURCE, allow_pickle=False) as a:
        weights = a['state_weights']
    with np.load(root/NORMALIZATION_SOURCE, allow_pickle=False) as a:
        normal = a['normalization_coordinates']
    hashes = dict(loaded['receipt']['input_hashes'])
    for path in ('src/bhsm/interface/muon_birth_finite_geometric_trace_endpoint.py',
                 'src/bhsm/interface/muon_birth_finite_normal_trace_graph.py',
                 'src/bhsm/interface/muon_exact_material_response.py',
                 'src/bhsm/interface/muon_birth_normal_trace_graph.py',
                 'src/bhsm/interface/muon_birth_normal_constrained_action.py',
                 'src/bhsm/interface/muon_birth_attached_phase.py'):
        hashes[path] = sha256((root/path).read_bytes()).hexdigest()
    initial = reference.copy(); resume = {}; resume_sha = None
    if resume_checkpoint is not None:
        cp = Path(resume_checkpoint); cp = cp if cp.is_absolute() else root/cp
        rb = (cp/'result.json').read_bytes(); cr = json.loads(rb)
        if cr['input_hashes'] != hashes or cr['consumed_receipt_sha256'] != loaded['receipt_sha256'] or cr['difference_step'] != difference_step:
            raise ValueError('resume must preserve the same action, source frame and derivative step')
        if sha256((cp/'application.npz').read_bytes()).hexdigest() != cr['numerical_sha256']:
            raise ValueError('checkpoint numerical values changed')
        with np.load(cp/'application.npz', allow_pickle=False) as a:
            initial = a['raw_pair']; resume = dict(row_scale=a['row_scale'], iteration_offset=cr['accepted_iteration'])
        resume_sha = sha256(rb).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(k, raw, current, scale, history):
        folder = out/'checkpoints'/f'accepted_{k:04d}'; folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz', dict(raw_pair=raw, residual=current['residual'],
            jacobian=current['jacobian'], row_scale=scale,
            temporal_face_cotangent=current['projected']['face']['value'],
            common_trace_cotangent=current['projected']['cotangent']))
        md = dict(scope='MOVING_TRACE_ENDPOINT_CHECKPOINT', accepted_iteration=k, history=history,
            input_hashes=hashes, consumed_receipt_sha256=loaded['receipt_sha256'], difference_step=difference_step,
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe', '-m', 'bhsm.interface.muon_birth_finite_geometric_trace_endpoint',
                '--initial-application', str(source), '--output', 'CHOOSE_NEW_OUTPUT_DIRECTORY',
                '--max-iterations', str(max_iterations), '--difference-step', str(difference_step),
                '--resume-checkpoint', str(folder)], resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    result = solve_moving_endpoint(initial, reference, rep, weights, normal, max_iterations=max_iterations,
        difference_step=difference_step, checkpoint=checkpoint, **resume)
    if hashes != {path: sha256((root/path).read_bytes()).hexdigest() for path in hashes}:
        raise RuntimeError('action owner changed during production')
    a = result['application']; p = a['projected']; chart = a['chart']
    arrays = dict(initial_raw_pair=initial, reference_raw_pair=reference, updated_raw_pair=result['raw'],
        updated_residual=a['residual'], updated_jacobian=a['jacobian'], row_scale=result['row_scale'],
        coordinate_weights=result['coordinate_weights'], graph_raw_gradient=a['graph']['raw_gradient'],
        graph_raw_hessian=a['graph']['raw_hessian'], temporal_face_cotangent=p['face']['value'],
        temporal_face_cotangent_derivative=p['face']['first'], common_trace_cotangent=p['cotangent'],
        six_trace_cotangent=p['six_trace_cotangent'], constrained_trace_lift=p['base']['velocity_lift'],
        constraint_annihilation=p['base']['constraint_annihilation'], saddle=p['base']['saddle'],
        saddle_solution=p['base']['solution'], saddle_residual=p['base']['solve_residual'],
        third_action_contraction=p['third_action_contraction'], boundary_contact=p['boundary_contact'])
    arrays.update(reference_clock_work=np.array(a['reference_clock_work']['value']),
        reference_clock_work_master_first=a['reference_clock_work']['master_first'],
        reference_time_profile=a['reference_clock_work']['reference_time_profile'])
    for key in ('affine_profile_reference_states', 'affine_interior_projection', 'affine_difference_coefficients',
                'wall_trace_map', 'wall_radial_derivative_map', 'rho', 'radial_quadrature', 'gauge_basis',
                'gauge_radial_basis', 'radial_value_map', 'radial_derivative_map'):
        arrays[key] = rep[key]
    iteration_archives = []
    for k, record in enumerate(result['records']):
        path = out/'iterations'/f'iteration_{k:04d}.npz'; path.parent.mkdir(exist_ok=True)
        _compressed_npz(path, record)
        iteration_archives.append(dict(path=path.relative_to(out).as_posix(),
            sha256=sha256(path.read_bytes()).hexdigest()))
    _compressed_npz(out/'application.npz', arrays)
    md = dict(scope='EVALUATED_FINITE_ANCHORED_TRIAL_GEOMETRIC_NORMAL_TEMPORAL_TRACE_ENDPOINT_CORRECTION', status=result['status'],
        history=result['history'], scaled_residual=result['scaled_residual'], unscaled_residual_norm=float(np.linalg.norm(a['residual'])),
        groups={name: dict(indices=list(range(*span)), norm=float(np.linalg.norm(a['residual'][slice(*span)]))) for name, span in a['groups'].items()},
        raw_arm_count=chart['raw_count'], master_unknown_count=len(a['jacobian'][0]), row_count=len(a['residual']),
        source_profile_projected=False, reference_value_anchor_preserved=True,
        response_chart='exact normalized two-harmonic admissible trial; anchors solved at every iterate; no physicalprofile selected',
        iteration_archives=iteration_archives,
        canonical_pullback='theta_birth=2*pad(Pi_parent)-Pi_joint_graph; incomingfinal+Pi, childinitial-Pi',
        energy_pullback=a['reference_clock_work']['convention'],
        reference_clock_work=a['reference_clock_work']['value'],
        geometric_trace='same metric/quotient radius pulled to the moving wall; all q and normal derivatives active',
        canonical_projection='joint same-action kinetic stationarity with80 multiplier/Gauss rows,4 attachment and2 normal trace coordinates',
        normal_temporal_row_not_physical_formation_condition=True,
        action_parameters=rep['endpoint_action_parameters'], common_scale_equation='GF=c_F/E_kappa^2',
        unassigned_area_equation='gamma=alpha_FSC*ell_current^(-m); no zero or alpha_EM assignment',
        difference_step=difference_step, resumed_checkpoint_sha256=resume_sha,
        input_hashes=hashes, consumed_receipt_sha256=loaded['receipt_sha256'],
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        gauge_labels=rep['gauge_labels'], gauge_count=rep['gauge_count'], radial_points=len(rep['rho']), cap_points=rep['cap_points'],
        affine_profile_enrichment=loaded['receipt']['affine_profile_enrichment'],
        physical_fullfield_junction_closed=False, physical_formation_closed=False, physical_native_heat_closed=False, physical_Pauli_value=False,
        error_scope='binary64 represented action and adjoint directional-Hessian cotangent derivatives; minimum weighted Newton correction is not branch selection')
    (out/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return md


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial-application', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-iterations', type=int, default=6); p.add_argument('--difference-step', type=float, default=2e-5)
    p.add_argument('--resume-checkpoint', type=Path)
    args = p.parse_args()
    print(json.dumps(materialize_moving_endpoint(args.initial_application, args.output,
        max_iterations=args.max_iterations, difference_step=args.difference_step, resume_checkpoint=args.resume_checkpoint), sort_keys=True))
