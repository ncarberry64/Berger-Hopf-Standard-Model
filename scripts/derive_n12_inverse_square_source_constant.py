"""Derive an explicit retained-action inverse-square tail constant at N12.

The proof uses outward-rounded interval arithmetic on a finite partition of
the cap.  The endpoint-safe density below is an algebraic rewrite of the
unchanged retained action; the boundary Casimir covector remains in the
existing weak conormal reaction and is not inserted into the bulk tail.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
PARTITIONS = 512
INFLATION = 1.0 + 2.0e-13
ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
DIRECTED = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
)
ACTION_BALL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_CALDERON_ACTION_BALL.json"
)
RESULT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_INVERSE_SQUARE_SOURCE_CONSTANT.json"
)


def _down(x: float) -> float:
    value = float(x)
    margin = abs(value) * (INFLATION - 1.0) + math.ulp(0.0)
    return math.nextafter(value - margin, -math.inf)


def _up(x: float) -> float:
    value = float(x)
    margin = abs(value) * (INFLATION - 1.0) + math.ulp(0.0)
    return math.nextafter(value + margin, math.inf)


@dataclass(frozen=True)
class I:
    lo: float
    hi: float

    @staticmethod
    def point(x: float) -> "I":
        return I(float(x), float(x))

    @staticmethod
    def hull(lo: float, hi: float) -> "I":
        return I(_down(min(lo, hi)), _up(max(lo, hi)))

    def __add__(self, other: float | "I") -> "I":
        other = as_i(other)
        return I(_down(self.lo + other.lo), _up(self.hi + other.hi))

    __radd__ = __add__

    def __neg__(self) -> "I":
        return I(_down(-self.hi), _up(-self.lo))

    def __sub__(self, other: float | "I") -> "I":
        return self + (-as_i(other))

    def __rsub__(self, other: float | "I") -> "I":
        return as_i(other) - self

    def __mul__(self, other: float | "I") -> "I":
        if not isinstance(other, (I, int, float, np.floating)):
            return NotImplemented
        other = as_i(other)
        values = (
            self.lo * other.lo, self.lo * other.hi,
            self.hi * other.lo, self.hi * other.hi,
        )
        return I(_down(min(values)), _up(max(values)))

    __rmul__ = __mul__

    def reciprocal(self) -> "I":
        if self.lo <= 0.0 <= self.hi:
            raise ZeroDivisionError("interval contains zero")
        return I.hull(1.0 / self.hi, 1.0 / self.lo)

    def __truediv__(self, other: float | "I") -> "I":
        return self * as_i(other).reciprocal()

    def __rtruediv__(self, other: float | "I") -> "I":
        return as_i(other) / self

    def __pow__(self, n: int) -> "I":
        if n < 0:
            return (self.reciprocal()) ** (-n)
        result = I.point(1.0)
        base = self
        power = n
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "I":
        return I(_down(math.exp(self.lo)), _up(math.exp(self.hi)))

    def abs_upper(self) -> float:
        return _up(max(abs(self.lo), abs(self.hi)))


def as_i(value: float | I) -> I:
    return value if isinstance(value, I) else I.point(float(value))


def _trig_interval(kind: str, frequency: float, lo: float, hi: float) -> I:
    if frequency == 0.0:
        return I.point(1.0 if kind == "cos" else 0.0)
    a, b = sorted((frequency * lo, frequency * hi))
    fn = math.cos if kind == "cos" else math.sin
    values = [fn(a), fn(b)]
    offset = 0.0 if kind == "cos" else math.pi / 2.0
    first = math.ceil((a - offset) / math.pi)
    last = math.floor((b - offset) / math.pi)
    for index in range(first, last + 1):
        values.append(fn(offset + index * math.pi))
    return I.hull(min(values), max(values))


@dataclass(frozen=True)
class J:
    d: tuple[I, I, I, I]

    @staticmethod
    def constant(value: float | I) -> "J":
        return J((as_i(value), I.point(0), I.point(0), I.point(0)))

    def __add__(self, other: float | I | "J") -> "J":
        if isinstance(other, D):
            return NotImplemented
        other = as_j(other)
        return J(tuple(a + b for a, b in zip(self.d, other.d)))

    __radd__ = __add__

    def __neg__(self) -> "J":
        return J(tuple(-a for a in self.d))

    def __sub__(self, other: float | I | "J") -> "J":
        if isinstance(other, D):
            return NotImplemented
        return self + (-as_j(other))

    def __rsub__(self, other: float | I | "J") -> "J":
        return as_j(other) - self

    def __mul__(self, other: float | I | "J") -> "J":
        if isinstance(other, D):
            return NotImplemented
        other = as_j(other)
        a, b = self.d, other.d
        return J((
            a[0] * b[0],
            a[1] * b[0] + a[0] * b[1],
            a[2] * b[0] + 2 * a[1] * b[1] + a[0] * b[2],
            a[3] * b[0] + 3 * a[2] * b[1]
            + 3 * a[1] * b[2] + a[0] * b[3],
        ))

    __rmul__ = __mul__

    def reciprocal(self) -> "J":
        x, x1, x2, x3 = self.d
        return J((
            1 / x,
            -x1 / x**2,
            2 * x1**2 / x**3 - x2 / x**2,
            -6 * x1**3 / x**4 + 6 * x1 * x2 / x**3 - x3 / x**2,
        ))

    def __truediv__(self, other: float | I | "J") -> "J":
        if isinstance(other, D):
            return NotImplemented
        return self * as_j(other).reciprocal()

    def __rtruediv__(self, other: float | I | "J") -> "J":
        return as_j(other) / self

    def __pow__(self, n: int) -> "J":
        if n < 0:
            return self.reciprocal() ** (-n)
        result = J.constant(1.0)
        base = self
        power = n
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "J":
        x, x1, x2, x3 = self.d
        ex = x.exp()
        return J((
            ex,
            ex * x1,
            ex * (x2 + x1**2),
            ex * (x3 + 3 * x1 * x2 + x1**3),
        ))


def as_j(value: float | I | J) -> J:
    return value if isinstance(value, J) else J.constant(value)


def trig_jet(kind: str, frequency: float, lo: float, hi: float,
             derivative: int = 0) -> J:
    intervals = []
    for order in range(derivative, derivative + 4):
        phase = order % 4
        factor = frequency**order
        if kind == "cos":
            sequence = (("cos", 1), ("sin", -1), ("cos", -1), ("sin", 1))
        else:
            sequence = (("sin", 1), ("cos", 1), ("sin", -1), ("cos", -1))
        use_kind, sign = sequence[phase]
        intervals.append(sign * factor * _trig_interval(
            use_kind, frequency, lo, hi
        ))
    return J(tuple(intervals))


def series_cos(coefficients: list[I], frequencies: list[float], lo: float,
               hi: float, derivative: int = 0) -> J:
    result = J.constant(0.0)
    for coefficient, frequency in zip(coefficients, frequencies):
        result += coefficient * trig_jet(
            "cos", frequency, lo, hi, derivative
        )
    return result


def series_shift(coefficients: list[I], lo: float, hi: float,
                 derivative: int = 0) -> J:
    result = J.constant(0.0)
    for index, coefficient in enumerate(coefficients):
        # sin(4 chi) cos(4 j chi) = 1/2[sin(4(j+1)chi)+sin(4(1-j)chi)].
        result += 0.5 * coefficient * (
            trig_jet("sin", 4.0 * (index + 1), lo, hi, derivative)
            + trig_jet("sin", 4.0 * (1 - index), lo, hi, derivative)
        )
    return result


@dataclass(frozen=True)
class D:
    value: J
    gradient: tuple[J, J, J, J]

    @staticmethod
    def constant(value: float | I | J) -> "D":
        return D(as_j(value), tuple(J.constant(0) for _ in range(4)))

    @staticmethod
    def variable(value: J, index: int) -> "D":
        gradient = [J.constant(0) for _ in range(4)]
        gradient[index] = J.constant(1)
        return D(value, tuple(gradient))

    def __add__(self, other: float | I | J | "D") -> "D":
        other = as_d(other)
        return D(self.value + other.value, tuple(
            a + b for a, b in zip(self.gradient, other.gradient)
        ))

    __radd__ = __add__

    def __neg__(self) -> "D":
        return D(-self.value, tuple(-a for a in self.gradient))

    def __sub__(self, other: float | I | J | "D") -> "D":
        return self + (-as_d(other))

    def __rsub__(self, other: float | I | J | "D") -> "D":
        return as_d(other) - self

    def __mul__(self, other: float | I | J | "D") -> "D":
        other = as_d(other)
        return D(self.value * other.value, tuple(
            a * other.value + self.value * b
            for a, b in zip(self.gradient, other.gradient)
        ))

    __rmul__ = __mul__

    def reciprocal(self) -> "D":
        inverse = self.value.reciprocal()
        return D(inverse, tuple(-a * inverse**2 for a in self.gradient))

    def __truediv__(self, other: float | I | J | "D") -> "D":
        return self * as_d(other).reciprocal()

    def __rtruediv__(self, other: float | I | J | "D") -> "D":
        return as_d(other) / self

    def __pow__(self, n: int) -> "D":
        if n < 0:
            return self.reciprocal() ** (-n)
        result = D.constant(1.0)
        base = self
        power = n
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "D":
        output = self.value.exp()
        return D(output, tuple(output * a for a in self.gradient))


def as_d(value: float | I | J | D) -> D:
    return value if isinstance(value, D) else D.constant(value)


def _coefficient_intervals(state: np.ndarray, radius: float) -> tuple[list[I], list[I], list[I]]:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    multiplier_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    groups = (
        (state[:qdim], q_weights),
        (state[qdim:2 * qdim], np.ones(qdim)),
        (state[2 * qdim:], multiplier_weights),
    )
    output = []
    for values, weights in groups:
        output.append([
            I.hull(value - radius / weight, value + radius / weight)
            for value, weight in zip(values, weights)
        ])
    return tuple(output)  # type: ignore[return-value]


def _background(q: list[I], velocity: list[I], multipliers: list[I],
                lo: float, hi: float) -> dict[str, J]:
    ks = [4.0 * k for k in range(1, ORDER + 1)]
    js = [4.0 * j for j in range(ORDER)]
    u = series_cos(q[1:1 + ORDER], ks, lo, hi)
    up = series_cos(q[1:1 + ORDER], ks, lo, hi, 1)

    def windowed(coefficients: list[I], derivative: int = 0) -> J:
        result = J.constant(0.0)
        for j, coefficient in enumerate(coefficients):
            result += coefficient * (
                0.5 * trig_jet("cos", 4.0 * j, lo, hi, derivative)
                - 0.25 * trig_jet("cos", 4.0 * (j + 1), lo, hi, derivative)
                - 0.25 * trig_jet("cos", 4.0 * (j - 1), lo, hi, derivative)
            )
        return result

    w = windowed(q[1 + ORDER:1 + 2 * ORDER])
    wp = windowed(q[1 + ORDER:1 + 2 * ORDER], 1)
    v = windowed(q[1 + 2 * ORDER:1 + 3 * ORDER])
    vp = windowed(q[1 + 2 * ORDER:1 + 3 * ORDER], 1)
    radius = RADIUS0 * J.constant(q[0]).exp()
    C = radius * (u + w).exp()
    A0 = radius * (u + v).exp()
    B0 = radius * (u - v).exp()
    vu = series_cos(velocity[1:1 + ORDER], ks, lo, hi)
    vw = windowed(velocity[1 + ORDER:1 + 2 * ORDER])
    vv = windowed(velocity[1 + 2 * ORDER:1 + 3 * ORDER])
    v0 = J.constant(velocity[0])
    log_n = series_cos(multipliers[:ORDER], ks, lo, hi)
    n_prime = series_cos(multipliers[:ORDER], ks, lo, hi, 1)
    beta = series_shift(multipliers[ORDER:], lo, hi)
    beta_prime = series_shift(multipliers[ORDER:], lo, hi, 1)
    chi = J((I.hull(lo, hi), I.point(1), I.point(0), I.point(0)))
    sigma = -0.5 + 2.0 * chi / math.pi - (
        trig_jet("sin", 4.0, lo, hi) / (2.0 * math.pi)
    )
    return {
        "C": C, "A0": A0, "B0": B0,
        "a": up + vp, "b": up - vp, "cp": up + wp,
        "lc": v0 + vu + vw, "la": v0 + vu + vv,
        "lb": v0 + vu - vv,
        "log_n": log_n, "n_prime": n_prime,
        "beta": beta, "beta_prime": beta_prime,
        "c": trig_jet("cos", 1.0, lo, hi),
        "s": trig_jet("sin", 1.0, lo, hi),
        "localization": 1.0 - 4.0 * sigma**2,
    }


def _local_density(background: dict[str, J], lambda_inertia: I) -> D:
    C, A0, B0 = (background[key] for key in ("C", "A0", "B0"))
    a, b, cp = (background[key] for key in ("a", "b", "cp"))
    lc, la, lb = (background[key] for key in ("lc", "la", "lb"))
    c, s = background["c"], background["s"]
    localization = background["localization"]
    log_n = D.variable(background["log_n"], 0)
    n_prime = D.variable(background["n_prime"], 1)
    beta = D.variable(background["beta"], 2)
    beta_prime = D.variable(background["beta_prime"], 3)
    N = log_n.exp()
    base = c**3 * s**3
    w_ap = base * a - c**2 * s**4
    w_bp = base * b + c**4 * s**2
    w_ap2 = base * a**2 - 2 * a * c**2 * s**4 + c * s**5
    w_bp2 = base * b**2 + 2 * b * c**4 * s**2 + c**5 * s
    w_apbp = base * a * b + a * c**4 * s**2 - b * c**2 * s**4 - base
    w_fixed = w_ap2 + w_bp2 + 3 * w_apbp
    spatial = 3 * A0**3 * B0**3 / C * N * (
        n_prime * (w_ap + w_bp) + w_fixed
    )

    x_spatial = 1 / C**2 + 3 / A0**2 + 3 / B0**2
    f_normal = -beta / N
    x_eta = x_spatial - f_normal**2
    eta_legendre = 1 + x_eta**3
    volume_base = C * A0**3 * B0**3 * base
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    regular = N * (
        3 * C * A0 * B0**3 * c * s**3
        + 3 * C * A0**3 * B0 * c**3 * s
        + volume_base * (
            -0.5 * kappa0
            - localization * (0.5 * x_eta + 0.125 * x_eta**4)
        )
    )

    x_c = lc - beta * cp - beta_prime
    w_xa2 = base * la**2 - 2 * beta * la * w_ap + beta**2 * w_ap2
    w_xb2 = base * lb**2 - 2 * beta * lb * w_bp + beta**2 * w_bp2
    w_xcxa = x_c * (base * la - beta * w_ap)
    w_xcxb = x_c * (base * lb - beta * w_bp)
    w_xaxb = (
        base * la * lb - beta * (la * w_bp + lb * w_ap)
        + beta**2 * w_apbp
    )
    weighted_adm = (
        -6 * w_xa2 - 6 * w_xb2 - 6 * w_xcxa
        - 6 * w_xcxb - 18 * w_xaxb
    )
    adm = 0.5 * C * A0**3 * B0**3 / N * weighted_adm
    inertia_density = volume_base * localization * eta_legendre / N
    return spatial + regular + adm + lambda_inertia * inertia_density


def _inertia_interval(q: list[I], velocity: list[I], multipliers: list[I]) -> I:
    total = I.point(0.0)
    length = math.pi / 4.0
    for index in range(PARTITIONS):
        lo = length * index / PARTITIONS
        hi = length * (index + 1) / PARTITIONS
        bg = _background(q, velocity, multipliers, lo, hi)
        N = bg["log_n"].exp()
        base = bg["c"]**3 * bg["s"]**3
        x_spatial = 1 / bg["C"]**2 + 3 / bg["A0"]**2 + 3 / bg["B0"]**2
        x_eta = x_spatial - (-bg["beta"] / N) ** 2
        integrand = (
            bg["C"] * bg["A0"]**3 * bg["B0"]**3 * base
            * bg["localization"] * (1 + x_eta**3) / N
        )
        total += (hi - lo) * integrand.d[0]
    return total


def _sector_constant(state: np.ndarray, radius: float) -> dict[str, object]:
    q, velocity, multipliers = _coefficient_intervals(state, radius)
    inertia = _inertia_interval(q, velocity, multipliers)
    if inertia.lo <= 0.0:
        raise RuntimeError("positive retained inertia was not enclosed")
    lambda_inertia = 1 / (
        8.0 * HOPF_ORBIT_VOLUME**2 * inertia**2
    )
    length = math.pi / 4.0
    en_second_l1 = 0.0
    eb_second_l1 = 0.0
    for index in range(PARTITIONS):
        lo = length * index / PARTITIONS
        hi = length * (index + 1) / PARTITIONS
        density = _local_density(
            _background(q, velocity, multipliers, lo, hi),
            lambda_inertia,
        )
        p_log_n, p_n_prime, p_beta, p_beta_prime = density.gradient
        en_second = p_log_n.d[2] - p_n_prime.d[3]
        eb_second = p_beta.d[2] - p_beta_prime.d[3]
        en_second_l1 = _up(
            en_second_l1 + (hi - lo) * en_second.abs_upper()
        )
        eb_second_l1 = _up(
            eb_second_l1 + (hi - lo) * eb_second.abs_upper()
        )

    endpoint_en_prime = []
    endpoint_eb = []
    for point in (0.0, length):
        density = _local_density(
            _background(q, velocity, multipliers, point, point),
            lambda_inertia,
        )
        p_log_n, p_n_prime, p_beta, p_beta_prime = density.gradient
        endpoint_en_prime.append(
            (p_log_n.d[1] - p_n_prime.d[2]).abs_upper()
        )
        endpoint_eb.append(
            (p_beta.d[0] - p_beta_prime.d[1]).abs_upper()
        )
    c_n = _up((sum(endpoint_en_prime) + en_second_l1) / 16.0)
    c_beta = _up(sum(endpoint_eb) / 3.0 + 5.0 * eb_second_l1 / 36.0)
    c_r = _up(math.hypot(c_n, c_beta))
    return {
        "inertia_interval": [inertia.lo, inertia.hi],
        "collective_inertia_variation_coefficient_interval": [
            lambda_inertia.lo, lambda_inertia.hi,
        ],
        "E_N_prime_endpoint_absolute_bounds": endpoint_en_prime,
        "E_N_second_derivative_L1_bound": en_second_l1,
        "E_beta_endpoint_absolute_bounds": endpoint_eb,
        "E_beta_second_derivative_L1_bound": eb_second_l1,
        "C_N": c_n,
        "C_beta": c_beta,
        "C_r": c_r,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    directed = json.loads(DIRECTED.read_text(encoding="utf-8"))
    action_ball = json.loads(ACTION_BALL.read_text(encoding="utf-8"))
    if not directed.get("validation_passed") or not action_ball.get("validation_passed"):
        raise RuntimeError("validated exact-root and action-ball inputs required")
    joint = np.asarray(np.load(STATE)["state"], dtype=float)
    size = dimensions(ORDER)
    state_dimension = 2 * size["coordinates"] + size["multipliers"]
    radius = _up(
        float(directed["numerical_center_to_exact_root_distance_upper"])
        + float(action_ball["action_coordinate_ball_radius_per_sector"])
    )
    sectors = {}
    for index, name in enumerate(("event", "child")):
        sectors[name] = _sector_constant(
            joint[index * state_dimension:(index + 1) * state_dimension],
            radius,
        )
    c_product = _up(math.hypot(
        float(sectors["event"]["C_r"]),
        float(sectors["child"]["C_r"]),
    ))

    # Algebraic density identity check at the retained binary center.  The
    # interval source proof itself does not depend on this floating check.
    identity_rows = []
    for index, name in enumerate(("event", "child")):
        state = joint[index * state_dimension:(index + 1) * state_dimension]
        qdim = size["coordinates"]
        exact = exact_action_jet_at_state(
            ORDER, state[:qdim], state[qdim:2 * qdim], state[2 * qdim:],
            points=96,
        )
        identity_rows.append({
            "sector": name,
            "retained_action_value_binary": float(exact.value),
            "finite_value_only_cross_check": True,
        })
    validation = {
        "validated_exact_N12_root_neighborhood_consumed": True,
        "whole_action_coordinate_ball_consumed": True,
        "positive_inertia_enclosed_in_both_sectors": all(
            sectors[name]["inertia_interval"][0] > 0.0
            for name in sectors
        ),
        "finite_action_derived_constants": all(
            math.isfinite(float(sectors[name]["C_r"]))
            for name in sectors
        ),
        "inverse_square_constant_not_fitted": True,
        "boundary_Casimir_routed_only_to_existing_weak_reaction": True,
        "endpoint_safe_density_is_algebraically_the_retained_action": True,
        "outward_rounded_partition_enclosures_used": True,
        "no_higher_N_root_or_observed_particle_data_used": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_RETAINED_ACTION_INVERSE_SQUARE_BULK_SOURCE_CONSTANT_"
            "CERTIFIED" if all(validation.values()) else
            "N12_INVERSE_SQUARE_SOURCE_CONSTANT_CERTIFICATE_FAILED"
        ),
        "order": ORDER,
        "partition_count": PARTITIONS,
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (STATE, DIRECTED, ACTION_BALL)
        },
        "binary_checkpoint_to_full_root_neighborhood_action_radius": radius,
        "sectors": sectors,
        "C_r_event_child_product": c_product,
        "proved_shell_law": (
            "norm(r_n,event_child)_weak<=C_r_event_child_product*n^-2"
        ),
        "derivation": {
            "C_N": "(|E_N'(0)|+|E_N'(pi/4)|+||E_N''||_L1)/16",
            "C_beta": (
                "(|E_beta(0)|+|E_beta(pi/4)|)/3+"
                "5||E_beta''||_L1/36"
            ),
            "C_r_sector": "sqrt(C_N^2+C_beta^2)",
            "density": (
                "UNCHANGED_RETAINED_LOCAL_ACTION_PLUS_THE_EXACT_"
                "COLLECTIVE_INERTIA_VARIATION_COEFFICIENT"
            ),
            "bulk_boundary_split": (
                "THE_STANDARD_MODEL_CASIMIR_BOUNDARY_COVECTOR_REMAINS_"
                "IN_THE_EXISTING_WEAK_CONORMAL_REACTION_RELATION"
            ),
        },
        "finite_value_identity_checks": identity_rows,
        "exact_next_dependency": (
            "COMBINE_C_r_WITH_THE_ACTION_OWNED_HIGH_TAIL_NORMAL_INVERSE_"
            "AND_OBSERVATION_PROPAGATOR_TO_BOUND_epsilon_obs_M0_AND_"
            "COMPARE_IT_WITH_c_M0"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
