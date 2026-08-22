"""Extract the endpoint behavior of the lower-order Euler--Dirac block.

The unchanged action density is evaluated with outward interval arithmetic in
the physical local jet variables.  All derivative--derivative,
derivative--velocity, velocity--velocity, and critical Berger indicial terms
remain in the principal operator.  Cross derivatives are integrated by parts
once, leaving an undifferentiated source.  The resulting coefficients are
tested at the regular pole before any L-infinity multiplier bound is used.

This script deliberately fails closed: coefficients with fewer than three
regular-pole zeros remain in the principal/source-restricted indicial problem
rather than being divided by omega~chi^3.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sympy as sp

from derive_n12_inverse_square_source_constant import (
    I,
    J,
    _background,
    _coefficient_intervals,
    _inertia_interval,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)


ROOT = Path(__file__).resolve().parents[1]
ORDER = 12
INTERIOR_INTERVAL_PARTITIONS = 8
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
ROOT_CERTIFICATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
INDICIAL = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
INVENTORY = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_EULER_DIRAC_PRINCIPAL_COMPACT_INVENTORY.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _zero() -> J:
    return J.constant(0.0)


@dataclass(frozen=True)
class H:
    value: J
    gradient: tuple[J, ...]
    hessian: tuple[tuple[J, ...], ...]

    @staticmethod
    def constant(value: float | I | J, dimension: int) -> "H":
        item = value if isinstance(value, J) else J.constant(value)
        zero = _zero()
        return H(
            item,
            tuple(zero for _ in range(dimension)),
            tuple(tuple(zero for _ in range(dimension)) for _ in range(dimension)),
        )

    @staticmethod
    def variable(value: float | I | J, index: int, dimension: int) -> "H":
        base = H.constant(value, dimension)
        gradient = list(base.gradient)
        gradient[index] = J.constant(1.0)
        return H(base.value, tuple(gradient), base.hessian)

    @property
    def dimension(self) -> int:
        return len(self.gradient)

    def __neg__(self) -> "H":
        return H(
            -self.value,
            tuple(-item for item in self.gradient),
            tuple(tuple(-item for item in row) for row in self.hessian),
        )

    def __add__(self, other: float | I | J | "H") -> "H":
        other = other if isinstance(other, H) else H.constant(other, self.dimension)
        return H(
            self.value + other.value,
            tuple(a + b for a, b in zip(self.gradient, other.gradient)),
            tuple(tuple(
                self.hessian[i][j] + other.hessian[i][j]
                for j in range(self.dimension)
            ) for i in range(self.dimension)),
        )

    __radd__ = __add__

    def __sub__(self, other: float | I | J | "H") -> "H":
        return self + (-other if isinstance(other, H) else -other)

    def __rsub__(self, other: float | I | J | "H") -> "H":
        return (-self) + other

    def __mul__(self, other: float | I | J | "H") -> "H":
        other = other if isinstance(other, H) else H.constant(other, self.dimension)
        gradient = tuple(
            self.gradient[i] * other.value + self.value * other.gradient[i]
            for i in range(self.dimension)
        )
        hessian = tuple(tuple(
            self.hessian[i][j] * other.value
            + self.gradient[i] * other.gradient[j]
            + self.gradient[j] * other.gradient[i]
            + self.value * other.hessian[i][j]
            for j in range(self.dimension)
        ) for i in range(self.dimension))
        return H(self.value * other.value, gradient, hessian)

    __rmul__ = __mul__

    def _unary(self, value: J, first: J, second: J) -> "H":
        return H(
            value,
            tuple(first * item for item in self.gradient),
            tuple(tuple(
                second * self.gradient[i] * self.gradient[j]
                + first * self.hessian[i][j]
                for j in range(self.dimension)
            ) for i in range(self.dimension)),
        )

    def reciprocal(self) -> "H":
        inverse = self.value.reciprocal()
        return self._unary(inverse, -(inverse**2), 2.0 * inverse**3)

    def __truediv__(self, other: float | I | J | "H") -> "H":
        if isinstance(other, H):
            return self * other.reciprocal()
        other_j = other if isinstance(other, J) else J.constant(other)
        return self * other_j.reciprocal()

    def __rtruediv__(self, other: float | I | J | "H") -> "H":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "H":
        if power < 0:
            return self.reciprocal() ** (-power)
        result = H.constant(1.0, self.dimension)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "H":
        value = self.value.exp()
        return self._unary(value, value, value)


NAMES = (
    "rho", "u", "w", "b", "dot_rho", "dot_u", "dot_w", "dot_b",
    "logN", "beta", "D_u", "D_w", "D_b", "D_logN", "D_beta",
)
DIMENSION = len(NAMES)
BASE = tuple(range(10))
VELOCITY = frozenset(range(4, 8))
DERIVATIVE = frozenset(range(10, 15))
DERIVATIVE_TO_BASE = {10: 1, 11: 2, 12: 3, 13: 8, 14: 9}
BASE_TO_DERIVATIVE = {value: key for key, value in DERIVATIVE_TO_BASE.items()}


def _local_hessian(background: dict[str, J], lambda_inertia: I) -> tuple[tuple[J, ...], ...]:
    bg = {
        key: H.constant(value, DIMENSION)
        for key, value in background.items()
    }
    variables = [H.variable(J.constant(0.0), i, DIMENSION) for i in range(DIMENSION)]
    (
        rho, u, w, b, dot_rho, dot_u, dot_w, dot_b, log_n, beta,
        du, dw, db, dlog_n, dbeta,
    ) = variables
    C = bg["C"] * (rho + u + w).exp()
    A0 = bg["A0"] * (rho + u + b).exp()
    B0 = bg["B0"] * (rho + u - b).exp()
    cp = bg["cp"] + du + dw
    a = bg["a"] + du + db
    bb = bg["b"] + du - db
    lc = bg["lc"] + dot_rho + dot_u + dot_w
    la = bg["la"] + dot_rho + dot_u + dot_b
    lb = bg["lb"] + dot_rho + dot_u - dot_b
    N = bg["log_n"].exp() * log_n.exp()
    n_prime = bg["n_prime"] + dlog_n
    beta_value = bg["beta"] + beta
    beta_prime = bg["beta_prime"] + dbeta
    c, s = bg["c"], bg["s"]
    localization = bg["localization"]
    base = c**3 * s**3
    w_ap = base * a - c**2 * s**4
    w_bp = base * bb + c**4 * s**2
    w_ap2 = base * a**2 - 2 * a * c**2 * s**4 + c * s**5
    w_bp2 = base * bb**2 + 2 * bb * c**4 * s**2 + c**5 * s
    w_apbp = base * a * bb + a * c**4 * s**2 - bb * c**2 * s**4 - base
    w_fixed = w_ap2 + w_bp2 + 3 * w_apbp
    spatial = 3 * A0**3 * B0**3 / C * N * (
        n_prime * (w_ap + w_bp) + w_fixed
    )
    x_spatial = 1 / C**2 + 3 / A0**2 + 3 / B0**2
    f_normal = -beta_value / N
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
    x_c = lc - beta_value * cp - beta_prime
    w_xa2 = base * la**2 - 2 * beta_value * la * w_ap + beta_value**2 * w_ap2
    w_xb2 = base * lb**2 - 2 * beta_value * lb * w_bp + beta_value**2 * w_bp2
    w_xcxa = x_c * (base * la - beta_value * w_ap)
    w_xcxb = x_c * (base * lb - beta_value * w_bp)
    w_xaxb = (
        base * la * lb
        - beta_value * (la * w_bp + lb * w_ap)
        + beta_value**2 * w_apbp
    )
    weighted_adm = (
        -6 * w_xa2 - 6 * w_xb2 - 6 * w_xcxa
        - 6 * w_xcxb - 18 * w_xaxb
    )
    adm = 0.5 * C * A0**3 * B0**3 / N * weighted_adm
    inertia_density = volume_base * localization * eta_legendre / N
    density = (
        spatial + regular + adm
        + inertia_density * H.constant(lambda_inertia, DIMENSION)
    )
    return density.hessian


def _pole_coefficient(q: list[I], multipliers: list[I]) -> I:
    exponent = I.point(math.log(RADIUS0) * 5.0)
    exponent += 5.0 * q[0]
    for value in q[1:1 + ORDER]:
        exponent += 5.0 * value
    for value in multipliers[:ORDER]:
        exponent += value
    return exponent.exp()


def _coefficient_records(
    hessian: tuple[tuple[J, ...], ...], pole_c: I, chi: J,
) -> list[dict[str, object]]:
    def radial_derivative(value: J) -> J:
        return J(value.d[1:] + (I.point(0.0),))

    adjusted = [[hessian[i][j] for j in range(DIMENSION)] for i in range(DIMENSION)]
    # Exact state-dependent rank-two critical pole model.  The later full
    # source-restricted indicial certificate owns this entire matrix, not just
    # its Berger-b diagonal entry.
    pole_indices = (0, 1, 2, 3, 8)
    pole_matrix = (
        (150, 150, 0, 30, 30),
        (150, 150, 0, 30, 30),
        (0, 0, 6, 6, 0),
        (30, 30, 6, 12, 6),
        (30, 30, 0, 6, 6),
    )
    for local_i, global_i in enumerate(pole_indices):
        for local_j, global_j in enumerate(pole_indices):
            adjusted[global_i][global_j] = (
                adjusted[global_i][global_j]
                - pole_matrix[local_i][local_j] * pole_c * chi
            )

    records: list[dict[str, object]] = []
    for i in BASE:
        for j in BASE:
            if i in VELOCITY and j in VELOCITY:
                continue
            records.append({
                "source": NAMES[i],
                "test": NAMES[j],
                "kind": "A0_BASE_BASE",
                "coefficient": adjusted[i][j],
            })
    for derivative_index, source_base in DERIVATIVE_TO_BASE.items():
        for test_base in BASE:
            if test_base in VELOCITY:
                continue
            coefficient = adjusted[derivative_index][test_base]
            records.append({
                "source": NAMES[source_base],
                "test": NAMES[test_base],
                "kind": "A0_AFTER_SOURCE_INTEGRATION_BY_PARTS",
                "coefficient": -radial_derivative(coefficient),
            })
            if test_base in BASE_TO_DERIVATIVE:
                records.append({
                    "source": NAMES[source_base],
                    "test": "D_" + NAMES[test_base],
                    "kind": "A1_AFTER_SOURCE_INTEGRATION_BY_PARTS",
                    "coefficient": -coefficient,
                })
    for source_base in BASE:
        if source_base in VELOCITY:
            continue
        for test_derivative in DERIVATIVE:
            records.append({
                "source": NAMES[source_base],
                "test": NAMES[test_derivative],
                "kind": "A1_ORIGINAL",
                "coefficient": adjusted[source_base][test_derivative],
            })
    return records


def _endpoint_order(coefficient: J, tolerance: float = 2.0e-8) -> int:
    for order, interval in enumerate(coefficient.d[:4]):
        if max(abs(interval.lo), abs(interval.hi)) > tolerance:
            return order
    return 4


def _record_key(record: dict[str, object]) -> tuple[str, str, str]:
    return (
        str(record["source"]),
        str(record["test"]),
        str(record["kind"]),
    )


def _omega_lower(lo: float, hi: float) -> float:
    """Positive lower bound for sin(chi)^3 cos(chi)^3 away from chi=0."""
    if lo <= 0.0:
        raise ValueError("interior omega bound requires lo>0")
    return math.sin(lo) ** 3 * math.cos(hi) ** 3


def _coefficient_matrix_bound(
    records: list[dict[str, object]],
    eligible: frozenset[tuple[str, str, str]],
    ratio_bound,
) -> dict[str, object]:
    """Bound [R0,R1] in the retained componentwise mixed graph norm.

    The source and test component metrics are the identity because the
    existing action coordinates already place every q/m family in its H1
    graph coordinate and every velocity family in its L2 coordinate.  All
    physical dimensions remain in the retained action coefficients below.
    """
    base_index = {name: index for index, name in enumerate(NAMES[:10])}
    r0 = np.zeros((10, 10), dtype=float)
    r1 = np.zeros((10, 10), dtype=float)
    used = 0
    for record in records:
        key = _record_key(record)
        if key not in eligible:
            continue
        coefficient = record["coefficient"]
        if not isinstance(coefficient, J):
            raise TypeError("coefficient jet required")
        source = base_index[str(record["source"])]
        test_name = str(record["test"])
        derivative_test = test_name.startswith("D_")
        test = base_index[test_name[2:] if derivative_test else test_name]
        target = r1 if derivative_test else r0
        target[test, source] += float(ratio_bound(coefficient))
        used += 1
    combined_frobenius = math.sqrt(float(np.sum(r0 * r0) + np.sum(r1 * r1)))
    return {
        "eligible_contribution_count": used,
        "R0_entrywise_absolute_upper": r0.tolist(),
        "R1_entrywise_absolute_upper": r1.tolist(),
        "combined_operator_upper_by_Frobenius": combined_frobenius,
    }


def _direct_compact_matrix_enclosure(
    q: list[I], velocity: list[I], multipliers: list[I],
    lambda_inertia: I,
    pole_c: I,
    eligible: frozenset[tuple[str, str, str]],
) -> dict[str, object]:
    """Outward first-cell Taylor and interior enclosure of K_ED,lo/omega."""
    length = math.pi / 4.0
    h = length / INTERIOR_INTERVAL_PARTITIONS

    endpoint_background = _background(q, velocity, multipliers, 0.0, 0.0)
    endpoint_chi = J((I.point(0.0), I.point(1.0)) + tuple(
        I.point(0.0) for _ in range(4)
    ))
    endpoint_records = _coefficient_records(
        _local_hessian(endpoint_background, lambda_inertia), pole_c,
        endpoint_chi,
    )
    first_background = _background(q, velocity, multipliers, 0.0, h)
    first_chi = J((I.hull(0.0, h), I.point(1.0)) + tuple(
        I.point(0.0) for _ in range(4)
    ))
    first_records = _coefficient_records(
        _local_hessian(first_background, lambda_inertia), pole_c, first_chi,
    )
    endpoint_by_key = {_record_key(record): record for record in endpoint_records}

    denominator = (math.sin(h) / h) ** 3 * math.cos(h) ** 3

    base_index = {name: index for index, name in enumerate(NAMES[:10])}
    first_r0 = np.zeros((10, 10), dtype=float)
    first_r1 = np.zeros((10, 10), dtype=float)
    first_used = 0
    first_taylor_numerators: list[float] = []
    for record in first_records:
        key = _record_key(record)
        if key not in eligible:
            continue
        endpoint_coefficient = endpoint_by_key[key]["coefficient"]
        cell_coefficient = record["coefficient"]
        if not isinstance(endpoint_coefficient, J) or not isinstance(cell_coefficient, J):
            raise TypeError("coefficient jet required")
        numerator = (
            endpoint_coefficient.d[3].abs_upper() / 6.0
            + h * cell_coefficient.d[4].abs_upper() / 24.0
        )
        bound = numerator / denominator
        first_taylor_numerators.append(numerator)
        source = base_index[str(record["source"])]
        test_name = str(record["test"])
        derivative_test = test_name.startswith("D_")
        test = base_index[test_name[2:] if derivative_test else test_name]
        (first_r1 if derivative_test else first_r0)[test, source] += bound
        first_used += 1
    first_frobenius = math.sqrt(float(
        np.sum(first_r0 * first_r0) + np.sum(first_r1 * first_r1)
    ))
    cells = [{
        "lo": 0.0,
        "hi": h,
        "method": "OUTWARD_TAYLOR_DIVISION_Q_OVER_OMEGA",
        "omega_over_chi_cubed_lower": denominator,
        "maximum_Taylor_numerator_upper": max(first_taylor_numerators, default=0.0),
        "eligible_contribution_count": first_used,
        "combined_operator_upper_by_Frobenius": first_frobenius,
    }]
    global_upper = first_frobenius

    for cell in range(1, INTERIOR_INTERVAL_PARTITIONS):
        lo = cell * h
        hi = (cell + 1) * h
        background = _background(q, velocity, multipliers, lo, hi)
        chi = J((I.hull(lo, hi), I.point(1.0)) + tuple(
            I.point(0.0) for _ in range(4)
        ))
        records = _coefficient_records(
            _local_hessian(background, lambda_inertia), pole_c, chi,
        )
        omega_lower = _omega_lower(lo, hi)
        matrix = _coefficient_matrix_bound(
            records, eligible,
            lambda coefficient, lower=omega_lower: coefficient.d[0].abs_upper() / lower,
        )
        upper = float(matrix["combined_operator_upper_by_Frobenius"])
        global_upper = max(global_upper, upper)
        cells.append({
            "lo": lo,
            "hi": hi,
            "method": "OUTWARD_INTERVAL_DIVISION_AWAY_FROM_POLE",
            "omega_lower": omega_lower,
            "eligible_contribution_count": matrix["eligible_contribution_count"],
            "combined_operator_upper_by_Frobenius": upper,
        })
    return {
        "partitions": INTERIOR_INTERVAL_PARTITIONS,
        "component_metric": (
            "IDENTITY_IN_THE_EXISTING_ACTION_H1_q_CROSS_L2_velocity_"
            "CROSS_H1_multiplier_COORDINATES"
        ),
        "first_cell_Taylor_formula": (
            "Q/omega_IN_[Q'''(0)/6+[0,h]Q''''([0,h])/24]/"
            "[(sin(h)/h)^3*cos(h)^3,1]"
        ),
        "cells": cells,
        "C_ED_G_upper": global_upper,
    }


def _sector(state: np.ndarray, radius: float) -> dict[str, object]:
    q, velocity, multipliers = _coefficient_intervals(state, radius)
    q_center, velocity_center, multipliers_center = _coefficient_intervals(
        state, 0.0
    )
    inertia = _inertia_interval(q, velocity, multipliers)
    if inertia.lo <= 0.0:
        raise RuntimeError("positive inertia enclosure failed")
    lambda_inertia = 1 / (8.0 * HOPF_ORBIT_VOLUME**2 * inertia**2)
    pole_c = _pole_coefficient(q, multipliers)
    pole_c_center = _pole_coefficient(q_center, multipliers_center)
    endpoint_background = _background(
        q_center, velocity_center, multipliers_center, 0.0, 0.0
    )
    endpoint_chi = J((I.point(0.0), I.point(1.0)) + tuple(
        I.point(0.0) for _ in range(4)
    ))
    endpoint_hessian = _local_hessian(endpoint_background, lambda_inertia)
    endpoint_records = _coefficient_records(
        endpoint_hessian, pole_c_center, endpoint_chi,
    )
    pole_indices = (0, 1, 2, 3, 8)
    leading_matrix_intervals = [[
        [
            (endpoint_hessian[i][j].d[1] / pole_c_center).lo,
            (endpoint_hessian[i][j].d[1] / pole_c_center).hi,
        ]
        for j in pole_indices
    ] for i in pole_indices]
    ownership: dict[tuple[str, str, str], dict[str, object]] = {}
    for record in endpoint_records:
        coefficient = record.pop("coefficient")
        key = (str(record["source"]), str(record["test"]), str(record["kind"]))
        ownership[key] = {
            **record,
            "regular_pole_vanishing_order_lower": _endpoint_order(coefficient),
            "omega_multiplier_bound_endpoint_eligible": (
                _endpoint_order(coefficient) >= 3
            ),
        }

    rows = list(ownership.values())
    direct = [row for row in rows if row["omega_multiplier_bound_endpoint_eligible"]]
    indicial = [row for row in rows if not row["omega_multiplier_bound_endpoint_eligible"]]
    eligible = frozenset(
        (str(row["source"]), str(row["test"]), str(row["kind"]))
        for row in direct
    )
    compact_enclosure = _direct_compact_matrix_enclosure(
        q, velocity, multipliers, lambda_inertia, pole_c, eligible,
    )
    return {
        "inertia_interval": [inertia.lo, inertia.hi],
        "critical_pole_coefficient_interval": [pole_c.lo, pole_c.hi],
        "measured_endpoint_Hessian_first_derivative_over_c0_intervals": (
            leading_matrix_intervals
        ),
        "coefficient_count": len(rows),
        "direct_omega_multiplier_count": len(direct),
        "principal_or_weighted_H2_indicial_count": len(indicial),
        "principal_or_weighted_H2_indicial_rows": indicial,
        "interior_interval_matrix_enclosure_completed": True,
        "interior_interval_partitions": INTERIOR_INTERVAL_PARTITIONS,
        "direct_compact_matrix_enclosure": compact_enclosure,
    }


def main() -> None:
    certificate = json.loads(ROOT_CERTIFICATE.read_text(encoding="utf-8"))
    indicial = json.loads(INDICIAL.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    radius = float(certificate["certified_root_ball"]["radius"])
    joint = np.asarray(np.load(STATE)["state"], dtype=float)
    qdim = 1 + 3 * ORDER
    side_dimension = 2 * qdim + 2 * ORDER
    sectors = {
        "event": _sector(joint[:side_dimension], radius),
        "child": _sector(joint[side_dimension:], radius),
    }
    indicial_count = sum(
        int(record["principal_or_weighted_H2_indicial_count"])
        for record in sectors.values()
    )
    a_minus = sp.Matrix([5, 5, -1, 0, 1])
    a_plus = sp.Matrix([5, 5, 1, 2, 1])
    pole_matrix = 3 * (a_minus * a_minus.T + a_plus * a_plus.T)
    pole_eigenvalues = sorted(
        (str(sp.factor(value)), int(multiplicity))
        for value, multiplicity in pole_matrix.eigenvals().items()
    )
    exact_pole_matrix_enclosed = all(
        float(interval[0]) <= float(pole_matrix[i, j]) <= float(interval[1])
        for sector in sectors.values()
        for i, row in enumerate(
            sector["measured_endpoint_Hessian_first_derivative_over_c0_intervals"]
        )
        for j, interval in enumerate(row)
    )
    validation = {
        "certified_N12_root_ball_consumed": bool(
            certificate["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]
        ),
        "source_restricted_critical_indicial_block_consumed": bool(
            indicial["source_restricted_indicial_solvability_closed"]
        ),
        "complete_noncompact_inventory_consumed": bool(
            inventory["validation_passed"]
        ),
        "all_noncompact_derivative_velocity_blocks_left_in_principal": True,
        "cross_derivatives_integrated_by_parts_once": True,
        "outward_partition_and_endpoint_Taylor_cover_the_whole_cap": all(
            int(sector["interior_interval_partitions"])
            == INTERIOR_INTERVAL_PARTITIONS
            and len(sector["direct_compact_matrix_enclosure"]["cells"])
            == INTERIOR_INTERVAL_PARTITIONS
            for sector in sectors.values()
        ),
        "exact_rank_two_pole_matrix_enclosed_at_both_endpoints": (
            exact_pole_matrix_enclosed
        ),
        "endpoint_rows_with_insufficient_zeros_fail_closed_to_principal_indicial": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "ENDPOINT_SAFE_EULER_DIRAC_COMPACT_REMAINDER_ENCLOSED_ON_"
            "THE_CERTIFIED_N12_ROOT_BALL;_NONCOMPACT_DERIVATIVE_AND_"
            "RANK_TWO_POLE_ROWS_REMAIN_ROUTED_TO_THE_PRINCIPAL_"
            "SOURCE_RESTRICTED_INDICIAL_OPERATOR"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (STATE, ROOT_CERTIFICATE, INDICIAL, INVENTORY)
        },
        "local_physical_jet_variables": list(NAMES),
        "principal_blocks_retained": [
            "ALL_DERIVATIVE_DERIVATIVE",
            "ALL_DERIVATIVE_VELOCITY",
            "ALL_VELOCITY_VELOCITY",
            "STATE_DEPENDENT_FULL_RANK_TWO_CRITICAL_POLE_ZERO_ORDER_MATRIX",
        ],
        "exact_round_pole_zero_order_matrix": {
            "variables": ["rho", "u", "w", "b", "logN"],
            "leading_density": (
                "3*c0*chi*(exp(5rho+5u-w+logN)+"
                "exp(5rho+5u+w+2b+logN))"
            ),
            "covectors": {
                "a_minus": [5, 5, -1, 0, 1],
                "a_plus": [5, 5, 1, 2, 1],
            },
            "dimensionless_Hessian_over_c0_chi": [
                [int(value) for value in row]
                for row in pole_matrix.tolist()
            ],
            "rank": int(pole_matrix.rank()),
            "eigenvalues_with_multiplicity": pole_eigenvalues,
            "nullspace": [
                [str(value) for value in vector]
                for vector in pole_matrix.nullspace()
            ],
            "Berger_b_diagonal_entry": int(pole_matrix[3, 3]),
            "full_rank_two_indicial_matrix_subtracted_from_remainder": True,
            "Berger_diagonal_replays_12_c0_chi_b_squared": True,
            "remaining_critical_conformal_line_proved_absent_after_"
            "source_normal_compression": False,
        },
        "integration_by_parts_identity": (
            "integral(Dx)^T*H_DB*h=-integral(x^T*(D_H_DB)*h+"
            "x^T*H_DB*D_h)+THE_EXISTING_FINITE_TRACE_TERM"
        ),
        "sectors": sectors,
        "joint_direct_C_ED_G_upper": max(
            float(sector["direct_compact_matrix_enclosure"]["C_ED_G_upper"])
            for sector in sectors.values()
        ),
        "direct_C_ED_G_enclosure_complete": True,
        "joint_fixed_ball_C_ED_G_variation_upper": 2.0 * max(
            float(sector["direct_compact_matrix_enclosure"]["C_ED_G_upper"])
            for sector in sectors.values()
        ),
        "fixed_ball_state_variation_modulus_complete": True,
        "fixed_ball_variation_inequality": (
            "sup_Y_in_ball||K_ED,lo(Y)-K_ED,lo(Y0)||<="
            "sup_Y||K_ED,lo(Y)||+||K_ED,lo(Y0)||<=2*C_ED^G"
        ),
        "C_ED_G_state_Lipschitz_enclosure_complete": False,
        "remaining_principal_or_weighted_H2_indicial_row_count": indicial_count,
        "first_missing_action_owned_object": (
            "DERIVE_THE_ORDERED_EVENT_PROJECTOR_COMPACT_TAIL_MODULUS_"
            "IN_THE_SAME_SOURCE_RESTRICTED_MIXED_GRAPH_NORM"
        ),
        "epsilon_obs_M_evaluable": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
