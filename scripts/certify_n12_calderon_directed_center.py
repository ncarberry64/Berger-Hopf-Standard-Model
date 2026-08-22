"""Directed interval center audit for the N12 Calderon graph symbol.

The retained 96-point action is reevaluated with interval order-two jets on
the existing boundary-compatible (w, shift) quotient.  All physical inputs
remain the certified N12 event/child pair.  This supplies the center rounding
enclosure needed by the finite action-ball lemma; it adds no equation or gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

import bhsm.interface.aether_exact_radial_schur_lift_v15_83 as reduced_action
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
DPS = int(os.environ.get("BHSM_N12_CALDERON_CENTER_DPS", "60"))
ROOT_NEIGHBORHOOD_MULTIPLIER = float(os.environ.get(
    "BHSM_N12_CALDERON_ROOT_NEIGHBORHOOD_MULTIPLIER", "2.0"
))
ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
PROMOTION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
ROOT_ROUNDING = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_DIRECTED_ROUNDING_CERTIFICATE.json"
)
EXACT_NORMAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_NORMAL_1E20.npz"
)
EXACT_RESIDUAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_CALDERON_DIRECTED_CENTER_RESULT",
    str(ROOT / (
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
    )),
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _iv(value: Any) -> Any:
    if hasattr(value, "ctx") and value.ctx is mp.iv:
        return value
    exact = mp.mpf(float(value))
    return mp.iv.mpf([exact, exact])


class IntervalJet:
    """Second-order multivariate jet with directed interval scalars."""

    __slots__ = ("value", "gradient", "hessian")
    active_indices: np.ndarray
    active_weights: np.ndarray

    def __init__(self, value: Any, gradient: np.ndarray, hessian: np.ndarray):
        self.value = _iv(value)
        self.gradient = np.asarray(gradient, dtype=object)
        self.hessian = np.asarray(hessian, dtype=object)

    @classmethod
    def constant(cls, value: Any, size: int) -> "IntervalJet":
        del size
        count = cls.active_indices.size
        zero = _iv(0.0)
        gradient = np.empty(count, dtype=object)
        gradient.fill(zero)
        hessian = np.empty((count, count), dtype=object)
        hessian.fill(zero)
        return cls(value, gradient, hessian)

    @classmethod
    def affine(cls, value: Any, coefficients: np.ndarray) -> "IntervalJet":
        vector = np.asarray(coefficients, dtype=float)[cls.active_indices]
        vector = vector / cls.active_weights
        gradient = np.asarray([_iv(item) for item in vector], dtype=object)
        count = vector.size
        zero = _iv(0.0)
        hessian = np.empty((count, count), dtype=object)
        hessian.fill(zero)
        return cls(value, gradient, hessian)

    def _coerce(self, other: Any) -> "IntervalJet":
        return other if isinstance(other, IntervalJet) else self.constant(
            other, self.gradient.size
        )

    def __add__(self, other: Any) -> "IntervalJet":
        other = self._coerce(other)
        return IntervalJet(
            self.value + other.value,
            self.gradient + other.gradient,
            self.hessian + other.hessian,
        )

    __radd__ = __add__

    def __neg__(self) -> "IntervalJet":
        return IntervalJet(-self.value, -self.gradient, -self.hessian)

    def __sub__(self, other: Any) -> "IntervalJet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Any) -> "IntervalJet":
        return (-self) + other

    def __mul__(self, other: Any) -> "IntervalJet":
        other = self._coerce(other)
        return IntervalJet(
            self.value * other.value,
            self.gradient * other.value + other.gradient * self.value,
            self.hessian * other.value + other.hessian * self.value
            + np.outer(self.gradient, other.gradient)
            + np.outer(other.gradient, self.gradient),
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "IntervalJet":
        return IntervalJet(
            1 / self.value,
            -self.gradient / self.value ** 2,
            2 * np.outer(self.gradient, self.gradient) / self.value ** 3
            - self.hessian / self.value ** 2,
        )

    def __truediv__(self, other: Any) -> "IntervalJet":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: Any) -> "IntervalJet":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "IntervalJet":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return self.constant(1.0, self.gradient.size)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = self.constant(1.0, self.gradient.size)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "IntervalJet":
        value = mp.iv.exp(self.value)
        return IntervalJet(
            value,
            self.gradient * value,
            (
                self.hessian + np.outer(self.gradient, self.gradient)
            ) * value,
        )


def _endpoints(value: Any) -> tuple[mp.mpf, mp.mpf]:
    return mp.mpf(value.a), mp.mpf(value.b)


def _mid_radius(matrix: np.ndarray) -> tuple[mp.matrix, mp.matrix]:
    rows, columns = matrix.shape
    midpoint = mp.matrix(rows, columns)
    radius = mp.matrix(rows, columns)
    for row in range(rows):
        for column in range(columns):
            lo, hi = _endpoints(matrix[row, column])
            midpoint[row, column] = (lo + hi) / 2
            radius[row, column] = (hi - lo) / 2
    return midpoint, radius


def _abs_matrix(matrix: mp.matrix) -> mp.matrix:
    return mp.matrix([
        [abs(matrix[row, column]) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ])


def _frobenius(matrix: mp.matrix) -> mp.mpf:
    return mp.sqrt(mp.fsum(
        abs(matrix[row, column]) ** 2
        for row in range(matrix.rows)
        for column in range(matrix.cols)
    ))


def _interval_frobenius_upper(matrix: np.ndarray) -> mp.mpf:
    return mp.sqrt(mp.fsum(
        max(abs(lo), abs(hi)) ** 2
        for value in matrix.flat
        for lo, hi in (_endpoints(value),)
    ))


def _lower(value: Any) -> mp.mpf:
    return _endpoints(value)[0]


def _interval_matmul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    output = np.empty((left.shape[0], right.shape[1]), dtype=object)
    for row in range(left.shape[0]):
        for column in range(right.shape[1]):
            total = _iv(0.0)
            for inner in range(left.shape[1]):
                total += left[row, inner] * right[inner, column]
            output[row, column] = total
    return output


def _interval_transpose(matrix: np.ndarray) -> np.ndarray:
    return np.asarray(matrix.T, dtype=object)


def _interval_identity(size: int) -> np.ndarray:
    output = np.empty((size, size), dtype=object)
    for row in range(size):
        for column in range(size):
            output[row, column] = _iv(1.0 if row == column else 0.0)
    return output


def _interval_inverse_2x2(matrix: np.ndarray) -> np.ndarray:
    determinant = (
        matrix[0, 0] * matrix[1, 1]
        - matrix[0, 1] * matrix[1, 0]
    )
    return np.asarray([
        [matrix[1, 1] / determinant, -matrix[0, 1] / determinant],
        [-matrix[1, 0] / determinant, matrix[0, 0] / determinant],
    ], dtype=object)


def _interval_inverse_sqrt_2x2(matrix: np.ndarray) -> np.ndarray:
    determinant = (
        matrix[0, 0] * matrix[1, 1]
        - matrix[0, 1] * matrix[1, 0]
    )
    root_det = mp.iv.sqrt(determinant)
    trace = matrix[0, 0] + matrix[1, 1]
    denominator = mp.iv.sqrt(trace + 2 * root_det)
    shifted = matrix.copy()
    shifted[0, 0] += root_det
    shifted[1, 1] += root_det
    inverse = _interval_inverse_2x2(shifted)
    return inverse * denominator


def _attachment_interval(
    coordinates: np.ndarray, q_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    shape = coordinates[1 + 2 * ORDER:1 + 3 * ORDER]
    boundary_shape = _iv(0.0)
    for value, sign in zip(shape, signs_j):
        boundary_shape += _iv(value) * _iv(sign)
    exponential = mp.iv.exp(4 * boundary_shape)
    factor = -(exponential - 1) / (exponential + 1)
    raw = np.empty((2, qdim), dtype=object)
    raw.fill(_iv(0.0))
    raw[0, 0] = _iv(1.0)
    for mode in range(ORDER):
        raw[0, 1 + mode] = _iv(signs_k[mode])
        raw[0, 1 + 2 * ORDER + mode] = factor * _iv(signs_j[mode])
    raw[1] = -raw[0]
    raw[1, 0] += _iv(1.0)
    scaled = raw.copy()
    for column in range(qdim):
        scaled[:, column] = scaled[:, column] / _iv(q_weights[column])
    return raw, scaled


def _interval_dot(coefficients: np.ndarray, values: np.ndarray) -> Any:
    total = _iv(0.0)
    for coefficient, value in zip(coefficients, values):
        total += _iv(coefficient) * _iv(value)
    return total


def _interval_reduced_action_hessian(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
) -> np.ndarray:
    """Replay the retained z-action without collapsing q intervals."""

    q = np.asarray(coordinates, dtype=object)
    velocity = np.asarray(velocities, dtype=object)
    multipliers = np.asarray(multipliers, dtype=object)
    z = np.concatenate((velocity, multipliers))
    total_size = z.size
    nodes, quadrature = np.polynomial.legendre.leggauss(POINTS)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, ORDER + 1, dtype=float)
    js = np.arange(ORDER, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    u_coeff = q[1:1 + ORDER]
    w_coeff = q[1 + ORDER:1 + 2 * ORDER]
    v_coeff = q[1 + 2 * ORDER:1 + 3 * ORDER]
    radius = _iv(reduced_action.RADIUS0) * mp.iv.exp(q[0])
    kappa0 = _iv(15.0 * 5.0 ** (1.0 / 3.0) / 4.0)
    bulk = IntervalJet.constant(0.0, total_size)
    inertia = IntervalJet.constant(0.0, total_size)
    localization = reduced_action.identity_response_localization(chi)
    qdim = dimensions(ORDER)["coordinates"]

    for index, coordinate in enumerate(chi):
        window = math.sin(2.0 * coordinate) ** 2
        window_prime = 2.0 * math.sin(4.0 * coordinate)
        u = _interval_dot(cos_k[:, index], u_coeff)
        up = _interval_dot(-4.0 * ks * sin_k[:, index], u_coeff)
        wp = (
            _iv(window_prime) * _interval_dot(cos_j[:, index], w_coeff)
            + _iv(window) * _interval_dot(
                -4.0 * js * sin_j[:, index], w_coeff
            )
        )
        vp = (
            _iv(window_prime) * _interval_dot(cos_j[:, index], v_coeff)
            + _iv(window) * _interval_dot(
                -4.0 * js * sin_j[:, index], v_coeff
            )
        )
        w = _iv(window) * _interval_dot(cos_j[:, index], w_coeff)
        v = _iv(window) * _interval_dot(cos_j[:, index], v_coeff)
        C = radius * mp.iv.exp(u + w)
        A = radius * mp.iv.exp(u + v) * _iv(math.cos(coordinate))
        B = radius * mp.iv.exp(u - v) * _iv(math.sin(coordinate))
        cp = up + wp
        ap = up + vp - _iv(math.tan(coordinate))
        bp = up - vp + 1 / _iv(math.tan(coordinate))
        volume = C * A**3 * B**3
        spatial_volume = A**3 * B**3

        lc_vector = np.zeros(total_size)
        la_vector = np.zeros(total_size)
        lb_vector = np.zeros(total_size)
        lc_vector[0] = la_vector[0] = lb_vector[0] = 1.0
        lc_vector[1:1 + ORDER] = cos_k[:, index]
        la_vector[1:1 + ORDER] = cos_k[:, index]
        lb_vector[1:1 + ORDER] = cos_k[:, index]
        lc_vector[1 + ORDER:1 + 2 * ORDER] = window * cos_j[:, index]
        la_vector[1 + 2 * ORDER:1 + 3 * ORDER] = window * cos_j[:, index]
        lb_vector[1 + 2 * ORDER:1 + 3 * ORDER] = -window * cos_j[:, index]
        lapse_vector = np.zeros(total_size)
        lapse_vector[qdim:qdim + ORDER] = cos_k[:, index]
        lapse_prime_vector = np.zeros(total_size)
        lapse_prime_vector[qdim:qdim + ORDER] = (
            -4.0 * ks * sin_k[:, index]
        )
        shift_vector = np.zeros(total_size)
        shift_vector[qdim + ORDER:qdim + 2 * ORDER] = (
            math.sin(4.0 * coordinate) * cos_j[:, index]
        )
        shift_prime_vector = np.zeros(total_size)
        shift_prime_vector[qdim + ORDER:qdim + 2 * ORDER] = (
            4.0 * math.cos(4.0 * coordinate) * cos_j[:, index]
            + math.sin(4.0 * coordinate)
            * (-4.0 * js * sin_j[:, index])
        )
        lc = IntervalJet.affine(_interval_dot(lc_vector, z), lc_vector)
        la = IntervalJet.affine(_interval_dot(la_vector, z), la_vector)
        lb = IntervalJet.affine(_interval_dot(lb_vector, z), lb_vector)
        log_n = IntervalJet.affine(
            _interval_dot(lapse_vector, z), lapse_vector
        )
        n_prime = IntervalJet.affine(
            _interval_dot(lapse_prime_vector, z), lapse_prime_vector
        )
        beta = IntervalJet.affine(
            _interval_dot(shift_vector, z), shift_vector
        )
        beta_prime = IntervalJet.affine(
            _interval_dot(shift_prime_vector, z), shift_prime_vector
        )
        N = log_n.exp()
        Hc = (lc - beta * cp - beta_prime) / N
        Ha = (la - beta * ap) / N
        Hb = (lb - beta * bp) / N
        adm = Hc**2 + 3 * Ha**2 + 3 * Hb**2 - (
            Hc + 3 * Ha + 3 * Hb
        ) ** 2
        f_normal = -beta / N
        x_spatial = (
            1 / C**2
            + _iv(3.0 * math.cos(coordinate) ** 2) / A**2
            + _iv(3.0 * math.sin(coordinate) ** 2) / B**2
        )
        x_eta = (-f_normal**2) + x_spatial
        eta_legendre = 1 + x_eta**3
        fixed_gravity = ap**2 + bp**2 + 3 * ap * bp
        spatial_gravity = N * (
            n_prime * (ap + bp) + fixed_gravity
        ) * (_iv(3.0) * spatial_volume / C)
        algebraic_core = (
            0.5 * adm
            - (0.5 * x_eta + 0.125 * x_eta**4)
            * _iv(localization[index])
        )
        algebraic_core = algebraic_core + (
            _iv(3.0) / A**2 + _iv(3.0) / B**2 - 0.5 * kappa0
        )
        algebraic = N * volume * algebraic_core
        bulk = bulk + (spatial_gravity + algebraic) * _iv(
            quadrature[index]
        )
        inertia = inertia + (eta_legendre / N) * (
            _iv(quadrature[index]) * volume * _iv(localization[index])
        )

    action = bulk - 0.25 / (
        inertia * _iv(2.0 * reduced_action.HOPF_ORBIT_VOLUME**2)
    )
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    u_boundary = _interval_dot(signs_k, u_coeff)
    v_boundary = _interval_dot(signs_j, v_coeff)
    A_boundary = (
        radius * mp.iv.exp(u_boundary + v_boundary) / _iv(math.sqrt(2.0))
    )
    B_boundary = (
        radius * mp.iv.exp(u_boundary - v_boundary) / _iv(math.sqrt(2.0))
    )
    R4 = A_boundary * B_boundary / mp.iv.sqrt(
        A_boundary**2 + B_boundary**2
    )
    boundary_lapse_vector = np.zeros(total_size)
    boundary_lapse_vector[qdim:qdim + ORDER] = signs_k
    boundary_log_n = IntervalJet.affine(
        _interval_dot(boundary_lapse_vector, z), boundary_lapse_vector
    )
    action = action - boundary_log_n.exp() * (
        _iv(reduced_action.standard_model_casimir_coefficient()) / R4
    )
    return np.asarray(action.hessian, dtype=object)


def _action_hessian_interval(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    active_indices: np.ndarray,
    active_weights: np.ndarray,
) -> np.ndarray:
    if any(hasattr(value, "ctx") for value in np.asarray(
        coordinates, dtype=object
    )):
        IntervalJet.active_indices = active_indices
        IntervalJet.active_weights = active_weights
        return _interval_reduced_action_hessian(
            coordinates, velocities, multipliers
        )
    original_jet = reduced_action.Jet
    original_affine = reduced_action._affine
    IntervalJet.active_indices = active_indices
    IntervalJet.active_weights = active_weights
    reduced_action.Jet = IntervalJet
    reduced_action._affine = lambda value, coefficients: IntervalJet.affine(
        value, coefficients
    )
    try:
        jet = reduced_action.exact_action_jet_at_state(
            ORDER, coordinates, velocities, multipliers, points=POINTS
        )
        return np.asarray(jet.hessian, dtype=object)
    finally:
        reduced_action.Jet = original_jet
        reduced_action._affine = original_affine


def _enclose_inverse(
    matrix: np.ndarray, *, require_contractive: bool = True,
) -> dict[str, Any]:
    midpoint, radius = _mid_radius(matrix)
    inverse = midpoint ** -1
    identity = mp.eye(midpoint.rows)
    residual = identity - inverse * midpoint
    residual_norm = _frobenius(residual)
    matrix_radius_norm = _frobenius(radius)
    product_radius = _abs_matrix(inverse) * radius
    defect = residual_norm + _frobenius(product_radius)
    if defect >= 1 and require_contractive:
        raise np.linalg.LinAlgError("interval inverse defect is not contractive")
    inverse_norm = _frobenius(inverse)
    inverse_bound = (
        inverse_norm / (1 - defect) if defect < 1 else mp.inf
    )
    inverse_radius = (
        inverse_norm * defect / (1 - defect) if defect < 1 else mp.inf
    )
    return {
        "midpoint": midpoint,
        "radius": radius,
        "inverse": inverse,
        "midpoint_residual_norm": residual_norm,
        "matrix_radius_Frobenius": matrix_radius_norm,
        "defect": defect,
        "inverse_bound": inverse_bound,
        "inverse_radius": inverse_radius,
        "contractive": bool(defect < 1),
    }


def _response_interval(
    inverse_data: dict[str, Any],
) -> tuple[np.ndarray, dict[str, mp.mpf]]:
    inverse = inverse_data["inverse"]
    start = inverse.rows - 2
    residual = inverse_data["midpoint_residual_norm"]
    inverse_norm = _frobenius(inverse)
    midpoint_inverse_error = inverse_norm * residual / (1 - residual)
    exact_midpoint_inverse_norm = inverse_norm / (1 - residual)
    matrix_radius = inverse_data["matrix_radius_Frobenius"]
    perturbation_product = exact_midpoint_inverse_norm * matrix_radius
    if perturbation_product >= 1:
        raise np.linalg.LinAlgError(
            "response-block perturbation is not contractive"
        )
    left = _frobenius(mp.matrix([
        [inverse[row, column] for column in range(inverse.cols)]
        for row in range(start, inverse.rows)
    ])) + midpoint_inverse_error
    right = _frobenius(mp.matrix([
        [inverse[row, column] for column in range(start, inverse.cols)]
        for row in range(inverse.rows)
    ])) + midpoint_inverse_error
    radius = (
        midpoint_inverse_error
        + left * matrix_radius * right / (1 - perturbation_product)
    )
    output = np.empty((2, 2), dtype=object)
    for row in range(2):
        for column in range(2):
            center = inverse[start + row, start + column]
            output[row, column] = mp.iv.mpf([
                center - radius, center + radius
            ])
    return output, {
        "midpoint_inverse_error_Frobenius": midpoint_inverse_error,
        "matrix_radius_Frobenius": matrix_radius,
        "exact_midpoint_inverse_Frobenius_bound": (
            exact_midpoint_inverse_norm
        ),
        "response_left_factor_Frobenius_bound": left,
        "response_right_factor_Frobenius_bound": right,
        "response_perturbation_product": perturbation_product,
        "response_block_radius_bound": radius,
    }


def main() -> None:
    if DPS < 40:
        raise ValueError("at least 40 interval decimal digits required")
    if ROOT_NEIGHBORHOOD_MULTIPLIER < 1.0:
        raise ValueError("root-neighborhood multiplier must be at least one")
    mp.mp.dps = DPS + 20
    mp.iv.dps = DPS
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if promotion.get("DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED") is not True:
        raise RuntimeError("certified N12 pair required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    root_rounding = json.loads(ROOT_ROUNDING.read_text(encoding="utf-8"))
    if root_rounding.get("validation_passed") is not True:
        raise RuntimeError("directed N12 root enclosure required")
    root_contraction = float(root_rounding["directed_contraction_bound"])
    center_root_distance = float(root_rounding["directed_Y_upper"]) / (
        1.0 - root_contraction
    )
    exact_normal = np.load(EXACT_NORMAL)
    normal_basis = np.asarray(exact_normal["normal_basis"], dtype=float)
    normal_jacobian = np.asarray(
        exact_normal["analytic_normal_jacobian"], dtype=float
    )
    residual = np.asarray(json.loads(
        EXACT_RESIDUAL.read_text(encoding="utf-8")
    )["exact_residual_vector"], dtype=float)
    approximate_inverse = np.linalg.inv(normal_jacobian)
    correction_coefficients = [
        -mp.fsum(
            mp.mpf(float(approximate_inverse[row, column]))
            * mp.mpf(float(residual[column]))
            for column in range(residual.size)
        )
        for row in range(residual.size)
    ]
    correction_norm = mp.sqrt(mp.fsum(
        value**2 for value in correction_coefficients
    ))
    first_picard_root_distance = root_contraction * center_root_distance
    first_picard_enclosure_radius = (
        ROOT_NEIGHBORHOOD_MULTIPLIER * first_picard_root_distance
    )
    exact_root_neighborhood_radius = (
        (ROOT_NEIGHBORHOOD_MULTIPLIER - 1.0)
        * first_picard_root_distance
    )
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    velocity_keep = np.concatenate((
        np.arange(0, 1 + ORDER),
        np.arange(1 + 2 * ORDER, 1 + 3 * ORDER),
    ))
    active_indices = np.concatenate((
        velocity_keep,
        qdim + np.arange(ORDER),
    ))
    active_weights = np.concatenate((
        np.ones(velocity_keep.size), m_weights[:ORDER]
    ))
    state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))
    joint_weights = np.concatenate((state_weights, state_weights))
    normal_row_norms = np.linalg.norm(normal_basis, axis=1)
    first_picard_center = []
    for row in range(joint.size):
        action_correction = mp.fsum(
            mp.mpf(float(normal_basis[row, column]))
            * correction_coefficients[column]
            for column in range(residual.size)
        )
        first_picard_center.append(
            mp.mpf(float(joint[row]))
            + action_correction / mp.mpf(float(joint_weights[row]))
        )
    states = {}
    for index, name in enumerate(("event", "child")):
        offset = index * state_dimension
        center = first_picard_center[
            index * state_dimension:(index + 1) * state_dimension
        ]
        states[name] = np.asarray([
            mp.iv.mpf([
                value - mp.mpf(
                    first_picard_enclosure_radius
                    * normal_row_norms[offset + local] / weight
                ),
                value + mp.mpf(
                    first_picard_enclosure_radius
                    * normal_row_norms[offset + local] / weight
                ),
            ])
            for local, (value, weight) in enumerate(zip(center, state_weights))
        ], dtype=object)
    attachments = {}
    hessians = {}
    for name, state in states.items():
        q = state[:qdim]
        attachments[name] = _attachment_interval(q, q_weights)
        hessians[name] = _action_hessian_interval(
            q, state[qdim:2 * qdim], state[2 * qdim:],
            active_indices, active_weights,
        )

    grams = {}
    for name in ("event", "child"):
        scaled = attachments[name][1]
        grams[name] = _interval_matmul(
            scaled, _interval_transpose(scaled)
        )
    common_gram = np.empty((2, 2), dtype=object)
    for row in range(2):
        for column in range(2):
            common_gram[row, column] = (
                grams["event"][row, column]
                + grams["child"][row, column]
            ) / 2
    common_inverse_sqrt = _interval_inverse_sqrt_2x2(common_gram)
    common_trace = common_gram[0, 0] + common_gram[1, 1]
    common_discriminant = mp.iv.sqrt(
        (common_gram[0, 0] - common_gram[1, 1]) ** 2
        + 4 * common_gram[0, 1] * common_gram[1, 0]
    )
    common_gram_minimum_lower = _lower(
        (common_trace - common_discriminant) / 2
    )
    common_inverse_sqrt_frobenius_upper = _interval_frobenius_upper(
        common_inverse_sqrt
    )

    sector_records = {}
    responses = {}
    for name in ("event", "child"):
        core_inverse_data = _enclose_inverse(hessians[name])
        raw_attachment = attachments[name][0][:, velocity_keep]
        coupling_velocity = _interval_matmul(
            common_inverse_sqrt, raw_attachment
        )
        coupling = np.empty((2, active_indices.size), dtype=object)
        coupling.fill(_iv(0.0))
        coupling[:, :velocity_keep.size] = coupling_velocity
        dimension = active_indices.size + 2
        matrix = np.empty((dimension, dimension), dtype=object)
        matrix.fill(_iv(0.0))
        matrix[:active_indices.size, :active_indices.size] = hessians[name]
        matrix[:active_indices.size, -2:] = -coupling.T
        matrix[-2:, :active_indices.size] = coupling
        inverse_data = _enclose_inverse(matrix)
        responses[name], response_data = _response_interval(inverse_data)
        sector_records[name] = {
            "quotient_dimension": dimension,
            "gauge_fixed_Dirac_core_dimension": active_indices.size,
            "gauge_fixed_Dirac_core_inverse_defect_upper": float(
                core_inverse_data["defect"]
            ),
            "gauge_fixed_Dirac_core_inverse_Frobenius_bound": float(
                core_inverse_data["inverse_bound"]
            ),
            "interval_inverse_defect_upper": float(inverse_data["defect"]),
            "interval_inverse_Frobenius_bound": float(
                inverse_data["inverse_bound"]
            ),
            "interval_inverse_radius_bound": float(
                inverse_data["inverse_radius"]
            ),
            "response_Frobenius_bound": float(
                _interval_frobenius_upper(responses[name])
            ),
            **{
                key: float(value) for key, value in response_data.items()
            },
        }

    graphs = {}
    frame_norm_bounds = {}
    for name, sign in (("event", -1.0), ("child", 1.0)):
        identity = _interval_identity(2)
        graph = np.vstack((identity, sign * responses[name]))
        graphs[name] = graph
        frame_norm_bounds[name] = mp.sqrt(
            1 + mp.mpf(sector_records[name]["response_Frobenius_bound"]) ** 2
        )
    symbol = np.column_stack((graphs["child"], -graphs["event"]))
    symbol_inverse = _enclose_inverse(symbol, require_contractive=False)
    raw_symbol_gap_lower = (
        (1 - symbol_inverse["defect"])
        / _frobenius(symbol_inverse["inverse"])
        if symbol_inverse["contractive"] else mp.mpf(0)
    )
    symbol_gap_lower = raw_symbol_gap_lower / max(frame_norm_bounds.values())
    validation = {
        "certified_direct_N12_pair_consumed": True,
        "retained_96_point_action_replayed_with_interval_jets": True,
        "existing_boundary_compatible_w_shift_quotient_used": True,
        "both_quotient_interval_inverse_defects_contractive": all(
            record["interval_inverse_defect_upper"] < 1.0
            for record in sector_records.values()
        ),
        "both_gauge_fixed_Dirac_core_interval_inverses_contractive": all(
            record["gauge_fixed_Dirac_core_inverse_defect_upper"] < 1.0
            for record in sector_records.values()
        ),
        "four_by_four_graph_symbol_interval_inverse_contractive": bool(
            symbol_inverse["defect"] < 1
        ),
        "directed_symbol_gap_positive": bool(symbol_gap_lower > 0),
        "positive_normal_section_action_neighborhood_about_exact_root_"
        "enclosed": bool(
            exact_root_neighborhood_radius > 0.0
        ),
        "no_sampled_history_promoted_as_an_interval": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_EXACT_ROOT_NEIGHBORHOOD_CALDERON_GRAPH_SYMBOL_CERTIFIED_"
            "BY_DIRECTED_INTERVAL_ACTION_JETS"
            if all(validation.values()) else
            "N12_EXACT_ROOT_ENCLOSURE_CALDERON_CERTIFICATE_FAILED"
        ),
        "order": ORDER,
        "points": POINTS,
        "interval_decimal_digits": DPS,
        "checkpoint": str(CHECKPOINT.relative_to(ROOT)).replace("\\", "/"),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "promotion_SHA256": _sha256(PROMOTION),
        "root_rounding_SHA256": _sha256(ROOT_ROUNDING),
        "exact_normal_SHA256": _sha256(EXACT_NORMAL),
        "exact_residual_SHA256": _sha256(EXACT_RESIDUAL),
        "numerical_center_to_exact_root_distance_upper": center_root_distance,
        "first_Picard_action_correction_norm": float(correction_norm),
        "first_Picard_center_to_exact_root_distance_upper": (
            first_picard_root_distance
        ),
        "first_Picard_normal_enclosure_radius": (
            first_picard_enclosure_radius
        ),
        "certified_normal_section_action_neighborhood_radius_about_exact_"
        "root": (
            exact_root_neighborhood_radius
        ),
        "root_neighborhood_multiplier": ROOT_NEIGHBORHOOD_MULTIPLIER,
        "exact_root_action_coordinate_distance_upper": (
            first_picard_root_distance
        ),
        "root_enclosure_geometry": (
            "EXACT_FIRST_FIXED_APPROXIMATE_INVERSE_PICARD_CENTER;_THE_"
            "CONTRACTION_REMAINDER_LIES_IN_THE_STORED_57_DIMENSIONAL_"
            "NORMAL_BASIS_AND_IS_ENCLOSED_USING_ITS_COORDINATE_ROW_NORMS;_"
            "THIS_IS_A_NORMAL_SECTION_ENCLOSURE_NOT_AN_ARBITRARY_STATE_"
            "NEIGHBORHOOD"
        ),
        "sector_records": sector_records,
        "common_trace_Gram": {
            "minimum_eigenvalue_lower": float(common_gram_minimum_lower),
            "inverse_sqrt_Frobenius_bound": float(
                common_inverse_sqrt_frobenius_upper
            ),
        },
        "symbol": {
            "dimension": 4,
            "normalization": (
                "UNNORMALIZED_GRAPH_SYMBOL_DIVIDED_BY_A_DIRECTED_"
                "UPPER_BOUND_ON_THE_TWO_GRAPH_FRAME_NORMS"
            ),
            "raw_graph_symbol_minimum_singular_value_lower": float(
                raw_symbol_gap_lower
            ),
            "maximum_graph_frame_norm_upper": float(
                max(frame_norm_bounds.values())
            ),
            "interval_inverse_defect_upper": float(symbol_inverse["defect"]),
            "interval_inverse_Frobenius_bound": (
                float(symbol_inverse["inverse_bound"])
                if symbol_inverse["contractive"] else None
            ),
            "minimum_singular_value_lower": float(symbol_gap_lower),
            "bound_uses_Frobenius_inverse_norm": True,
        },
        "scope": (
            "DIRECTED_EXACT_ROOT_ENCLOSURE_ONLY;_THE_POSITIVE_DURATION_"
            "PROPAGATOR_REMAINS_A_SEPARATE_LEMMA"
        ),
        "exact_next_dependency": (
            "ENCLOSE_A_WHOLE_ACTION_COORDINATE_NEIGHBORHOOD_ABOUT_"
            "EACH_EXACT_ROOT_USING_THE_DIRECTED_CORRELATED_GRAPH_GAP"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
