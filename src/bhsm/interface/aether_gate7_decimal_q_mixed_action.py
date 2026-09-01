"""Decimal configuration gradient and reduced--configuration action Hessian.

Gate 7 needs a stable selected-line field on a nearly singular event family.
The retained high-precision velocity jet already supplies the reduced
``(velocity,multiplier)`` Hessian.  This module evaluates only the two missing
pieces from the same retained action: ``L_q`` and ``L_(v,m),q``.  It uses the
same 96-point quadrature, boundary Casimir, and local thirteen-variable pullback
as the production action; no new action term or physical datum is introduced.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
import math

import numpy as np

from bhsm.interface.aether_high_precision_velocity_jet import (
    _Jet,
    _basis,
    _d,
    _zero_matrix,
    _zero_vector,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


SparseMap = list[tuple[int, Decimal]]


def _map(values: np.ndarray, *, offset: int = 0) -> SparseMap:
    return [
        (offset + index, _d(value))
        for index, value in enumerate(values)
        if value != 0.0
    ]


def _mapped(
    state: list[Decimal], mapping: SparseMap, constant: Decimal = Decimal(0),
) -> Decimal:
    return constant + sum(state[index] * value for index, value in mapping)


def _accumulate_q_mixed(
    local: _Jet,
    q_maps: list[SparseMap],
    reduced_maps: list[SparseMap],
    gradient_q: list[Decimal],
    gradient_reduced: list[Decimal],
    mixed_reduced_q: list[list[Decimal]],
) -> None:
    for local_index, mapping in enumerate(q_maps):
        coefficient = local.gradient[local_index]
        for index, value in mapping:
            gradient_q[index] += coefficient * value
    for local_index, mapping in enumerate(reduced_maps):
        coefficient = local.gradient[local_index]
        for index, value in mapping:
            gradient_reduced[index] += coefficient * value
    for left_index, reduced_mapping in enumerate(reduced_maps):
        if not reduced_mapping:
            continue
        for right_index, q_mapping in enumerate(q_maps):
            coefficient = local.hessian[left_index][right_index]
            if coefficient == 0 or not q_mapping:
                continue
            for row, left_value in reduced_mapping:
                scaled = coefficient * left_value
                for column, right_value in q_mapping:
                    mixed_reduced_q[row][column] += scaled * right_value


def decimal_q_gradient_and_reduced_q_hessian(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
    precision: int = 60,
) -> dict[str, object]:
    """Return Decimal ``L_q`` and ``L_(v,m),q`` for the retained action."""

    if precision < 34:
        raise ValueError("Decimal Gate-7 action blocks need at least 34 digits")
    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    reduced_dim = qdim + mdim
    q_raw = np.asarray(coordinates, dtype=float)
    v_raw = np.asarray(velocities, dtype=float)
    m_raw = np.asarray(multipliers, dtype=float)
    if q_raw.shape != (qdim,) or v_raw.shape != (qdim,) or m_raw.shape != (mdim,):
        raise ValueError("state dimensions do not match order")

    basis = _basis(order, points)
    with localcontext() as context:
        context.prec = precision
        q = [_d(value) for value in q_raw]
        reduced_state = [
            *[_d(value) for value in v_raw],
            *[_d(value) for value in m_raw],
        ]
        bulk_value = Decimal(0)
        inertia_value = Decimal(0)
        bulk_q = _zero_vector(qdim)
        bulk_r = _zero_vector(reduced_dim)
        bulk_rq = _zero_matrix(reduced_dim, qdim)
        inertia_q = _zero_vector(qdim)
        inertia_r = _zero_vector(reduced_dim)
        inertia_rq = _zero_matrix(reduced_dim, qdim)
        ks = basis["ks"]
        js = basis["js"]

        for node, coordinate in enumerate(basis["chi"]):
            cos_k = basis["cos_k"][:, node]
            sin_k = basis["sin_k"][:, node]
            cos_j = basis["cos_j"][:, node]
            sin_j = basis["sin_j"][:, node]
            window = math.sin(2.0 * coordinate) ** 2
            window_prime = 2.0 * math.sin(4.0 * coordinate)

            log_c = np.zeros(qdim)
            log_a = np.zeros(qdim)
            log_b = np.zeros(qdim)
            log_c[0] = log_a[0] = log_b[0] = 1.0
            log_c[1:1 + order] = cos_k
            log_a[1:1 + order] = cos_k
            log_b[1:1 + order] = cos_k
            log_c[1 + order:1 + 2 * order] = window * cos_j
            log_a[1 + 2 * order:1 + 3 * order] = window * cos_j
            log_b[1 + 2 * order:1 + 3 * order] = -window * cos_j

            up = np.zeros(qdim)
            cp = np.zeros(qdim)
            ap = np.zeros(qdim)
            bp = np.zeros(qdim)
            up[1:1 + order] = -4.0 * ks * sin_k
            shape_prime = window_prime * cos_j + window * (-4.0 * js * sin_j)
            cp[:] = up
            cp[1 + order:1 + 2 * order] = shape_prime
            ap[:] = up
            ap[1 + 2 * order:1 + 3 * order] = shape_prime
            bp[:] = up
            bp[1 + 2 * order:1 + 3 * order] = -shape_prime

            lc = np.zeros(qdim)
            la = np.zeros(qdim)
            lb = np.zeros(qdim)
            lc[0] = la[0] = lb[0] = 1.0
            lc[1:1 + order] = cos_k
            la[1:1 + order] = cos_k
            lb[1:1 + order] = cos_k
            lc[1 + order:1 + 2 * order] = window * cos_j
            la[1 + 2 * order:1 + 3 * order] = window * cos_j
            lb[1 + 2 * order:1 + 3 * order] = -window * cos_j

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

            q_maps = [
                _map(log_c), _map(log_a), _map(log_b),
                _map(cp), _map(ap), _map(bp),
                [], [], [], [], [], [], [],
            ]
            reduced_maps = [
                [], [], [], [], [], [],
                _map(lc), _map(la), _map(lb),
                _map(log_n, offset=qdim),
                _map(n_prime, offset=qdim),
                _map(beta, offset=qdim),
                _map(beta_prime, offset=qdim),
            ]
            constants = [
                _d(math.log(RADIUS0)),
                _d(math.log(RADIUS0 * math.cos(coordinate))),
                _d(math.log(RADIUS0 * math.sin(coordinate))),
                Decimal(0), -_d(math.tan(coordinate)),
                _d(1.0 / math.tan(coordinate)),
                Decimal(0), Decimal(0), Decimal(0), Decimal(0),
                Decimal(0), Decimal(0), Decimal(0),
            ]
            values = [
                _mapped(q, q_map, constant)
                + _mapped(reduced_state, reduced_map)
                for q_map, reduced_map, constant in zip(
                    q_maps, reduced_maps, constants, strict=True,
                )
            ]
            variables = [
                _Jet.variable(value, index, 13)
                for index, value in enumerate(values)
            ]
            (
                log_c_j, log_a_j, log_b_j, cp_j, ap_j, bp_j,
                lc_j, la_j, lb_j, log_n_j, n_prime_j, beta_j,
                beta_prime_j,
            ) = variables
            c_radius = log_c_j.exp()
            a_radius = log_a_j.exp()
            b_radius = log_b_j.exp()
            lapse = log_n_j.exp()
            hc = (lc_j - beta_j * cp_j - beta_prime_j) / lapse
            ha = (la_j - beta_j * ap_j) / lapse
            hb = (lb_j - beta_j * bp_j) / lapse
            adm = (
                hc**2 + _d(3.0) * ha**2 + _d(3.0) * hb**2
                - (hc + _d(3.0) * ha + _d(3.0) * hb)**2
            )
            f_normal = -beta_j / lapse
            x_spatial = (
                Decimal(1) / c_radius**2
                + _d(3.0 * math.cos(coordinate) ** 2) / a_radius**2
                + _d(3.0 * math.sin(coordinate) ** 2) / b_radius**2
            )
            x_eta = x_spatial - f_normal**2
            eta = Decimal(1) + x_eta**3
            fixed_gravity = ap_j**2 + bp_j**2 + _d(3.0) * ap_j * bp_j
            volume = c_radius * a_radius**3 * b_radius**3
            spatial_volume = a_radius**3 * b_radius**3
            spatial_gravity = (
                _d(3.0) * spatial_volume / c_radius * lapse
                * (n_prime_j * (ap_j + bp_j) + fixed_gravity)
            )
            sigma = (
                _d(-0.5) + _d(2.0 * coordinate / math.pi)
                - _d(math.sin(4.0 * coordinate) / (2.0 * math.pi))
            )
            localization = Decimal(1) - _d(4.0) * sigma**2
            kappa0 = _d(15.0 * 5.0 ** (1.0 / 3.0) / 4.0)
            algebraic = lapse * volume * (
                _d(3.0) / a_radius**2 + _d(3.0) / b_radius**2
                - _d(0.5) * kappa0
                - localization * (_d(0.5) * x_eta + _d(0.125) * x_eta**4)
                + _d(0.5) * adm
            )
            quadrature = _d(basis["quadrature"][node])
            local_bulk = quadrature * (spatial_gravity + algebraic)
            local_inertia = quadrature * volume * localization * eta / lapse
            bulk_value += local_bulk.value
            inertia_value += local_inertia.value
            _accumulate_q_mixed(
                local_bulk, q_maps, reduced_maps, bulk_q, bulk_r, bulk_rq,
            )
            _accumulate_q_mixed(
                local_inertia, q_maps, reduced_maps,
                inertia_q, inertia_r, inertia_rq,
            )

        coefficient = _d(0.25 / (2.0 * HOPF_ORBIT_VOLUME**2))
        inertia2 = inertia_value**2
        inertia3 = inertia_value**3
        gradient_q = [
            bulk_q[column] + coefficient * inertia_q[column] / inertia2
            for column in range(qdim)
        ]
        mixed = [[
            bulk_rq[row][column] + coefficient * (
                inertia_rq[row][column] / inertia2
                - _d(2.0) * inertia_r[row] * inertia_q[column] / inertia3
            )
            for column in range(qdim)
        ] for row in range(reduced_dim)]

        signs_k = (-1.0) ** np.arange(1, order + 1)
        signs_j = (-1.0) ** np.arange(order)
        log_a_boundary = np.zeros(qdim)
        log_b_boundary = np.zeros(qdim)
        log_a_boundary[0] = log_b_boundary[0] = 1.0
        log_a_boundary[1:1 + order] = signs_k
        log_b_boundary[1:1 + order] = signs_k
        log_a_boundary[1 + 2 * order:1 + 3 * order] = signs_j
        log_b_boundary[1 + 2 * order:1 + 3 * order] = -signs_j
        boundary_lapse = np.zeros(mdim)
        boundary_lapse[:order] = signs_k
        q_maps = [_map(log_a_boundary), _map(log_b_boundary), []]
        reduced_maps = [[], [], _map(boundary_lapse, offset=qdim)]
        values = [
            _mapped(q, q_maps[0], _d(math.log(RADIUS0))),
            _mapped(q, q_maps[1], _d(math.log(RADIUS0))),
            _mapped(reduced_state, reduced_maps[2]),
        ]
        log_a_j, log_b_j, log_n_j = [
            _Jet.variable(value, index, 3) for index, value in enumerate(values)
        ]
        a_boundary = log_a_j.exp() / _d(math.sqrt(2.0))
        b_boundary = log_b_j.exp() / _d(math.sqrt(2.0))
        square = a_boundary**2 + b_boundary**2
        root_value = square.value.sqrt()
        root = _Jet(
            root_value,
            [item / (_d(2.0) * root_value) for item in square.gradient],
            [[
                square.hessian[i][j] / (_d(2.0) * root_value)
                - square.gradient[i] * square.gradient[j]
                / (_d(4.0) * root_value**3)
                for j in range(3)
            ] for i in range(3)],
        )
        boundary = (
            -_d(standard_model_casimir_coefficient())
            * log_n_j.exp() / (a_boundary * b_boundary / root)
        )
        zero_q = _zero_vector(qdim)
        zero_r = _zero_vector(reduced_dim)
        zero_rq = _zero_matrix(reduced_dim, qdim)
        _accumulate_q_mixed(
            boundary, q_maps, reduced_maps, zero_q, zero_r, zero_rq,
        )
        for column in range(qdim):
            gradient_q[column] += zero_q[column]
        for row in range(reduced_dim):
            for column in range(qdim):
                mixed[row][column] += zero_rq[row][column]

        return {
            "gradient_configuration": gradient_q,
            "hessian_reduced_configuration": mixed,
            "precision": precision,
            "points": points,
            "unchanged_retained_action": True,
        }


__all__ = ["decimal_q_gradient_and_reduced_q_hessian"]
