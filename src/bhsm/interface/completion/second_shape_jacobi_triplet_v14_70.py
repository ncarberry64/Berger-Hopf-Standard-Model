"""BHSM v14.70 round second-shape Jacobi spectrum and triplet-selection gate.

The v14.69 first moving-seam metric variation vanishes on the retained
reflection-symmetric round equator because K_ab=0.  This sprint therefore
executes the required fallback: derive the exact *second* normal-shape
variation on a spatial S3 seam in the round S4 cap and audit whether it can
supply exactly three nonuniform moving-seam channels without adding a new
selection rule.

For a time-independent physical normal displacement xi on S3_a, the graph
chi=pi/2+epsilon*xi/a has induced metric

    h_ij(epsilon)
      = a^2 cos^2(epsilon xi/a) gamma_ij
        + epsilon^2 (d_i xi)(d_j xi),

hence

    d h/d epsilon|0 = 0,
    d^2 h/d epsilon^2|0
      = 2[d xi tensor d xi - (xi^2/a^2) h].

The bilinear polarization is

    D2h[xi,eta]
      = d xi tensor d eta + d eta tensor d xi
        - 2 xi eta h/a^2.

Its trace gives the universal minimal-equator Jacobi form

    Q[xi,eta] = int(<grad xi,grad eta>-3 xi eta/a^2)dmu.

On scalar S3 harmonics,

    -Delta Y_l = l(l+2)Y_l/a^2,
    J_l = (l(l+2)-3)/a^2 = (l-1)(l+3)/a^2,
    multiplicity = (l+1)^2.

Therefore the scalar round Jacobi operator has multiplicities 1,4,9,16,...
and contains no exactly three-dimensional eigenspace.  The first positive
space is l=2 with dimension 9.  Representation-theoretically it is the
(j_L,j_R)=(1,1) irrep of SU(2)_L x SU(2)_R.  After choosing a diagonal SU(2),
it decomposes as 1 + 3 + 5.  The rank-three antisymmetric projector is exact,
but choosing that diagonal subgroup and selecting only its triplet is *not*
currently action-owned.  Thus a mathematical three-channel subspace exists,
while physical BHSM three-channel selection remains fail closed.

This module does not claim the area Jacobi operator is the complete BHSM
second shape Hessian.  The full Hessian must also include the M8/M5 bulk
second variation, GHY, compatibility multipliers/KKT reaction, matter and
nonlocal spectral terms on the globally stationary background.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any, Sequence

import numpy as np

from bhsm.interface.completion.tensor_differential_incidence_v14_69 import (
    VERSION as V1469_VERSION,
    round_shape_kernel_payload,
)

VERSION = "v14.70"
PRIMARY_VERDICT = (
    "BHSM_V14_70_THE_RETAINED_TWO_CAP_REFLECTION_SYMMETRY_KEEPS_THE_ROUND_"
    "EQUATOR_FIRST_SHAPE_STATIONARY_AND_THE_EXACT_SECOND_NORMAL_SHAPE_"
    "VARIATION_YIELDS_THE_S3_JACOBI_SPECTRUM_J_L_EQUALS_L_MINUS_1_TIMES_"
    "L_PLUS_3_OVER_A_SQUARED_WITH_MULTIPLICITIES_L_PLUS_1_SQUARED_SO_ROUND_"
    "SCALAR_GEOMETRY_DOES_NOT_SELECT_EXACTLY_THREE_CHANNELS;_THE_FIRST_"
    "POSITIVE_L2_SPACE_IS_NINE_DIMENSIONAL_AND_CONTAINS_A_1_PLUS_3_PLUS_5_"
    "DIAGONAL_SU2_DECOMPOSITION_BUT_THE_TRIPLET_SELECTION_REQUIRES_AN_ACTION_"
    "OWNED_HOPF_OR_POLARIZATION_INTERTWINER_AND_THE_COMPLETE_GLOBAL_SECOND_"
    "SHAPE_HESSIAN_REMAINS_OPEN"
)
EXACT_NEXT_OBJECT = (
    "FULL_GLOBAL_SECOND_SHAPE_HESSIAN_ON_THE_ACTION_STATIONARY_PARENT_CHILD_"
    "BACKGROUND_INCLUDING_BULK_GHY_COMPATIBILITY_KKT_AND_NONLOCAL_SPECTRAL_"
    "TERMS_WITH_AN_ACTION_OWNED_HOPF_POLARIZATION_OR_DIAGONAL_SU2_"
    "INTERTWINER_THAT_SELECTS_OR_REJECTS_THE_L2_TRIPLET_THEN_THREE_"
    "NONUNIFORM_SHAPE_DERIVATIVES_COMPLETE_CALDERON_PROJECTORS_RELATIVE_HEAT_"
    "SUPERTRACE_AND_FROZEN_NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def round_graph_metric_second_variation(
    xi: float,
    grad_xi: Sequence[float],
    radius: float = 1.0,
) -> np.ndarray:
    """Return h''(0) in an orthonormal tangent frame on S3_a.

    xi is a physical normal displacement and grad_xi are physical orthonormal
    gradient components.  The background tangent metric in this frame is I3.
    """
    a = float(radius)
    if a <= 0.0:
        raise ValueError("radius must be positive")
    g = np.asarray(grad_xi, dtype=float).reshape(-1)
    if g.shape != (3,):
        raise ValueError("grad_xi must contain three tangent components")
    return 2.0 * (np.outer(g, g) - (float(xi) ** 2 / a**2) * np.eye(3))


def round_graph_metric_second_bilinear(
    xi: float,
    grad_xi: Sequence[float],
    eta: float,
    grad_eta: Sequence[float],
    radius: float = 1.0,
) -> np.ndarray:
    """Polarized second shape differential D^2 h[xi,eta]."""
    a = float(radius)
    if a <= 0.0:
        raise ValueError("radius must be positive")
    gx = np.asarray(grad_xi, dtype=float).reshape(-1)
    ge = np.asarray(grad_eta, dtype=float).reshape(-1)
    if gx.shape != (3,) or ge.shape != (3,):
        raise ValueError("gradients must contain three tangent components")
    return np.outer(gx, ge) + np.outer(ge, gx) - 2.0 * float(xi) * float(eta) / a**2 * np.eye(3)


def constant_displacement_exact_metric(epsilon: float, xi: float, radius: float = 1.0) -> np.ndarray:
    """Exact round-equator graph metric for spatially constant xi."""
    a = float(radius)
    if a <= 0.0:
        raise ValueError("radius must be positive")
    factor = math.cos(float(epsilon) * float(xi) / a) ** 2
    return factor * np.eye(3)


def constant_displacement_second_fd_residual(radius: float = 1.7, xi: float = 0.43, eps: float = 1e-4) -> float:
    exact = round_graph_metric_second_variation(xi, [0.0, 0.0, 0.0], radius)
    h0 = constant_displacement_exact_metric(0.0, xi, radius)
    hp = constant_displacement_exact_metric(eps, xi, radius)
    hm = constant_displacement_exact_metric(-eps, xi, radius)
    fd = (hp - 2.0 * h0 + hm) / eps**2
    return float(np.linalg.norm(fd - exact))


def jacobi_eigenvalue(ell: int, radius: float = 1.0) -> float:
    if not isinstance(ell, int) or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    a = float(radius)
    if a <= 0.0:
        raise ValueError("radius must be positive")
    return ((ell - 1) * (ell + 3)) / a**2


def scalar_harmonic_multiplicity(ell: int) -> int:
    if not isinstance(ell, int) or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    return (ell + 1) ** 2


def scalar_laplacian_eigenvalue(ell: int, radius: float = 1.0) -> float:
    if not isinstance(ell, int) or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    a = float(radius)
    if a <= 0.0:
        raise ValueError("radius must be positive")
    return ell * (ell + 2) / a**2


def jacobi_spectrum(max_ell: int = 6, radius: float = 1.0) -> list[dict[str, Any]]:
    if not isinstance(max_ell, int) or max_ell < 0:
        raise ValueError("max_ell must be a nonnegative integer")
    return [
        {
            "ell": ell,
            "laplacian_eigenvalue": scalar_laplacian_eigenvalue(ell, radius),
            "jacobi_eigenvalue": jacobi_eigenvalue(ell, radius),
            "multiplicity": scalar_harmonic_multiplicity(ell),
            "classification": (
                "HOMOGENEOUS_NEGATIVE_GEOMETRIC_AREA_MODE" if ell == 0 else
                "AMBIENT_ISOMETRY_ZERO_MODE" if ell == 1 else
                "POSITIVE_ROUND_AREA_JACOBI_MODE"
            ),
        }
        for ell in range(max_ell + 1)
    ]


def no_exact_threefold_scalar_eigenspace(max_ell: int = 64) -> bool:
    return all(scalar_harmonic_multiplicity(ell) != 3 for ell in range(max_ell + 1))


def _matrix_space_projector(fn) -> np.ndarray:
    cols: list[np.ndarray] = []
    for i in range(3):
        for j in range(3):
            e = np.zeros((3, 3), dtype=float)
            e[i, j] = 1.0
            cols.append(np.asarray(fn(e), dtype=float).reshape(-1))
    return np.column_stack(cols)


def l2_diagonal_su2_projectors() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project 3 tensor 3 = 1 + 3 + 5 under a chosen diagonal SU(2).

    In the matrix model of spin-1 tensor spin-1, scalar=trace,
    triplet=antisymmetric, quintet=symmetric traceless.
    """
    p1 = _matrix_space_projector(lambda a: np.trace(a) / 3.0 * np.eye(3))
    p3 = _matrix_space_projector(lambda a: 0.5 * (a - a.T))
    p5 = _matrix_space_projector(lambda a: 0.5 * (a + a.T) - np.trace(a) / 3.0 * np.eye(3))
    return p1, p3, p5


def projector_quality(p: np.ndarray) -> dict[str, float | int]:
    x = np.asarray(p, dtype=float)
    return {
        "rank": int(np.linalg.matrix_rank(x, tol=1e-11)),
        "idempotence_residual": float(np.linalg.norm(x @ x - x)),
        "self_adjoint_residual": float(np.linalg.norm(x - x.T)),
    }


def reflection_stationarity_payload() -> dict[str, Any]:
    prior = round_shape_kernel_payload()
    return {
        "version": VERSION,
        "source_round_cap": "v7.1 g5=-dt^2+a(t)^2[dchi^2+sin^2(chi)ds_S3^2] with seam chi=pi/2",
        "cap_reflection": "chi -> pi-chi exchanges the two identical caps and sends normal displacement xi -> -xi",
        "shape_stationarity_theorem": "for a cap-exchange/reflection-even global functional Gamma[xi]=Gamma[-xi], D_Gamma[0]=0",
        "round_extrinsic_curvature": "K_ab=0",
        "v14_69_first_shape_response_norm": prior["pure_normal_round_response_norm"],
        "nonround_action_stationary_branch_constructed": False,
        "reason_nonround_not_promoted": "no action-selected reflection-breaking parent/child stationary solution is present in the retained archive",
        "fallback_to_second_shape_required": True,
        "full_global_background_stationarity_under_all_bulk_variations_proved_here": False,
        "physical_BHSM_prediction": False,
    }


def second_shape_metric_payload() -> dict[str, Any]:
    xi = 0.37
    gx = np.asarray([0.21, -0.08, 0.13])
    eta = -0.19
    ge = np.asarray([0.04, 0.17, -0.11])
    a = 1.6
    q = round_graph_metric_second_bilinear(xi, gx, eta, ge, a)
    qx = round_graph_metric_second_variation(xi, gx, a)
    polar = 0.5 * (
        round_graph_metric_second_variation(xi + eta, gx + ge, a)
        - round_graph_metric_second_variation(xi, gx, a)
        - round_graph_metric_second_variation(eta, ge, a)
    )
    trace_half = 0.5 * float(np.trace(q))
    expected_trace_half = float(gx @ ge - 3.0 * xi * eta / a**2)
    return {
        "version": VERSION,
        "exact_graph_formula": "h_ij(eps)=a^2 cos^2(eps xi/a) gamma_ij+eps^2 d_i xi d_j xi for a static normal graph",
        "first_variation": "0 at the round equator",
        "second_variation": "D2h[xi,eta]=d xi tensor d eta+d eta tensor d xi-2 xi eta h/a^2",
        "quadratic_second_variation_matrix": qx.tolist(),
        "bilinear_second_variation_matrix": q.tolist(),
        "polarization_identity_residual": float(np.linalg.norm(polar - q)),
        "half_trace": trace_half,
        "expected_half_trace": expected_trace_half,
        "trace_jacobi_identity_residual": abs(trace_half - expected_trace_half),
        "constant_displacement_finite_difference_residual": constant_displacement_second_fd_residual(),
        "second_shape_is_bilinear_not_a_first_order_linear_incidence_map": True,
        "full_BHSM_second_shape_hessian_complete": False,
        "physical_BHSM_prediction": False,
    }


def jacobi_spectrum_payload() -> dict[str, Any]:
    rows = jacobi_spectrum(8, 1.0)
    return {
        "version": VERSION,
        "operator": "J_round=-Delta_S3-3/a^2 in the area/minimal-equator convention",
        "eigenvalue_formula": "J_l=[l(l+2)-3]/a^2=(l-1)(l+3)/a^2",
        "multiplicity_formula": "(l+1)^2",
        "rows_radius_one": rows,
        "homogeneous_l0_eigenvalue": jacobi_eigenvalue(0),
        "l1_zero_mode_multiplicity": scalar_harmonic_multiplicity(1),
        "first_positive_ell": 2,
        "first_positive_eigenvalue": jacobi_eigenvalue(2),
        "first_positive_multiplicity": scalar_harmonic_multiplicity(2),
        "no_exact_threefold_scalar_eigenspace_through_ell64": no_exact_threefold_scalar_eigenspace(),
        "l1_interpretation": "normal components of ambient great-sphere rotation/isometry orbit; symmetry zero modes before physical interpretation",
        "area_jacobi_operator_equals_full_BHSM_shape_hessian": False,
        "physical_BHSM_prediction": False,
    }


def l2_triplet_decomposition_payload() -> dict[str, Any]:
    p1, p3, p5 = l2_diagonal_su2_projectors()
    quality = {"singlet": projector_quality(p1), "triplet": projector_quality(p3), "quintet": projector_quality(p5)}
    return {
        "version": VERSION,
        "l2_round_harmonic_space": "H_l=2 ~= (j_L,j_R)=(1,1) of SU2_L x SU2_R, dimension 9",
        "chosen_subgroup_for_decomposition": "diagonal SU2",
        "branching": "(1,1)|SU2_diag = j=0 + j=1 + j=2, dimensions 1+3+5",
        "matrix_model": "3 tensor 3 = trace + antisymmetric + symmetric_traceless",
        "projector_quality": quality,
        "projector_sum_identity_residual": float(np.linalg.norm(p1 + p3 + p5 - np.eye(9))),
        "pairwise_orthogonality_residual": float(max(np.linalg.norm(p1 @ p3), np.linalg.norm(p1 @ p5), np.linalg.norm(p3 @ p5))),
        "triplet_rank": int(np.linalg.matrix_rank(p3, tol=1e-11)),
        "triplet_mathematically_available": True,
        "diagonal_SU2_selected_by_current_global_BHSM_action": False,
        "triplet_selected_over_singlet_and_quintet_by_current_global_BHSM_action": False,
        "predeclared_three_shape_channels_identified_with_this_triplet": False,
        "physical_BHSM_prediction": False,
    }


def three_shape_channel_gate_payload() -> dict[str, Any]:
    spec = jacobi_spectrum_payload()
    decomp = l2_triplet_decomposition_payload()
    return {
        "version": VERSION,
        "round_scalar_second_shape_spectrum_supplies_exact_threefold_eigenspace": False,
        "reason": "scalar S3 harmonic multiplicities are (l+1)^2; first positive l=2 multiplicity is 9",
        "l2_contains_rank_three_subrepresentation_after_diagonal_SU2_choice": decomp["triplet_mathematically_available"],
        "action_owned_selection_of_diagonal_SU2_or_Hopf_polarization": False,
        "action_owned_intertwiner_to_v14_55_three_predeclared_shape_channels": False,
        "physical_three_nonuniform_shape_derivatives_available": False,
        "classification": "THREE_CHANNEL_KINEMATIC_SUBSPACE_EXISTS_BUT_ACTION_SELECTION_BLOCKED",
        "full_second_shape_action_needed": True,
        "physical_BHSM_prediction": False,
    }


def provenance_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "v7_1_round_cap_geometry_owned": True,
        "v7_1_cap_reflection_owned": True,
        "v14_69_first_shape_kernel_owned": True,
        "universal_round_graph_second_metric_variation_derived": True,
        "universal_round_area_jacobi_spectrum_derived": True,
        "l2_1_plus_3_plus_5_representation_decomposition_derived": True,
        "action_selected_nonround_stationary_cap": False,
        "complete_BHSM_second_shape_Hessian_bulk_GHY_KKT_nonlocal": False,
        "action_selected_diagonal_SU2_or_Hopf_polarization": False,
        "physical_h_C_and_k_D_from_same_global_solution": False,
        "complete_gauge_metric_spinor_ghost_projector": False,
        "all_physical_provenance_inputs_present": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "physical_execution_allowed": False,
        "reason": "three physical nonuniform shape derivatives and complete action-derived global operator/projector data are not yet frozen",
        "round_second_shape_theorem_may_be_used_as_physical_neutrino_prediction": False,
        "physical_mass_PMNS_splitting_or_probability_emitted": False,
        "no_retuning_preserved": True,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "reflection symmetry makes the round seam shape coordinate first-stationary within the retained symmetric two-cap branch",
            "K_ab=0 remains exact at the round equator",
            "exact static-normal-graph second induced-metric variation",
            "polarized second shape differential",
            "trace of the second metric variation gives the round minimal-equator Jacobi bilinear form",
            "S3 scalar Laplacian eigenvalues l(l+2)/a^2",
            "round area Jacobi eigenvalues (l-1)(l+3)/a^2",
            "scalar harmonic multiplicities (l+1)^2",
            "l=1 has four symmetry zero modes",
            "first positive scalar round area mode is l=2 with multiplicity nine",
            "l=2 representation is (1,1) under SU2_L x SU2_R",
            "chosen diagonal SU2 decomposes l=2 as 1+3+5",
            "rank-three antisymmetric projector is exact, orthogonal, and idempotent",
        ],
        "invalidated": [
            "round first-order normal trace can generate the three shape channels",
            "round scalar second-shape spectrum contains an exactly threefold eigenvalue",
            "the l=2 triplet is automatically selected by round geometry",
            "the universal area Jacobi operator is already the complete BHSM second shape Hessian",
        ],
        "reclassified": [
            "three-channel possibility is a subrepresentation-selection problem rather than a round scalar eigenvalue-count problem",
            "the l=1 normal modes are symmetry zero modes rather than three flavor channels",
            "the first positive round scalar shape space is nine-dimensional and requires additional polarization to isolate a triplet",
            "nonround-cap search remains open, while the round fallback is now explicitly exhausted through second order kinematically",
        ],
        "open": [
            "globally stationary nonround parent/child cap or proof it is excluded",
            "complete second variation of M8 and M5 bulk actions",
            "GHY second shape contribution",
            "compatibility/KKT multiplier second variation and Schur reduction",
            "nonlocal determinant/relative heat contribution to shape Hessian",
            "action-owned Hopf polarization or diagonal SU2 selection",
            "intertwiner from selected triplet to the predeclared three moving-seam channels",
            "physical h_C and k_D on the same stationary solution",
            "complete gauge-fixed metric/gauge/spinor/ghost Calderon blocks",
            "continuum relative heat supertrace",
            "frozen no-retuning neutrino execution",
            "all downstream particle/force/flavor completion",
        ],
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    p = provenance_gate_payload()
    s = second_shape_metric_payload()
    j = jacobi_spectrum_payload()
    t = l2_triplet_decomposition_payload()
    validation = {
        "v14_69_dependency_present": V1469_VERSION == "v14.69",
        "second_metric_polarization_exact": s["polarization_identity_residual"] < 1e-12,
        "second_metric_trace_jacobi_exact": s["trace_jacobi_identity_residual"] < 1e-12,
        "constant_displacement_finite_difference_agrees": s["constant_displacement_finite_difference_residual"] < 1e-7,
        "jacobi_l1_zero": abs(jacobi_eigenvalue(1)) < 1e-15,
        "jacobi_l2_positive": jacobi_eigenvalue(2) > 0.0,
        "l2_multiplicity_nine": scalar_harmonic_multiplicity(2) == 9,
        "no_threefold_scalar_eigenspace": j["no_exact_threefold_scalar_eigenspace_through_ell64"],
        "triplet_projector_rank_three": t["triplet_rank"] == 3,
        "triplet_projectors_complete": t["projector_sum_identity_residual"] < 1e-12,
        "triplet_projectors_orthogonal": t["pairwise_orthogonality_residual"] < 1e-12,
        "physical_gate_fail_closed": not p["all_physical_provenance_inputs_present"],
        "no_physical_prediction_emitted": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "physical_execution_allowed": False,
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def next_object_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "why": [
            "round reflection symmetry keeps the first shape variation zero",
            "the universal second-shape scalar spectrum has no exactly threefold eigenspace",
            "a rank-three l=2 subrepresentation exists only after a diagonal SU2/Hopf polarization choice",
            "the complete BHSM second shape Hessian needs bulk, GHY, compatibility/KKT and nonlocal terms on one stationary background",
            "only an action-owned polarization/intertwiner can turn the mathematical triplet into the three physical moving-seam derivatives",
        ],
        "forbidden_shortcuts": [
            "do not select the l=2 triplet from flavor data",
            "do not identify l=1 symmetry zero modes with neutrino flavors",
            "do not use the area Jacobi coefficient as the complete physical shape Hessian",
            "do not insert a nonround K_ab by hand",
            "do not run the neutrino comparison until all operator/projector inputs are derived and hash-frozen",
        ],
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_round_reflection_stationarity_v14_70.json": reflection_stationarity_payload(),
        "BHSM_second_shape_metric_hessian_v14_70.json": second_shape_metric_payload(),
        "BHSM_round_jacobi_spectrum_v14_70.json": jacobi_spectrum_payload(),
        "BHSM_l2_triplet_decomposition_v14_70.json": l2_triplet_decomposition_payload(),
        "BHSM_three_shape_channel_gate_v14_70.json": three_shape_channel_gate_payload(),
        "BHSM_provenance_gate_v14_70.json": provenance_gate_payload(),
        "BHSM_neutrino_kill_screen_v14_70.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_70.json": status_payload(),
        "BHSM_completion_gate_v14_70.json": completion_gate_payload(),
        "BHSM_next_object_gate_v14_70.json": next_object_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = root / name
        data = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
        path.write_text(data, encoding="utf-8", newline="\n")
        written.append(path)
    return written
