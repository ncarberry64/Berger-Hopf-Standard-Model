"""BHSM v14.69 tensor differential incidence and round-seam shape-kernel gate.

This sprint upgrades the v14.68 scalar incidence map to the exact symmetric-
tensor differential of the already-owned v7.1/v11.3 compatibility chain.

For a bundle-like M8 metric split into horizontal/base and vertical/fiber
blocks,

    G = [[A, B], [B*, C]],

its quotient horizontal metric is the Schur complement

    Q_H(G) = A - B C^{-1} B*.

The Frechet differential and its Frobenius adjoint are evaluated explicitly.
For each M5->M4 seam inclusion T, the fixed-embedding trace is h=T* g T,
with differential T* delta g T and adjoint T Lambda T*.  A moving normal seam
adds the standard first shape term 2 xi K.

On the reflection-symmetric round equator K=0.  Therefore a pure normal seam
displacement is in the *first-order metric-trace kernel*.  This is an exact
reason the v14.68 scalar moving-seam incidence cannot yet be promoted to the
full physical tensor map: the physical nonuniform shape channels require a
nonround stationary cap with K != 0, or the second shape variation.

Within the action-owned metric sector, the round fixed-splitting maps are
surjective at each stage:

    DQ_H : Sym^2(R8) -> Sym^2(R5), rank 15, kernel 21,
    Tr   : Sym^2(R5) -> Sym^2(R4), rank 10, kernel 5,
    Tr o DQ_H has rank 10.

Using their exact adjoints, the common M4 symmetric-tensor channel is lifted
isometrically into M8/M5+/M5-/M4.  Tensoring that lift with the two-dimensional
v14.68 attachment tangent produces a 20-dimensional action-connected tensor
incidence subspace and a positive semidefinite Wentzell reaction whose nonzero
spectrum is exactly the recovered attachment spectrum with multiplicity 10.

Fail-closed boundary:
* this is the metric symmetric-tensor sector, not the complete gauge-fixed
  metric+gauge+spinor+ghost Calderon space;
* physical h_C and k_D still require the globally stationary background;
* the round seam has K=0, so first-order normal shape response is absent;
* nonuniform moving-seam harmonics, complete projectors, continuum relative
  heat supertrace, and the neutrino kill screen remain open.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any, Callable, Sequence

import numpy as np

from bhsm.interface.completion.action_attachment_wentzell_v14_67 import (
    attachment_response_roots,
    attachment_wentzell_response,
)
from bhsm.interface.completion.global_attachment_incidence_curvature_v14_68 import (
    canonical_incidence_isometry,
)

VERSION = "v14.69"
PRIMARY_VERDICT = (
    "BHSM_V14_69_THE_ACTION_OWNED_METRIC_COMPATIBILITY_CHAIN_HAS_AN_EXACT_"
    "TENSOR_FRECHET_DIFFERENTIAL_AND_ADJOINT_WITH_DQ_H_RANK_15_TRACE_RANK_10_"
    "AND_A_CANONICAL_20_DIMENSIONAL_COMMON_SEAM_TENSOR_ATTACHMENT_LIFT_BUT_"
    "THE_ROUND_EQUATOR_HAS_ZERO_EXTRINSIC_CURVATURE_SO_PURE_NORMAL_MOVING_"
    "SEAM_DEFORMATIONS_ARE_IN_THE_FIRST_ORDER_METRIC_TRACE_KERNEL_AND_FULL_"
    "PHYSICAL_CALDERON_CLOSURE_REQUIRES_THE_NONROUND_STATIONARY_BACKGROUND_"
    "OR_SECOND_SHAPE_VARIATION_PLUS_COMPLETE_GAUGE_GHOST_ZERO_MODE_PROJECTORS"
)
EXACT_NEXT_OBJECT = (
    "GLOBAL_ACTION_STATIONARY_NONROUND_PARENT_CHILD_CAP_BACKGROUND_WITH_"
    "ACTION_DERIVED_EXTRINSIC_CURVATURE_AND_SECOND_SHAPE_HESSIAN_FOR_THREE_"
    "NONUNIFORM_MOVING_SEAM_HARMONICS_THEN_GAUGE_FIXED_METRIC_GAUGE_SPINOR_"
    "GHOST_CALDERON_OPERATORS_CONTINUUM_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_"
    "NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def sym_basis(n: int) -> list[np.ndarray]:
    """Frobenius-orthonormal basis of real symmetric n x n matrices."""
    if n < 1:
        raise ValueError("n must be positive")
    out: list[np.ndarray] = []
    for i in range(n):
        e = np.zeros((n, n), dtype=float)
        e[i, i] = 1.0
        out.append(e)
    inv = 1.0 / math.sqrt(2.0)
    for i in range(n):
        for j in range(i + 1, n):
            e = np.zeros((n, n), dtype=float)
            e[i, j] = inv
            e[j, i] = inv
            out.append(e)
    return out


def sym_coordinates(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=float)
    if x.ndim != 2 or x.shape[0] != x.shape[1] or np.linalg.norm(x - x.T) > 1e-11:
        raise ValueError("matrix must be real symmetric")
    return np.asarray([float(np.sum(e * x)) for e in sym_basis(x.shape[0])], dtype=float)


def sym_from_coordinates(coords: Sequence[float], n: int) -> np.ndarray:
    c = np.asarray(coords, dtype=float).reshape(-1)
    basis = sym_basis(n)
    if len(c) != len(basis):
        raise ValueError("coordinate length mismatch")
    out = np.zeros((n, n), dtype=float)
    for value, e in zip(c, basis):
        out += value * e
    return out


def linear_map_matrix(domain_n: int, codomain_n: int, fn: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    cols = []
    for e in sym_basis(domain_n):
        y = np.asarray(fn(e), dtype=float)
        if y.shape != (codomain_n, codomain_n):
            raise ValueError("linear map returned wrong shape")
        cols.append(sym_coordinates(0.5 * (y + y.T)))
    return np.column_stack(cols)


def _spd(a: np.ndarray, name: str) -> np.ndarray:
    x = np.asarray(a, dtype=float)
    if x.ndim != 2 or x.shape[0] != x.shape[1] or np.linalg.norm(x - x.T) > 1e-11:
        raise ValueError(f"{name} must be symmetric")
    if float(np.min(np.linalg.eigvalsh(x))) <= 0.0:
        raise ValueError(f"{name} must be positive definite")
    return x


def kk_metric_from_quotient(q: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Construct G with Schur quotient Q_H(G)=q."""
    qq = _spd(q, "q")
    cc = _spd(c, "c")
    bb = np.asarray(b, dtype=float)
    m = qq.shape[0]
    k = cc.shape[0]
    if bb.shape != (m, k):
        raise ValueError("b shape mismatch")
    a = qq + bb @ np.linalg.solve(cc, bb.T)
    return np.block([[a, bb], [bb.T, cc]])


def horizontal_quotient_metric(g: np.ndarray, base_dim: int = 5) -> np.ndarray:
    """Q_H=A-B C^{-1} B^T for a bundle-like metric block decomposition."""
    x = _spd(g, "G")
    m = int(base_dim)
    if not 0 < m < x.shape[0]:
        raise ValueError("invalid base_dim")
    a = x[:m, :m]
    b = x[:m, m:]
    c = x[m:, m:]
    return 0.5 * ((a - b @ np.linalg.solve(c, b.T)) + (a - b @ np.linalg.solve(c, b.T)).T)


def horizontal_quotient_differential(g: np.ndarray, dg: np.ndarray, base_dim: int = 5) -> np.ndarray:
    x = _spd(g, "G")
    d = np.asarray(dg, dtype=float)
    if d.shape != x.shape or np.linalg.norm(d - d.T) > 1e-11:
        raise ValueError("dG must be symmetric with G shape")
    m = int(base_dim)
    a_b = x[:m, m:]
    c = x[m:, m:]
    da = d[:m, :m]
    db = d[:m, m:]
    dc = d[m:, m:]
    ci = np.linalg.inv(c)
    out = da - db @ ci @ a_b.T - a_b @ ci @ db.T + a_b @ ci @ dc @ ci @ a_b.T
    return 0.5 * (out + out.T)


def horizontal_quotient_adjoint(g: np.ndarray, lam: np.ndarray, base_dim: int = 5) -> np.ndarray:
    """Frobenius adjoint DQ_H^*[lam]."""
    x = _spd(g, "G")
    y = np.asarray(lam, dtype=float)
    m = int(base_dim)
    if y.shape != (m, m) or np.linalg.norm(y - y.T) > 1e-11:
        raise ValueError("lambda must be symmetric base tensor")
    b = x[:m, m:]
    c = x[m:, m:]
    ci = np.linalg.inv(c)
    hv = -y @ b @ ci
    vv = ci @ b.T @ y @ b @ ci
    out = np.block([[y, hv], [hv.T, vv]])
    return 0.5 * (out + out.T)


def seam_embedding() -> np.ndarray:
    """Round equatorial tangent inclusion R4 -> R5."""
    t = np.zeros((5, 4), dtype=float)
    t[:4, :4] = np.eye(4)
    return t


def trace_metric(g5: np.ndarray, t: np.ndarray | None = None) -> np.ndarray:
    g = np.asarray(g5, dtype=float)
    T = seam_embedding() if t is None else np.asarray(t, dtype=float)
    if g.shape != (5, 5) or T.shape != (5, 4):
        raise ValueError("trace dimensions mismatch")
    return 0.5 * (T.T @ g @ T + (T.T @ g @ T).T)


def trace_differential(dg5: np.ndarray, t: np.ndarray | None = None) -> np.ndarray:
    return trace_metric(dg5, t)


def trace_adjoint(lam4: np.ndarray, t: np.ndarray | None = None) -> np.ndarray:
    y = np.asarray(lam4, dtype=float)
    T = seam_embedding() if t is None else np.asarray(t, dtype=float)
    if y.shape != (4, 4) or np.linalg.norm(y - y.T) > 1e-11:
        raise ValueError("lambda4 must be symmetric")
    return 0.5 * (T @ y @ T.T + (T @ y @ T.T).T)


def moving_trace_differential(dg5: np.ndarray, xi: float, extrinsic_curvature: np.ndarray, t: np.ndarray | None = None) -> np.ndarray:
    """Normal-shape first variation: delta h=T^T delta g T + 2 xi K."""
    k = np.asarray(extrinsic_curvature, dtype=float)
    if k.shape != (4, 4) or np.linalg.norm(k - k.T) > 1e-11:
        raise ValueError("K must be symmetric 4x4")
    return trace_differential(dg5, t) + 2.0 * float(xi) * k


def round_metric8() -> np.ndarray:
    return np.eye(8, dtype=float)


def generic_bundle_metric8() -> np.ndarray:
    q = np.diag([1.1, 1.25, 1.4, 1.6, 1.85])
    q[0, 1] = q[1, 0] = 0.07
    q[2, 4] = q[4, 2] = -0.05
    c = np.diag([1.3, 1.7, 2.2])
    b = np.asarray([
        [0.08, -0.03, 0.02],
        [0.04, 0.05, -0.01],
        [-0.02, 0.03, 0.06],
        [0.01, -0.04, 0.03],
        [0.05, 0.02, -0.02],
    ])
    return kk_metric_from_quotient(q, b, c)


def dq_matrix(g8: np.ndarray | None = None) -> np.ndarray:
    g = round_metric8() if g8 is None else np.asarray(g8, dtype=float)
    return linear_map_matrix(8, 5, lambda dg: horizontal_quotient_differential(g, dg, 5))


def trace_matrix() -> np.ndarray:
    return linear_map_matrix(5, 4, trace_differential)


def chain_matrix(g8: np.ndarray | None = None) -> np.ndarray:
    return trace_matrix() @ dq_matrix(g8)


def finite_difference_dq_residual(eps: float = 2e-7) -> float:
    g = generic_bundle_metric8()
    rng = np.random.default_rng(1469)
    z = rng.normal(size=(8, 8))
    dg = 0.5 * (z + z.T)
    exact = horizontal_quotient_differential(g, dg)
    gp = g + eps * dg
    gm = g - eps * dg
    fd = (horizontal_quotient_metric(gp) - horizontal_quotient_metric(gm)) / (2.0 * eps)
    return float(np.linalg.norm(exact - fd))


def dq_adjoint_residual() -> float:
    g = generic_bundle_metric8()
    rng = np.random.default_rng(1470)
    z = rng.normal(size=(8, 8)); dg = 0.5 * (z + z.T)
    y0 = rng.normal(size=(5, 5)); y = 0.5 * (y0 + y0.T)
    lhs = float(np.sum(y * horizontal_quotient_differential(g, dg)))
    rhs = float(np.sum(horizontal_quotient_adjoint(g, y) * dg))
    return abs(lhs - rhs)


def trace_adjoint_residual() -> float:
    rng = np.random.default_rng(1471)
    z = rng.normal(size=(5, 5)); dg = 0.5 * (z + z.T)
    y0 = rng.normal(size=(4, 4)); y = 0.5 * (y0 + y0.T)
    lhs = float(np.sum(y * trace_differential(dg)))
    rhs = float(np.sum(trace_adjoint(y) * dg))
    return abs(lhs - rhs)


def tensor_rank_payload() -> dict[str, Any]:
    dq0 = dq_matrix()
    tr = trace_matrix()
    ch = tr @ dq0
    dqg = dq_matrix(generic_bundle_metric8())
    return {
        "version": VERSION,
        "spaces": {
            "Sym2_M8_dimension": 36,
            "Sym2_M5_dimension": 15,
            "Sym2_M4_dimension": 10,
        },
        "round_DQ_H_rank": int(np.linalg.matrix_rank(dq0, tol=1e-11)),
        "round_DQ_H_kernel_dimension": int(dq0.shape[1] - np.linalg.matrix_rank(dq0, tol=1e-11)),
        "generic_bundle_DQ_H_rank": int(np.linalg.matrix_rank(dqg, tol=1e-11)),
        "trace_rank": int(np.linalg.matrix_rank(tr, tol=1e-11)),
        "trace_kernel_dimension": int(tr.shape[1] - np.linalg.matrix_rank(tr, tol=1e-11)),
        "trace_after_DQ_H_rank": int(np.linalg.matrix_rank(ch, tol=1e-11)),
        "round_DQ_H_nonzero_singular_values": np.linalg.svd(dq0, compute_uv=False).tolist(),
        "trace_nonzero_singular_values": np.linalg.svd(tr, compute_uv=False).tolist(),
        "generic_DQ_H_finite_difference_residual": finite_difference_dq_residual(),
        "DQ_H_adjoint_virtual_work_residual": dq_adjoint_residual(),
        "trace_adjoint_virtual_work_residual": trace_adjoint_residual(),
        "full_tensor_formulas_derived": True,
        "physical_background_numerically_selected": False,
        "physical_BHSM_prediction": False,
    }


def round_shape_kernel_payload() -> dict[str, Any]:
    zero = np.zeros((5, 5))
    k0 = np.zeros((4, 4))
    kg = np.diag([0.08, -0.03, 0.05, 0.02])
    xi = 0.37
    round_response = moving_trace_differential(zero, xi, k0)
    generic_response = moving_trace_differential(zero, xi, kg)
    plus = generic_response
    minus = moving_trace_differential(zero, xi, -kg)
    return {
        "version": VERSION,
        "shape_formula": "delta h_ab=(Tr delta g)_ab+2 xi K_ab plus tangential Lie derivative",
        "round_equator_K": "0",
        "pure_normal_round_response_norm": float(np.linalg.norm(round_response)),
        "generic_nonzero_K_response_norm": float(np.linalg.norm(generic_response)),
        "reflected_cap_response_sum_norm": float(np.linalg.norm(plus + minus)),
        "pure_normal_displacement_is_first_order_metric_trace_kernel_on_round_equator": True,
        "three_nonuniform_shape_channels_derived_from_round_first_variation": False,
        "required_resolution": "nonround action-stationary K_ab or second shape variation/Hessian",
        "physical_BHSM_prediction": False,
    }


def round_common_tensor_lifts() -> dict[str, np.ndarray]:
    """Isometric lifts Sym2(M4)-> each metric stratum on the round branch."""
    g8 = round_metric8()
    lifts: dict[str, list[np.ndarray]] = {"M8": [], "M5_plus": [], "M5_minus": [], "M4": []}
    for y in sym_basis(4):
        y5 = trace_adjoint(y)
        y8 = horizontal_quotient_adjoint(g8, y5)
        lifts["M8"].append(sym_coordinates(y8))
        lifts["M5_plus"].append(sym_coordinates(y5))
        lifts["M5_minus"].append(sym_coordinates(y5))
        lifts["M4"].append(sym_coordinates(y))
    return {k: np.column_stack(v) for k, v in lifts.items()}


def heterogeneous_tensor_incidence_isometry() -> np.ndarray:
    """Lift 2 attachment tangents x 10 seam tensors into heterogeneous metric spaces."""
    es = canonical_incidence_isometry()  # vertex order M8,M5+,M5-,M4
    lifts = round_common_tensor_lifts()
    ordered = [lifts["M8"], lifts["M5_plus"], lifts["M5_minus"], lifts["M4"]]
    row_sizes = [x.shape[0] for x in ordered]
    out = np.zeros((sum(row_sizes), 20), dtype=complex)
    r0 = 0
    for vi, lv in enumerate(ordered):
        rr = slice(r0, r0 + lv.shape[0])
        for a in range(2):
            cc = slice(a * 10, (a + 1) * 10)
            out[rr, cc] = es[vi, a] * lv
        r0 += lv.shape[0]
    return out


def tensor_attachment_operator(h_core: float = 0.181391690148362, depth_curvature: float = 1.0) -> np.ndarray:
    e = heterogeneous_tensor_incidence_isometry()
    wa = np.kron(attachment_wentzell_response(h_core, depth_curvature), np.eye(10))
    out = e @ wa @ e.conj().T
    return 0.5 * (out + out.conj().T)


def tensor_incidence_payload() -> dict[str, Any]:
    lifts = round_common_tensor_lifts()
    lift_residuals = {k: float(np.linalg.norm(v.T @ v - np.eye(10))) for k, v in lifts.items()}
    e = heterogeneous_tensor_incidence_isometry()
    w = tensor_attachment_operator()
    ev = np.linalg.eigvalsh(w)
    nz = ev[ev > 1e-11]
    expected = np.sort(np.repeat(np.asarray(attachment_response_roots()), 10))
    return {
        "version": VERSION,
        "heterogeneous_boundary_metric_dimension": int(e.shape[0]),
        "attachment_tensor_subspace_dimension": int(e.shape[1]),
        "stratum_dimensions": {"M8": 36, "M5_plus": 15, "M5_minus": 15, "M4": 10},
        "individual_common_tensor_lift_isometry_residuals": lift_residuals,
        "global_tensor_incidence_isometry_residual": float(np.linalg.norm(e.conj().T @ e - np.eye(20))),
        "global_tensor_incidence_rank": int(np.linalg.matrix_rank(e, tol=1e-11)),
        "tensor_Wentzell_dimension": int(w.shape[0]),
        "tensor_Wentzell_rank": int(np.linalg.matrix_rank(w, tol=1e-11)),
        "tensor_Wentzell_hermiticity_residual": float(np.linalg.norm(w - w.conj().T)),
        "tensor_Wentzell_minimum_eigenvalue": float(np.min(ev)),
        "nonzero_spectrum_matches_attachment_roots_x10_residual": float(np.max(np.abs(nz - expected))),
        "scalar_incidence_superseded_for_common_symmetric_tensor_metric_sector": True,
        "full_gauge_fixed_calderon_space_closed": False,
        "physical_BHSM_prediction": False,
    }


def compatibility_jacobian_round() -> np.ndarray:
    """Linearized two-cap metric compatibility system on round K=0.

    Variables: G8(36), g5+(15), g5-(15), h4(10), xi+(1), xi-(1).
    Rows: C85+(15), C85-(15), C54+(10), C54-(10).
    """
    dq = dq_matrix()
    tr = trace_matrix()
    J = np.zeros((50, 78), dtype=float)
    # column offsets
    oG, op, om, oh, oxp, oxm = 0, 36, 51, 66, 76, 77
    # C85+
    J[0:15, oG:oG+36] = -dq
    J[0:15, op:op+15] = np.eye(15)
    # C85-
    J[15:30, oG:oG+36] = -dq
    J[15:30, om:om+15] = np.eye(15)
    # C54+
    J[30:40, op:op+15] = -tr
    J[30:40, oh:oh+10] = np.eye(10)
    # C54-
    J[40:50, om:om+15] = -tr
    J[40:50, oh:oh+10] = np.eye(10)
    # round K=0 => xi columns exactly zero
    return J


def compatibility_reducibility_matrix() -> np.ndarray:
    """Ten exact relations among the duplicated two-cap compatibility rows.

    For C85+ = g+ - Q, C85- = g- - Q and C54+- = h-Tr(g+-),

        Tr(C85+) - Tr(C85-) + C54+ - C54- = 0.

    This is the linear compatibility-complex identity.  It is a multiplier
    reducibility, not a new physical gauge symmetry.
    """
    tr = trace_matrix()
    r = np.zeros((10, 50), dtype=float)
    r[:, 0:15] = tr
    r[:, 15:30] = -tr
    r[:, 30:40] = np.eye(10)
    r[:, 40:50] = -np.eye(10)
    return r


def compatibility_payload() -> dict[str, Any]:
    j = compatibility_jacobian_round()
    r = compatibility_reducibility_matrix()
    xp = np.zeros(78); xp[76] = 1.0
    xm = np.zeros(78); xm[77] = 1.0
    rng = np.random.default_rng(1472)
    lam = rng.normal(size=50)
    delta = rng.normal(size=78)
    lhs = float(lam @ (j @ delta))
    rhs = float((j.T @ lam) @ delta)
    rank = int(np.linalg.matrix_rank(j, tol=1e-11))
    return {
        "version": VERSION,
        "round_two_cap_compatibility_jacobian_shape": list(j.shape),
        "round_two_cap_compatibility_rank": rank,
        "round_two_cap_compatibility_nullity": int(j.shape[1] - rank),
        "constraint_row_redundancy_dimension": int(j.shape[0] - rank),
        "reducibility_matrix_rank": int(np.linalg.matrix_rank(r, tol=1e-11)),
        "reducibility_identity_residual": float(np.linalg.norm(r @ j)),
        "reducibility_identity": "Tr(C85_plus)-Tr(C85_minus)+C54_plus-C54_minus=0",
        "pure_xi_plus_constraint_residual_norm": float(np.linalg.norm(j @ xp)),
        "pure_xi_minus_constraint_residual_norm": float(np.linalg.norm(j @ xm)),
        "compatibility_adjoint_virtual_work_residual": abs(lhs-rhs),
        "round_shape_coordinates_are_explicit_null_directions_of_first_metric_compatibility_differential": True,
        "two_cap_multiplier_system_is_reducible_by_ten_common_seam_tensor_relations": True,
        "metric_compatibility_tensor_chain_derived": True,
        "complete_physical_constraint_operator_derived": False,
        "physical_BHSM_prediction": False,
    }


def provenance_gate_payload() -> dict[str, Any]:
    required = {
        "global_stationary_nonround_parent_child_background": False,
        "physical_extrinsic_curvature_K_plus_minus": False,
        "second_shape_Hessian_or_nonzero_first_shape_response": False,
        "three_action_selected_nonuniform_shape_harmonics": False,
        "physical_h_C_and_Schur_k_D_from_same_global_solution": False,
        "gauge_fixed_metric_gauge_spinor_ghost_Calderon_operators": False,
        "complete_zero_mode_projectors": False,
        "continuum_relative_heat_supertrace": False,
    }
    return {
        "version": VERSION,
        "DQ_H_tensor_formula_derived": True,
        "DQ_H_adjoint_derived": True,
        "two_cap_trace_tensor_formula_derived": True,
        "trace_adjoint_derived": True,
        "round_common_seam_tensor_attachment_lift_derived": True,
        "round_first_shape_kernel_proved": True,
        "required_for_physical_closure": required,
        "all_physical_provenance_inputs_present": all(required.values()),
        "postcomparison_parameter_choice_allowed": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    p = provenance_gate_payload()
    required = {
        "physical_global_tensor_attachment_operator": p["all_physical_provenance_inputs_present"],
        "action_selected_three_transverse_pair_wake_channels": False,
        "physical_nonabelian_holonomy": False,
        "complete_detector_projection_map": False,
        "blinded_targets_hash_frozen_before_prediction": False,
    }
    return {
        "version": VERSION,
        "required_inputs": required,
        "all_required_inputs_present": all(required.values()),
        "physical_execution_allowed": all(required.values()),
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "postcomparison_parameter_adjustment_allowed": False,
        "physical_mass_PMNS_splitting_or_probability_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "exact Schur-complement formula Q_H=A-B C^-1 B^T for the bundle-like metric block",
            "exact Frechet differential DQ_H",
            "exact Frobenius adjoint DQ_H^* and virtual-work identity",
            "DQ_H rank 15 and kernel 21 on the round fixed splitting",
            "generic bundle-like DQ_H remains rank 15 in the deterministic witness",
            "fixed cap trace differential and trace adjoint",
            "trace rank 10 and kernel 5",
            "trace composed with DQ_H has rank 10",
            "moving normal seam variation contributes 2 xi K",
            "round equator K=0 makes pure normal displacement invisible to first metric-trace variation",
            "round common Sym2(M4) channel lifts isometrically into M8/M5+/M5-/M4",
            "the duplicated two-cap compatibility complex has ten exact common-seam row reducibilities",
            "two attachment tangents times ten seam tensor modes give a rank-20 incidence subspace",
            "tensor Wentzell nonzero spectrum equals recovered attachment roots with multiplicity ten",
        ],
        "invalidated": [
            "claim that the v14.68 scalar incidence map was already the full tensor incidence map",
            "claim that round-equator first-order trace variation can generate physical normal moving-seam channels",
            "need to treat DQ_H or trace adjoints as undefined algebraically",
            "promotion of the round tensor theorem class to complete gauge-fixed physical Calderon closure",
        ],
        "reclassified": [
            "full tensor-map obstruction -> physical background and shape-response obstruction",
            "DQ_H and trace-map formulas -> algebraically closed on the metric sector",
            "moving-seam normal mode -> first-order kernel at the round equator",
            "two-cap compatibility multipliers -> reducible system with ten exact common-seam relations",
            "v14.68 scalar lift -> common-mode shadow of a 20-dimensional symmetric-tensor attachment lift",
        ],
        "open": [
            "action-selected nonround global stationary parent background",
            "action-selected regular child cap backgrounds",
            "physical K_ab on both caps",
            "second shape Hessian if K_ab remains zero",
            "three nonuniform moving-seam harmonic derivatives",
            "physical h_C and k_D from the same global solution",
            "full gauge-fixed metric Calderon operator",
            "gauge and ghost Calderon blocks",
            "spinor Calderon block and complete zero-mode projector",
            "continuum relative heat supertrace",
            "physical pair-wake Floquet BVP",
            "frozen no-retuning neutrino execution",
        ],
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "USB_touched": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def completion_gate_payload() -> dict[str, Any]:
    ranks = tensor_rank_payload()
    shape = round_shape_kernel_payload()
    tensor = tensor_incidence_payload()
    comp = compatibility_payload()
    prov = provenance_gate_payload()
    validation = {
        "DQ_H_rank_15": ranks["round_DQ_H_rank"] == 15 and ranks["generic_bundle_DQ_H_rank"] == 15,
        "DQ_H_kernel_21": ranks["round_DQ_H_kernel_dimension"] == 21,
        "trace_rank_10": ranks["trace_rank"] == 10,
        "chain_rank_10": ranks["trace_after_DQ_H_rank"] == 10,
        "DQ_H_finite_difference": ranks["generic_DQ_H_finite_difference_residual"] < 1e-7,
        "adjoint_identities": ranks["DQ_H_adjoint_virtual_work_residual"] < 1e-11 and ranks["trace_adjoint_virtual_work_residual"] < 1e-11,
        "round_shape_kernel": shape["pure_normal_round_response_norm"] == 0.0,
        "generic_shape_response_nonzero": shape["generic_nonzero_K_response_norm"] > 0.0,
        "tensor_incidence_rank_20": tensor["global_tensor_incidence_rank"] == 20,
        "tensor_incidence_isometric": tensor["global_tensor_incidence_isometry_residual"] < 1e-11,
        "tensor_Wentzell_rank_20": tensor["tensor_Wentzell_rank"] == 20,
        "tensor_Wentzell_spectrum": tensor["nonzero_spectrum_matches_attachment_roots_x10_residual"] < 1e-11,
        "compatibility_rank_40_with_10_reducibilities": comp["round_two_cap_compatibility_rank"] == 40 and comp["constraint_row_redundancy_dimension"] == 10 and comp["reducibility_identity_residual"] < 1e-11,
        "shape_columns_null_round": comp["pure_xi_plus_constraint_residual_norm"] == 0.0 and comp["pure_xi_minus_constraint_residual_norm"] == 0.0,
        "neutrino_fail_closed": neutrino_kill_screen_payload()["physical_execution_allowed"] is False,
        "BHSM_fail_closed": prov["all_physical_provenance_inputs_present"] is False,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_69",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "physical_execution_allowed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def next_object_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "why": [
            "the tensor DQ_H and trace formulas are now explicit, so algebraic incidence is no longer the blocker",
            "the round equator has K=0, making normal shape coordinates invisible at first order",
            "three physical moving-seam channels therefore require a nonround stationary background or second shape variation",
            "only after that can the complete gauge-fixed Calderon and heat-supertrace pipeline be physical",
        ],
        "forbidden_shortcut": "do not insert ad hoc K_ab, shape-channel amplitudes, measured neutrino data, or fitted mixing information",
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    payloads = {
        "BHSM_tensor_rank_gate_v14_69.json": tensor_rank_payload(),
        "BHSM_round_shape_kernel_v14_69.json": round_shape_kernel_payload(),
        "BHSM_tensor_attachment_incidence_v14_69.json": tensor_incidence_payload(),
        "BHSM_tensor_compatibility_gate_v14_69.json": compatibility_payload(),
        "BHSM_provenance_gate_v14_69.json": provenance_gate_payload(),
        "BHSM_neutrino_kill_screen_v14_69.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_69.json": status_payload(),
        "BHSM_completion_gate_v14_69.json": completion_gate_payload(),
        "BHSM_next_object_gate_v14_69.json": next_object_payload(),
    }
    return payloads


def materialize(directory: str | Path) -> list[Path]:
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = out / name
        path.write_bytes(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False).encode("utf-8") + b"\n")
        written.append(path)
    return written


__all__ = [
    "VERSION", "PRIMARY_VERDICT", "EXACT_NEXT_OBJECT", "sym_basis", "sym_coordinates",
    "sym_from_coordinates", "linear_map_matrix", "kk_metric_from_quotient",
    "horizontal_quotient_metric", "horizontal_quotient_differential", "horizontal_quotient_adjoint",
    "seam_embedding", "trace_metric", "trace_differential", "trace_adjoint",
    "moving_trace_differential", "round_metric8", "generic_bundle_metric8", "dq_matrix",
    "trace_matrix", "chain_matrix", "finite_difference_dq_residual", "dq_adjoint_residual",
    "trace_adjoint_residual", "tensor_rank_payload", "round_shape_kernel_payload",
    "round_common_tensor_lifts", "heterogeneous_tensor_incidence_isometry",
    "tensor_attachment_operator", "tensor_incidence_payload", "compatibility_jacobian_round", "compatibility_reducibility_matrix",
    "compatibility_payload", "provenance_gate_payload", "neutrino_kill_screen_payload",
    "status_payload", "completion_gate_payload", "next_object_payload", "artifact_payloads", "materialize",
]
