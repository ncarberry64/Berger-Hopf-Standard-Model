"""Finite anchored chart of the owned normalized reciprocal-join response.

The two harmonics already used by the normal trial are determined by the
existing two material-wall traces, not new physical coefficients.  Their
implicit derivatives supply a genuine finite response chart in place of
using a second-order sigma polynomial as a nonlinear continuation.
"""
from __future__ import annotations

from functools import lru_cache
import math
import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_moving_geometric_action import _sin, _cos, _sqrt, _atanh, _fields
from .aether_n3_exact_full_local_action_jet_v17_60 import _linear, _variables
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0, HOPF_ORBIT_VOLUME
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient


class _Series3:
    """Univariate Taylor coefficients through degree three, factorial divided."""
    __array_priority__ = 1000
    def __init__(self, coefficients):
        self.c = np.asarray(coefficients, float)
        if self.c.shape[0] != 4:
            raise ValueError('four Taylor coefficients required')
    @classmethod
    def constant(cls, value):
        a = np.asarray(value, float)
        return cls(np.stack((a, np.zeros_like(a), np.zeros_like(a), np.zeros_like(a))))
    @classmethod
    def variable(cls, value):
        return cls(np.array([value, 1., 0., 0.]))
    def __add__(self, other):
        o = other if isinstance(other, _Series3) else _Series3.constant(other)
        return _Series3(np.stack([self.c[k]+o.c[k] for k in range(4)]))
    __radd__ = __add__
    def __neg__(self):
        return _Series3(-self.c)
    def __sub__(self, other):
        return self+(-other if isinstance(other, _Series3) else -np.asarray(other))
    def __rsub__(self, other):
        return -self+other
    def __mul__(self, other):
        o = other if isinstance(other, _Series3) else _Series3.constant(other)
        return _Series3(np.stack([sum(self.c[j]*o.c[k-j] for j in range(k+1)) for k in range(4)]))
    __rmul__ = __mul__
    def reciprocal(self):
        b = [1/self.c[0]]
        for k in range(1, 4):
            b.append(-sum(self.c[j]*b[k-j] for j in range(1, k+1))/self.c[0])
        return _Series3(np.stack(b))
    def __truediv__(self, other):
        return self*(other.reciprocal() if isinstance(other, _Series3) else 1/np.asarray(other))
    def integral(self, weights):
        return _Series3(self.c@weights)


def _series_sin(x):
    c = x.c; s = np.sin(c[0]); v = np.cos(c[0])
    return _Series3(np.stack((s, v*c[1], v*c[2]-s*c[1]**2/2,
        v*c[3]-s*c[1]*c[2]-v*c[1]**3/6)))


@lru_cache(maxsize=8)
def _rule(points):
    if not isinstance(points, int) or points < 24:
        raise ValueError('resolved positive normalization quadrature required')
    x, w = np.polynomial.legendre.leggauss(points)
    return (x+1)/2, w/2


def _constraint_series(a, delta, points):
    x, w = _rule(points); wall = math.pi/4+delta
    chi = math.pi*x/2
    f = _Series3.constant(chi)+a[0]*np.sin(2*chi)+a[1]*np.sin(6*chi)
    s = _series_sin(2*f); Z = (s*s*.25).integral(w)*(math.pi/2)
    c = wall*x; fp = c+a[0]*_series_sin(2*c)+a[1]*_series_sin(6*c)
    sp = _series_sin(2*fp); N = (sp*sp*.25).integral(w)*wall
    fw = wall+a[0]*_series_sin(2*wall)+a[1]*_series_sin(6*wall)
    return np.stack(((fw-math.pi/4).c, (N/Z-.5).c)), Z.c


def _constraints_and_jacobian(a, delta, points):
    aa = [_Series3.constant(x) for x in a]; d = _Series3.constant(delta)
    value, _ = _constraint_series(aa, d, points); J = np.empty((2, 2))
    for k in range(2):
        variables = [_Series3.constant(x) for x in a]; variables[k] = _Series3.variable(a[k])
        E, _ = _constraint_series(variables, d, points); J[:, k] = E[:, 1]
    return value[:, 0], J


def anchored_join_coefficients(delta, *, points=96, tolerance=3e-15, max_iterations=16):
    """Solve f(wall)=pi/4 and normalized sigma(wall)=0.

    f=chi+a1 sin(2chi)+a3 sin(6chi), wall=pi/4+delta.  First, second and
    third derivatives follow from implicit Taylor equations with the same
    quadrature, not finite differences or an independently chosen profile.
    The sufficient lower bound f'>=1-2|a1|-6|a3| is retained explicitly.
    """
    if not np.isfinite(delta) or abs(delta) >= math.pi/4:
        raise ValueError('local material wall chart required')
    a = -np.array([21., 5.])*float(delta)/16; history = []
    for k in range(max_iterations):
        E, J = _constraints_and_jacobian(a, float(delta), points); norm = float(np.max(abs(E)))
        if norm <= tolerance:
            break
        step = np.linalg.solve(J, -E); accepted = False
        for j in range(14):
            damping = 2.**(-j); trial = a+damping*step
            if 1-2*abs(trial[0])-6*abs(trial[1]) <= 0:
                continue
            newE, _ = _constraints_and_jacobian(trial, float(delta), points)
            if np.max(abs(newE)) < norm:
                accepted = True; break
        history.append(dict(iteration=k, residual=norm, damping=damping, accepted=accepted))
        if not accepted:
            raise ValueError('anchored chart Newton stalled within the monotone domain')
        a = trial
    E, J = _constraints_and_jacobian(a, float(delta), points)
    if np.max(abs(E)) > tolerance or 1-2*abs(a[0])-6*abs(a[1]) <= 0:
        raise ValueError('anchored normalized chart not solved in the monotone domain')
    t = np.zeros((2, 4)); t[:, 0] = a
    for order in range(1, 4):
        equations, _ = _constraint_series([_Series3(row) for row in t], _Series3.variable(delta), points)
        t[:, order] = np.linalg.solve(J, -equations[:, order])
    equations, normalization = _constraint_series([_Series3(row) for row in t], _Series3.variable(delta), points)
    derivatives = t[:, 1:]*np.array([1., 2., 6.])
    return dict(coefficients=a, derivatives=derivatives, Taylor_coefficients=t,
        anchor_residual=E, anchor_Taylor_residual=equations, implicit_jacobian=J,
        normalization=normalization[0], normalization_derivatives=normalization[1:]*np.array([1., 2., 6.]),
        monotone_derivative_lower_bound=float(1-2*abs(a[0])-6*abs(a[1])), points=points, history=history,
        W_owner='aether_eta_sigma_response_constraint_v15_40.response_constraint_action',
        W='sin(f)^2*cos(f)^2=(1/4)sin(2f)^2', new_physical_coefficient=False,
        physical_mode_or_formation_selected=False)


def _compose_scalar(x, value, first, second):
    return Jet(value, first*x.gradient, first*x.hessian+second*np.outer(x.gradient, x.gradient))


def _sigma_partials(delta, chi, chart):
    """Literal normalized cumulative response with analytic partials."""
    x, w = _rule(chart['points']); a = chart['coefficients']; ap = chart['derivatives'][:, 0]; app = chart['derivatives'][:, 1]
    c = float(chi)*x; basis = np.array([np.sin(2*c), np.sin(6*c)])
    f = c+a@basis; fd = ap@basis; fdd = app@basis
    W = .25*np.sin(2*f)**2; Wf = .5*np.sin(4*f); Wff = 2*np.cos(4*f)
    N = float(chi)*(w@W); Nd = float(chi)*(w@(Wf*fd)); Ndd = float(chi)*(w@(Wff*fd*fd+Wf*fdd))
    Z = chart['normalization']; Zd, Zdd = chart['normalization_derivatives'][:2]
    wall_basis = np.array([np.sin(2*chi), np.sin(6*chi)])
    fw = chi+a@wall_basis; fdw = ap@wall_basis
    fchi = 1+2*a[0]*np.cos(2*chi)+6*a[1]*np.cos(6*chi)
    Wwall = .25*np.sin(2*fw)**2; Wfwall = .5*np.sin(4*fw)
    if delta == 0.:
        # Z is known exactly at the base.  Keep the positive partial
        # quadrature N: chi/8-sin(4chi)/32 loses relative accuracy near0.
        Z = math.pi/16
    probability = N/Z
    value = probability-.5
    first = np.array([Nd/Z-N*Zd/Z**2, Wwall/Z])
    second = np.array([[Ndd/Z-2*Nd*Zd/Z**2-N*Zdd/Z**2+2*N*Zd*Zd/Z**3,
        Wfwall*fdw/Z-Wwall*Zd/Z**2], [Wfwall*fdw/Z-Wwall*Zd/Z**2, Wfwall*fchi/Z]])
    return value, first, second, probability


def exact_response_at(chi, delta, delta_rate, chart):
    """Full f/f'/f_dot/sigma twojets on one retained geometric vector."""
    if not all(isinstance(x, Jet) for x in (chi, delta, delta_rate)):
        raise ValueError('same scalar geometric jets required')
    a = [_compose_scalar(delta, chart['coefficients'][k], *chart['derivatives'][k, :2]) for k in range(2)]
    ap = [_compose_scalar(delta, *chart['derivatives'][k]) for k in range(2)]
    rate = [x*delta_rate for x in ap]
    f = chi+a[0]*_sin(2*chi)+a[1]*_sin(6*chi)
    spatial = 1+2*a[0]*_cos(2*chi)+6*a[1]*_cos(6*chi)
    temporal = rate[0]*_sin(2*chi)+rate[1]*_sin(6*chi)
    value, first, second, probability = _sigma_partials(delta.value, chi.value, chart)
    J = np.array([delta.gradient, chi.gradient])
    sigma = Jet(value, first@J, J.T@second@J+first[0]*delta.hessian+first[1]*chi.hessian)
    cumulative = Jet(probability, sigma.gradient, sigma.hessian)
    # The literal identity 1-4sigma^2=4p(1-p) avoids subtracting two
    # near-unit numbers at the pole.  It introduces no weight change.
    return dict(f=f, fprime=spatial, fdot=temporal, sigma=sigma,
        normalized_cumulative=cumulative, localization_weight=4*cumulative*(1-cumulative))


def exact_moving_cap_action_jet(order, coordinates, velocities, multipliers, *, points=96,
        source_value=0., source_rate=0., trial_normal=1., response_points=96):
    """Retained signed cap action with the finite anchored response applied.

    All metric, GHY/Hayward, Casimir, FR and normalization coefficients are
    unchanged.  Only the previous Taylor response is replaced by its solved
    owned cumulative map.  This is an admissible finite trial chart, not a
    selected physical mode, solved response adjoint or full formation branch.
    """
    if not all(np.isfinite(x) for x in (source_value, source_rate, trial_normal)):
        raise ValueError('finite trial source and normal required')
    inputs = [np.asarray(x, float) for x in (coordinates, velocities, multipliers)]
    nq = 1+3*order; nm = 2*order; dim = 2*nq+nm+2
    if any(x.shape != (size,) or not np.isfinite(x).all() for x, size in zip(inputs, (nq, nq, nm))):
        raise ValueError('finite retained geometric dimensions required')
    q, v, m = (_variables(np.asarray(x, float), offset, dim)
               for x, offset in zip(inputs, (0, nq, 2*nq)))
    if len(q) != nq or len(v) != nq or len(m) != nm:
        raise ValueError('retained dimensions required')
    src, rate = _variables(np.array([source_value, source_rate]), dim-2, dim)
    sk = (-1.)**np.arange(1, order+1); sj = (-1.)**np.arange(order)
    Cstar = RADIUS0*(q[0]+_linear(q[1:1+order], sk)+_linear(q[1+order:1+2*order], sj)).exp()
    logCdot = v[0]+_linear(v[1:1+order], sk)+_linear(v[1+order:1+2*order], sj)
    delta = trial_normal*src/Cstar; delta_rate = trial_normal*(rate-logCdot*src)/Cstar
    wall = math.pi/4+delta; chart = anchored_join_coefficients(float(delta.value), points=response_points)
    nodes, weights = _rule(points); bulk = Jet.constant(0., dim); inertia = Jet.constant(0., dim)
    for y, weight in zip(nodes, weights):
        chi = wall*y; F = _fields(order, q, v, m, chi); r = exact_response_at(chi, delta, delta_rate, chart)
        C, A, B, N = (F[name] for name in ('C', 'A', 'B', 'N'))
        Hc = (F['lc']-F['beta']*F['cp']-F['betap'])/N
        Ha = (F['la']-F['beta']*F['ap'])/N; Hb = (F['lb']-F['beta']*F['bp'])/N
        adm = Hc*Hc+3*Ha*Ha+3*Hb*Hb-(Hc+3*Ha+3*Hb)**2
        fn = (r['fdot']-F['beta']*r['fprime'])/N
        X = r['fprime']**2/C**2+3*_cos(r['f'])**2/A**2+3*_sin(r['f'])**2/B**2-fn*fn
        if not np.isfinite((1+X**3).value) or (1+X**3).value <= 0:
            raise ValueError('positive retained eta Legendre domain required')
        loc = r['localization_weight']; volume = C*A**3*B**3; spatial = A**3*B**3
        grav = 3*spatial/C*N*(F['np']*(F['ap']+F['bp'])+F['ap']**2+F['bp']**2+3*F['ap']*F['bp'])
        alg = N*volume*(3/A**2+3/B**2-.5*(15*5**(1/3)/4)-loc*(.5*X+.125*X**4)+.5*adm)
        bulk += weight*wall*(grav+alg)
        inertia += weight*wall*volume*loc*(1+X**3)/N
    if not np.isfinite(inertia.value) or inertia.value <= 0:
        raise ValueError('positive finite retained FR denominator required')
    FR = -.25/(2*HOPF_ORBIT_VOLUME**2*inertia)
    F = _fields(order, q, v, m, wall); A, B, N = (F[name] for name in ('A', 'B', 'N'))
    R4 = A*B/_sqrt(A*A+B*B); casimir = -standard_model_casimir_coefficient()/R4*N
    U = F['C']*(delta_rate+F['beta'])/N; theta = _atanh(U); rho = A**3*B**3
    rho_rate = 3*rho*(F['la']+F['lb']+(F['ap']+F['bp'])*delta_rate)
    boundary = -theta*rho_rate; area = -N*rho*_sqrt(1-U*U)
    trace = exact_response_at(wall, delta, delta_rate, chart)
    return dict(total=bulk+FR+casimir+boundary, bulk=bulk, FR=FR,
        fixed_wall_extension=bulk+FR+casimir, moving_GHY_Hayward=boundary,
        surface_per_gamma=area, retained_local_Casimir=casimir, FR_denominator=inertia,
        Cstar=Cstar, wall=wall, source_indices=(dim-2, dim-1), qdim=nq, mdim=nm,
        response_chart=chart, exact_f_trace=trace['f']-math.pi/4, exact_sigma_trace=trace['sigma'],
        exact_response_applied=True, physical_mode_or_formation_selected=False)


def exact_geometric_connection_coefficient_jets(order, q, velocity, multipliers, rho,
        *, source_value=0., source_rate=0., trial_normal=1., clock='coordinate_time', response_points=96):
    """Owned material Maxwell densities with the same finite anchored response.

    Geometry/connection pullback equations are unchanged.  Only sigma is
    evaluated by its exact full-domain normalized cumulative map; no ratio
    involving the previous quadratic approximation is used near the pole.
    Independent gauge inputs are material one-form components.
    """
    from .muon_parent_retarded_hypercharge import WALL
    if clock not in ('coordinate_time', 'boundary_proper_time'):
        raise ValueError('explicit common clock required')
    inputs = [np.asarray(x, float) for x in (q, velocity, multipliers)]
    nq = 1+3*order; dim = 2*nq+2*order+2
    if any(x.shape != (size,) or not np.isfinite(x).all() for x, size in zip(inputs, (nq, nq, 2*order))):
        raise ValueError('finite retained geometric dimensions required')
    rho = np.asarray(rho, float)
    if rho.ndim != 1 or not np.isfinite(rho).all() or np.any(rho <= 0) or np.any(rho > WALL):
        raise ValueError('owned regular material quadrature required')
    qj, vj, mj = (_variables(x, offset, dim) for x, offset in zip(inputs, (0, nq, 2*nq)))
    s, rate = _variables(np.array([source_value, source_rate]), dim-2, dim)
    sk = (-1.)**np.arange(1, order+1); sj = (-1.)**np.arange(order)
    Cstar = RADIUS0*(qj[0]+_linear(qj[1:1+order], sk)+_linear(qj[1+order:1+2*order], sj)).exp()
    logCdot = vj[0]+_linear(vj[1:1+order], sk)+_linear(vj[1+order:1+2*order], sj)
    delta = trial_normal*s/Cstar; delta_rate = trial_normal*(rate-logCdot*s)/Cstar
    wall = math.pi/4+delta; chart = anchored_join_coefficients(float(delta.value), points=response_points)
    jac = 2*wall/WALL; Nb = _linear(mj[:order], sk).exp()
    clock_lapse = Jet.constant(1., dim) if clock == 'coordinate_time' else Nb
    rows = []
    for rr in rho:
        chi = (float(rr)/WALL)*wall; fields = _fields(order, qj, vj, mj, chi)
        LF = _sqrt(fields['A']**2+fields['B']**2)
        radius = fields['A']*fields['B']/LF; Crho = fields['C']/2
        response = exact_response_at(chi, delta, delta_rate, chart)
        sigma = response['sigma']
        common = 2*math.pi**4*LF**5*response['localization_weight']
        lapse = fields['N']/clock_lapse; shift = 2*fields['beta']/clock_lapse
        adv = (2*float(rr)/WALL)*delta_rate/clock_lapse
        lam = fields['A']**2/LF**2
        lr = lam*(1-lam)*(fields['ap']-fields['bp'])
        lt = 2*lam*(1-lam)*(fields['la']-fields['lb'])/clock_lapse
        rows.append(dict(electric=jac*common*Crho*radius/lapse,
            electric_radial=common*radius**3/(lapse*Crho*jac), radial=common*lapse*radius/(Crho*jac),
            angular=jac*common*lapse*Crho/radius, shift=(shift+adv)/jac,
            connection_lambda=lam, lambda_tau=lt+adv*lr, lambda_rho=jac*lr,
            induced_lambda_tau_unadvected=lt, induced_lambda_rho_unadvected=lr,
            material_jacobian=jac, material_velocity=adv, boundary_lapse=Nb, sigma=sigma))
    return dict(rows=rows, clock=clock, coordinate_count=dim,
        chart='exact normalized anchored material sigma and wall; same q/qdot/m/s/sdot',
        gauge_field_policy='material one-form coefficients fixed in reference chart',
        induced_connection_motion_count=1, response_chart=chart, exact_response_applied=True)
