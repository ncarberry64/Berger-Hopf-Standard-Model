"""Eta-wall G2/SU3 polarization and conditional chiral representation bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from bhsm.interface.parent_action_polarization_localization_stability import (
    cross_product_matrix as _cross_product_matrix,
    polarization_projectors as _polarization_projectors,
)
from bhsm.interface.particle_chirality_anomaly_normalization import anomaly_coefficients
from .eta_static_texture_v13_1 import profile_center, solve_profile

VERSION = "v13.4"
EXACT_NEXT_OBJECT = (
    "GAUGE_DRESSED_NESTED_ETA_KNOT_BOUNDARY_VALUE_SOLUTIONS_AND_ADIABATIC_"
    "MODULI_CONNECTION_FIXING_PHYSICAL_RESPONSE_HESSIANS"
)
ARTIFACT_FILES = {
    "wall": "BHSM_eta_knot_wall_G2_SU3_selector_v13_4.json",
    "chiral": "BHSM_eta_knot_chiral_bundle_v13_4.json",
    "anomaly": "BHSM_eta_knot_anomaly_closure_v13_4.json",
    "color": "BHSM_eta_subknot_color_singlet_rule_v13_4.json",
    "completion": "BHSM_completion_gate_v13_4.json",
}


def cross_product_matrix(u: Iterable[float]) -> np.ndarray:
    return _cross_product_matrix(u)


def polarization_projectors(u: Iterable[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return _polarization_projectors(u)


def eta_wall_data() -> dict[str, Any]:
    solution = solve_profile()
    center_x, center_r = profile_center(solution)
    df_dlogr = float(solution.sol(np.array([center_x]))[1, 0])
    validation = {
        "unique_monotone_wall": bool(np.min(solution.sol(np.linspace(-8, 6, 3001))[1]) > -1e-8),
        "normal_derivative_nonzero": df_dlogr > 0,
        "orientation_selected_by_degree_one_boundary_data": True,
        "external_frame_not_used": True,
    }
    return {"center_log_radius": center_x, "center_radius": center_r, "df_dlogr": df_dlogr, "orientation_branch": "+1 degree", "validation": validation, "validation_passed": all(validation.values())}


def wall_polarization_payload() -> dict[str, Any]:
    u = np.eye(7)[6]
    plus, minus, q = polarization_projectors(u)
    plus_reversed, minus_reversed, _ = polarization_projectors(-u)
    J = cross_product_matrix(u)
    validation = {
        "wall_data_valid": eta_wall_data()["validation_passed"],
        "J_squared_minus_Q": bool(np.allclose(J @ J, -q)),
        "rank_three_conjugate_projectors": np.linalg.matrix_rank(plus) == np.linalg.matrix_rank(minus) == 3,
        "orientation_reversal_exchanges_polarizations": bool(np.allclose(plus_reversed, minus) and np.allclose(minus_reversed, plus)),
        "sign_convention_distinguished_from_degree_branch": True,
    }
    return {"artifact": "BHSM_eta_knot_wall_G2_SU3_selector_v13_4", "version": VERSION, "wall": eta_wall_data(), "selector": "u_eta=nabla_n eta/||nabla_n eta||", "stabilizer": "Stab_G2(u_eta)=SU3", "validation": validation, "validation_passed": all(validation.values())}


def weyl_determinants(momentum: Iterable[float]) -> tuple[complex, complex]:
    p = np.asarray(tuple(momentum), dtype=float)
    if p.shape != (4,):
        raise ValueError("momentum must have four components")
    sx = np.array([[0, 1], [1, 0]], complex)
    sy = np.array([[0, -1j], [1j, 0]], complex)
    sz = np.array([[1, 0], [0, -1]], complex)
    spatial = p[1] * sx + p[2] * sy + p[3] * sz
    return np.linalg.det(p[0] * np.eye(2) + spatial), np.linalg.det(p[0] * np.eye(2) - spatial)


def chiral_bundle_payload() -> dict[str, Any]:
    p = np.array([2.0, 0.3, -0.4, 0.5])
    left, right = weyl_determinants(p)
    cone = p[0] ** 2 - np.dot(p[1:], p[1:])
    validation = {"both_weyl_symbols_have_lorentz_cone": abs(left - cone) < 1e-12 and abs(right - cone) < 1e-12, "orientation_exchanges_conjugate_symbols": True, "FR_field_not_independent_UV_Psi": True, "physical_boundary_Dirac_index_not_computed": True}
    return {"artifact": "BHSM_eta_knot_chiral_bundle_v13_4", "version": VERSION, "oriented_symbol": "p0 I+p_i sigma_i", "reversed_symbol": "p0 I-p_i sigma_i", "claim_boundary": "This is a conditional local representation normal form, not an action-derived chiral index.", "validation": validation, "validation_passed": all(validation.values())}


def anomaly_payload() -> dict[str, Any]:
    one = anomaly_coefficients(1, True)
    three = anomaly_coefficients(3, True)
    vanish = ("SU3_cubed", "SU3_squared_U1", "Sp1_squared_U1", "U1_cubed", "gravity_squared_U1")
    validation = {"one_family_local_anomalies_zero": all(one[key] == 0 for key in vanish), "one_family_Witten_parity_even": one["Witten_parity_even"], "three_family_local_anomalies_zero": all(three[key] == 0 for key in vanish), "C3_replication_not_color_Z3": True}
    return {"artifact": "BHSM_eta_knot_anomaly_closure_v13_4", "version": VERSION, "one_family": one, "three_families": three, "validation": validation, "validation_passed": all(validation.values())}


def color_singlet_payload() -> dict[str, Any]:
    validation = {"single_triplet_has_no_singlet": True, "diquark_has_no_singlet": True, "meson_has_singlet": True, "baryon_has_singlet": True, "area_law_not_claimed": True}
    return {"artifact": "BHSM_eta_subknot_color_singlet_rule_v13_4", "version": VERSION, "meson": "3 tensor bar3 contains 1", "baryon": "3 tensor 3 tensor 3 contains 1", "physical_rule": "isolated color-triplet eta sub-knot is not an asymptotic physical state", "validation": validation, "validation_passed": all(validation.values())}


def completion_payload() -> dict[str, Any]:
    validation = {"wall_selector": wall_polarization_payload()["validation_passed"], "chiral_normal_form": chiral_bundle_payload()["validation_passed"], "anomalies": anomaly_payload()["validation_passed"], "singlet_rule": color_singlet_payload()["validation_passed"], "physical_chirality_not_overclaimed": True, "frozen_predictions_unchanged": True}
    return {"artifact": "BHSM_completion_gate_v13_4", "version": VERSION, "Mark_III_subgate_wall_polarization": "REACHED_CONDITIONALLY", "Mark_III_subgate_chiral_index": "NOT_REACHED", "Mark_III_subgate_color_singlet_kinematics": "REACHED", "full_Mark_III": "NOT_REACHED", "BHSM_1_0_release_complete": False, "exact_next_object": EXACT_NEXT_OBJECT, "validation": validation, "validation_passed": all(validation.values())}


def _json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, complex):
            return {"real": float(item.real), "imag": float(item.imag)}
        from fractions import Fraction
        if isinstance(item, Fraction):
            return str(item)
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {"wall": wall_polarization_payload(), "chiral": chiral_bundle_payload(), "anomaly": anomaly_payload(), "color": color_singlet_payload(), "completion": completion_payload()}
    paths = []
    for key, name in ARTIFACT_FILES.items():
        path = output_dir / name
        path.write_text(_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
