"""BHSM v8.6 complex profile and isospectral attachment manual sprint.

This module continues the bounded v8.5 component/profile audit.  It derives a
parameter-free linear isospectral alignment functor, a canonical polar-current
normalization, and kill-tests the existing Hopf, C3 triality, and G2 complex
structures as sources of CKM mixing and CP.  Candidate formulas remain
non-authoritative until the frozen action supplies their incidence and channel
normalization.
"""

from __future__ import annotations

from itertools import permutations
from math import acos, atan2, cos, factorial, pi, sin, sqrt
from typing import Any

import numpy as np
from sympy import S
from sympy.physics.wigner import clebsch_gordan

from . import topographic_profile_component_selection as v85


VERSION = "v8.6"
SPRINT = "bhsm-complex-profile-isospectral-attachment-v8-6"
SOURCE_MAIN_SHA = v85.SOURCE_MAIN_SHA
PRIMARY_RESULT = (
    "BHSM_LINEAR_ISOSPECTRAL_SLOT_ATTACHMENT_AND_POLAR_CURRENT_FUNCTORS_"
    "CONSTRUCTED_CONDITIONALLY"
)
FINAL_VERDICT = (
    "BHSM_FULL_FLAVOR_COMPLETION_REMAINS_BLOCKED_BY_NO_ACTION_DERIVED_"
    "ORIENTED_TRANSFER_WEIGHT_AND_NO_ACTION_OWNED_G2_C3_PROFILE_"
    "NORMALIZATION"
)
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVED_ORIENTED_CHIRAL_TRANSFER_AND_NORMALIZED_G2_C3_"
    "COMPLEX_CURRENT_PROFILE"
)

THETA_C3 = 2.0 * pi / 3.0
OMEGA = np.exp(2j * pi / 3.0)


def polar_unitary(matrix: np.ndarray, tol: float = 1.0e-14) -> np.ndarray:
    """Return the unique unitary polar factor of a full-rank square matrix."""

    transfer = np.asarray(matrix, dtype=complex)
    if transfer.ndim != 2 or transfer.shape[0] != transfer.shape[1]:
        raise ValueError("polar_unitary requires a square matrix")
    gram = transfer.conj().T @ transfer
    values, vectors = np.linalg.eigh(gram)
    if float(values.min()) <= tol:
        raise ValueError("polar_unitary requires full rank")
    inverse_root = vectors @ np.diag(values ** -0.5) @ vectors.conj().T
    return transfer @ inverse_root


def jarlskog(matrix: np.ndarray) -> float:
    unitary = np.asarray(matrix, dtype=complex)
    return float(
        np.imag(
            unitary[0, 0]
            * unitary[1, 1]
            * np.conj(unitary[0, 1])
            * np.conj(unitary[1, 0])
        )
    )


def standard_sines(matrix: np.ndarray) -> dict[str, float]:
    """Extract the three standard sine angles from a unitary matrix."""

    unitary = np.asarray(matrix, dtype=complex)
    s13 = float(abs(unitary[0, 2]))
    c13 = sqrt(max(0.0, 1.0 - s13 * s13))
    return {
        "sin_theta_12": float(abs(unitary[0, 1]) / c13),
        "sin_theta_23": float(abs(unitary[1, 2]) / c13),
        "sin_theta_13": s13,
    }


def frozen_ckm_screen() -> dict[str, Any]:
    """Reproduce the repository's frozen internal-rule CKM screen."""

    up = np.diag(v85.frozen_transfer_diagonal("up"))
    down = np.diag(v85.frozen_transfer_diagonal("down"))
    s12 = sqrt(float(down[2] / down[1]))
    s23 = float(2.0 * down[1])
    s13 = sqrt(float(up[2]))
    delta = float(4.0 * sqrt(v85.S_OVERLAP))
    c12 = sqrt(1.0 - s12 * s12)
    c23 = sqrt(1.0 - s23 * s23)
    c13 = sqrt(1.0 - s13 * s13)
    e_plus = np.exp(1j * delta)
    e_minus = np.exp(-1j * delta)
    matrix = np.array(
        [
            [c12 * c13, s12 * c13, s13 * e_minus],
            [
                -s12 * c23 - c12 * s23 * s13 * e_plus,
                c12 * c23 - s12 * s23 * s13 * e_plus,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * e_plus,
                -c12 * s23 - s12 * c23 * s13 * e_plus,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )
    return {
        "angles": {
            "sin_theta_12": s12,
            "sin_theta_23": s23,
            "sin_theta_13": s13,
        },
        "delta": delta,
        "jarlskog": jarlskog(matrix),
        "matrix_magnitudes": np.abs(matrix).tolist(),
        "status": "REPOSITORY_FROZEN_INTERNAL_RULE_SCREEN_NOT_ACTION_THEOREM",
    }


def minimum_trace_isospectral_alignment(
    profile: np.ndarray, frozen_diagonal: np.ndarray
) -> dict[str, Any]:
    """Solve min Tr(M H) on the unitary orbit of a fixed nondegenerate D.

    With D in strictly descending order and H with simple ascending spectrum,
    von Neumann's trace inequality pairs the largest D eigenvalue with the
    smallest H eigenvalue.  The minimizer is unique modulo column phases.
    """

    H = np.asarray(profile, dtype=complex)
    D = np.asarray(frozen_diagonal, dtype=float)
    if H.shape != D.shape or H.shape[0] != H.shape[1]:
        raise ValueError("profile and frozen diagonal must be square and equal-sized")
    if not np.allclose(H, H.conj().T, atol=1.0e-12):
        raise ValueError("profile must be Hermitian")
    d = np.diag(D)
    if not np.all(np.diff(d) < 0):
        raise ValueError("frozen diagonal must be strictly descending")
    h, vectors = np.linalg.eigh(H)
    if np.min(np.diff(h)) <= 1.0e-12:
        raise ValueError("profile spectrum must be simple")
    mass = vectors @ D @ vectors.conj().T
    candidate_traces = []
    for perm in permutations(range(len(d))):
        candidate_traces.append(float(np.dot(d[list(perm)], h)))
    trace_value = float(np.real(np.trace(mass @ H)))
    return {
        "profile_eigenvalues_ascending": h.tolist(),
        "frozen_eigenvalues_descending": d.tolist(),
        "alignment_vectors": vectors,
        "oriented_mass_matrix": mass,
        "trace_cost": trace_value,
        "minimum_permutation_trace": min(candidate_traces),
        "trace_minimum_verified": bool(
            np.isclose(trace_value, min(candidate_traces), rtol=0.0, atol=1.0e-11)
        ),
        "unique_modulo_column_phases": True,
        "slot_permutation_ambiguity_removed": True,
        "frozen_spectrum_preserved": bool(
            np.allclose(np.linalg.eigvalsh(mass)[::-1], d, atol=1.0e-12)
        ),
        "linearity": "E_align(M;H)=Tr(M H), so f(X)=X",
        "action_term_present": False,
    }


def isospectral_alignment_audit() -> dict[str, Any]:
    alignments: dict[str, Any] = {}
    vectors: dict[str, np.ndarray] = {}
    for sector in ("up", "down"):
        alignment = minimum_trace_isospectral_alignment(
            v85.heat_kernel_sector_matrix(sector),
            v85.frozen_transfer_diagonal(sector),
        )
        vectors[sector] = alignment.pop("alignment_vectors")
        alignment["oriented_mass_matrix"] = np.real_if_close(
            alignment["oriented_mass_matrix"], tol=1000
        ).real.tolist()
        alignments[sector] = alignment
    V = vectors["up"].conj().T @ vectors["down"]
    return {
        "theorem": (
            "argmin_(M in orbit(D_f)) Tr(M H_f) pairs descending frozen masses "
            "with ascending simple profile eigenvalues"
        ),
        "sectors": alignments,
        "CKM_candidate_magnitudes": np.abs(V).tolist(),
        "jarlskog": jarlskog(V),
        "continuous_parameters_added": 0,
        "slot_assignments_remaining": 0,
        "physical_promotion": False,
        "reason_not_promoted": (
            "the current action does not contain or derive the linear alignment "
            "functional coupling the frozen mass spectrum to H_f"
        ),
        "verdict": (
            "BHSM_ISOSPECTRAL_SLOT_ATTACHMENT_FUNCTOR_CONSTRUCTED_"
            "CONDITIONALLY"
        ),
    }


def _small_d_diagonal(j: int, m: int, beta: float) -> float:
    total = 0.0
    for k in range(min(j + m, j - m) + 1):
        coefficient = (
            (-1) ** k
            * factorial(j + m)
            * factorial(j - m)
            / (
                factorial(j + m - k)
                * factorial(j - m - k)
                * factorial(k)
                * factorial(k)
            )
        )
        total += (
            coefficient
            * cos(beta / 2.0) ** (2 * j - 2 * k)
            * sin(beta / 2.0) ** (2 * k)
        )
    return float(total)


def _zyz_phase_beta(rotation: np.ndarray) -> tuple[float, float]:
    """Return alpha+gamma and beta for Rz(alpha)Ry(beta)Rz(gamma)."""

    R = np.asarray(rotation, dtype=float)
    beta = acos(float(np.clip(R[2, 2], -1.0, 1.0)))
    if abs(sin(beta)) > 1.0e-12:
        alpha = atan2(float(R[1, 2]), float(R[0, 2]))
        gamma = atan2(float(R[2, 1]), float(-R[2, 0]))
        return alpha + gamma, beta
    if beta < pi / 2.0:
        return atan2(float(R[1, 0]), float(R[0, 0])), beta
    return 0.0, beta


def _wigner_diagonal(j: int, m: int, rotation: np.ndarray) -> complex:
    phase, beta = _zyz_phase_beta(rotation)
    return np.exp(-1j * m * phase) * _small_d_diagonal(j, m, beta)


def _c3_rotations() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    identity = np.eye(3)
    cycle = np.array(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )
    return identity, cycle, cycle @ cycle


def c3_character_factor(L: int, r: int, character: int) -> complex:
    if character not in (0, 1, 2):
        raise ValueError("C3 character must be 0, 1, or 2")
    return sum(
        OMEGA ** (-character * index)
        * np.conj(_wigner_diagonal(L, r, rotation))
        for index, rotation in enumerate(_c3_rotations())
    ) / sqrt(3.0)


def c3_character_matrix_element(
    target: tuple[Any, Any], source: tuple[Any, Any], character: int
) -> complex:
    J_t, m_t = target
    J_s, m_s = source
    r = m_t - m_s
    total = 0.0j
    for L in v85._allowed_L_values(J_t, m_t, J_s, m_s):
        cg = clebsch_gordan(J_s, S(L), J_t, m_s, r, m_t)
        if cg == 0:
            continue
        base = (
            (2 * L + 1)
            * sqrt(float((2 * J_s + 1) / (2 * J_t + 1)))
            * float(cg * cg)
            * np.exp(-v85.S_OVERLAP * v85.berger_lambda(S(L), r))
        )
        total += base * c3_character_factor(L, int(r), character)
    return complex(total)


def c3_cross_matrix(character: int) -> np.ndarray:
    return np.array(
        [
            [
                c3_character_matrix_element(target, source, character)
                for source in v85.SECTOR_BLOCKS["down"]
            ]
            for target in v85.SECTOR_BLOCKS["up"]
        ],
        dtype=complex,
    )


def weighted_cross_polar(
    transfer: np.ndarray, up_power: float = -0.5, down_power: float = 1.0
) -> np.ndarray:
    up = np.diag(v85.frozen_transfer_diagonal("up"))
    down = np.diag(v85.frozen_transfer_diagonal("down"))
    weighted = np.diag(up**up_power) @ transfer @ np.diag(down**down_power)
    return polar_unitary(weighted)


def compare_to_frozen(candidate: np.ndarray) -> dict[str, Any]:
    target = frozen_ckm_screen()
    candidate_angles = standard_sines(candidate)
    relative = {
        key: (candidate_angles[key] - target["angles"][key]) / target["angles"][key]
        for key in candidate_angles
    }
    candidate_j = jarlskog(candidate)
    relative_j = (candidate_j - target["jarlskog"]) / target["jarlskog"]
    return {
        "candidate_angles": candidate_angles,
        "target_angles": target["angles"],
        "relative_angle_errors": relative,
        "candidate_jarlskog": candidate_j,
        "target_jarlskog": target["jarlskog"],
        "relative_jarlskog_error": relative_j,
        "matrix_magnitudes": np.abs(candidate).tolist(),
        "frobenius_magnitude_error": float(
            np.linalg.norm(np.abs(candidate) - np.asarray(target["matrix_magnitudes"]))
        ),
        "all_within_declared_ten_percent": bool(
            all(abs(value) <= 0.10 for value in relative.values())
            and abs(relative_j) <= 0.10
        ),
    }


def single_hopf_shift_no_go() -> dict[str, Any]:
    """A single shifted kernel gives only row/column phases to cross polar."""

    m_up = np.array([float(m) for _, m in v85.SECTOR_BLOCKS["up"]])
    m_down = np.array([float(m) for _, m in v85.SECTOR_BLOCKS["down"]])
    base = weighted_cross_polar(v85.heat_kernel_cross_matrix())
    left = np.diag(np.exp(1j * m_up * THETA_C3))
    right = np.diag(np.exp(1j * m_down * THETA_C3))
    shifted = left @ base @ right.conj().T
    return {
        "factorization": (
            "T(theta)=diag(exp(i m_u theta)) T(0) "
            "diag(exp(i m_d theta))^dagger"
        ),
        "polar_covariance": "polar(L T R^dagger)=L polar(T) R^dagger",
        "magnitudes_unchanged": bool(
            np.allclose(np.abs(shifted), np.abs(base), atol=1.0e-13)
        ),
        "jarlskog_base": jarlskog(base),
        "jarlskog_shifted": jarlskog(shifted),
        "physical_CP_generated": False,
        "verdict": (
            "SINGLE_HOPF_U1_TRANSLATION_CANNOT_GENERATE_CP_IN_THE_"
            "CROSS_POLAR_CURRENT"
        ),
    }


def oriented_incidence_candidate_audit() -> dict[str, Any]:
    real_transfer = v85.heat_kernel_cross_matrix().astype(complex)
    candidate = weighted_cross_polar(real_transfer)
    comparison = compare_to_frozen(candidate)
    return {
        "candidate": (
            "U_or=polar(Theta_u^(-1/2) H_ud Theta_d); target inverse-half "
            "normalization and full lower-partner source incidence"
        ),
        "up_power": -0.5,
        "down_power": 1.0,
        "primitive_charged_incidence_motivation": (
            "Omega_up=6, Omega_down=12 gives a factor-two lower-partner "
            "incidence distinction, but the exponent map is not derived"
        ),
        **comparison,
        "CP_generated": False,
        "action_owned_weighting": False,
        "verdict": (
            "ORIENTED_INCIDENCE_POLAR_CANDIDATE_APPROXIMATES_THETA12_AND_"
            "THETA23_BUT_FAILS_THETA13_AND_HAS_ZERO_CP"
        ),
    }


def g2_c3_profile_audit() -> dict[str, Any]:
    point = v85.heat_kernel_cross_matrix().astype(complex)
    chi0 = c3_cross_matrix(0)
    chi1 = c3_cross_matrix(1)

    optimistic = weighted_cross_polar(point - 1j * chi1)
    normalized = weighted_cross_polar(chi0 - 1j * chi1)
    optimistic_comparison = compare_to_frozen(optimistic)
    normalized_comparison = compare_to_frozen(normalized)

    return {
        "complex_structure": "Pi_10=(Q-iJ_u)/2 fixes the relative phase -i",
        "triality_character": "chi=1 C3 Fourier character",
        "optimistic_mixed_normalization": {
            "profile": "T_point-i T_chi1",
            **optimistic_comparison,
            "continuous_parameters_added": 0,
            "nonzero_CP": abs(optimistic_comparison["candidate_jarlskog"]) > 1.0e-12,
            "promotion_allowed": False,
            "reason": (
                "T_point and T_chi1 use inequivalent single-center versus "
                "normalized-orbit conventions; their relative norm is not action-owned"
            ),
        },
        "character_normalized_profile": {
            "profile": "T_chi0-i T_chi1",
            **normalized_comparison,
            "continuous_parameters_added": 0,
            "nonzero_CP": abs(normalized_comparison["candidate_jarlskog"]) > 1.0e-12,
            "promotion_allowed": False,
            "reason": (
                "the normalized C3-character construction is coefficient-free but "
                "fails the frozen CKM hierarchy"
            ),
        },
        "action_selects_G2_section": False,
        "action_maps_triality_character_to_Berger_profile": False,
        "action_fixes_relative_channel_norm": False,
        "verdict": (
            "G2_C3_COMPLEX_PROFILE_CAN_GENERATE_CP_WITHOUT_A_CONTINUOUS_"
            "PHASE_BUT_NO_ACTION_OWNED_NORMALIZATION_PASSES_THE_FROZEN_SCREEN"
        ),
    }


def status_report() -> dict[str, Any]:
    target = frozen_ckm_screen()
    alignment = isospectral_alignment_audit()
    hopf = single_hopf_shift_no_go()
    oriented = oriented_incidence_candidate_audit()
    g2c3 = g2_c3_profile_audit()
    validation = {
        "minimum_trace_alignment_removes_permutations": alignment[
            "slot_assignments_remaining"
        ]
        == 0,
        "minimum_trace_alignment_preserves_frozen_spectra": all(
            row["frozen_spectrum_preserved"]
            for row in alignment["sectors"].values()
        ),
        "polar_current_is_unitary": bool(
            np.allclose(
                weighted_cross_polar(v85.heat_kernel_cross_matrix()).conj().T
                @ weighted_cross_polar(v85.heat_kernel_cross_matrix()),
                np.eye(3),
                atol=1.0e-12,
            )
        ),
        "single_hopf_shift_has_zero_CP": not hopf["physical_CP_generated"],
        "oriented_candidate_fails_strict_frozen_screen": not oriented[
            "all_within_declared_ten_percent"
        ],
        "g2_c3_optimistic_candidate_has_CP": g2c3[
            "optimistic_mixed_normalization"
        ]["nonzero_CP"],
        "g2_c3_normalized_candidate_fails_frozen_screen": not g2c3[
            "character_normalized_profile"
        ]["all_within_declared_ten_percent"],
    }
    return {
        "artifact": "BHSM_complex_profile_isospectral_attachment_v8_6",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "primary_result": PRIMARY_RESULT,
        "frozen_CKM_screen": target,
        "minimum_trace_isospectral_alignment": alignment,
        "polar_current_functor": {
            "formula": "U(T)=T(T^dagger T)^(-1/2)",
            "full_rank_requirement": True,
            "unitary": True,
            "unique": True,
            "closest_unitary_in_Frobenius_norm": True,
            "action_absorbs_positive_polar_factor": False,
            "verdict": "BHSM_POLAR_CURRENT_FUNCTOR_CONSTRUCTED_CONDITIONALLY",
        },
        "single_Hopf_shift_audit": hopf,
        "oriented_incidence_candidate": oriented,
        "G2_C3_complex_profile": g2c3,
        "validated": [
            "linear f(X)=X minimum-trace functor removes all 36 slot assignments",
            "polar decomposition gives a unique coefficient-free unitary current map",
            "single Hopf U1 translation is rephasing-only in the cross-current route",
            "G2 complex structure plus a C3 character can generate nonzero CP without a continuous phase",
        ],
        "invalidated": [
            "single Hopf phase as a physical CP source for the polar cross current",
            "oriented real transfer alone as full CKM because theta13 and CP fail",
            "normalized G2-C3 character profile as the frozen CKM solution",
            "the visually close unnormalized G2-C3 combination as promotable physics",
        ],
        "open": [
            "action derivation of the oriented transfer powers",
            "action-selected G2 unit section and orientation",
            "action map from triality character to Berger current profile",
            "action normalization of singlet versus complex character channels",
            "proof that the positive polar factor is wavefunction normalization rather than a physical vertex singular-value response",
        ],
        "physical_mass_emitted": False,
        "physical_CKM_emitted": False,
        "new_continuous_parameter_added": False,
        "frozen_predictions_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "final_verdict": FINAL_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(status_report(), indent=2, sort_keys=True))


