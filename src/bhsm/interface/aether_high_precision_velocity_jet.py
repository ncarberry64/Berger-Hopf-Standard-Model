"""High-precision retained-action blocks for the canonical momentum.

The velocity gradient and the full velocity/multiplier Hessian are evaluated
with Decimal arithmetic.  This avoids amplifying binary64 action-Hessian
roundoff through the ill-conditioned canonical lift and the nearly-null
ordered-event eigenline.  The retained action and both physical definitions
are unchanged.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, localcontext
from functools import lru_cache

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


def _d(value: float) -> Decimal:
    return Decimal.from_float(float(value))


@dataclass
class _Jet:
    value: Decimal
    gradient: list[Decimal]
    hessian: list[list[Decimal]]

    @classmethod
    def constant(cls, value: Decimal | float, size: int) -> "_Jet":
        scalar = value if isinstance(value, Decimal) else _d(value)
        return cls(
            scalar,
            [Decimal(0) for _ in range(size)],
            [[Decimal(0) for _ in range(size)] for _ in range(size)],
        )

    @classmethod
    def variable(cls, value: Decimal, index: int, size: int) -> "_Jet":
        result = cls.constant(value, size)
        result.gradient[index] = Decimal(1)
        return result

    def _coerce(self, other: Decimal | float | "_Jet") -> "_Jet":
        return other if isinstance(other, _Jet) else self.constant(other, len(self.gradient))

    def __add__(self, other: Decimal | float | "_Jet") -> "_Jet":
        other = self._coerce(other)
        size = len(self.gradient)
        return _Jet(
            self.value + other.value,
            [self.gradient[i] + other.gradient[i] for i in range(size)],
            [[self.hessian[i][j] + other.hessian[i][j]
              for j in range(size)] for i in range(size)],
        )

    __radd__ = __add__

    def __neg__(self) -> "_Jet":
        return _Jet(
            -self.value,
            [-value for value in self.gradient],
            [[-value for value in row] for row in self.hessian],
        )

    def __sub__(self, other: Decimal | float | "_Jet") -> "_Jet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Decimal | float | "_Jet") -> "_Jet":
        return self._coerce(other) - self

    def __mul__(self, other: Decimal | float | "_Jet") -> "_Jet":
        other = self._coerce(other)
        size = len(self.gradient)
        gradient = [
            self.gradient[i] * other.value
            + other.gradient[i] * self.value
            for i in range(size)
        ]
        hessian = [[
            self.hessian[i][j] * other.value
            + other.hessian[i][j] * self.value
            + self.gradient[i] * other.gradient[j]
            + other.gradient[i] * self.gradient[j]
            for j in range(size)
        ] for i in range(size)]
        return _Jet(self.value * other.value, gradient, hessian)

    __rmul__ = __mul__

    def reciprocal(self) -> "_Jet":
        size = len(self.gradient)
        value2 = self.value * self.value
        value3 = value2 * self.value
        return _Jet(
            Decimal(1) / self.value,
            [-item / value2 for item in self.gradient],
            [[
                Decimal(2) * self.gradient[i] * self.gradient[j] / value3
                - self.hessian[i][j] / value2
                for j in range(size)
            ] for i in range(size)],
        )

    def __truediv__(self, other: Decimal | float | "_Jet") -> "_Jet":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: Decimal | float | "_Jet") -> "_Jet":
        return self._coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "_Jet":
        if not isinstance(exponent, int):
            raise TypeError("integer powers only")
        if exponent < 0:
            return (self ** (-exponent)).reciprocal()
        result = self.constant(1.0, len(self.gradient))
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "_Jet":
        value = self.value.exp()
        size = len(self.gradient)
        return _Jet(
            value,
            [value * item for item in self.gradient],
            [[value * (
                self.hessian[i][j]
                + self.gradient[i] * self.gradient[j]
            ) for j in range(size)] for i in range(size)],
        )


@lru_cache(maxsize=None)
def _basis(order: int, points: int) -> dict[str, np.ndarray]:
    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    return {
        "chi": chi,
        "quadrature": quadrature,
        "ks": ks,
        "js": js,
        "cos_k": np.cos(4.0 * np.outer(ks, chi)),
        "sin_k": np.sin(4.0 * np.outer(ks, chi)),
        "cos_j": np.cos(4.0 * np.outer(js, chi)),
        "sin_j": np.sin(4.0 * np.outer(js, chi)),
    }


def _dot(values: list[Decimal], coefficients: np.ndarray) -> Decimal:
    return sum(value * _d(coefficient)
               for value, coefficient in zip(values, coefficients))


def _nonzero(values: np.ndarray) -> list[tuple[int, Decimal]]:
    return [(index, _d(value)) for index, value in enumerate(values) if value != 0.0]


def _zero_vector(size: int) -> list[Decimal]:
    return [Decimal(0) for _ in range(size)]


def _zero_matrix(rows: int, columns: int) -> list[list[Decimal]]:
    return [[Decimal(0) for _ in range(columns)] for _ in range(rows)]


def _accumulate_local(
    local: _Jet,
    velocity_maps: list[list[tuple[int, Decimal]]],
    multiplier_maps: list[list[tuple[int, Decimal]]],
    gradient_v: list[Decimal],
    gradient_m: list[Decimal],
    hessian_vv: list[list[Decimal]],
    hessian_mv: list[list[Decimal]],
    hessian_mm: list[list[Decimal]],
) -> None:
    for local_index, mapping in enumerate(velocity_maps):
        coefficient = local.gradient[local_index]
        for index, value in mapping:
            gradient_v[index] += coefficient * value
    for local_index, mapping in enumerate(multiplier_maps, start=3):
        coefficient = local.gradient[local_index]
        for index, value in mapping:
            gradient_m[index] += coefficient * value
    for a, left in enumerate(velocity_maps):
        for b, right in enumerate(velocity_maps):
            coefficient = local.hessian[a][b]
            if coefficient == 0:
                continue
            for i, left_value in left:
                for j, right_value in right:
                    hessian_vv[i][j] += coefficient * left_value * right_value
    for a, left in enumerate(multiplier_maps, start=3):
        for b, right in enumerate(velocity_maps):
            coefficient = local.hessian[a][b]
            if coefficient == 0:
                continue
            for i, left_value in left:
                for j, right_value in right:
                    hessian_mv[i][j] += coefficient * left_value * right_value
    for a, left in enumerate(multiplier_maps, start=3):
        for b, right in enumerate(multiplier_maps, start=3):
            coefficient = local.hessian[a][b]
            if coefficient == 0:
                continue
            for i, left_value in left:
                for j, right_value in right:
                    hessian_mm[i][j] += coefficient * left_value * right_value


def high_precision_velocity_jet_blocks(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
    precision: int = 50,
) -> dict[str, object]:
    """Return Decimal L_v and the full (v,m) retained-action Hessian."""

    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    q_raw = np.asarray(coordinates, dtype=float)
    v_raw = np.asarray(velocities, dtype=float)
    m_raw = np.asarray(multipliers, dtype=float)
    if q_raw.shape != (qdim,) or v_raw.shape != (qdim,) or m_raw.shape != (mdim,):
        raise ValueError("state dimensions do not match order")
    basis = _basis(order, points)
    with localcontext() as context:
        context.prec = precision
        q = [_d(value) for value in q_raw]
        velocity = [_d(value) for value in v_raw]
        multipliers_d = [_d(value) for value in m_raw]
        radius = _d(RADIUS0) * q[0].exp()
        kappa0 = _d(15.0 * 5.0 ** (1.0 / 3.0) / 4.0)

        bulk_value = Decimal(0)
        inertia_value = Decimal(0)
        bulk_gv = _zero_vector(qdim)
        bulk_gm = _zero_vector(mdim)
        bulk_hvv = _zero_matrix(qdim, qdim)
        bulk_hmv = _zero_matrix(mdim, qdim)
        bulk_hmm = _zero_matrix(mdim, mdim)
        inertia_gv = _zero_vector(qdim)
        inertia_gm = _zero_vector(mdim)
        inertia_hvv = _zero_matrix(qdim, qdim)
        inertia_hmv = _zero_matrix(mdim, qdim)
        inertia_hmm = _zero_matrix(mdim, mdim)

        u_coeff = q[1:1 + order]
        w_coeff = q[1 + order:1 + 2 * order]
        b_coeff = q[1 + 2 * order:1 + 3 * order]
        for node, coordinate in enumerate(basis["chi"]):
            cos_k = basis["cos_k"][:, node]
            sin_k = basis["sin_k"][:, node]
            cos_j = basis["cos_j"][:, node]
            sin_j = basis["sin_j"][:, node]
            ks = basis["ks"]
            js = basis["js"]
            window_f = math.sin(2.0 * coordinate) ** 2
            window_prime_f = 2.0 * math.sin(4.0 * coordinate)
            window = _d(window_f)
            u = _dot(u_coeff, cos_k)
            up = _dot(u_coeff, -4.0 * ks * sin_k)
            w = window * _dot(w_coeff, cos_j)
            b = window * _dot(b_coeff, cos_j)
            wp = _dot(
                w_coeff,
                window_prime_f * cos_j
                + window_f * (-4.0 * js * sin_j),
            )
            bp_shape = _dot(
                b_coeff,
                window_prime_f * cos_j
                + window_f * (-4.0 * js * sin_j),
            )
            cos_chi = _d(math.cos(coordinate))
            sin_chi = _d(math.sin(coordinate))
            tan_chi = _d(math.tan(coordinate))
            c_radius = radius * (u + w).exp()
            a_radius = radius * (u + b).exp() * cos_chi
            b_radius = radius * (u - b).exp() * sin_chi
            cp = up + wp
            ap = up + bp_shape - tan_chi
            bp = up - bp_shape + Decimal(1) / tan_chi
            volume = c_radius * a_radius**3 * b_radius**3
            spatial_volume = a_radius**3 * b_radius**3

            lc = np.zeros(qdim)
            la = np.zeros(qdim)
            lb = np.zeros(qdim)
            lc[0] = la[0] = lb[0] = 1.0
            lc[1:1 + order] = cos_k
            la[1:1 + order] = cos_k
            lb[1:1 + order] = cos_k
            lc[1 + order:1 + 2 * order] = window_f * cos_j
            la[1 + 2 * order:1 + 3 * order] = window_f * cos_j
            lb[1 + 2 * order:1 + 3 * order] = -window_f * cos_j
            log_n = np.zeros(mdim)
            n_prime = np.zeros(mdim)
            beta = np.zeros(mdim)
            beta_prime = np.zeros(mdim)
            log_n[:order] = cos_k
            n_prime[:order] = -4.0 * ks * sin_k
            beta[order:2 * order] = math.sin(4.0 * coordinate) * cos_j
            beta_prime[order:2 * order] = (
                4.0 * math.cos(4.0 * coordinate) * cos_j
                + math.sin(4.0 * coordinate) * (-4.0 * js * sin_j)
            )
            local_maps_v = [_nonzero(lc), _nonzero(la), _nonzero(lb)]
            local_maps_m = [
                _nonzero(log_n), _nonzero(n_prime),
                _nonzero(beta), _nonzero(beta_prime),
            ]
            values = [
                _dot(velocity, lc), _dot(velocity, la), _dot(velocity, lb),
                _dot(multipliers_d, log_n),
                _dot(multipliers_d, n_prime),
                _dot(multipliers_d, beta),
                _dot(multipliers_d, beta_prime),
            ]
            variables = [_Jet.variable(value, index, 7)
                         for index, value in enumerate(values)]
            lc_j, la_j, lb_j, log_n_j, n_prime_j, beta_j, beta_prime_j = variables
            lapse = log_n_j.exp()
            hc = (lc_j - beta_j * cp - beta_prime_j) / lapse
            ha = (la_j - beta_j * ap) / lapse
            hb = (lb_j - beta_j * bp) / lapse
            adm = (
                hc**2 + _d(3.0) * ha**2 + _d(3.0) * hb**2
                - (hc + _d(3.0) * ha + _d(3.0) * hb)**2
            )
            f_normal = -beta_j / lapse
            x_spatial = (
                Decimal(1) / c_radius**2
                + _d(3.0) * cos_chi**2 / a_radius**2
                + _d(3.0) * sin_chi**2 / b_radius**2
            )
            x_eta = x_spatial - f_normal**2
            eta = Decimal(1) + x_eta**3
            fixed_gravity = ap**2 + bp**2 + _d(3.0) * ap * bp
            spatial_gravity = (
                _d(3.0) * spatial_volume / c_radius * lapse
                * (n_prime_j * (ap + bp) + fixed_gravity)
            )
            sigma = (
                _d(-0.5) + _d(2.0 * coordinate / math.pi)
                - _d(math.sin(4.0 * coordinate) / (2.0 * math.pi))
            )
            localization = Decimal(1) - _d(4.0) * sigma**2
            algebraic = lapse * volume * (
                _d(3.0) / a_radius**2 + _d(3.0) / b_radius**2
                - _d(0.5) * kappa0
                - localization * (_d(0.5) * x_eta + _d(0.125) * x_eta**4)
                + _d(0.5) * adm
            )
            quadrature = _d(basis["quadrature"][node])
            local_bulk = quadrature * (spatial_gravity + algebraic)
            local_inertia = (
                quadrature * volume * localization * eta / lapse
            )
            bulk_value += local_bulk.value
            inertia_value += local_inertia.value
            _accumulate_local(
                local_bulk, local_maps_v, local_maps_m,
                bulk_gv, bulk_gm, bulk_hvv, bulk_hmv, bulk_hmm,
            )
            _accumulate_local(
                local_inertia, local_maps_v, local_maps_m,
                inertia_gv, inertia_gm, inertia_hvv, inertia_hmv,
                inertia_hmm,
            )

        coefficient = _d(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2))
        inertia2 = inertia_value**2
        inertia3 = inertia_value**3
        gradient_v = [
            bulk_gv[i] + coefficient * inertia_gv[i] / inertia2
            for i in range(qdim)
        ]
        hessian_vv = [[
            bulk_hvv[i][j] + coefficient * (
                inertia_hvv[i][j] / inertia2
                - _d(2.0) * inertia_gv[i] * inertia_gv[j] / inertia3
            )
            for j in range(qdim)
        ] for i in range(qdim)]
        hessian_mv = [[
            bulk_hmv[i][j] + coefficient * (
                inertia_hmv[i][j] / inertia2
                - _d(2.0) * inertia_gm[i] * inertia_gv[j] / inertia3
            )
            for j in range(qdim)
        ] for i in range(mdim)]
        hessian_mm = [[
            bulk_hmm[i][j] + coefficient * (
                inertia_hmm[i][j] / inertia2
                - _d(2.0) * inertia_gm[i] * inertia_gm[j] / inertia3
            )
            for j in range(mdim)
        ] for i in range(mdim)]
        gradient_m = [
            bulk_gm[i] + coefficient * inertia_gm[i] / inertia2
            for i in range(mdim)
        ]

        # The retained boundary Casimir is independent of velocity but does
        # contribute to the multiplier gradient and multiplier Hessian used by
        # the ordered-event operator.
        signs_k = [Decimal(-1) ** (index + 1) for index in range(order)]
        signs_j = [Decimal(-1) ** index for index in range(order)]
        u_boundary = sum(q[1 + index] * signs_k[index]
                         for index in range(order))
        b_boundary = sum(q[1 + 2 * order + index] * signs_j[index]
                         for index in range(order))
        a_boundary = radius * (u_boundary + b_boundary).exp() / _d(math.sqrt(2.0))
        b_boundary_radius = (
            radius * (u_boundary - b_boundary).exp() / _d(math.sqrt(2.0))
        )
        r4 = (
            a_boundary * b_boundary_radius
            / (a_boundary**2 + b_boundary_radius**2).sqrt()
        )
        boundary_log_n = sum(
            multipliers_d[index] * signs_k[index]
            for index in range(order)
        )
        boundary_factor = (
            -_d(standard_model_casimir_coefficient())
            * boundary_log_n.exp() / r4
        )
        action_value = bulk_value - coefficient / inertia_value + boundary_factor
        for i in range(order):
            gradient_m[i] += boundary_factor * signs_k[i]
            for j in range(order):
                hessian_mm[i][j] += (
                    boundary_factor * signs_k[i] * signs_k[j]
                )
        return {
            "gradient_velocity": gradient_v,
            "gradient_multiplier": gradient_m,
            "hessian_velocity_velocity": hessian_vv,
            "hessian_multiplier_velocity": hessian_mv,
            "hessian_multiplier_multiplier": hessian_mm,
            "action_value": action_value,
            "bulk_value": bulk_value,
            "inertia_value": inertia_value,
            "precision": precision,
        }


def _solve(
    matrix: list[list[Decimal]], right: list[list[Decimal]],
) -> list[list[Decimal]]:
    a = [row[:] for row in matrix]
    b = [row[:] for row in right]
    size = len(a)
    columns = len(b[0])
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(a[row][column]))
        if pivot != column:
            a[column], a[pivot] = a[pivot], a[column]
            b[column], b[pivot] = b[pivot], b[column]
        diagonal = a[column][column]
        if diagonal == 0:
            raise np.linalg.LinAlgError("singular high-precision lift system")
        for row in range(column + 1, size):
            factor = a[row][column] / diagonal
            if factor == 0:
                continue
            a[row][column] = Decimal(0)
            for inner in range(column + 1, size):
                a[row][inner] -= factor * a[column][inner]
            for rhs_column in range(columns):
                b[row][rhs_column] -= factor * b[column][rhs_column]
    result = _zero_matrix(size, columns)
    for row in range(size - 1, -1, -1):
        for rhs_column in range(columns):
            remainder = b[row][rhs_column] - sum(
                a[row][inner] * result[inner][rhs_column]
                for inner in range(row + 1, size)
            )
            result[row][rhs_column] = remainder / a[row][row]
    return result


def _matmul(
    left: list[list[Decimal]], right: list[list[Decimal]],
) -> list[list[Decimal]]:
    return [[
        sum(left[row][inner] * right[inner][column]
            for inner in range(len(right)))
        for column in range(len(right[0]))
    ] for row in range(len(left))]


def high_precision_canonical_momentum(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
    precision: int = 50,
) -> np.ndarray:
    """Evaluate the unchanged canonical momentum with a high-precision jet."""

    blocks = high_precision_velocity_jet_blocks(
        order, coordinates, velocities, multipliers,
        points=points, precision=precision,
    )
    return high_precision_canonical_momentum_from_blocks(
        order, coordinates, blocks, precision=precision,
    )


def high_precision_canonical_momentum_from_blocks(
    order: int,
    coordinates: np.ndarray,
    blocks: dict[str, object],
    *,
    precision: int = 50,
) -> np.ndarray:
    """Evaluate canonical momentum while reusing an exact sector jet."""

    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    with localcontext() as context:
        context.prec = precision
        form = blocks["hessian_velocity_velocity"]
        constraints = blocks["hessian_multiplier_velocity"]
        q = [_d(value) for value in np.asarray(coordinates, dtype=float)]
        signs_k = [Decimal(-1) ** (index + 1) for index in range(order)]
        signs_j = [Decimal(-1) ** index for index in range(order)]
        boundary_value = sum(
            q[1 + 2 * order + index] * signs_j[index]
            for index in range(order)
        )
        exponential = (_d(4.0) * boundary_value).exp()
        tanh_twice = (exponential - Decimal(1)) / (exponential + Decimal(1))
        first = _zero_vector(qdim)
        first[0] = Decimal(1)
        for index in range(order):
            first[1 + index] = signs_k[index]
            first[1 + 2 * order + index] = -tanh_twice * signs_j[index]
        second = [-value for value in first]
        second[0] += Decimal(1)
        combined = [first, second] + [row[:] for row in constraints]
        inverse_times = _solve(form, [list(column) for column in zip(*combined)])
        compliance = _matmul(combined, inverse_times)
        target = _zero_matrix(2 + mdim, 2)
        target[0][0] = Decimal(1)
        target[1][1] = Decimal(1)
        compliance_solution = _solve(compliance, target)
        lift = _matmul(inverse_times, compliance_solution)
        gradient = blocks["gradient_velocity"]
        momentum = [
            sum(lift[row][column] * gradient[row] for row in range(qdim))
            for column in range(2)
        ]
    return np.asarray([float(value) for value in momentum])


def high_precision_ordered_eigenpair_from_blocks(
    blocks: dict[str, object],
    reference: np.ndarray,
    *,
    precision: int = 50,
) -> dict[str, object]:
    """Evaluate the selected ordered eigenline from the same Decimal Hessian.

    Binary eigendecomposition selects the already-owned simple eigenline.  A
    Decimal Schur complement then evaluates its eigenvalue without replacing
    the branch selector or changing the ordered-event equation.
    """

    vv = blocks["hessian_velocity_velocity"]
    mv = blocks["hessian_multiplier_velocity"]
    mm = blocks["hessian_multiplier_multiplier"]
    qdim = len(vv)
    mdim = len(mm)
    hessian = [
        vv[row][:] + [mv[column][row] for column in range(mdim)]
        for row in range(qdim)
    ] + [
        mv[row][:] + mm[row][:]
        for row in range(mdim)
    ]
    hessian_float = np.asarray([
        [float(value) for value in row] for row in hessian
    ], dtype=float)
    values, vectors = np.linalg.eigh(hessian_float)
    reference_float = np.asarray(reference, dtype=float)
    if reference_float.shape != (qdim + mdim,):
        raise ValueError("ordered-event reference dimension mismatch")
    index = int(np.argmax(np.abs(vectors.T @ reference_float)))
    vector = vectors[:, index]
    estimate = float(values[index])
    pivot = int(np.argmax(np.abs(vector)))
    retained = [item for item in range(qdim + mdim) if item != pivot]
    with localcontext() as context:
        context.prec = precision
        diagonal = hessian[pivot][pivot]
        coupling = [hessian[item][pivot] for item in retained]
        complement = [[hessian[row][column] for column in retained]
                      for row in retained]
        eigenvalue = Decimal.from_float(estimate)
        for _ in range(6):
            shifted = [[
                complement[row][column]
                - (eigenvalue if row == column else Decimal(0))
                for column in range(len(retained))
            ] for row in range(len(retained))]
            inverse_coupling = [row[0] for row in _solve(
                shifted, [[value] for value in coupling]
            )]
            residual = (
                diagonal - eigenvalue
                - sum(left * right for left, right in zip(
                    coupling, inverse_coupling,
                ))
            )
            derivative = -Decimal(1) - sum(
                value * value for value in inverse_coupling
            )
            correction = residual / derivative
            eigenvalue -= correction
            if abs(correction) < Decimal(10) ** (-(precision - 8)):
                break
    gaps = np.abs(values - values[index])
    gaps[index] = np.inf
    return {
        "eigenvalue": float(eigenvalue),
        "eigenvalue_decimal": str(eigenvalue),
        "binary_estimate": estimate,
        "index": index,
        "vector": vector,
        "spectral_gap": float(np.min(gaps)),
    }


def high_precision_constraint_residual_from_blocks(
    velocities: np.ndarray,
    blocks: dict[str, object],
) -> np.ndarray:
    """Return the unchanged multiplier and canonical-energy constraints."""

    velocity = [_d(value) for value in np.asarray(velocities, dtype=float)]
    gradient_v = blocks["gradient_velocity"]
    energy = (
        sum(left * right for left, right in zip(gradient_v, velocity))
        - blocks["action_value"]
    )
    return np.asarray([
        *[float(value) for value in blocks["gradient_multiplier"]],
        float(energy),
    ])


__all__ = [
    "high_precision_velocity_jet_blocks",
    "high_precision_canonical_momentum",
    "high_precision_canonical_momentum_from_blocks",
    "high_precision_ordered_eigenpair_from_blocks",
    "high_precision_constraint_residual_from_blocks",
]
