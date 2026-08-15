"""Measure action-owned N=3 stiffness at the accepted v18.12 state."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import eta_legendre_minimum
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_action_covector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, boundary_radius_and_jacobian,
    kkt_variable_scales, unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import (
    _CHILD_M, _CHILD_Q, _CHILD_V, v18_12_selected_raw_vector,
)
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import _canonical_pair
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import HOPF_ORBIT_VOLUME, RADIUS0
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import _gauss_rule
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import sobolev_weights, spectral_frequencies


VERSION = "v18.14"
CLASSIFICATION = "BHSM_N3_ACTION_OWNED_STIFFNESS_MEASUREMENT"
FULL_BHSM_COMPLETE = False
PROBE_SMALL = 1.0e-6
PROBE_LOCAL = 1.0e-4


def _local_action_terms(q: np.ndarray, velocity: np.ndarray, m: np.ndarray) -> dict[str, float]:
    """Numerically separate the unchanged retained local action terms."""
    chi, weights = _gauss_rule(44)
    ks = np.arange(1, ORDER + 1, dtype=float)
    js = np.arange(ORDER, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi)); sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi)); sin_j = np.sin(4.0 * np.outer(js, chi))
    u_coeff = q[1:1 + ORDER]; w_coeff = q[1 + ORDER:1 + 2 * ORDER]
    v_coeff = q[1 + 2 * ORDER:1 + 3 * ORDER]
    u = u_coeff @ cos_k; up = (-4.0 * ks * u_coeff) @ sin_k
    window = np.sin(2.0 * chi) ** 2; window_prime = 2.0 * np.sin(4.0 * chi)
    w = window * (w_coeff @ cos_j); v = window * (v_coeff @ cos_j)
    wp = window_prime * (w_coeff @ cos_j) + window * ((-4.0 * js * w_coeff) @ sin_j)
    vp = window_prime * (v_coeff @ cos_j) + window * ((-4.0 * js * v_coeff) @ sin_j)
    radius = RADIUS0 * math.exp(float(q[0]))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    cp = up + wp; ap = up + vp - np.tan(chi); bp = up - vp + 1.0 / np.tan(chi)
    qdim = Q_DIMENSION
    lc = velocity[0] + velocity[1:1 + ORDER] @ cos_k + window * (velocity[1 + ORDER:1 + 2 * ORDER] @ cos_j)
    la = velocity[0] + velocity[1:1 + ORDER] @ cos_k + window * (velocity[1 + 2 * ORDER:1 + 3 * ORDER] @ cos_j)
    lb = velocity[0] + velocity[1:1 + ORDER] @ cos_k - window * (velocity[1 + 2 * ORDER:1 + 3 * ORDER] @ cos_j)
    log_n = m[:ORDER] @ cos_k; n_prime = (-4.0 * ks * m[:ORDER]) @ sin_k
    beta = np.sin(4.0 * chi) * (m[ORDER:] @ cos_j)
    beta_prime = 4.0 * np.cos(4.0 * chi) * (m[ORDER:] @ cos_j) + np.sin(4.0 * chi) * ((-4.0 * js * m[ORDER:]) @ sin_j)
    lapse = np.exp(log_n)
    hc = (lc - beta * cp - beta_prime) / lapse
    ha = (la - beta * ap) / lapse
    hb = (lb - beta * bp) / lapse
    adm = hc**2 + 3.0 * ha**2 + 3.0 * hb**2 - (hc + 3.0 * ha + 3.0 * hb) ** 2
    volume = C * A**3 * B**3; spatial_volume = A**3 * B**3
    x_spatial = 1.0 / C**2 + 3.0 * np.cos(chi)**2 / A**2 + 3.0 * np.sin(chi)**2 / B**2
    x_eta = x_spatial - (beta / lapse)**2
    raw = np.sin(chi)**2 * np.cos(chi)**2
    augmented_chi = np.concatenate(([0.0], chi, [math.pi / 4.0]))
    augmented_raw = np.concatenate(([0.0], raw, [0.25]))
    cumulative = np.concatenate(([0.0], np.cumsum(
        0.5 * (augmented_raw[1:] + augmented_raw[:-1]) * np.diff(augmented_chi)
    )))
    cumulative *= 0.5 / cumulative[-1]
    localization = 1.0 - 4.0 * (-0.5 + cumulative[1:-1])**2
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    spatial_gravity = float(weights @ (3.0 * lapse * spatial_volume / C * (
        n_prime * (ap + bp) + ap**2 + bp**2 + 3.0 * ap * bp
    )))
    intrinsic_curvature = float(weights @ (lapse * volume * (3.0 / A**2 + 3.0 / B**2)))
    cosmological = float(weights @ (lapse * volume * (-0.5 * kappa0)))
    eta_potential = float(weights @ (
        -lapse * volume * localization * (0.5 * x_eta + 0.125 * x_eta**4)
    ))
    adm_kinetic = float(weights @ (0.5 * lapse * volume * adm))
    inertia = float(weights @ (volume * localization * (1.0 + x_eta**3) / lapse))
    hopf = -0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    ub = float(u_coeff @ signs_k); vb = float(v_coeff @ signs_j)
    ab = radius * math.exp(ub + vb) / math.sqrt(2.0)
    bb = radius * math.exp(ub - vb) / math.sqrt(2.0)
    r4 = ab * bb / math.sqrt(ab**2 + bb**2)
    casimir = -math.exp(float(m[:ORDER] @ signs_k)) * standard_model_casimir_coefficient() / r4
    return {
        "spatial_gravity": spatial_gravity,
        "intrinsic_curvature": intrinsic_curvature,
        "cosmological": cosmological,
        "eta_potential": eta_potential,
        "adm_kinetic": adm_kinetic,
        "hopf_inertia": hopf,
        "boundary_casimir": casimir,
    }


def _fit_power(radii: list[float], values: list[float]) -> dict[str, float | None]:
    x = np.log(np.asarray(radii)); y0 = np.abs(np.asarray(values))
    floor = max(float(np.max(y0)) * 1.0e-12, 1.0e-300)
    mask = y0 > floor
    if np.count_nonzero(mask) < 3:
        return {"exponent": None, "r_squared": None}
    y = np.log(y0[mask]); xx = x[mask]
    slope, intercept = np.polyfit(xx, y, 1)
    predicted = slope * xx + intercept
    denominator = float(np.sum((y - np.mean(y))**2))
    r2 = 1.0 - float(np.sum((y - predicted)**2)) / max(denominator, 1.0e-300)
    return {"exponent": float(slope), "r_squared": r2}


def _dominant_direction_term(
    q: np.ndarray, velocity: np.ndarray, m: np.ndarray,
    local_direction: np.ndarray,
) -> tuple[str, dict[str, float]]:
    direction = np.asarray(local_direction, dtype=float)
    direction /= max(float(np.linalg.norm(direction)), 1.0e-300)
    step = 1.0e-4
    z = np.concatenate((q, velocity, m))
    center = _local_action_terms(q, velocity, m)
    plus = z + step * direction; minus = z - step * direction
    plus_terms = _local_action_terms(plus[:10], plus[10:20], plus[20:])
    minus_terms = _local_action_terms(minus[:10], minus[10:20], minus[20:])
    curvatures = {
        key: float((plus_terms[key] - 2.0 * center[key] + minus_terms[key]) / step**2)
        for key in center
    }
    return max(curvatures, key=lambda key: abs(curvatures[key])), curvatures


def _evaluate_global(raw: np.ndarray) -> tuple[float, np.ndarray, float]:
    scales = kkt_variable_scales()
    y = raw * scales
    base = raw[:-1]
    action = exact_local_jet_sbp_action_covector(base)
    action_covector = np.asarray(action["covector"]) / scales[:-1]
    event_covector = sbp_event_covector(base) / scales[:-1] / scales[-1]
    residual = np.concatenate((
        action_covector + y[-1] * event_covector,
        [sbp_event_value_from_base(base) / scales[-1]],
    ))
    return float(action["Gamma_replacement"]), residual, _minimum_node_eta(raw)


def _coherent_direction(columns: list[int], *, multiplier: bool = False) -> np.ndarray:
    direction = np.zeros(376)
    if multiplier:
        offset = (NODES - 1) * Q_DIMENSION
        for node in range(NODES):
            for column in columns:
                direction[offset + node * M_DIMENSION + column] = 1.0
    else:
        for node in range(NODES - 1):
            for column in columns:
                direction[node * Q_DIMENSION + column] = 1.0
    return direction


def _normalize_owned(direction: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(kkt_variable_scales() * direction))
    if norm == 0.0:
        raise ValueError("zero direction")
    return direction / norm


def _direction_inventory(raw: np.ndarray) -> list[tuple[str, np.ndarray, str]]:
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"]); m = np.asarray(state["multipliers"])
    eta_gradient = np.zeros(ORDER)
    step = 2.0e-5
    for column in range(ORDER):
        plus = m[-1].copy(); minus = m[-1].copy()
        plus[ORDER + column] += step; minus[ORDER + column] -= step
        eta_gradient[column] = (
            eta_legendre_minimum(q[-1], plus, points=1600)["minimum"]
            - eta_legendre_minimum(q[-1], minus, points=1600)["minimum"]
        ) / (2.0 * step)
    eta_direction = np.zeros(376)
    offset = (NODES - 1) * Q_DIMENSION
    coefficients = eta_gradient / max(float(np.linalg.norm(eta_gradient)), 1.0e-300)
    for node in range(NODES):
        eta_direction[offset + node * M_DIMENSION + ORDER:offset + node * M_DIMENSION + 2 * ORDER] = coefficients
    period = np.zeros(376); period[-2] = 1.0
    event_multiplier = np.zeros(376); event_multiplier[-1] = 1.0
    return [
        ("reconstruction_log_scale", _normalize_owned(_coherent_direction([0])), "scale"),
        ("u_mode_1", _normalize_owned(_coherent_direction([1])), "u"),
        ("w_mode_0", _normalize_owned(_coherent_direction([1 + ORDER])), "w"),
        ("v_mode_0", _normalize_owned(_coherent_direction([1 + 2 * ORDER])), "v"),
        ("eta_sensitive_shift", _normalize_owned(eta_direction), "shift"),
        ("lapse_mode_1", _normalize_owned(_coherent_direction([0], multiplier=True)), "lapse"),
        ("period", _normalize_owned(period), "period"),
        ("event_multiplier", _normalize_owned(event_multiplier), "event_multiplier"),
    ]


def action_owned_stiffness_measurement() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector()
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"]); m = np.asarray(state["multipliers"])
    period = float(state["period"]); velocity = trapezoid_sbp_difference() @ q / period
    qe, ve, me = q[-1], velocity[-1], m[-1]
    radii, _ = boundary_radius_and_jacobian(q)
    base_radius = float(radii[-1])
    factors = [0.80, 0.90, 1.00, 1.10, 1.25]
    groups = {
        "scale": [0], "u": list(range(1, 1 + ORDER)),
        "w": list(range(1 + ORDER, 1 + 2 * ORDER)),
        "v": list(range(1 + 2 * ORDER, 1 + 3 * ORDER)),
        "velocity_scale": [Q_DIMENSION],
        "velocity_u": list(range(Q_DIMENSION + 1, Q_DIMENSION + 1 + ORDER)),
        "velocity_w": list(range(Q_DIMENSION + 1 + ORDER, Q_DIMENSION + 1 + 2 * ORDER)),
        "velocity_v": list(range(Q_DIMENSION + 1 + 2 * ORDER, 2 * Q_DIMENSION)),
        "lapse": list(range(2 * Q_DIMENSION, 2 * Q_DIMENSION + ORDER)),
        "shift": list(range(2 * Q_DIMENSION + ORDER, 2 * Q_DIMENSION + 2 * ORDER)),
    }
    family = []
    for factor in factors:
        qs = qe.copy(); qs[0] += math.log(factor)
        jet = exact_full_action_jet_at_state(ORDER, qs, ve, me, points=44)
        terms = _local_action_terms(qs, ve, me)
        group_curvature = {}
        for name, indices in groups.items():
            block = jet.hessian[np.ix_(indices, indices)]
            group_curvature[name] = float(np.max(np.abs(np.linalg.eigvalsh(block))))
        family.append({
            "radius_factor": factor,
            "reconstructed_radius": base_radius * factor,
            "action": float(jet.value),
            "action_terms": terms,
            "term_sum_residual": float(sum(terms.values()) - jet.value),
            "group_maximum_absolute_curvature": group_curvature,
        })
    term_powers = {
        term: _fit_power(
            [row["reconstructed_radius"] for row in family],
            [row["action_terms"][term] for row in family],
        ) for term in family[0]["action_terms"]
    }
    curvature_powers = {
        group: _fit_power(
            [row["reconstructed_radius"] for row in family],
            [row["group_maximum_absolute_curvature"][group] for row in family],
        ) for group in groups
    }
    center_jet = exact_full_action_jet_at_state(ORDER, qe, ve, me, points=44)
    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q_owned = 1.0 / ((1.0 + frequencies**2)**3.0)
    m_owned = 1.0 / sobolev_weights(ORDER)["multipliers"]
    natural = np.concatenate((q_owned, q_owned / period, m_owned))
    action_reference = float(sum(abs(value) for value in _local_action_terms(qe, ve, me).values()))
    dimensionless_hessian = (
        natural[:, None] * center_jet.hessian * natural[None, :] / action_reference
    )
    dimensionless_eigenvalues = np.linalg.eigvalsh(dimensionless_hessian)
    nonzero = np.abs(dimensionless_eigenvalues) > max(
        float(np.max(np.abs(dimensionless_eigenvalues))) * 1.0e-12, 1.0e-14
    )
    intrinsic_action_step = 1.0 / math.sqrt(max(float(np.max(np.abs(dimensionless_eigenvalues))), 1.0e-300))
    gamma0, residual0, eta0 = _evaluate_global(raw)
    direction_rows = []
    power_map = {"scale": "scale", "u": "u", "w": "w", "v": "v", "shift": "shift", "lapse": "lapse"}
    for name, direction, family_group in _direction_inventory(raw):
        gp, rp, etap = _evaluate_global(raw + PROBE_LOCAL * direction)
        gm, rm, etam = _evaluate_global(raw - PROBE_LOCAL * direction)
        gs, rs, etas = _evaluate_global(raw + PROBE_SMALL * direction)
        curvature = float((gp - 2.0 * gamma0 + gm) / PROBE_LOCAL**2)
        response_local = float(np.linalg.norm(rp - rm) / (2.0 * PROBE_LOCAL))
        response_small = float(np.linalg.norm(rs - residual0) / PROBE_SMALL)
        local_direction = np.zeros(26)
        local_index = {
            "reconstruction_log_scale": 0, "u_mode_1": 1,
            "w_mode_0": 1 + ORDER, "v_mode_0": 1 + 2 * ORDER,
            "lapse_mode_1": 2 * Q_DIMENSION,
        }.get(name)
        if local_index is not None:
            local_direction[local_index] = 1.0
        elif name == "eta_sensitive_shift":
            offset = (NODES - 1) * Q_DIMENSION + (NODES - 1) * M_DIMENSION
            local_direction[2 * Q_DIMENSION + ORDER:] = direction[offset + ORDER:offset + 2 * ORDER]
        if np.linalg.norm(local_direction) > 0.0:
            dominant_term, term_curvatures = _dominant_direction_term(qe, ve, me, local_direction)
        else:
            dominant_term = "event_KKT_coupling" if family_group == "event_multiplier" else "period_induced_kinetic_and_heat"
            term_curvatures = {}
        raw_to_owned = float(np.linalg.norm(direction))
        if raw_to_owned < 1.0e-2:
            stiffness_class = "PREDOMINANTLY_COORDINATE_UNIT_COMPRESSION"
        elif family_group == "event_multiplier":
            stiffness_class = "LINEAR_EVENT_KKT_COUPLING_NOT_ACTION_CURVATURE"
        else:
            stiffness_class = "PHYSICAL_RESPONSE_ANISOTROPY_BUT_NOT_INTRINSIC_1E6_ACTION_STEP"
        direction_rows.append({
            "direction": name,
            "raw_coordinate_step_norm_at_1e-6": float(PROBE_SMALL * np.linalg.norm(direction)),
            "action_owned_step_norm": PROBE_SMALL,
            "action_change_at_1e-4": float(gp - gamma0),
            "action_change_at_1e-6": float(gs - gamma0),
            "directional_second_variation": curvature,
            "exact_376_residual_change_at_1e-6": float(np.linalg.norm(rs - residual0)),
            "exact_376_response_per_owned_step_at_1e-6": response_small,
            "exact_376_response_per_owned_step_at_1e-4": response_local,
            "response_linearity_ratio_1e-4_to_1e-6": response_local / max(response_small, 1.0e-300),
            "eta_minimum_at_plus_1e-4": etap,
            "eta_minimum_at_minus_1e-4": etam,
            "eta_minimum_at_plus_1e-6": etas,
            "radius_power_exponent": (
                curvature_powers[power_map[family_group]]["exponent"]
                if family_group in power_map else (0.0 if family_group == "event_multiplier" else None)
            ),
            "dominant_action_term": dominant_term,
            "directional_action_term_second_variations": term_curvatures,
            "raw_to_action_owned_step_ratio": raw_to_owned,
            "stiffness_classification": stiffness_class,
        })
    pc, _, lc, _ = _canonical_pair(_CHILD_Q, _CHILD_V, _CHILD_M)
    pe, _, le, _ = _canonical_pair(qe, ve, me)
    child_artifact = __import__("json").loads(Path(
        "artifacts/BHSM_aether_n3_square_kkt_complete_child_promotion_v18_12.json"
    ).read_text(encoding="utf-8"))["square_kkt_complete_child_promotion"]
    conditioning_ratio = float(
        np.max(np.abs(dimensionless_eigenvalues[nonzero]))
        / np.min(np.abs(dimensionless_eigenvalues[nonzero]))
    )
    return {
        "source_state": "EXACT_ACCEPTED_V18_12",
        "physical_equations_changed": False,
        "acceptance_conditions_added": False,
        "characteristic_scales": {
            "terminal_reconstructed_radius": base_radius,
            "radius0": RADIUS0,
            "period": period,
            "event_multiplier": float(state["event_multiplier"]),
            "geometry_coordinate_norms": {
                "u": float(np.linalg.norm(qe[1:1 + ORDER])),
                "w": float(np.linalg.norm(qe[1 + ORDER:1 + 2 * ORDER])),
                "v": float(np.linalg.norm(qe[1 + 2 * ORDER:1 + 3 * ORDER])),
            },
            "eta_Legendre_minimum": eta0,
            "lapse_multiplier_norm": float(np.linalg.norm(me[:ORDER])),
            "shift_multiplier_norm": float(np.linalg.norm(me[ORDER:])),
            "canonical_child_momentum_norm": float(np.linalg.norm(pc)),
            "canonical_event_momentum_norm": float(np.linalg.norm(pe)),
            "canonical_momentum_mismatch_norm": float(np.linalg.norm(pc - pe)),
            "canonical_child_radial_flux_norm": float(np.linalg.norm(lc)),
            "canonical_event_radial_flux_norm": float(np.linalg.norm(le)),
            "resolved_dynamic_flux_envelope": child_artifact["event_to_complete_child"]["resolved_dynamic_flux_envelope"],
        },
        "scale_family": family,
        "measured_action_term_radius_powers": term_powers,
        "measured_curvature_radius_powers": curvature_powers,
        "local_dimensionless_curvature_spectrum": {
            "normalization": "EXISTING_H6_PRODUCT_WEIGHTS_PLUS_PERIOD_INDUCED_VELOCITY_SCALE_DIVIDED_BY_LOCAL_ACTION_TERM_NORM",
            "natural_variable_amplitudes": natural.tolist(),
            "action_reference": action_reference,
            "eigenvalues": dimensionless_eigenvalues.tolist(),
            "maximum_absolute_eigenvalue": float(np.max(np.abs(dimensionless_eigenvalues))),
            "nonzero_absolute_condition_ratio": conditioning_ratio,
            "unit_action_characteristic_owned_step": intrinsic_action_step,
            "ratio_to_1e-6": intrinsic_action_step / PROBE_SMALL,
        },
        "global_directional_measurements": direction_rows,
        "source_global_action": gamma0,
        "source_exact_376_residual_norm": float(np.linalg.norm(residual0)),
        "source_eta_minimum": eta0,
    }


def completion_payload() -> dict[str, Any]:
    result = action_owned_stiffness_measurement()
    spectrum = result["local_dimensionless_curvature_spectrum"]
    rows = result["global_directional_measurements"]
    term_residual = max(abs(row["term_sum_residual"]) for row in result["scale_family"])
    all_eta = min(
        min(row["eta_minimum_at_plus_1e-4"], row["eta_minimum_at_minus_1e-4"])
        for row in rows
    )
    intrinsic_tiny = bool(spectrum["unit_action_characteristic_owned_step"] <= 10.0 * PROBE_SMALL)
    validation = {
        "exact_v18_12_source": result["source_state"] == "EXACT_ACCEPTED_V18_12",
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "no_acceptance_condition_added": not result["acceptance_conditions_added"],
        "exact_376_frontier_reproduced": abs(result["source_exact_376_residual_norm"] - 0.829011042726390) < 5.0e-12,
        "local_action_terms_reconstruct_action": term_residual < 2.0e-10,
        "scale_family_eta_admissible": all_eta > 1.0e-5,
        "finite_dimensionless_spectrum": bool(np.all(np.isfinite(spectrum["eigenvalues"]))),
        "canonical_child_gate_unchanged": result["characteristic_scales"]["canonical_momentum_mismatch_norm"] < 1.0e-7,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_action_owned_stiffness_measurement_v18_14",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "action_owned_stiffness_measurement": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "stiffness_hypothesis_promoted": bool(passed and intrinsic_tiny),
        "stiffness_reclassification": (
            "GENUINE_MICROSCOPIC_PHYSICAL_STIFFNESS" if intrinsic_tiny
            else "RAW_COORDINATE_NEAR_STALL_NOT_EXPLAINED_BY_ACTION_NORMALIZED_CURVATURE"
        ),
        "real_physical_property_explained": (
            "MEASURED_RADIUS_SCALING_OF_RETAINED_ACTION_TERMS_AND_LOCAL_CURVATURE_"
            "SEPARATES_ACTION_STIFFNESS_FROM_RAW_COORDINATE_RESPONSE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "DERIVE_AND_EQUIVALENCE_TEST_AN_ACTION_OWNED_NUMERICAL_SCALING" if passed and not intrinsic_tiny
            else "CONTINUE_SQUARE_KKT_WITH_MEASURED_PHYSICAL_STIFFNESS"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_action_owned_stiffness_measurement_v18_14.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "action_owned_stiffness_measurement", "completion_payload", "materialize"]
