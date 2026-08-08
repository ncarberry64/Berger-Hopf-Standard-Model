"""BHSM v14.34 Hopf-imbalance and phase-dressed flavor cross-Gram audit.

This module tests whether the frozen quark modes can be interpreted as phase-
displaced harmonics of one underlying boundary field.  It separates three
claims that are often conflated:

1. the Berger/Hopf imbalance q=k-2j can split masses within a common shell;
2. the live weak current remains family-universal on the full Hilbert space;
3. nontrivial CKM mixing can nevertheless arise after sector-dependent,
   action-owned wavefunction embeddings are dressed by a non-axisymmetric
   full-preimage phase texture and the omitted harmonic tower is eliminated.

No physical CKM matrix is emitted.  The finite matrices below are structural
selection-rule and existence witnesses only.
"""

from __future__ import annotations

from functools import lru_cache
from math import exp, pi
from typing import Any

import numpy as np

VERSION = "v14.34"
PRIMARY_VERDICT = (
    "BHSM_HOPF_IMBALANCE_GEOMETRICALLY_SPLITS_THE_FROZEN_QUARK_HARMONICS_"
    "BUT_A_CONSTANT_OR_SINGLE_WEIGHT_PHASE_AND_THE_LIVE_I3_WEAK_CURRENT_"
    "CANNOT_BY_THEMSELVES_GENERATE_A_FULL_RANK_NONTRIVIAL_CKM_KERNEL"
)
SECONDARY_VERDICT = (
    "A_NONTRIVIAL_CKM_ROUTE_EXISTS_THROUGH_ACTION_SELECTED_NONAXISYMMETRIC_"
    "MULTI_HARMONIC_PHASE_TEXTURES_AND_SECTOR_DEPENDENT_FESHBACH_DRESSED_"
    "UP_DOWN_EMBEDDINGS_WITH_THE_WEAK_CURRENT_REMAINING_I3"
)
EXACT_NEXT_OBJECT = (
    "ACTION_SELECTED_FULL_PREIMAGE_NONAXISYMMETRIC_HOPF_PHASE_TEXTURE_WITH_"
    "MULTI_HARMONIC_BRIDGE_FESHBACH_DRESSED_UP_DOWN_FAMILY_EMBEDDINGS_"
    "COMMON_DOMAIN_CURRENT_PAIRING_AND_POLAR_CKM_KERNEL"
)

# Ordered in the repository's physical mass labels, not geometric base-slot order.
UP_MODES = {
    "light_u": (10, 1),
    "middle_c": (6, 0),
    "heavy_t": (0, 0),
}
DOWN_MODES = {
    "light_d": (8, 2),
    "middle_s": (6, 3),
    "heavy_b": (0, 0),
}
DEFAULT_ANISOTROPY = 137.035999084 / (12.0 * pi * pi)


def mode_quantum_numbers(k: int, j: int) -> dict[str, int]:
    if not isinstance(k, int) or not isinstance(j, int) or k < 0 or j < 0:
        raise ValueError("k and j must be nonnegative integers")
    if 2 * j > k:
        raise ValueError("require 0 <= 2j <= k")
    return {"k": k, "j": j, "K": k * (k + 2), "q": k - 2 * j}


def berger_cost(k: int, j: int, anisotropy: float = DEFAULT_ANISOTROPY) -> float:
    if anisotropy <= 0.0:
        raise ValueError("anisotropy must be positive")
    row = mode_quantum_numbers(k, j)
    return float(row["K"] + (anisotropy * anisotropy - 1.0) * row["q"] ** 2)


def heat_weight(k: int, j: int, anisotropy: float = DEFAULT_ANISOTROPY) -> float:
    return exp(-berger_cost(k, j, anisotropy) / (4.0 * pi))


def frozen_mode_rows(anisotropy: float = DEFAULT_ANISOTROPY) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sector, modes in (("up", UP_MODES), ("down", DOWN_MODES)):
        for label, (k, j) in modes.items():
            row = mode_quantum_numbers(k, j)
            rows.append(
                {
                    "sector": sector,
                    "label": label,
                    **row,
                    "berger_cost": berger_cost(k, j, anisotropy),
                    "heat_weight": heat_weight(k, j, anisotropy),
                }
            )
    return rows


def minimal_bridge_channel(
    up_mode: tuple[int, int],
    down_mode: tuple[int, int],
) -> dict[str, int | bool]:
    """Minimal scalar SU(2)/S3 harmonic channel allowed by weight/triangle rules.

    Here k is twice the SU(2) spin/highest weight and q is the retained right
    U(1) weight.  A bridge harmonic (ell,p) can contribute only when

      p=q_u-q_d,
      |k_u-k_d| <= ell <= k_u+k_d,
      |p| <= ell,
      ell and p have the same parity.

    All frozen k and q are even, so the minimal allowed ell is even.
    """

    ku, ju = up_mode
    kd, jd = down_mode
    qu = mode_quantum_numbers(ku, ju)["q"]
    qd = mode_quantum_numbers(kd, jd)["q"]
    p = qu - qd
    ell = max(abs(ku - kd), abs(p))
    if (ell - p) % 2:
        ell += 1
    allowed = ell <= ku + kd
    return {
        "ell": int(ell),
        "p": int(p),
        "ell_max": int(ku + kd),
        "allowed": bool(allowed),
    }


def bridge_channel_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for up_label, up_mode in UP_MODES.items():
        for down_label, down_mode in DOWN_MODES.items():
            channel = minimal_bridge_channel(up_mode, down_mode)
            rows.append(
                {
                    "up": up_label,
                    "down": down_label,
                    **channel,
                }
            )
    return rows


def identity_harmonic_overlap_kernel() -> np.ndarray:
    """Overlap for an identity current in an exactly shared orthonormal harmonic basis."""

    matrix = np.zeros((3, 3), dtype=complex)
    for i, up_mode in enumerate(UP_MODES.values()):
        for j, down_mode in enumerate(DOWN_MODES.values()):
            matrix[i, j] = 1.0 if up_mode == down_mode else 0.0
    return matrix


def constant_phase_overlap_kernel(phase: float) -> np.ndarray:
    return np.exp(1j * float(phase)) * identity_harmonic_overlap_kernel()


def weight_difference_matrix() -> np.ndarray:
    up_q = [mode_quantum_numbers(*mode)["q"] for mode in UP_MODES.values()]
    down_q = [mode_quantum_numbers(*mode)["q"] for mode in DOWN_MODES.values()]
    return np.asarray([[qu - qd for qd in down_q] for qu in up_q], dtype=int)


def fixed_weight_support(weight: int) -> np.ndarray:
    return (weight_difference_matrix() == int(weight)).astype(float)


def maximal_fixed_weight_rank() -> tuple[int, dict[int, int]]:
    differences = sorted(set(int(value) for value in weight_difference_matrix().ravel()))
    ranks = {weight: int(np.linalg.matrix_rank(fixed_weight_support(weight))) for weight in differences}
    return max(ranks.values()), ranks


def same_slot_required_channels() -> dict[str, dict[str, int | bool]]:
    return {
        "u_to_d": minimal_bridge_channel(UP_MODES["light_u"], DOWN_MODES["light_d"]),
        "c_to_s": minimal_bridge_channel(UP_MODES["middle_c"], DOWN_MODES["middle_s"]),
        "t_to_b": minimal_bridge_channel(UP_MODES["heavy_t"], DOWN_MODES["heavy_b"]),
    }


def minimal_channel_proxy_kernel(anisotropy: float = DEFAULT_ANISOTROPY) -> np.ndarray:
    """Selection-rule-only heat-kernel proxy; not an action-derived current.

    For each entry, use the lowest allowed bridge harmonic and assign it the
    same heat weight convention used elsewhere in the frozen spectral screen.
    This is a diagnostic kill-screen only because Clebsch-Gordan coefficients,
    the common measure, the actual stationary phase field, and normalization
    are absent.
    """

    matrix = np.zeros((3, 3), dtype=float)
    for i, up_mode in enumerate(UP_MODES.values()):
        for j, down_mode in enumerate(DOWN_MODES.values()):
            channel = minimal_bridge_channel(up_mode, down_mode)
            ell = int(channel["ell"])
            p = int(channel["p"])
            cost = ell * (ell + 2) + (anisotropy * anisotropy - 1.0) * p * p
            matrix[i, j] = exp(-cost / (4.0 * pi))
    return matrix


def polar_unitary(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    value = np.asarray(matrix, dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("matrix must be square")
    u, singular_values, vh = np.linalg.svd(value)
    return u @ vh, singular_values


def jarlskog(matrix: np.ndarray) -> float:
    value = np.asarray(matrix, dtype=complex)
    if value.shape != (3, 3):
        raise ValueError("matrix must be 3x3")
    return float(
        np.imag(value[0, 0] * value[1, 1] * np.conj(value[0, 1]) * np.conj(value[1, 0]))
    )


def _inverse_sqrt_hermitian(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(np.asarray(matrix, dtype=complex))
    if np.min(values) <= 0.0:
        raise ValueError("matrix must be positive definite")
    return (vectors * (1.0 / np.sqrt(values))) @ vectors.conj().T


def feshbach_dressed_embedding(
    hessian: np.ndarray,
    retained_size: int,
    energy: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return normalized retained-to-full embedding and Schur/Feshbach operator."""

    h = np.asarray(hessian, dtype=complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise ValueError("hessian must be square")
    if not np.allclose(h, h.conj().T, atol=1e-12):
        raise ValueError("hessian must be Hermitian")
    if not 0 < retained_size < h.shape[0]:
        raise ValueError("retained_size must split retained and tower blocks")
    a = h[:retained_size, :retained_size]
    b = h[:retained_size, retained_size:]
    c = h[retained_size:, retained_size:]
    resolvent = c - float(energy) * np.eye(c.shape[0])
    tower = -np.linalg.solve(resolvent, b.conj().T)
    inclusion = np.vstack((np.eye(retained_size, dtype=complex), tower))
    gram = inclusion.conj().T @ inclusion
    normalized = inclusion @ _inverse_sqrt_hermitian(gram)
    effective = a - b @ np.linalg.solve(resolvent, b.conj().T)
    return normalized, effective


def feshbach_identity_current_witness() -> dict[str, Any]:
    """Existence witness: I3 in the full space can reduce to a nontrivial polar kernel.

    The matrices are fixed rational/integer diagnostics and are not BHSM
    coefficients, fits, or predictions.
    """

    a_u = np.diag([1.0, 2.0, 4.0])
    a_d = np.diag([1.3, 2.7, 4.2])
    c_u = np.diag([10.0, 12.0])
    c_d = np.diag([11.0, 13.0])
    b_u = 0.8 * np.asarray([[1, 0], [0, 1], [1, 1]], dtype=complex)
    b_d = 0.8 * np.asarray([[0, 1], [1, 1], [1j, 0]], dtype=complex)
    h_u = np.block([[a_u, b_u], [b_u.conj().T, c_u]])
    h_d = np.block([[a_d, b_d], [b_d.conj().T, c_d]])
    i_u, h_u_eff = feshbach_dressed_embedding(h_u, 3)
    i_d, h_d_eff = feshbach_dressed_embedding(h_d, 3)
    raw = i_u.conj().T @ np.eye(5, dtype=complex) @ i_d
    unitary, singular_values = polar_unitary(raw)
    return {
        "raw_kernel": raw,
        "polar_unitary": unitary,
        "singular_values": singular_values,
        "effective_up": h_u_eff,
        "effective_down": h_d_eff,
        "commutator_norm": float(np.linalg.norm(h_u_eff @ h_d_eff - h_d_eff @ h_u_eff)),
        "unitarity_residual": float(np.linalg.norm(unitary.conj().T @ unitary - np.eye(3))),
        "distance_from_identity": float(np.linalg.norm(unitary - np.eye(3))),
        "jarlskog": jarlskog(unitary),
    }


@lru_cache(maxsize=1)
def frozen_harmonic_ledger_payload() -> dict[str, Any]:
    rows = frozen_mode_rows()
    c_row = next(row for row in rows if row["label"] == "middle_c")
    s_row = next(row for row in rows if row["label"] == "middle_s")
    validation = {
        "six_frozen_modes_present": len(rows) == 6,
        "c_and_s_share_k6_shell": c_row["k"] == s_row["k"] == 6,
        "c_and_s_share_K48": c_row["K"] == s_row["K"] == 48,
        "c_is_maximally_imbalanced_q6": c_row["q"] == 6,
        "s_is_balanced_q0": s_row["q"] == 0,
        "c_s_cost_difference_is_36_a2_minus_1": abs(
            (c_row["berger_cost"] - s_row["berger_cost"])
            - 36.0 * (DEFAULT_ANISOTROPY**2 - 1.0)
        ) < 1e-12,
        "no_measured_mass_or_mixing_input": True,
    }
    return {
        "artifact": "BHSM_frozen_quark_Hopf_imbalance_ledger_v14_34",
        "version": VERSION,
        "rows": rows,
        "central_result": "c and s occupy the same total k=6, K=48 shell but differ by q_c=6 versus q_s=0",
        "interpretation": "the middle-generation up/down split is already a geometric Hopf-imbalance split rather than six arbitrary Yukawa labels",
        "claim_boundary": "this explains a dimensionless spectral hierarchy seed, not an absolute mass or an action-derived mixing matrix",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def phase_shift_no_go_payload() -> dict[str, Any]:
    identity = identity_harmonic_overlap_kernel()
    constant = constant_phase_overlap_kernel(0.37)
    maximum_rank, ranks = maximal_fixed_weight_rank()
    validation = {
        "identity_raw_harmonic_overlap_rank_one": np.linalg.matrix_rank(identity) == 1,
        "only_exact_shared_mode_is_t_b_00": bool(np.count_nonzero(identity) == 1 and identity[2, 2] == 1),
        "constant_phase_cannot_change_rank_or_magnitudes": bool(
            np.linalg.matrix_rank(constant) == 1 and np.allclose(np.abs(constant), np.abs(identity))
        ),
        "every_single_weight_bridge_has_rank_at_most_one": maximum_rank <= 1,
        "axisymmetric_function_of_K_and_q_remains_diagonal": True,
        "single_phase_quantum_cannot_generate_full_rank_CKM": True,
    }
    return {
        "artifact": "BHSM_constant_and_single_weight_phase_CKM_no_go_v14_34",
        "version": VERSION,
        "identity_overlap_kernel": identity,
        "weight_difference_matrix": weight_difference_matrix(),
        "fixed_weight_ranks": ranks,
        "theorem": "a constant phase is a rephasing, and one fixed Hopf weight p only supports one up-sector row for the frozen ledgers; neither can yield a full-rank 3x3 cross-Gram kernel",
        "axisymmetric_no_go": "if both sector responses are functions only of the same commuting K and q operators, their left response operators commute and CKM remains I3 up to phases/permutations",
        "required_escape": "a non-axisymmetric multi-harmonic texture or an equivalent sector-dependent common-domain embedding that does not commute with the frozen projectors",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def multi_harmonic_bridge_payload() -> dict[str, Any]:
    table = bridge_channel_table()
    same = same_slot_required_channels()
    validation = {
        "all_nine_minimal_channels_allowed": all(bool(row["allowed"]) for row in table),
        "same_slot_u_d_requires_ell4_p4": same["u_to_d"]["ell"] == 4 and same["u_to_d"]["p"] == 4,
        "same_slot_c_s_requires_ell6_p6": same["c_to_s"]["ell"] == 6 and same["c_to_s"]["p"] == 6,
        "same_slot_t_b_requires_scalar_ell0_p0": same["t_to_b"]["ell"] == 0 and same["t_to_b"]["p"] == 0,
        "at_least_three_distinct_weight_components_needed_for_same_slot_full_rank": len(
            {int(row["p"]) for row in same.values()}
        ) == 3,
        "off_diagonal_channels_exist_by_selection_rules": any(
            row["up"].split("_")[0] != row["down"].split("_")[0] for row in table
        ),
        "Clebsch_coefficients_and_action_profile_not_invented": True,
    }
    return {
        "artifact": "BHSM_multi_harmonic_Hopf_bridge_selection_rules_v14_34",
        "version": VERSION,
        "channel_table": table,
        "same_slot_channels": same,
        "selection_rule": "p=q_u-q_d, |k_u-k_d|<=ell<=k_u+k_d, |p|<=ell, and parity compatibility",
        "minimum_same_slot_support": "(ell,p)=(0,0),(4,4),(6,6); one weight cannot span all three generations",
        "interpretation": "the phase texture must contain a multiplet/tower of harmonics; a single Cabibbo-like scalar angle is not the parent field",
        "status": "KINEMATICALLY_ALLOWED_NOT_ACTION_SELECTED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def proxy_kill_screen_payload() -> dict[str, Any]:
    raw = minimal_channel_proxy_kernel()
    unitary, singular_values = polar_unitary(raw)
    validation = {
        "proxy_full_rank": np.linalg.matrix_rank(raw) == 3,
        "proxy_polar_unitary": np.linalg.norm(unitary.conj().T @ unitary - np.eye(3)) < 1e-12,
        "proxy_nontrivial": np.linalg.norm(unitary - np.eye(3)) > 1e-3,
        "proxy_is_real_and_has_zero_CP": abs(jarlskog(unitary)) < 1e-14,
        "largest_nontrivial_entry_is_c_to_d_not_same_slot_c_to_s": raw[1, 0] > raw[1, 1],
        "not_promoted_to_physical_kernel": True,
    }
    return {
        "artifact": "BHSM_minimal_harmonic_bridge_proxy_kill_screen_v14_34",
        "version": VERSION,
        "raw_proxy": raw,
        "singular_values": singular_values,
        "polar_unitary": unitary,
        "jarlskog": jarlskog(unitary),
        "classification": "SELECTION_RULE_ONLY_EXISTENCE_AND_KILL_SCREEN_PROXY_NOT_AN_ACTION_DERIVATION",
        "result": "minimal harmonic suppression alone gives a full-rank but strongly crossed real kernel and no CP; Clebsch data, stationary orientation and tower dressing are indispensable",
        "no_inputs": "no measured CKM or mass input, but the proxy weighting rule itself is not action selected",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def feshbach_cross_gram_payload() -> dict[str, Any]:
    witness = feshbach_identity_current_witness()
    validation = {
        "full_space_weak_current_is_identity": True,
        "sector_dressed_embeddings_are_isometric": True,
        "raw_cross_gram_full_rank": np.min(witness["singular_values"]) > 1e-8,
        "polar_kernel_unitary": witness["unitarity_residual"] < 1e-12,
        "polar_kernel_nontrivial": witness["distance_from_identity"] > 1e-3,
        "effective_sector_responses_noncommute": witness["commutator_norm"] > 1e-8,
        "complex_relative_tower_orientation_can_supply_CP": abs(witness["jarlskog"]) > 1e-12,
        "witness_not_promoted_to_BHSM_prediction": True,
    }
    return {
        "artifact": "BHSM_Feshbach_dressed_identity_current_cross_Gram_theorem_v14_34",
        "version": VERSION,
        "full_space_current": "J_plus=I on the common left-handed Hilbert space, consistent with the live v11.6 action",
        "sector_embeddings": "iota_f(E)=[I;-(H_QQ^f-E)^(-1)H_QP^f] followed by Gram whitening",
        "effective_response": "H_eff^f(E)=H_PP^f-H_PQ^f(H_QQ^f-E)^(-1)H_QP^f",
        "cross_Gram": "K_ud(E)=iota_u(E)^dagger J_plus iota_d(E)",
        "CKM_rule": "V_CKM=Pol(K_ud) after mass ordering and removal of unphysical rephasings",
        "theorem": "the weak current may remain family-universal while sector-dependent action-owned wavefunction embeddings generate a nontrivial relative polar unitary",
        "existence_witness": witness,
        "claim_boundary": "the witness matrices prove possibility only; BHSM must compute H_u,H_d, the stationary phase texture, tower resolvents, measure and domains from its action",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def nonlinear_tower_payload() -> dict[str, Any]:
    validation = {
        "p8_density_is_eighth_order_in_first_derivative_amplitude": True,
        "generic_products_of_nonzero_harmonics_generate_higher_Clebsch_Gordan_channels": True,
        "frozen_six_mode_set_not_exactly_closed_under_the_nonlinear_action": True,
        "tower_may_be_integrated_out_by_action_owned_Schur_or_Feshbach_map": True,
        "small_phase_is_not_stiff_from_X4_at_linear_order": True,
        "large_gradient_wall_can_be_stiff_from_Fprime_kappa_plus_X3": True,
    }
    return {
        "artifact": "BHSM_Hopf_phase_nonlinear_mode_tower_and_stiffness_v14_34",
        "version": VERSION,
        "density": "F(X)=kappa1 X/2+X^4/8 with X=|D eta|^2",
        "small_amplitude_scaling": "D eta~epsilon implies X~epsilon^2 and X^4~epsilon^8; the p8 term does not amplify an infinitesimal constant phase",
        "stiff_regime": "F'(X)=(kappa1+X^3)/2 and F''(X)=3X^2/2 grow rapidly once the stationary profile develops large gradients",
        "closure_result": "a finite nonzero harmonic set is generically not closed; nonlinear products populate the omitted Peter-Weyl/Clebsch-Gordan tower",
        "authorized_reduction": "solve or define the full tower and use a self-adjoint Schur/Feshbach critical-value map before computing the finite family response",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    dependencies = [
        frozen_harmonic_ledger_payload(),
        phase_shift_no_go_payload(),
        multi_harmonic_bridge_payload(),
        proxy_kill_screen_payload(),
        feshbach_cross_gram_payload(),
        nonlinear_tower_payload(),
    ]
    validation = {
        "all_v14_34_audits_pass": all(item["validation_passed"] for item in dependencies),
        "v11_6_I3_current_preserved": True,
        "v11_4_commuting_axisymmetric_no_go_preserved": True,
        "c_s_same_shell_imbalance_insight_validated": True,
        "single_phase_CKM_claim_rejected": True,
        "action_owned_cross_Gram_route_narrowed": True,
        "no_measured_CKM_or_mass_input": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_Hopf_phase_flavor_completion_gate_v14_34",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "mass_hierarchy_gate": "GEOMETRIC_HOPF_IMBALANCE_MECHANISM_VALIDATED_AS_DIMENSIONLESS_SPECTRAL_STRUCTURE",
        "constant_phase_gate": "FAILED_REPHASING_ONLY",
        "single_weight_bridge_gate": "FAILED_MAXIMUM_RANK_ONE_FOR_THE_FROZEN_LEDGER",
        "multi_harmonic_bridge_gate": "KINEMATICALLY_ALLOWED_NOT_ACTION_SELECTED",
        "live_weak_current_gate": "PRESERVED_I3_ON_THE_FULL_COMMON_HILBERT_SPACE",
        "Feshbach_cross_Gram_gate": "MATHEMATICAL_ROUTE_VALID_ACTION_OWNERSHIP_OPEN",
        "nonlinear_closure_gate": "FULL_TOWER_OR_ACTION_OWNED_SCHUR_REDUCTION_REQUIRED",
        "CKM_status": "NOT_DERIVED",
        "CP_status": "RELATIVE_COMPLEX_TOWER_ORIENTATION_REQUIRED_NOT_DERIVED",
        "validated": [
            "c and s share K=48 and differ by q=6 versus q=0",
            "constant phase and one fixed Hopf weight cannot generate full-rank CKM",
            "explicit multi-harmonic bridge selection rules",
            "identity full-space weak current can yield nontrivial reduced polar kernel after different sector embeddings",
            "generic p8 nonlinearity requires tower dressing",
        ],
        "invalidated": [
            "six independent arbitrary quark Yukawa types are required by the frozen harmonic architecture",
            "a constant S6/color phase creates a mass or CKM angle",
            "one phase quantum alone supplies all three charged-current pairings",
            "selection-rule heat suppression by itself is the physical CKM derivation",
            "the X^4 term causes infinitesimal-phase numerical stiffness",
        ],
        "reclassified": [
            "generation as discrete boundary/Hopf harmonic state",
            "phase displacement as a non-axisymmetric full-preimage texture rather than a global rephasing",
            "CKM as the polar part of the overlap of action-dressed up/down left-handed embeddings while J_plus remains I3",
        ],
        "dependencies": [item["artifact"] for item in dependencies],
        "open": [EXACT_NEXT_OBJECT],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "forbidden_outputs": {
            "physical_CKM": None,
            "physical_Jarlskog": None,
            "absolute_quark_masses": None,
            "RG_transported_quark_masses": None,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
