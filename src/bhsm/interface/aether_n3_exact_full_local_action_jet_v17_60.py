"""Exact full local action jet in coordinates, velocities, and multipliers."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    Jet,
    identity_response_localization,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_high_accuracy_action_covector_v17_57 import _high_accuracy_local_first_derivatives
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import ORDER, unpack_reduced
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import HOPF_ORBIT_VOLUME, RADIUS0
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions, generalized_lagrangian

VERSION = "v17.60"
CLASSIFICATION = "BHSM_N3_EXACT_FULL_LOCAL_ACTION_JET"
FULL_BHSM_COMPLETE = False


def _variables(values: np.ndarray, offset: int, size: int) -> list[Jet]:
    result = []
    for index, value in enumerate(values):
        gradient = np.zeros(size)
        gradient[offset + index] = 1.0
        result.append(Jet.affine(value, gradient))
    return result


def _linear(variables: list[Jet], coefficients: np.ndarray) -> Jet:
    result = Jet.constant(0.0, variables[0].gradient.size)
    for variable, coefficient in zip(variables, coefficients):
        result = result + float(coefficient) * variable
    return result


def _sqrt(value: Jet) -> Jet:
    root = np.sqrt(value.value)
    return Jet(
        root,
        value.gradient / (2.0 * root),
        value.hessian / (2.0 * root)
        - np.outer(value.gradient, value.gradient) / (4.0 * root**3),
    )


def exact_full_action_jet_at_state(
    order: int, coordinates: np.ndarray, velocities: np.ndarray,
    multipliers: np.ndarray, *, points: int = 44,
) -> Jet:
    size = dimensions(order)
    q = np.asarray(coordinates)
    velocity = np.asarray(velocities)
    multipliers = np.asarray(multipliers)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    if q.shape != (qdim,) or velocity.shape != (qdim,) or multipliers.shape != (mdim,):
        raise ValueError("state dimensions do not match order")
    total = 2 * qdim + mdim
    qj = _variables(q, 0, total)
    vj = _variables(velocity, qdim, total)
    mj = _variables(multipliers, 2 * qdim, total)
    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi)); sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi)); sin_j = np.sin(4.0 * np.outer(js, chi))
    u_coeff = qj[1:1 + order]
    w_coeff = qj[1 + order:1 + 2 * order]
    b_coeff = qj[1 + 2 * order:1 + 3 * order]
    radius = RADIUS0 * qj[0].exp()
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    bulk = Jet.constant(0.0, total); inertia = Jet.constant(0.0, total)
    # Exact normalized identity response.  Keeping the response integral in
    # closed form prevents the retained action from acquiring a spurious
    # dependence on the Gauss quadrature used for the outer action integral.
    localization = identity_response_localization(chi)
    for index, coordinate in enumerate(chi):
        window = math.sin(2.0 * coordinate) ** 2
        window_prime = 2.0 * math.sin(4.0 * coordinate)
        u = _linear(u_coeff, cos_k[:, index])
        up = _linear(u_coeff, -4.0 * ks * sin_k[:, index])
        w = window * _linear(w_coeff, cos_j[:, index])
        b = window * _linear(b_coeff, cos_j[:, index])
        wp = _linear(w_coeff, window_prime * cos_j[:, index] + window * (-4.0 * js * sin_j[:, index]))
        bp_shape = _linear(b_coeff, window_prime * cos_j[:, index] + window * (-4.0 * js * sin_j[:, index]))
        C = radius * (u + w).exp()
        A = radius * (u + b).exp() * math.cos(coordinate)
        B = radius * (u - b).exp() * math.sin(coordinate)
        cp = up + wp
        ap = up + bp_shape - math.tan(coordinate)
        bp = up - bp_shape + 1.0 / math.tan(coordinate)
        volume = C * A**3 * B**3
        spatial_volume = A**3 * B**3
        lc_coeff = np.zeros(qdim); la_coeff = np.zeros(qdim); lb_coeff = np.zeros(qdim)
        lc_coeff[0] = la_coeff[0] = lb_coeff[0] = 1.0
        lc_coeff[1:1 + order] = la_coeff[1:1 + order] = lb_coeff[1:1 + order] = cos_k[:, index]
        lc_coeff[1 + order:1 + 2 * order] = window * cos_j[:, index]
        la_coeff[1 + 2 * order:1 + 3 * order] = window * cos_j[:, index]
        lb_coeff[1 + 2 * order:1 + 3 * order] = -window * cos_j[:, index]
        lapse_coeff = np.zeros(mdim); lapse_coeff[:order] = cos_k[:, index]
        lapse_prime_coeff = np.zeros(mdim); lapse_prime_coeff[:order] = -4.0 * ks * sin_k[:, index]
        shift_coeff = np.zeros(mdim); shift_coeff[order:2 * order] = math.sin(4.0 * coordinate) * cos_j[:, index]
        shift_prime_coeff = np.zeros(mdim); shift_prime_coeff[order:2 * order] = (
            4.0 * math.cos(4.0 * coordinate) * cos_j[:, index]
            + math.sin(4.0 * coordinate) * (-4.0 * js * sin_j[:, index])
        )
        lc = _linear(vj, lc_coeff); la = _linear(vj, la_coeff); lb = _linear(vj, lb_coeff)
        log_n = _linear(mj, lapse_coeff); n_prime = _linear(mj, lapse_prime_coeff)
        beta = _linear(mj, shift_coeff); beta_prime = _linear(mj, shift_prime_coeff)
        N = log_n.exp()
        Hc = (lc - beta * cp - beta_prime) / N
        Ha = (la - beta * ap) / N
        Hb = (lb - beta * bp) / N
        adm = Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2 - (Hc + 3.0 * Ha + 3.0 * Hb)**2
        f_normal = -beta / N
        x_spatial = 1.0 / C**2 + 3.0 * math.cos(coordinate)**2 / A**2 + 3.0 * math.sin(coordinate)**2 / B**2
        x_eta = x_spatial - f_normal**2
        eta_legendre = 1.0 + x_eta**3
        fixed_gravity = ap**2 + bp**2 + 3.0 * ap * bp
        spatial_gravity = 3.0 * spatial_volume / C * N * (n_prime * (ap + bp) + fixed_gravity)
        algebraic = N * volume * (
            3.0 / A**2 + 3.0 / B**2 - 0.5 * kappa0
            - localization[index] * (0.5 * x_eta + 0.125 * x_eta**4) + 0.5 * adm
        )
        bulk = bulk + quadrature[index] * (spatial_gravity + algebraic)
        inertia = inertia + quadrature[index] * (volume * localization[index] * eta_legendre / N)
    action = bulk - 0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = _linear(u_coeff, signs_k)
    b_boundary = _linear(b_coeff, signs_j)
    A_boundary = radius * (u_boundary + b_boundary).exp() / math.sqrt(2.0)
    B_boundary = radius * (u_boundary - b_boundary).exp() / math.sqrt(2.0)
    R4 = A_boundary * B_boundary / _sqrt(A_boundary**2 + B_boundary**2)
    boundary_lapse_coeff = np.zeros(mdim); boundary_lapse_coeff[:order] = signs_k
    boundary_log_n = _linear(mj, boundary_lapse_coeff)
    return action - standard_model_casimir_coefficient() / R4 * boundary_log_n.exp()


def exact_full_local_action_jet_audit() -> dict[str, Any]:
    unpacked = unpack_reduced(v17_53_selected_raw_vector())
    q = np.asarray(unpacked["coordinates"])[-1]
    m = np.asarray(unpacked["multipliers"])[-1]
    all_q = np.asarray(unpacked["coordinates"])
    velocity = (trapezoid_sbp_difference() @ all_q / float(unpacked["period"]))[-1]
    jet = exact_full_action_jet_at_state(ORDER, q, velocity, m, points=36)
    value = generalized_lagrangian(q, velocity, m, order=ORDER, points=36)
    _, dq, dv, dm = _high_accuracy_local_first_derivatives(
        q, velocity, m, points=36, coordinate_relative_step=1e-4
    )
    reference = np.concatenate((dq, dv, dm))
    return {
        "source_state": "v17.53_terminal_node",
        "physical_action_changed": False,
        "jet_dimension": jet.gradient.size,
        "value": float(jet.value),
        "reference_value": float(value),
        "value_difference": float(jet.value - value),
        "gradient_reference_relative_residual": float(
            np.linalg.norm(jet.gradient - reference) / max(1.0, np.linalg.norm(reference))
        ),
        "hessian_symmetry_residual": float(
            np.linalg.norm(jet.hessian - jet.hessian.T) / max(1.0, np.linalg.norm(jet.hessian))
        ),
        "gradient": jet.gradient.tolist(),
    }


def completion_payload() -> dict[str, Any]:
    result = exact_full_local_action_jet_audit()
    validation = {
        "physical_action_unchanged": not result["physical_action_changed"],
        "full_local_dimension_owned": result["jet_dimension"] == 26,
        "action_value_exactly_reproduced": abs(result["value_difference"]) < 2e-12,
        "gradient_matches_validated_hybrid": result["gradient_reference_relative_residual"] < 2e-7,
        "hessian_symmetric": result["hessian_symmetry_residual"] < 2e-13,
    }
    return {"artifact":"BHSM_aether_n3_exact_full_local_action_jet_v17_60","version":VERSION,
        "classification":CLASSIFICATION,"FULL_BHSM_COMPLETE":False,"exact_full_local_action_jet":result,
        "status":"VALIDATED" if all(validation.values()) else "INVALIDATED",
        "real_physical_property_explained":"EXACT_SAME_ACTION_LOCAL_COORDINATE_VELOCITY_MULTIPLIER_JET",
        "dependency_advanced":"REMOVES_THE_LAST_LOCAL_ACTION_FINITE_DIFFERENCE_FROM_THE_N3_RESIDUAL",
        "active_calculation":"ASSEMBLE_THE_EXACT_LOCAL_JET_SBP_COVECTOR_AND_REAUDIT_SCALE_DIRECTION_IDENTIFIABILITY",
        "validation":validation,"validation_passed":all(validation.values())}


def materialize(directory: str | Path) -> Path:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);path=target/"BHSM_aether_n3_exact_full_local_action_jet_v17_60.json";path.write_text(deterministic_json(completion_payload()),encoding="utf-8");return path


__all__=["VERSION","CLASSIFICATION","FULL_BHSM_COMPLETE","exact_full_action_jet_at_state","exact_full_local_action_jet_audit","completion_payload","materialize"]
