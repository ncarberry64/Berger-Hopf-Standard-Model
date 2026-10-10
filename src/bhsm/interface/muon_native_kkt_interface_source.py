"""Differentiate one prescribed interface source in its scalar-action KKT dual.

This finite real (or explicitly realified) weak-action chart derives its
entries from L=S+lambda^T R. It is not an adapter for Gate-7 residual rows.
The chart's owner/domain/pairing and normal-displacement provenance must be
supplied; metadata does not prove a physical action identification. Unknown
sectors cannot be represented by absent entries or implicit zeros.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import sympy as sp
from flint import arb, arb_mat, ctx

from .muon_native_interface_bulk_forcing import seven_port_forcing_direction


ACTION_SECTORS = (
    'bulk_geometric', 'reset', 'trace_momentum_conormal', 'dynamic_flux',
    'Wentzell', 'scalar_topographic', 'contact',
)
CONSTRAINT_SECTORS = ('gauge_BRST_constraints', 'multiplier_owned_constraints')


@dataclass(frozen=True)
class SignedSector:
    """One already pulled-back action sector; signs are applied exactly once."""
    name: str
    expression: sp.Expr
    sign: int = 1
    zero_provenance: str | None = None


@dataclass(frozen=True)
class OwnerAction:
    """A supplied complete scalar action in one owned real weak-form chart.

    Only one source s is present. Its geometric direction is independently
    recorded by source_provenance and the existing 3+2+2 port image b_psi.
    The source direction is not selected by this algebra. Constraints are
    uneliminated rows; multipliers are independent unknown KKT coordinates.
    """
    eta: tuple[sp.Symbol, ...]
    multipliers: tuple[sp.Symbol, ...]
    source: sp.Symbol
    action_sectors: tuple[SignedSector, ...]
    constraints: tuple[sp.Expr, ...]
    base: Mapping[sp.Symbol, sp.Expr]
    owner_identity: Mapping[str, str]
    source_provenance: str
    b_psi: sp.Matrix
    required_sectors: tuple[str, ...] = ACTION_SECTORS
    constraint_provenance: tuple[str, ...] = ()

    def validate(self):
        coordinates = self.eta + self.multipliers + (self.source,)
        if not self.eta or len(set(coordinates)) != len(coordinates):
            raise ValueError('distinct nonempty field, multiplier and source coordinates required')
        if any(not isinstance(x, sp.Symbol) or x.is_real is not True for x in coordinates):
            raise ValueError('explicit real or realified action coordinates required')
        if len(self.constraints) != len(self.multipliers):
            raise ValueError('one independent multiplier per uneliminated constraint required')
        if len(self.constraint_provenance) != len(self.constraints) or any(not p for p in self.constraint_provenance):
            raise ValueError('each constraint needs signed owner provenance')
        if any(not self.owner_identity.get(k) for k in ('action', 'domain', 'pairing', 'branch')):
            raise ValueError('action, domain, pairing and branch identity required')
        if (not self.source_provenance or not isinstance(self.b_psi, sp.MatrixBase)
                or self.b_psi.shape != (7, 1)):
            raise ValueError('independent normal-source provenance and exactly seven port coordinates required')
        names = tuple(t.name for t in self.action_sectors)
        if len(set(names)) != len(names) or set(names) != set(self.required_sectors):
            raise ValueError('signed action sectors omitted or double counted')
        if not names:
            raise ValueError('explicit signed action sector ledger required')
        for term in self.action_sectors:
            if term.expression is None:
                raise ValueError(term.name + ': UNEVALUATED action sector')
            if term.sign not in (-1, 1):
                raise ValueError('each signed sector must occur exactly once')
            expression = sp.sympify(term.expression)
            if expression == 0 and not term.zero_provenance:
                raise ValueError(term.name + ': explicit zero needs action provenance')
            if expression.free_symbols.intersection(self.multipliers):
                raise ValueError('multiplier terms belong in lambda^T R exactly once')
        if any(r is None for r in self.constraints):
            raise ValueError('UNEVALUATED constraint sector')
        if any(sp.sympify(r).free_symbols.intersection(self.multipliers) for r in self.constraints):
            raise ValueError('constraints must be independent of their KKT multipliers')
        if any(x not in self.base for x in coordinates):
            raise ValueError('fixed owned field/source/multiplier base required')
        if sp.sympify(self.base[self.source]) != 0:
            raise ValueError('normal displacement chart is based at s=0')
        for value in list(self.base.values()) + list(self.b_psi):
            value = sp.sympify(value)
            if value.free_symbols or value.is_real is not True or value.is_finite is not True:
                raise ValueError('evaluated finite real base and port data required')
        return coordinates


def _at_base(expression, action):
    value = expression.subs(action.base, simultaneous=True)
    if isinstance(value, sp.MatrixBase):
        value = value.applyfunc(sp.simplify)
        entries = list(value)
    else:
        value = sp.simplify(value)
        entries = [value]
    if any(x.free_symbols or x.is_real is not True or x.is_finite is not True for x in entries):
        raise ValueError('consumed action derivatives remain UNEVALUATED')
    return value


def differentiate_owner_kkt(action: OwnerAction):
    """Produce h=(L_eta,s,R_s) at FIXED eta and lambda from the action.

    No lambda_s symbol or solved response enters these partial derivatives.
    R_eta,s is directional in the single consumed s, not a generic second
    constraint tensor. H is the required internal KKT Hessian itself.
    """
    variables = action.validate()
    eta, lam, s = action.eta, action.multipliers, action.source
    S = sum(term.sign * sp.sympify(term.expression) for term in action.action_sectors)
    R = sp.Matrix(len(action.constraints), 1, list(map(sp.sympify, action.constraints)))
    L = S + sum(l * r for l, r in zip(lam, R))
    L_eta = sp.Matrix([sp.diff(L, x) for x in eta])
    E = L_eta.col_join(R)
    E_base = _at_base(E, action)
    if E_base != sp.zeros(len(eta) + len(lam), 1):
        raise ValueError('owned stationary base required: L_eta=0 and R=0')
    R_eta = R.jacobian(eta)
    S_eta_s = sp.Matrix([sp.diff(S, x, s) for x in eta])
    R_eta_s = R_eta.diff(s)
    R_s = R.diff(s)
    multiplier_contact = R_eta_s.T * sp.Matrix(len(lam), 1, list(lam))
    L_eta_s = S_eta_s + multiplier_contact
    h = L_eta_s.col_join(R_s)
    H = E.jacobian(eta + lam)
    # Independent differentiation of the full KKT residual, not cached rows.
    if (E.diff(s) - h).applyfunc(sp.simplify) != sp.zeros(E.rows, 1):
        raise ArithmeticError('action source decomposition disagrees with direct residual derivative')
    evaluated = {key: _at_base(value, action) for key, value in dict(
        S_eta_s=S_eta_s, R_eta_s=R_eta_s, R_s=R_s,
        multiplier_contact=multiplier_contact, L_eta_s=L_eta_s,
        L_etaeta=L_eta.jacobian(eta), R_eta=R_eta,
        S_ss=sp.diff(S, s, 2), R_ss=R.diff(s, 2),
        multiplier_source_contact=sum(l * sp.diff(r, s, 2) for l, r in zip(lam, R)),
        L_ss=sp.diff(L, s, 2), H_KKT=H, h_psi=h,
    ).items()}
    if evaluated['H_KKT'] != evaluated['H_KKT'].T:
        raise ArithmeticError('supplied real scalar-action chart must have a symmetric KKT Hessian')
    return dict(**evaluated, E_base=E_base, L=L, S=S, E=E,
                variables=eta + lam, source=s,
                owner_identity=dict(action.owner_identity),
                fixed_coordinates=tuple(str(x) for x in eta + lam),
                source_provenance=action.source_provenance, b_psi=action.b_psi,
                direct_source_derivative=_at_base(E.diff(s), action))


def _amat(matrix):
    return arb_mat([[arb(str(x)) for x in row] for row in matrix.tolist()])


def _arb_scalar(value):
    """Exact rational conversion only: never silently narrow a transcendental."""
    if sp.sympify(value).is_Rational is not True:
        raise ValueError('Arb replay currently requires exact rational weak-form entries')
    return arb(str(value))


def solve_owner_kkt(action: OwnerAction):
    """One source-column solve with retained field and multiplier reactions.

    Exact rational algebra and Arb replay both solve the same column. Neither
    uses an explicit inverse. Interval residual inclusion only validates the
    supplied finite arithmetic; it is not a continuum error certificate.
    """
    data = differentiate_owner_kkt(action)
    H, h = data['H_KKT'], data['h_psi']
    if any(x.is_Rational is not True for x in list(H) + list(h) + [data['L_ss']]):
        raise ValueError('exact rational weak-action data required for this replay')
    delta = H.LUsolve(-h)
    z = sp.simplify(data['L_ss'] + (h.T * delta)[0])
    replay = (H * delta + h).applyfunc(sp.simplify)
    # A full L-path evaluation gives the direct quadratic independently of
    # the assembled H/h contraction and retains lambda0 R_ss contacts.
    epsilon = sp.Symbol('_kkt_path_epsilon', real=True)
    path = dict(action.base)
    path.update({x: sp.sympify(action.base[x]) + epsilon * delta[k]
                 for k, x in enumerate(data['variables'])})
    path[action.source] = epsilon
    direct = sp.simplify(sp.diff(data['L'].subs(path, simultaneous=True), epsilon, 2).subs(epsilon, 0))
    difference = sp.simplify(direct - z)
    if replay != sp.zeros(H.rows, 1) or difference != 0:
        raise ArithmeticError('owner response/direct quadratic replay failed')
    AH, ah = _amat(H), _amat(h)
    adelta = -AH.solve(ah)
    areplay = AH * adelta + ah
    az = _arb_scalar(data['L_ss']) + (ah.transpose() * adelta)[0, 0]
    adirect = (_arb_scalar(data['L_ss'])
               + (adelta.transpose() * AH * adelta)[0, 0]
               + 2 * (ah.transpose() * adelta)[0, 0])
    if not all(x.contains(0) for x in areplay.entries()) or not (az - adirect).contains(0):
        raise ArithmeticError('Arb owned-coordinate replay failed')
    n = len(action.eta)
    return dict(**data, delta_psi=delta, delta_eta_psi=delta[:n, :],
                delta_lambda_psi=delta[n:, :], replay=replay, z_psi=z,
                direct_quadratic=direct, direct_minus_schur=difference,
                arb_delta=adelta, arb_replay=areplay, arb_z=az,
                arb_direct_minus_schur=adirect - az,
                precision_bits=ctx.prec)


def _control_geometry():
    """Prescribed finite geometry only; never a BHSM normal-source producer."""
    q = sp.Rational
    operands = dict(trace_map=sp.eye(3),
                    state_direction=sp.Matrix([q(1, 5), q(2, 7), -q(1, 3)]),
                    trace_shape=sp.Matrix([q(1, 11), -q(1, 13), q(1, 17)]),
                    momentum=sp.Matrix([q(2, 5), -q(3, 7)]),
                    force=sp.Matrix([q(11, 13), q(5, 17)]),
                    conormal=sp.Matrix([q(1, 19), -q(2, 23)]),
                    momentum_mixed=sp.Matrix([q(3, 29), -q(5, 31)]),
                    momentum_rate_direction=sp.Matrix([q(7, 37), q(11, 41)]))
    b = (operands['trace_map'] * operands['state_direction'] + operands['trace_shape']).col_join(
        operands['momentum']).col_join(operands['force'] - operands['conormal']
                                     - operands['momentum_mixed'] - operands['momentum_rate_direction'])
    produced = seven_port_forcing_direction(**{key: _amat(value) for key, value in operands.items()})
    if not all((produced[k, 0] - arb(str(b[k]))).contains(0) for k in range(7)):
        raise ArithmeticError('existing seven-port kinematics disagrees with exact control')
    return b, operands


def finite_control_action(v=sp.S.Zero, J=sp.S.Zero):
    """A complete *control* action with nonzero constraint multiplier/contact.

    v/J vary this finite family while its stationary eta0/lambda0 remain
    exact. This makes total branch impedance jets differentiable without
    importing any physical mode, state or measured quantity.
    """
    q = sp.Rational
    eta0, eta1, lam, s = sp.symbols('eta0 eta1 lambda0 s', real=True)
    eta = sp.Matrix([eta0, eta1])
    b, _ = _control_geometry()
    A = sp.Matrix([[4 + v + v * J / 7, 1 + J / 5], [1 + J / 5, 3 + J + v * J / 11]])
    G = sp.Matrix([[q(1, 5), q(1, 13)], [q(1, 13), q(1, 7)]])
    d = sp.Matrix([[1, 1]])
    C = sp.Matrix([[q(1, k + 2) for k in range(7)], [(-1)**k * q(1, k + 3) for k in range(7)]])
    c = C * b + sp.Matrix([v / 9 + v * J / 17, J / 8])
    e = sp.Matrix([[b[0] / 3 + J / 19, b[6] / 5 + v / 23]])
    rho = (sp.Matrix([[q(1, k + 7) for k in range(7)]]) * b)[0]
    kappa = q(2, 7) + v * J / 29
    qss = (b.T * (9 * sp.eye(7)) * b)[0] + v / 31 + J / 37 + v * J / 41
    lambda_base = q(3, 2)
    bulk = (eta.T * A * eta)[0] / 2 - lambda_base * (d * eta)[0]
    bulk += s * (eta.T * c)[0] + s**2 * qss / 2
    constraint = (d * eta)[0] + (eta.T * G * eta)[0] / 2
    constraint += s * ((e * eta)[0] - rho) + s**2 * kappa / 2
    sectors = (SignedSector('bulk_geometric', bulk),) + tuple(
        SignedSector(name, sp.S.Zero, zero_provenance='absent by definition of this finite control action')
        for name in ACTION_SECTORS[1:])
    return OwnerAction(eta=(eta0, eta1), multipliers=(lam,), source=s,
                       action_sectors=sectors, constraints=(constraint,),
                       base={eta0: 0, eta1: 0, lam: lambda_base, s: 0},
                       owner_identity=dict(action='FINITE_CONTROL_ACTION_V1', domain='finite real chart R2 x R1 x R1',
                                           pairing='scalar action covector pairing in the declared real chart',
                                           branch='eta=0,lambda=3/2 stationary finite v/J family'),
                       source_provenance='prescribed finite normal-direction kinematics; NOT a physical BHSM xi_psi',
                       b_psi=b, constraint_provenance=('single control constraint; gauge/BRST rows absent by definition',))


def finite_control_branch_jets():
    """Differentiate z of the SAME controlled action family along v,J.

    The direction and chart are fixed by definition in this finite family.
    One symbolic KKT column supplies z(v,J); no second source tensor is made.
    Surface/inertia polynomials are explicitly prescribed control sectors.
    """
    v, J = sp.symbols('v J', real=True)
    action = finite_control_action(v, J)
    S = sum(t.sign * t.expression for t in action.action_sectors)
    L = S + sum(l * r for l, r in zip(action.multipliers, action.constraints))
    E = sp.Matrix([sp.diff(L, x) for x in action.eta] + list(action.constraints))
    H = E.jacobian(action.eta + action.multipliers).subs(action.base, simultaneous=True)
    h = E.diff(action.source).subs(action.base, simultaneous=True)
    Lss = sp.diff(L, action.source, 2).subs(action.base, simultaneous=True)
    delta = H.LUsolve(-h)
    z = Lss + (h.T * delta)[0]
    surface = 2 + v / 3 + J / 5 + v * J / 7
    inertia = 3 + v / 11 + J / 13 + v * J / 17
    def jets(expression):
        return {key: str(sp.simplify(value.subs({v: 0, J: 0}))) for key, value in dict(
            value=expression, v=sp.diff(expression, v), J=sp.diff(expression, J), vJ=sp.diff(expression, v, J)).items()}
    return dict(owner_z=jets(z), surface_jacobi=jets(surface), inertia=jets(inertia))
