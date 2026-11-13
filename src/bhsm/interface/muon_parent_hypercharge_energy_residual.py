"""Strong continuum residual of the retained frozen hypercharge weak probe.

The energy inequality is an exact continuum statement on its stated domain.
Its application below uses analytic coefficient/basis derivatives, a specified
C2 temporal continuation, and ordinary quadrature.  Sampled growth constants
and quadrature refinements are estimates, not interval enclosures.  The common
connection normalization remains unassigned, just as in the consumed packet.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid
from scipy.linalg import cho_factor, cho_solve
from scipy.special import eval_jacobi, gammaln, logsumexp

from .ae3_c2_photon_symbol_audit import stable_weight_and_log_derivative
from .muon_birth_candidate_geometry_action import ROOT, evaluate_retained_candidate_geometry
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_velocity import current_parent_fields
from .muon_parent_retarded_hypercharge import ALPHA, WALL, compact_trace_pulse

RETAINED_PACKET = 'artifacts/muon_parent_retarded_hypercharge_20261010/canonical_run_2'
ADVANCED_PACKET = 'artifacts/muon_parent_hypercharge_advanced_probe_20261010/run_4'


def radial_basis_two_jet(rho, order):
    """Differentiate the SAME Friedrichs Jacobi polynomial through order two."""
    rho = np.asarray(rho, float)
    if (type(order) is not int or order < 1 or rho.ndim != 1
            or not np.isfinite(rho).all() or np.any(rho <= 0) or np.any(rho > WALL)):
        raise ValueError('positive interior/wall coordinates and positive integer order required')
    x = rho/WALL
    a, b = 2., 4.+2*ALPHA
    F = x**ALPHA*(1-x)
    F1 = (ALPHA*x**(ALPHA-1)-(ALPHA+1)*x**ALPHA)/WALL
    F2 = (ALPHA*(ALPHA-1)*x**(ALPHA-2)
          -ALPHA*(ALPHA+1)*x**(ALPHA-1))/WALL**2
    columns = [[], [], []]
    for j in range(order):
        lognorm = (gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)
                   -gammaln(j+a+b+1)-np.log(2*j+a+b+1))
        norm = np.exp(-lognorm/2)
        P = norm*eval_jacobi(j, a, b, 2*x-1)
        P1 = (norm*(j+a+b+1)/WALL*eval_jacobi(j-1, a+1, b+1, 2*x-1)
              if j else np.zeros_like(x))
        P2 = (norm*(j+a+b+1)*(j+a+b+2)/WALL**2
              *eval_jacobi(j-2, a+2, b+2, 2*x-1) if j >= 2 else np.zeros_like(x))
        columns[0].append(F*P)
        columns[1].append(F1*P+F*P1)
        columns[2].append(F2*P+2*F1*P1+F*P2)
    columns[0].append(x**ALPHA)
    columns[1].append(ALPHA*x**(ALPHA-1)/WALL)
    columns[2].append(ALPHA*(ALPHA-1)*x**(ALPHA-2)/WALL**2)
    return tuple(np.column_stack(c) for c in columns)


def frozen_coefficient_one_jet(rho, repository=ROOT, *, shift_sign=1):
    """Apply analytic rho derivatives to the actual retained q/m reconstruction.

    The sign reversal is the time-reversed formal adjoint's shift, not a new
    physical background.  No finite differences or temporal history enter.
    """
    if shift_sign not in (-1, 1):
        raise ValueError('shift_sign must be +1 or -1')
    rho = np.asarray(rho, float)
    if (rho.ndim != 1 or not np.isfinite(rho).all()
            or np.any(rho <= 0) or np.any(rho > WALL)):
        raise ValueError('require finite 0<rho<=pi/2')
    repository = Path(repository)
    q, velocity, m = retained_state(repository)
    snapshot = evaluate_retained_candidate_geometry(repository)
    fields = current_parent_fields(np.concatenate((q, velocity, m))[None],
        [np.log(snapshot['geometry']['R4'])], rho)
    k, j = np.arange(1, 13), np.arange(12)
    ck, cj = np.cos(2*rho[:, None]*k), np.cos(2*rho[:, None]*j)
    dk, dj = -2*k*np.sin(2*rho[:, None]*k), -2*j*np.sin(2*rho[:, None]*j)
    window, window1 = np.sin(rho)**2, np.sin(2*rho)
    u1 = dk@q[1:13]
    w1 = window1*(cj@q[13:25])+window*(dj@q[13:25])
    v1 = window1*(cj@q[25:37])+window*(dj@q[25:37])
    C1 = u1+w1
    A1 = u1+v1-.5*np.tan(rho/2)
    B1 = u1-v1+.5/np.tan(rho/2)
    A, B = fields['A'][0], fields['B'][0]
    LF1 = (A*A*A1+B*B*B1)/(A*A+B*B)
    radius1 = A1+B1-LF1
    lapse1 = dk@m[:12]
    W, W1 = np.array([stable_weight_and_log_derivative(float(x)) for x in rho]).T
    common = 2*np.pi**2*fields['connection_component_coefficient_per_kappa1'][0]*W
    C, radius, lapse = (fields[key][0] for key in ('C_rho', 'base_radius', 'proper_lapse'))
    electric = common*C*radius/lapse
    radial = common*lapse*radius/C
    potential = 9*common*lapse*C/radius
    common1 = 5*LF1+W1
    log_e = common1+C1+radius1-lapse1
    log_r = common1+lapse1+radius1-C1
    log_V = common1+lapse1+C1-radius1
    Nb = float(fields['boundary_lapse'][0])
    shift = shift_sign*2*np.sin(2*rho)*(cj@m[12:])/Nb
    shift1 = shift_sign*(4*np.cos(2*rho)*(cj@m[12:])
                         +2*np.sin(2*rho)*(dj@m[12:]))/Nb
    # Analytic boundary value, eliminating only sin(pi)'s rounding residue.
    shift[rho == WALL] = 0.
    pole_slope = shift_sign*4*float(np.sum(m[12:]))/Nb
    return dict(electric=electric, radial=radial, potential=potential,
        shift=shift, electric_derivative=electric*log_e,
        radial_derivative=radial*log_r, potential_derivative=potential*log_V,
        shift_derivative=shift1, electric_log_derivative=log_e,
        radial_log_derivative=log_r, potential_log_derivative=log_V,
        pole_rates=np.array([5*pole_slope, -3*pole_slope, -3*pole_slope]),
        coefficient_derivatives='ANALYTIC_RETAINED_COSINE_WINDOW_AND_LAMBDA',
        physical_background_stationarity=False)


def normal_energy_growth_rates(coefficients):
    """The three signed energy rates, without coordinate coercivity assumptions."""
    b, bp = coefficients['shift'], coefficients['shift_derivative']
    return np.stack((bp+b*coefficients['electric_log_derivative'],
        bp-b*coefficients['radial_log_derivative'],
        -bp-b*coefficients['potential_log_derivative']), axis=-1)


def strong_residual(a, a_t, a_tt, a_rho, a_t_rho, a_rho_rho, coefficients):
    """Apply the full continuum Euler operator, including coefficient derivatives."""
    e, r, V, beta, ep, rp, bp = (coefficients[k] for k in (
        'electric', 'radial', 'potential', 'shift', 'electric_derivative',
        'radial_derivative', 'shift_derivative'))
    return (e*a_tt-2*e*beta*a_t_rho-(ep*beta+e*bp)*a_t
            -(r-e*beta**2)*a_rho_rho
            -(rp-ep*beta**2-2*e*beta*bp)*a_rho+V*a)


def normal_energy_density(a, a_t, a_rho, coefficients):
    e, r, V, beta = (coefficients[k] for k in ('electric', 'radial', 'potential', 'shift'))
    pi = e*(a_t-beta*a_rho)
    return .5*(pi*pi/e+r*a_rho*a_rho+V*a*a), pi


def normal_energy_identity_density(a, pi, b, forcing, coefficients):
    """Return exact interior E' density and boundary flux for independent checks."""
    e, r, V, beta = (coefficients[k] for k in ('electric', 'radial', 'potential', 'shift'))
    rates = normal_energy_growth_rates(coefficients)
    interior = .5*(rates[..., 0]*pi*pi/e+rates[..., 1]*r*b*b
                   +rates[..., 2]*V*a*a)+pi*forcing/e
    density = .5*(pi*pi/e+r*b*b+V*a*a)
    return interior, beta*density+r*b*pi/e


def quintic_hermite_jet(q0, v0, a0, q1, v1, a1, width, unit_nodes):
    """C2 quintic through supplied endpoint value/first/second derivative data."""
    if not np.isfinite(width) or width <= 0:
        raise ValueError('positive finite interval width required')
    z = np.asarray(unit_nodes, float)
    if z.ndim != 1 or not np.isfinite(z).all() or np.any(z < 0) or np.any(z > 1):
        raise ValueError('unit interval nodes required')
    values = tuple(np.asarray(v, float) for v in (q0, v0, a0, q1, v1, a1))
    if any(v.shape != values[0].shape or not np.isfinite(v).all() for v in values):
        raise ValueError('matching finite endpoint jets required')
    q0, v0, a0, q1, v1, a1 = values
    c0, c1, c2 = q0, width*v0, .5*width**2*a0
    A, B, C = q1-c0-c1-c2, width*v1-c1-2*c2, width**2*a1-2*c2
    cs = np.stack((c0, c1, c2, 10*A-4*B+.5*C,
                   -15*A+7*B-C, 6*A-3*B+.5*C))
    powers = z[:, None]**np.arange(6)
    first = np.column_stack((np.zeros_like(z), np.ones_like(z),
        2*z, 3*z*z, 4*z**3, 5*z**4))/width
    second = np.column_stack((np.zeros_like(z), np.zeros_like(z),
        2*np.ones_like(z), 6*z, 12*z*z, 20*z**3))/width**2
    return powers@cs, first@cs, second@cs


def reconstruct_nodal_acceleration(data, source_duration):
    """ODE nodal acceleration anchors the explicit temporal polynomial, not its interior."""
    M, N, K = (data[k] for k in ('M', 'N', 'K'))
    q, v, times = (data[k] for k in ('state', 'velocity', 'times'))
    n = q.shape[1]-1
    wall_acc = compact_trace_pulse(times, source_duration)[2]
    rhs = -(v@(N.T-N).T+q@K.T)[:, :n]-wall_acc[:, None]*M[:n, n]
    a = cho_solve(cho_factor(M[:n, :n]), rhs.T).T
    return np.column_stack((a, wall_acc))


def load_retained_probe(repository=ROOT, *, run_index=2):
    """Bind the actual saved finite solution and every producer-pinned input hash."""
    if type(run_index) is not int or not 0 <= run_index <= 4:
        raise ValueError('retained run index 0..4 required')
    repository = Path(repository)
    directory = repository/RETAINED_PACKET
    receipt_bytes = (directory/'result.json').read_bytes()
    receipt = json.loads(receipt_bytes)
    for path, expected in receipt['input_hashes'].items():
        if sha256((repository/path).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Producer-pinned input hash mismatch: {path}')
    path = directory/f'run_{run_index}.npz'
    with np.load(path, allow_pickle=False) as saved:
        data = {k: saved[k].copy() for k in saved.files}
    info = receipt['runs'][run_index]
    n, nt = info['radial_order'], len(data['times'])
    if (data['state'].shape != (nt, n+1) or data['velocity'].shape != (nt, n+1)
            or any(data[k].shape != (n+1, n+1) for k in ('M', 'N', 'K', 'Kspatial', 'Kshift'))
            or any(not np.isfinite(v).all() for v in data.values())
            or np.any(np.diff(data['times']) <= 0)):
        raise ValueError('Malformed retained finite probe')
    g, dg, _ = compact_trace_pulse(data['times'], info['source_duration'])
    if not np.array_equal(data['state'][:, -1], g) or not np.array_equal(data['velocity'][:, -1], dg):
        raise ValueError('Retained prescribed trace and velocity disagree')
    if np.any(data['state'][0]) or np.any(data['velocity'][0]):
        raise ValueError('Retarded initial perturbation must vanish')
    return data, info, dict(receipt_sha256=sha256(receipt_bytes).hexdigest(),
        solution_path=path.relative_to(repository).as_posix(),
        solution_sha256=sha256(path.read_bytes()).hexdigest(), input_hashes=receipt['input_hashes'])


def load_support_adjoint_pair(repository=ROOT):
    """Bind the separately executed, same-support primal/advanced pair."""
    repository = Path(repository)
    directory = repository/ADVANCED_PACKET
    receipt_bytes = (directory/'result.json').read_bytes()
    receipt = json.loads(receipt_bytes)
    for row in receipt['hashes']:
        raw = (repository/row['path']).read_bytes()
        if len(raw) != row['bytes'] or sha256(raw).hexdigest() != row['sha256']:
            raise ValueError(f'Advanced producer-pinned input hash mismatch: {row["path"]}')
    arrays = {}
    hashes = {}
    for name in ('retarded', 'advanced'):
        path = directory/f'{name}.npz'
        raw = path.read_bytes()
        hashes[name] = sha256(raw).hexdigest()
        if hashes[name] != receipt['runs'][name]['npz_sha256']:
            raise ValueError(f'Advanced solution hash mismatch: {name}')
        with np.load(path, allow_pickle=False) as saved:
            arrays[name] = {k: saved[k].copy() for k in saved.files}
        data = arrays[name]
        n = receipt['radial_order']; nt = len(data['times'])
        if (any(not np.isfinite(v).all() for v in data.values())
                or data['state'].shape != (nt, n+1) or data['velocity'].shape != (nt, n+1)
                or np.any(data['state'][0]) or np.any(data['velocity'][0])):
            raise ValueError('Malformed support primal/advanced initial-domain data')
        g, dg, _ = compact_trace_pulse(data['times'], receipt['runs'][name]['source_duration'])
        if not np.array_equal(data['state'][:, -1], g) or not np.array_equal(data['velocity'][:, -1], dg):
            raise ValueError('Advanced/retarded prescribed trace disagreement')
    p, z = arrays['retarded'], arrays['advanced']
    if (not np.array_equal(p['times'], z['times'])
            or not np.array_equal(p['M'], z['M']) or not np.array_equal(p['K'], z['K'])
            or not np.array_equal(p['N'], -z['N'])):
        raise ValueError('Primal/advanced matrices must share one form with reversed shift')
    info = dict(radial_order=receipt['radial_order'],
        source_duration=receipt['runs']['retarded']['source_duration'])
    return arrays, info, dict(receipt_sha256=sha256(receipt_bytes).hexdigest(),
        solution_sha256=hashes, source_hashes=receipt['hashes'],
        retained_reciprocal_pairing_defect=receipt['reciprocal_pairing_defect'])


def _temporal_samples(data, info, quadrature_order, end_time):
    if type(quadrature_order) is not int or quadrature_order < 2:
        raise ValueError('at least two temporal Gauss nodes per saved interval required')
    times = data['times']
    matching = np.flatnonzero(times == end_time)
    if len(matching) != 1 or matching[0] < 1:
        raise ValueError('end_time must be a retained interval endpoint')
    last = int(matching[0])
    x, w = leggauss(quadrature_order)
    unit = (x+1)/2
    acc = reconstruct_nodal_acceleration(data, info['source_duration'])
    ts, ws, qs, vs, aas = [], [], [], [], []
    for i in range(last):
        width = times[i+1]-times[i]
        nodes = times[i]+width*unit
        q, v, a = quintic_hermite_jet(data['state'][i], data['velocity'][i], acc[i],
            data['state'][i+1], data['velocity'][i+1], acc[i+1], width, unit)
        # The interior continuation must not change the prescribed boundary
        # pulse.  Its lift and both derivatives remain EXACTLY that input.
        q[:, -1], v[:, -1], a[:, -1] = compact_trace_pulse(nodes, info['source_duration'])
        ts.append(nodes); ws.append(w*width/2)
        qs.append(q); vs.append(v); aas.append(a)
    return tuple(np.concatenate(v) for v in (ts, ws, qs, vs, aas))


def evaluate_continuum_residual(data, info, repository=ROOT, *, radial_quadrature=960,
        temporal_quadrature=3, end_time=None, shift_sign=1, growth_grid=8193):
    """Evaluate a true strong residual of an explicit spatial/temporal continuation.

    A constant C is sampled, not bounded.  The reported logarithmic estimate
    avoids overflow and is conditional on C dominating the continuum rates.
    Ordinary quadrature and binary64 polynomial arithmetic are not certified.
    """
    if type(radial_quadrature) is not int or radial_quadrature < 16:
        raise ValueError('radial quadrature >=16 required')
    if type(growth_grid) is not int or growth_grid < 33:
        raise ValueError('growth grid >=33 required')
    end_time = info['source_duration'] if end_time is None else float(end_time)
    t, tw, q, v, acc = _temporal_samples(data, info, temporal_quadrature, end_time)
    x, rw = leggauss(radial_quadrature)
    rho, rw = (x+1)*WALL/2, rw*WALL/2
    coefficients = frozen_coefficient_one_jet(rho, repository, shift_sign=shift_sign)
    B, D, D2 = radial_basis_two_jet(rho, info['radial_order'])
    norms, energies, lift_contractions = [], [], []
    wall_lift = B[:, -1]
    for start in range(0, len(t), 256):
        sl = slice(start, start+256)
        a, at, att, ar, atr, arr = (q[sl]@B.T, v[sl]@B.T, acc[sl]@B.T,
            q[sl]@D.T, v[sl]@D.T, q[sl]@D2.T)
        R = strong_residual(a, at, att, ar, atr, arr, coefficients)
        norms.append(np.sqrt((R*R/coefficients['electric'])@rw))
        energy, _ = normal_energy_density(a, at, ar, coefficients)
        energies.append(energy@rw)
        lift_contractions.append((R*wall_lift)@rw*q[sl, -1])
    norm = np.concatenate(norms)
    energy = np.concatenate(energies)
    lift = np.concatenate(lift_contractions)
    grho = np.linspace(0, WALL, growth_grid)[1:]
    gc = frozen_coefficient_one_jet(grho, repository, shift_sign=shift_sign)
    rates = normal_energy_growth_rates(gc)
    pole = gc['pole_rates']
    column_max = np.maximum(np.max(rates, axis=0), pole)
    C = float(np.max(column_max))
    positive = norm > 0
    log_bound = (-.5*np.log(2)+float(logsumexp(np.log(tw[positive])
        +np.log(norm[positive])+.5*C*(end_time-t[positive])))) if positive.any() else None
    bound = float(np.exp(log_bound)) if log_bound is not None and log_bound < 700 else (0. if log_bound is None else None)
    result = dict(radial_quadrature=radial_quadrature, temporal_quadrature=temporal_quadrature,
        time_samples=len(t), end_time=end_time, radial_order=info['radial_order'],
        residual_L2_time_space_weighted=float(np.sqrt(np.dot(tw, norm*norm))),
        residual_L1_time_L2_space_weighted=float(np.dot(tw, norm)),
        residual_L2_space_max_sample=float(np.max(norm)),
        normal_energy_max_sample=float(np.max(energy)),
        trace_lift_residual_pairing=float(np.dot(tw, lift)),
        sampled_growth_constant=C, sampled_rate_column_maxima=column_max.tolist(),
        exact_pole_rate_limits=pole.tolist(), growth_grid=growth_grid,
        error_sqrt_energy_estimate=bound, error_sqrt_energy_estimate_log=log_bound,
        continuum_growth_constant_certified=False, continuum_residual_enclosed=False,
        continuum_error_bound_certified=False, common_normalization_assigned=False,
        temporal_continuation='Interior C2 piecewise quintic Hermite through retained q,v and ODE nodal acceleration; wall lift uses exact sine^4 pulse and its derivatives',
        temporal_continuation_ODE_defect_included=True,
        coefficient_derivative_method=coefficients['coefficient_derivatives'],
        derivative_and_quadrature_roundoff_enclosed=False,
        error_domain='zero initial perturbation; zero wall trace; finite-energy Friedrichs pole',
        energy_formula='E=1/2 integral (pi^2/e+r a_rho^2+V a^2); pi=e(a_t-beta a_rho)',
        strong_residual_formula='e a_tt-2e beta a_trho-(e beta)prime a_t-(r-e beta^2)a_rhorho-(r-e beta^2)prime a_rho+V a',
        energy_estimate_formula='sqrt(E(T)) <= (1/sqrt(2)) integral exp(C(T-t)/2) norm(f(t))_(1/e) dt',
        action_trace_pairing_error_bound=None,
        pairing_bound_status='Requires advanced boundary adjoint and its own residual; energy norm alone does not bound conormal trace',
        native_heat_evaluated=False, physical_Pauli_contraction=False,
        scope='EVALUATED_CONTINUUM_RESIDUAL_ESTIMATE_OF_FROZEN_ACTUAL_E1_PLUS_CONTROL_TRACE_COMPONENT')
    return result


def advanced_goal_residual_estimate(pair, info, repository=ROOT, *,
        radial_quadrature=960, temporal_quadrature=4, growth_grid=8193):
    """Apply the continuum Green identity to the compact boundary pairing.

    If L a_num=R, L z=0, z|wall=g and z(D)=pi_z(D)=0, then
    F_exact=F_direct_num+integral z R.  An approximate advanced solution adds
    its residual-energy remainder.  The resulting numbers are quadrature /
    sampled-coefficient ESTIMATES, not a certified conormal enclosure.
    """
    Dtime = info['source_duration']
    primal, adjoint = pair['retarded'], pair['advanced']
    t, tw, q, v, acc = _temporal_samples(primal, info, temporal_quadrature, Dtime)
    u, uw, z, zv, zacc = _temporal_samples(adjoint, info, temporal_quadrature, Dtime)
    if not np.allclose(t, Dtime-u[::-1], rtol=0, atol=4e-16) or not np.allclose(tw, uw[::-1], rtol=0, atol=4e-16):
        raise ValueError('Matched reflected temporal quadrature required')
    x, rw = leggauss(radial_quadrature)
    rho, rw = (x+1)*WALL/2, rw*WALL/2
    B, Br, Brr = radial_basis_two_jet(rho, info['radial_order'])
    c = frozen_coefficient_one_jet(rho, repository)
    cr = frozen_coefficient_one_jet(rho, repository, shift_sign=-1)
    rp_norm, rz_norm, contractions, lift_contractions = [], [], [], []
    z_original = z[::-1]
    for start in range(0, len(t), 256):
        sl = slice(start, start+256)
        R = strong_residual(q[sl]@B.T, v[sl]@B.T, acc[sl]@B.T,
            q[sl]@Br.T, v[sl]@Br.T, q[sl]@Brr.T, c)
        Rz = strong_residual(z[sl]@B.T, zv[sl]@B.T, zacc[sl]@B.T,
            z[sl]@Br.T, zv[sl]@Br.T, z[sl]@Brr.T, cr)
        rp_norm.append(np.sqrt((R*R/c['electric'])@rw))
        rz_norm.append(np.sqrt((Rz*Rz/cr['electric'])@rw))
        contractions.append((R*(z_original[sl]@B.T))@rw)
        lift_contractions.append((R*B[:, -1])@rw*q[sl, -1])
    rp, rz = np.concatenate(rp_norm), np.concatenate(rz_norm)
    contraction = float(np.dot(tw, np.concatenate(contractions)))
    lift = float(np.dot(tw, np.concatenate(lift_contractions)))
    grho = np.linspace(0, WALL, growth_grid)[1:]
    cg = frozen_coefficient_one_jet(grho, repository, shift_sign=-1)
    rates = normal_energy_growth_rates(cg)
    Cback = float(max(np.max(rates), np.max(cg['pole_rates'])))
    kmin = float(min(np.min(cg['potential']/cg['electric']),
                    np.min(c['potential']/c['electric'])))
    # Causal integral at each reverse-time node.  Trapezoidal accumulation
    # is independently refined by increasing the Gauss nodes per interval.
    # It is NOT a guaranteed overestimate of the positive integral.
    discounted = np.exp(-.5*Cback*u)*rz
    cumulative = cumulative_trapezoid(np.concatenate(([0.], discounted)),
        x=np.concatenate(([0.], u)), initial=0)[1:]
    sqrtEz = np.exp(.5*Cback*u)*cumulative/np.sqrt(2)
    remainder = float(np.dot(uw, rp[::-1]*np.sqrt(2/kmin)*sqrtEz))
    wall = frozen_coefficient_one_jet(np.array([WALL]), repository)
    Dw = radial_basis_two_jet(np.array([WALL]), info['radial_order'])[1][0]
    direct = float(np.dot(tw, q[:, -1]*(q@Dw)*wall['radial'][0]))
    weak_rows = acc@primal['M'].T+v@(primal['N'].T-primal['N']).T+q@primal['K'].T
    weak = float(np.dot(tw, q[:, -1]*weak_rows[:, -1]))
    return dict(radial_quadrature=radial_quadrature, temporal_quadrature=temporal_quadrature,
        end_time=Dtime, time_samples=len(t), growth_grid=growth_grid,
        advanced_sampled_growth_constant=Cback,
        sampled_potential_over_electric_minimum=kmin,
        primal_strong_residual_L2_time_space=float(np.sqrt(np.dot(tw, rp*rp))),
        advanced_strong_residual_L2_time_space=float(np.sqrt(np.dot(uw, rz*rz))),
        direct_conormal_trace_pairing=direct, finite_weak_trace_pairing=weak,
        advanced_residual_contraction=contraction, trace_lift_residual_contraction=lift,
        direct_plus_advanced_residual_correction=direct+contraction,
        finite_weak_correction=contraction-lift,
        finite_weak_plus_goal_correction=weak+contraction-lift,
        strong_weak_green_identity_defect=abs(weak-direct-lift),
        advanced_energy_remainder_estimate=remainder,
        relative_remainder_estimate=remainder/max(abs(weak), np.finfo(float).tiny),
        goal_formula='F_exact=F_direct_num+integral z_num R+integral (z-z_num)R',
        remainder_formula='abs(remainder)<=integral norm(R(t))_(1/e)*sqrt(2 E_z_error(t)/inf(V/e)) dt',
        endpoint_terms='zero retarded initial data, zero advanced terminal data, equal prescribed wall trace, Friedrichs pole',
        bound_premises=['Cback >= supremum of reversed-shift energy rates',
            'kmin <= infimum V/e', 'certified strong residual norms and time integrals'],
        bound_premises_certified=False, continuum_pairing_enclosed=False,
        numerical_Galerkin_orthogonality_is_physical_cancellation=False,
        native_heat_evaluated=False, physical_Pauli_contraction=False,
        scope='EVALUATED_GOAL_SPECIFIC_CONTINUUM_PAIRING_ESTIMATE_FOR_CONTROL_TRACE')


def materialize_energy_residual(repository=ROOT, *, run_index=2,
        radial_quadratures=(640, 960, 1280), temporal_quadratures=(2, 3, 4)):
    """Consume the retained solution; do not rerun its scientific trajectory."""
    repository = Path(repository)
    for values, minimum in ((radial_quadratures, 16), (temporal_quadratures, 2)):
        if (len(values) < 2 or any(type(n) is not int or n < minimum for n in values)
                or tuple(sorted(set(values))) != tuple(values)):
            raise ValueError('at least two increasing valid quadrature orders required')
    data, info, provenance = load_retained_probe(repository, run_index=run_index)
    runs = [evaluate_continuum_residual(data, info, repository,
        radial_quadrature=n, temporal_quadrature=temporal_quadratures[-1])
        for n in radial_quadratures]
    runs.extend(evaluate_continuum_residual(data, info, repository,
        radial_quadrature=radial_quadratures[-1], temporal_quadrature=n)
        for n in temporal_quadratures[:-1])
    pair, pair_info, pair_provenance = load_support_adjoint_pair(repository)
    goals = [advanced_goal_residual_estimate(pair, pair_info, repository,
        radial_quadrature=n, temporal_quadrature=temporal_quadratures[-1])
        for n in radial_quadratures]
    goals.extend(advanced_goal_residual_estimate(pair, pair_info, repository,
        radial_quadrature=radial_quadratures[-1], temporal_quadrature=n)
        for n in temporal_quadratures[:-1])
    source = Path(__file__).resolve()
    imported_sources = ['ae3_c2_photon_symbol_audit.py', 'muon_birth_candidate_geometry_action.py',
        'muon_moving_geometric_action.py', 'muon_parent_maxwell_velocity.py',
        'muon_parent_retarded_hypercharge.py']
    source_records = []
    for name in imported_sources:
        path = repository/'src/bhsm/interface'/name
        raw = path.read_bytes()
        source_records.append(dict(path=path.relative_to(repository).as_posix(),
            bytes=len(raw), sha256=sha256(raw).hexdigest()))
    growth_checks = []
    for count in (4097, 8193, 16385):
        grid = np.linspace(0, WALL, count)[1:]
        cg = frozen_coefficient_one_jet(grid, repository)
        rates = normal_energy_growth_rates(cg)
        growth_checks.append(dict(grid=count,
            forward_C_sample=float(max(np.max(rates), np.max(cg['pole_rates']))),
            backward_C_sample=float(max(np.max(-rates), np.max(-cg['pole_rates']))),
            potential_over_electric_min_sample=float(np.min(cg['potential']/cg['electric'])),
            uniform_extrema_certified=False))
    return dict(provenance=provenance,
        producer_source=dict(path=source.relative_to(repository).as_posix(),
            sha256=sha256(source.read_bytes()).hexdigest()),
        analytic_coefficient_and_domain_sources=source_records,
        retained_run_index=run_index, retained_weak_pairing=info['boundary_trace_contraction'],
        retained_direct_pairing=info['direct_conormal_trace_pairing'],
        retained_finite_interior_residual_max=info['interior_algebraic_residual_max'],
        boundary_flux_domain='Analytic beta(pi/2)=0; trace-zero error has pi=0 there; Friedrichs pole flux tends to zero',
        runs=runs, advanced_pair_provenance=pair_provenance,
        advanced_goal_estimates=goals, numerical_refinement_is_enclosure=False,
        selected_refinement_index=len(radial_quadratures)-1,
        selected_forward_residual_estimate=runs[len(radial_quadratures)-1],
        selected_advanced_goal_estimate=goals[len(radial_quadratures)-1],
        growth_coercivity_grid_refinement=growth_checks,
        last_radial_refinement_estimates=dict(
            strong_residual_L2_difference=abs(runs[len(radial_quadratures)-1]['residual_L2_time_space_weighted']
                -runs[len(radial_quadratures)-2]['residual_L2_time_space_weighted']),
            goal_remainder_difference=abs(goals[len(radial_quadratures)-1]['advanced_energy_remainder_estimate']
                -goals[len(radial_quadratures)-2]['advanced_energy_remainder_estimate'])),
        last_temporal_refinement_estimates=dict(
            strong_residual_L2_difference=abs(runs[len(radial_quadratures)-1]['residual_L2_time_space_weighted']
                -runs[-1]['residual_L2_time_space_weighted']),
            goal_remainder_difference=abs(goals[len(radial_quadratures)-1]['advanced_energy_remainder_estimate']
                -goals[-1]['advanced_energy_remainder_estimate'])),
        physical_source_selected=False, complete_native_kernel=False,
        physical_Pauli_contraction=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--repository', default=str(ROOT))
    args = parser.parse_args()
    output = Path(args.output)
    packet = materialize_energy_residual(args.repository)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')


if __name__ == '__main__':
    main()
