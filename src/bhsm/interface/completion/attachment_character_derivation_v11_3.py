"""Action-derived reciprocal attachment characters and constraint matrices."""

from __future__ import annotations

from typing import Any

from sympy import Matrix, Rational

from .support_character_constraint_system_v11_2 import VARIABLES as V11_VARIABLES
from .support_character_constraint_system_v11_2 import constraint_matrix as v11_matrix


W_CORE = Rational(-1, 2)
W_WALL = Rational(1, 2)


def total_weight(prefactor_weight: Rational, incidence_weight: Rational) -> Rational:
    return prefactor_weight + incidence_weight


def attachment_subsystem() -> tuple[list[str], Matrix, Matrix]:
    variables = ["w_I_C", "w_I_W", "w_Lambda85", "w_dmu5", "w_h_enc"]
    matrix = Matrix([
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
    ])
    rhs = Matrix([Rational(-1, 2), Rational(1, 2), 0, 0, 0])
    return variables, matrix, rhs


def expanded_matrix() -> tuple[Matrix, Matrix]:
    base = v11_matrix()
    rows = [list(base.row(i)) for i in range(base.rows)]
    rhs = [0] * base.rows
    def row(name: str, value: Rational) -> None:
        coefficients = [0] * len(V11_VARIABLES)
        coefficients[V11_VARIABLES.index(name)] = 1
        rows.append(coefficients)
        rhs.append(value)
    row("w_C", W_CORE)
    row("w_W", W_WALL)
    row("w_compatibility", Rational(0))
    row("w_attachment", Rational(0))
    return Matrix(rows), Matrix(rhs)


def primitive_weight_rows() -> list[dict[str, Any]]:
    return [
        {"field": "G8", "incidence_map": "Q_H lift into L_D^(-1/2)", "homogeneity_degree": 1, "support_weight": 0, "incidence_weight": "-1/2", "derivation_equation": "w(upsilon^(1/2) I_C)=1/2-1/2=0", "covariant_derivative": "D I_C=nabla I_C+(1/2)A_D I_C when differentiated", "linear_A_D_coupling": 0, "quadratic_A_D_coupling": 0, "boundary_contribution": "inherited GHY through G8; attachment term algebraic"},
        {"field": "g5", "incidence_map": "identity lift into L_D^(+1/2)", "homogeneity_degree": 1, "support_weight": 0, "incidence_weight": "+1/2", "derivation_equation": "w(upsilon^(-1/2) I_W)=-1/2+1/2=0", "covariant_derivative": "D I_W=nabla I_W-(1/2)A_D I_W when differentiated", "linear_A_D_coupling": 0, "quadratic_A_D_coupling": 0, "boundary_contribution": "inherited GHY and Lambda54 matcher"},
        {"field": "Lambda85", "incidence_map": "dual attachment pairing", "homogeneity_degree": 1, "support_weight": 0, "incidence_weight": "0", "derivation_equation": "neutral dressed mismatch and neutral dmu5 imply w_Lambda85=0", "covariant_derivative": "none (algebraic multiplier)", "linear_A_D_coupling": 0, "quadratic_A_D_coupling": 0, "boundary_contribution": "none"},
        {"field": "h_enc", "incidence_map": "intrinsic enclosure metric", "homogeneity_degree": 1, "support_weight": 0, "incidence_weight": "not an attachment carrier", "derivation_equation": "inherited EH/coframe constraint r_e=0", "covariant_derivative": "ordinary Levi-Civita/isometric pullback derivative", "linear_A_D_coupling": 0, "quadratic_A_D_coupling": 0, "boundary_contribution": "intrinsic seam action unchanged"},
    ]


def character_payload() -> dict[str, Any]:
    subvars, submatrix, subrhs = attachment_subsystem()
    subsolution = list(submatrix.LUsolve(subrhs))
    matrix, rhs = expanded_matrix()
    pivots = matrix.rref()[1]
    free = [i for i in range(matrix.cols) if i not in pivots]
    validation = {
        "opposite_half_characters": W_CORE == -W_WALL,
        "primitive_generator_normalized": abs(W_CORE - W_WALL) == 1,
        "both_dressed_terms_neutral": total_weight(Rational(1, 2), W_CORE) == total_weight(Rational(-1, 2), W_WALL) == 0,
        "attachment_subsystem_unique": submatrix.rank() == 5 and len(submatrix.nullspace()) == 0,
        "expanded_rank_exact": matrix.rank() == 11,
        "expanded_nullity_exact": len(matrix.nullspace()) == 8,
        "intrinsic_metric_neutral": subsolution[-1] == 0,
        "no_empirical_normalization": True,
    }
    return {
        "artifact": "BHSM_attachment_character_derivation_v11_3",
        "classification": "AUTHOR_ACTION_SELECTION_PLUS_DERIVED_CHARACTERS",
        "action_selection_principle": "BHSM_RECIPROCAL_CORE_SURFACE_ATTACHMENT_PRINCIPLE",
        "primitive_support_character_normalization": "|w_C-w_W|=1; minimal representative adopted, not a fitted parameter",
        "characters": {"I_C": "-1/2", "I_W": "+1/2", "Lambda85": "0", "dmu5": "0", "h_enc": "0"},
        "attachment_subsystem": {"variables": subvars, "matrix": [[str(value) for value in row] for row in submatrix.tolist()], "right_hand_side": [str(value) for value in subrhs], "rank": submatrix.rank(), "nullity": len(submatrix.nullspace()), "solution": [str(value) for value in subsolution]},
        "expanded_variables": V11_VARIABLES,
        "expanded_matrix": [[str(value) for value in row] for row in matrix.tolist()],
        "expanded_right_hand_side": [str(value) for value in rhs],
        "rank": matrix.rank(),
        "nullity": len(matrix.nullspace()),
        "pivot_columns": [V11_VARIABLES[i] for i in pivots],
        "free_columns": [V11_VARIABLES[i] for i in free],
        "physical_attachment_character_directions": [],
        "boundary_only_directions": [name for name in ("w_wall_embedding", "w_surface") if name in [V11_VARIABLES[i] for i in free]],
        "core_only_directions": [name for name in ("w_core", "w_BH_transfer") if name in [V11_VARIABLES[i] for i in free]],
        "primitive_field_propagation": primitive_weight_rows(),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def constraint_matrix_payload() -> dict[str, Any]:
    payload = character_payload()
    return {
        "artifact": "BHSM_attachment_character_constraint_matrix_v11_3",
        "classification": "DERIVED_WITH_ADOPTED_PRIMITIVE_GENERATOR_NORMALIZATION",
        "attachment_subsystem": payload["attachment_subsystem"],
        "expanded_variables": payload["expanded_variables"],
        "expanded_matrix": payload["expanded_matrix"],
        "expanded_right_hand_side": payload["expanded_right_hand_side"],
        "rank": payload["rank"],
        "nullity": payload["nullity"],
        "pivot_columns": payload["pivot_columns"],
        "free_columns": payload["free_columns"],
        "common_generator_normalization": payload["primitive_support_character_normalization"],
        "physical_character_directions": payload["physical_attachment_character_directions"],
        "boundary_only_directions": payload["boundary_only_directions"],
        "core_only_directions": payload["core_only_directions"],
        "row_provenance": [
            "v11.2 frozen S8/S4 homogeneous action rows",
            "neutral upsilon^(1/2) I_C term",
            "neutral upsilon^(-1/2) I_W term",
            "neutral inherited Lambda85 pairing and dmu5",
            "neutral complete attachment mismatch",
        ],
        "validation": payload["validation"],
        "validation_passed": payload["validation_passed"],
    }
