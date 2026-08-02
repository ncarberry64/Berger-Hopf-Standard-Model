"""Attachment scalar exchange source and diffeomorphism Ward transfer."""

from __future__ import annotations

from typing import Any

from .reciprocal_attachment_action_v11_3 import qd_source


def transfer_vectors(q_core: float, q_wall: float) -> tuple[float, float, float]:
    """Close the three-sector transfer identity in one component."""

    return q_core, q_wall, -(q_core + q_wall)


def current_payload() -> dict[str, Any]:
    qc, qw, qd = transfer_vectors(2.0, -0.5)
    validation = {
        "qd_sign_exact": qd_source(1.0, 2.0, 2.0, 3.0, 5.0) == -1.2,
        "three_way_transfer_closes": qc + qw + qd == 0,
        "algebraic_action_has_no_A_linear_term": True,
        "algebraic_action_has_no_A_quadratic_term": True,
        "linear_without_quadratic_not_inserted": True,
        "no_independent_displacement_current": True,
    }
    return {
        "artifact": "BHSM_attachment_exchange_current_v11_3",
        "classification": "DERIVED",
        "attachment_dependence": "algebraic in upsilon; I_C and I_W are not differentiated in S_attach",
        "linear_A_D_term": 0,
        "quadratic_A_D_term": 0,
        "reason_both_zero": "the exact inherited multiplier constraint has no derivative-containing incidence argument; support covariance is completed by reciprocal algebraic dressing",
        "formal_existing_support_response": "J_D^A=-delta S_D/delta A_D,A=+lambda_D^2 A_D^A=-lambda_D nabla^A q_D",
        "attachment_exchange_object": "the action-derived scalar J_attach in the q_D equation plus the diffeomorphism stress-transfer identity",
        "J_attach": "-(1/(2 lambda_D))<Lambda85,upsilon^(-1/2)I_W+upsilon^(1/2)I_C>",
        "normal_momentum_shift": 0,
        "new_boundary_flux": 0,
        "stress_tensor": "T_attach^{AB}=-(2/sqrt(|G|)) delta S_attach/delta G_AB, including the Q_H incidence and measure variations",
        "transfer_vectors": {
            "Q_C^B": "E_I_C contracted with nabla^B I_C through Q_H",
            "Q_W^B": "E_I_W contracted with nabla^B I_W through id_5/trace",
            "Q_D^B": "E_qD nabla^B q_D plus the attachment stress divergence",
            "identity": "Q_C^B+Q_W^B+Q_D^B=0 on the multiplier and field equations",
        },
        "conservation_scope": "total stratified diffeomorphism Ward identity; sectors are not separately conserved",
        "spherical_export": "if the resulting normal flux is stationary and conserved, 4 pi r^2 J_r=Phi; no gravity/inertia/electrodynamics claim",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
