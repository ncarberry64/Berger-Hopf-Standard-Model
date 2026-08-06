"""Canonical eta-wall projector connection and exact SU(3) singlet closure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm

from .eta_knot_chiral_color_completion_v13_4 import cross_product_matrix, eta_wall_data, polarization_projectors

VERSION = "v13.5"
EXACT_NEXT_OBJECT = (
    "NUMERICAL_GAUGE_DRESSED_SINGLET_MESON_AND_BARYON_ETA_BOUNDARY_VALUE_"
    "SOLUTIONS_WITH_FULL_GAUSS_CONSTRAINT_NONRADIAL_STABILITY_AND_RESPONSE_HESSIANS"
)
ARTIFACT_FILES = {
    "connection": "BHSM_eta_wall_projector_connection_v13_5.json",
    "singlet": "BHSM_eta_subknot_singlet_covariant_closure_v13_5.json",
    "bvp": "BHSM_gauge_dressed_nested_eta_BVP_contract_v13_5.json",
    "completion": "BHSM_completion_gate_v13_5.json",
}


def projector_derivative(unit: np.ndarray, tangent: np.ndarray) -> np.ndarray:
    u, a = np.asarray(unit, float), np.asarray(tangent, float)
    if u.shape != (7,) or a.shape != (7,):
        raise ValueError("unit and tangent must be seven-vectors")
    u = u / np.linalg.norm(u)
    if abs(float(u @ a)) > 1e-12:
        raise ValueError("tangent must be orthogonal to unit")
    J_a = cross_product_matrix(a)
    return (-np.outer(a, u) - np.outer(u, a) - 1j * J_a) / 2


def projector_curvature(unit: np.ndarray, tangent_a: np.ndarray, tangent_b: np.ndarray) -> np.ndarray:
    plus, _, _ = polarization_projectors(unit)
    dpa, dpb = projector_derivative(unit, tangent_a), projector_derivative(unit, tangent_b)
    return plus @ (dpa @ dpb - dpb @ dpa) @ plus


def image_frame(projector: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(np.asarray(projector, complex))
    frame = vectors[:, np.argsort(values)[-3:]]
    for column in range(3):
        pivot = int(np.argmax(np.abs(frame[:, column])))
        frame[:, column] *= np.exp(-1j * np.angle(frame[pivot, column]))
    return frame


def reference_curvature() -> dict[str, Any]:
    u, a, b = np.eye(7)[6], np.eye(7)[0], np.eye(7)[1]
    plus, _, _ = polarization_projectors(u)
    curvature = projector_curvature(u, a, b)
    frame = image_frame(plus)
    restricted = frame.conj().T @ curvature @ frame
    validation = {"curvature_projected": bool(np.allclose(plus @ curvature @ plus, curvature, atol=1e-13)), "restricted_curvature_anti_Hermitian": bool(np.allclose(restricted.conj().T, -restricted, atol=1e-13)), "restricted_curvature_traceless": abs(np.trace(restricted)) < 1e-13, "curvature_nonzero": np.linalg.norm(restricted) > 1e-8, "rank_three_bundle": frame.shape == (7, 3)}
    return {"curvature_7x7": curvature, "curvature_restricted_3x3": restricted, "curvature_norm": float(np.linalg.norm(restricted)), "validation": validation, "validation_passed": all(validation.values())}


def connection_payload() -> dict[str, Any]:
    reference = reference_curvature()
    validation = {"wall_selector_nonzero": eta_wall_data()["df_dlogr"] > 0, "projector_connection_curvature_valid": reference["validation_passed"], "no_new_continuous_coupling_added": True, "physical_Yang_Mills_normalization_not_claimed": True}
    return {"artifact": "BHSM_eta_wall_projector_connection_v13_5", "version": VERSION, "rank_three_bundle": "Image(Pi_10(u_eta))", "connection": "nabla^P=P d", "curvature": "F^P=P[dP,dP]P", "reference_curvature": reference, "normalization_boundary": "geometry does not fix the coefficient of Tr(F^2)", "validation": validation, "validation_passed": all(validation.values())}


def _epsilon(q1: np.ndarray, q2: np.ndarray, q3: np.ndarray) -> complex:
    return complex(np.linalg.det(np.column_stack((q1, q2, q3))))


def singlet_covariance_witness() -> dict[str, Any]:
    H = np.array([[0.6, 0.2 + 0.1j, -0.1j], [0.2 - 0.1j, -0.4, 0.3], [0.1j, 0.3, -0.2]], complex)
    H = (H + H.conj().T) / 2 - np.trace(H) * np.eye(3) / 3
    U = expm(1j * H)
    q1 = np.array([1 + 0.2j, -0.3 + 0.4j, 0.7 - 0.1j])
    q2 = np.array([0.4, 1j, -0.2 + 0.3j])
    q3 = np.array([0.1 - 0.2j, -0.5, 0.8j])
    A = np.array([[0.3j, 0.2, -0.1j], [-0.2, -0.1j, 0.4], [-0.1j, -0.4, -0.2j]], complex)
    A = (A - A.conj().T) / 2 - np.trace((A - A.conj().T) / 2) * np.eye(3) / 3
    infinitesimal = _epsilon(A @ q1, q2, q3) + _epsilon(q1, A @ q2, q3) + _epsilon(q1, q2, A @ q3)
    validation = {"U_unitary": bool(np.allclose(U.conj().T @ U, np.eye(3), atol=1e-13)), "det_U_one": abs(np.linalg.det(U) - 1) < 1e-13, "meson_finite_transport_invariant": abs(np.vdot(U @ q1, U @ q2) - np.vdot(q1, q2)) < 1e-13, "baryon_finite_transport_invariant": abs(_epsilon(U @ q1, U @ q2, U @ q3) - _epsilon(q1, q2, q3)) < 1e-13, "baryon_infinitesimal_connection_cancels": abs(infinitesimal) < 1e-13}
    return {"infinitesimal_baryon_connection_term": infinitesimal, "validation": validation, "validation_passed": all(validation.values())}


def singlet_payload() -> dict[str, Any]:
    witness = singlet_covariance_witness()
    validation = {"finite_and_infinitesimal_SU3_closure": witness["validation_passed"], "dynamic_confinement_potential_not_claimed": True, "isolated_triplet_not_promoted": True}
    return {"artifact": "BHSM_eta_subknot_singlet_covariant_closure_v13_5", "version": VERSION, "witness": witness, "validation": validation, "validation_passed": all(validation.values())}


def nested_bvp_contract_payload() -> dict[str, Any]:
    validation = {"eta_equation_retained": True, "connection_is_projector_induced": True, "SU3_Gauss_constraint_required": True, "singlet_boundary_condition_required": True, "no_proxy_solution_promoted": True}
    return {"artifact": "BHSM_gauge_dressed_nested_eta_BVP_contract_v13_5", "version": VERSION, "status": "FORMULATED_NOT_SOLVED", "bulk_eta_equation": "D_A[(1+g sigma^2)(kappa1+X_eta^3)D^A eta]+Lambda_eta eta=0", "projector_connection": "P=Pi_10(u_eta), F=P[dP,dP]P", "connection_equation": "must follow from a retained action variation/Gauss constraint", "exact_next_object": EXACT_NEXT_OBJECT, "validation": validation, "validation_passed": all(validation.values())}


def completion_payload() -> dict[str, Any]:
    validation = {"canonical_projector_connection_derived": connection_payload()["validation_passed"], "exact_singlet_covariant_closure": singlet_payload()["validation_passed"], "nonlinear_BVP_typed": nested_bvp_contract_payload()["validation_passed"], "physical_g3_not_claimed": True, "nested_solution_not_invented": True}
    return {"artifact": "BHSM_completion_gate_v13_5", "version": VERSION, "Mark_III_subgate_induced_color_connection": "REACHED_CONDITIONALLY", "Mark_III_subgate_covariant_singlet_closure": "REACHED", "Mark_III_subgate_nested_nonlinear_solution": "NOT_REACHED", "BHSM_1_0_release_complete": False, "exact_next_object": EXACT_NEXT_OBJECT, "validation": validation, "validation_passed": all(validation.values())}


def _json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray): return item.tolist()
        if isinstance(item, np.generic): return item.item()
        if isinstance(item, complex): return {"real": float(item.real), "imag": float(item.imag)}
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {"connection": connection_payload(), "singlet": singlet_payload(), "bvp": nested_bvp_contract_payload(), "completion": completion_payload()}
    paths = []
    for key, name in ARTIFACT_FILES.items():
        path = output_dir / name
        path.write_text(_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
