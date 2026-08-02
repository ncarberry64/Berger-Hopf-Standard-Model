"""Exact action-character matrix, including the relational ontology candidates."""

from __future__ import annotations

from typing import Any

from sympy import Matrix


PRE_ONTOLOGY_VARIABLES = ["r_e", "w_gauge_connection", "w_projector", "w_chi", "w_sigma", "w_psi", "w_phi", "w_C", "w_W", "w_wall_embedding", "w_compatibility", "w_core"]
RELATIONAL_VARIABLES = ["w_attachment", "w_embedding", "w_normal_bundle", "w_relational_interval", "w_surface", "w_displacement_current", "w_BH_transfer"]
VARIABLES = PRE_ONTOLOGY_VARIABLES + RELATIONAL_VARIABLES
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
    return Matrix([coefficients + [0] * len(RELATIONAL_VARIABLES) for _, coefficients in ROWS])


def constraint_payload() -> dict[str, Any]:
    matrix = constraint_matrix()
    nullspace = [[int(value) for value in vector] for vector in matrix.nullspace()]
    validation = {
        "matrix_exact": matrix.shape == (12, 19),
        "rank_exact": matrix.rank() == 7,
        "nullity_exact": len(nullspace) == 12,
        "forced_coframe_trivial": all(vector[0] == 0 for vector in nullspace),
        "open_columns_exact": [VARIABLES[i] for i in range(matrix.cols) if all(matrix[j, i] == 0 for j in range(matrix.rows))] == VARIABLES[7:],
    }
    return {
        "artifact": "BHSM_support_character_constraint_system_v11_2",
        "scope": "maximal exact homogeneous-character system justified by explicit frozen S8/S4 terms, with the new relational objects included as columns but no ontology-only equation promoted to an action constraint",
        "assumptions": [
            "the provisional coframe character acts on the full D8 metric and its induced localized S4 coframe",
            "existing independent coefficients are inert rather than spurions",
            "real and Hermitian-conjugate fields co-scale under the positive real character in this candidate",
            "action invariance is tested as a candidate global representation symmetry; no local G_D gauge symmetry is assumed",
        ],
        "coefficient_policy": "existing independent action coefficients are inert; assigning spurion characters would add the missing datum rather than derive it",
        "pre_ontology_result_preserved": {"shape": [12, 12], "rank": 7, "nullity": 5},
        "variables": VARIABLES,
        "row_labels": [label for label, _ in ROWS],
        "matrix": [coefficients + [0] * len(RELATIONAL_VARIABLES) for _, coefficients in ROWS],
        "right_hand_side": [0] * len(ROWS),
        "rank": matrix.rank(),
        "nullity": len(nullspace),
        "nullspace_basis": nullspace,
        "forced_zero_within_full_coframe_candidate": VARIABLES[:7],
        "unconstrained": VARIABLES[7:],
        "discrete_solutions": [],
        "sign_ambiguities": VARIABLES[7:],
        "continuous_rescalings": "twelve independent directions after including relational candidates, not one common normalization",
        "common_normalization_direction": None,
        "physical_null_directions": VARIABLES[7:],
        "inconsistent_rows": [],
        "sector_specific_ambiguities": ["w_C", "w_W", "w_compatibility"],
        "boundary_only_ambiguities": ["w_wall_embedding", "w_surface"],
        "core_only_ambiguities": ["w_core", "w_BH_transfer"],
        "boundary_only_constraints": [],
        "core_only_constraints": [],
        "ontology_rows_not_promoted": ["core/surface opposition", "attachment neutrality", "boundary spectral invariance", "displacement conservation", "black-hole transfer neutrality"],
        "interpretation": "the current action rejects nontrivial universal/intrinsic coframe scaling but supplies no attachment, embedding, displacement, boundary-spectrum, or transfer equation; the ontology relocates the leading candidate without fixing it",
        "status": "EXACT_EXPANDED_CONSTRAINT_MATRIX_RANK_7_NULLITY_12_ATTACHMENT_LEDGER_UNDERDETERMINED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
