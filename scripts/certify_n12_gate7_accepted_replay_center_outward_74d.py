"""Certify the accepted replay center in the frozen causal 74D norm.

This is a certificate-local outward realization of the tracked retained N=12
action.  It deliberately does not import either high-precision scratch jet.
The action is differentiated with Arb distinct-direction mixed jets, so the
third and fourth derivatives are contracted before any norm is taken.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import os
from typing import Sequence

import numpy as np
from flint import arb, arb_mat, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (  # noqa: E402
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (  # noqa: E402
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (  # noqa: E402
    assemble_cancelled_arc_proper_time_coefficient_first_jet,
)


ORDER = 12
POINTS = 96
QDIM = 37
MDIM = 24
STATE = 98
REDUCED = 61
LOCAL = 13
PRECISION = 384
SHARD_REVISION = 2
TUBE_SHARD_REVISION = 1

BASE = ROOT / "artifacts" / "flagship_integration"
ENDPOINT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
OLD_JACOBIAN = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PRECONDITIONER = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
RESULT = BASE / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
DATA = RESULT.with_suffix(".npz")
WORK = BASE / ".accepted_replay_outward_74d_work"
FIRST_STOP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
KRAWCZYK_THEOREM = ROOT / "theory" / "n12_c2_stop_correlated_defect_krawczyk.md"
CONTINUUM_CHILD = (
    ROOT / "artifacts" / "n12_continuum_majorant_effectiveness"
    / "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
TRIAL_DESCRIPTOR_SCALE = 1.0e-7
TEST_DESCRIPTOR_SCALE = 1.0e6


def _a(value: float | int | str | arb) -> arb:
    return value if isinstance(value, arb) else arb(value)


def _object(value: object) -> np.ndarray:
    return np.asarray(value, dtype=object)


@lru_cache(maxsize=None)
def _partitions(mask: int) -> tuple[tuple[int, ...], ...]:
    if mask == 0:
        return ((),)
    first = mask & -mask
    rest = mask ^ first
    rows: list[tuple[int, ...]] = []
    for partition in _partitions(rest):
        rows.append((first,) + partition)
        for index in range(len(partition)):
            merged = list(partition)
            merged[index] |= first
            rows.append(tuple(sorted(merged)))
    return tuple(sorted(set(rows)))


@dataclass(frozen=True)
class Mixed:
    """Arb distinct-direction mixed jet with broadcast tensor legs."""

    d: tuple[object, ...]

    @property
    def directions(self) -> int:
        return (len(self.d) - 1).bit_length()

    @classmethod
    def constant(cls, value: float | int | arb, directions: int) -> "Mixed":
        data: list[object] = [_a(0) for _ in range(1 << directions)]
        data[0] = _a(value)
        return cls(tuple(data))

    @classmethod
    def affine(cls, value: arb, legs: Sequence[object]) -> "Mixed":
        data: list[object] = [_a(0) for _ in range(1 << len(legs))]
        data[0] = value
        for index, leg in enumerate(legs):
            data[1 << index] = leg
        return cls(tuple(data))

    def __neg__(self) -> "Mixed":
        return Mixed(tuple(-item for item in self.d))

    def __add__(self, other: float | int | arb | "Mixed") -> "Mixed":
        if not isinstance(other, Mixed):
            other = Mixed.constant(other, self.directions)
        return Mixed(tuple(a + b for a, b in zip(self.d, other.d)))

    __radd__ = __add__

    def __sub__(self, other: float | int | arb | "Mixed") -> "Mixed":
        return self + (-other if isinstance(other, Mixed) else -_a(other))

    def __rsub__(self, other: float | int | arb | "Mixed") -> "Mixed":
        return (-self) + other

    def __mul__(self, other: float | int | arb | "Mixed") -> "Mixed":
        if not isinstance(other, Mixed):
            other = Mixed.constant(other, self.directions)
        data: list[object] = []
        for mask in range(len(self.d)):
            total: object = _a(0)
            subset = mask
            while True:
                total = total + self.d[subset] * other.d[mask ^ subset]
                if subset == 0:
                    break
                subset = (subset - 1) & mask
            data.append(total)
        return Mixed(tuple(data))

    __rmul__ = __mul__

    def _unary(self, value: arb, outer: Sequence[arb]) -> "Mixed":
        data: list[object] = [_a(0) for _ in self.d]
        data[0] = value
        for mask in range(1, len(self.d)):
            total: object = _a(0)
            for partition in _partitions(mask):
                product: object = outer[len(partition)]
                for block in partition:
                    product = product * self.d[block]
                total = total + product
            data[mask] = total
        return Mixed(tuple(data))

    def reciprocal(self) -> "Mixed":
        value = self.d[0]
        if not isinstance(value, arb) or value.contains(0):
            raise ArithmeticError("mixed reciprocal crosses zero")
        outer = [_a(0)]
        factorial = 1
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(((-1) ** order) * factorial / value ** (order + 1))
        return self._unary(1 / value, outer)

    def __truediv__(self, other: float | int | arb | "Mixed") -> "Mixed":
        return self * (other.reciprocal() if isinstance(other, Mixed) else 1 / _a(other))

    def __rtruediv__(self, other: float | int | arb) -> "Mixed":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "Mixed":
        if power == 0:
            return Mixed.constant(1, self.directions)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = Mixed.constant(1, self.directions)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "Mixed":
        value = self.d[0].exp()
        return self._unary(value, [_a(0)] + [value] * self.directions)

    def positive_power(self, power: float) -> "Mixed":
        value = self.d[0]
        if not isinstance(value, arb) or not (value > 0):
            raise ArithmeticError("positive power needs a positive Arb value")
        p = _a(power)
        powered = (p * value.log()).exp()
        outer = [_a(0)]
        coefficient = _a(1)
        for order in range(1, self.directions + 1):
            coefficient *= p - (order - 1)
            outer.append(coefficient * ((p - order) * value.log()).exp())
        return self._unary(powered, outer)


def _sparse(values: np.ndarray, offset: int = 0) -> list[tuple[int, arb]]:
    return [(offset + i, _a(float(x))) for i, x in enumerate(values) if x != 0.0]


@dataclass(frozen=True)
class LocalTerm:
    maps: tuple[list[tuple[int, arb]], ...]
    values: tuple[arb, ...]
    bulk: Mixed
    inertia: Mixed


def _basis() -> tuple[np.ndarray, ...]:
    nodes, quadrature = np.polynomial.legendre.leggauss(POINTS)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, ORDER + 1, dtype=float)
    js = np.arange(ORDER, dtype=float)
    return (
        chi, quadrature, ks, js,
        np.cos(4.0 * np.outer(ks, chi)), np.sin(4.0 * np.outer(ks, chi)),
        np.cos(4.0 * np.outer(js, chi)), np.sin(4.0 * np.outer(js, chi)),
    )


_BASIS = _basis()


def _mapped(state: Sequence[arb], mapping: Sequence[tuple[int, arb]], constant: float = 0.0) -> arb:
    total = _a(constant)
    for index, coefficient in mapping:
        total += state[index] * coefficient
    return total


def _local_variables(
    values: Sequence[arb], directions: int, leg_values: Sequence[np.ndarray] | None,
) -> list[Mixed]:
    variables: list[Mixed] = []
    local_dimension = len(values)
    for index, value in enumerate(values):
        if leg_values is None:
            legs = []
            for axis in range(directions):
                shape = [1] * directions
                shape[axis] = local_dimension
                leg = np.empty(shape, dtype=object)
                leg.fill(_a(0))
                position = [0] * directions
                position[axis] = index
                leg[tuple(position)] = _a(1)
                legs.append(leg)
        else:
            legs = [np.asarray(item[index], dtype=object) for item in leg_values]
        variables.append(Mixed.affine(value, legs))
    return variables


def _integrand(
    state: Sequence[arb], node: int, directions: int,
    leg_values: Sequence[np.ndarray] | None = None,
) -> LocalTerm:
    chi, quadrature, ks, js, cos_k, sin_k, cos_j, sin_j = _BASIS
    coordinate = float(chi[node])
    window = math.sin(2.0 * coordinate) ** 2
    window_prime = 2.0 * math.sin(4.0 * coordinate)
    qmaps = [np.zeros(QDIM) for _ in range(6)]
    logc, loga, logb, cp, ap, bp = qmaps
    logc[0] = loga[0] = logb[0] = 1.0
    logc[1:13] = loga[1:13] = logb[1:13] = cos_k[:, node]
    logc[13:25] = window * cos_j[:, node]
    loga[25:37] = window * cos_j[:, node]
    logb[25:37] = -window * cos_j[:, node]
    up = -4.0 * ks * sin_k[:, node]
    wp = window_prime * cos_j[:, node] + window * (-4.0 * js * sin_j[:, node])
    cp[1:13] = ap[1:13] = bp[1:13] = up
    cp[13:25] = wp
    ap[25:37] = wp
    bp[25:37] = -wp
    vmaps = [array.copy() for array in (logc, loga, logb)]
    mmaps = [np.zeros(MDIM) for _ in range(4)]
    logn, nprime, beta, betaprime = mmaps
    logn[:12] = cos_k[:, node]
    nprime[:12] = -4.0 * ks * sin_k[:, node]
    beta[12:] = math.sin(4.0 * coordinate) * cos_j[:, node]
    betaprime[12:] = (
        4.0 * math.cos(4.0 * coordinate) * cos_j[:, node]
        + math.sin(4.0 * coordinate) * (-4.0 * js * sin_j[:, node])
    )
    maps = tuple(
        [_sparse(x) for x in qmaps]
        + [_sparse(x, QDIM) for x in vmaps]
        + [_sparse(x, 2 * QDIM) for x in mmaps]
    )
    constants = (
        0.0, 0.0, 0.0, 0.0, -math.tan(coordinate),
        1.0 / math.tan(coordinate), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    )
    local_values = tuple(_mapped(state, m, c) for m, c in zip(maps, constants))
    z = _local_variables(local_values, directions, leg_values)
    log_c, log_a, log_b, cpj, apj, bpj, lc, la, lb, log_n, npj, bet, betp = z
    C = RADIUS0 * log_c.exp()
    A = (RADIUS0 * math.cos(coordinate)) * log_a.exp()
    B = (RADIUS0 * math.sin(coordinate)) * log_b.exp()
    N = log_n.exp()
    hc = (lc - bet * cpj - betp) / N
    ha = (la - bet * apj) / N
    hb = (lb - bet * bpj) / N
    adm = hc**2 + 3 * ha**2 + 3 * hb**2 - (hc + 3 * ha + 3 * hb)**2
    xeta = 1 / C**2 + 3 * math.cos(coordinate) ** 2 / A**2 + 3 * math.sin(coordinate) ** 2 / B**2 - (-bet / N)**2
    fixed = apj**2 + bpj**2 + 3 * apj * bpj
    volume = C * A**3 * B**3
    spatial = A**3 * B**3
    sigma = -0.5 + 2.0 * coordinate / math.pi - math.sin(4.0 * coordinate) / (2.0 * math.pi)
    localization = 1.0 - 4.0 * sigma**2
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    gravity = 3 * spatial / C * N * (npj * (apj + bpj) + fixed)
    algebraic = N * volume * (
        3 / A**2 + 3 / B**2 - 0.5 * kappa0
        - localization * (0.5 * xeta + 0.125 * xeta**4) + 0.5 * adm
    )
    weight = float(quadrature[node])
    return LocalTerm(maps, local_values, weight * (gravity + algebraic), weight * volume * localization * (1 + xeta**3) / N)


def _boundary(
    state: Sequence[arb], directions: int,
    raw_legs: Sequence[np.ndarray] | None = None,
) -> tuple[tuple[list[tuple[int, arb]], ...], Mixed]:
    sk = (-1.0) ** np.arange(1, 13)
    sj = (-1.0) ** np.arange(12)
    la = np.zeros(QDIM); lb = np.zeros(QDIM); ln = np.zeros(MDIM)
    la[0] = lb[0] = 1.0
    la[1:13] = lb[1:13] = sk
    la[25:37] = sj; lb[25:37] = -sj; ln[:12] = sk
    maps = (_sparse(la), _sparse(lb), _sparse(ln, 2 * QDIM))
    values = tuple(_mapped(state, m) for m in maps)
    local_legs = None
    if raw_legs is not None:
        local_legs = []
        for leg in raw_legs:
            local_legs.append(np.asarray([
                sum(coef * leg[index] for index, coef in mapping)
                for mapping in maps
            ], dtype=object))
    a, b, n = _local_variables(values, directions, local_legs)
    A = RADIUS0 * a.exp() / math.sqrt(2.0)
    B = RADIUS0 * b.exp() / math.sqrt(2.0)
    r4 = A * B / (A**2 + B**2).positive_power(0.5)
    return maps, -standard_model_casimir_coefficient() * n.exp() / r4


def _action_local_jets(
    state_values: np.ndarray,
    *,
    fourth_legs: Sequence[np.ndarray] | None = None,
) -> dict[str, object]:
    """Return outward raw g/H, plus local T or contracted U data."""
    state = [_a(value) for value in np.asarray(state_values, dtype=object)]
    if fourth_legs is None:
        directions = 3
        bulk = Mixed.constant(0, directions); inertia = Mixed.constant(0, directions)
        terms: list[LocalTerm] = []
        for node in range(POINTS):
            term = _integrand(state, node, directions)
            bulk += term.bulk; inertia += term.inertia; terms.append(term)
        action = bulk - (0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / inertia
        boundary_maps, boundary = _boundary(state, directions)
        action += boundary
        return {"action": action, "terms": terms, "boundary_maps": boundary_maps}
    directions = 4
    bulk = Mixed.constant(0, directions); inertia = Mixed.constant(0, directions)
    for node in range(POINTS):
        # Convert the four raw global legs to the thirteen local affine legs.
        base = _integrand(state, node, 1)
        local_legs = []
        for leg in fourth_legs:
            local_legs.append(np.asarray([
                sum(coef * leg[index] for index, coef in mapping)
                for mapping in base.maps
            ], dtype=object))
        term = _integrand(state, node, directions, local_legs)
        bulk += term.bulk; inertia += term.inertia
    action = bulk - (0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / inertia
    _, boundary = _boundary(state, directions, fourth_legs)
    action += boundary
    return {"contracted_fourth": action.d[15]}


def _contracted_action(
    state_values: np.ndarray, raw_legs: Sequence[np.ndarray],
    dense_maps: Sequence[np.ndarray],
) -> object:
    """Outward retained-action mixed contraction in fixed global legs."""
    state = [_a(value) for value in np.asarray(state_values, dtype=object)]
    directions = len(raw_legs)
    bulk = Mixed.constant(0, directions); inertia = Mixed.constant(0, directions)
    for node in range(POINTS):
        mapping = dense_maps[node]
        local_legs: list[np.ndarray] = []
        for leg in raw_legs:
            leg_array = np.asarray(leg, dtype=object)
            rows = []
            for local in range(LOCAL):
                total: object = _a(0)
                for column in np.flatnonzero(mapping[local]):
                    total = total + _a(float(mapping[local, column])) * leg_array[column]
                rows.append(total)
            local_legs.append(np.asarray(rows, dtype=object))
        term = _integrand(state, node, directions, local_legs)
        bulk += term.bulk; inertia += term.inertia
    action = bulk - (0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / inertia
    _, boundary = _boundary(state, directions, raw_legs)
    action += boundary
    return action.d[-1]


def _bounds(values: object) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(values, dtype=object)
    lo = np.empty(array.shape, dtype=np.longdouble)
    hi = np.empty(array.shape, dtype=np.longdouble)
    for index in np.ndindex(array.shape):
        value = array[index]
        midpoint = float(value)
        radius = math.nextafter(float(abs(value - arb(midpoint)).upper()), math.inf)
        lo[index] = np.nextafter(np.longdouble(midpoint) - np.longdouble(radius), -np.longdouble(np.inf))
        hi[index] = np.nextafter(np.longdouble(midpoint) + np.longdouble(radius), np.longdouble(np.inf))
    return lo, hi


def _midrad(values: object) -> tuple[np.ndarray, np.ndarray]:
    lo, hi = _bounds(values)
    midpoint = (lo + hi) / np.longdouble(2)
    radius = np.nextafter((hi - lo) / np.longdouble(2), np.longdouble(np.inf))
    return midpoint, radius


def _float_transform_radius(absolute_sum: np.ndarray, operations: int) -> np.ndarray:
    epsilon = np.finfo(np.longdouble).eps
    gamma = np.longdouble(operations) * epsilon / (
        np.longdouble(1) - np.longdouble(operations) * epsilon
    )
    return np.nextafter(gamma * absolute_sum, np.longdouble(np.inf))


@dataclass
class ActionJets:
    gradient_arb: np.ndarray
    hessian_arb: np.ndarray
    gradient_mid: np.ndarray
    gradient_rad: np.ndarray
    hessian_mid: np.ndarray
    hessian_rad: np.ndarray
    bulk_third_terms: list[tuple[np.ndarray, np.ndarray, np.ndarray]]
    inertia_third_terms: list[tuple[np.ndarray, np.ndarray, np.ndarray]]
    inertia_value: arb
    inertia_gradient_mid: np.ndarray
    inertia_gradient_rad: np.ndarray
    inertia_hessian_mid: np.ndarray
    inertia_hessian_rad: np.ndarray
    dense_maps: list[np.ndarray]

    def contract_third(
        self, raw_directions: np.ndarray, *, left: slice, right: slice,
        direction_radius: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        directions = np.asarray(raw_directions, dtype=np.longdouble)
        direction_rad = np.zeros_like(directions) if direction_radius is None else np.asarray(direction_radius, dtype=np.longdouble)
        def contract(terms: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
            count = directions.shape[1]
            midpoint = np.zeros((left.stop - left.start, right.stop - right.start, count), dtype=np.longdouble)
            radius = np.zeros_like(midpoint)
            for mapping, local_mid, local_rad in terms:
                ml = np.asarray(mapping[:, left], dtype=np.longdouble)
                mr = np.asarray(mapping[:, right], dtype=np.longdouble)
                ld = np.asarray(mapping, dtype=np.longdouble) @ directions
                ldr = np.abs(np.asarray(mapping, dtype=np.longdouble)) @ direction_rad
                center = np.einsum("ai,bj,abc,ck->ijk", ml, mr, local_mid, ld, optimize=True)
                absolute = np.einsum(
                    "ai,bj,abc,ck->ijk", np.abs(ml), np.abs(mr),
                    np.abs(local_mid) + local_rad, np.abs(ld) + ldr, optimize=True,
                )
                local_uncertainty = np.einsum(
                    "ai,bj,abc,ck->ijk", np.abs(ml), np.abs(mr),
                    local_rad, np.abs(ld), optimize=True,
                )
                direction_uncertainty = np.einsum(
                    "ai,bj,abc,ck->ijk", np.abs(ml), np.abs(mr),
                    np.abs(local_mid) + local_rad, ldr, optimize=True,
                )
                midpoint += center
                radius += local_uncertainty + direction_uncertainty + _float_transform_radius(absolute, mapping.shape[0]**3)
            radius += _float_transform_radius(np.abs(midpoint) + radius, max(1, len(terms)))
            return midpoint, radius

        bulk_mid, bulk_rad = contract(self.bulk_third_terms)
        inertia_mid, inertia_rad = contract(self.inertia_third_terms)
        igm = np.asarray(self.inertia_gradient_mid, dtype=np.longdouble)
        igr = np.asarray(self.inertia_gradient_rad, dtype=np.longdouble)
        ihm = np.asarray(self.inertia_hessian_mid, dtype=np.longdouble)
        ihr = np.asarray(self.inertia_hessian_rad, dtype=np.longdouble)
        dmid = directions
        drad = direction_rad
        gd_mid = igm @ dmid
        gd_rad = np.abs(igm) @ drad + igr @ (np.abs(dmid) + drad)
        hd_mid = ihm[:, :] @ dmid
        hd_rad = np.abs(ihm) @ drad + ihr @ (np.abs(dmid) + drad)
        il = slice(left.start, left.stop); ir = slice(right.start, right.stop)
        cross_mid = (
            ihm[il, ir, None] * gd_mid[None, None, :]
            + hd_mid[il, None, :] * igm[ir][None, :, None]
            + igm[il][:, None, None] * hd_mid[ir, None, :].transpose(1, 0, 2)
        )
        cross_rad = (
            np.abs(ihm[il, ir, None]) * gd_rad[None, None, :]
            + ihr[il, ir, None] * (np.abs(gd_mid)[None, None, :] + gd_rad[None, None, :])
            + np.abs(hd_mid[il, None, :]) * igr[ir][None, :, None]
            + hd_rad[il, None, :] * (np.abs(igm[ir])[None, :, None] + igr[ir][None, :, None])
            + igr[il][:, None, None] * (np.abs(hd_mid[ir, None, :].transpose(1, 0, 2)) + hd_rad[ir, None, :].transpose(1, 0, 2))
            + np.abs(igm[il])[:, None, None] * hd_rad[ir, None, :].transpose(1, 0, 2)
        )
        cubic_mid = igm[il][:, None, None] * igm[ir][None, :, None] * gd_mid[None, None, :]
        cubic_abs = (
            (np.abs(igm[il]) + igr[il])[:, None, None]
            * (np.abs(igm[ir]) + igr[ir])[None, :, None]
            * (np.abs(gd_mid) + gd_rad)[None, None, :]
        )
        cubic_rad = cubic_abs - np.abs(cubic_mid)
        c2m, c2r = _midrad(_a(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / self.inertia_value**2)
        c3m, c3r = _midrad(-2 * _a(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / self.inertia_value**3)
        c4m, c4r = _midrad(6 * _a(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2)) / self.inertia_value**4)
        midpoint = bulk_mid + c2m * inertia_mid + c3m * cross_mid + c4m * cubic_mid
        radius = (
            bulk_rad
            + abs(c2m) * inertia_rad + c2r * (np.abs(inertia_mid) + inertia_rad)
            + abs(c3m) * cross_rad + c3r * (np.abs(cross_mid) + cross_rad)
            + abs(c4m) * cubic_rad + c4r * (np.abs(cubic_mid) + cubic_rad)
        )
        radius += _float_transform_radius(
            np.abs(bulk_mid) + bulk_rad + np.abs(c2m * inertia_mid)
            + np.abs(c3m * cross_mid) + np.abs(c4m * cubic_mid), 8,
        )
        return np.asarray(midpoint, dtype=float), np.asarray(
            radius + np.abs(midpoint - np.asarray(midpoint, dtype=float)), dtype=float,
        )


def _dense_mapping(maps: Sequence[Sequence[tuple[int, arb]]]) -> np.ndarray:
    result = np.zeros((len(maps), STATE), dtype=float)
    for row, mapping in enumerate(maps):
        for column, coefficient in mapping:
            result[row, column] = float(coefficient)
    return result


def _mat(values: np.ndarray) -> arb_mat:
    array = np.asarray(values, dtype=object)
    if array.ndim == 1:
        array = array[:, None]
    return arb_mat([[array[i, j] for j in range(array.shape[1])] for i in range(array.shape[0])])


def _array(matrix: arb_mat) -> np.ndarray:
    return np.asarray([
        [matrix[i, j] for j in range(matrix.ncols())]
        for i in range(matrix.nrows())
    ], dtype=object)


def _ball(midpoint: np.ndarray, radius: np.ndarray) -> np.ndarray:
    mid = np.asarray(midpoint, dtype=float); rad = np.asarray(radius, dtype=float)
    result = np.empty(mid.shape, dtype=object)
    for index in np.ndindex(mid.shape):
        result[index] = arb(float(mid[index]), float(rad[index]))
    return result


def _center_radius(value: arb) -> tuple[float, float]:
    midpoint = float(value)
    radius = math.nextafter(float(abs(value - arb(midpoint)).upper()), math.inf)
    return midpoint, radius


def _norm_upper(values: np.ndarray) -> float:
    total = 0.0
    for value in np.asarray(values, dtype=object).ravel():
        upper = math.nextafter(float(abs(value).upper()), math.inf)
        total = math.nextafter(total + upper * upper, math.inf)
    return math.nextafter(math.sqrt(total), math.inf)


def _eigenline(
    hessian: np.ndarray, midpoint: np.ndarray, reference: np.ndarray,
) -> tuple[np.ndarray, arb, float, float]:
    reduced = np.asarray(hessian[QDIM:, QDIM:], dtype=object)
    values, vectors = np.linalg.eigh(np.asarray(midpoint[QDIM:, QDIM:], dtype=float))
    selected = 24
    psi0 = vectors[:, selected]
    if float(psi0 @ reference) < 0:
        psi0 = -psi0
    psi = _mat(np.asarray([_a(float(x)) for x in psi0], dtype=object))
    lam = _a(float(values[selected]))
    H = _mat(reduced)
    identity = arb_mat(np.eye(REDUCED, dtype=int).tolist())
    # These are approximation refinements, not enclosure iterations.  Recenter
    # after every bordered Newton solve and certify only the final point by its
    # outward residual/gap.  Carrying the prior interval through the next
    # Newton step creates a spurious O(1e-40) eigenline width which the causal
    # inverse amplifies catastrophically.
    for _ in range(4):
        residual = H * psi - lam * psi
        norm_defect = (_array(psi.transpose() * psi)[0, 0] - 1) / 2
        K = arb_mat(REDUCED + 1, REDUCED + 1)
        block = H - lam * identity
        for i in range(REDUCED):
            for j in range(REDUCED):
                K[i, j] = block[i, j]
            K[i, REDUCED] = -psi[i, 0]
            K[REDUCED, i] = psi[i, 0]
        rhs = arb_mat(REDUCED + 1, 1)
        for i in range(REDUCED):
            rhs[i, 0] = -residual[i, 0]
        rhs[REDUCED, 0] = -norm_defect
        correction = K.solve(rhs, algorithm="precond")
        for i in range(REDUCED):
            psi[i, 0] += correction[i, 0]
        lam += correction[REDUCED, 0]
        for i in range(REDUCED):
            psi[i, 0] = arb(psi[i, 0].mid())
        lam = arb(lam.mid())
    residual = _array(H * psi - lam * psi).ravel()
    gap = float(min(abs(values[selected] - np.delete(values, selected))))
    residual_upper = _norm_upper(residual)
    angle = math.nextafter(residual_upper / (gap - residual_upper), math.inf)
    psi_array = _array(psi).ravel()
    for i in range(REDUCED):
        psi_array[i] += arb(0, angle)
    rayleigh = (_mat(psi_array).transpose() * H * _mat(psi_array))[0, 0] / (
        _mat(psi_array).transpose() * _mat(psi_array)
    )[0, 0]
    return psi_array, rayleigh, gap, residual_upper


@dataclass
class RateEnclosure:
    value: np.ndarray
    derivative: np.ndarray | None
    gap_lower: float
    eigen_residual_upper: float
    action_jets: ActionJets


def _mixed_contraction(
    state: np.ndarray,
    dense_maps: Sequence[np.ndarray],
    *legs: np.ndarray,
) -> np.ndarray:
    """Contract the retained action in several small signed tensor legs.

    Each leg is either one raw state direction or a matrix whose columns are
    directions.  The column axes are kept distinct, so this routine forms
    only the particular directional products needed by the bordered
    identities; it never materializes an ambient D3/D4/D5 tensor.
    """
    dimensions = [1 if np.asarray(leg).ndim == 1 else np.asarray(leg).shape[1]
                  for leg in legs]
    broadcast: list[np.ndarray] = []
    for axis, leg in enumerate(legs):
        array = np.asarray(leg, dtype=object)
        shape = [STATE] + [1] * len(legs)
        shape[axis + 1] = dimensions[axis]
        broadcast.append(array.reshape(shape))
    value = np.asarray(
        _contracted_action(state, broadcast, dense_maps), dtype=object,
    )
    return value.reshape(tuple(dimensions))


def _arb_dot(left: np.ndarray, right: np.ndarray) -> arb:
    total = _a(0)
    for a, b in zip(
        np.asarray(left, dtype=object).ravel(),
        np.asarray(right, dtype=object).ravel(),
        strict=True,
    ):
        total += a * b
    return total


def _arb_norm_lower(values: np.ndarray) -> float:
    total = _a(0)
    for value in np.asarray(values, dtype=object).ravel():
        lower = _a(abs(value).lower())
        total += lower * lower
    return math.nextafter(float(total.sqrt().lower()), -math.inf)


def _arb_norm_bounds(values: np.ndarray) -> dict[str, float]:
    """Return directed Euclidean lower/upper bounds for an Arb vector."""
    array = np.asarray(values, dtype=object).ravel()
    return {
        "lower": _arb_norm_lower(array),
        "upper": _norm_upper(array),
    }


def _rate_second_directional(
    state: np.ndarray,
    descriptor: float | arb,
    weights: np.ndarray,
    reference: np.ndarray,
    augmented_direction: np.ndarray,
) -> np.ndarray:
    """Outward second directional derivative of the augmented exact rate.

    This is the one-direction specialization of the already-retained
    differentiated bordered identities.  It needs signed D3/D4/D5 action
    contractions only.  In particular, no dense third-order field tensor and
    no binary eigenline reselection is introduced.
    """
    jets = _arb_action_jets(state)
    dense_maps = jets.dense_maps
    psi, eigenvalue, _, _ = _eigenline(
        jets.hessian_arb, jets.hessian_mid, reference,
    )
    q_weights, reduced_weights, _, _ = metric_data()
    w = np.asarray(weights, dtype=float)
    direction = np.asarray(augmented_direction, dtype=object).reshape(STATE + 1)
    raw_u = np.asarray([
        direction[i] / _a(float(w[i])) for i in range(STATE)
    ], dtype=object)
    ds = direction[STATE]

    gradient = np.asarray([
        jets.gradient_arb[i] / _a(float(w[i])) for i in range(STATE)
    ], dtype=object)
    H_action = np.asarray([[
        jets.hessian_arb[i, j] / _a(float(w[i])) / _a(float(w[j]))
        for j in range(STATE)] for i in range(STATE)
    ], dtype=object)
    configuration = np.asarray([
        _a(float(q_weights[i])) * _a(state[QDIM + i]) for i in range(QDIM)
    ], dtype=object)
    configuration_first = np.asarray([
        _a(float(q_weights[i])) * raw_u[QDIM + i] for i in range(QDIM)
    ], dtype=object)

    rhs = np.empty(REDUCED, dtype=object)
    for i in range(REDUCED):
        source = _a(0)
        if i < QDIM:
            source += _a(float(q_weights[i])) * gradient[i]
        for j in range(QDIM):
            source -= H_action[QDIM + i, j] * configuration[j]
        rhs[i] = _a(float(reduced_weights[i])) * source

    Hraw = np.asarray(jets.hessian_arb[QDIM:, QDIM:], dtype=object)
    K = arb_mat(REDUCED + 1, REDUCED + 1)
    for i in range(REDUCED):
        for j in range(REDUCED):
            K[i, j] = Hraw[i, j] - (eigenvalue if i == j else 0)
        K[i, REDUCED] = psi[i]
        K[REDUCED, i] = psi[i]
    response_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        response_rhs[i, 0] = rhs[i]
    response = _verified_solve(K, response_rhs)
    hard = np.asarray([response[i, 0] for i in range(REDUCED)], dtype=object)
    bpsi = response[REDUCED, 0]

    out_reduced = np.zeros((STATE, REDUCED), dtype=object)
    out_full = np.zeros((STATE, STATE), dtype=object)
    for i in range(REDUCED):
        out_reduced[QDIM + i, i] = _a(1)
    for i in range(STATE):
        out_full[i, i] = _a(1)
    p = np.asarray([_a(0)] * QDIM + list(psi), dtype=object)
    hfull = np.asarray([_a(0)] * QDIM + list(hard), dtype=object)
    qdirection = np.asarray([_a(0) for _ in range(STATE)], dtype=object)
    qdirection_first = np.asarray([_a(0) for _ in range(STATE)], dtype=object)
    for i in range(QDIM):
        qdirection[i] = configuration[i] / _a(float(w[i]))
        qdirection_first[i] = configuration_first[i] / _a(float(w[i]))

    fixed_first = np.column_stack((p, hfull, qdirection))
    first_outputs = _mixed_contraction(
        state, dense_maps, out_reduced, fixed_first, raw_u,
    ).reshape(REDUCED, 3)
    H1psi = first_outputs[:, 0]
    H1hard = first_outputs[:, 1]
    H1configuration = first_outputs[:, 2]
    lambda_first = _arb_dot(psi, H1psi)

    eigen_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        eigen_rhs[i, 0] = -(H1psi[i] - lambda_first * psi[i])
    psi_first_solve = _verified_solve(K, eigen_rhs)
    psi_first = np.asarray([
        psi_first_solve[i, 0] for i in range(REDUCED)
    ], dtype=object)

    dgradient_raw = _array(_mat(jets.hessian_arb) * _mat(raw_u)).ravel()
    rhs_first = np.empty(REDUCED, dtype=object)
    for i in range(REDUCED):
        source = _a(0)
        if i < QDIM:
            source += (
                _a(float(q_weights[i])) * dgradient_raw[i]
                / _a(float(w[i]))
            )
        source -= H1configuration[i] / _a(float(w[QDIM + i]))
        for j in range(QDIM):
            source -= H_action[QDIM + i, j] * configuration_first[j]
        rhs_first[i] = _a(float(reduced_weights[i])) * source

    response_first_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        response_first_rhs[i, 0] = rhs_first[i] - (
            H1hard[i] - lambda_first * hard[i] + bpsi * psi_first[i]
        )
    response_first_rhs[REDUCED, 0] = -_arb_dot(psi_first, hard)
    response_first = _verified_solve(K, response_first_rhs)
    hard_first = np.asarray([
        response_first[i, 0] for i in range(REDUCED)
    ], dtype=object)
    b_first = response_first[REDUCED, 0]

    fixed_second = np.column_stack((p, hfull, qdirection))
    second_outputs = _mixed_contraction(
        state, dense_maps, out_reduced, fixed_second, raw_u, raw_u,
    ).reshape(REDUCED, 3)
    H2psi = second_outputs[:, 0]
    H2hard = second_outputs[:, 1]
    H2configuration = second_outputs[:, 2]
    H1psi_first = _mixed_contraction(
        state, dense_maps, out_reduced,
        np.asarray([_a(0)] * QDIM + list(psi_first), dtype=object), raw_u,
    ).reshape(REDUCED)
    lambda_second = _arb_dot(psi, H2psi) + 2 * _arb_dot(
        psi_first, H1psi,
    )
    eigen_second_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        source = (
            H2psi[i] + 2 * H1psi_first[i]
            - lambda_second * psi[i] - 2 * lambda_first * psi_first[i]
        )
        eigen_second_rhs[i, 0] = -source
    eigen_second_rhs[REDUCED, 0] = -_arb_dot(psi_first, psi_first)
    psi_second_solve = _verified_solve(K, eigen_second_rhs)
    psi_second = np.asarray([
        psi_second_solve[i, 0] for i in range(REDUCED)
    ], dtype=object)

    gradient_second = _mixed_contraction(
        state, dense_maps, out_full, raw_u, raw_u,
    ).reshape(STATE)
    H1configuration_first = _mixed_contraction(
        state, dense_maps, out_reduced, qdirection_first, raw_u,
    ).reshape(REDUCED)
    rhs_second = np.empty(REDUCED, dtype=object)
    for i in range(REDUCED):
        source = _a(0)
        if i < QDIM:
            source += (
                _a(float(q_weights[i])) * gradient_second[i]
                / _a(float(w[i]))
            )
        source -= H2configuration[i] / _a(float(w[QDIM + i]))
        source -= 2 * H1configuration_first[i] / _a(float(w[QDIM + i]))
        rhs_second[i] = _a(float(reduced_weights[i])) * source

    hfirst_full = np.asarray([_a(0)] * QDIM + list(hard_first), dtype=object)
    H1hard_first = _mixed_contraction(
        state, dense_maps, out_reduced, hfirst_full, raw_u,
    ).reshape(REDUCED)
    response_second_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        K2_response = (
            H2hard[i] - lambda_second * hard[i] + bpsi * psi_second[i]
        )
        K1_response_first = (
            H1hard_first[i] - lambda_first * hard_first[i]
            + b_first * psi_first[i]
        )
        response_second_rhs[i, 0] = (
            rhs_second[i] - K2_response - 2 * K1_response_first
        )
    response_second_rhs[REDUCED, 0] = -(
        _arb_dot(psi_second, hard) + 2 * _arb_dot(psi_first, hard_first)
    )
    response_second = _verified_solve(K, response_second_rhs)
    hard_second = np.asarray([
        response_second[i, 0] for i in range(REDUCED)
    ], dtype=object)
    b_second = response_second[REDUCED, 0]

    psi_action = np.asarray([_a(0)] * QDIM + [
        _a(float(reduced_weights[i])) * psi[i] for i in range(REDUCED)
    ], dtype=object)
    hard_action = np.asarray(list(configuration) + [
        _a(float(reduced_weights[i])) * hard[i] for i in range(REDUCED)
    ], dtype=object)
    a = np.asarray([
        psi_action[i] / _a(float(w[i])) for i in range(STATE)
    ], dtype=object)
    d = np.asarray([
        hard_action[i] / _a(float(w[i])) for i in range(STATE)
    ], dtype=object)
    p_first = np.asarray([_a(0)] * QDIM + list(psi_first), dtype=object)
    p_second = np.asarray([_a(0)] * QDIM + list(psi_second), dtype=object)
    a_first = np.asarray([_a(0)] * QDIM + [
        _a(float(reduced_weights[i])) * psi_first[i]
        / _a(float(w[QDIM + i])) for i in range(REDUCED)
    ], dtype=object)
    a_second = np.asarray([_a(0)] * QDIM + [
        _a(float(reduced_weights[i])) * psi_second[i]
        / _a(float(w[QDIM + i])) for i in range(REDUCED)
    ], dtype=object)
    d_first = np.asarray(list(qdirection_first[:QDIM]) + [
        _a(float(reduced_weights[i])) * hard_first[i]
        / _a(float(w[QDIM + i])) for i in range(REDUCED)
    ], dtype=object)
    d_second = np.asarray([_a(0)] * QDIM + [
        _a(float(reduced_weights[i])) * hard_second[i]
        / _a(float(w[QDIM + i])) for i in range(REDUCED)
    ], dtype=object)

    c_and_R = _mixed_contraction(
        state, dense_maps, p, p, np.column_stack((a, d)),
    ).reshape(2)
    cpsi, remainder = c_and_R
    U_base = _mixed_contraction(
        state, dense_maps, raw_u, p, p, np.column_stack((a, d)),
    ).reshape(2)
    T_first = _mixed_contraction(
        state, dense_maps, p_first, p, np.column_stack((a, d)),
    ).reshape(2)
    T_last_first = _mixed_contraction(
        state, dense_maps, p, p, np.column_stack((a_first, d_first)),
    ).reshape(2)
    first_cR = U_base + 2 * T_first + T_last_first

    V_base = _mixed_contraction(
        state, dense_maps, raw_u, raw_u, p, p,
        np.column_stack((a, d)),
    ).reshape(2)
    U_pfirst = _mixed_contraction(
        state, dense_maps, raw_u, p_first, p,
        np.column_stack((a, d)),
    ).reshape(2)
    U_lastfirst = _mixed_contraction(
        state, dense_maps, raw_u, p, p,
        np.column_stack((a_first, d_first)),
    ).reshape(2)
    T_psecond = _mixed_contraction(
        state, dense_maps, p_second, p, np.column_stack((a, d)),
    ).reshape(2)
    T_pfirst2 = _mixed_contraction(
        state, dense_maps, p_first, p_first, np.column_stack((a, d)),
    ).reshape(2)
    T_cross = _mixed_contraction(
        state, dense_maps, p_first, p,
        np.column_stack((a_first, d_first)),
    ).reshape(2)
    T_lastsecond = _mixed_contraction(
        state, dense_maps, p, p, np.column_stack((a_second, d_second)),
    ).reshape(2)
    second_cR = (
        V_base + 4 * U_pfirst + 2 * U_lastfirst
        + 2 * T_psecond + 2 * T_pfirst2 + 4 * T_cross
        + T_lastsecond
    )
    c_first, R_first = first_cR
    c_second, R_second = second_cR

    s = _a(descriptor)
    delta = cpsi * bpsi + s * remainder
    delta_first = (
        c_first * bpsi + cpsi * b_first + ds * remainder + s * R_first
    )
    delta_second = (
        c_second * bpsi + 2 * c_first * b_first + cpsi * b_second
        + 2 * ds * R_first + s * R_second
    )

    numerator = np.asarray(
        [s * item for item in configuration]
        + [_a(float(reduced_weights[i])) * (
            bpsi * psi[i] + s * hard[i]
        ) for i in range(REDUCED)], dtype=object,
    )
    numerator_first = np.asarray(
        [ds * configuration[i] + s * configuration_first[i] for i in range(QDIM)]
        + [_a(float(reduced_weights[i])) * (
            b_first * psi[i] + bpsi * psi_first[i]
            + ds * hard[i] + s * hard_first[i]
        ) for i in range(REDUCED)], dtype=object,
    )
    numerator_second = np.asarray(
        [2 * ds * configuration_first[i] for i in range(QDIM)]
        + [_a(float(reduced_weights[i])) * (
            b_second * psi[i] + 2 * b_first * psi_first[i]
            + bpsi * psi_second[i] + 2 * ds * hard_first[i]
            + s * hard_second[i]
        ) for i in range(REDUCED)], dtype=object,
    )
    norm = _arb_dot(numerator, numerator).sqrt()
    norm_first = _arb_dot(numerator, numerator_first) / norm
    norm_second = (
        _arb_dot(numerator_first, numerator_first)
        + _arb_dot(numerator, numerator_second) - norm_first**2
    ) / norm
    field = np.asarray([item / norm for item in numerator], dtype=object)
    field_first = np.asarray([
        numerator_first[i] / norm - numerator[i] * norm_first / norm**2
        for i in range(STATE)
    ], dtype=object)
    field_second = np.asarray([
        numerator_second[i] / norm
        - 2 * numerator_first[i] * norm_first / norm**2
        - numerator[i] * norm_second / norm**2
        + 2 * numerator[i] * norm_first**2 / norm**3
        for i in range(STATE)
    ], dtype=object)
    scalar_second = (
        delta_second / norm - 2 * delta_first * norm_first / norm**2
        - delta * norm_second / norm**2
        + 2 * delta * norm_first**2 / norm**3
    )
    return np.asarray(list(field_second) + [scalar_second], dtype=object)


def _rate_enclosure(
    state: np.ndarray, descriptor: float | arb, weights: np.ndarray,
    reference: np.ndarray,
    augmented_directions: np.ndarray | tuple[np.ndarray, np.ndarray] | None,
) -> RateEnclosure:
    jets = _arb_action_jets(state)
    psi, eigenvalue, gap, eigen_residual = _eigenline(
        jets.hessian_arb, jets.hessian_mid, reference,
    )
    q_weights, reduced_weights, _, _ = metric_data()
    w = np.asarray(weights, dtype=float)
    gradient = np.asarray([
        jets.gradient_arb[i] / _a(float(w[i])) for i in range(STATE)
    ], dtype=object)
    H = np.asarray([[
        jets.hessian_arb[i, j] / _a(float(w[i])) / _a(float(w[j]))
        for j in range(STATE)] for i in range(STATE)
    ], dtype=object)
    configuration = np.asarray([
        _a(float(q_weights[i])) * _a(state[QDIM + i]) for i in range(QDIM)
    ], dtype=object)
    rhs = np.empty(REDUCED, dtype=object)
    for i in range(REDUCED):
        source = _a(0)
        if i < QDIM:
            source += _a(float(q_weights[i])) * gradient[i]
        for j in range(QDIM):
            source -= H[QDIM + i, j] * configuration[j]
        rhs[i] = _a(float(reduced_weights[i])) * source
    Hraw = np.asarray(jets.hessian_arb[QDIM:, QDIM:], dtype=object)
    K = arb_mat(REDUCED + 1, REDUCED + 1)
    for i in range(REDUCED):
        for j in range(REDUCED):
            K[i, j] = Hraw[i, j] - (eigenvalue if i == j else 0)
        K[i, REDUCED] = psi[i]
        K[REDUCED, i] = psi[i]
    response_rhs = arb_mat(REDUCED + 1, 1)
    for i in range(REDUCED):
        response_rhs[i, 0] = rhs[i]
    response = _verified_solve(K, response_rhs)
    hard = np.asarray([response[i, 0] for i in range(REDUCED)], dtype=object)
    bpsi = response[REDUCED, 0]
    pfull = np.asarray([_a(0)] * QDIM + list(psi), dtype=object)
    psi_action = np.asarray([_a(0)] * QDIM + [
        _a(float(reduced_weights[i])) * psi[i] for i in range(REDUCED)
    ], dtype=object)
    hard_action = np.asarray(list(configuration) + [
        _a(float(reduced_weights[i])) * hard[i] for i in range(REDUCED)
    ], dtype=object)
    da = np.asarray([psi_action[i] / _a(float(w[i])) for i in range(STATE)], dtype=object)
    dh = np.asarray([hard_action[i] / _a(float(w[i])) for i in range(STATE)], dtype=object)
    dense_maps = jets.dense_maps
    p_leg = np.empty((STATE, 1, 1), dtype=object)
    for i in range(STATE):
        p_leg[i, 0, 0] = pfull[i]
    da_dh_leg = np.empty((STATE, 1, 2), dtype=object)
    for i in range(STATE):
        da_dh_leg[i, 0, 0] = da[i]; da_dh_leg[i, 0, 1] = dh[i]
    c_and_r = np.asarray(_contracted_action(
        state, [p_leg, p_leg, da_dh_leg], dense_maps,
    ), dtype=object).reshape(2)
    cpsi, remainder = c_and_r
    s = _a(descriptor)
    delta = cpsi * bpsi + s * remainder
    G = np.asarray(
        [s * item for item in configuration]
        + [_a(float(reduced_weights[i])) * (bpsi * psi[i] + s * hard[i]) for i in range(REDUCED)],
        dtype=object,
    )
    norm = _a(0)
    for item in G:
        norm += item * item
    norm = norm.sqrt()
    value = np.asarray([item / norm for item in G] + [delta / norm], dtype=object)
    if augmented_directions is None:
        return RateEnclosure(value, None, gap - eigen_residual, eigen_residual, jets)

    direction_balls: np.ndarray | None = None
    if isinstance(augmented_directions, tuple):
        directions = np.asarray(augmented_directions[0], dtype=float)
        direction_rad = np.asarray(augmented_directions[1], dtype=float)
    else:
        candidate = np.asarray(augmented_directions)
        if candidate.dtype == object and candidate.size and isinstance(candidate.flat[0], arb):
            direction_balls = np.asarray(candidate, dtype=object)
            directions = np.empty(direction_balls.shape, dtype=float)
            direction_rad = np.empty_like(directions)
            for index in np.ndindex(direction_balls.shape):
                directions[index], direction_rad[index] = _center_radius(direction_balls[index])
        else:
            directions = np.asarray(augmented_directions, dtype=float)
            direction_rad = np.zeros_like(directions)
    count = directions.shape[1]
    if direction_balls is None:
        raw = directions[:STATE] / w[:, None]
        raw_rad = direction_rad[:STATE] / w[:, None]
        raw_ball = _mat(_ball(raw, raw_rad))
        ds = np.asarray([
            arb(float(directions[STATE, k]), float(direction_rad[STATE, k]))
            for k in range(count)
        ], dtype=object)
    else:
        raw_ball_array = np.empty((STATE, count), dtype=object)
        for i in range(STATE):
            for k in range(count):
                raw_ball_array[i, k] = direction_balls[i, k] / _a(float(w[i]))
        raw_ball = _mat(raw_ball_array)
        ds = np.asarray([direction_balls[STATE, k] for k in range(count)], dtype=object)
    dgradient = _array(_mat(jets.hessian_arb) * raw_ball)
    # Only three signed H-directional actions are needed: on psi, hard,
    # and the q-configuration column.  Contract them in Arb before export.
    out_leg = np.empty((STATE, REDUCED, 1, 1), dtype=object)
    fixed_leg = np.empty((STATE, 1, 3, 1), dtype=object)
    input_leg = np.empty((STATE, 1, 1, count + 2), dtype=object)
    qdirection = np.asarray([_a(0) for _ in range(STATE)], dtype=object)
    for i in range(QDIM):
        qdirection[i] = configuration[i] / _a(float(w[i]))
    hfull = np.asarray([_a(0)] * QDIM + list(hard), dtype=object)
    for i in range(STATE):
        for j in range(REDUCED):
            out_leg[i, j, 0, 0] = _a(1) if i == QDIM + j else _a(0)
        fixed_leg[i, 0, 0, 0] = pfull[i]
        fixed_leg[i, 0, 1, 0] = hfull[i]
        fixed_leg[i, 0, 2, 0] = qdirection[i]
        for k in range(count):
            input_leg[i, 0, 0, k] = raw_ball[i, k]
        input_leg[i, 0, 0, count] = da[i]
        input_leg[i, 0, 0, count + 1] = dh[i]
    directional = np.asarray(_contracted_action(
        state, [out_leg, fixed_leg, input_leg], dense_maps,
    ), dtype=object).reshape(REDUCED, 3, count + 2)
    output_fixed = directional[:, 0, count:count + 2]
    # Selected-line first variation, all causal directions in one solve.
    eig_rhs = arb_mat(REDUCED + 1, count)
    slopes: list[arb] = []
    for k in range(count):
        slope = _a(0)
        for i in range(REDUCED):
            slope += psi[i] * directional[i, 0, k]
        slopes.append(slope)
        for i in range(REDUCED):
            total = directional[i, 0, k] - slope * psi[i]
            eig_rhs[i, k] = -total
    dline = _verified_solve(K, eig_rhs)

    response_direction_rhs = arb_mat(REDUCED + 1, count)
    dconfig = np.empty((QDIM, count), dtype=object)
    for i in range(QDIM):
        for k in range(count):
            dconfig[i, k] = _a(float(q_weights[i])) * raw_ball[QDIM + i, k]
    for k in range(count):
        drhs = [_a(0) for _ in range(REDUCED)]
        for i in range(REDUCED):
            source = _a(0)
            if i < QDIM:
                source += _a(float(q_weights[i])) * dgradient[i, k] / _a(float(w[i]))
            for j in range(QDIM):
                source -= H[QDIM + i, j] * dconfig[j, k]
            source -= directional[i, 2, k] / _a(float(w[QDIM + i]))
            drhs[i] = _a(float(reduced_weights[i])) * source
        for i in range(REDUCED):
            dKresponse = _a(0)
            dKresponse += directional[i, 1, k] - slopes[k] * hard[i]
            dKresponse += dline[i, k] * bpsi
            response_direction_rhs[i, k] = drhs[i] - dKresponse
        bottom = _a(0)
        for j in range(REDUCED):
            bottom += dline[j, k] * hard[j]
        response_direction_rhs[REDUCED, k] = -bottom
    dresponse = _verified_solve(K, response_direction_rhs)

    # Keep the selected-line and hard-response variations as the original
    # Arb balls.  Exporting them to binary64 here destroys their correlation
    # with the bordered solves and creates an avoidable O(1e-12) radius floor
    # that the unstable causal recurrence later amplifies.
    dpsi_action = np.empty((STATE, count), dtype=object)
    dhard_action = np.empty((STATE, count), dtype=object)
    for k in range(count):
        for i in range(STATE):
            if i < QDIM:
                dpsi_action[i, k] = _a(0)
                dhard_action[i, k] = dconfig[i, k] / _a(float(w[i]))
            else:
                dpsi_action[i, k] = (
                    _a(float(reduced_weights[i - QDIM])) * dline[i - QDIM, k] / _a(float(w[i]))
                )
                dhard_action[i, k] = (
                    _a(float(reduced_weights[i - QDIM])) * dresponse[i - QDIM, k] / _a(float(w[i]))
                )
    dynamic_leg = np.empty((STATE, 1, 1, 2 * count), dtype=object)
    for i in range(STATE):
        for k in range(count):
            dynamic_leg[i, 0, 0, k] = dpsi_action[i, k]
            dynamic_leg[i, 0, 0, count + k] = dhard_action[i, k]
    dynamic_T = np.asarray(_contracted_action(
        state, [p_leg, p_leg, dynamic_leg], dense_maps,
    ), dtype=object).reshape(2 * count)

    # D4S[v,psi,psi,(psi_action,hard_action)] in one correlated evaluation.
    raw0 = np.empty((STATE, count, 1, 1, 1), dtype=object)
    raw1 = np.empty((STATE, 1, 1, 1, 1), dtype=object)
    raw2 = np.empty_like(raw1)
    raw3 = np.empty((STATE, 1, 1, 1, 2), dtype=object)
    for i in range(STATE):
        for k in range(count):
            raw0[i, k, 0, 0, 0] = raw_ball[i, k]
        raw1[i, 0, 0, 0, 0] = pfull[i]
        raw2[i, 0, 0, 0, 0] = pfull[i]
        raw3[i, 0, 0, 0, 0] = da[i]
        raw3[i, 0, 0, 0, 1] = dh[i]
    fourth = np.asarray(_contracted_action(
        state, [raw0, raw1, raw2, raw3], dense_maps,
    ), dtype=object).reshape(count, 2)

    derivative = np.empty((STATE + 1, count), dtype=object)
    for k in range(count):
        dc = fourth[k, 0]
        dR = fourth[k, 1]
        for i in range(REDUCED):
            dc += 2 * dline[i, k] * output_fixed[i, 0]
            dR += 2 * dline[i, k] * output_fixed[i, 1]
        dc += dynamic_T[k]
        dR += dynamic_T[count + k]
        db = dresponse[REDUCED, k]
        ddelta = dc * bpsi + cpsi * db + ds[k] * remainder + s * dR
        dG = np.empty(STATE, dtype=object)
        for i in range(QDIM):
            dG[i] = ds[k] * configuration[i] + s * dconfig[i, k]
        for i in range(REDUCED):
            dG[QDIM + i] = _a(float(reduced_weights[i])) * (
                db * psi[i] + bpsi * dline[i, k]
                + ds[k] * hard[i] + s * dresponse[i, k]
            )
        dn = _a(0)
        for i in range(STATE):
            dn += G[i] * dG[i]
        dn /= norm
        for i in range(STATE):
            derivative[i, k] = (dG[i] - G[i] * dn / norm) / norm
        derivative[STATE, k] = ddelta / norm - delta * dn / norm**2
    return RateEnclosure(value, derivative, gap - eigen_residual, eigen_residual, jets)


def _arb_action_jets(state_values: np.ndarray) -> ActionJets:
    """Outward raw g/H and a correlated local representation of D3S."""
    state = [_a(value) for value in np.asarray(state_values, dtype=object)]
    bulk_value = _a(0); inertia_value = _a(0)
    bulk_gradient = [_a(0) for _ in range(STATE)]
    inertia_gradient = [_a(0) for _ in range(STATE)]
    bulk_hessian = [[_a(0) for _ in range(STATE)] for _ in range(STATE)]
    inertia_hessian = [[_a(0) for _ in range(STATE)] for _ in range(STATE)]
    bulk_third_terms: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    inertia_third_terms: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def accumulate(term: Mixed, maps: Sequence[Sequence[tuple[int, arb]]], gradient: list[arb], hessian: list[list[arb]]) -> None:
        local_gradient = np.asarray(term.d[1], dtype=object).reshape(len(maps))
        local_hessian = np.asarray(term.d[3], dtype=object).reshape(len(maps), len(maps))
        for a, mapping in enumerate(maps):
            for i, ci in mapping:
                gradient[i] += local_gradient[a] * ci
        for a, left_map in enumerate(maps):
            for b, right_map in enumerate(maps):
                coefficient = local_hessian[a, b]
                for i, ci in left_map:
                    for j, cj in right_map:
                        hessian[i][j] += coefficient * ci * cj

    for node in range(POINTS):
        term = _integrand(state, node, 2)
        bulk_value += term.bulk.d[0]; inertia_value += term.inertia.d[0]
        accumulate(term.bulk, term.maps, bulk_gradient, bulk_hessian)
        accumulate(term.inertia, term.maps, inertia_gradient, inertia_hessian)
        mapping = _dense_mapping(term.maps)
        bulk_third_terms.append((mapping, np.empty(0), np.empty(0)))
        inertia_third_terms.append((mapping, np.empty(0), np.empty(0)))

    boundary_maps, boundary = _boundary(state, 2)
    accumulate(boundary, boundary_maps, bulk_gradient, bulk_hessian)
    boundary_mapping = _dense_mapping(boundary_maps)
    bulk_third_terms.append((boundary_mapping, np.empty(0), np.empty(0)))

    coefficient = _a(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2))
    gradient = [
        bulk_gradient[i] + coefficient * inertia_gradient[i] / inertia_value**2
        for i in range(STATE)
    ]
    hessian = [[
        bulk_hessian[i][j] + coefficient * (
            inertia_hessian[i][j] / inertia_value**2
            - 2 * inertia_gradient[i] * inertia_gradient[j] / inertia_value**3
        )
        for j in range(STATE)] for i in range(STATE)
    ]

    gm, gr = _midrad(np.asarray(gradient, dtype=object))
    hm, hr = _midrad(np.asarray(hessian, dtype=object))

    igm, igr = _midrad(np.asarray(inertia_gradient, dtype=object))
    ihm, ihr = _midrad(np.asarray(inertia_hessian, dtype=object))

    return ActionJets(
        np.asarray(gradient, dtype=object), np.asarray(hessian, dtype=object),
        np.asarray(gm, dtype=float), np.asarray(gr + np.abs(gm - np.asarray(gm, dtype=float)), dtype=float),
        np.asarray(hm, dtype=float), np.asarray(hr + np.abs(hm - np.asarray(hm, dtype=float)), dtype=float),
        bulk_third_terms, inertia_third_terms, inertia_value,
        np.asarray(igm, dtype=float), np.asarray(igr, dtype=float),
        np.asarray(ihm, dtype=float), np.asarray(ihr, dtype=float),
        [item[0] for item in bulk_third_terms[:POINTS]],
    )


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".json", ".md"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _aggregate_sha256(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256(path)))
    return digest.hexdigest().upper()


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(values, dtype=object)
    midpoint = np.empty(array.shape, dtype=float)
    radius = np.empty(array.shape, dtype=float)
    for index in np.ndindex(array.shape):
        midpoint[index], radius[index] = _center_radius(array[index])
    return midpoint, radius


def _arb_string_array(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=object)
    result = np.empty(array.shape, dtype="<U180")
    for index in np.ndindex(array.shape):
        result[index] = array[index].str(140)
    return result


def _parse_arb_string_array(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values)
    result = np.empty(array.shape, dtype=object)
    for index in np.ndindex(array.shape):
        result[index] = arb(str(array[index]))
    return result


def _frame(tangent: np.ndarray, scale: float) -> np.ndarray:
    result = np.zeros((99, 74))
    result[:98, :73] = tangent
    result[98, 73] = scale
    return result


def _arb_matrix(midpoint: np.ndarray, radius: np.ndarray | None = None) -> arb_mat:
    """Materialize a binary input, or an exported ball, as an Arb matrix."""
    midpoint = np.asarray(midpoint, dtype=float)
    if radius is None:
        return arb_mat([[arb(float(value)) for value in row] for row in midpoint])
    radius = np.asarray(radius, dtype=float)
    return arb_mat([
        [arb(float(value), float(error)) for value, error in zip(row, errors)]
        for row, errors in zip(midpoint, radius)
    ])


def _arb_vector(midpoint: np.ndarray, radius: np.ndarray | None = None) -> arb_mat:
    midpoint = np.asarray(midpoint, dtype=float).reshape(-1)
    if radius is None:
        return arb_mat([[arb(float(value))] for value in midpoint])
    radius = np.asarray(radius, dtype=float).reshape(-1)
    return arb_mat([
        [arb(float(value), float(error))]
        for value, error in zip(midpoint, radius)
    ])


def _arb_mat_from_array(values: np.ndarray) -> arb_mat:
    array = np.asarray(values, dtype=object)
    if array.ndim == 1:
        return arb_mat([[array[i]] for i in range(array.shape[0])])
    return arb_mat([[array[i, j] for j in range(array.shape[1])] for i in range(array.shape[0])])


def _matrix_export(value: arb_mat) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty((value.nrows(), value.ncols()), dtype=float)
    radius = np.empty_like(midpoint)
    for i in range(value.nrows()):
        for j in range(value.ncols()):
            midpoint[i, j], radius[i, j] = _center_radius(value[i, j])
    return midpoint, radius


def _vector_norm_upper(value: arb_mat) -> float:
    total = arb(0)
    for i in range(value.nrows()):
        total += value[i, 0] ** 2
    return float(total.sqrt().upper())


def _verified_solve(matrix: arb_mat, rhs: arb_mat) -> arb_mat:
    """Solve an interval linear system, with a residual/Neumann fallback."""
    try:
        return matrix.solve(rhs, algorithm="precond")
    except ZeroDivisionError:
        pass
    midpoint = arb_mat(matrix.nrows(), matrix.ncols())
    for i in range(matrix.nrows()):
        for j in range(matrix.ncols()):
            midpoint[i, j] = arb(float(matrix[i, j]))
    midpoint_rhs = arb_mat(rhs.nrows(), rhs.ncols())
    for i in range(rhs.nrows()):
        for j in range(rhs.ncols()):
            midpoint_rhs[i, j] = arb(float(rhs[i, j]))
    try:
        inverse = midpoint.inv()
    except ZeroDivisionError:
        midpoint_binary = np.asarray([
            [float(midpoint[i, j]) for j in range(midpoint.ncols())]
            for i in range(midpoint.nrows())
        ], dtype=float)
        inverse = _arb_matrix(np.linalg.inv(midpoint_binary))
    approximation = inverse * midpoint_rhs
    identity = arb_mat(np.eye(matrix.nrows(), dtype=int).tolist())
    remainder = identity - inverse * matrix
    q = arb(0)
    for i in range(remainder.nrows()):
        row = arb(0)
        for j in range(remainder.ncols()):
            row += abs(remainder[i, j])
        if row.upper() > q.upper():
            q = row
    q_upper = float(q.upper())
    if not q_upper < 1.0:
        raise ArithmeticError(
            f"bordered interval Neumann factor does not contract: {q_upper}"
        )
    defect = inverse * (rhs - matrix * approximation)
    result = arb_mat(approximation.nrows(), approximation.ncols())
    for column in range(approximation.ncols()):
        defect_upper = max(
            float(abs(defect[i, column]).upper())
            for i in range(defect.nrows())
        )
        correction = math.nextafter(defect_upper / (1.0 - q_upper), math.inf)
        for i in range(approximation.nrows()):
            result[i, column] = approximation[i, column] + arb(0, correction)
    return result


def _linear_composition() -> None:
    """Compose outward Y and the exact frozen-A linear defect blocks.

    The expensive action contractions are already present in WORK.  All
    projections and frozen reduced inverses below are recomputed in Arb from
    the stored binary inputs, which are thereby interpreted as exact dyadics.
    """
    ctx.prec = PRECISION
    missing = [
        str(WORK / f"endpoint_{i:03d}.npz") for i in range(371)
        if not (WORK / f"endpoint_{i:03d}.npz").exists()
    ] + [
        str(WORK / f"midpoint_{i:03d}.npz") for i in range(370)
        if not (WORK / f"midpoint_{i:03d}.npz").exists()
    ]
    if missing:
        raise RuntimeError(f"missing {len(missing)} retained action shards")

    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    centers = np.column_stack((states * weights[None, :], descriptors))
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right_reduced = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    endpoint = [np.load(WORK / f"endpoint_{i:03d}.npz") for i in range(371)]
    midpoint = [np.load(WORK / f"midpoint_{i:03d}.npz") for i in range(370)]
    coordinate = arb_mat(74, 1)
    maximum_y = 0.0
    maximum_y_owner = 0
    c_mid = np.empty((370, 74, 74)); c_rad = np.empty_like(c_mid)
    dl_mid = np.empty_like(c_mid); dl_rad = np.empty_like(c_mid)
    dr_mid = np.empty_like(c_mid); dr_rad = np.empty_like(c_mid)
    maximum_gap_residual = 0.0
    minimum_gap = math.inf

    for interval, h_float in enumerate(np.diff(times)):
        h = arb(float(h_float))
        test_np = _frame(tangents[interval + 1], TEST_DESCRIPTOR_SCALE)
        trial_left_np = _frame(tangents[interval], TRIAL_DESCRIPTOR_SCALE)
        test = _arb_matrix(test_np.T)
        trial_left = _arb_matrix(trial_left_np)
        frozen_left = _arb_matrix(old_left[interval])
        frozen_reduced_right = _arb_matrix(old_right_reduced[interval])
        frozen_inverse = frozen_reduced_right.inv()

        e0 = _arb_mat_from_array(_parse_arb_string_array(endpoint[interval]["value_arb"]))
        e1 = _arb_mat_from_array(_parse_arb_string_array(endpoint[interval + 1]["value_arb"]))
        em = _arb_mat_from_array(_parse_arb_string_array(midpoint[interval]["value_arb"]))
        center0 = _arb_vector(centers[interval])
        center1 = _arb_vector(centers[interval + 1])
        residual = center1 - center0 - h * (e0 + 4 * em + e1) / 6
        reduced_residual = test * residual
        coordinate = -frozen_inverse * (
            reduced_residual + test * frozen_left * trial_left * coordinate
        )
        y_here = _vector_norm_upper(coordinate)
        if y_here > maximum_y:
            maximum_y = y_here
            maximum_y_owner = interval + 1

        endpoint_left = _arb_mat_from_array(_parse_arb_string_array(
            endpoint[interval]["derivative_arb"],
        ))
        endpoint_right = _arb_mat_from_array(_parse_arb_string_array(
            endpoint[interval + 1]["derivative_arb"],
        ))
        midpoint_derivative = _parse_arb_string_array(
            midpoint[interval]["derivative_arb"],
        )
        midpoint_left = _arb_mat_from_array(midpoint_derivative[:, :74])
        midpoint_right = _arb_mat_from_array(midpoint_derivative[:, 74:])
        new_left = -trial_left - h * (endpoint_left + 4 * midpoint_left) / 6
        trial_right_np = _frame(tangents[interval + 1], TRIAL_DESCRIPTOR_SCALE)
        trial_right = _arb_matrix(trial_right_np)
        new_right = trial_right - h * (4 * midpoint_right + endpoint_right) / 6
        frozen_left_reduced = test * frozen_left * trial_left
        new_left_reduced = test * new_left
        new_right_reduced = test * new_right
        c_value = frozen_inverse * frozen_left_reduced
        dl_value = frozen_inverse * (frozen_left_reduced - new_left_reduced)
        dr_value = frozen_inverse * (frozen_reduced_right - new_right_reduced)
        np.savez_compressed(
            WORK / f"linear_{interval:03d}.npz",
            C_arb=_arb_string_array(_array(c_value)),
            DL_arb=_arb_string_array(_array(dl_value)),
            DR_arb=_arb_string_array(_array(dr_value)),
            precision_bits=np.asarray(PRECISION),
        )
        c_mid[interval], c_rad[interval] = _matrix_export(c_value)
        dl_mid[interval], dl_rad[interval] = _matrix_export(dl_value)
        dr_mid[interval], dr_rad[interval] = _matrix_export(dr_value)
        minimum_gap = min(
            minimum_gap,
            float(endpoint[interval]["gap_lower"]),
            float(endpoint[interval + 1]["gap_lower"]),
            float(midpoint[interval]["gap_lower"]),
        )
        maximum_gap_residual = max(
            maximum_gap_residual,
            float(endpoint[interval]["eigen_residual_upper"]),
            float(endpoint[interval + 1]["eigen_residual_upper"]),
            float(midpoint[interval]["eigen_residual_upper"]),
        )
        if (interval + 1) % 10 == 0 or interval == 369:
            print(json.dumps({"linear_composition_completed": interval + 1}), flush=True)

    descriptor_coordinate_ceiling = float(descriptors[-1] / TRIAL_DESCRIPTOR_SCALE)
    linear_data = WORK / "linear_composition.npz"
    np.savez_compressed(
        linear_data,
        C_mid=c_mid, C_rad=c_rad,
        DL_mid=dl_mid, DL_rad=dl_rad,
        DR_mid=dr_mid, DR_rad=dr_rad,
        outward_Y_causal_74D_block_sup=np.asarray(maximum_y),
        outward_Y_owner_node=np.asarray(maximum_y_owner),
        descriptor_coordinate_domain_ceiling=np.asarray(descriptor_coordinate_ceiling),
        minimum_branch_gap_lower=np.asarray(minimum_gap),
        maximum_eigen_residual_upper=np.asarray(maximum_gap_residual),
    )
    print(json.dumps({
        "outward_Y_causal_74D_block_sup": maximum_y,
        "outward_Y_owner_node": maximum_y_owner,
        "descriptor_coordinate_domain_ceiling": descriptor_coordinate_ceiling,
        "minimum_branch_gap_lower": minimum_gap,
        "maximum_eigen_residual_upper": maximum_gap_residual,
        "linear_data": str(linear_data),
    }, indent=2, sort_keys=True))


def _positive_dot_upper(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Upper bound a nonnegative binary64 matrix product."""
    inner = left.shape[1]
    gamma = inner * np.finfo(float).eps / (1.0 - inner * np.finfo(float).eps)
    value = left @ right
    value = value / (1.0 - gamma)
    return np.nextafter(value, math.inf)


def _ball_matmul(
    left_mid: np.ndarray,
    left_rad: np.ndarray,
    right_mid: np.ndarray,
    right_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Directed binary64 enclosure of a dense interval matrix product."""
    inner = left_mid.shape[1]
    eps = np.finfo(float).eps
    gamma = inner * eps / (1.0 - inner * eps)
    midpoint = left_mid @ right_mid
    absolute_center_product = _positive_dot_upper(np.abs(left_mid), np.abs(right_mid))
    center_roundoff = np.nextafter(gamma * absolute_center_product, math.inf)
    cross = _positive_dot_upper(np.abs(left_mid), right_rad)
    cross = np.nextafter(
        cross + _positive_dot_upper(left_rad, np.abs(right_mid)), math.inf,
    )
    cross = np.nextafter(
        cross + _positive_dot_upper(left_rad, right_rad), math.inf,
    )
    radius = np.nextafter(cross + center_roundoff, math.inf)
    return midpoint, radius


def _ball_add(
    left_mid: np.ndarray,
    left_rad: np.ndarray,
    right_mid: np.ndarray,
    right_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    midpoint = left_mid + right_mid
    rounding = np.finfo(float).eps * (np.abs(left_mid) + np.abs(right_mid))
    radius = np.nextafter(left_rad + right_rad + rounding, math.inf)
    return midpoint, radius


def _block_row_frobenius_sum_upper(midpoint: np.ndarray, radius: np.ndarray) -> float:
    blocks = midpoint.reshape(74, -1, 74).transpose(1, 0, 2)
    errors = radius.reshape(74, -1, 74).transpose(1, 0, 2)
    magnitude = np.nextafter(np.abs(blocks) + errors, math.inf)
    squared = magnitude * magnitude
    count = squared.shape[1] * squared.shape[2]
    gamma = count * np.finfo(float).eps / (1.0 - count * np.finfo(float).eps)
    sums = np.sum(squared, axis=(1, 2)) / (1.0 - gamma)
    norms = np.nextafter(np.sqrt(np.nextafter(sums, math.inf)), math.inf)
    total_gamma = len(norms) * np.finfo(float).eps / (
        1.0 - len(norms) * np.finfo(float).eps
    )
    return math.nextafter(float(np.sum(norms) / (1.0 - total_gamma)), math.inf)


def _compose_z1() -> None:
    """Bound the frozen-preconditioner linear defect in the causal block norm."""
    exact_shards = [WORK / f"linear_{i:03d}.npz" for i in range(370)]
    if all(path.exists() for path in exact_shards):
        ctx.prec = PRECISION
        row = arb_mat(74, 0)
        maximum = 0.0
        owner = 0
        rows: list[float] = []
        for interval, shard in enumerate(exact_shards):
            with np.load(shard) as source:
                if int(source["precision_bits"]) != PRECISION:
                    raise RuntimeError("linear Arb shard precision mismatch")
                c_value = _arb_mat_from_array(_parse_arb_string_array(source["C_arb"]))
                dl_value = _arb_mat_from_array(_parse_arb_string_array(source["DL_arb"]))
                dr_value = _arb_mat_from_array(_parse_arb_string_array(source["DR_arb"]))
            row = -c_value * row
            if interval > 0:
                offset = row.ncols() - 74
                for i in range(74):
                    for j in range(74):
                        row[i, offset + j] += dl_value[i, j]
            extended = arb_mat(74, row.ncols() + 74)
            for i in range(74):
                for j in range(row.ncols()):
                    extended[i, j] = row[i, j]
                for j in range(74):
                    extended[i, row.ncols() + j] = dr_value[i, j]
            row = extended
            row_mid, row_rad = _matrix_export(row)
            bound = _block_row_frobenius_sum_upper(row_mid, row_rad)
            rows.append(bound)
            if bound > maximum:
                maximum = bound
                owner = interval + 1
            if (interval + 1) % 10 == 0 or interval == 369:
                print(json.dumps({
                    "z1_Arb_rows_completed": interval + 1,
                    "current_row_upper": bound,
                    "maximum_upper": maximum,
                }), flush=True)
        np.savez_compressed(WORK / "z1_composition.npz", row_upper=np.asarray(rows))
        print(json.dumps({
            "outward_Z1_causal_74D_block_sup_Frobenius_row_upper": maximum,
            "outward_Z1_owner_node": owner,
            "precision_bits": PRECISION,
        }, indent=2, sort_keys=True))
        return
    path = WORK / "linear_composition.npz"
    if not path.exists():
        raise RuntimeError("run --compose-linear first")
    with np.load(path) as source:
        c_mid = np.asarray(source["C_mid"], dtype=float)
        c_rad = np.asarray(source["C_rad"], dtype=float)
        dl_mid = np.asarray(source["DL_mid"], dtype=float)
        dl_rad = np.asarray(source["DL_rad"], dtype=float)
        dr_mid = np.asarray(source["DR_mid"], dtype=float)
        dr_rad = np.asarray(source["DR_rad"], dtype=float)
    row_mid = np.empty((74, 0), dtype=float)
    row_rad = np.empty_like(row_mid)
    maximum = 0.0
    owner = 0
    rows = []
    for interval in range(370):
        if row_mid.shape[1]:
            row_mid, row_rad = _ball_matmul(
                -c_mid[interval], c_rad[interval], row_mid, row_rad,
            )
        if interval > 0:
            updated_mid, updated_rad = _ball_add(
                row_mid[:, -74:], row_rad[:, -74:],
                dl_mid[interval], dl_rad[interval],
            )
            row_mid[:, -74:] = updated_mid
            row_rad[:, -74:] = updated_rad
        row_mid = np.column_stack((row_mid, dr_mid[interval]))
        row_rad = np.column_stack((row_rad, dr_rad[interval]))
        bound = _block_row_frobenius_sum_upper(row_mid, row_rad)
        rows.append(bound)
        if bound > maximum:
            maximum = bound
            owner = interval + 1
        if (interval + 1) % 10 == 0 or interval == 369:
            print(json.dumps({
                "z1_rows_completed": interval + 1,
                "current_row_upper": bound,
                "maximum_upper": maximum,
            }), flush=True)
    np.savez_compressed(WORK / "z1_composition.npz", row_upper=np.asarray(rows))
    print(json.dumps({
        "outward_Z1_causal_74D_block_sup_Frobenius_row_upper": maximum,
        "outward_Z1_owner_node": owner,
    }, indent=2, sort_keys=True))


def _compose_z2(radius: float) -> None:
    """Compose a fixed-radius outward nonlinear Jacobian variation.

    The interval derivative is evaluated directly over the complete causal
    block-sup ball.  Dividing its composed variation by ``radius`` defines a
    conservative radii-polynomial ``Z2`` coefficient at this radius.  Thus
    ``Z2*r`` bounds the complete nonlinear derivative variation, while the
    conventional ``Z1 + 2*Z2*r`` contraction test retains an extra factor of
    two rather than assuming radial homogeneity of the interval evaluation.
    """
    ctx.prec = PRECISION
    missing = [
        str(_tube_target("endpoint", i)) for i in range(371)
        if not _tube_target("endpoint", i).exists()
    ] + [
        str(_tube_target("midpoint", i)) for i in range(370)
        if not _tube_target("midpoint", i).exists()
    ]
    if missing:
        raise RuntimeError(f"missing {len(missing)} tube shards")
    linear_path = WORK / "linear_composition.npz"
    z1_path = WORK / "z1_composition.npz"
    if not linear_path.exists() or not z1_path.exists():
        raise RuntimeError("run both linear compositions first")
    with np.load(linear_path) as source:
        required = {
            "outward_Y_causal_74D_block_sup",
            "descriptor_coordinate_domain_ceiling",
        }
        if not required.issubset(source.files):
            raise RuntimeError("linear composition predates summary metadata")
        outward_y = float(source["outward_Y_causal_74D_block_sup"])
        descriptor_ceiling = float(source["descriptor_coordinate_domain_ceiling"])
    with np.load(z1_path) as source:
        z1_rows = np.asarray(source["row_upper"], dtype=float)
    outward_z1 = float(np.max(z1_rows))

    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right_reduced = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    center_endpoint = [
        np.load(WORK / f"endpoint_{i:03d}.npz") for i in range(371)
    ]
    center_midpoint = [
        np.load(WORK / f"midpoint_{i:03d}.npz") for i in range(370)
    ]
    tube_endpoint = [
        np.load(_tube_target("endpoint", i)) for i in range(371)
    ]
    tube_midpoint = [
        np.load(_tube_target("midpoint", i)) for i in range(370)
    ]
    for source in (*tube_endpoint, *tube_midpoint):
        if float(source["domain_radius"]) != float(radius):
            raise RuntimeError("tube radius mismatch")
        if int(source["precision_bits"]) != PRECISION:
            raise RuntimeError("tube precision mismatch")

    row = arb_mat(74, 0)
    maximum = 0.0
    owner = 0
    rows: list[float] = []
    center_inclusion_failures = 0
    minimum_descriptor_lower = math.inf
    minimum_gap = math.inf
    maximum_eigen_residual = 0.0
    maximum_state_radius = 0.0
    for interval, h_float in enumerate(np.diff(times)):
        h = _a(float(h_float))
        test = _arb_matrix(_frame(
            tangents[interval + 1], TEST_DESCRIPTOR_SCALE,
        ).T)
        trial_left = _arb_matrix(_frame(
            tangents[interval], TRIAL_DESCRIPTOR_SCALE,
        ))
        trial_right = _arb_matrix(_frame(
            tangents[interval + 1], TRIAL_DESCRIPTOR_SCALE,
        ))
        frozen_left = _arb_matrix(old_left[interval])
        frozen_inverse = _arb_matrix(old_right_reduced[interval]).inv()

        center_e0 = _arb_mat_from_array(_parse_arb_string_array(
            center_endpoint[interval]["derivative_arb"],
        ))
        center_e1 = _arb_mat_from_array(_parse_arb_string_array(
            center_endpoint[interval + 1]["derivative_arb"],
        ))
        center_m_array = _parse_arb_string_array(
            center_midpoint[interval]["derivative_arb"],
        )
        center_ml = _arb_mat_from_array(center_m_array[:, :74])
        center_mr = _arb_mat_from_array(center_m_array[:, 74:])
        tube_e0 = _arb_mat_from_array(_parse_arb_string_array(
            tube_endpoint[interval]["derivative_arb"],
        ))
        tube_e1 = _arb_mat_from_array(_parse_arb_string_array(
            tube_endpoint[interval + 1]["derivative_arb"],
        ))
        tube_m_array = _parse_arb_string_array(
            tube_midpoint[interval]["derivative_arb"],
        )
        tube_ml = _arb_mat_from_array(tube_m_array[:, :74])
        tube_mr = _arb_mat_from_array(tube_m_array[:, 74:])

        center_left = -trial_left - h * (center_e0 + 4 * center_ml) / 6
        center_right = trial_right - h * (4 * center_mr + center_e1) / 6
        tube_left = -trial_left - h * (tube_e0 + 4 * tube_ml) / 6
        tube_right = trial_right - h * (4 * tube_mr + tube_e1) / 6
        variation_left = frozen_inverse * test * (tube_left - center_left)
        variation_right = frozen_inverse * test * (tube_right - center_right)

        with np.load(WORK / f"linear_{interval:03d}.npz") as source:
            c_value = _arb_mat_from_array(_parse_arb_string_array(source["C_arb"]))
        row = -c_value * row
        if interval > 0:
            offset = row.ncols() - 74
            for i in range(74):
                for j in range(74):
                    row[i, offset + j] += variation_left[i, j]
        extended = arb_mat(74, row.ncols() + 74)
        for i in range(74):
            for j in range(row.ncols()):
                extended[i, j] = row[i, j]
            for j in range(74):
                extended[i, row.ncols() + j] = variation_right[i, j]
        row = extended
        row_mid, row_rad = _matrix_export(row)
        bound = _block_row_frobenius_sum_upper(row_mid, row_rad)
        rows.append(bound)
        if bound > maximum:
            maximum = bound
            owner = interval + 1

        for source in (
            tube_endpoint[interval], tube_endpoint[interval + 1],
            tube_midpoint[interval],
        ):
            minimum_descriptor_lower = min(
                minimum_descriptor_lower, float(source["descriptor_lower"]),
            )
            minimum_gap = min(minimum_gap, float(source["gap_lower"]))
            maximum_eigen_residual = max(
                maximum_eigen_residual, float(source["eigen_residual_upper"]),
            )
            maximum_state_radius = max(
                maximum_state_radius, float(source["maximum_state_radius"]),
            )

        # A failed center inclusion indicates an implementation/provenance
        # mismatch, not a bound to be widened.  Test after all exact algebra
        # has been assembled in the common residual frame.
        for candidate in (variation_left, variation_right):
            for i in range(candidate.nrows()):
                for j in range(candidate.ncols()):
                    if not candidate[i, j].contains(0):
                        center_inclusion_failures += 1
        if (interval + 1) % 10 == 0 or interval == 369:
            print(json.dumps({
                "z2_interval_rows_completed": interval + 1,
                "current_variation_upper": bound,
                "maximum_variation_upper": maximum,
            }), flush=True)

    outward_z2 = math.nextafter(maximum / float(radius), math.inf)
    p_value = (
        _a(outward_y) + _a(outward_z1) * _a(radius)
        + _a(outward_z2) * _a(radius) ** 2
    )
    contraction_value = _a(outward_z1) + 2 * _a(outward_z2) * _a(radius)
    self_map_upper = math.nextafter(float(p_value.upper()), math.inf)
    contraction_upper = math.nextafter(float(contraction_value.upper()), math.inf)
    validation = {
        "radius_strictly_inside_descriptor_domain": radius < descriptor_ceiling,
        "all_endpoint_and_midpoint_descriptors_positive": minimum_descriptor_lower > 0.0,
        "selected_branch_uniformly_simple": minimum_gap > 0.0,
        "center_derivative_contained_in_every_tube_block": center_inclusion_failures == 0,
        "radii_polynomial_strict_self_map": self_map_upper < radius,
        "radii_polynomial_strict_contraction": contraction_upper < 1.0,
    }
    passed = all(validation.values())
    np.savez_compressed(
        WORK / "z2_composition.npz",
        row_variation_upper=np.asarray(rows),
        domain_radius=np.asarray(radius),
        outward_Y=np.asarray(outward_y),
        outward_Z1=np.asarray(outward_z1),
        outward_Z2=np.asarray(outward_z2),
        self_map_upper=np.asarray(self_map_upper),
        contraction_upper=np.asarray(contraction_upper),
    )
    print(json.dumps({
        "status": (
            "ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION_VALIDATED"
            if passed else
            "ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION_INVALIDATED_AT_RADIUS"
        ),
        "outward_Y": outward_y,
        "outward_Z1": outward_z1,
        "outward_Z2_fixed_radius_conservative": outward_z2,
        "radius": radius,
        "maximum_composed_derivative_variation_upper": maximum,
        "maximum_variation_owner_node": owner,
        "self_map_upper": self_map_upper,
        "contraction_upper": contraction_upper,
        "descriptor_coordinate_domain_ceiling": descriptor_ceiling,
        "minimum_descriptor_lower": minimum_descriptor_lower,
        "minimum_branch_gap_lower": minimum_gap,
        "maximum_eigen_residual_upper": maximum_eigen_residual,
        "maximum_state_component_radius": maximum_state_radius,
        "center_inclusion_failures": center_inclusion_failures,
        "validation": validation,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


def _outward_y_bounds() -> tuple[float, float, int]:
    """Return rigorous lower/upper bounds for the accepted-center ``Y``."""
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    centers = np.column_stack((states * weights[None, :], descriptors))
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        old_left = np.asarray(source["left_Newton_blocks"], dtype=float)
        old_right = np.asarray(
            source["reduced_right_Newton_blocks"], dtype=float,
        )
    coordinate = arb_mat(74, 1)
    maximum_upper = 0.0
    owner_lower = 0.0
    owner = 0
    for interval, h_float in enumerate(np.diff(times)):
        h = _a(float(h_float))
        e0 = _arb_mat_from_array(_parse_arb_string_array(
            np.load(WORK / f"endpoint_{interval:03d}.npz")["value_arb"],
        ))
        e1 = _arb_mat_from_array(_parse_arb_string_array(
            np.load(WORK / f"endpoint_{interval + 1:03d}.npz")["value_arb"],
        ))
        em = _arb_mat_from_array(_parse_arb_string_array(
            np.load(WORK / f"midpoint_{interval:03d}.npz")["value_arb"],
        ))
        residual = (
            _arb_vector(centers[interval + 1])
            - _arb_vector(centers[interval]) - h * (e0 + 4 * em + e1) / 6
        )
        test = _arb_matrix(_frame(
            tangents[interval + 1], TEST_DESCRIPTOR_SCALE,
        ).T)
        trial = _arb_matrix(_frame(
            tangents[interval], TRIAL_DESCRIPTOR_SCALE,
        ))
        inverse = _arb_matrix(old_right[interval]).inv()
        coordinate = -inverse * (
            test * residual
            + test * _arb_matrix(old_left[interval]) * trial * coordinate
        )
        vector = _array(coordinate).ravel()
        upper = _norm_upper(vector)
        if upper > maximum_upper:
            maximum_upper = upper
            owner_lower = _arb_norm_lower(vector)
            owner = interval + 1
    return owner_lower, maximum_upper, owner


def _accepted_center_curvature_obstruction() -> None:
    """Certify the one-direction obstruction to every accepted-center radius.

    A valid same-center ``Z2`` must dominate the derivative at the center of
    the preconditioned Jacobian in every unit causal direction.  Therefore a
    single rigorous directional lower bound, together with a rigorous lower
    bound for ``Y``, can disprove the radii polynomial without constructing a
    dense upper tensor.  The numerical reconnaissance uniquely localized this
    check to accepted node 1, causal coordinate 61.
    """
    ctx.prec = PRECISION
    node = 1
    direction_index = 61
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        states = np.asarray(source["projected_states"], dtype=float)
        descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(REPLAY.with_suffix(".npz")) as source:
        midpoint_values = np.asarray(
            source["midpoint_augmented_action_values"], dtype=float,
        )
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(
            source["endpoint_physical_tangent_action"], dtype=float,
        )
    with np.load(PRECONDITIONER.with_suffix(".npz")) as source:
        right = np.asarray(source["reduced_right_Newton_blocks"], dtype=float)

    frame = _frame(tangents[node], TRIAL_DESCRIPTOR_SCALE)
    direction = np.asarray([
        _a(float(value)) for value in frame[:, direction_index]
    ], dtype=object)
    endpoint_second = _rate_second_directional(
        states[node], float(descriptors[node]), weights, reference, direction,
    )
    with np.load(WORK / f"endpoint_{node:03d}.npz") as source:
        endpoint_first = _parse_arb_string_array(
            source["derivative_arb"],
        )[:, direction_index]

    local_coordinates: list[arb_mat] = []
    local_field_coordinates: list[arb_mat] = []
    local_descriptor_coordinates: list[arb_mat] = []
    stage_records: list[dict[str, object]] = []
    local_intervals = (node - 1, node)
    for interval in local_intervals:
        h = _a(float(times[interval + 1] - times[interval]))
        is_right = interval == node - 1
        sign = -1 if is_right else 1
        midpoint_first = np.asarray([
            _a(0.5) * direction[i] + sign * h * endpoint_first[i] / 8
            for i in range(STATE + 1)
        ], dtype=object)
        midpoint_second_incidence = np.asarray([
            sign * h * endpoint_second[i] / 8 for i in range(STATE + 1)
        ], dtype=object)
        midpoint_augmented = midpoint_values[interval]
        midpoint_state = midpoint_augmented[:STATE] / weights
        midpoint_descriptor = float(midpoint_augmented[STATE])
        intrinsic_midpoint_second = _rate_second_directional(
            midpoint_state, midpoint_descriptor, weights, reference,
            midpoint_first,
        )
        midpoint_linear = _rate_enclosure(
            midpoint_state, midpoint_descriptor, weights, reference,
            midpoint_second_incidence[:, None],
        ).derivative[:, 0]
        midpoint_second = np.asarray([
            intrinsic_midpoint_second[i] + midpoint_linear[i]
            for i in range(STATE + 1)
        ], dtype=object)
        residual_second = np.asarray([
            -h * (endpoint_second[i] + 4 * midpoint_second[i]) / 6
            for i in range(STATE + 1)
        ], dtype=object)
        test = _arb_matrix(_frame(
            tangents[interval + 1], TEST_DESCRIPTOR_SCALE,
        ).T)
        inverse = _arb_matrix(right[interval]).inv()
        residual_field = residual_second.copy()
        residual_field[STATE] = _a(0)
        residual_descriptor = np.asarray(
            [_a(0) for _ in range(STATE + 1)], dtype=object,
        )
        residual_descriptor[STATE] = residual_second[STATE]
        tested = test * _arb_mat_from_array(residual_second)
        tested_field = test * _arb_mat_from_array(residual_field)
        tested_descriptor = test * _arb_mat_from_array(residual_descriptor)
        local = -inverse * tested
        local_field = -inverse * tested_field
        local_descriptor = -inverse * tested_descriptor
        local_coordinates.append(local)
        local_field_coordinates.append(local_field)
        local_descriptor_coordinates.append(local_descriptor)
        endpoint_hs = np.asarray([
            -h * endpoint_second[i] / 6 for i in range(STATE + 1)
        ], dtype=object)
        midpoint_intrinsic_hs = np.asarray([
            -4 * h * intrinsic_midpoint_second[i] / 6
            for i in range(STATE + 1)
        ], dtype=object)
        midpoint_incidence_hs = np.asarray([
            -4 * h * midpoint_linear[i] / 6 for i in range(STATE + 1)
        ], dtype=object)
        stage_records.append({
            "interval": interval,
            "action_interval": [
                float(times[interval]), float(times[interval + 1]),
            ],
            "midpoint_action_coordinate": float(
                0.5 * (times[interval] + times[interval + 1])
            ),
            "raw_endpoint_rate_second": _arb_norm_bounds(endpoint_second),
            "raw_endpoint_configuration_rate_second": _arb_norm_bounds(
                endpoint_second[:QDIM]
            ),
            "raw_endpoint_reduced_field_rate_second": _arb_norm_bounds(
                endpoint_second[QDIM:STATE]
            ),
            "raw_endpoint_descriptor_rate_second": _arb_norm_bounds(
                endpoint_second[STATE:]
            ),
            "HS_endpoint_term": _arb_norm_bounds(endpoint_hs),
            "HS_intrinsic_midpoint_term": _arb_norm_bounds(
                midpoint_intrinsic_hs
            ),
            "HS_midpoint_incidence_term": _arb_norm_bounds(
                midpoint_incidence_hs
            ),
            "HS_complete_residual_second": _arb_norm_bounds(residual_second),
            "HS_field_output_only": _arb_norm_bounds(residual_field),
            "HS_descriptor_output_only": _arb_norm_bounds(
                residual_descriptor
            ),
            "after_test_frame": _arb_norm_bounds(_array(tested)),
            "after_test_frame_field_output_only": _arb_norm_bounds(
                _array(tested_field)
            ),
            "after_test_frame_descriptor_output_only": _arb_norm_bounds(
                _array(tested_descriptor)
            ),
            "after_frozen_preconditioner": _arb_norm_bounds(_array(local)),
            "after_frozen_preconditioner_field_output_only": (
                _arb_norm_bounds(_array(local_field))
            ),
            "after_frozen_preconditioner_descriptor_output_only": (
                _arb_norm_bounds(_array(local_descriptor))
            ),
        })

    contributions: list[arb_mat] = []
    field_contributions: list[arb_mat] = []
    descriptor_contributions: list[arb_mat] = []
    for position, (local, interval) in enumerate(zip(
        local_coordinates, local_intervals, strict=True,
    )):
        transported = local
        transported_field = local_field_coordinates[position]
        transported_descriptor = local_descriptor_coordinates[position]
        for later in range(interval + 1, 370):
            with np.load(WORK / f"linear_{later:03d}.npz") as source:
                C = _arb_mat_from_array(_parse_arb_string_array(source["C_arb"]))
            transported = -C * transported
            transported_field = -C * transported_field
            transported_descriptor = -C * transported_descriptor
        contributions.append(transported)
        field_contributions.append(transported_field)
        descriptor_contributions.append(transported_descriptor)
        stage_records[position]["after_complete_causal_transport"] = (
            _arb_norm_bounds(_array(transported))
        )
        stage_records[position][
            "after_complete_causal_transport_field_output_only"
        ] = _arb_norm_bounds(_array(transported_field))
        stage_records[position][
            "after_complete_causal_transport_descriptor_output_only"
        ] = _arb_norm_bounds(_array(transported_descriptor))
    obstruction = contributions[0] + contributions[1]
    obstruction_field = field_contributions[0] + field_contributions[1]
    obstruction_descriptor = (
        descriptor_contributions[0] + descriptor_contributions[1]
    )
    obstruction_vector = _array(obstruction).ravel()
    obstruction_field_vector = _array(obstruction_field).ravel()
    obstruction_descriptor_vector = _array(obstruction_descriptor).ravel()
    z2_lower = _arb_norm_lower(obstruction_vector)
    z2_direction_upper = _norm_upper(obstruction_vector)
    y_lower, y_upper, y_owner = _outward_y_bounds()
    discriminant_upper = math.nextafter(float(
        (_a(1) - 4 * _a(y_lower) * _a(z2_lower)).upper()
    ), math.inf)
    minimum_quadratic_lower = math.nextafter(float(
        (_a(y_lower) - 1 / (4 * _a(z2_lower))).lower()
    ), -math.inf)
    invalidated = discriminant_upper < 0.0 and minimum_quadratic_lower > 0.0

    with np.load(WORK / "z1_composition.npz") as source:
        z1_upper = math.nextafter(
            float(np.max(np.asarray(source["row_upper"], dtype=float))),
            math.inf,
        )

    stop_record = json.loads(FIRST_STOP.read_text(encoding="utf-8"))
    hit_left, hit_right = (
        float(value)
        for value in stop_record["terminal_bracket"]["action_interval"]
    )
    empty_state_jets = np.empty((states.shape[0], STATE, 0), dtype=float)
    empty_descriptor_jets = np.empty((states.shape[0], 0), dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        proper_pullback = assemble_cancelled_arc_proper_time_coefficient_first_jet(
            arc_nodes=times,
            states=states,
            state_action_first_jet=empty_state_jets,
            state_weights=weights,
            signed_descriptor=descriptors,
            signed_descriptor_first_jet=empty_descriptor_jets,
            cancelled_field_action_norm=np.asarray(
                source["cancelled_field_action_norm"], dtype=float,
            ),
            cancelled_norm_state_gradient_action=np.asarray(
                source["cancelled_norm_state_gradient_action"], dtype=float,
            ),
            cancelled_norm_descriptor_derivative=np.asarray(
                source["cancelled_norm_descriptor_derivative"], dtype=float,
            ),
        )
    proper_nodes = np.asarray(proper_pullback["proper_times"], dtype=float)
    proper_density = np.asarray(
        proper_pullback["proper_time_density"], dtype=float,
    )

    def proper_time_at(action_coordinate: float) -> float:
        interval = int(np.searchsorted(times, action_coordinate) - 1)
        if interval < 0:
            return 0.0
        width = float(times[interval + 1] - times[interval])
        offset = float(action_coordinate - times[interval])
        density = float(
            proper_density[interval]
            + offset / width
            * (proper_density[interval + 1] - proper_density[interval])
        )
        return float(
            proper_nodes[interval]
            + 0.5 * offset * (proper_density[interval] + density)
        )

    witness_action = float(times[node])
    witness_proper = float(proper_nodes[node])
    hit_proper_left = proper_time_at(hit_left)
    hit_proper_right = proper_time_at(hit_right)
    maximum_HS_upper = max(
        float(record["HS_complete_residual_second"]["upper"])
        for record in stage_records
    )
    maximum_preconditioned_upper = max(
        float(record["after_frozen_preconditioner"]["upper"])
        for record in stage_records
    )
    maximum_transported_upper = max(
        float(record["after_complete_causal_transport"]["upper"])
        for record in stage_records
    )

    def radii_small_root(z2: float) -> tuple[float, float]:
        discriminant = (1.0 - z1_upper) ** 2 - 4.0 * y_upper * z2
        if discriminant < 0.0:
            return discriminant, math.nan
        root = (
            (1.0 - z1_upper) - math.sqrt(discriminant)
        ) / (2.0 * z2)
        return discriminant, root

    HS_discriminant, HS_small_root = radii_small_root(maximum_HS_upper)
    preconditioned_discriminant, preconditioned_small_root = radii_small_root(
        maximum_preconditioned_upper
    )
    first_stage = stage_records[0]
    descriptor_test_factor = (
        float(first_stage["after_test_frame_descriptor_output_only"]["lower"])
        / float(first_stage["HS_descriptor_output_only"]["upper"])
    )
    descriptor_preconditioner_factor = (
        float(first_stage[
            "after_frozen_preconditioner_descriptor_output_only"
        ]["lower"])
        / float(first_stage["after_test_frame_descriptor_output_only"]["upper"])
    )
    descriptor_transport_factor = (
        float(first_stage[
            "after_complete_causal_transport_descriptor_output_only"
        ]["lower"])
        / float(first_stage[
            "after_frozen_preconditioner_descriptor_output_only"
        ]["upper"])
    )
    required_radius_floor = y_upper / (1.0 - z1_upper)
    domain_radius_ceiling = float(descriptors[-1] / TRIAL_DESCRIPTOR_SCALE)
    provenance_paths = (
        Path(__file__).resolve(),
        ENDPOINT, ENDPOINT.with_suffix(".npz"),
        REPLAY, REPLAY.with_suffix(".npz"),
        OLD_JACOBIAN, OLD_JACOBIAN.with_suffix(".npz"),
        PRECONDITIONER, PRECONDITIONER.with_suffix(".npz"),
        FIRST_STOP, KRAWCZYK_THEOREM, CONTINUUM_CHILD,
    )
    validation = {
        "same_frozen_accepted_replay_center": True,
        "same_causal_74D_frame": True,
        "same_retained_exact_field_normalization": True,
        "same_branch_24_without_binary_reselection": True,
        "same_frozen_preconditioner": True,
        "signed_D3_D4_D5_action_contractions_evaluated_in_Arb": True,
        "endpoint_and_two_adjacent_midpoint_second_identities_included": True,
        "both_adjacent_local_residual_blocks_composed_before_norm": True,
        "complete_frozen_causal_transport_to_terminal_node_composed_before_norm": True,
        "necessary_quadratic_discriminant_strictly_negative": invalidated,
        "witness_strictly_precedes_certified_first_hit_bracket": (
            witness_action < hit_left
        ),
        "local_HS_and_preconditioned_small_roots_fit_frozen_domain": (
            required_radius_floor < HS_small_root < domain_radius_ceiling
            and required_radius_floor < preconditioned_small_root
            < domain_radius_ceiling
        ),
        "field_descriptor_output_split_recombines_exactly": all(
            (obstruction_field_vector[i] + obstruction_descriptor_vector[i]
             - obstruction_vector[i]).contains(0)
            for i in range(obstruction_vector.size)
        ),
        "current_theorem_ends_at_first_hit_not_post_child_persistence": True,
        "existing_child_persistence_certificate_is_separate": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION",
        "status": (
            "SAME_CENTER_GATE7_Z2_PROOF_COORDINATE_AMPLIFICATION_ADJUDICATED"
            if invalidated else
            "ACCEPTED_REPLAY_CENTER_DIRECTIONAL_OBSTRUCTION_INCONCLUSIVE"
        ),
        "owner": "SAME_CENTER_GATE7_Z2_PHYSICAL_LOCALIZATION_AND_ADJUDICATION",
        "theorem_convention": {
            "self_map": "Y+Z1*r+Z2*r^2<r",
            "contraction": "Z1+2*Z2*r<1",
        },
        "outward_operands": {
            "Y_lower": y_lower,
            "Y_upper": y_upper,
            "Y_owner_node": y_owner,
            "Z1_upper": z1_upper,
            "required_radius_floor": required_radius_floor,
            "frozen_domain_radius_ceiling": domain_radius_ceiling,
            "Z2_required_lower_from_center_direction": z2_lower,
            "Z2_same_direction_upper": z2_direction_upper,
            "Z2_obstruction_node": node,
            "Z2_obstruction_causal_coordinate": direction_index,
            "necessary_discriminant_upper_1_minus_4_Ylower_Z2lower": (
                discriminant_upper
            ),
            "necessary_quadratic_global_minimum_lower": (
                minimum_quadratic_lower
            ),
        },
        "Z2_WITNESS_LOCATION": {
            "owning_block_intervals": list(local_intervals),
            "owning_node": node,
            "owning_midpoint_action_coordinates": [
                float(0.5 * (times[index] + times[index + 1]))
                for index in local_intervals
            ],
            "witness_action_arc_coordinate": witness_action,
            "witness_proper_time_coordinate_numerical": witness_proper,
            "certified_first_hit_action_arc_bracket": [hit_left, hit_right],
            "first_hit_proper_time_bracket_numerical": [
                hit_proper_left, hit_proper_right,
            ],
            "signed_action_separation_witness_minus_first_hit": [
                witness_action - hit_right, witness_action - hit_left,
            ],
            "signed_proper_time_separation_witness_minus_first_hit_numerical": [
                witness_proper - hit_proper_right,
                witness_proper - hit_proper_left,
            ],
            "classification": "PRE_ENVELOPMENT",
            "proper_time_values_are_existing_binary64_pullback_not_interval_authority": True,
        },
        "amplification_decomposition": {
            "actual_operator_order": (
                "LOCAL_RATE_D2_TO_HERMITE_SIMPSON_RESIDUAL_TO_TEST_FRAME_"
                "TO_FROZEN_PRECONDITIONER_TO_COMPLETE_CAUSAL_TRANSPORT_"
                "TO_TERMINAL_CAUSAL_NORM"
            ),
            "trial_descriptor_scale": TRIAL_DESCRIPTOR_SCALE,
            "test_descriptor_scale": TEST_DESCRIPTOR_SCALE,
            "input_direction_action_coordinate": direction_index,
            "input_direction_field_part_norm": float(np.linalg.norm(
                np.asarray([float(value) for value in direction[:STATE]])
            )),
            "input_direction_descriptor_component": float(direction[STATE]),
            "local_interval_stages": stage_records,
            "terminal_total": _arb_norm_bounds(obstruction_vector),
            "terminal_field_output_only": _arb_norm_bounds(
                obstruction_field_vector
            ),
            "terminal_descriptor_output_only": _arb_norm_bounds(
                obstruction_descriptor_vector
            ),
            "maximum_local_HS_curvature_upper": maximum_HS_upper,
            "maximum_local_preconditioned_curvature_upper": (
                maximum_preconditioned_upper
            ),
            "maximum_single_block_transported_curvature_upper": (
                maximum_transported_upper
            ),
            "local_HS_radii_discriminant": HS_discriminant,
            "local_HS_small_root": HS_small_root,
            "local_preconditioned_radii_discriminant": (
                preconditioned_discriminant
            ),
            "local_preconditioned_small_root": preconditioned_small_root,
            "descriptor_test_scaling_amplification_lower": (
                descriptor_test_factor
            ),
            "descriptor_preconditioner_amplification_lower": (
                descriptor_preconditioner_factor
            ),
            "descriptor_causal_transport_amplification_lower": (
                descriptor_transport_factor
            ),
            "terminal_over_maximum_local_HS_amplification_lower": (
                z2_lower / maximum_HS_upper
            ),
            "dominant_amplification_classification": (
                "DESCRIPTOR_SCALING_DOMINANT_WITH_DECISIVE_CAUSAL_TRANSPORT"
            ),
            "field_plus_descriptor_identity_verified": all(
                (obstruction_field_vector[i] + obstruction_descriptor_vector[i]
                 - obstruction_vector[i]).contains(0)
                for i in range(obstruction_vector.size)
            ),
        },
        "physical_interpretation": {
            "Z2_is_physical_spacetime_curvature": False,
            "Z2_definition": (
                "CURVATURE_LIPSCHITZ_QUANTITY_OF_THE_NONLINEAR_GATE7_"
                "RESIDUAL_IN_THE_FROZEN_REDUCED_CAUSAL_PROOF_COORDINATES"
            ),
            "raw_local_output_owner": "REDUCED_EULER_DIRAC_FIELD_RESPONSE",
            "raw_configuration_rate_curvature_upper": float(
                first_stage["raw_endpoint_configuration_rate_second"]["upper"]
            ),
            "raw_reduced_field_rate_curvature_upper": float(
                first_stage["raw_endpoint_reduced_field_rate_second"]["upper"]
            ),
            "raw_descriptor_rate_curvature_upper": float(
                first_stage["raw_endpoint_descriptor_rate_second"]["upper"]
            ),
            "lapse_shift_radius_anisotropy_constraint_terms": (
                "ACTION_COUPLED_IN_THE_SIGNED_D3_D4_D5_BORDERED_RESPONSE;_"
                "THE_CURRENT_EXACT_IDENTITY_DOES_NOT_DEFINE_AN_INVARIANT_"
                "ADDITIVE_SPLIT_OF_THESE_MIXED_TERMS"
            ),
            "input_direction_has_zero_independent_descriptor_component": True,
            "large_terminal_descriptor_channel_is_generated_by_field_"
            "CURVATURE_THEN_PROOF_SCALED": True,
        },
        "formation_corridor_adjudication": {
            "required_parent_domain": (
                "CERTIFIED_RESET_RELATION_THROUGH_CANONICAL_EARLIEST_STOP"
            ),
            "witness_is_inside_required_parent_domain": True,
            "shorter_start_to_first_hit_corridor_can_exclude_witness": False,
            "diagnostic_classification": (
                "FORMATION_CORRIDOR_NONLINEAR_OBSTRUCTION_CANDIDATE"
            ),
            "current_theorem_overextends_post_hit_child_dynamics": False,
            "theorem_scope": "A_ROOT_SOLUTION_ONLY_THROUGH_FIRST_HIT",
            "theorem_text_source": (
                "theory/n12_c2_stop_correlated_defect_krawczyk.md"
            ),
        },
        "child_persistence_separation": {
            "separately_owned_in_BHSM": True,
            "existing_N12_continuum_child_persistence_certificate": (
                "artifacts/n12_continuum_majorant_effectiveness/"
                "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
            ),
            "positive_duration_persistence_certified_there": True,
            "transferred_by_parent_Gate7_Z2": False,
            "eternal_stability_claim": False,
        },
        "decision": {
            "classification": (
                "PROOF_COORDINATE_CURVATURE_AMPLIFICATION"
                if invalidated else "INCONCLUSIVE"
            ),
            "reason": (
                "THE_RAW_LOCAL_DIRECTIONAL_CURVATURE_DOES_NOT_BY_ITSELF_"
                "EXCLUDE_A_RADIUS,_BUT_THE_FROZEN_TEST_PRECONDITIONER_AND_"
                "CAUSAL_PROOF_COORDINATES_AMPLIFY_IT_UNTIL_THE_NECESSARY_"
                "RADII_DISCRIMINANT_IS_STRICTLY_NEGATIVE"
                if invalidated else
                "THE_SINGLE_DIRECTION_DOES_NOT_EXCLUDE_EVERY_RADIUS"
            ),
            "current_same_center_contraction_theorem_obstructed": invalidated,
            "physical_spacetime_instability_claim": False,
            "root_nonexistence_claim": False,
            "another_center_or_trajectory_authorized": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "provenance_SHA256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in provenance_paths
        },
        "derived_work_aggregate_SHA256": {
            "371_outward_endpoint_rate_and_DF_shards": _aggregate_sha256([
                WORK / f"endpoint_{index:03d}.npz" for index in range(371)
            ]),
            "370_outward_midpoint_rate_and_DF_shards": _aggregate_sha256([
                WORK / f"midpoint_{index:03d}.npz" for index in range(370)
            ]),
            "370_outward_linear_preconditioned_shards": _aggregate_sha256([
                WORK / f"linear_{index:03d}.npz" for index in range(370)
            ]),
            "outward_Z1_composition": _sha256(WORK / "z1_composition.npz"),
        },
        "FULL_BHSM_COMPLETE": False,
    }
    np.savez_compressed(
        DATA,
        terminal_directional_curvature_mid=np.asarray([
            float(value) for value in obstruction_vector
        ]),
        terminal_directional_curvature_radius=np.asarray([
            _center_radius(value)[1] for value in obstruction_vector
        ]),
        terminal_field_output_directional_curvature_mid=np.asarray([
            float(value) for value in obstruction_field_vector
        ]),
        terminal_field_output_directional_curvature_radius=np.asarray([
            _center_radius(value)[1] for value in obstruction_field_vector
        ]),
        terminal_descriptor_output_directional_curvature_mid=np.asarray([
            float(value) for value in obstruction_descriptor_vector
        ]),
        terminal_descriptor_output_directional_curvature_radius=np.asarray([
            _center_radius(value)[1] for value in obstruction_descriptor_vector
        ]),
        local_interval_indices=np.asarray(local_intervals, dtype=int),
        obstruction_node=np.asarray(node),
        obstruction_causal_coordinate=np.asarray(direction_index),
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


def _worker(index: int, stage: str) -> tuple[int, str]:
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / f"{stage}_{index:03d}.npz"
    if target.exists():
        try:
            with np.load(target) as existing:
                if (
                    "derivative_arb" in existing.files
                    and int(existing["precision_bits"]) == PRECISION
                    and "shard_revision" in existing.files
                    and int(existing["shard_revision"]) == SHARD_REVISION
                ):
                    return index, "reused"
        except Exception:
            pass
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        endpoint_states = np.asarray(source["projected_states"], dtype=float)
        endpoint_descriptors = np.asarray(source["independent_signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    if stage == "endpoint":
        directions = _frame(tangents[index], TRIAL_DESCRIPTOR_SCALE)
        enclosed = _rate_enclosure(
            endpoint_states[index], float(endpoint_descriptors[index]),
            weights, reference, directions,
        )
    elif stage == "midpoint":
        with np.load(REPLAY.with_suffix(".npz")) as source:
            augmented = np.asarray(source["midpoint_augmented_action_values"][index], dtype=float)
        left = np.load(WORK / f"endpoint_{index:03d}.npz")
        right = np.load(WORK / f"endpoint_{index + 1:03d}.npz")
        h = _a(float(times[index + 1] - times[index]))
        left_frame = _frame(tangents[index], TRIAL_DESCRIPTOR_SCALE)
        right_frame = _frame(tangents[index + 1], TRIAL_DESCRIPTOR_SCALE)
        left_derivative = _parse_arb_string_array(left["derivative_arb"])
        right_derivative = _parse_arb_string_array(right["derivative_arb"])
        direction_ball = np.empty((99, 148), dtype=object)
        for i in range(99):
            for k in range(74):
                direction_ball[i, k] = (
                    _a(0.5 * left_frame[i, k]) + h * left_derivative[i, k] / 8
                )
                direction_ball[i, 74 + k] = (
                    _a(0.5 * right_frame[i, k]) - h * right_derivative[i, k] / 8
                )
        # Two 74-column correlated evaluations are materially faster and use
        # less peak memory than one 148-column broadcast, while preserving
        # each left/right block correlation through the final projection.
        left_enclosed = _rate_enclosure(
            augmented[:98] / weights, float(augmented[98]), weights,
            reference, direction_ball[:, :74],
        )
        right_enclosed = _rate_enclosure(
            augmented[:98] / weights, float(augmented[98]), weights,
            reference, direction_ball[:, 74:],
        )
        enclosed = RateEnclosure(
            left_enclosed.value,
            np.column_stack((left_enclosed.derivative, right_enclosed.derivative)),
            min(left_enclosed.gap_lower, right_enclosed.gap_lower),
            max(left_enclosed.eigen_residual_upper, right_enclosed.eigen_residual_upper),
            left_enclosed.action_jets,
        )
    else:
        raise ValueError(stage)
    value_mid, value_rad = _export(enclosed.value)
    derivative_mid, derivative_rad = _export(enclosed.derivative)
    np.savez_compressed(
        target, value_mid=value_mid, value_rad=value_rad,
        derivative_mid=derivative_mid, derivative_rad=derivative_rad,
        value_arb=_arb_string_array(enclosed.value),
        derivative_arb=_arb_string_array(enclosed.derivative),
        precision_bits=np.asarray(PRECISION),
        shard_revision=np.asarray(SHARD_REVISION),
        gap_lower=enclosed.gap_lower,
        eigen_residual_upper=enclosed.eigen_residual_upper,
    )
    return index, "computed"


def _arb_row_norm_upper(values: np.ndarray) -> np.ndarray:
    """Euclidean row-norm upper bounds for an Arb matrix."""
    array = np.asarray(values, dtype=object)
    result = np.empty(array.shape[0], dtype=float)
    for i in range(array.shape[0]):
        total = arb(0)
        for j in range(array.shape[1]):
            total += array[i, j] ** 2
        result[i] = math.nextafter(float(total.sqrt().upper()), math.inf)
    return result


def _tube_target(stage: str, index: int) -> Path:
    return WORK / f"tube_{stage}_{index:03d}.npz"


def _tube_worker(index: int, stage: str, radius: float) -> tuple[int, str]:
    """Enclose the exact Jacobian over one causal block-sup radius."""
    ctx.prec = PRECISION
    WORK.mkdir(parents=True, exist_ok=True)
    target = _tube_target(stage, index)
    if target.exists():
        try:
            with np.load(target) as existing:
                if (
                    "derivative_arb" in existing.files
                    and int(existing["precision_bits"]) == PRECISION
                    and int(existing["tube_shard_revision"]) == TUBE_SHARD_REVISION
                    and float(existing["domain_radius"]) == float(radius)
                ):
                    return index, "reused"
        except Exception:
            pass
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        endpoint_states = np.asarray(source["projected_states"], dtype=float)
        endpoint_descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)

    if stage == "endpoint":
        frame = _frame(tangents[index], TRIAL_DESCRIPTOR_SCALE)
        raw_frame = frame[:STATE] / weights[:, None]
        state_radius = np.nextafter(
            float(radius) * np.linalg.norm(raw_frame, axis=1), math.inf,
        )
        state_ball = np.asarray([
            arb(float(endpoint_states[index, i]), float(state_radius[i]))
            for i in range(STATE)
        ], dtype=object)
        descriptor_radius = math.nextafter(
            float(radius) * TRIAL_DESCRIPTOR_SCALE, math.inf,
        )
        descriptor_ball = arb(
            float(endpoint_descriptors[index]), descriptor_radius,
        )
        enclosed = _rate_enclosure(
            state_ball, descriptor_ball, weights, reference, frame,
        )
        maximum_state_radius = float(np.max(state_radius))
    elif stage == "midpoint":
        with np.load(REPLAY.with_suffix(".npz")) as source:
            augmented = np.asarray(
                source["midpoint_augmented_action_values"][index], dtype=float,
            )
        with np.load(_tube_target("endpoint", index)) as source:
            left_derivative = _parse_arb_string_array(source["derivative_arb"])
        with np.load(_tube_target("endpoint", index + 1)) as source:
            right_derivative = _parse_arb_string_array(source["derivative_arb"])
        h = _a(float(times[index + 1] - times[index]))
        left_frame = _frame(tangents[index], TRIAL_DESCRIPTOR_SCALE)
        right_frame = _frame(tangents[index + 1], TRIAL_DESCRIPTOR_SCALE)
        left_direction = np.empty((STATE + 1, 74), dtype=object)
        right_direction = np.empty_like(left_direction)
        for i in range(STATE + 1):
            for k in range(74):
                left_direction[i, k] = (
                    _a(0.5 * left_frame[i, k])
                    + h * left_derivative[i, k] / 8
                )
                right_direction[i, k] = (
                    _a(0.5 * right_frame[i, k])
                    - h * right_derivative[i, k] / 8
                )
        augmented_radius = np.nextafter(
            float(radius) * (
                _arb_row_norm_upper(left_direction)
                + _arb_row_norm_upper(right_direction)
            ),
            math.inf,
        )
        state_ball = np.asarray([
            arb(
                float(augmented[i] / weights[i]),
                float(augmented_radius[i] / weights[i]),
            )
            for i in range(STATE)
        ], dtype=object)
        descriptor_ball = arb(
            float(augmented[STATE]), float(augmented_radius[STATE]),
        )
        left_enclosed = _rate_enclosure(
            state_ball, descriptor_ball, weights, reference, left_direction,
        )
        right_enclosed = _rate_enclosure(
            state_ball, descriptor_ball, weights, reference, right_direction,
        )
        enclosed = RateEnclosure(
            left_enclosed.value,
            np.column_stack((left_enclosed.derivative, right_enclosed.derivative)),
            min(left_enclosed.gap_lower, right_enclosed.gap_lower),
            max(
                left_enclosed.eigen_residual_upper,
                right_enclosed.eigen_residual_upper,
            ),
            left_enclosed.action_jets,
        )
        maximum_state_radius = float(np.max(augmented_radius[:STATE] / weights))
    else:
        raise ValueError(stage)

    descriptor_lower = float(descriptor_ball.lower())
    np.savez_compressed(
        target,
        derivative_arb=_arb_string_array(enclosed.derivative),
        precision_bits=np.asarray(PRECISION),
        tube_shard_revision=np.asarray(TUBE_SHARD_REVISION),
        domain_radius=np.asarray(radius),
        gap_lower=np.asarray(enclosed.gap_lower),
        eigen_residual_upper=np.asarray(enclosed.eigen_residual_upper),
        descriptor_lower=np.asarray(descriptor_lower),
        maximum_state_radius=np.asarray(maximum_state_radius),
    )
    return index, "computed"


def _run_tube_stage(stage: str, workers: int, radius: float) -> None:
    if not (radius > 0.0 and math.isfinite(radius)):
        raise ValueError("positive finite tube radius required")
    total = 371 if stage == "endpoint" else 370
    if stage == "midpoint":
        missing = [
            str(_tube_target("endpoint", index)) for index in range(371)
            if not _tube_target("endpoint", index).exists()
        ]
        if missing:
            raise RuntimeError(f"missing {len(missing)} endpoint tube shards")
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_tube_worker, index, stage, radius)
            for index in range(total)
        ]
        for count, future in enumerate(futures, 1):
            index, disposition = future.result()
            if count % 8 == 0 or count == total:
                print(json.dumps({
                    "tube_stage": stage,
                    "completed": count,
                    "total": total,
                    "index": index,
                    "disposition": disposition,
                    "domain_radius": radius,
                }), flush=True)


def _run_stage(stage: str, workers: int) -> None:
    total = 371 if stage == "endpoint" else 370
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_worker, index, stage) for index in range(total)]
        for count, future in enumerate(futures, 1):
            index, disposition = future.result()
            if count % 8 == 0 or count == total:
                print(json.dumps({
                    "stage": stage, "completed": count, "total": total,
                    "index": index, "disposition": disposition,
                }), flush=True)


def _probe(index: int) -> None:
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        state = np.asarray(source["projected_states"][index], dtype=float)
        descriptor = float(source["independent_signed_descriptors"][index])
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(OLD_JACOBIAN.with_suffix(".npz")) as source:
        tangent = np.asarray(source["endpoint_physical_tangent_action"][index], dtype=float)
    direction = np.zeros((99, 74)); direction[:98, :73] = tangent
    direction[98, 73] = TRIAL_DESCRIPTOR_SCALE
    ctx.prec = PRECISION
    result = _rate_enclosure(state, descriptor, weights, reference, direction)
    print(json.dumps({
        "node": index,
        "rate_shape": list(result.value.shape),
        "derivative_shape": list(result.derivative.shape),
        "maximum_rate_radius": max(float(abs(x - arb(float(x))).upper()) for x in result.value),
        "maximum_derivative_radius": max(float(abs(x - arb(float(x))).upper()) for x in result.derivative.ravel()),
        "gap_lower": result.gap_lower,
        "eigen_residual_upper": result.eigen_residual_upper,
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", type=int)
    parser.add_argument("--stage", choices=("endpoint", "midpoint"))
    parser.add_argument("--tube-stage", choices=("endpoint", "midpoint"))
    parser.add_argument("--compose-linear", action="store_true")
    parser.add_argument("--compose-z1", action="store_true")
    parser.add_argument("--compose-z2", action="store_true")
    parser.add_argument("--curvature-obstruction", action="store_true")
    parser.add_argument("--radius", type=float)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.probe is not None:
        _probe(args.probe)
        return
    if args.stage is not None:
        _run_stage(args.stage, args.workers)
        return
    if args.tube_stage is not None:
        if args.radius is None:
            raise RuntimeError("--tube-stage requires --radius")
        _run_tube_stage(args.tube_stage, args.workers, args.radius)
        return
    if args.compose_linear:
        _linear_composition()
        return
    if args.compose_z1:
        _compose_z1()
        return
    if args.compose_z2:
        if args.radius is None:
            raise RuntimeError("--compose-z2 requires --radius")
        _compose_z2(args.radius)
        return
    if args.curvature_obstruction:
        _accepted_center_curvature_obstruction()
        return
    raise RuntimeError("full accepted-center composition is not yet materialized")


if __name__ == "__main__":
    main()
