"""BHSM v14.68 global-envelopment curvature and attachment-incidence gate.

This sprint takes the corrected v11.4 common-attachment response recovered in
v14.67 and derives two missing structural ingredients from the already-owned
global-envelopment and compatibility architecture:

1. h_C and k_D are not independent local constants.  They are reduced Hessian
   quotients of the same globally stationary parent/child action.  In the v10
   degree-one radial truncation h_C reduces exactly to the stored breathing
   frequency formula.  In the global scale coordinate x_D=-log(upsilon), the
   physical depth curvature is the gauge/constraint-reduced Schur curvature
   of the full global Hessian, not the historical conditional value 1+octave.

2. The v7.1/v11.3 compatibility maps determine a canonical *reduced symmetric*
   incidence map from attachment tangent coordinates into the four-stratum
   M8/M5+/M5-/M4 vertex space.  On q=(q_C,q_W,x_D) with
       -q_C+q_W+x_D=0,
   the dynamic two-cap seam constraints give
       y=(q_C,q_W,q_W,q_W).
   Restricting to the exact KKT tangent basis gives a rank-two map J.  Its
   metric-canonical isometry E=J(J*J)^(-1/2) lifts the 2x2 attachment Wentzell
   response into the four-stratum boundary space without the uniform
   per-vertex placement or dimension doubling used only as a theorem witness
   in v14.67.

The resulting global coupled Wentzell operator is Hermitian positive
semidefinite and gives an exact self-adjoint boundary-triple domain in the
retained common-mode theorem class.  Its nonzero spectrum is exactly the
v11.4 attachment restoring spectrum.

Fail-closed boundary:
* the v10 profile numbers remain a proxy until the full global BVP selects the
  stationary profile and all action coefficients;
* the full tensor differential DQ_H, cap trace maps, and compatibility
  transports must still be evaluated on that stationary background;
* actual M8/M5/M4 tangential Calderon operators, complete gauge/ghost/zero
  mode projectors, continuum relative heat supertrace, and physical neutrino
  comparison remain open.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

import numpy as np

from bhsm.interface.completion.action_attachment_wentzell_v14_67 import (
    H_CORE_REPRESENTATIVE,
    attachment_response_roots,
    attachment_wentzell_response,
    tangent_basis,
    constraint_jacobian,
    inverse_sqrt_positive,
)
from bhsm.interface.completion.operator_valued_calderon_wentzell_v14_66 import (
    VERTICES,
    vertex_endpoint_indices,
    diagnostic_operator_data,
    diagnostic_vertex_gauges,
    gauge_transform_operator_data,
    gauge_transform_global_matrix,
    assemble_operator_weyl,
    boundary_green_form,
    matrix_heat_trace,
    matrix_logdet_positive,
)

VERSION = "v14.68"
PRIMARY_VERDICT = (
    "BHSM_V14_68_THE_GLOBAL_ENVELOPMENT_ACTION_RECLASSIFIES_H_CORE_AND_DEPTH_"
    "CURVATURE_AS_SCHUR_REDUCED_GLOBAL_HESSIAN_OUTPUTS_AND_THE_V7_1_V11_3_"
    "COMPATIBILITY_CHAIN_DERIVES_A_CANONICAL_RANK_TWO_SYMMETRIC_ATTACHMENT_"
    "INCIDENCE_MAP_INTO_THE_M8_M5_PLUS_M5_MINUS_M4_VERTEX_SPACE_SO_THE_"
    "RECOVERED_V11_4_WENTZELL_RESPONSE_CAN_BE_INSERTED_WITHOUT_UNIFORM_"
    "PLACEMENT_OR_MODE_DIMENSION_DOUBLING_BUT_FULL_PHYSICAL_CLOSURE_STILL_"
    "REQUIRES_THE_STATIONARY_TENSOR_DQ_H_TRACE_MAPS_ACTUAL_STRATUM_CALDERON_"
    "OPERATORS_COMPLETE_PROJECTORS_AND_CONTINUUM_RELATIVE_HEAT_SUPERTRACE"
)

EXACT_NEXT_OBJECT = (
    "FULL_TENSOR_EVALUATION_ON_THE_GLOBAL_STATIONARY_PARENT_CHILD_BACKGROUND_"
    "OF_DQ_H_THE_TWO_CAP_TRACE_MAPS_AND_COMPATIBILITY_TRANSPORTS_WITH_THE_"
    "SCHUR_REDUCED_GLOBAL_H_CORE_AND_K_D_INSERTED_INTO_THE_ACTUAL_M8_M5_"
    "PLUS_MINUS_M4_TANGENTIAL_CALDERON_OPERATORS_COMPLETE_GAUGE_GHOST_ZERO_"
    "MODE_PROJECTORS_CONTINUUM_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_NEUTRINO_"
    "KILL_SCREEN"
)

# v10.0 fixed-profile audit coefficients.  These reproduce the archived
# representative h_C but are explicitly proxy/profile-audit data, not physical
# stationary-profile outputs.
V10_PROXY = {
    "A2": 386.5944147001787,
    "A8": 222345.01532513634,
    "D2": 1900.581921090333,
    "D8": 1293643.725528066,
    "kappa1": 1.0,
}


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _positive(value: float, name: str) -> float:
    x = float(value)
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return x


def _hermitian(a: np.ndarray, name: str = "matrix", tol: float = 1e-11) -> np.ndarray:
    x = np.asarray(a, dtype=complex)
    if x.ndim != 2 or x.shape[0] != x.shape[1]:
        raise ValueError(f"{name} must be square")
    if np.linalg.norm(x - x.conj().T) > tol:
        raise ValueError(f"{name} must be Hermitian")
    return 0.5 * (x + x.conj().T)


# ---------------------------------------------------------------------------
# Global curvature outputs
# ---------------------------------------------------------------------------

def core_stationary_radius(kappa1: float, A2: float, A8: float) -> float:
    k = _positive(kappa1, "kappa1")
    a2 = _positive(A2, "A2")
    a8 = _positive(A8, "A8")
    return (a8 / (5.0 * k * a2)) ** (1.0 / 6.0)


def core_global_curvature(
    kappa1: float,
    A2: float,
    A8: float,
    D2: float,
    D8: float,
) -> tuple[float, float, float, float]:
    """Return (R*, V''(R*), M_RR(R*), h_C=V''/M_RR).

    This is the exact v10 degree-one p=2+p=8 radial truncation.  It becomes a
    physical h_C only when the global action selects the stationary profile
    whose integrals are A2,A8,D2,D8.
    """
    k = _positive(kappa1, "kappa1")
    a2 = _positive(A2, "A2")
    a8 = _positive(A8, "A8")
    d2 = _positive(D2, "D2")
    d8 = _positive(D8, "D8")
    r = core_stationary_radius(k, a2, a8)
    stiffness = 30.0 * k * a2 * r**3
    mass = k * d2 * r**5 + d8 / r
    return r, stiffness, mass, stiffness / mass


def global_scale_action_derivatives(
    x: float,
    power_coefficients: Mapping[int, float],
    z_log: float = 0.0,
) -> tuple[float, float, float]:
    """Return scale-dependent action contribution and first two x derivatives.

    Gamma(x)=sum_p A_p exp(p x)+Z x.  A scale-neutral B may be added without
    affecting either derivative and is intentionally omitted here.
    """
    xx = float(x)
    if not math.isfinite(xx):
        raise ValueError("x must be finite")
    z = float(z_log)
    if not math.isfinite(z):
        raise ValueError("z_log must be finite")
    value = z * xx
    first = z
    second = 0.0
    for p_raw, a_raw in power_coefficients.items():
        p = int(p_raw)
        a = float(a_raw)
        if p == 0 or not math.isfinite(a):
            raise ValueError("power coefficients require nonzero integer p and finite A_p")
        e = math.exp(p * xx)
        value += a * e
        first += p * a * e
        second += p * p * a * e
    return value, first, second


def schur_effective_curvature(
    hessian: np.ndarray,
    active_index: int = 0,
    eliminated_indices: Sequence[int] | None = None,
) -> float:
    """Gauge/constraint-reduced scalar curvature by exact Schur complement."""
    h = _hermitian(hessian, "global Hessian")
    n = h.shape[0]
    i = int(active_index)
    if not 0 <= i < n:
        raise ValueError("active_index out of range")
    if eliminated_indices is None:
        inds = [j for j in range(n) if j != i]
    else:
        inds = [int(j) for j in eliminated_indices]
    if i in inds or len(set(inds)) != len(inds) or any(not 0 <= j < n for j in inds):
        raise ValueError("invalid eliminated indices")
    if not inds:
        return float(h[i, i].real)
    hii = h[np.ix_(inds, inds)]
    ev = np.linalg.eigvalsh(hii)
    if float(np.min(ev)) <= 0.0:
        raise ValueError("eliminated Hessian block must be strictly positive")
    hxi = h[np.ix_([i], inds)]
    hix = h[np.ix_(inds, [i])]
    out = h[i, i] - (hxi @ np.linalg.solve(hii, hix))[0, 0]
    if abs(out.imag) > 1e-10:
        raise ValueError("Schur curvature is not real")
    return float(out.real)


def depth_global_curvature(
    x: float,
    power_coefficients: Mapping[int, float],
    z_log: float = 0.0,
    cross_vector: np.ndarray | None = None,
    interior_hessian: np.ndarray | None = None,
) -> float:
    """Return globally reduced k_D in the canonical x_D=-log(upsilon) coordinate.

    The direct second derivative is sum p^2 A_p exp(p x).  If the scale mode
    couples to other physical fields, their stationary response is eliminated
    by the Schur correction h_xi H_ii^{-1} h_ix.
    """
    _, _, direct = global_scale_action_derivatives(x, power_coefficients, z_log)
    if cross_vector is None and interior_hessian is None:
        return direct
    if cross_vector is None or interior_hessian is None:
        raise ValueError("cross_vector and interior_hessian must be supplied together")
    c = np.asarray(cross_vector, dtype=complex).reshape(-1)
    hi = _hermitian(interior_hessian, "interior Hessian")
    if hi.shape != (len(c), len(c)):
        raise ValueError("cross/interior dimensions mismatch")
    h = np.zeros((1 + len(c), 1 + len(c)), dtype=complex)
    h[0, 0] = direct
    h[0, 1:] = c.conj()
    h[1:, 0] = c
    h[1:, 1:] = hi
    return schur_effective_curvature(h, 0)


# ---------------------------------------------------------------------------
# Action-owned reduced symmetric incidence map
# ---------------------------------------------------------------------------

def scalar_stratum_incidence_map() -> np.ndarray:
    """Map (q_C,q_W,x_D) to (M8,M5+,M5-,M4) scalar amplitudes.

    I_C=Q_H(G8) supplies the M8/core amplitude.  Both cap wall incidences use
    the same q_W on the reflection-symmetric branch.  The two C54 constraints
    make the dynamic M4 seam metric share that wall amplitude.  x_D changes
    the reciprocal relation but has no independent vertex metric incidence.
    """
    return np.asarray(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )


def tangent_stratum_incidence() -> np.ndarray:
    j0 = scalar_stratum_incidence_map()
    n = tangent_basis()
    return j0 @ n


def canonical_incidence_isometry() -> np.ndarray:
    """Isometric embedding of the 2D attachment tangent into 4-stratum space."""
    j = tangent_stratum_incidence().astype(complex)
    gram = j.conj().T @ j
    return j @ inverse_sqrt_positive(gram)


def incidence_projector() -> np.ndarray:
    e = canonical_incidence_isometry()
    return e @ e.conj().T


def boundary_attachment_operator(
    mode_dim: int = 1,
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = 1.0,
) -> np.ndarray:
    d = int(mode_dim)
    if d < 1:
        raise ValueError("mode_dim must be positive")
    e = canonical_incidence_isometry()
    ed = np.kron(e, np.eye(d, dtype=complex))
    wa = np.kron(
        attachment_wentzell_response(h_core, depth_curvature),
        np.eye(d, dtype=complex),
    )
    out = ed @ wa @ ed.conj().T
    return _hermitian(out, "incidence-lifted attachment operator")


def coupled_wentzell_extension_matrices(dim: int, vertex_wentzell: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exact continuity + globally coupled Wentzell flux extension.

    The vertex operator W may couple different strata.  On the continuity
    subspace the flux equation is p_{v,1}+p_{v,2}+sum_w W_vw u_w=0.  Each
    target vertex value is represented by the average of its two equal edge
    endpoint traces.  Hermitian W yields AB*=BA*.
    """
    d = int(dim)
    if d < 1:
        raise ValueError("dim must be positive")
    w = _hermitian(vertex_wentzell, "vertex Wentzell")
    nv = len(VERTICES)
    if w.shape != (nv * d, nv * d):
        raise ValueError("vertex Wentzell dimension mismatch")
    endpoints = vertex_endpoint_indices()
    n_end = 2 * nv
    n = n_end * d
    a = np.zeros((n, n), dtype=complex)
    b = np.zeros((n, n), dtype=complex)
    I = np.eye(d, dtype=complex)
    row = 0
    for vi, vertex in enumerate(VERTICES):
        ie, je = endpoints[vertex]
        si = slice(ie * d, (ie + 1) * d)
        sj = slice(je * d, (je + 1) * d)
        rr = slice(row, row + d)
        a[rr, si] = I
        a[rr, sj] = -I
        row += d

        rr = slice(row, row + d)
        b[rr, si] = I
        b[rr, sj] = I
        for wi, target in enumerate(VERTICES):
            te1, te2 = endpoints[target]
            st1 = slice(te1 * d, (te1 + 1) * d)
            st2 = slice(te2 * d, (te2 + 1) * d)
            block = w[vi*d:(vi+1)*d, wi*d:(wi+1)*d]
            a[rr, st1] += 0.5 * block
            a[rr, st2] += 0.5 * block
        row += d
    return a, b


def sample_coupled_wentzell_domain_data(
    dim: int,
    vertex_wentzell: np.ndarray,
    seed: int = 1468,
) -> tuple[np.ndarray, np.ndarray]:
    d = int(dim)
    w = _hermitian(vertex_wentzell, "vertex Wentzell")
    if w.shape != (len(VERTICES) * d, len(VERTICES) * d):
        raise ValueError("vertex Wentzell dimension mismatch")
    rng = np.random.default_rng(seed)
    endpoints = vertex_endpoint_indices()
    u = rng.normal(size=len(VERTICES)*d) + 1j*rng.normal(size=len(VERTICES)*d)
    f = w @ u
    n_end = 2 * len(VERTICES)
    g0 = np.zeros(n_end*d, dtype=complex)
    g1 = np.zeros(n_end*d, dtype=complex)
    for vi, vertex in enumerate(VERTICES):
        ie, je = endpoints[vertex]
        si = slice(ie*d, (ie+1)*d)
        sj = slice(je*d, (je+1)*d)
        uv = u[vi*d:(vi+1)*d]
        p = rng.normal(size=d) + 1j*rng.normal(size=d)
        g0[si] = uv
        g0[sj] = uv
        g1[si] = p
        g1[sj] = -f[vi*d:(vi+1)*d] - p
    return g0, g1


def coupled_wentzell_diagnostics(mode_dim: int = 6) -> dict[str, Any]:
    w = boundary_attachment_operator(mode_dim)
    a, b = coupled_wentzell_extension_matrices(mode_dim, w)
    rank = int(np.linalg.matrix_rank(np.concatenate((a, b), axis=1)))
    comm = float(np.linalg.norm(a @ b.conj().T - b @ a.conj().T))
    f0, f1 = sample_coupled_wentzell_domain_data(mode_dim, w, 1468)
    g0, g1 = sample_coupled_wentzell_domain_data(mode_dim, w, 1469)
    green = boundary_green_form(f0, f1, g0, g1)
    ev = np.linalg.eigvalsh(w)
    nz = ev[ev > 1e-11]
    return {
        "boundary_dimension": int(a.shape[0]),
        "vertex_operator_dimension": int(w.shape[0]),
        "rank_A_B": rank,
        "ABstar_minus_BAstar_norm": comm,
        "sample_boundary_green_form_abs": float(abs(green)),
        "vertex_Wentzell_rank": int(np.linalg.matrix_rank(w, tol=1e-11)),
        "vertex_Wentzell_zero_mode_count": int(np.sum(np.abs(ev) <= 1e-11)),
        "minimum_nonzero_vertex_Wentzell_eigenvalue": float(np.min(nz)),
        "maximum_vertex_Wentzell_eigenvalue": float(np.max(ev)),
        "self_adjoint_extension_pass": bool(rank == a.shape[0] and comm < 1e-11 and abs(green) < 1e-10),
    }


# ---------------------------------------------------------------------------
# Retained operator-valued response with the incidence-derived Wentzell term
# ---------------------------------------------------------------------------

def diagnostic_lengths() -> dict[str, float]:
    return {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}


def incidence_response_operator() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ks, us, _ = diagnostic_operator_data()
    d = next(iter(ks.values())).shape[0]
    m = assemble_operator_weyl(diagnostic_lengths(), ks, us)
    w = boundary_attachment_operator(d)
    return _hermitian(m + w, "incidence response"), m, w


def incidence_response_gauge_covariance_residual() -> float:
    ks, us, _ = diagnostic_operator_data()
    d = next(iter(ks.values())).shape[0]
    h, m, w = incidence_response_operator()
    gauges = diagnostic_vertex_gauges(d)
    ksg, usg = gauge_transform_operator_data(ks, us, gauges)
    mg = assemble_operator_weyl(diagnostic_lengths(), ksg, usg)
    wg = gauge_transform_global_matrix(w, gauges)
    hg = _hermitian(mg + wg, "gauge transformed incidence response")
    expected = gauge_transform_global_matrix(h, gauges)
    return float(np.linalg.norm(hg - expected))


# ---------------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------------

def global_curvature_payload() -> dict[str, Any]:
    r, stiff, mass, h = core_global_curvature(**V10_PROXY)
    # Frozen theorem witness for the global x_D scale Hessian.  It is chosen
    # before evaluation and is not particle data.  x*=0 is stationary because
    # Z cancels the first derivative.
    powers = {8: 0.04, 6: -0.03, 3: 0.02}
    _, d1_no_z, d2 = global_scale_action_derivatives(0.0, powers, 0.0)
    z = -d1_no_z
    _, d1, _ = global_scale_action_derivatives(0.0, powers, z)
    hi = np.asarray([[2.1, 0.14], [0.14, 1.7]], dtype=float)
    cross = np.asarray([0.23, -0.11], dtype=float)
    kd = depth_global_curvature(0.0, powers, z, cross, hi)
    # Coordinate invariance check under an invertible change of eliminated variables.
    t = np.asarray([[1.3, 0.2], [-0.1, 0.9]], dtype=float)
    hi2 = t.T @ hi @ t
    cross2 = t.T @ cross
    kd2 = depth_global_curvature(0.0, powers, z, cross2, hi2)
    return {
        "version": VERSION,
        "core_curvature_definition": "h_C=V_RR/M_RR on the globally stationary core branch after physical reduction",
        "v10_radial_truncation": {
            "R_star": r,
            "V_RR": stiff,
            "M_RR": mass,
            "h_C_proxy": h,
            "archived_v11_4_h_C": H_CORE_REPRESENTATIVE,
            "match_residual": abs(h - H_CORE_REPRESENTATIVE),
            "profile_status": "V10_FIXED_PROFILE_PROXY_NOT_GLOBAL_STATIONARY_PHYSICAL_PROFILE",
        },
        "depth_curvature_definition": "k_D_eff=H_xx-H_xI H_II,perp^-1 H_Ix in canonical x_D=-log(upsilon)",
        "direct_scale_second_derivative": d2,
        "diagnostic_log_coefficient_Z": z,
        "diagnostic_stationarity_residual": abs(d1),
        "diagnostic_schur_depth_curvature": kd,
        "diagnostic_interior_basis_change_residual": abs(kd-kd2),
        "historical_k_D_equals_1_promoted_to_physical": False,
        "h_C_and_k_D_are_global_Hessian_outputs_not_independent_local_inputs": True,
        "physical_numerical_h_C_derived": False,
        "physical_numerical_k_D_derived": False,
        "physical_BHSM_prediction": False,
    }


def incidence_map_payload() -> dict[str, Any]:
    j0 = scalar_stratum_incidence_map()
    n = tangent_basis()
    j = tangent_stratum_incidence()
    e = canonical_incidence_isometry()
    p = incidence_projector()
    return {
        "version": VERSION,
        "source_chain": [
            "v7.1 I_C=Q_H(G8), I_W=id_5(g5), Lambda54(h-iota^*g5)",
            "v11.3 reciprocal matcher I_W=upsilon I_C",
            "x_D=-log(upsilon) so -q_C+q_W+x_D=0",
            "two-cap reflection-symmetric dynamic seam reduction",
        ],
        "coordinate_order": ["q_C", "q_W", "x_D"],
        "vertex_order": list(VERTICES),
        "constraint_jacobian": constraint_jacobian().tolist(),
        "tangent_basis": n.tolist(),
        "scalar_vertex_map_J0": j0.tolist(),
        "tangent_vertex_map_J": j.tolist(),
        "J_rank": int(np.linalg.matrix_rank(j)),
        "J_star_J": (j.T @ j).tolist(),
        "canonical_isometry_E": [[float(z.real) for z in row] for row in e],
        "E_star_E_residual": float(np.linalg.norm(e.conj().T @ e - np.eye(2))),
        "incidence_projector_rank": int(np.linalg.matrix_rank(p, tol=1e-12)),
        "incidence_projector_idempotence_residual": float(np.linalg.norm(p @ p - p)),
        "uniform_per_vertex_placement_required": False,
        "attachment_mode_dimension_doubling_required": False,
        "reduced_symmetric_incidence_map_closed": True,
        "full_tensor_DQ_H_and_trace_maps_evaluated_on_physical_background": False,
        "physical_BHSM_prediction": False,
    }


def coupled_wentzell_payload() -> dict[str, Any]:
    d = 6
    w = boundary_attachment_operator(d)
    ev = np.linalg.eigvalsh(w)
    nonzero = ev[ev > 1e-11]
    roots = np.asarray(attachment_response_roots())
    expected = np.sort(np.repeat(roots, d))
    diag = coupled_wentzell_diagnostics(d)
    return {
        "version": VERSION,
        "mode_dimension": d,
        "vertex_mode_dimension": d,
        "vertex_operator_dimension": int(w.shape[0]),
        "nonzero_attachment_eigenvalues": nonzero.tolist(),
        "nonzero_spectrum_matches_attachment_roots_residual": float(np.max(np.abs(nonzero-expected))),
        "rank_expected_2d": int(2*d),
        "rank_actual": int(np.linalg.matrix_rank(w, tol=1e-11)),
        "W_hermiticity_residual": float(np.linalg.norm(w-w.conj().T)),
        "W_positive_semidefinite": bool(np.min(ev) > -1e-12),
        "self_adjoint_domain": diag,
        "v14_67_uniform_vertex_lift_superseded_in_reduced_symmetric_sector": True,
        "full_physical_tensor_incidence_claim": False,
        "physical_BHSM_prediction": False,
    }


def operator_insertion_payload() -> dict[str, Any]:
    h, m, w = incidence_response_operator()
    ev = np.linalg.eigvalsh(h)
    ev0 = np.linalg.eigvalsh(m)
    t = 0.55
    return {
        "version": VERSION,
        "response_dimension": int(h.shape[0]),
        "v14_67_uniform_lift_response_dimension": 48,
        "no_mode_dimension_doubling": h.shape[0] == 24,
        "response_hermiticity_residual": float(np.linalg.norm(h-h.conj().T)),
        "response_minimum_eigenvalue": float(np.min(ev)),
        "baseline_minimum_eigenvalue": float(np.min(ev0)),
        "attachment_operator_rank": int(np.linalg.matrix_rank(w, tol=1e-11)),
        "vertex_gauge_covariance_residual_when_attachment_transport_is_transformed": incidence_response_gauge_covariance_residual(),
        "diagnostic_heat_trace_increment": matrix_heat_trace(h, t)-matrix_heat_trace(m, t),
        "diagnostic_logdet_increment": matrix_logdet_positive(h)-matrix_logdet_positive(m),
        "actual_physical_M8_M5_M4_tangential_operators_inserted": False,
        "complete_physical_projectors_inserted": False,
        "continuum_relative_heat_supertrace_computed": False,
        "physical_BHSM_prediction": False,
    }


def provenance_gate_payload() -> dict[str, Any]:
    required = {
        "global_stationary_profile_selects_A2_A8_D2_D8_and_h_C": False,
        "global_stationary_full_Hessian_selects_physical_k_D_eff": False,
        "full_tensor_DQ_H_evaluated_on_stationary_M8_background": False,
        "full_two_cap_trace_maps_evaluated_on_stationary_M5_backgrounds": False,
        "compatibility_transport_between_stratum_tangential_Hilbert_spaces": False,
        "actual_M8_M5plus_M5minus_M4_tangential_Calderon_operators": False,
        "complete_gauge_ghost_zero_mode_projectors": False,
        "continuum_relative_heat_supertrace": False,
    }
    return {
        "version": VERSION,
        "global_curvature_functionals_derived": True,
        "reduced_symmetric_incidence_map_derived": True,
        "canonical_incidence_Wentzell_lift_derived": True,
        "required_for_physical_closure": required,
        "all_physical_provenance_inputs_present": all(required.values()),
        "postcomparison_parameter_choice_allowed": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    p = provenance_gate_payload()
    required = {
        "physical_global_attachment_operator": p["all_physical_provenance_inputs_present"],
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
            "The v10 radial h_C formula is exactly a potential-Hessian over kinetic-Gram quotient.",
            "The archived v10 fixed-profile proxy reproduces the corrected v11.4 h_C representative.",
            "The global depth curvature is the Schur-reduced x_D Hessian, not an independent octave constant.",
            "Schur-reduced depth curvature is invariant under invertible changes of eliminated-field coordinates.",
            "The v7.1/v11.3 compatibility chain fixes the reduced symmetric vertex incidence y=(q_C,q_W,q_W,q_W).",
            "Restriction to the exact reciprocal KKT tangent gives a rank-two incidence map.",
            "The metric-canonical incidence isometry E=J(J*J)^-1/2 is unique for the declared Euclidean retained boundary metric.",
            "The incidence-lifted four-stratum Wentzell operator has exactly the two attachment restoring roots as its nonzero spectrum.",
            "A globally coupled Hermitian Wentzell operator satisfies the exact self-adjoint boundary-triple criterion.",
            "The incidence construction removes the v14.67 theorem-only uniform per-vertex lift and avoids doubling the retained mode dimension.",
            "The retained operator response changes under the incidence-derived attachment term without measured-data tuning.",
        ],
        "invalidated": [
            "h_C and k_D should be treated as independent local constants in the final global theory.",
            "The historical k_D=1 ground assignment may be promoted to a physical result before the global Hessian is evaluated.",
            "The recovered 2D attachment response must be copied uniformly to all four vertices.",
            "The attachment tangent factor must double the physical tangential Hilbert-space dimension.",
        ],
        "reclassified": [
            "h_C is a global stationary radial Hessian quotient; its archived numerical value is still proxy/selected-branch data.",
            "k_D is a global Schur curvature in x_D=-log(upsilon), with the historical octave value demoted to a conditional witness.",
            "The incidence-placement blocker is structurally closed in the reflection-symmetric scalar amplitude sector.",
            "The remaining incidence blocker is evaluation of the full tensor DQ_H/trace/transport operators on the physical stationary background.",
        ],
        "open": [
            "solve the full global stationary parent/child profile and coefficients",
            "evaluate physical h_C from that profile",
            "evaluate physical Schur-reduced k_D from the same Hessian",
            "evaluate tensor DQ_H on the stationary M8 background",
            "evaluate both M5 cap trace differentials and common M4 seam map",
            "derive the inter-stratum compatibility transports in the retained physical Hilbert spaces",
            "insert actual M8/M5/M4 tangential Calderon operators",
            "derive complete gauge/ghost/zero-mode projectors",
            "derive the physical non-Abelian holonomy",
            "derive action-selected moving-seam/pair-wake channel amplitudes and phases",
            "compute the continuum relative heat supertrace",
            "run the frozen no-retuning neutrino kill screen only after all provenance gates close",
        ],
    }


def completion_gate_payload() -> dict[str, Any]:
    prov = provenance_gate_payload()
    kill = neutrino_kill_screen_payload()
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "usb_touched": False,
        "global_h_C_functional_derived": True,
        "global_k_D_Schur_functional_derived": True,
        "reduced_symmetric_incidence_map_closed": True,
        "incidence_derived_self_adjoint_Wentzell_domain_closed_in_retained_theorem_class": True,
        "physical_full_tensor_incidence_closed": False,
        "physical_global_attachment_operator_closed": prov["all_physical_provenance_inputs_present"],
        "continuum_relative_heat_supertrace_closed": False,
        "neutrino_physical_execution_allowed": kill["physical_execution_allowed"],
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def next_object_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "highest_upstream_blocker": "evaluation of the full tensor compatibility differential and global Schur Hessian on the physical stationary parent/child background",
        "closed_in_v14_68": [
            "global Hessian functional definition of h_C",
            "global Schur-Hessian functional definition of k_D",
            "demotion of historical k_D=1 to conditional witness status",
            "reduced symmetric four-stratum incidence map from v7.1/v11.3 compatibility",
            "canonical metric incidence isometry",
            "globally coupled self-adjoint Wentzell lift without uniform placement",
            "operator-valued retained response insertion without mode-dimension doubling",
        ],
        "postcomparison_choice_forbidden": True,
    }


def master_payload() -> dict[str, Any]:
    p = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "global_curvature": global_curvature_payload(),
        "incidence_map": incidence_map_payload(),
        "coupled_wentzell": coupled_wentzell_payload(),
        "operator_insertion": operator_insertion_payload(),
        "provenance_gate": provenance_gate_payload(),
        "neutrino_kill_screen": neutrino_kill_screen_payload(),
    }
    p["sha256_without_self_hash"] = sha256_payload(p)
    return p


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_global_attachment_incidence_curvature_v14_68.json": master_payload(),
        "BHSM_global_curvature_gate_v14_68.json": global_curvature_payload(),
        "BHSM_attachment_incidence_map_v14_68.json": incidence_map_payload(),
        "BHSM_coupled_wentzell_gate_v14_68.json": coupled_wentzell_payload(),
        "BHSM_operator_insertion_gate_v14_68.json": operator_insertion_payload(),
        "BHSM_provenance_gate_v14_68.json": provenance_gate_payload(),
        "BHSM_neutrino_kill_screen_v14_68.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_68.json": status_payload(),
        "BHSM_next_object_gate_v14_68.json": next_object_payload(),
        "BHSM_completion_gate_v14_68.json": completion_gate_payload(),
    }


def materialize(out_dir: Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        p = out / name
        p.write_bytes(canonical_json_bytes(payload) + b"\n")
        written.append(p)
    return written
