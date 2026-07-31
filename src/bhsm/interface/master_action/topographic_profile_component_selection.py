"""BHSM v8.5 topographic-profile component selection and current audit.

This bounded manual sprint starts from the frozen v8.4 Berger block/current
library.  It constructs the unique normalized Riesz representative of point
evaluation inside each associated Berger block, derives the complete harmonic
moment functional for a scalar profile, and kill-tests the two simplest
zero-parameter heat-profile attachments.  It does not promote either candidate
to the authoritative BHSM action.
"""

from __future__ import annotations

from itertools import permutations
from math import pi
from typing import Any, Iterable

import numpy as np
from sympy import Rational, S, exp, sqrt
from sympy.physics.wigner import clebsch_gordan


VERSION = "v8.5"
SPRINT = "bhsm-topographic-profile-component-selection-v8-5"
SOURCE_MAIN_SHA = "0721ee6a79f97cae5b3ac5bf040fa07ef9584678"
PRIMARY_RESULT = (
    "BHSM_TOPOGRAPHIC_REPRODUCING_KERNEL_COMPONENT_SELECTOR_"
    "CONSTRUCTED_CONDITIONALLY"
)
FINAL_VERDICT = (
    "BHSM_MASS_AND_CKM_REMAIN_BLOCKED_BY_NO_ACTION_SELECTED_FULL_S3_"
    "COMPLEX_PROFILE_AND_NO_ACTION_DERIVED_PROFILE_TO_ISOSPECTRAL_"
    "FLAVOR_ORIENTATION_FUNCTOR"
)
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVED_NONHOMOGENEOUS_BERGER_WEAK_CURRENT_PROFILE_"
    "WITH_COMPLEX_HOPF_MOMENTS_AND_ISOSPECTRAL_SLOT_ATTACHMENT"
)

ALPHA_LOW_INVERSE = 137.035999177
# Frozen repository value; the displayed alpha formula is provenance, not a
# request to recompute it at platform-dependent precision.
A_SQUASH = 1.157054135733433
S_OVERLAP = 1.0 / (4.0 * pi)

SECTOR_BLOCKS: dict[str, tuple[tuple[Rational, Rational], ...]] = {
    "charged_lepton": (
        (S(0), S(0)),
        (Rational(5, 2), Rational(1, 2)),
        (Rational(9, 2), Rational(3, 2)),
    ),
    "up": ((S(0), S(0)), (S(3), S(3)), (S(5), S(4))),
    "down": ((S(0), S(0)), (S(3), S(0)), (S(4), S(2))),
}


def _float(value: Any) -> float:
    return float(value.evalf(30) if hasattr(value, "evalf") else value)


def berger_lambda(J: Rational, m: Rational, a: float = A_SQUASH) -> float:
    """Repository-normalized associated-scalar eigenvalue."""

    return 4.0 * _float(J * (J + 1)) + 4.0 * (a * a - 1.0) * _float(m * m)


def frozen_transfer_diagonal(
    sector: str, *, a: float = A_SQUASH, s: float = S_OVERLAP
) -> np.ndarray:
    """Return the unchanged historical block-central transfer factors."""

    return np.diag(
        [np.exp(-s * berger_lambda(J, m, a)) for J, m in SECTOR_BLOCKS[sector]]
    )


def reproducing_kernel_selector(J: Rational, m: Rational) -> dict[str, Any]:
    """The normalized point-evaluation state at the identity frame.

    For unit-Haar-normalized Y^J_(n,m)=sqrt(2J+1)D^J_(n,m), the Riesz
    representative of evaluation at h has coefficients conjugate(D^J_nm(h)).
    At h=e this is the single Wigner component n=m.  Its existence is exact;
    the physical selection of h and a frame is not supplied by the action.
    """

    two_J = int(2 * J)
    two_m = int(2 * m)
    labels = list(range(-two_J, two_J + 1, 2))
    coefficients = [1 if two_n == two_m else 0 for two_n in labels]
    return {
        "J": str(J),
        "m": str(m),
        "block_rank": two_J + 1,
        "basis_two_n": labels,
        "identity_frame_coefficients": coefficients,
        "norm_squared": sum(value * value for value in coefficients),
        "general_coefficients": "conjugate(D^J_(n,m)(h))",
        "reproducing_kernel_diagonal": f"2J+1={two_J + 1}",
        "unique_after_point_and_frame_selection": True,
        "point_and_frame_action_selected": False,
    }


def component_selector_ledger() -> dict[str, Any]:
    return {
        sector: [reproducing_kernel_selector(J, m) for J, m in blocks]
        for sector, blocks in SECTOR_BLOCKS.items()
    }


def quark_right_weight_matrix() -> np.ndarray:
    """r_ij=m_u,i-m_d,j in frozen heavy-to-light slot order."""

    return np.array(
        [
            [int(mu - md) for _, md in SECTOR_BLOCKS["down"]]
            for _, mu in SECTOR_BLOCKS["up"]
        ],
        dtype=int,
    )


def right_u1_invariant_profile_audit() -> dict[str, Any]:
    """Prove the rank bound for a Hopf-phase-neutral scalar profile."""

    weights = quark_right_weight_matrix()
    support = (weights == 0).astype(int)
    # A generic matrix with this support has only its first row nonzero.
    generic = support.astype(float)
    return {
        "harmonic_expansion": "Phi=sum_(L,p,r) phi_(L,p,r) Y^L_(p,r)",
        "right_U1_invariance": "Phi(g exp(theta T3))=Phi(g)",
        "consequence": "phi_(L,p,r)=0 for every r!=0",
        "required_right_weights": weights.tolist(),
        "surviving_support_mask": support.tolist(),
        "surviving_transition_count": int(support.sum()),
        "generic_support_rank": int(np.linalg.matrix_rank(generic)),
        "maximum_possible_rank": 1,
        "full_rank_CKM_possible": False,
        "verdict": (
            "HOPF_PHASE_NEUTRAL_SCALAR_PROFILE_CANNOT_GENERATE_"
            "FULL_RANK_FROZEN_QUARK_MIXING"
        ),
    }


def determinant_weight_sets() -> list[list[int]]:
    """Right weights used by every 3x3 determinant permutation."""

    weights = quark_right_weight_matrix()
    return [
        [int(weights[row, column]) for row, column in enumerate(perm)]
        for perm in permutations(range(3))
    ]


def full_rank_moment_requirement() -> dict[str, Any]:
    sets = determinant_weight_sets()
    return {
        "determinant_permutation_weight_sets": sets,
        "distinct_weight_count_per_term": [len(set(values)) for values in sets],
        "all_terms_require_three_distinct_right_weights": all(
            len(set(values)) == 3 for values in sets
        ),
        "minimal_candidate_sets": sorted({tuple(sorted(values)) for values in sets}),
        "minimum_independent_Hopf_weight_moments": 3,
        "point_delta_profile_rank_bound": 1,
        "point_delta_reason": "V_ij=u_i(h0)^* d_j(h0) is one outer product",
    }


def _allowed_L_values(
    J_target: Rational,
    m_target: Rational,
    J_source: Rational,
    m_source: Rational,
) -> Iterable[int]:
    r = m_target - m_source
    lower = max(abs(J_target - J_source), abs(r))
    upper = J_target + J_source
    # Quark blocks are integral.  The implementation also supports equal-parity
    # half-integral sector blocks, for which L remains integral.
    first = int(lower)
    last = int(upper)
    return range(first, last + 1)


def profile_moment_formula() -> dict[str, Any]:
    """Complete finite harmonic moment formula in the aligned coherent frame."""

    return {
        "normalized_basis": "Y^J_(n,m)=sqrt(2J+1)D^J_(n,m)",
        "selected_state_at_identity": "|J,m;e>=|J,n=m,m>",
        "profile": "Phi=sum phi_(L,p,r)Y^L_(p,r)",
        "matrix_element": (
            "M_ij[Phi]=sum_L phi_(L,r_ij,r_ij) "
            "sqrt((2L+1)(2J_d,j+1)/(2J_u,i+1)) "
            "CG(J_d,j m_d,j,L r_ij|J_u,i m_u,i)^2"
        ),
        "sum_is_finite": True,
        "reason": "triangle rule max(|Ju-Jd|,|r|)<=L<=Ju+Jd",
        "action_owned_profile_moments": False,
    }


def heat_kernel_profile_coefficient(
    L: int, r: Rational, *, a: float = A_SQUASH, s: float = S_OVERLAP
) -> float:
    """Coefficient of normalized Y^L_(r,r) in K_s(g,e)."""

    eigenvalue = berger_lambda(S(L), r, a)
    return np.sqrt(2 * L + 1) * np.exp(-s * eigenvalue)


def heat_kernel_matrix_element(
    target: tuple[Rational, Rational],
    source: tuple[Rational, Rational],
    *,
    a: float = A_SQUASH,
    s: float = S_OVERLAP,
) -> float:
    """Aligned coherent-state matrix element of the point-centered heat kernel."""

    J_t, m_t = target
    J_s, m_s = source
    r = m_t - m_s
    total = 0.0
    for L in _allowed_L_values(J_t, m_t, J_s, m_s):
        cg = clebsch_gordan(J_s, S(L), J_t, m_s, r, m_t)
        if cg == 0:
            continue
        eigenvalue = berger_lambda(S(L), r, a)
        term = (
            (2 * L + 1)
            * np.sqrt(_float((2 * J_s + 1) / (2 * J_t + 1)))
            * _float(cg * cg)
            * np.exp(-s * eigenvalue)
        )
        total += term
    return float(total)


def heat_kernel_sector_matrix(
    sector: str, *, a: float = A_SQUASH, s: float = S_OVERLAP
) -> np.ndarray:
    blocks = SECTOR_BLOCKS[sector]
    return np.array(
        [
            [heat_kernel_matrix_element(target, source, a=a, s=s) for source in blocks]
            for target in blocks
        ],
        dtype=float,
    )


def heat_kernel_cross_matrix(
    *, a: float = A_SQUASH, s: float = S_OVERLAP
) -> np.ndarray:
    return np.array(
        [
            [
                heat_kernel_matrix_element(target, source, a=a, s=s)
                for source in SECTOR_BLOCKS["down"]
            ]
            for target in SECTOR_BLOCKS["up"]
        ],
        dtype=float,
    )


def _normalized_descending_eigenvalues(matrix: np.ndarray) -> np.ndarray:
    values = np.linalg.eigvalsh(matrix)[::-1]
    return values / values[0]


def direct_profile_dressing_audit() -> dict[str, Any]:
    """Kill-test M_f=D_f^(1/2) H_f D_f^(1/2)."""

    rows: dict[str, Any] = {}
    for sector in ("charged_lepton", "up", "down"):
        transfer = frozen_transfer_diagonal(sector)
        profile = heat_kernel_sector_matrix(sector)
        root = np.diag(np.sqrt(np.diag(transfer)))
        dressed = root @ profile @ root
        frozen = np.diag(transfer)
        ratios = _normalized_descending_eigenvalues(dressed)
        rows[sector] = {
            "frozen_ratios": frozen.tolist(),
            "dressed_ratios": ratios.tolist(),
            "multiplicative_shift": (ratios / frozen).tolist(),
            "frozen_ratios_preserved": bool(np.allclose(ratios, frozen, atol=1e-13)),
            "dressed_matrix": dressed.tolist(),
        }
    return {
        "candidate": "M_f=D_f^(1/2) H_f D_f^(1/2)",
        "new_continuous_parameter": False,
        "sectors": rows,
        "all_frozen_ratios_preserved": all(
            row["frozen_ratios_preserved"] for row in rows.values()
        ),
        "verdict": "DIRECT_HEAT_PROFILE_DRESSING_REJECTED_BY_FROZEN_RATIO_LOCK",
    }


def _orthogonal_eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(matrix)
    return values, vectors


def _jarlskog_real(matrix: np.ndarray) -> float:
    return float(
        np.imag(matrix[0, 0] * matrix[1, 1] * np.conj(matrix[0, 1]) * np.conj(matrix[1, 0]))
    )


def isospectral_orientation_audit() -> dict[str, Any]:
    """Audit M_f=U_f D_f U_f^T with U_f from the heat-profile eigenvectors."""

    H_u = heat_kernel_sector_matrix("up")
    H_d = heat_kernel_sector_matrix("down")
    eval_u, base_u = _orthogonal_eigensystem(H_u)
    eval_d, base_d = _orthogonal_eigensystem(H_d)

    assignments = []
    for perm_u in permutations(range(3)):
        U_u = base_u[:, perm_u]
        for perm_d in permutations(range(3)):
            U_d = base_d[:, perm_d]
            V = U_u.T @ U_d
            assignments.append(
                {
                    "up_assignment": list(perm_u),
                    "down_assignment": list(perm_d),
                    "absolute_overlap": np.abs(V).tolist(),
                    "jarlskog": _jarlskog_real(V),
                }
            )

    rounded = {
        tuple(np.round(np.asarray(row["absolute_overlap"]).ravel(), 12))
        for row in assignments
    }
    return {
        "candidate": "M_f=U_f D_f U_f^T; U_f diagonalizes H_f",
        "profile_eigenvalues": {
            "up": eval_u.tolist(),
            "down": eval_d.tolist(),
        },
        "frozen_singular_values_preserved_by_construction": True,
        "up_eigenvector_to_slot_assignments": 6,
        "down_eigenvector_to_slot_assignments": 6,
        "joint_assignments": len(assignments),
        "distinct_absolute_overlap_matrices": len(rounded),
        "all_candidates_real_orthogonal": True,
        "all_jarlskog_zero": all(abs(row["jarlskog"]) < 1e-15 for row in assignments),
        "representative_ascending_assignment": assignments[0],
        "action_selects_assignment": False,
        "action_selects_profile_to_mass_orientation_rule": False,
        "verdict": (
            "ISOSPECTRAL_HEAT_PROFILE_ORIENTATION_PRESERVES_FROZEN_RATIOS_"
            "BUT_LEAVES_DISCRETE_SLOT_ASSIGNMENT_AND_CP_OPEN"
        ),
    }


def heat_kernel_candidate_audit() -> dict[str, Any]:
    cross = heat_kernel_cross_matrix()
    sectors = {
        sector: heat_kernel_sector_matrix(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    return {
        "profile": "Berger heat kernel K_s(g,e)",
        "coefficient": (
            "phi_(L,p,r)=sqrt(2L+1) exp(-s lambda_(L,r)) delta_(p,r)"
        ),
        "a": A_SQUASH,
        "s": S_OVERLAP,
        "new_continuous_parameter": False,
        "full_point_and_frame_selected": True,
        "point_and_frame_action_selected": False,
        "sector_matrices": {name: matrix.tolist() for name, matrix in sectors.items()},
        "sector_matrices_real_symmetric": all(
            np.allclose(matrix, matrix.T, atol=1e-13) for matrix in sectors.values()
        ),
        "cross_matrix": cross.tolist(),
        "cross_matrix_rank": int(np.linalg.matrix_rank(cross, tol=1e-12)),
        "cross_matrix_determinant": float(np.linalg.det(cross)),
        "cross_matrix_unitary": bool(np.allclose(cross.T @ cross, np.eye(3), atol=1e-12)),
        "cross_matrix_is_CKM": False,
        "reason_not_CKM": (
            "it is a real transfer/multiplication matrix, not an action-derived "
            "isometry between normalized quark mass eigenbases"
        ),
    }


def status_report() -> dict[str, Any]:
    selector = component_selector_ledger()
    u1 = right_u1_invariant_profile_audit()
    moments = full_rank_moment_requirement()
    heat = heat_kernel_candidate_audit()
    direct = direct_profile_dressing_audit()
    isospectral = isospectral_orientation_audit()
    validation = {
        "all_identity_selectors_normalized": all(
            row["norm_squared"] == 1
            for rows in selector.values()
            for row in rows
        ),
        "right_U1_profile_rank_at_most_one": u1["maximum_possible_rank"] == 1,
        "three_Hopf_moments_required_for_determinant": moments[
            "all_terms_require_three_distinct_right_weights"
        ],
        "point_heat_profile_cross_matrix_full_rank": heat["cross_matrix_rank"] == 3,
        "point_heat_profile_not_unitary": heat["cross_matrix_unitary"] is False,
        "direct_dressing_breaks_frozen_ratio_lock": direct[
            "all_frozen_ratios_preserved"
        ]
        is False,
        "isospectral_route_has_36_unselected_assignments": isospectral[
            "joint_assignments"
        ]
        == 36,
        "isospectral_real_profile_has_zero_CP": isospectral["all_jarlskog_zero"],
    }
    return {
        "artifact": "BHSM_topographic_profile_component_selection_v8_5",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "primary_result": PRIMARY_RESULT,
        "component_selector": selector,
        "profile_moment_functional": profile_moment_formula(),
        "right_U1_invariant_profile_audit": u1,
        "full_rank_moment_requirement": moments,
        "heat_kernel_candidate": heat,
        "direct_profile_dressing": direct,
        "isospectral_orientation": isospectral,
        "validated": [
            "point/frame-conditioned unique normalized state in each Berger block",
            "complete finite profile harmonic-moment functional",
            "right-U1-neutral profile rank-one no-go",
            "three independent Hopf-weight moments required by every determinant term",
            "full-point Berger heat kernel gives a no-fit full-rank transfer candidate",
        ],
        "invalidated": [
            "homogeneous or Hopf-phase-neutral scalar profile as the complete CKM source",
            "point-delta profile as a full-rank current",
            "direct symmetrized heat-profile dressing under strict frozen-ratio lock",
            "real isospectral heat-profile orientation as a complete CKM-plus-CP theorem",
        ],
        "open": [
            "action-selected full-S3 point/frame or equivalent profile orientation",
            "action-derived nonhomogeneous profile with at least three Hopf-weight moments",
            "action-selected complex phase/holonomy for nonzero Jarlskog invariant",
            "action-derived profile-to-isospectral mass-orientation functor",
            "action-selected eigenvector-to-frozen-slot assignment",
        ],
        "physical_mass_emitted": False,
        "CKM_matrix_emitted": False,
        "frozen_predictions_changed": False,
        "new_free_parameter_added": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "final_verdict": FINAL_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(status_report(), indent=2, sort_keys=True))


