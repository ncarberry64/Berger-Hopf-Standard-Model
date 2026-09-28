"""Signed implicit-action contractions in one supplied current realization.

This is an evaluator, not a choice of formation history or endpoint.  Its
normal system must include every normal variable of the supplied realization.
A local 124-variable solve may be evaluated as a subsystem, but cannot be
passed off as the complete Gate-7 action. Arb outputs enclose the supplied
operands; domain/tail/discretization errors remain separate owned inputs.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable

from flint import arb, arb_mat


def checked(value, rows, cols, name):
    if not isinstance(value, arb_mat) or (value.nrows(), value.ncols()) != (rows, cols):
        raise ValueError(f'{name}: expected {rows}x{cols} Arb matrix')
    if not all(v.is_finite() for v in value.entries()):
        raise ArithmeticError(f'{name}: nonfinite operand')
    return value


@dataclass(frozen=True)
class ActionBase:
    """Identity of the same action family, including every coordinate convention."""
    state: str
    coefficients: str
    duration: str
    internal: str
    contact: str
    orientation_reset: str

    def __post_init__(self):
        if not all(isinstance(v, str) and v for v in vars(self).values()):
            raise ValueError('all common-base identifiers must be explicit')

    @property
    def digest(self):
        return sha256(json.dumps(vars(self), sort_keys=True).encode()).hexdigest()


@dataclass
class ActionSector:
    """Partial objective derivatives, prior to common internal elimination.

    ``objective_product(kind, direction, normal_direction)`` returns
    (Gamma_xi,d, Gamma_n,d). Here d=(u,0,dn) for H, or (0,v,dn) for B.
    Residual curvature is contracted separately once after the signed sum.
    No internal second-jet tensor is requested.
    """
    name: str
    base: ActionBase
    gamma_xi: arb_mat
    gamma_n: arb_mat
    objective_product: Callable | None = None


@dataclass
class ImplicitAction:
    base: ActionBase
    F_n: arb_mat
    F_xi: arb_mat
    F_P: Callable
    sectors: tuple[ActionSector, ...]
    required_sectors: tuple[str, ...]
    scope: str
    errors: dict
    residual_curvature_product: Callable | None = None
    normal_residual: arb_mat | None = None

    def validate(self):
        n, d = self.F_n.nrows(), self.F_xi.ncols()
        if n < 1 or d < 1 or not self.scope:
            raise ValueError('nonempty internal/physical frames and scope required')
        checked(self.F_n, n, n, 'F_n')
        checked(self.F_xi, n, d, 'F_xi')
        names = tuple(s.name for s in self.sectors)
        if len(set(names)) != len(names) or set(names) != set(self.required_sectors):
            raise ValueError('signed action sectors omitted or double counted')
        if not names:
            raise ValueError('explicit action sector ledger required')
        for sector in self.sectors:
            if sector.base != self.base:
                raise ValueError('mixed-base action assembly')
            checked(sector.gamma_xi, d, 1, sector.name+' Gamma_xi')
            checked(sector.gamma_n, n, 1, sector.name+' Gamma_n')
        return n, d


def evaluate_gate7_current_action(query, requested_products):
    """Return requested force or directional H/B using one signed adjoint.

    requested_products may contain q66=True, H66_u=<column>, B66x73_v=<column>.
    The underlying reducer also supports smaller dimensions for exact tests.
    Only one normal directional solve and one transpose solve per H/B product
    are needed. The final transpose solve maps the contracted normal output
    back to all physical directions, without storing Phi_xi.

    Supplied error evidence is returned verbatim. Missing uniform errors are
    not replaced by point radii or interpreted as zero.
    """
    n, d = query.validate()
    unknown = set(requested_products)-{'q66', 'H66_u', 'B66x73_v'}
    if unknown:
        raise ValueError('unknown requested product: '+str(sorted(unknown)))
    gn = sum((s.gamma_n for s in query.sectors), arb_mat(n, 1))
    gx = sum((s.gamma_xi for s in query.sectors), arb_mat(d, 1))
    eta = query.F_n.transpose().solve(gn)
    result = dict(base_SHA256=query.base.digest, scope=query.scope,
                  errors=query.errors, adjoint=eta,
                  adjoint_replay=query.F_n.transpose()*eta-gn)
    result['normal_residual'] = (None if query.normal_residual is None else
                                checked(query.normal_residual, n, 1, 'normal residual'))
    if requested_products.get('q66'):
        result['q66'] = checked(gx-query.F_xi.transpose()*eta, d, 1, 'q')
    for key, kind in [('H66_u', 'H'), ('B66x73_v', 'B')]:
        if key not in requested_products:
            continue
        direction = requested_products[key]
        checked(direction, d if kind == 'H' else 73, 1, key+' input')
        forcing = query.F_xi*direction if kind == 'H' else query.F_P(direction)
        checked(forcing, n, 1, 'directional normal forcing')
        dn = -query.F_n.solve(forcing)
        cx, cn = arb_mat(d, 1), arb_mat(n, 1)
        for sector in query.sectors:
            if sector.objective_product is None:
                raise ValueError(sector.name+': contracted objective curvature missing')
            sx, sn = sector.objective_product(kind, direction, dn)
            cx += checked(sx, d, 1, sector.name+' Gamma_xi,d')
            cn += checked(sn, n, 1, sector.name+' Gamma_n,d')
        if query.residual_curvature_product is None:
            raise ValueError('contracted residual curvature missing')
        # The callback returns +eta^T F_ab. Subtract once for L=Gamma-eta F.
        rx, rn = query.residual_curvature_product(kind, direction, dn, eta)
        cx -= checked(rx, d, 1, 'eta F_xi,d')
        cn -= checked(rn, n, 1, 'eta F_n,d')
        dual = query.F_n.transpose().solve(cn)
        result[key] = checked(cx-query.F_xi.transpose()*dual, d, 1, key)
        result[key+'_normal_replay'] = query.F_n*dn+forcing
        result[key+'_adjoint_replay'] = query.F_n.transpose()*dual-cn
    return result


def point_euclidean_enclosure(column):
    """Norm enclosure after signed composition, including supplied ball radii."""
    checked(column, column.nrows(), 1, 'column')
    return sum((v*v for v in column.entries()), arb(0)).nonnegative_part().sqrt()
