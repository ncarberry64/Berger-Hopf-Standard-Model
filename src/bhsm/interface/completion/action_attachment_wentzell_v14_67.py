"""BHSM v14.67 recovered action-normalized attachment Gram-Hessian gate.

This sprint recovers the corrected v11.4 common-attachment response from the
2026-08-03 provenance branch and inserts that response into the v14.66
operator-valued Calderon/Wentzell theorem class without promoting its
conditional source data to physical predictions.

The authoritative corrected v11.4 coordinates are
    q=(q_C,q_W,x_D=q_D/lambda_D),
with action-whitened kinetic Gram K=I_3, reciprocal matcher
    B=(-1,1,1),
and tangent basis
    N=[[1,1],[1,0],[0,1]].
For positive core curvature h_C and depth curvature k_D>0,
    H=diag(h_C,0,k_D).
The KKT tangent pencil is therefore
    K_parallel=N^T K N=[[2,1],[1,2]],
    H_parallel=N^T H N=[[h_C,h_C],[h_C,h_C+k_D]].
The generalized restoring roots are positive and simple:
    mu_±=(h_C+k_D ± sqrt(h_C^2-h_C k_D+k_D^2))/3.

The canonical kinetic-whitened attachment response is
    W_att=K_parallel^{-1/2} H_parallel K_parallel^{-1/2}.
It is Hermitian positive for h_C,k_D>0 and has eigenvalues mu_±.  Tensoring
W_att with a retained tangential mode block gives a mathematically admissible
self-adjoint Wentzell term.  This removes the arbitrary diagnostic Schur block
used in v14.66 at theorem level.

Fail-closed boundary:
* h_C is only action-derived on the selected finite-radius core branch in the
  recovered v11.4 source; the global-envelopment branch must select it.
* k_D=1+octave was recorded as a conditional spectral-action assignment.
* the physical incidence map placing the 2D attachment tangent response into
  the full M8/M5±/M4 Calderon domain remains to be derived.
* actual M8/M5/M4 tangential operators, complete projectors, continuum heat
  supertrace, and physical neutrino comparison remain open.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any, Mapping

import numpy as np

from bhsm.interface.completion.operator_valued_calderon_wentzell_v14_66 import (
    VERTICES,
    EDGE_NAMES,
    diagnostic_operator_data,
    assemble_operator_weyl,
    block_diag,
    wentzell_extension_matrices,
    boundary_green_form,
    diagnostic_zero_modes,
    orthogonal_complement_basis,
    matrix_heat_trace,
    matrix_logdet_positive,
)

VERSION = "v14.67"
H_CORE_REPRESENTATIVE = 0.181391690148362
GROUND_DEPTH_CURVATURE = 1.0
SOURCE_PR = 218
SOURCE_COMMIT = "013ea158103e39e73ce88da77a4914a5e3c8c49c"
SOURCE_PATH = "src/bhsm/interface/completion/common_attachment_response_v11_4.py"

PRIMARY_VERDICT = (
    "BHSM_V14_67_THE_ARCHIVE_ALREADY_CONTAINS_A_CORRECTED_ACTION_WHITENED_"
    "COMMON_ATTACHMENT_GRAM_HESSIAN_ON_A_SELECTED_FINITE_RADIUS_CORE_BRANCH_"
    "AND_ITS_KKT_TANGENT_RESPONSE_CAN_REPLACE_THE_ARBITRARY_V14_66_WENTZELL_"
    "SCHUR_WITNESS_IN_THE_OPERATOR_VALUED_THEOREM_CLASS_BUT_PHYSICAL_CLOSURE_"
    "STILL_REQUIRES_GLOBAL_ENVELOPMENT_DERIVATION_OF_H_CORE_AND_DEPTH_"
    "CURVATURE_PLUS_THE_ACTION_OWNED_INCIDENCE_MAP_INTO_THE_FULL_CALDERON_DOMAIN"
)

RECONCILIATION_VERDICT = (
    "BHSM_V14_67_THE_CORRECTED_V11_4_IMPLEMENTATION_MUST_TAKE_PRECEDENCE_OVER_"
    "THE_EARLIER_UNWHITENED_MANUAL_PACKET_PENCIL_BECAUSE_ONE_SHARED_WHITENING_"
    "MAP_MUST_BE_APPLIED_TO_BOTH_THE_KINETIC_GRAM_AND_THE_HESSIAN"
)

EXACT_NEXT_OBJECT = (
    "GLOBAL_ENVELOPMENT_DERIVATION_OF_THE_COMMON_ATTACHMENT_H_CORE_AND_DEPTH_"
    "CURVATURE_WITH_ACTION_OWNED_DIFFERENTIAL_INCIDENCE_MAP_FROM_THE_TWO_"
    "DIMENSIONAL_KKT_TANGENT_RESPONSE_INTO_THE_M8_M5_PLUS_MINUS_M4_CALDERON_"
    "DOMAIN_THEN_ACTUAL_STRATUM_TANGENTIAL_OPERATORS_COMPLETE_PROJECTORS_"
    "CONTINUUM_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_NEUTRINO_KILL_SCREEN"
)


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


def _positive(x: float, name: str) -> float:
    y = float(x)
    if not math.isfinite(y) or y <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return y


def constraint_jacobian() -> np.ndarray:
    return np.asarray([[-1.0, 1.0, 1.0]], dtype=float)


def tangent_basis() -> np.ndarray:
    return np.asarray([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]], dtype=float)


def action_whitened_kinetic() -> np.ndarray:
    return np.eye(3, dtype=float)


def action_whitened_hessian(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> np.ndarray:
    h = _positive(h_core, "h_core")
    k = _positive(depth_curvature, "depth_curvature")
    return np.diag([h, 0.0, k]).astype(float)


def reduced_attachment_matrices(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> tuple[np.ndarray, np.ndarray]:
    n = tangent_basis()
    kg = n.T @ action_whitened_kinetic() @ n
    hh = n.T @ action_whitened_hessian(h_core, depth_curvature) @ n
    return kg, hh


def attachment_characteristic_coefficients(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> tuple[float, float, float]:
    h = _positive(h_core, "h_core")
    k = _positive(depth_curvature, "depth_curvature")
    # det(H_parallel-mu K_parallel)=3 mu^2-2(h+k) mu+h k
    return 3.0, -2.0 * (h + k), h * k


def attachment_response_roots(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> tuple[float, float]:
    h = _positive(h_core, "h_core")
    k = _positive(depth_curvature, "depth_curvature")
    d = h * h - h * k + k * k
    s = math.sqrt(d)
    return (h + k - s) / 3.0, (h + k + s) / 3.0


def inverse_sqrt_positive(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=complex)
    if x.ndim != 2 or x.shape[0] != x.shape[1]:
        raise ValueError("matrix must be square")
    if np.linalg.norm(x - x.conj().T) > 1e-12:
        raise ValueError("matrix must be Hermitian")
    w, v = np.linalg.eigh(0.5 * (x + x.conj().T))
    if float(np.min(w)) <= 0.0:
        raise ValueError("matrix must be strictly positive")
    return (v * (1.0 / np.sqrt(w))) @ v.conj().T


def attachment_wentzell_response(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> np.ndarray:
    kg, hh = reduced_attachment_matrices(h_core, depth_curvature)
    r = inverse_sqrt_positive(kg)
    w = r @ hh @ r
    return 0.5 * (w + w.conj().T)


def attachment_generalized_eigenvectors(
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> tuple[np.ndarray, np.ndarray]:
    """Return K-normalized tangent eigenvectors and roots.

    Columns are vectors in the original 3-coordinate attachment space and
    satisfy B v=0 and v_i^* K v_j=delta_ij with K=I_3.
    """
    kg, hh = reduced_attachment_matrices(h_core, depth_curvature)
    r = inverse_sqrt_positive(kg)
    w = r @ hh @ r
    vals, vecs = np.linalg.eigh(w)
    tangent_coeff = r @ vecs
    full = tangent_basis() @ tangent_coeff
    # Full vectors are K=I normalized because coeff^* K_parallel coeff=I.
    return np.asarray(full, dtype=complex), np.asarray(vals, dtype=float)


def lifted_attachment_wentzell(
    mode_dim: int,
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> np.ndarray:
    d = int(mode_dim)
    if d < 1:
        raise ValueError("mode_dim must be positive")
    return np.kron(attachment_wentzell_response(h_core, depth_curvature), np.eye(d, dtype=complex))


def lifted_operator_data() -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, float]]:
    """Lift the v14.66 diagnostic common-mode blocks by the 2D attachment tangent factor."""
    ks, us, betas = diagnostic_operator_data()
    kt = {name: np.kron(np.eye(2, dtype=complex), k) for name, k in ks.items()}
    ut = {name: np.kron(np.eye(2, dtype=complex), u) for name, u in us.items()}
    return kt, ut, betas


def uniform_theorem_wentzell_blocks(
    mode_dim: int = 6,
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> dict[str, np.ndarray]:
    """Uniform theorem-class placement of W_att on all four diamond vertices.

    This is intentionally only an admissibility/insertion witness.  The
    physical differential incidence map deciding where/how the attachment
    tangent response enters the M8/M5±/M4 boundary space remains open.
    """
    w = lifted_attachment_wentzell(mode_dim, h_core, depth_curvature)
    return {v: w.copy() for v in VERTICES}


def uniform_wentzell_diagnostics(
    mode_dim: int = 6,
    h_core: float = H_CORE_REPRESENTATIVE,
    depth_curvature: float = GROUND_DEPTH_CURVATURE,
) -> dict[str, Any]:
    ws = uniform_theorem_wentzell_blocks(mode_dim, h_core, depth_curvature)
    d = 2 * int(mode_dim)
    a, b = wentzell_extension_matrices(d, ws)
    rank = int(np.linalg.matrix_rank(np.concatenate((a, b), axis=1)))
    comm = float(np.linalg.norm(a @ b.conj().T - b @ a.conj().T))
    ev = np.linalg.eigvalsh(next(iter(ws.values())))
    return {
        "boundary_dimension": int(a.shape[0]),
        "rank_A_B": rank,
        "ABstar_minus_BAstar_norm": comm,
        "minimum_lifted_Wentzell_eigenvalue": float(np.min(ev)),
        "maximum_lifted_Wentzell_eigenvalue": float(np.max(ev)),
        "self_adjoint_extension_pass": rank == a.shape[0] and comm < 1e-11,
        "physical_incidence_placement_claim": False,
    }


def sample_uniform_wentzell_domain_data(
    mode_dim: int = 6,
    seed: int = 1467,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    d = 2 * int(mode_dim)
    n_end = 8
    g0 = np.zeros(n_end * d, dtype=complex)
    g1 = np.zeros(n_end * d, dtype=complex)
    ws = uniform_theorem_wentzell_blocks(mode_dim)
    # endpoint layout inherited from v14.66 diamond:
    by_vertex = {
        "M8": (0, 7),
        "M5_plus": (1, 2),
        "M5_minus": (4, 6),
        "M4": (3, 5),
    }
    for vertex in VERTICES:
        i_ep, j_ep = by_vertex[vertex]
        si = slice(i_ep * d, (i_ep + 1) * d)
        sj = slice(j_ep * d, (j_ep + 1) * d)
        u = rng.normal(size=d) + 1j * rng.normal(size=d)
        p = rng.normal(size=d) + 1j * rng.normal(size=d)
        g0[si] = u
        g0[sj] = u
        g1[si] = p
        g1[sj] = -ws[vertex] @ u - p
    return g0, g1


def lifted_response_operator(
    lengths: Mapping[str, float] | None = None,
) -> np.ndarray:
    ks, us, _ = lifted_operator_data()
    if lengths is None:
        lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    m = assemble_operator_weyl(lengths, ks, us)
    w = block_diag([uniform_theorem_wentzell_blocks(6)[v] for v in VERTICES])
    h = m + w
    return 0.5 * (h + h.conj().T)


def lifted_projected_response() -> tuple[np.ndarray, np.ndarray]:
    h = lifted_response_operator()
    # Remove the same two theorem-only global modes, now in a 12-dimensional
    # common endpoint block.  This is not the physical ghost/projector system.
    z = diagnostic_zero_modes(12)
    q = orthogonal_complement_basis(z, h.shape[0])
    hp = q.conj().T @ h @ q
    return 0.5 * (hp + hp.conj().T), q


def recovered_gram_hessian_payload() -> dict[str, Any]:
    kg, hh = reduced_attachment_matrices()
    roots = attachment_response_roots()
    full_vecs, vals = attachment_generalized_eigenvectors()
    b = constraint_jacobian()
    return {
        "version": VERSION,
        "source": {
            "pull_request": SOURCE_PR,
            "commit": SOURCE_COMMIT,
            "path": SOURCE_PATH,
            "recovered_version": "v11.4",
        },
        "classification_recovered": "DERIVED_ON_AUTHOR_SELECTED_FINITE_RADIUS_CORE_BRANCH",
        "coordinate_order": ["q_C", "q_W", "x_D=q_D/lambda_D"],
        "constraint_jacobian": constraint_jacobian().tolist(),
        "tangent_basis": tangent_basis().tolist(),
        "action_whitened_kinetic": action_whitened_kinetic().tolist(),
        "representative_action_whitened_hessian": action_whitened_hessian().tolist(),
        "reduced_kinetic": kg.tolist(),
        "reduced_hessian": hh.tolist(),
        "representative_roots": list(roots),
        "representative_eigenvalue_residual": float(np.max(np.abs(vals - np.asarray(roots)))),
        "constraint_tangent_eigenvector_residual": float(np.linalg.norm(b @ full_vecs)),
        "K_normalization_residual": float(np.linalg.norm(full_vecs.conj().T @ full_vecs - np.eye(2))),
        "source_ledger": {
            "kinetic_gram": "ACTION_WHITENED_CONDITIONAL",
            "core_curvature": "ACTION_DERIVED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH",
            "wall_curvature": "ACTION_DERIVED_AT_CRITICAL_WALL_BRANCH",
            "depth_curvature": "CONDITIONAL_SPECTRAL_ACTION_ASSIGNMENT",
            "constraint": "ACTION_DERIVED",
        },
        "physical_unconditional_Gram_Hessian_claim": False,
        "physical_BHSM_prediction": False,
    }


def normalization_reconciliation_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "verdict": RECONCILIATION_VERDICT,
        "adopted_coordinate_rule": "K_white=W^T K_action W and H_white=W^T H_action W with the same W",
        "recovered_v11_4_shared_whitening_map": "identity in already action-whitened coordinates",
        "earlier_manual_unwhitened_packet_pencil_authoritative": False,
        "mixed_whitened_unwhitened_pencil_forbidden": True,
        "reason": "generalized eigenvalues are coordinate invariant only when both quadratic forms are transformed by the same invertible map",
        "physical_BHSM_prediction": False,
    }


def attachment_wentzell_payload() -> dict[str, Any]:
    w = attachment_wentzell_response()
    roots = np.asarray(attachment_response_roots())
    ev = np.linalg.eigvalsh(w)
    d = uniform_wentzell_diagnostics()
    f0, f1 = sample_uniform_wentzell_domain_data(6, 1467)
    g0, g1 = sample_uniform_wentzell_domain_data(6, 1468)
    green = boundary_green_form(f0, f1, g0, g1)
    return {
        "version": VERSION,
        "attachment_response_matrix": [[float(x.real) for x in row] for row in w],
        "attachment_response_eigenvalues": ev.tolist(),
        "generalized_root_match_residual": float(np.max(np.abs(ev - roots))),
        "attachment_response_hermiticity_residual": float(np.linalg.norm(w - w.conj().T)),
        "attachment_response_positive": bool(np.min(ev) > 0.0),
        "uniform_theorem_lift": d,
        "sample_boundary_green_form_abs": float(abs(green)),
        "arbitrary_v14_66_diagnostic_Schur_block_needed_for_this_theorem_lift": False,
        "physical_diamond_incidence_map_derived": False,
        "physical_BHSM_prediction": False,
    }


def operator_response_insertion_payload() -> dict[str, Any]:
    ks, us, betas = lifted_operator_data()
    h = lifted_response_operator()
    hp, q = lifted_projected_response()
    d = next(iter(ks.values())).shape[0]
    t = 0.55
    # A comparison reference with Wentzell response removed, used only to
    # prove the recovered attachment term changes the operator response.
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    m0 = assemble_operator_weyl(lengths, ks, us)
    m0p = q.conj().T @ m0 @ q
    return {
        "version": VERSION,
        "lifted_common_mode_dimension": d,
        "berger_beta_diagnostic": betas,
        "response_dimension": int(h.shape[0]),
        "projected_dimension": int(hp.shape[0]),
        "response_hermiticity_residual": float(np.linalg.norm(h - h.conj().T)),
        "response_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(h))),
        "projected_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(hp))),
        "QstarQ_residual": float(np.linalg.norm(q.conj().T @ q - np.eye(q.shape[1]))),
        "diagnostic_attachment_increment_heat_trace": matrix_heat_trace(hp, t) - matrix_heat_trace(m0p, t),
        "diagnostic_attachment_increment_logdet": matrix_logdet_positive(hp) - matrix_logdet_positive(m0p),
        "actual_M8_M5_M4_tangential_operators_inserted": False,
        "complete_physical_projectors_inserted": False,
        "full_continuum_relative_heat_supertrace_computed": False,
        "physical_BHSM_prediction": False,
    }


def provenance_gate_payload() -> dict[str, Any]:
    required = {
        "global_envelopment_selects_h_core_without_author_branch_choice": False,
        "depth_curvature_derived_from_same_global_action_not_conditional_spectral_assignment": False,
        "common_attachment_differential_incidence_map_into_M8_M5plus_M5minus_M4_domain": False,
        "actual_M8_tangential_Calderon_operator": False,
        "actual_M5plus_M5minus_cap_Calderon_operators": False,
        "actual_intrinsic_M4_tangential_operator": False,
        "complete_gauge_ghost_zero_mode_Calderon_projectors": False,
        "continuum_relative_heat_supertrace": False,
    }
    return {
        "version": VERSION,
        "recovered_algebraic_Gram_Hessian_available": True,
        "recovered_Gram_Hessian_unconditional_physical": False,
        "required_for_physical_closure": required,
        "all_physical_provenance_inputs_present": all(required.values()),
        "postcomparison_parameter_choice_allowed": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    provenance = provenance_gate_payload()
    required = {
        "unconditional_physical_common_attachment_response": provenance["all_physical_provenance_inputs_present"],
        "global_stationary_parent_child_background": False,
        "action_selected_three_transverse_moving_seam_channels": False,
        "action_selected_nonabelian_holonomy": False,
        "complete_physical_projectors": False,
        "continuum_relative_heat_supertrace": False,
        "physical_detector_projection_map": False,
        "blinded_targets_hash_frozen_before_prediction": False,
    }
    return {
        "version": VERSION,
        "required_inputs": required,
        "all_required_inputs_present": all(required.values()),
        "physical_execution_allowed": all(required.values()),
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "postcomparison_parameter_adjustment_allowed": False,
        "physical_mass_PMNS_or_splitting_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "The v11.4 provenance branch already contains the corrected action-whitened common-attachment response.",
            "The reciprocal matcher is B=(-1,1,1) on coordinates (q_C,q_W,x_D).",
            "The exact KKT tangent kinetic matrix is [[2,1],[1,2]].",
            "For h_C>0 and k_D>0 the exact KKT tangent Hessian is positive and nondegenerate.",
            "The restoring roots are mu_±=(h_C+k_D±sqrt(h_C^2-h_C k_D+k_D^2))/3.",
            "Kinetic whitening produces a unique positive Hermitian 2x2 attachment response with exactly those eigenvalues.",
            "Tensoring the recovered attachment response with the retained common mode gives an exact self-adjoint Wentzell theorem-class domain.",
            "The recovered response changes the finite operator heat/logdet diagnostic without any measured-data tuning.",
        ],
        "invalidated": [
            "The BHSM archive contains no evaluated common-attachment Gram-Hessian at all.",
            "The arbitrary diagnostic KKT Schur block used in v14.66 is still mathematically necessary after v11.4 recovery.",
            "The earlier manual unwhitened packet pencil can be mixed with the corrected v11.3-whitened Gram matrix.",
        ],
        "reclassified": [
            "The Gram-Hessian blocker is now provenance/global-selection rather than missing algebra.",
            "The v11.4 numerical h_C is a representative selected-branch value, not a universal physical constant.",
            "The depth octave entry is conditional spectral-action data until derived from the global microscopic action.",
            "Placement of W_att in the four-stratum Calderon boundary space is an incidence-map theorem, not a free Wentzell choice.",
        ],
        "open": [
            "derive h_C from the global stationary envelopment solution",
            "derive k_D from the same microscopic/global action",
            "derive the differential incidence map from the attachment tangent bundle to M8/M5±/M4 boundary data",
            "insert actual M8 tangential Calderon operator",
            "insert actual M5 plus/minus cap operators",
            "insert actual intrinsic M4 operator",
            "derive complete gauge/ghost/zero-mode Calderon projectors",
            "derive action-selected non-Abelian holonomy",
            "derive three transverse moving-seam channel amplitudes and phases",
            "compute the continuum relative heat supertrace",
            "exhaust global stationary branches and the gauge-reduced Hessian",
            "run the frozen no-retuning neutrino kill screen only afterward",
        ],
    }


def completion_gate_payload() -> dict[str, Any]:
    kill = neutrino_kill_screen_payload()
    provenance = provenance_gate_payload()
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_prediction_emitted": False,
        "usb_touched": False,
        "recovered_corrected_v11_4_Gram_Hessian": True,
        "action_whitened_KKT_tangent_response_closed_symbolically": True,
        "retained_mode_self_adjoint_Wentzell_lift_closed": True,
        "physical_unconditional_common_attachment_response_closed": provenance["all_physical_provenance_inputs_present"],
        "physical_continuum_operator_domain_closed": False,
        "physical_continuum_relative_heat_supertrace_closed": False,
        "neutrino_physical_execution_allowed": kill["physical_execution_allowed"],
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def next_object_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "highest_upstream_blocker": "global action provenance and differential incidence placement of the recovered 2D attachment response",
        "closed_in_v14_67": [
            "recovery of corrected v11.4 action-whitened Gram/Hessian",
            "exact symbolic KKT tangent pencil",
            "canonical kinetic-whitened attachment Wentzell response",
            "retained-mode tensor lift and self-adjoint extension witness",
            "operator response insertion and fail-closed heat/logdet diagnostic",
            "normalization reconciliation against the earlier unwhitened manual packet",
        ],
        "postcomparison_choice_forbidden": True,
    }


def master_payload() -> dict[str, Any]:
    p = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "reconciliation_verdict": RECONCILIATION_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "recovered_gram_hessian": recovered_gram_hessian_payload(),
        "normalization_reconciliation": normalization_reconciliation_payload(),
        "attachment_wentzell": attachment_wentzell_payload(),
        "operator_response_insertion": operator_response_insertion_payload(),
        "provenance_gate": provenance_gate_payload(),
        "neutrino_kill_screen": neutrino_kill_screen_payload(),
    }
    p["sha256_without_self_hash"] = sha256_payload(p)
    return p


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_action_attachment_wentzell_v14_67.json": master_payload(),
        "BHSM_recovered_gram_hessian_gate_v14_67.json": recovered_gram_hessian_payload(),
        "BHSM_normalization_reconciliation_gate_v14_67.json": normalization_reconciliation_payload(),
        "BHSM_attachment_wentzell_lift_gate_v14_67.json": attachment_wentzell_payload(),
        "BHSM_operator_response_insertion_gate_v14_67.json": operator_response_insertion_payload(),
        "BHSM_provenance_gate_v14_67.json": provenance_gate_payload(),
        "BHSM_neutrino_kill_screen_v14_67.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_67.json": status_payload(),
        "BHSM_next_object_gate_v14_67.json": next_object_payload(),
        "BHSM_completion_gate_v14_67.json": completion_gate_payload(),
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
