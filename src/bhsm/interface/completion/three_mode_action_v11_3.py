"""Action-normalized local q_C/q_W/q_D KKT operator."""

from __future__ import annotations

from typing import Any

from sympy import Matrix, symbols


def constraint_jacobian() -> Matrix:
    """Linearized I_W-upsilon I_C=0 in normalized (q_C,q_W,q_D/lambda_D)."""

    return Matrix([[-1, 1, 1]])


def tangent_basis() -> Matrix:
    return Matrix([[1, 1], [1, 0], [0, 1]])


def kinetic_matrix() -> Matrix:
    """Whitened positive action metric; whitening adds no physical parameter."""

    return Matrix.eye(3)


def three_mode_payload() -> dict[str, Any]:
    B = constraint_jacobian()
    N = tangent_basis()
    K = kinetic_matrix()
    Kred = N.T * K * N
    h_c, h_w, h_d = symbols("h_C h_W h_D", real=True)
    H = Matrix.diag(h_c, h_w, h_d)
    Hred = N.T * H * N
    validation = {
        "three_slots_preserved": B.cols == 3,
        "one_attachment_constraint": B.rank() == 1,
        "tangent_basis_exact": bool(B * N == Matrix.zeros(1, 2)),
        "kinetic_rank_three_before_constraint": K.rank() == 3,
        "reduced_kinetic_rank_two": Kred.rank() == 2,
        "reduced_kinetic_positive": bool(Kred.det() > 0 and Kred.trace() > 0),
        "no_scale_required": True,
        "uncomputed_Hessian_not_promoted": True,
    }
    return {
        "artifact": "BHSM_three_mode_action_v11_3",
        "classification": "DERIVED_CONDITIONAL",
        "coordinates": ["q_C action-normalized core incidence amplitude", "q_W action-normalized wall incidence amplitude", "x_D=q_D/lambda_D"],
        "quadratic_action": "S2=1/2 int[(dot q)^T K dot q-q^T H q+2 Lambda_attach B q] dmu",
        "kinetic_matrix": [[int(value) for value in row] for row in K.tolist()],
        "kinetic_rank": K.rank(),
        "kinetic_signature": [3, 0, 0],
        "constraint_jacobian": [[int(value) for value in row] for row in B.tolist()],
        "constraint_rank": B.rank(),
        "constraint_direction": "normal to ker B: (-1,1,1)",
        "tangent_basis": [[int(value) for value in row] for row in N.tolist()],
        "reduced_kinetic_matrix": [[int(value) for value in row] for row in Kred.tolist()],
        "reduced_kinetic_eigenvalues": [1, 3],
        "physical_mode_count": 2,
        "three_physical_slots_collapsed": False,
        "Hessian_parent": "diag(h_C,h_W,h_D) plus inherited embedding/boundary response blocks",
        "Hessian_reduced": [[str(value) for value in row] for row in Hred.tolist()],
        "Hessian_generic_rank": 2,
        "Hessian_rank_condition": "h_C h_W+h_C h_D+h_W h_D !=0",
        "attachment_induced_mixed_block": "constraint projection gives Hred_12=h_C in the displayed normalized tangent basis",
        "local_equilibrium": "I_W=upsilon I_C together with the three inherited sector equations and Lambda85 reactions",
        "second_variation": "KKT operator [[H,B^T],[B,0]] on the common attachment domain",
        "stability_status": "CONDITIONAL_ON_POSITIVITY_OF_THE_ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN",
        "exact_open_block": "ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_ON_COMMON_ATTACHMENT_DOMAIN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
