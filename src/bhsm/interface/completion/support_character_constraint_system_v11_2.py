"""Exact action-character constraint matrix for the strongest coframe lift."""

from __future__ import annotations

from typing import Any

from sympy import Matrix


VARIABLES = ["r_e", "w_gauge_connection", "w_projector", "w_chi", "w_sigma", "w_psi", "w_phi", "w_C", "w_W", "w_wall_embedding", "w_compatibility", "w_core"]
ROWS = [
    ("S8_Einstein_Hilbert", [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("S8_cosmological", [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("S8_sigma_mass", [8, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]),
    ("S8_sigma_quartic", [8, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0]),
    ("S8_chi_kinetic", [6, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("nonabelian_F_homogeneity", [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("projector_idempotency", [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("S4_fermion_kinetic", [3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0]),
    ("S4_scalar_kinetic", [2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]),
    ("S4_Yukawa", [4, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]),
    ("S4_scalar_quartic", [4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0]),
    ("S4_scalar_mass", [4, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]),
]


def constraint_matrix() -> Matrix:
    return Matrix([coefficients for _, coefficients in ROWS])


def constraint_payload() -> dict[str, Any]:
    matrix = constraint_matrix()
    nullspace = [[int(value) for value in vector] for vector in matrix.nullspace()]
    validation = {
        "matrix_exact": matrix.shape == (12, 12),
        "rank_exact": matrix.rank() == 7,
        "nullity_exact": len(nullspace) == 5,
        "forced_coframe_trivial": all(vector[0] == 0 for vector in nullspace),
        "open_columns_exact": [VARIABLES[i] for i in range(len(VARIABLES)) if all(row[i] == 0 for _, row in ROWS)] == VARIABLES[7:],
    }
    return {
        "artifact": "BHSM_support_character_constraint_system_v11_2",
        "scope": "maximal exact homogeneous-character system justified by the explicit frozen S8/S4 terms and the full-coframe candidate",
        "assumptions": [
            "the provisional coframe character acts on the full D8 metric and its induced localized S4 coframe",
            "existing independent coefficients are inert rather than spurions",
            "real and Hermitian-conjugate fields co-scale under the positive real character in this candidate",
            "action invariance is tested as a candidate global representation symmetry; no local G_D gauge symmetry is assumed",
        ],
        "coefficient_policy": "existing independent action coefficients are inert; assigning spurion characters would add the missing datum rather than derive it",
        "variables": VARIABLES,
        "row_labels": [label for label, _ in ROWS],
        "matrix": [coefficients for _, coefficients in ROWS],
        "right_hand_side": [0] * len(ROWS),
        "rank": matrix.rank(),
        "nullity": len(nullspace),
        "nullspace_basis": nullspace,
        "forced_zero_within_full_coframe_candidate": VARIABLES[:7],
        "unconstrained": VARIABLES[7:],
        "discrete_solutions": [],
        "sign_ambiguities": VARIABLES[7:],
        "continuous_rescalings": "five independent directions, not one common normalization",
        "sector_specific_ambiguities": ["w_C", "w_W", "w_compatibility"],
        "boundary_only_ambiguities": ["w_wall_embedding"],
        "core_only_ambiguities": ["w_core"],
        "interpretation": "the current action rejects nontrivial universal coframe scaling but contains no equations for the intended support, wall, compatibility, and core characters",
        "status": "EXACT_CONSTRAINT_MATRIX_RANK_7_NULLITY_5_PRIMITIVE_LEDGER_UNDERDETERMINED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
